#!/usr/bin/env node
// Compare the Jinja build (docs/) with the leantex build (docs-leantex/):
//
//   node leantex/compare-leantex.js
//
// What it does:
//   1. Renders both index.html files at 360 / 768 / 1280 px and writes
//      full-page screenshots to compare-out/ for side-by-side inspection.
//   2. Extracts the structure of each page — title, head metadata, JSON-LD,
//      heading outline, landmarks, ids, in-page link targets, image alt —
//      and prints a field-by-field diff.
//   3. Measures rendered characters-per-line of body text in the Experience
//      section (the 45–90 readable-measure band) and key computed colours.
//   4. Diffs docs/llms.txt against docs-leantex/llms.txt line by line.
//
// What it does NOT check: pixel equality (the two pages share a design, not
// bytes), scripted behaviour (the port has none by design), print output
// (compare docs-leantex/site.pdf with the browser's print of docs/ by hand).
//
// Environment: PW_MODULE (path of playwright/playwright-core) and CHROME
// (chromium executable) override the defaults for this host.

const path = require('path');
const fs = require('fs');

const PW = process.env.PW_MODULE ||
  '/local/home/quennv/.bun/install/cache/playwright-core@1.58.2@@@1';
const CHROME = process.env.CHROME ||
  '/local/home/quennv/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome';
const { chromium } = require(PW);

const root = path.resolve(__dirname, '..');
const REF = path.join(root, 'docs', 'index.html');
const PORT = path.join(root, 'docs-leantex', 'index.html');
const OUT = path.join(root, 'compare-out');
const WIDTHS = [360, 768, 1280];

function extractStructure() {
  const meta = (sel, attr) => {
    const el = document.querySelector(sel);
    return el ? el.getAttribute(attr || 'content') : null;
  };
  const headings = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')]
    .map(h => `${h.tagName.toLowerCase()}: ${h.textContent.trim().replace(/\s+/g, ' ')}`);
  const sections = [...document.querySelectorAll('section')].map(s => s.id || '(no id)');
  const landmarks = [...document.querySelectorAll('nav,main,header,footer,aside')]
    .map(l => l.tagName.toLowerCase());
  const ids = [...document.querySelectorAll('[id]')].map(e => e.id);
  const inPage = [...document.querySelectorAll('a[href^="#"], a[onclick]')]
    .map(a => a.getAttribute('href') || `onclick:${a.getAttribute('onclick')}`);
  const imgs = [...document.querySelectorAll('img')]
    .map(i => `${i.getAttribute('src')} alt=${JSON.stringify(i.getAttribute('alt'))}`);
  const jsonld = [...document.querySelectorAll('script[type="application/ld+json"]')]
    .map(s => { try { const d = JSON.parse(s.textContent); return `${d['@type']}: ${d.name}`; }
                catch { return 'unparseable'; } });
  // Measure: characters per rendered line of continuous text in Experience.
  let measure = null;
  const para = document.querySelector('#experience .experience-item p') ||
               document.querySelector('#experience li');
  if (para) {
    const cs = getComputedStyle(para);
    const lh = parseFloat(cs.lineHeight);
    const lines = Math.max(1, Math.round(para.getBoundingClientRect().height / lh));
    measure = Math.round(para.textContent.trim().length / lines);
  }
  const colour = sel => {
    const el = document.querySelector(sel);
    return el ? getComputedStyle(el).color : null;
  };
  // The two fidelity nits, measured: the top menu's computed face and the
  // awards line's face and spacing, from whichever selector the build uses.
  const style = (sel, props) => {
    const el = document.querySelector(sel);
    if (!el) return null;
    const cs = getComputedStyle(el);
    const out = {};
    for (const p of props) out[p] = cs[p];
    return out;
  };
  const navMenu =
    style('.navbar-menu .navbar-item',
      ['fontWeight', 'fontSize', 'fontVariant', 'letterSpacing', 'color', 'fontFamily']) ||
    style('nav[aria-label="Sections"] a',
      ['fontWeight', 'fontSize', 'fontVariant', 'letterSpacing', 'color', 'fontFamily']);
  const awards =
    style('.awards-text',
      ['fontSize', 'fontStyle', 'fontWeight', 'lineHeight', 'marginTop', 'color']) ||
    style('#education li em',
      ['fontSize', 'fontStyle', 'fontWeight', 'lineHeight', 'marginTop', 'color']);
  const eduItem =
    style('.education-item',
      ['marginBottom', 'paddingTop', 'paddingBottom', 'fontSize']) ||
    style('#education li',
      ['marginBottom', 'paddingTop', 'paddingBottom', 'fontSize']);
  return {
    title: document.title,
    lang: document.documentElement.lang || null,
    description: meta('meta[name="description"]'),
    canonical: meta('link[rel="canonical"]', 'href'),
    alternate: meta('link[rel="alternate"]', 'href'),
    ogTitle: meta('meta[property="og:title"]'),
    twitterCard: meta('meta[name="twitter:card"]'),
    favicon: meta('link[rel="icon"]', 'href'),
    stylesheets: [...document.querySelectorAll('link[rel="stylesheet"]')].length,
    scripts: [...document.querySelectorAll('script[src], script:not([type="application/ld+json"])')]
      .filter(s => s.textContent.trim() || s.src).length,
    jsonld, headings, landmarks, sections, ids, inPage, imgs, measure,
    bodyFont: getComputedStyle(document.body).fontFamily.split(',')[0],
    navMenu, awards, eduItem,
    accentSample: colour('#experience .experience-item h4') ||
                  colour('#experience .spaced > p:first-of-type > span'),
    mutedSample: colour('#experience .experience-item h5') ||
                 colour('#experience .spaced > p:first-of-type > span:nth-of-type(2)'),
  };
}

function diffField(name, a, b) {
  const A = JSON.stringify(a), B = JSON.stringify(b);
  if (A === B) return `  same  ${name}: ${A}`;
  return `  DIFF  ${name}:\n         ref:  ${A}\n         port: ${B}`;
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch({ executablePath: CHROME });
  const page = await browser.newPage();
  const results = {};
  for (const [label, file] of [['ref', REF], ['port', PORT]]) {
    for (const w of WIDTHS) {
      await page.setViewportSize({ width: w, height: 900 });
      await page.goto('file://' + file, { waitUntil: 'load' });
      await page.waitForTimeout(300);
      await page.screenshot({ path: path.join(OUT, `${label}-${w}.png`), fullPage: true });
    }
    results[label] = await page.evaluate(extractStructure);
  }
  await browser.close();

  const r = results.ref, p = results.port;
  console.log('== structural comparison (ref = docs/, port = docs-leantex/) ==');
  for (const k of Object.keys(r)) console.log(diffField(k, r[k], p[k]));

  console.log('\n== llms.txt line diff ==');
  const readLines = f => fs.readFileSync(f, 'utf8').split('\n');
  const a = readLines(path.join(root, 'docs', 'llms.txt'));
  const b = readLines(path.join(root, 'docs-leantex', 'llms.txt'));
  const setA = new Set(a.map(l => l.trim()).filter(Boolean));
  const setB = new Set(b.map(l => l.trim()).filter(Boolean));
  const onlyA = [...setA].filter(l => !setB.has(l));
  const onlyB = [...setB].filter(l => !setA.has(l));
  console.log(`ref ${a.length} lines, port ${b.length} lines; ` +
    `${onlyA.length} lines only in ref, ${onlyB.length} only in port`);
  for (const l of onlyA) console.log(`  ref only:  ${l}`);
  for (const l of onlyB) console.log(`  port only: ${l}`);

  console.log(`\nscreenshots in ${OUT} (ref-*.png vs port-*.png)`);
})();
