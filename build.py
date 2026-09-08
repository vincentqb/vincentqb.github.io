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

DATA_FILE = Path("data.yaml")
TEMPLATE_DIR = Path("templates")
STATIC_DIR = Path("static")
OUTPUT_DIR = Path("docs")
TEMPLATES = {"index.html.j2": "index.html", "llms.txt.j2": "llms.txt"}


def build() -> None:
    data = yaml.safe_load(DATA_FILE.read_text(encoding="utf-8"))
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for template_name, output_name in TEMPLATES.items():
        content = env.get_template(template_name).render(data=data).rstrip("\n") + "\n"
        output_path = OUTPUT_DIR / output_name
        output_path.write_text(content, encoding="utf-8")
        print(f"Generated {output_path} ({len(content)} characters)")

    if not STATIC_DIR.is_dir():
        print(f"Warning: {STATIC_DIR} not found, skipping static assets", file=sys.stderr)
        return
    shutil.copytree(STATIC_DIR, OUTPUT_DIR, dirs_exist_ok=True)
    print(f"Copied {STATIC_DIR} -> {OUTPUT_DIR}")


if __name__ == "__main__":
    try:
        build()
    except Exception as error:
        print(f"Build failed: {error}", file=sys.stderr)
        sys.exit(1)
