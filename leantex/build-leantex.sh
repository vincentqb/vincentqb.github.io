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
"$LEANTEX" site.tex -o "$OUT/"

# The web spelling of the page; the markdown twin is already written as
# llms.txt — its served name is declared in site.tex, so the head's
# alternate link and the file cannot drift.
mv "$OUT/site.html" "$OUT/index.html"

# Assets the page references.
cp -f ../static/profile.jpg "$OUT/"
cp -f ../static/favicon.svg "$OUT/"
cp -f style.css "$OUT/"
mkdir -p "$OUT/fonts"
cp -f fonts/*.ttf fonts/LICENSE-FontAwesome.txt "$OUT/fonts/"

echo "built $OUT: index.html, llms.txt, site.pdf"
