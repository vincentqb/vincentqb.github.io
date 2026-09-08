#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "jinja2>=3.1.6",
#     "pyyaml>=6.0.3",
#     "typer>=0.15",
# ]
# ///

import shutil
import sys
from pathlib import Path
from typing import Annotated

import typer
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape


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
    data: Annotated[Path, typer.Option("--data", "-d", help="Path to data YAML file.")] = Path("data.yaml"),
    templates: Annotated[Path, typer.Option("--templates", "-t", help="Path to template directory.")] = Path("templates"),
    static: Annotated[Path, typer.Option("--static", "-s", help="Path to static assets directory.")] = Path("static"),
    output_dir: Annotated[
        Path, typer.Option("--output-dir", "-o", help="Target output directory (GitHub Pages /docs deployment).")
    ] = Path("docs"),
) -> None:
    """Static site generator for vincentqb.github.io (generates index.html, llms.txt, and static assets)."""
    print(f"Building website into '{output_dir}'...")

    try:
        site_data = load_data(data)
        jinja_env = setup_jinja_env(templates)

        # Render main index.html
        render_template(
            env=jinja_env,
            template_name="index.html.j2",
            data=site_data,
            output_path=output_dir / "index.html",
        )

        # Render llms.txt for AI/LLM crawlers
        render_template(
            env=jinja_env,
            template_name="llms.txt.j2",
            data=site_data,
            output_path=output_dir / "llms.txt",
        )

        # Copy static assets (e.g. style.css, profile.jpg)
        copy_static_assets(static, output_dir)
    except Exception as e:
        print(f"\n❌ Build failed: {e}", file=sys.stderr)
        raise typer.Exit(code=1) from e

    print("\nBuild completed successfully!")


if __name__ == "__main__":
    typer.run(build)
