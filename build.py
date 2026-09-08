#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "jinja2>=3.1.6",
#     "pyyaml>=6.0.3",
# ]
# ///
"""Generate vincentqb.github.io into docs/ for GitHub Pages."""

import shutil
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATES = {"index.html.j2": "index.html", "llms.txt.j2": "llms.txt"}


def build(
    data_file: Path = Path("data.yaml"),
    template_dir: Path = Path("templates"),
    static_dir: Path = Path("static"),
    output_dir: Path = Path("docs"),
) -> None:
    data = yaml.safe_load(data_file.read_text(encoding="utf-8"))
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    for template_name, output_name in TEMPLATES.items():
        content = env.get_template(template_name).render(data=data).rstrip("\n") + "\n"
        output_path = output_dir / output_name
        output_path.write_text(content, encoding="utf-8")
        print(f"Generated {output_path} ({len(content)} characters)")

    if not static_dir.is_dir():
        print(f"Warning: {static_dir} not found, skipping static assets", file=sys.stderr)
        return
    shutil.copytree(static_dir, output_dir, dirs_exist_ok=True)
    print(f"Copied {static_dir} -> {output_dir}")


if __name__ == "__main__":
    try:
        build()
    except Exception as error:
        print(f"Build failed: {error}", file=sys.stderr)
        sys.exit(1)
