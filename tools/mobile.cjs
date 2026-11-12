// Focused touch-layout journeys, runnable in a real WebKit engine when installed.
// Device emulation is not a native iPad/Safari or VoiceOver session.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { createHash } = require("node:crypto");
const { launchHarness } = require("./browser-harness.cjs");

const args = process.argv.slice(2);
if (args.length > 1 || (args.length === 1 && !["--browser=webkit", "--browser=chromium"].includes(args[0]))) {
  console.error("Usage: node tools/mobile.cjs [--browser=webkit|--browser=chromium]");
  process.exit(1);
}
const browserName = args[0]?.split("=")[1] || "webkit";
const root = path.resolve(__dirname, "..");
const index = path.join(root, "index.html");
const source = fs.readFileSync(index, "utf8");
const hash = () => createHash("sha256").update(fs.readFileSync(index)).digest("hex");
const data = JSON.parse(source.match(/var DATA = (\[.*?\]);\n/s)[1]);
const [A, B] = data.filter((student) => student.c === "R");
const key = (student = A) => "r63sg_wb_" + student.id;
const sheet = () => ({ dots: [0, 0, 0, 0, 0, 0, 0], circles: [], lenses: [], purpose: "", expect: "", hate: "" });
const version = (n, text = `Synthetic mobile version ${n}?`) => ({
  k: `mobile-${n}`, n, text, date: "2026-11-10", prev: "Synthetic prior version?",
  why: "Synthetic mobile change.", reason: "", rc: 0, saved: n, penned: false, sheet: sheet(),
});
const record = (versions = []) => ({
  schema: 1, id: A.id, course: A.c,
  rec: { q: A.q, asof: "2026-09-29", leads: false, sheet: sheet() },
  versions, draft: null, updated: 1,
});
const report = {
  status: "running", passed: false, started_at: new Date().toISOString(),
  source_sha256: hash(), source_unchanged: true, browser_requested: browserName,
  browser_actual: null, browser_version: null, native_device: false, fonts: "offline fallbacks",
  results: [],
};
const out = path.join(root, "test-results", `mobile-${browserName}.json`);
function writeReport() {
  try { report.source_unchanged = hash() === report.source_sha256; }
  catch { report.source_unchanged = false; report.source_readable = false; }
  if (!report.source_unchanged || report.status === "running") {
    report.status = "failed";
    report.passed = false;
    process.exitCode = 1;
  }
  report.finished_at = new Date().toISOString();
  fs.mkdirSync(path.dirname(out), { recursive: true });
  fs.writeFileSync(out, JSON.stringify(report, null, 2) + "\n");
}
const frames = (page) => page.evaluate(() => new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve))));
const readRecord = (page) => page.evaluate((k) => JSON.parse(localStorage.getItem(k)), key());

(async () => {
  let harness;
  let context;
  let errors = [];
  async function fresh(options = {}, initial = record()) {
    context = await harness.browser.newContext({
      viewport: { width: 820, height: 1180 }, deviceScaleFactor: 2,
      isMobile: true, hasTouch: true, reducedMotion: "reduce", colorScheme: "light", ...options,
    });
    context.setDefaultTimeout(15000);
    await context.route(/fonts\.(googleapis|gstatic)\.com/, (route) => route.abort());
    const page = await context.newPage();
    page.on("pageerror", () => errors.push(true));
    await page.goto(harness.url);
    if (initial !== null) {
      await page.evaluate(([k, value]) => localStorage.setItem(k, JSON.stringify(value)), [key(), initial]);
      await page.goto(harness.url + "#" + A.id);
      await page.waitForFunction(() => document.getElementById("desk").dataset.on === "true");
    }
    await frames(page);
    return page;
  }
  async function check(name, run) {
    const start = Date.now();
    errors = [];
    let status = "passed";
    try {
      await run();
      assert.equal(errors.length, 0, "unexpected page error");
    } catch (error) {
      status = "failed";
      // Keep private browser content out of the persisted status report.
      console.error(`FAIL ${name}: ${String(error.message).split("\n")[0]}`);
    } finally {
      if (context) await context.close();
      context = null;
    }
    report.results.push({ name, status, elapsed_ms: Date.now() - start });
    if (status === "passed") console.log(`ok ${name}`);
  }
  async function noOverflow(page) {
    const size = await page.evaluate(() => ({ width: innerWidth, content: document.documentElement.scrollWidth }));
    assert.ok(size.content <= size.width, "touch layout has horizontal overflow");
  }
  async function navigate(page) {
    for (const [nav, heading] of [["nav-versions", "stv-h"], ["nav-checks", "ck-h"], ["nav-search", "step3title"]]) {
      await page.tap("#" + nav);
      await page.waitForFunction((id) => document.querySelector('#desk-nav a[aria-current="location"]')?.id === id, nav);
      const position = await page.evaluate((id) => {
        const element = document.getElementById(id), rect = element.getBoundingClientRect();
        const rail = document.getElementById("desk-nav").getBoundingClientRect();
        return { focused: document.activeElement === element, top: rect.top, bottom: rail.bottom };
      }, heading);
      assert.equal(position.focused, true, "station link must focus its destination");
      assert.ok(position.top >= position.bottom - 1, "station heading is hidden behind the rail");
    }
    await noOverflow(page);
  }
  async function save(page, text, n) {
    await page.tap("#q-open");
    await page.fill("#wb-text", text);
    await page.fill("#wb-why", "Synthetic mobile test change.");
    await page.fill("#wb-n", String(n));
    await page.fill("#wb-date", "2026-11-10");
    await page.tap("#wb-save");
    await page.waitForFunction((number) => document.querySelector("#ficha-num .num-v").textContent === String(number), n);
  }

  try {
    try { harness = await launchHarness(index, { browserName }); }
    catch (error) {
      report.status = "blocked";
      report.reason = String(error.message).split("\n")[0];
      console.error(`BLOCKED ${browserName}: ${report.reason}`);
      process.exitCode = 1;
      return;
    }
    report.browser_actual = harness.browser.browserType().name();
    if (report.browser_actual !== browserName) {
      report.status = "failed";
      report.reason = "The launched engine differs from the requested browser.";
      process.exitCode = 1;
      return;
    }
    report.browser_version = harness.browser.version();

    await check("portrait picker, filter status, and station navigation", async () => {
      const page = await fresh({}, null);
      await page.tap(`#periods [data-p="${A.p}"]`);
      await page.fill("#find", "synthetic-unmatched-mobile-999");
      assert.match(await page.locator("#name-status").textContent(), /^No name matches\./, "filter needs a result status");
      await page.fill("#find", "");
      await page.tap(`#names [data-id="${A.id}"]`);
      await navigate(page);
    });

    await check("landscape dark-theme station navigation and reflow", async () => {
      const page = await fresh({ viewport: { width: 1180, height: 820 }, colorScheme: "dark" });
      await navigate(page);
      await page.evaluate(() => {
        document.querySelectorAll("details").forEach((element) => { element.open = true; });
        document.querySelectorAll('.ck-more button[aria-expanded="false"]').forEach((button) => button.click());
      });
      await noOverflow(page);
    });

    await check("save, reload, comparison, check dots, and word annotation", async () => {
      const page = await fresh();
      const first = "How do synthetic mobile examples vary across groups?";
      const second = "How do synthetic mobile examples vary across groups during a test?";
      await save(page, first, 2);
      await page.reload();
      assert.equal(await page.locator("#ficha-q").textContent(), first, "saved text did not survive reload");
      await save(page, second, 3);
      await page.selectOption("#cmp-from", "2");
      await page.selectOption("#cmp-to", "3");
      assert.ok(await page.locator("#cmp-out ins").count() > 0, "comparison does not mark additions");
      await page.locator("#checks .dot").first().tap();
      assert.equal(await page.locator("#checks .dot").first().getAttribute("aria-pressed"), "true", "check did not fill");
      await page.locator("#words .w").first().tap();
      assert.ok(await page.locator("#words .w").first().getAttribute("data-l"), "word did not acquire its pen label");
      await page.reload();
      const saved = (await readRecord(page)).versions.find((value) => value.n === 3);
      assert.equal(saved.sheet.dots[0], 1, "check did not persist");
      assert.equal(saved.sheet.circles.length, 1, "word annotation did not persist");
    });

    await check("short phone form focus, static typing rail, and keyword focus", async () => {
      const page = await fresh({ viewport: { width: 375, height: 450 } });
      await page.tap("#q-open");
      await frames(page);
      const state = await page.evaluate(() => {
        const field = document.getElementById("wb-text"), rect = field.getBoundingClientRect();
        return { focused: document.activeElement === field, top: rect.top, bottom: rect.bottom,
          height: innerHeight, position: getComputedStyle(document.getElementById("desk-nav")).position };
      });
      assert.equal(state.focused, true, "form must focus its question field");
      assert.ok(state.top >= 0 && state.bottom <= state.height, "focused field is outside the short viewport");
      assert.equal(state.position, "static", "typing rail must be static");
      await page.evaluate(() => document.activeElement.blur());
      await page.waitForFunction(() => getComputedStyle(document.getElementById("desk-nav")).position === "sticky");
      await page.focus("#kw button");
      await page.keyboard.press("Space");
      assert.equal(await page.evaluate(() => document.activeElement.matches("#kw button")), true, "keyword focus was lost");
      await noOverflow(page);
    });

    await check("denied clipboard exposes usable text fallbacks", async () => {
      const page = await fresh({ viewport: { width: 375, height: 812 } }, record([version(2)]));
      await page.evaluate(() => Object.defineProperty(navigator, "clipboard", { configurable: true, value: {
        writeText: () => Promise.reject(new Error("Synthetic clipboard denial")),
      } }));
      const words = page.locator("#guide .search button.copy").first();
      await words.tap();
      await page.waitForFunction(() => document.querySelector("#guide .search button.copy").textContent.startsWith("Selected:"));
      assert.ok(await page.evaluate(() => getSelection().toString().length > 0), "search text was not selected");
      await page.tap("#vl-copy");
      await page.waitForFunction(() => document.getElementById("vl-copy").textContent.startsWith("Copy did not work"));
      assert.ok(await page.evaluate(() => getSelection().toString().includes("Synthetic mobile version")), "version fallback is unavailable");
      await page.tap("#ipad-copyall");
      await page.waitForFunction(() => !document.getElementById("ipad-backup").hidden);
      assert.ok((await page.inputValue("#ipad-backup")).includes("Synthetic mobile version"), "all-version fallback is unavailable");
    });

    await check("student switch invalidates a delayed clipboard fallback", async () => {
      const marker = "PRIVATE_SYNTHETIC_MOBILE_MARKER";
      const page = await fresh({}, record([version(2, marker + "?")]));
      await page.evaluate(() => Object.defineProperty(navigator, "clipboard", { configurable: true, value: {
        writeText: () => new Promise((resolve, reject) => { window.__mobileRejectCopy = reject; }),
      } }));
      await page.tap("#ipad-copyall");
      await page.tap("#who-not");
      await page.tap(`#periods [data-p="${B.p}"]`);
      await page.tap(`#names [data-id="${B.id}"]`);
      await page.evaluate(() => window.__mobileRejectCopy(new Error("Synthetic late denial")));
      await frames(page);
      assert.equal(await page.locator("#ipad-backup").isVisible(), false, "previous export appeared on another desk");
      assert.equal((await page.inputValue("#ipad-backup")).includes(marker), false, "previous export text leaked across desks");
    });

    await check("damaged data can be recovered, exported, and removed", async () => {
      const damaged = version(3, "Synthetic damaged mobile version?"); damaged.date = "not-a-date";
      const original = record([version(2), damaged]), raw = JSON.stringify(original);
      const page = await fresh({}, original);
      await page.tap("#ipad-recover");
      assert.equal(await page.inputValue("#ipad-backup"), raw, "recovery must expose the original raw data");
      await page.reload();
      await page.tap("#ipad-recover");
      assert.ok((await page.inputValue("#ipad-backup")).includes("Synthetic damaged mobile version"), "recovery was lost after reload");
      await page.tap("#ipad-remove");
      await page.tap("#ipad-remove-yes");
      const remains = await page.evaluate(([k, prefix]) => Object.keys(localStorage).some((value) => value === k || value.startsWith(prefix)), [key(), "r63sg_bad_" + A.id + "_"]);
      assert.equal(remains, false, "successful removal must clear active and recovery data");
      assert.equal(await page.inputValue("#ipad-backup"), "", "removed data remains in the export field");
    });

    await check("failed recovery backup locks editing and preserves the original", async () => {
      const damaged = version(3, "Synthetic unsaved recovery version?"); damaged.date = "invalid";
      const raw = JSON.stringify(record([version(2), damaged]));
      const page = await fresh({}, null);
      await page.evaluate(([k, value, prefix]) => {
        localStorage.setItem(k, value);
        const write = Storage.prototype.setItem;
        Storage.prototype.setItem = function (candidate, content) {
          if (candidate.startsWith(prefix)) throw new DOMException("Synthetic backup quota", "QuotaExceededError");
          return write.call(this, candidate, content);
        };
      }, [key(), raw, "r63sg_bad_" + A.id + "_"]);
      await page.evaluate((id) => { location.hash = id; }, A.id);
      await page.waitForFunction(() => document.getElementById("desk").dataset.on === "true");
      assert.equal(await page.locator("#q-open").isDisabled(), true, "unsafe editing was not locked");
      assert.equal(await page.evaluate((k) => localStorage.getItem(k), key()), raw, "original data was changed without a backup");
      await page.tap("#ipad-recover");
      assert.equal(await page.inputValue("#ipad-backup"), raw, "session recovery must remain exportable");
    });

    report.source_unchanged = hash() === report.source_sha256;
    report.passed = report.source_unchanged && report.results.length === 8 && report.results.every((result) => result.status === "passed");
    report.status = report.passed ? "passed" : "failed";
    if (!report.source_unchanged) console.error("FAIL source changed during mobile verification");
    console.log(`${report.results.filter((result) => result.status === "passed").length} of ${report.results.length} ${browserName} mobile cases passed`);
    process.exitCode = report.passed ? 0 : 1;
  } finally {
    let cleanupFailed = false;
    try { if (context) await context.close(); } catch { cleanupFailed = true; }
    try { if (harness) await harness.close(); } catch { cleanupFailed = true; }
    if (cleanupFailed) {
      report.status = "failed";
      report.passed = false;
      report.cleanup = "failed";
      process.exitCode = 1;
    }
    writeReport();
  }
})().catch((error) => {
  console.error("Mobile verifier failed: " + String(error.message).split("\n")[0]);
  report.status = "failed";
  report.passed = false;
  report.reason = "Unexpected verifier failure; see the local command output.";
  process.exitCode = 1;
  try { writeReport(); } catch { console.error("Could not persist the failed mobile verification report."); }
});
