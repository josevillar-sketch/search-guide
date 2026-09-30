// Acceptance tests for the Room 63 Question Workbench (build spec section 10, tests 1 to 31).
// Run: NODE_PATH="$(npm root -g)" node tools/workbench.cjs
//      NODE_PATH="$(npm root -g)" node tools/workbench.cjs 1 25 30   (only these tests; asking for any of
//      2-10, 12-15 or 31 runs the whole R1 chain 2-10 and 12-15, because each step builds on the one before)
// Prints "ok N Name" or "FAIL N Name: reason" for each test, then "N passed, M failed". Exits 1 on any failure.
//
// Harness (same as smoke.cjs): file:// URL, font hosts aborted, clipboard permissions, DATA parsed from the
// source, and any pageerror (or console error that is not a blocked font) fails the test that was running.
// Tests 2-10 and 12-15 share one context on R1, in order; test 31 runs last on that same context, which is
// still in its state after test 15 (every other test uses its own fresh context). Each test is wrapped, so a
// failure is recorded and the run goes on to the next test. TODAY is the device's local ISO date.
//
// Ambiguities, resolved by the most literal reading:
// - Text is compared as rendered: innerText, trimmed, whitespace runs collapsed. So CSS text-transform caps
//   count, and an inline SVG icon adds no text. Field values are compared exactly.
// - "Click" on a native radio or checkbox that is visually hidden (a chip): when the input's box is under 8px,
//   the test taps the middle of its label with the mouse, which is what a student taps. A DOM click is the
//   last resort, used only if the tap did not change the input.
// - Test 9 "its panel" is the element named by the button's aria-controls.
// - Test 10 "never exist for R1 or RQM": R1 is checked at every step of the chain; RQM gets its own fresh
//   context (load, circle one word, check again) so the R1 chain is not disturbed.
// - Test 11 uses one fresh context and a full page load per student.
// - Test 12 "each del starts with the sr": the first non-blank child node is span.sr whose text starts
//   "removed:" (del) or "added:" (ins).
// - Test 16 "the Example question" is #myq's original value (1.3): the textarea's content in the source,
//   which has quotation marks around "bus-stop benches".
// - Test 17 starts from a fresh context, so it saves V2 on R1 first. "Reload with no hash" is a full load
//   of the file URL without a fragment.
// - Test 20 "The form works": saving V2 shows #vl and stores a readable record with one version.
// - Test 21 completes {"schema":2,...} as an otherwise valid record with one version. "#q-open is disabled"
//   accepts the disabled property or aria-disabled="true". The dot is clicked with force (it may be disabled).
// - Test 22 gives the older record rec.asof "2026-08-20" (the spec leaves it open).
// - Test 25: "every disclosure open" means every <details> is open and every rendered
//   button[aria-expanded="false"] has been clicked. "Compare filled" means From is the record and #cmp-out has
//   text. R1's three versions are seeded into storage in the 6.2 shape, so a broken Save cannot hide the
//   layout results. Opening the form focuses #wb-text, and 2.1 makes the rail static while typing, so focus
//   leaves the field before the 820 sticky check. Overflow is asserted only at the three listed sizes;
//   1024x768 gets only the sticky and edge check. Both themes are run at every size.
// - Test 27: "X against Y" uses Y's computed background-color, composited over its ancestors when it is not
//   opaque. "Its panel" is the nearest ancestor of the .check row with a background. The dot ring is the
//   ::before border-top-color, and a ::before with no border fails.
// - Test 28: "keyboard-focus" means real Tab and Shift+Tab presses land on the element. The ring must also
//   be drawn (outline-style not none). Both themes, at 820x1180.
// - Test 29 samples document.getAnimations() at 0, 60, 200 and 400 ms after the Save click.
// - Test 30: `Inter`, `Roboto`, `Arial` "as font names" means inside a font or font-family declaration, a
//   fontFamily assignment, a CSS custom property or a Google Fonts family= parameter, outside the DATA line.
//   The other strings are matched as written (case-sensitive substrings). The RULE comment must match 9.1
//   word for word. \p{Extended_Pictographic} is searched in the whole file, DATA included.
// - Test 31 splits each text node (outside .sr) on whitespace and compares exact tokens.
const { chromium } = require("playwright");
const path = require("path");
const fs = require("fs");

// WB_INDEX points the suite at another copy of the page (used only to self-test this harness).
const INDEX = process.env.WB_INDEX ? path.resolve(process.env.WB_INDEX) : path.resolve(__dirname, "..", "index.html");
const FILE = "file://" + INDEX;
const SRC = fs.readFileSync(INDEX, "utf8");
const DATA = JSON.parse(SRC.match(/var DATA = (\[.*?\]);\n/s)[1]);
const byId = (id) => {
  const d = DATA.find((x) => x.id === id);
  if (!d) throw new Error("fixture missing from DATA: " + id);
  return d;
};

// Fixtures (10)
const R1 = "p1-nayibeborot";
const SYN = "p7-anabelalfonso"; // Seminar, starts with "Should"
const SQM = "p5-matthewdavila"; // Seminar, no "?"
const RQM = "p1-sofiagil"; // Research, no "?"
const NOQ = "p7-christophelopez"; // no question, topic known
const NT = "p3-chabelyborges"; // nt
const OTHER = "p1-leanacaballerogonza"; // test 16
const R1D = byId(R1);
const KEY = "r63sg_wb_" + R1;
const FIRST = R1D.n.split(" ")[0];

// Test strings (10), plus the few more the tests type as the student.
const V2 = "How does social media use affect sleep among high school athletes in Miami-Dade?";
const WHY = "Added a place: it was too big.";
const V3 = "How does social media use affect sleep among high school athletes in Miami-Dade during the 2026 season?";
const WHY3 = "Added a time.";
const V7 = "How does social media use affect sleep among high school swimmers in Miami-Dade?"; // test 7
const WHY7 = "Changed the group to swimmers."; // test 7
const V3FIX = "How does social media use affect sleep among high school athletes in Miami-Dade during the 2026-27 season?"; // test 15
const V4 = "How does social media use affect sleep among high school athletes in Miami-Dade during the 2026 football season?"; // tests 25
const WHY4 = "Named the season."; // test 25
const NOQ_TEXT = "How do guides written for teens change what teens in Miami do after school?"; // test 23
const NOQ_WHY = "This is my first version, from my log."; // test 23
// Test 31: every question text on the R1 chain is built only from these tokens.
const ALLOWED = new Set([R1D.q, V2, WHY, V7, WHY7, V3, WHY3, V3FIX].flatMap((s) => s.trim().split(/\s+/)));

const RULE = "/* RULE: every question string rendered comes from DATA[i].q or from text this student typed. Nothing here builds, completes, reorders, narrows, scores or suggests question wording. */";

// Dates (4): fixed arrays, never toLocaleDateString. TODAY is the device's local date.
const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
const SHORT = ["Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug", "Sept", "Oct", "Nov", "Dec"];
const pad = (n) => String(n).padStart(2, "0");
const NOW = new Date();
const TODAY = `${NOW.getFullYear()}-${pad(NOW.getMonth() + 1)}-${pad(NOW.getDate())}`;
const ymd = (iso) => iso.split("-").map(Number);
const fmtLong = (iso) => { const [y, m, d] = ymd(iso); return `${MONTHS[m - 1]} ${d}, ${y}`; }; // "October 1, 2026"
const fmtMeta = (iso) => { const [y, m, d] = ymd(iso); return `${SHORT[m - 1]} ${d}, ${y}`.toUpperCase(); }; // "SEPT 29, 2026"
const ASOF = "2026-09-29";

const TEST_MS = 150000; // hard stop for one test
const ACTION_MS = 5000; // Playwright action timeout
const CHAIN = [2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15];

let browser = null;
let T = null; // the running test: { fails, errors, cleanup }
let SHARED = null; // the R1 chain context from test 2
const results = [];

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const J = (v) => JSON.stringify(v);
const clip = (s, n = 160) => (s && s.length > n ? s.slice(0, n) + "…" : s);

// ---------- harness ----------
function check(ok, msg) { if (!ok) T.fails.push(msg); return !!ok; }
function must(ok, msg) { if (!ok) throw new Error(msg); }

function wire(page) {
  page.on("pageerror", (e) => { if (T) T.errors.push("pageerror: " + e.message); });
  page.on("console", (m) => {
    if (m.type() === "error" && !/fonts\.g|net::ERR|Failed to load resource/.test(m.text()) && T) T.errors.push("console: " + m.text());
  });
}
async function newCtx(opts = {}) {
  const ctx = await browser.newContext({ permissions: ["clipboard-read", "clipboard-write"], ...opts });
  ctx.setDefaultTimeout(ACTION_MS);
  // Fonts are decoration; block them so the test runs offline and the fallbacks render.
  await ctx.route(/fonts\.(googleapis|gstatic)\.com/, (r) => r.abort());
  const page = await ctx.newPage();
  wire(page);
  return { ctx, page };
}
async function fresh(opts) {
  const c = await newCtx(opts);
  T.cleanup.push(() => c.ctx.close());
  return c;
}
function chain() {
  if (!SHARED) throw new Error("the shared R1 context from test 2 is missing");
  return SHARED.page;
}
// A full page load (never a same-document hash change).
async function load(page, hash) {
  await page.goto("about:blank");
  await page.goto(FILE + (hash ? "#" + hash : ""));
}
function withTimeout(p, ms) {
  let t;
  return Promise.race([p, new Promise((_, rej) => { t = setTimeout(() => rej(new Error(`timed out after ${ms / 1000}s`)), ms); })])
    .finally(() => clearTimeout(t));
}
function errLine(e) {
  const lines = String((e && e.message) || e).replace(/\x1b\[[0-9;]*m/g, "").split("\n");
  const wait = lines.find((l) => /waiting for/.test(l));
  return lines[0] + (wait ? " (" + wait.trim().replace(/^- /, "") + ")" : "");
}
async function run(num, name, fn) {
  T = { fails: [], errors: [], cleanup: [] };
  let thrown = null;
  try { await withTimeout(fn(), TEST_MS); } catch (e) { thrown = e; }
  await sleep(30);
  for (const c of T.cleanup.reverse()) { try { await c(); } catch (e) { /* already closed */ } }
  const why = T.fails.slice(0, 4);
  if (T.fails.length > 4) why.push(`(+${T.fails.length - 4} more)`);
  if (thrown) why.push("stopped: " + errLine(thrown));
  if (T.errors.length) why.push("page errors: " + T.errors.slice(0, 3).join(" / "));
  const ok = why.length === 0;
  results.push({ num, name, ok });
  console.log(ok ? `ok ${num} ${name}` : `FAIL ${num} ${name}: ${why.join("; ")}`);
  T = null;
}

// ---------- reads (never wait) ----------
const q = {
  text: (page, sel) => page.evaluate((s) => {
    const e = document.querySelector(s);
    if (!e) return null;
    const t = typeof e.innerText === "string" ? e.innerText : e.textContent;
    return t.replace(/\s+/g, " ").trim();
  }, sel),
  texts: (page, sel) => page.evaluate((s) => Array.from(document.querySelectorAll(s)).map((e) => (typeof e.innerText === "string" ? e.innerText : e.textContent).replace(/\s+/g, " ").trim()), sel),
  value: (page, sel) => page.evaluate((s) => { const e = document.querySelector(s); return e ? e.value : null; }, sel),
  attr: (page, sel, a) => page.evaluate(([s, a2]) => { const e = document.querySelector(s); return e ? e.getAttribute(a2) : null; }, [sel, a]),
  checked: (page, sel) => page.evaluate((s) => { const e = document.querySelector(s); return e ? !!e.checked : null; }, sel),
  count: (page, sel) => page.evaluate((s) => document.querySelectorAll(s).length, sel),
  exists: (page, sel) => page.evaluate((s) => !!document.querySelector(s), sel),
  vis: (page, sel) => page.locator(sel).first().isVisible(),
  focus: (page) => page.evaluate(() => (document.activeElement ? document.activeElement.id || "(" + document.activeElement.tagName.toLowerCase() + " without id)" : null)),
  style: (page, sel, prop) => page.evaluate(([s, p]) => { const e = document.querySelector(s); return e ? getComputedStyle(e)[p] : null; }, [sel, prop]),
  store: (page, k) => page.evaluate((k2) => { try { return localStorage.getItem(k2); } catch (e) { return "(localStorage threw)"; } }, k),
};

// Poll until fn() reports ok, or the time runs out; returns the last { ok, got }.
async function poll(fn, ms = 1500) {
  const end = Date.now() + ms;
  for (;;) {
    let r;
    try { r = await fn(); } catch (e) { r = { ok: false, got: "(read failed: " + errLine(e) + ")" }; }
    if (r.ok || Date.now() > end) return r;
    await sleep(50);
  }
}

// ---------- assertions (poll briefly, record a clear failure, go on) ----------
const HOW = { eq: "should be", has: "should contain", starts: "should start with", ends: "should end with" };
function textMatch(got, want, how) {
  if (got == null) return false;
  if (how === "has") return got.includes(want);
  if (how === "starts") return got.startsWith(want);
  if (how === "ends") return got.endsWith(want);
  return got === want;
}
async function expectText(page, sel, want, how = "eq") {
  const r = await poll(async () => { const got = await q.text(page, sel); return { ok: textMatch(got, want, how), got }; });
  return check(r.ok, r.got == null ? `${sel} is missing` : `${sel} ${HOW[how]} ${J(want)}, got ${J(clip(r.got))}`);
}
async function expectValue(page, sel, want) {
  const r = await poll(async () => { const got = await q.value(page, sel); return { ok: got === want, got }; });
  return check(r.ok, r.got == null ? `${sel} is missing` : `${sel} value should be ${J(want)}, got ${J(clip(r.got))}`);
}
async function expectAttr(page, sel, attr, want) {
  const r = await poll(async () => { const got = await q.attr(page, sel, attr); return { ok: got === want, got }; });
  return check(r.ok, `${sel} [${attr}] should be ${J(want)}, got ${J(r.got)}`);
}
async function expectCount(page, sel, want, desc) {
  const test = typeof want === "function" ? want : (n) => n === want;
  const r = await poll(async () => { const got = await q.count(page, sel); return { ok: test(got), got }; });
  return check(r.ok, `${sel} count ${desc || "should be " + want}, got ${r.got}`);
}
async function expectVisible(page, sel, ms) {
  const r = await poll(async () => ({ ok: await q.vis(page, sel) }), ms);
  return check(r.ok, (await q.exists(page, sel)) ? `${sel} should be visible` : `${sel} is missing (should be visible)`);
}
// Hidden, and present in the DOM (so a missing element never passes).
async function expectHidden(page, sel) {
  const r = await poll(async () => { const ex = await q.exists(page, sel); return { ok: ex && !(await q.vis(page, sel)), got: ex }; });
  return check(r.ok, r.got ? `${sel} should be hidden` : `${sel} is missing (should be present and hidden)`);
}
// Not visible; removed from the DOM also counts.
async function expectGone(page, sel) {
  const r = await poll(async () => ({ ok: !(await q.vis(page, sel)) }));
  return check(r.ok, `${sel} should not be visible`);
}
async function expectFocus(page, id) {
  const r = await poll(async () => { const got = await q.focus(page); return { ok: got === id, got }; });
  return check(r.ok, `focus should be #${id}, got ${r.got ? (/^\(/.test(r.got) ? r.got : "#" + r.got) : "nothing"}`);
}
async function expectStyle(page, sel, prop, want) {
  const r = await poll(async () => { const got = await q.style(page, sel, prop); return { ok: got === want, got }; });
  return check(r.ok, `${sel} computed ${prop} should be ${J(want)}, got ${J(r.got)}`);
}
async function mustVisible(page, sel, ms = 2000) {
  const r = await poll(async () => ({ ok: await q.vis(page, sel) }), ms);
  must(r.ok, `${sel} did not become visible`);
}

// ---------- page actions ----------
// Tap a native radio or checkbox. A chip hides its input, so tap the middle of its visible label then,
// where a student's finger goes. (Playwright retargets any click on a label to the label's control, which
// for a 1px clipped input lands on whatever is around it, so the label is tapped with the mouse directly.)
async function tapInput(page, sel) {
  const loc = page.locator(sel).first();
  must((await loc.count()) > 0, `${sel} is missing`);
  const before = await loc.evaluate((el) => !!el.checked);
  const took = () => loc.evaluate((el, b) => (el.type === "radio" ? el.checked : el.checked !== b), before);
  const box = await loc.evaluate((el) => { const r = el.getBoundingClientRect(); return { w: r.width, h: r.height }; });
  if (box.w >= 8 && box.h >= 8) {
    try { await loc.click({ timeout: 2000 }); } catch (e) { /* covered: tap the label instead */ }
    if (await took()) return;
  }
  const pt = await loc.evaluate((el) => {
    const lab = (el.labels && el.labels[0]) || el.closest("label");
    if (!lab) return null;
    lab.scrollIntoView({ block: "center", behavior: "instant" });
    const r = lab.getBoundingClientRect();
    return r.width && r.height ? { x: r.left + r.width / 2, y: r.top + r.height / 2 } : null;
  });
  if (pt) {
    await page.mouse.click(pt.x, pt.y);
    if (await took()) return;
  }
  await loc.evaluate((el) => el.click()); // last resort
}
async function selectBy(page, sel, re) {
  const idx = await page.$eval(sel, (s, src) => Array.from(s.options).findIndex((o) => new RegExp(src).test(o.textContent.trim())), re.source);
  must(idx >= 0, `${sel} has no option matching ${re}`);
  await page.selectOption(sel, { index: idx });
}
async function selectedText(page, sel) {
  return page.evaluate((s) => { const e = document.querySelector(s); return e && e.selectedIndex >= 0 ? e.options[e.selectedIndex].textContent.trim() : null; }, sel);
}
// Close the form if an earlier failure left it open, so the next step starts where the spec expects.
async function settle(page) {
  try {
    if (await q.vis(page, "#wb-form")) {
      await page.click("#wb-cancel", { timeout: 2000 });
      await sleep(100);
      if (await q.vis(page, "#wb-confirm-drop")) await page.click("#wb-confirm-drop", { timeout: 2000 });
    }
  } catch (e) { /* the test that follows reports what is wrong */ }
}
async function saveVersion(page, { text, why, n }) {
  if (!(await q.vis(page, "#wb-form"))) await page.click("#q-open");
  await mustVisible(page, "#wb-form");
  await page.fill("#wb-text", text);
  await page.fill("#wb-why", why);
  if (n != null) await page.fill("#wb-n", String(n));
  await page.click("#wb-save");
  const r = await poll(async () => ({ ok: !(await q.vis(page, "#wb-form")) }), 2500);
  must(r.ok, `Save left the form open (errors: ${J(await q.texts(page, "#wb-form [id$='-err']"))})`);
}
async function readRecord(page) {
  const raw = await q.store(page, KEY);
  if (raw == null) return { raw, obj: null, err: `no ${KEY} in localStorage` };
  try { return { raw, obj: JSON.parse(raw), err: null }; } catch (e) { return { raw, obj: null, err: "unreadable: " + clip(raw, 60) }; }
}
async function pollRecord(page, pred, ms = 1500) {
  return poll(async () => { const r = await readRecord(page); let ok = false; try { ok = !!pred(r.obj); } catch (e) { ok = false; } return { ok, got: r }; }, ms);
}
function describeRec(r) {
  if (!r.obj) return r.err;
  const o = r.obj;
  const vs = Array.isArray(o.versions) ? o.versions : [];
  return `schema ${J(o.schema)}, ${vs.length} version(s) ${J(vs.map((v) => ({ n: v.n, text: clip(v.text, 40), prev: clip(v.prev, 40) })))}, rec.leads ${J(o.rec && o.rec.leads)}`;
}
function freshSheet() { return { dots: [0, 0, 0, 0, 0, 0, 0], circles: [], lenses: [], purpose: "", expect: "", hate: "" }; }
// A record in the 6.2 shape for R1.
function record(versions, recQ = R1D.q, schema = 1) {
  const t = Date.now();
  return {
    schema, id: R1, course: "R",
    rec: { q: recQ, asof: ASOF, leads: false, sheet: freshSheet() },
    versions: versions.map((v, i) => ({
      k: "wbtest" + i, n: v.n, date: v.date || TODAY, text: v.text, prev: v.prev, why: v.why, reason: "", rc: 0,
      saved: t - 60000 + i * 1000, penned: false, sheet: Object.assign(freshSheet(), v.sheet || {}),
    })),
    draft: null, updated: t,
  };
}
async function seed(page, obj) {
  await load(page);
  await page.evaluate(([k, v]) => localStorage.setItem(k, v), [KEY, typeof obj === "string" ? obj : JSON.stringify(obj)]);
}
// Record every text #wb-live shows from now on, so a message replaced a moment later still counts.
async function watchLive(page) {
  await page.evaluate(() => {
    window.__wbLive = [];
    if (window.__wbLiveObs) window.__wbLiveObs.disconnect();
    const note = () => {
      const e = document.getElementById("wb-live");
      const t = e ? e.textContent : "";
      const L = window.__wbLive;
      if (t && L[L.length - 1] !== t) L.push(t);
    };
    window.__wbLiveObs = new MutationObserver(note);
    window.__wbLiveObs.observe(document.documentElement, { subtree: true, childList: true, characterData: true });
  });
}
async function expectLive(page, sub, ms = 2500) {
  const r = await poll(async () => {
    const seen = await page.evaluate(() => { const e = document.getElementById("wb-live"); return (window.__wbLive || []).concat(e ? [e.textContent] : ["(no #wb-live)"]); });
    return { ok: seen.some((s) => s.includes(sub)), got: seen };
  }, ms);
  return check(r.ok, `#wb-live should contain ${J(sub)}, saw ${J((r.got || []).slice(-3).map((s) => clip(s, 90)))}`);
}
async function setClipboard(page, text) {
  await page.evaluate((t) => navigator.clipboard.writeText(t).catch(() => {}), text).catch(() => {});
}
async function readClipboard(page) {
  return page.evaluate(() => navigator.clipboard.readText());
}
// The original value of #myq: the textarea's content in the source (1.3 "resets #myq to its original value").
function exampleMyq(src) {
  const m = src.match(/<textarea\b[^>]*\bid=["']?myq\b[^>]*>([\s\S]*?)<\/textarea>/);
  if (!m) return null;
  return m[1].replace(/^\r?\n/, "").replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&");
}
// Put keyboard focus on sel with real key presses, so :focus-visible is the keyboard kind.
async function kbFocus(page, sel) {
  const on = () => page.$eval(sel, (e) => document.activeElement === e).catch(() => false);
  await page.focus(sel);
  await page.keyboard.press("Shift+Tab");
  await page.keyboard.press("Tab");
  if (!(await on())) {
    await page.focus(sel);
    await page.keyboard.press("Tab");
    await page.keyboard.press("Shift+Tab");
  }
  if (!(await on())) {
    await page.evaluate(() => { if (document.activeElement && document.activeElement.blur) document.activeElement.blur(); });
    for (let i = 0; i < 400 && !(await on()); i++) await page.keyboard.press("Tab");
  }
  must(await on(), `the Tab key never reached ${sel}`);
}
async function ringOf(page, sel) {
  await kbFocus(page, sel);
  return page.$eval(sel, (e) => {
    const cs = getComputedStyle(e);
    const cv = document.createElement("canvas");
    cv.width = cv.height = 1;
    const x = cv.getContext("2d");
    x.clearRect(0, 0, 1, 1);
    x.fillStyle = "rgba(0,0,0,0)";
    x.fillStyle = cs.outlineColor;
    x.fillRect(0, 0, 1, 1);
    const d = x.getImageData(0, 0, 1, 1).data;
    return { color: `rgb(${d[0]}, ${d[1]}, ${d[2]})`, raw: cs.outlineColor, style: cs.outlineStyle, width: cs.outlineWidth, fv: e.matches(":focus-visible") };
  });
}
function checkRing(tag, sel, r, want) {
  check(r.fv, `${tag}: ${sel} is not :focus-visible after keyboard focus`);
  check(r.style !== "none" && parseFloat(r.width) > 0, `${tag}: ${sel} draws no outline (style ${r.style}, width ${r.width})`);
  check(r.color === want, `${tag}: ${sel} outline color should be ${want}, got ${r.color} (${r.raw})`);
}

// Contrast (WCAG 2.x) of computed colors, measured inside the page (test 27).
function contrastProbe() {
  const cv = document.createElement("canvas");
  cv.width = cv.height = 1;
  const x = cv.getContext("2d", { willReadFrequently: true });
  const rgba = (c) => {
    x.clearRect(0, 0, 1, 1);
    x.fillStyle = "rgba(0,0,0,0)";
    x.fillStyle = c;
    x.fillRect(0, 0, 1, 1);
    const d = x.getImageData(0, 0, 1, 1).data;
    return [d[0], d[1], d[2], d[3] / 255];
  };
  const over = (top, base) => [0, 1, 2].map((i) => top[i] * top[3] + base[i] * (1 - top[3]));
  // The color behind an element: its background-color, composited over its ancestors' until one is opaque.
  const bgOf = (el) => {
    const layers = [];
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
      const c = rgba(getComputedStyle(n).backgroundColor);
      if (c[3] > 0) { layers.push(c); if (c[3] >= 0.999) break; }
    }
    let base = [255, 255, 255];
    for (let i = layers.length - 1; i >= 0; i--) base = over(layers[i], base);
    return base;
  };
  const lin = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
  const lum = (c) => 0.2126 * lin(c[0]) + 0.7152 * lin(c[1]) + 0.0722 * lin(c[2]);
  const ratio = (a, b) => { const la = lum(a) + 0.05, lb = lum(b) + 0.05; return la > lb ? la / lb : lb / la; };
  const hex = (c) => "#" + c.map((v) => Math.round(v).toString(16).padStart(2, "0")).join("");
  const out = [];
  const add = (label, el, bgEl, min, pseudo) => {
    if (!el || !bgEl) { out.push({ label, ok: false, msg: "is missing" }); return; }
    const bg = bgOf(bgEl);
    let fgRaw;
    if (pseudo) {
      const ps = getComputedStyle(el, "::before");
      if (ps.borderTopStyle === "none" || !(parseFloat(ps.borderTopWidth) > 0)) { out.push({ label, ok: false, msg: `has no ::before border (${ps.borderTopStyle} ${ps.borderTopWidth})` }); return; }
      fgRaw = rgba(ps.borderTopColor);
    } else {
      fgRaw = rgba(getComputedStyle(el).color);
    }
    const fg = fgRaw[3] < 1 ? over(fgRaw, bg) : fgRaw.slice(0, 3);
    const r = ratio(fg, bg);
    out.push({ label, ok: r >= min, msg: `${r.toFixed(2)} (${hex(fg)} on ${hex(bg)}), needs ${min}` });
  };
  const $ = (s) => document.querySelector(s);
  const ficha = $("#ficha");
  add("#ficha-q on #ficha", $("#ficha-q"), ficha, 4.5);
  add("#ficha-meta on #ficha", $("#ficha-meta"), ficha, 4.5);
  add("#ficha-num .num-v on #ficha", $("#ficha-num .num-v"), ficha, 3);
  add("#who-name on #desk-left", $("#who-name"), $("#desk-left"), 4.5);
  const nav = $("#desk-nav");
  const links = document.querySelectorAll("#desk-nav a");
  if (!links.length) out.push({ label: "#desk-nav a", ok: false, msg: "is missing" });
  links.forEach((a, i) => add(`#desk-nav a${a.id ? "#" + a.id : ":nth(" + i + ")"} on the nav`, a, nav, 4.5));
  const asks = document.querySelectorAll(".check .ck-ask");
  if (!asks.length) out.push({ label: ".check .ck-ask", ok: false, msg: "is missing" });
  asks.forEach((e, i) => add(`.check .ck-ask #${i + 1} on its panel`, e, e.closest(".check"), 4.5));
  const dots = document.querySelectorAll(".check .dot");
  if (!dots.length) out.push({ label: ".check .dot", ok: false, msg: "is missing" });
  dots.forEach((e, i) => add(`.check .dot #${i + 1} ::before ring on its panel`, e, e.closest(".check"), 3, true));
  add("#vl-text on #vl", $("#vl-text"), $("#vl"), 4.5);
  return out;
}

// ---------- the tests ----------
const TESTS = {};

TESTS[1] = ["Example state", async () => {
  const { page } = await fresh();
  await load(page);
  await expectAttr(page, "#desk", "data-on", "false");
  await expectHidden(page, "#desk-left");
  await expectHidden(page, "#desk-nav");
  await expectVisible(page, "#guide .example-tag");
  await expectCount(page, "#guide .slip .search", 3);
}];

TESTS[2] = ["Pick", async () => {
  SHARED = await newCtx();
  const page = SHARED.page;
  await load(page, R1);
  await expectAttr(page, "#desk", "data-on", "true");
  await expectHidden(page, "#pick");
  await expectText(page, "#ficha-q", R1D.q);
  await expectText(page, "#ficha-num .num-v", String(ymd(ASOF)[2])); // "29"
  await expectText(page, "#ficha-meta", "ON RECORD · " + fmtMeta(ASOF)); // "ON RECORD · SEPT 29, 2026"
  await expectText(page, "#guide .qblk .q", R1D.q);
  await expectValue(page, "#myq", R1D.q);
  await expectFocus(page, "ficha-h");
}];

TESTS[3] = ["Open the form", async () => {
  const page = chain();
  await page.click("#q-open");
  await expectVisible(page, "#wb-form");
  await expectFocus(page, "wb-text");
  await expectValue(page, "#wb-text", R1D.q);
  await expectValue(page, "#wb-n", "2");
  await expectValue(page, "#wb-date", TODAY);
  await expectText(page, "#wb-save", `Save Version 2 for ${FIRST}`);
  const values = await page.$$eval("input[name=wb-reason]", (es) => es.map((e) => e.value));
  check(values.length === 7, `expected 7 input[name=wb-reason], found ${values.length}`);
  for (const v of values) {
    const sel = `input[name=wb-reason][value="${v}"]`;
    await tapInput(page, sel);
    check((await q.checked(page, sel)) === true, `clicking reason "${v}" did not check it`);
    const got = await q.value(page, "#wb-text");
    check(got === R1D.q, `#wb-text changed after reason "${v}": ${J(clip(got))}`);
  }
  await sleep(700); // past the 600ms draft debounce
  const after = await q.value(page, "#wb-text");
  check(after === R1D.q, `#wb-text changed after the reason chips settled: ${J(clip(after))}`);
}];

TESTS[4] = ["Validation", async () => {
  const page = chain();
  await page.click("#wb-save");
  await expectText(page, "#wb-text-err", "matches your last version", "has");
  await expectFocus(page, "wb-text");
  await page.fill("#wb-text", V2);
  await page.click("#wb-save");
  await expectVisible(page, "#wb-why-err");
  await expectFocus(page, "wb-why");
}];

TESTS[5] = ["Save", async () => {
  const page = chain();
  await page.fill("#wb-why", WHY);
  await watchLive(page);
  await page.click("#wb-save");
  await expectHidden(page, "#wb-form");
  await expectFocus(page, "vl-h");
  await expectLive(page, "Saved on this iPad as Version 2");
  await expectText(page, "#ficha-q", V2);
  await expectText(page, "#guide .qblk .q", V2);
  await expectValue(page, "#myq", V2);
  await expectText(page, "#ficha-num .num-v", "2");
  await expectVisible(page, "#guide .srch-note");
  await expectText(page, "#tb", "Searches from Version 2");
  const r = await pollRecord(page, (o) => o && o.schema === 1 && Array.isArray(o.versions) && o.versions.length === 1 && o.versions[0].n === 2 && o.versions[0].prev === R1D.q);
  check(r.ok, `${KEY} should hold schema 1 with one version, n 2, prev = DATA.q; it holds ${describeRec(r.got)}`);

  // Tap budget: a separate fresh context on R1. Exactly 2 clicks; the rest is typing.
  const { page: p2 } = await fresh();
  await load(p2, R1);
  let clicks = 0;
  await p2.click("#q-open"); clicks++;
  await p2.fill("#wb-text", V2);
  await p2.fill("#wb-why", WHY);
  await p2.click("#wb-save"); clicks++;
  const vl = await poll(async () => ({ ok: await q.vis(p2, "#vl") }));
  check(clicks === 2 && vl.ok, "tap budget: #vl is not visible after #q-open, typing, and #wb-save (2 clicks)");
}];

TESTS[6] = ["Version line", async () => {
  const page = chain();
  const sentinel = "__workbench_sentinel__";
  await setClipboard(page, sentinel);
  await page.click("#vl-copy");
  const want = `Version 2 · Date ${fmtLong(TODAY)}: ${V2}\nMy last version said: ${R1D.q}\nWhat I changed, and why: ${WHY}\nDots: 0 of 7 filled`;
  const r = await poll(async () => { const got = await readClipboard(page); return { ok: got === want, got }; }, 2500);
  check(r.ok, `clipboard should be ${J(want)}, got ${J(r.got === sentinel ? "(nothing copied)" : r.got)}`);
}];

TESTS[7] = ["Duplicate number", async () => {
  const page = chain();
  await settle(page);
  await page.click("#q-open");
  await mustVisible(page, "#wb-form");
  await page.fill("#wb-n", "2");
  await page.fill("#wb-text", V7);
  await page.fill("#wb-why", WHY7);
  await page.click("#wb-save");
  await expectText(page, "#wb-n-err", "Version 2 is already saved on this iPad. Use the next number in your log.");
  await page.click("#wb-cancel");
  await page.click("#wb-confirm-drop");
  await expectFocus(page, "q-open");
}];

TESTS[8] = ["Dots", async () => {
  const page = chain();
  await settle(page);
  const dot1 = '#checks li.check[data-k="1"] .dot';
  await page.click(dot1);
  await expectAttr(page, dot1, "aria-pressed", "true");
  await expectText(page, "#ck-count", "1 of 7 filled", "starts");
  await expectText(page, "#nav-checks .badge", "1/7");
  await page.reload();
  await expectAttr(page, dot1, "aria-pressed", "true");
  await saveVersion(page, { text: V3, why: WHY3, n: 3 });
  const r = await poll(async () => {
    const got = await page.$$eval("#checks li.check .dot", (ds) => ds.map((d) => d.getAttribute("aria-pressed")));
    return { ok: got.length === 7 && got.every((p) => p === "false"), got };
  });
  check(r.ok, `after saving Version 3 the seven dots should be unpressed, got aria-pressed ${J(r.got)}`);
  await expectVisible(page, "#ck-new");
}];

TESTS[9] = ["Repair", async () => {
  const page = chain();
  await settle(page);
  const btn = page.locator('.check[data-k="4"] .why-fail').first();
  await btn.click();
  const exp = await poll(async () => { const got = await btn.getAttribute("aria-expanded"); return { ok: got === "true", got }; });
  check(exp.ok, `.check[data-k="4"] .why-fail aria-expanded should be "true", got ${J(exp.got)}`);
  const panelId = await btn.getAttribute("aria-controls");
  must(panelId, '.check[data-k="4"] .why-fail has no aria-controls');
  const panel = `[id="${panelId}"]`;
  await expectText(page, panel, "Repair (Plate VII): Add the missing who, where, or when.", "has");
  await page.locator(`${panel} .repair-go`).first().click();
  await mustVisible(page, "#wb-form");
  const ck = await poll(async () => ({ ok: (await q.checked(page, 'input[name=wb-reason][value="check"]')) === true }));
  check(ck.ok, 'the "check" reason (input[name=wb-reason][value="check"]) is not checked');
  await expectValue(page, "#wb-check", "4");
  await expectValue(page, "#wb-text", V3);
  await page.click("#wb-cancel");
  const conf = await poll(async () => ({ ok: await q.vis(page, "#wb-confirm-drop") }), 400);
  if (conf.ok) await page.click("#wb-confirm-drop");
}];

TESTS[10] = ["Circle it and notes", async () => {
  const page = chain();
  await settle(page);
  const noShape = async (p, who, when) => {
    const n = await q.count(p, '[data-note="yesno"], [data-note="qmark"]');
    check(n === 0, `${who} shows a yes-or-no or question-mark note ${when}`);
  };
  check(await q.exists(page, "#notes"), "#notes is missing");
  await expectCount(page, "#notes [data-note]", 0);
  await noShape(page, "R1", "before any circle");
  await tapInput(page, 'input[name=pen][value="who"]');
  await page.click('#words .w[data-i="9"]');
  await expectAttr(page, '#words .w[data-i="9"]', "data-l", "who");
  await expectText(page, "#circ-slots", "Not circled yet", "has");
  await expectCount(page, '[data-note="slots"]', (n) => n > 0, "should be at least 1");
  await expectCount(page, '[data-note="verb"]', (n) => n > 0, "should be at least 1");
  await noShape(page, "R1", "after circling a who");
  await tapInput(page, 'input[name=pen][value="verb"]');
  await page.click('#words .w[data-i="1"]');
  await expectCount(page, '[data-note="verb"]', 0);
  await noShape(page, "R1", "after circling a verb");

  // RQM, in its own fresh context.
  const { page: p } = await fresh();
  await load(p, RQM);
  const ready = await poll(async () => ({ ok: (await q.count(p, "#words .w")) > 0 }));
  must(ready.ok, "RQM: no #words .w to circle");
  await noShape(p, "RQM", "before any circle");
  await p.click('#words .w[data-i="0"]');
  const lit = await poll(async () => ({ ok: (await q.attr(p, '#words .w[data-i="0"]', "data-l")) != null }));
  check(lit.ok, "RQM: tapping word 0 with the default pen did not circle it");
  await noShape(p, "RQM", "after a circle");
}];

TESTS[11] = ["Seminar notes", async () => {
  const { page } = await fresh();
  await load(page, SYN);
  await expectText(page, '[data-note="yesno"]', "starts with “Should.”", "has");
  await load(page, SQM);
  await expectCount(page, '[data-note="qmark"]', (n) => n > 0, "should be at least 1");
  await load(page, RQM);
  const ready = await poll(async () => ({ ok: await q.exists(page, "#notes") }));
  check(ready.ok, "RQM: #notes is missing");
  await expectCount(page, '[data-note="qmark"]', 0);
}];

TESTS[12] = ["Diff", async () => {
  const page = chain();
  await settle(page);
  const from0 = await selectedText(page, "#cmp-from");
  const to0 = await selectedText(page, "#cmp-to");
  check(/^Version 2\b/.test(from0 || "") && /^Version 3\b/.test(to0 || ""), `compare defaults should be Version 2 → Version 3, got ${J(from0)} → ${J(to0)}`);
  await selectBy(page, "#cmp-from", /^On record/);
  await selectBy(page, "#cmp-to", /^Version 2\b/);
  await expectText(page, "#cmp-sum", "2 words out · 3 words in");
  const dels = await poll(async () => { const got = await q.texts(page, "#cmp-out del"); return { ok: got.some((t) => t.includes("mental health")), got }; });
  check(dels.ok, `#cmp-out del should include "mental health", got ${J(dels.got)}`);
  await expectCount(page, "#cmp-out ins", (n) => n >= 2, "should be at least 2");
  const marks = await page.$$eval("#cmp-out del, #cmp-out ins", (es) => es.map((e) => {
    let n = e.firstChild;
    while (n && n.nodeType === 3 && !n.textContent.trim()) n = n.nextSibling;
    const sr = n && n.nodeType === 1 && n.tagName === "SPAN" && n.classList.contains("sr") ? n.textContent : null;
    return { tag: e.tagName.toLowerCase(), sr };
  }));
  check(marks.length > 0, "#cmp-out has no del or ins");
  marks.forEach((m, i) => {
    const want = m.tag === "del" ? "removed:" : "added:";
    check(m.sr != null && m.sr.trim().startsWith(want), `#cmp-out ${m.tag} #${i + 1} should start with <span class="sr">${want} </span>, got ${J(m.sr)}`);
  });
}];

TESTS[13] = ["Timeline", async () => {
  const page = chain();
  await settle(page);
  await expectCount(page, "#timeline li.ver", 3);
  await expectAttr(page, "#timeline li.ver", "data-n", "3");
  const last = await page.$$eval("#timeline li.ver", (ls) => (ls.length ? ls[ls.length - 1].className : null));
  check(last != null && /(^|\s)rec(\s|$)/.test(last), `the last #timeline li.ver should have class rec, got ${J(last)}`);
}];

TESTS[14] = ["In your log", async () => {
  const page = chain();
  await settle(page);
  await tapInput(page, "#vl-penned");
  check((await q.checked(page, "#vl-penned")) === true, "#vl-penned did not become checked");
  await expectGone(page, "#vl-edit");
  await expectGone(page, "#vl-remove");
  await expectText(page, "#ficha-stamp", "IN YOUR LOG");
  await tapInput(page, "#vl-penned");
  check((await q.checked(page, "#vl-penned")) === false, "#vl-penned did not become unchecked");
  await expectVisible(page, "#vl-edit");
  await expectVisible(page, "#vl-remove");
}];

TESTS[15] = ["Fix and remove", async () => {
  const page = chain();
  await settle(page);
  const before = await readRecord(page);
  must(before.obj && Array.isArray(before.obj.versions), "no readable stored record before the fix: " + before.err);
  const count0 = before.obj.versions.length;
  await page.click("#vl-edit");
  await mustVisible(page, "#wb-form");
  await page.fill("#wb-text", V3FIX);
  await page.click("#wb-save");
  await expectHidden(page, "#wb-form");
  const fixed = await pollRecord(page, (o) => {
    const v = o.versions.find((x) => x.n === 3);
    return o.versions.length === count0 && v && v.text === V3FIX && v.sheet && Array.isArray(v.sheet.circles) && v.sheet.circles.length === 0;
  });
  if (!fixed.ok) {
    const o = fixed.got.obj;
    const v = o && Array.isArray(o.versions) ? o.versions.find((x) => x.n === 3) : null;
    check(o && o.versions && o.versions.length === count0, `version count should stay ${count0}, got ${o && o.versions ? o.versions.length : fixed.got.err}`);
    check(v && v.text === V3FIX, `Version 3 text should be updated to ${J(V3FIX)}, got ${J(v && v.text)}`);
    check(v && v.sheet && Array.isArray(v.sheet.circles) && v.sheet.circles.length === 0, `Version 3 circles should be empty, got ${J(v && v.sheet && v.sheet.circles)}`);
  }
  await page.click("#vl-remove");
  await page.click("#vl-remove-yes");
  await expectFocus(page, "ficha-h");
  const removed = await pollRecord(page, (o) => o.versions.length === count0 - 1 && !o.versions.some((x) => x.n === 3));
  check(removed.ok, `after Remove, Version 3 should be gone (${count0 - 1} left); stored: ${describeRec(removed.got)}`);
}];

TESTS[16] = ["Shared iPad", async () => {
  const { page } = await fresh();
  await load(page, R1);
  await saveVersion(page, { text: V2, why: WHY });
  await page.click("#who-not");
  await expectVisible(page, "#pick");
  const last = await q.store(page, "r63sg_last");
  check(last === null, `localStorage.r63sg_last should be null, got ${J(last)}`);
  const wb = await q.store(page, KEY);
  check(wb !== null, `${KEY} should still exist`);
  const example = exampleMyq(fs.readFileSync(INDEX, "utf8")) ?? (await page.$eval("#myq", (e) => e.defaultValue));
  await expectValue(page, "#myq", example);
  await page.click('#periods .chip[data-p="1"]');
  await page.click(`#names .name[data-id="${OTHER}"]`);
  const other = byId(OTHER);
  const on = await poll(async () => ({ ok: (await q.text(page, "#ficha-q")) === other.q }));
  must(on.ok, `picking ${OTHER} did not open her desk`);
  const html = await page.content();
  check(!html.includes(V2), `page.content() still contains V2 after picking ${OTHER}`);
}];

TESTS[17] = ["Welcome back", async () => {
  const { page } = await fresh();
  await load(page, R1);
  await saveVersion(page, { text: V2, why: WHY });
  await load(page); // reload with no hash
  await expectVisible(page, "#back");
  await expectText(page, "#back", "Your desk is on this iPad", "has");
  await page.click("#back button.go");
  await expectText(page, "#ficha-q", V2);
}];

TESTS[18] = ["Storage off", async () => {
  const { ctx, page } = await fresh();
  await ctx.addInitScript(() => {
    Storage.prototype.setItem = function () { throw new DOMException("Storage is off for this test.", "QuotaExceededError"); };
  });
  await load(page, R1);
  await expectVisible(page, "#store-banner");
  await page.click("#q-open");
  await mustVisible(page, "#wb-form");
  await expectText(page, "#wb-save", "Show my version line");
  await page.fill("#wb-text", V2);
  await page.fill("#wb-why", WHY);
  await page.click("#wb-save");
  await expectVisible(page, "#vl");
  await expectText(page, "#ficha-num .num-v", "2");
}];

TESTS[19] = ["Quota mid-session", async () => {
  const { ctx, page } = await fresh();
  await ctx.addInitScript(() => {
    const orig = Storage.prototype.setItem;
    Storage.prototype.setItem = function (k, v) {
      if (String(k).indexOf("r63sg_wb_") === 0) throw new DOMException("The quota has been exceeded.", "QuotaExceededError");
      return orig.call(this, k, v);
    };
  });
  await load(page, R1);
  await page.click("#q-open");
  await mustVisible(page, "#wb-form");
  await page.fill("#wb-text", V2);
  await page.fill("#wb-why", WHY);
  await watchLive(page);
  await page.click("#wb-save");
  await expectLive(page, "This iPad did not save it.");
  await expectVisible(page, "#store-banner");
}];

TESTS[20] = ["Corrupt record", async () => {
  const { page } = await fresh();
  await load(page, R1);
  await page.evaluate((k) => localStorage.setItem(k, "{not json"), KEY);
  await page.reload();
  const bad = await poll(async () => {
    const kv = await page.evaluate(() => { const o = {}; for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i); o[k] = localStorage.getItem(k); } return o; });
    const keys = Object.keys(kv).filter((k) => /^r63sg_bad_p1-nayibeborot_\d+$/.test(k));
    return { ok: keys.some((k) => kv[k] === "{not json"), got: keys.map((k) => [k, kv[k]]) };
  });
  check(bad.ok, `a key matching ^r63sg_bad_p1-nayibeborot_\\d+$ should hold "{not json", found ${J(bad.got)}`);
  await expectText(page, "#wb-notice", "could not be read", "has");
  await saveVersion(page, { text: V2, why: WHY });
  await expectVisible(page, "#vl");
  const r = await pollRecord(page, (o) => o && Array.isArray(o.versions) && o.versions.length === 1 && o.versions[0].text === V2);
  check(r.ok, `after a save, ${KEY} should hold one version with V2; it holds ${describeRec(r.got)}`);
}];

TESTS[21] = ["Newer schema", async () => {
  const { page } = await fresh();
  await load(page, R1);
  const raw = JSON.stringify(record([{ n: 2, text: V2, prev: R1D.q, why: WHY, date: "2026-09-15" }], R1D.q, 2));
  await page.evaluate(([k, v]) => localStorage.setItem(k, v), [KEY, raw]);
  await page.reload();
  await expectText(page, "#wb-notice", "newer Search Guide", "has");
  const dis = await poll(async () => {
    const got = await page.evaluate(() => { const b = document.getElementById("q-open"); return b ? { disabled: !!b.disabled, aria: b.getAttribute("aria-disabled") } : null; });
    return { ok: !!got && (got.disabled || got.aria === "true"), got };
  });
  check(dis.ok, `#q-open should be disabled, got ${J(dis.got)}`);
  const dot = '#checks li.check[data-k="1"] .dot';
  const has = await poll(async () => ({ ok: await q.exists(page, dot) }));
  check(has.ok, `${dot} is missing (read-only still renders what validates)`);
  if (has.ok) await page.locator(dot).first().click({ force: true, timeout: 2000 }).catch(() => {});
  await sleep(900); // past any debounce
  const after = await q.store(page, KEY);
  check(after === raw, `the stored string changed after a dot click in read-only mode: ${J(clip(after, 120))}`);
}];

TESTS[22] = ["Record newer", async () => {
  const { page } = await fresh();
  await load(page, R1);
  const old = record([{ n: 2, text: V2, prev: "An older question?", why: WHY, date: "2026-09-01" }], "An older question?");
  old.rec.asof = "2026-08-20";
  await page.evaluate(([k, v]) => localStorage.setItem(k, v), [KEY, JSON.stringify(old)]);
  await page.reload();
  await expectVisible(page, "#rec-ask");
  await page.click("#rec-ask-record");
  await expectText(page, "#ficha-q", R1D.q);
  await expectText(page, "#ficha-meta", "ON RECORD", "starts");
  const r = await pollRecord(page, (o) => o && o.rec && o.rec.leads === true);
  check(r.ok, `the stored rec.leads should be true; stored: ${describeRec(r.got)}`);
}];

TESTS[23] = ["No question", async () => {
  const { page } = await fresh();
  const noq = byId(NOQ);
  await load(page, NOQ);
  await expectText(page, "#ficha-q", "Topic: " + noq.tp);
  await expectText(page, "#q-open", "Save my first version");
  await page.click("#q-open");
  await mustVisible(page, "#wb-form");
  await expectValue(page, "#wb-text", "");
  await expectValue(page, "#wb-n", "1");
  await page.fill("#wb-text", NOQ_TEXT);
  await page.fill("#wb-why", NOQ_WHY);
  await page.click("#wb-save");
  await expectText(page, '#vl-text [data-line="2"]', "none. This is my first.", "ends");
  await load(page, NT);
  await expectText(page, "#ficha-q", "No question or topic is on record yet.");
}];

TESTS[24] = ["Hosted", async () => {
  const { page } = await fresh();
  const body = fs.readFileSync(INDEX, "utf8");
  await page.route("https://claude.ai/r63-test", (r) => r.fulfill({ contentType: "text/html", body }));
  await page.goto("https://claude.ai/r63-test");
  await page.click('#periods .chip[data-p="1"]');
  await expectHidden(page, "#printp");
}];

TESTS[25] = ["Widths and themes", async () => {
  const { page } = await fresh({ viewport: { width: 375, height: 800 } });
  await seed(page, record([
    { n: 2, text: V2, prev: R1D.q, why: WHY, sheet: { dots: [1, 1, 0, 1, 0, 0, 0] } },
    { n: 3, text: V3, prev: V2, why: WHY3 },
    { n: 4, text: V4, prev: V3, why: WHY4, sheet: { dots: [1, 0, 1, 0, 1, 0, 0], circles: [[1, "verb"], [6, "var"], [9, "who"], [12, "where"], [15, "when"]] } },
  ]));
  const busy = async (tag) => {
    if (!(await q.vis(page, "#wb-form"))) await page.click("#q-open");
    check(await q.vis(page, "#wb-form"), `${tag}: the form did not open`);
    if (await q.exists(page, "#cmp-from")) await selectBy(page, "#cmp-from", /^On record/);
    const filled = await page.evaluate(() => { const o = document.getElementById("cmp-out"); return !!o && o.textContent.trim().length > 0; });
    check(filled, `${tag}: compare is not filled (#cmp-out empty or missing)`);
    await page.evaluate(() => {
      for (let pass = 0; pass < 2; pass++) {
        document.querySelectorAll('button[aria-expanded="false"]').forEach((b) => { if (b.getClientRects().length && !b.disabled) b.click(); });
        document.querySelectorAll("details").forEach((d) => { d.open = true; });
      }
    });
    await sleep(50);
  };
  for (const scheme of ["light", "dark"]) {
    await page.emulateMedia({ colorScheme: scheme });
    for (const [w, h] of [[375, 800], [820, 1180], [1180, 820], [1024, 768]]) {
      const tag = `${w}x${h} ${scheme}`;
      await page.setViewportSize({ width: w, height: h });
      await load(page, R1);
      await busy(tag);
      if (w !== 1024) {
        const over = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
        check(over <= 0, `${tag}: ${over}px sideways scroll`);
      }
      if (w >= 1024) {
        const g = await page.evaluate(() => {
          const l = document.getElementById("desk-left"), m = document.getElementById("desk-main");
          if (!l || !m) return null;
          return { pos: getComputedStyle(l).position, right: l.getBoundingClientRect().right, left: m.getBoundingClientRect().left };
        });
        check(g && g.pos === "sticky", `${tag}: #desk-left position should be sticky, got ${J(g && g.pos)}`);
        check(g && g.right < g.left, `${tag}: #desk-left right edge (${g && g.right}) should be left of #desk-main's left edge (${g && g.left})`);
      }
      if (w === 820) {
        await page.evaluate(() => { if (document.activeElement && document.activeElement.blur) document.activeElement.blur(); });
        await expectStyle(page, "#desk-nav", "position", "sticky");
      }
    }
  }
}];

TESTS[26] = ["Keyboard-safe rail", async () => {
  const { page } = await fresh({ viewport: { width: 375, height: 800 } });
  await load(page, R1);
  await page.click("#q-open");
  await mustVisible(page, "#wb-text");
  await page.evaluate(() => { if (document.activeElement && document.activeElement.blur) document.activeElement.blur(); });
  await page.focus("#wb-text");
  await expectStyle(page, "#desk-nav", "position", "static");
  await page.$eval("#wb-text", (e) => e.blur());
  await expectStyle(page, "#desk-nav", "position", "sticky");
}];

TESTS[27] = ["Contrast", async () => {
  const { page } = await fresh({ viewport: { width: 375, height: 800 } });
  await seed(page, record([{ n: 2, text: V2, prev: R1D.q, why: WHY }]));
  for (const scheme of ["light", "dark"]) {
    await page.emulateMedia({ colorScheme: scheme });
    await load(page, R1);
    await mustVisible(page, "#vl");
    const rows = await page.evaluate(contrastProbe);
    rows.forEach((r) => check(r.ok, `${scheme}: ${r.label} ${r.msg}`));
  }
}];

TESTS[28] = ["Focus rings", async () => {
  const { page } = await fresh({ viewport: { width: 820, height: 1180 } });
  await seed(page, record([{ n: 2, text: V2, prev: R1D.q, why: WHY }]));
  const PINE = "rgb(36, 94, 85)", GOLD = "rgb(240, 197, 106)";
  for (const scheme of ["light", "dark"]) {
    await page.emulateMedia({ colorScheme: scheme });
    await load(page, R1);
    await mustVisible(page, "#q-open");
    checkRing(scheme, "#q-open", await ringOf(page, "#q-open"), PINE);
    checkRing(scheme, "#who-done", await ringOf(page, "#who-done"), GOLD);
    await page.click("#q-open");
    await mustVisible(page, "#wb-save");
    checkRing(scheme, "#wb-save", await ringOf(page, "#wb-save"), scheme === "light" ? PINE : GOLD);
  }
}];

TESTS[29] = ["Reduced motion", async () => {
  const { page } = await fresh();
  await page.emulateMedia({ reducedMotion: "reduce" });
  await load(page, R1);
  await page.click("#q-open");
  await mustVisible(page, "#wb-form");
  await page.fill("#wb-text", V2);
  await page.fill("#wb-why", WHY);
  await page.click("#wb-save");
  const seen = [];
  for (const wait of [0, 60, 140, 200]) { // samples at 0, 60, 200 and 400 ms
    if (wait) await sleep(wait);
    seen.push(await page.evaluate(() => document.getAnimations().map((a) => a.animationName || a.transitionProperty || a.constructor.name)));
  }
  must(await q.vis(page, "#vl"), "the save did not happen (#vl is not visible)");
  const any = seen.find((s) => s.length);
  check(!any, `document.getAnimations() should be empty after a save under reduced motion, got ${J(any)}`);
}];

TESTS[30] = ["Source invariants", async () => {
  const src = fs.readFileSync(INDEX, "utf8");
  for (const s of ["fetch(", "XMLHttpRequest", "sendBeacon", "alert(", "confirm(", "prompt(", "Patrick+Hand", "Cormorant", "backdrop-filter"]) {
    const i = src.indexOf(s);
    check(i < 0, `index.html contains ${J(s)} (…${J(src.slice(Math.max(0, i - 30), i + 30))}…)`);
  }
  const code = src.split("\n").filter((l) => !l.startsWith("var DATA = ")).join("\n");
  const FONT = /(?:font(?:-family)?\s*:|fontFamily\s*=|--[\w-]+\s*:|family=)[^;}]{0,200}?\b(Inter|Roboto|Arial)\b/g;
  const fonts = Array.from(code.matchAll(FONT), (m) => m[1]);
  check(fonts.length === 0, `index.html names a banned font: ${J([...new Set(fonts)])}`);
  const pict = src.match(/\p{Extended_Pictographic}/gu);
  check(!pict, `index.html contains Extended_Pictographic characters: ${J(pict && [...new Set(pict)].map((c) => c + " U+" + c.codePointAt(0).toString(16).toUpperCase()))}`);
  check(src.includes(RULE), src.includes("RULE:") ? "the RULE: comment is there but its words differ from 9.1" : "the RULE: comment is missing");
  const bytes = fs.statSync(INDEX).size;
  check(bytes < 360000, `index.html is ${bytes} bytes; it must stay under 360,000`);
}];

TESTS[31] = ["Wording invariant", async () => {
  const page = chain();
  const SELS = ["#ficha-q", "#guide .qblk .q", "#vl-text .vl-q", "#timeline .ver-q", "#cmp-out"];
  const toks = await page.evaluate((sels) => {
    const out = [];
    for (const sel of sels) {
      document.querySelectorAll(sel).forEach((root) => {
        const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
        for (let n = w.nextNode(); n; n = w.nextNode()) {
          if (n.parentElement && n.parentElement.closest(".sr")) continue; // sr spans removed
          n.textContent.trim().split(/\s+/).filter(Boolean).forEach((t) => out.push([sel, t]));
        }
      });
    }
    return out;
  }, SELS);
  check(toks.some(([s]) => s === "#ficha-q"), "#ficha-q has no text to check");
  const bad = toks.filter(([, t]) => !ALLOWED.has(t));
  check(bad.length === 0, `words not from DATA.q or the typed strings: ${J(bad.slice(0, 6).map(([s, t]) => `${s}: ${t}`))}${bad.length > 6 ? ` (+${bad.length - 6} more)` : ""}`);
}];

// ---------- main ----------
(async () => {
  const asked = process.argv.slice(2).map(Number).filter((n) => TESTS[n]);
  let pick = asked.length ? new Set(asked) : new Set(Object.keys(TESTS).map(Number));
  if (asked.some((n) => CHAIN.includes(n) || n === 31)) CHAIN.forEach((n) => pick.add(n));
  pick = [...pick].sort((a, b) => a - b);

  browser = await chromium.launch();
  process.on("unhandledRejection", (e) => { if (T) T.errors.push("unhandled: " + errLine(e)); });
  for (const n of pick) await run(n, TESTS[n][0], TESTS[n][1]);
  if (SHARED) await SHARED.ctx.close().catch(() => {});
  await browser.close();

  const passed = results.filter((r) => r.ok).length;
  const failed = results.length - passed;
  console.log(`${passed} passed, ${failed} failed`);
  process.exit(failed ? 1 : 0);
})().catch(async (e) => {
  console.error("workbench.cjs crashed: " + (e && e.stack ? e.stack : e));
  try { if (browser) await browser.close(); } catch (x) { /* ignore */ }
  process.exit(1);
});
