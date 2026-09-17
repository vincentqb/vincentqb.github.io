Build [vincentqb.github.io](https://vincentqb.github.io) with `uv run --script build.py`.

## leantex port

`leantex/` holds a port of this site to [leantex]: one source, `leantex/site.tex`,
producing `index.html`, `llms.txt`, and a print resume `site.pdf` from the same
document — the Jinja build's two outputs plus one the browser's print stylesheet
only approximates.

```sh
# build into docs-leantex/ (needs the leantex binary)
LEANTEX=/path/to/leantex ./leantex/build-leantex.sh

# compare with the Jinja build in docs/
node leantex/compare-leantex.js
```

The comparison renders both pages at 360/768/1280 px into `compare-out/`,
diffs the page structure (title, head metadata, JSON-LD, heading outline,
landmarks, ids, link targets, image alt), measures characters-per-line, and
diffs the two `llms.txt` files. It does not check pixel equality or scripted
behaviour; the port has no script by design (in-page anchors + CSS
`scroll-behavior`, and a scroll-driven animation for the return-to-top).

Colours differ deliberately: the site's accent `hsl(0,85%,54%)` reads at
4.28:1 on white and Bulma's grey at 4.49:1 on white-bis — both below WCAG 2.2
SC 1.4.3's 4.5:1 — so the port uses the same hues at 45%/44% lightness
(5.40:1 / 5.19:1), measured with leantex's own contrast arithmetic.
