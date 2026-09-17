#!/usr/bin/env bash
# Build the leantex port of the site into docs-leantex/: index.html and
# llms.txt from one source (leantex/site.tex), plus site.pdf — the print
# output the site's @media print block approximates.
#
# Needs the leantex binary; point LEANTEX at it if it is not on PATH:
#   LEANTEX=/path/to/leantex ./leantex/build-leantex.sh
set -euo pipefail
cd "$(dirname "$0")"

LEANTEX="${LEANTEX:-leantex}"
OUT=../docs-leantex

# The photo lives in static/; leantex resolves images beside the document.
cp -f ../static/profile.jpg .

mkdir -p "$OUT"
"$LEANTEX" site.tex -o "$OUT/" --emit html,md,pdf

# The web spellings of the two text outputs.
mv "$OUT/site.html" "$OUT/index.html"
mv "$OUT/site.md" "$OUT/llms.txt"

# Assets the page references.
cp -f ../static/profile.jpg "$OUT/"
cp -f style.css "$OUT/"

echo "built $OUT: index.html, llms.txt, site.pdf"
