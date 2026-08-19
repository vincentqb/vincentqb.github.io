#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "jinja2>=3.1.6",
#     "pyyaml>=6.0.3",
# ]
# ///

import argparse
import shutil
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Configuration Constants
DEFAULT_DATA_FILE = "data.yaml"
DEFAULT_TEMPLATE_DIR = "templates"
DEFAULT_STATIC_DIR = "static"
DEFAULT_OUTPUT_DIR = "docs"  # Output folder for GitHub Pages /docs deployment


def load_data(filepath: str | Path) -> dict:
    """Load and parse the YAML data file."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Data file not found at: {path}")

    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def setup_jinja_env(template_dir: str | Path) -> Environment:
    """Initialize and configure the Jinja2 environment."""
    path = Path(template_dir)
    if not path.exists():
        raise FileNotFoundError(f"Template directory not found at: {path}")

    return Environment(
        loader=FileSystemLoader(str(path)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_template(env: Environment, template_name: str, data: dict, output_path: Path) -> None:
    """Render a specific template and write it to the output directory."""
    template = env.get_template(template_name)
    content = template.render(data=data)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(content)
        # Ensure trailing newline
        if not content.endswith("\n"):
            file.write("\n")
    print(f"✓ Generated: {output_path} ({len(content)} bytes)")


def copy_static_assets(src_dir: str | Path, dest_dir: str | Path) -> None:
    """Copy all static assets from src_dir to dest_dir."""
    src = Path(src_dir)
    dest = Path(dest_dir)

    if not src.exists():
        print(f"! Warning: Static directory '{src}' not found. Skipping static assets.")
        return

    if src.resolve() == dest.resolve():
        return

    dest.mkdir(parents=True, exist_ok=True)
    for item in sorted(src.iterdir()):
        target = dest / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)
        print(f"✓ Copied asset: {item} -> {target}")


def build(
    data_file: str | Path,
    template_dir: str | Path,
    static_dir: str | Path,
    output_dir: str | Path,
) -> None:
    """Execute site generation."""
    out_dir = Path(output_dir)
    print(f"Building website into '{out_dir}'...")

    site_data = load_data(data_file)
    jinja_env = setup_jinja_env(template_dir)

    # Render main index.html
    render_template(
        env=jinja_env,
        template_name="index.html.j2",
        data=site_data,
        output_path=out_dir / "index.html",
    )

    # Render llms.txt for AI/LLM crawlers
    render_template(
        env=jinja_env,
        template_name="llms.txt.j2",
        data=site_data,
        output_path=out_dir / "llms.txt",
    )

    # Copy static assets (e.g. style.css, profile.jpg)
    copy_static_assets(static_dir, out_dir)

    print("\nBuild completed successfully!")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Static site generator for vincentqb.github.io (generates index.html, llms.txt, and static assets)"
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Target output directory (default: '{DEFAULT_OUTPUT_DIR}')",
    )
    parser.add_argument(
        "--data",
        "-d",
        default=DEFAULT_DATA_FILE,
        help=f"Path to data YAML file (default: '{DEFAULT_DATA_FILE}')",
    )
    parser.add_argument(
        "--templates",
        "-t",
        default=DEFAULT_TEMPLATE_DIR,
        help=f"Path to template directory (default: '{DEFAULT_TEMPLATE_DIR}')",
    )
    parser.add_argument(
        "--static",
        "-s",
        default=DEFAULT_STATIC_DIR,
        help=f"Path to static assets directory (default: '{DEFAULT_STATIC_DIR}')",
    )

    args = parser.parse_args()

    try:
        build(
            data_file=args.data,
            template_dir=args.templates,
            static_dir=args.static,
            output_dir=args.output_dir,
        )
    except Exception as e:
        print(f"\n❌ Build failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
