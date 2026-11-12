#!/usr/bin/env node
// Prints each handout to a letter PDF and checks it.
// Run after build.py:  NODE_PATH="$(npm root -g)" node classroom/build-pdf.cjs
// Fails (exit 1) when a handout does not have the page count listed here, when a web font did not load
// (the PDF would silently fall back to Georgia or Verdana), or when anything runs past the sheet's edge.
const { chromium } = require("playwright");
const path = require("path");
const fs = require("fs");

const HANDOUTS = [
  ["own-data-or-public-data", 1],
  ["method-planning-grid", 2],
  ["method-section-checklist", 1],
  ["sda-lab", 2],
];
const FACES = ['900 20px "Fraunces"', '650 20px "Fraunces"', '400 12px "Atkinson Hyperlegible"', '700 12px "Atkinson Hyperlegible"', '700 12px "Space Mono"'];

(async () => {
  const browser = await chromium.launch();
  let bad = 0;
  for (const [name, want] of HANDOUTS) {
    const page = await browser.newPage();
    await page.goto("file://" + path.join(__dirname, name + ".html"));
    await page.evaluate((faces) => Promise.all(faces.map((f) => document.fonts.load(f))), FACES);
    await page.evaluate(() => document.fonts.ready);
    const missing = await page.evaluate((faces) => faces.filter((f) => !document.fonts.check(f)), FACES);
    await page.emulateMedia({ media: "print" });
    await page.setViewportSize({ width: 710, height: 960 }); // the printable area of a letter sheet, in CSS px
    const wide = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
    const out = path.join(__dirname, name + ".pdf");
    await page.pdf({ path: out, preferCSSPageSize: true, printBackground: true });
    const got = (fs.readFileSync(out, "latin1").match(/\/Type\s*\/Page[^s]/g) || []).length;
    const problems = [];
    if (got !== want) problems.push(`${got} pages, expected ${want}`);
    if (missing.length) problems.push("fonts not loaded: " + missing.join(", "));
    if (wide) problems.push("content is wider than the sheet");
    console.log(`${problems.length ? "FAIL" : "ok  "} ${name}.pdf  ${got} page${got === 1 ? "" : "s"}${problems.length ? "  " + problems.join("; ") : ""}`);
    bad += problems.length;
    await page.close();
  }
  await browser.close();
  process.exit(bad ? 1 : 0);
})();
