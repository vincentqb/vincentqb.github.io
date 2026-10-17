#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "jinja2>=3.1.6",
#     "pyyaml>=6.0.3",
# ]
# ///
"""Generate vincentqb.github.io into docs/ for GitHub Pages."""

import colorsys
import shutil
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape


def build(
    data_file: Path = Path("data.yaml"),
    template_dir: Path = Path("templates"),
    static_dir: Path = Path("static"),
    output_dir: Path = Path("docs"),
) -> None:
    data = yaml.safe_load(data_file.read_text(encoding="utf-8"))
    # Bulma takes HSL channels; derive them from the shared sRGB accent so
    # the website, favicon, and PDFs cannot acquire separate red values.
    accent = data["palette"]["accent"]["srgb"]
    rgb = tuple(int(accent[i : i + 2], 16) / 255 for i in (0, 2, 4))
    hue, lightness, saturation = colorsys.rgb_to_hls(*rgb)
    accent_hsl = tuple(f"{v:.6f}" for v in (hue * 360, saturation * 100, lightness * 100))
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    for template_path in sorted(template_dir.glob("*.j2")):
        if template_path.name.startswith("_"):
            continue
        content = env.get_template(template_path.name).render(data=data, accent_hsl=accent_hsl).rstrip("\n") + "\n"
        output_path = output_dir / template_path.stem
        output_path.write_text(content, encoding="utf-8")
        print(f"Generated {output_path} ({len(content)} characters)")

    if not static_dir.is_dir():
        print(f"Warning: {static_dir} not found, skipping static assets", file=sys.stderr)
        return
    shutil.copytree(static_dir, output_dir, dirs_exist_ok=True)
    print(f"Copied {static_dir} -> {output_dir}")


if __name__ == "__main__":
    build()
