#!/usr/bin/env node
// Design floor for everything students see. Run: NODE_PATH="$(npm root -g)" node tools/design_check.cjs
// Renders the Search Guide, the Research Library and the print handouts in headless Chromium, at phone and
// desktop width, light and dark, and measures the rules in DESIGN.md on the rendered page. Exit 1 on any failure.
// It reports selectors only, never page text, so no student name or question reaches the output.
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const only = process.argv[2]; // optional: a substring of a surface name
const html = fs.readFileSync(path.join(ROOT, "index.html"), "utf8");
const DATA = JSON.parse(html.match(/var DATA = (\[.*?\]);\n/s)[1]);
const research = DATA.find((d) => d.c === "R" && d.q);
const seminar = DATA.find((d) => d.c === "S" && d.q);

const SURFACES = [
  { name: "search-guide home", file: "index.html" },
  { name: "search-guide desk (research)", file: "index.html", hash: research.id },
  { name: "search-guide desk (seminar)", file: "index.html", hash: seminar.id },
  { name: "search-guide desk, form open", file: "index.html", hash: research.id, state: "form" },
  { name: "search-guide desk, version saved", file: "index.html", hash: research.id, state: "saved" },
  { name: "search-guide desk, circled and checked", file: "index.html", hash: seminar.id, state: "worked" },
  { name: "research-library", file: "classroom/research-library.html" },
  { name: "handout own-data", file: "classroom/own-data-or-public-data.html", print: true },
  { name: "handout planning-grid", file: "classroom/method-planning-grid.html", print: true },
  { name: "handout checklist", file: "classroom/method-section-checklist.html", print: true },
  { name: "handout sda-lab", file: "classroom/sda-lab.html", print: true },
];
const VIEWS = [
  { w: 380, h: 800, scheme: "light" },
  { w: 380, h: 800, scheme: "dark" },
  { w: 1280, h: 900, scheme: "light" },
  { w: 1280, h: 900, scheme: "dark" },
];

// The only one-sided borders allowed: the quotation bar beside a student's own question, and drawn chevrons.
const STRIPE_OK = [".q", ".q-rec", "summary::before"];

// States a student reaches by acting. The words typed here are test filler in a throwaway browser profile.
async function enterState(page, state) {
  if (state === "form" || state === "saved") {
    await page.click("#q-open");
    await page.waitForSelector("#wb-form", { state: "visible" });
  }
  if (state === "saved") {
    await page.fill("#wb-text", "Design check filler version, not a question.");
    await page.fill("#wb-why", "Design check filler reason.");
    await page.click("#wb-save");
    await page.waitForTimeout(500);
  }
  if (state === "worked") {
    for (const sel of ["#st-checks .dot", "#st-checks .ck-more button", "#words .w"]) {
      const el = page.locator(sel).first();
      if (await el.count()) await el.click().catch(() => {});
    }
    await page.waitForTimeout(300);
  }
}

// Source rules: checked on the files themselves.
function sourceChecks(file) {
  let text = fs.readFileSync(path.join(ROOT, file), "utf8");
  if (file === "index.html") text = text.replace(/var DATA = \[.*?\];\n/s, ""); // the roster is data, not design
  const out = [];
  const banned = text.match(/\b(Inter|Roboto|Arial)\b/g);
  if (banned) out.push(`banned font named: ${[...new Set(banned)].join(", ")}`);
  if (/[–—]/.test(text)) out.push("en or em dash in the source");
  if (/[\u{1F300}-\u{1FAFF}]/u.test(text)) out.push("emoji in the source");
  const css = (text.match(/<style>[\s\S]*?<\/style>/g) || []).join("\n");
  for (const m of css.matchAll(/([^{}]+)\{([^{}]*)\}/g)) {
    const side = m[2].match(/border-(left|right|inline-start|inline-end)(-width)?\s*:\s*(\d+(?:\.\d+)?)px/);
    const selector = m[1].trim();
    if (side && +side[3] >= 2 && !STRIPE_OK.some((ok) => selector.includes(ok))) out.push(`side stripe in the stylesheet: ${selector.slice(0, 48)} (${side[3]}px)`);
  }
  if (!/::selection/.test(text)) out.push("no ::selection style: selected text falls back to the browser's blue");
  if (/<(input|textarea)\b/.test(text) && !/caret-color/.test(text)) out.push("fields without caret-color");
  if (!/:focus-visible/.test(text) && /<(a|button|input|textarea|select|summary)\b/.test(text)) out.push("no :focus-visible style");
  if (/(transition|animation)\s*:/.test(text) && !/prefers-reduced-motion/.test(text)) out.push("motion without a prefers-reduced-motion rule");
  return out;
}

// Rendered rules: run inside the page.
function renderedChecks(opts) {
  const fails = [];
  const sel = (el) => {
    let s = el.tagName.toLowerCase();
    if (el.id) s += "#" + el.id;
    else if (el.classList.length) s += "." + [...el.classList].slice(0, 2).join(".");
    const p = el.parentElement;
    if (p && p !== document.body && !el.id) s = (p.id ? p.tagName.toLowerCase() + "#" + p.id : p.tagName.toLowerCase() + (p.classList.length ? "." + p.classList[0] : "")) + " > " + s;
    return s;
  };
  const add = (rule, el, detail) => fails.push(`${rule}: ${sel(el)}${detail ? " (" + detail + ")" : ""}`);
  const visible = (el) => {
    if (!el.getClientRects().length) return false;
    const cs = getComputedStyle(el);
    if (cs.visibility === "hidden" || cs.display === "none" || +cs.opacity === 0) return false;
    const r = el.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) return false;
    // visually hidden helpers
    return !(cs.position === "absolute" && (cs.clip !== "auto" || cs.clipPath !== "none") && r.width <= 2);
  };
  const all = [...document.body.querySelectorAll("*")].filter((e) => !["SCRIPT", "STYLE", "TEMPLATE"].includes(e.tagName));
  const shown = all.filter(visible);
  const px = (v) => parseFloat(v) || 0;
  const rootPx = px(getComputedStyle(document.documentElement).fontSize);

  // 1. No page wider than its viewport.
  if (document.documentElement.scrollWidth > document.documentElement.clientWidth + 1) fails.push(`overflow: the page scrolls sideways (${document.documentElement.scrollWidth}px in a ${document.documentElement.clientWidth}px viewport)`);

  // 2. No eyebrow: a small tracked uppercase label sitting directly above a heading.
  for (const h of shown.filter((e) => /^H[12]$/.test(e.tagName))) {
    let prev = h.previousElementSibling;
    while (prev && !visible(prev)) prev = prev.previousElementSibling;
    if (!prev || !prev.textContent.trim() || prev.children.length > 1) continue;
    const a = getComputedStyle(prev), b = getComputedStyle(h);
    if (a.textTransform === "uppercase" && px(a.letterSpacing) > 0 && px(a.fontSize) < px(b.fontSize) * 0.62) add("eyebrow above a heading", prev);
  }

  // 3. No side stripe: one thick coloured side border on a block.
  for (const e of shown) {
    const cs = getComputedStyle(e);
    const w = { l: px(cs.borderLeftWidth), r: px(cs.borderRightWidth), t: px(cs.borderTopWidth), b: px(cs.borderBottomWidth) };
    for (const side of ["l", "r"]) {
      const other = side === "l" ? w.r : w.l;
      if (w[side] > 1.6 && w[side] > other + 1 && w[side] > w.t + 1 && w[side] > w.b + 1 && !opts.stripeAllow.some((s) => e.matches(s))) add("side stripe", e, `${w[side].toFixed(1)}px`);
    }
  }

  // 4. Type: display size ceiling, tracking floor, balanced headings.
  for (const e of shown) {
    if (![...e.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim())) continue;
    const cs = getComputedStyle(e), fs = px(cs.fontSize);
    if (!opts.print && fs > rootPx * 6 + 0.5) add("display type over 6rem", e, `${(fs / rootPx).toFixed(2)}rem`);
    if (cs.letterSpacing !== "normal" && px(cs.letterSpacing) / fs < -0.0405) add("tracking tighter than -0.04em", e, `${(px(cs.letterSpacing) / fs).toFixed(3)}em`);
  }
  for (const h of shown.filter((e) => /^H[1-3]$/.test(e.tagName))) {
    const cs = getComputedStyle(h);
    const wrap = cs.textWrapStyle || cs.textWrap || "";
    if (!/balance/.test(wrap) && h.getClientRects().length && h.getBoundingClientRect().height > px(cs.lineHeight) * 1.5) add("heading wraps without text-wrap: balance", h);
  }

  // 5. Measure: running text that wraps stays within 75ch.
  const probe = document.createElement("span");
  probe.textContent = "0000000000";
  probe.style.cssText = "position:absolute;visibility:hidden;white-space:nowrap;letter-spacing:0";
  for (const e of shown.filter((x) => /^(P|LI|DD|BLOCKQUOTE)$/.test(x.tagName) || opts.proseAlso.some((s) => x.matches(s)))) {
    if (e.querySelector("p,li,table,ul,ol")) continue;
    const cs = getComputedStyle(e), lh = px(cs.lineHeight) || px(cs.fontSize) * 1.4;
    const inner = e.clientWidth - px(cs.paddingLeft) - px(cs.paddingRight);
    if (e.getBoundingClientRect().height - px(cs.paddingTop) - px(cs.paddingBottom) < lh * 1.6) continue; // one line
    e.appendChild(probe);
    const ch = probe.getBoundingClientRect().width / 10;
    probe.remove();
    if (ch && inner / ch > 76.5) add("measure over 75ch", e, `${Math.round(inner / ch)}ch`);
  }

  // 6. Contrast of every piece of text against the nearest solid ground.
  const rgb = (c) => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(/[,\s/]+/).map(Number); return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 }; };
  const lum = ({ r, g, b }) => { const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }; return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b); };
  const over = (top, under) => ({ r: top.r * top.a + under.r * (1 - top.a), g: top.g * top.a + under.g * (1 - top.a), b: top.b * top.a + under.b * (1 - top.a), a: 1 });
  const ground = (el) => {
    const layers = [];
    for (let n = el; n; n = n.parentElement) {
      const cs = getComputedStyle(n), c = rgb(cs.backgroundColor);
      if (c && c.a > 0) { layers.push(c); if (c.a === 1) break; }
      else if (cs.backgroundImage !== "none" && n !== document.body) return null; // picture or gradient with no solid colour: not measurable here
    }
    let base = { r: 255, g: 255, b: 255, a: 1 };
    for (const c of layers.reverse()) base = over(c, base);
    return base;
  };
  const seen = new Set();
  for (const e of shown) {
    if (![...e.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim())) continue;
    if (e.closest("[disabled],[aria-disabled=true]")) continue;
    const cs = getComputedStyle(e), fg = rgb(cs.color), bg = ground(e);
    if (!fg || !bg) continue;
    const c = over(fg, bg), L1 = lum(c), L2 = lum(bg);
    const ratio = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
    const fs = px(cs.fontSize), large = fs >= 24 || (fs >= 18.66 && +cs.fontWeight >= 700);
    const need = large ? 3 : 4.5;
    const key = sel(e) + cs.color + JSON.stringify(bg);
    if (ratio < need - 0.01 && !seen.has(key)) { seen.add(key); add("contrast", e, `${ratio.toFixed(2)}:1, needs ${need}:1`); }
  }

  // 7. Touch targets at phone width: 44px, except links inside a sentence.
  if (opts.phone && !opts.print) {
    for (const e of shown.filter((x) => x.matches("a[href],button,input:not([type=hidden]),select,textarea,summary,[role=button],[role=tab]"))) {
      if (e.tagName === "A" && e.closest("p,li,td,dd,figcaption,small") && getComputedStyle(e).display.startsWith("inline")) continue;
      const lab = e.matches("input[type=checkbox],input[type=radio]") && e.closest("label"); // the label is the target
      const r = (lab || e).getBoundingClientRect();
      if (r.height < 43.5 || r.width < 43.5) add("touch target under 44px", e, `${Math.round(r.width)}x${Math.round(r.height)}`);
    }
  }

  // 8. Icons are drawn, never a font glyph.
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const glyph = /[←-⇿⌀-⏿■-◿☀-➿⬀-⯿]/;
  const flagged = new Set();
  for (let n = walker.nextNode(); n; n = walker.nextNode()) {
    const p = n.parentElement;
    if (!p || ["SCRIPT", "STYLE", "TEMPLATE"].includes(p.tagName) || !visible(p)) continue;
    if (glyph.test(n.textContent) && !flagged.has(p)) { flagged.add(p); add("font glyph used as an icon", p); }
  }
  for (const e of shown) {
    for (const pseudo of ["::before", "::after"]) {
      const c = getComputedStyle(e, pseudo).content;
      if (c && c !== "none" && c !== "normal" && glyph.test(c) && !flagged.has(e)) { flagged.add(e); add("font glyph used as an icon", e, pseudo); }
    }
  }

  // 9. No card inside a card. A card is a bordered, filled, round-cornered block that holds other blocks.
  const isCard = (e) => {
    if (e.matches("button,a,input,textarea,select,summary,code,pre,table,td,th,svg,span,p,label,li > b")) return false;
    const cs = getComputedStyle(e);
    const b = ["Top", "Right", "Bottom", "Left"].map((k) => px(cs["border" + k + "Width"]) > 0 && cs["border" + k + "Style"] !== "none");
    const bg = rgb(cs.backgroundColor);
    return b.every(Boolean) && px(cs.borderTopLeftRadius) > 0 && bg && bg.a > 0 && e.children.length > 1 && e.getBoundingClientRect().height > 60;
  };
  for (const e of shown.filter(isCard)) {
    for (let n = e.parentElement; n && n !== document.body; n = n.parentElement) {
      if (!visible(n) || !isCard(n)) continue;
      const a = getComputedStyle(e).backgroundColor, b = getComputedStyle(n).backgroundColor;
      if (!opts.nestAllow.some((sel) => e.matches(sel))) add("card inside a card", e, a === b ? "same ground" : "");
      break;
    }
  }

  // 10. Structure: one h1, no skipped heading level, every field labelled, every icon button named.
  const hs = shown.filter((e) => /^H[1-6]$/.test(e.tagName));
  const h1s = hs.filter((h) => h.tagName === "H1").length;
  if (!opts.sheets && h1s !== 1) fails.push(`structure: ${h1s} h1 elements on screen`); // a handout has one title per sheet
  let last = 0;
  for (const h of hs) { const lv = +h.tagName[1]; if (last && lv > last + 1) add("heading level skipped", h, `h${last} to h${lv}`); last = lv; }
  for (const f of shown.filter((e) => e.matches("input:not([type=hidden]),textarea,select"))) {
    const named = f.getAttribute("aria-label") || f.getAttribute("aria-labelledby") || (f.id && document.querySelector(`label[for="${CSS.escape(f.id)}"]`)) || f.closest("label");
    if (!named) add("field without a label", f);
  }
  for (const b of shown.filter((e) => e.matches("button,a[href]"))) {
    if (!b.textContent.trim() && !b.getAttribute("aria-label") && !b.getAttribute("aria-labelledby") && !b.title) add("control without a name", b);
  }
  return fails;
}

(async () => {
  const browser = await chromium.launch();
  let total = 0;
  for (const s of SURFACES) {
    if (only && !s.name.includes(only)) continue;
    const found = new Map(); // failure -> views
    const note = (f, view) => found.set(f, (found.get(f) || new Set()).add(view));
    if (!s.hash && !s.state) for (const f of sourceChecks(s.file)) note("source: " + f, "file");
    for (const v of VIEWS) {
      for (const media of s.print ? ["screen", "print"] : ["screen"]) {
        if (media === "print" && (v.w !== 1280 || v.scheme !== "light")) continue;
        const ctx = await browser.newContext({ viewport: media === "print" ? { width: 710, height: 960 } : { width: v.w, height: v.h }, colorScheme: v.scheme });
        const page = await ctx.newPage();
        const errors = [];
        page.on("pageerror", (e) => errors.push(String(e).slice(0, 80)));
        await page.goto("file://" + path.join(ROOT, s.file) + (s.hash ? "#" + s.hash : ""));
        await page.evaluate(() => document.fonts.ready);
        await page.waitForTimeout(350);
        if (s.state) await enterState(page, s.state);
        if (media === "print") await page.emulateMedia({ media: "print" });
        const view = media === "print" ? "print" : `${v.w} ${v.scheme}`;
        const fails = await page.evaluate(renderedChecks, {
          phone: v.w < 500, print: media === "print", sheets: !!s.print,
          stripeAllow: [".q", ".q-rec", "blockquote"], // a quoted question keeps its quotation bar
          proseAlso: [".band", ".lede", ".hint", ".rule"],
          nestAllow: ["#ficha", "#vl", "form", ".page"], // the question card on the night desk, the paper version list, a form, a printed sheet
        });
        for (const f of fails) note(f, view);
        for (const e of errors) note("script error: " + e, view);
        await ctx.close();
      }
    }
    console.log(`${found.size ? "FAIL" : "ok  "} ${s.name}${found.size ? "  " + found.size + " finding" + (found.size === 1 ? "" : "s") : ""}`);
    for (const [f, views] of found) console.log(`       ${f}   [${[...views].join(", ")}]`);
    total += found.size;
  }
  await browser.close();
  console.log(total ? `\n${total} findings. The rules are in DESIGN.md.` : "\nPASS: every surface meets the design floor in DESIGN.md.");
  process.exit(total ? 1 : 0);
})();
