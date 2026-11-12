// Consequential failures reproduced during the finish pass. Uses disposable browser storage.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { launchHarness } = require("./browser-harness.cjs");

const INDEX = path.resolve(__dirname, "..", "index.html");
const SRC = fs.readFileSync(INDEX, "utf8");
const DATA = JSON.parse(SRC.match(/var DATA = (\[.*?\]);\n/s)[1]);
const [A, B] = DATA.filter((s) => s.c === "R");
const key = (student = A) => "r63sg_wb_" + student.id;
const badPrefix = "r63sg_bad_" + A.id + "_";
const sheet = () => ({ dots: [0, 0, 0, 0, 0, 0, 0], circles: [], lenses: [], purpose: "", expect: "", hate: "" });
const version = (n, text = `Synthetic regression version ${n}?`) => ({
  k: `regression-${n}`, n, text, date: "2026-11-10", prev: "Synthetic previous version?",
  why: "Synthetic test change.", reason: "", rc: 0, saved: n, penned: false, sheet: sheet(),
});
const record = (versions = [version(2)]) => ({
  schema: 1, id: A.id, course: A.c, rec: { q: A.q, asof: "2026-09-29", leads: false, sheet: sheet() },
  versions, draft: null, updated: 1,
});
const waitFrames = (page) => page.evaluate(() => new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve))));
const stored = (page) => page.evaluate((k) => JSON.parse(localStorage.getItem(k)), key());

(async () => {
  const harness = await launchHarness(INDEX);
  const results = [];
  let context;
  let errors;
  async function fresh(options = {}, data = record()) {
    context = await harness.browser.newContext({ viewport: { width: 1180, height: 900 }, reducedMotion: "reduce", ...options });
    context.setDefaultTimeout(15000);
    await context.route(/fonts\.(googleapis|gstatic)\.com/, (route) => route.abort());
    const page = await context.newPage();
    page.on("pageerror", () => errors.push("unexpected page error"));
    await page.goto(harness.url);
    if (data !== null) {
      await page.evaluate(([k, value]) => localStorage.setItem(k, JSON.stringify(value)), [key(), data]);
      await page.goto(harness.url + "#" + A.id);
    }
    await waitFrames(page);
    return page;
  }
  async function test(name, fn) {
    errors = [];
    try {
      await fn();
      assert.equal(errors.length, 0, "page errors occurred");
      results.push(true);
      console.log(`ok ${results.length} ${name}`);
    } catch (error) {
      results.push(false);
      // Assertions use synthetic text or booleans; no student record is logged.
      console.error(`FAIL ${results.length} ${name}: ${error.message.split("\n")[0]}`);
    } finally {
      if (context) await context.close();
      context = null;
    }
  }
  async function otherTab() {
    const page = await context.newPage();
    await page.goto(harness.url + "#" + A.id);
    return page;
  }
  async function recoveryText(page) {
    await page.waitForFunction(() => !document.getElementById("ipad-recover").hidden);
    await page.click("#ipad-recover");
    return page.inputValue("#ipad-backup");
  }

  try {
    await test("station navigation follows focused headings at all critical widths", async () => {
      const page = await fresh({}, record([]));
      for (const [width, height] of [[1440, 1000], [1180, 820], [820, 1000], [375, 812]]) {
        await page.setViewportSize({ width, height });
        for (const [nav, heading] of [["nav-versions", "stv-h"], ["nav-checks", "ck-h"], ["nav-search", "step3title"]]) {
          await page.focus("#" + nav);
          await page.keyboard.press("Enter");
          await page.waitForFunction((id) => document.querySelector('#desk-nav a[aria-current="location"]')?.id === id, nav);
          assert.equal(await page.evaluate(() => document.activeElement.id), heading, "navigation must focus its heading");
        }
      }
    });

    await test("keyboard keyword toggles retain focus and pressed state", async () => {
      const page = await fresh();
      await page.focus("#kw button");
      await page.keyboard.press("Space");
      assert.equal(await page.evaluate(() => document.activeElement.matches("#kw button")), true, "keyword focus was lost");
      assert.equal(await page.evaluate(() => document.activeElement.getAttribute("aria-pressed")), "false", "keyword did not toggle off");
      await page.keyboard.press("Space");
      assert.equal(await page.evaluate(() => document.activeElement.getAttribute("aria-pressed")), "true", "keyword did not toggle back on");
      await page.fill("#myq", "Synthetic keywords for a regression");
      assert.equal(await page.evaluate(() => document.activeElement.id), "myq", "typing must not steal focus into a keyword");
    });

    await test("roster filter announces counts and no results without names", async () => {
      const page = await fresh({}, null);
      await page.click(`#periods [data-p="${A.p}"]`);
      const status = page.locator("#name-status");
      assert.equal(await status.getAttribute("role"), "status", "filter needs a polite status");
      assert.match(await status.textContent(), /^\d+ names found\.$/, "filter count is missing");
      await page.fill("#find", "synthetic-no-match-999");
      assert.match(await status.textContent(), /^No name matches\./, "no-result announcement is missing");
      assert.equal(await page.evaluate(() => document.activeElement.id), "find", "filtering must preserve input focus");
      await page.fill("#find", "");
      assert.match(await status.textContent(), /^\d+ names found\.$/, "clearing filter must restore result count");
    });

    await test("opening a form keeps its focused textarea visible on a short phone", async () => {
      const page = await fresh({ viewport: { width: 320, height: 450 }, isMobile: true, hasTouch: true });
      await page.click("#q-open");
      await waitFrames(page);
      const state = await page.evaluate(() => {
        const field = document.getElementById("wb-text"), rect = field.getBoundingClientRect();
        return { focused: document.activeElement === field, top: rect.top, bottom: rect.bottom, height: innerHeight };
      });
      assert.equal(state.focused, true, "form must focus the question field");
      assert.ok(state.top >= 0 && state.bottom <= state.height, "focused question field is outside the viewport");
    });

    await test("delayed clipboard callbacks cannot reveal another student's export", async () => {
      const marker = "PRIVATE_SYNTHETIC_REGRESSION_A";
      const page = await fresh({}, record([version(2, marker + "?")]));
      await page.evaluate(() => Object.defineProperty(navigator, "clipboard", { configurable: true, value: {
        writeText: () => new Promise((resolve, reject) => { window.__rejectRegressionCopy = reject; }),
      } }));
      await page.click("#ipad-copyall");
      await page.click("#who-not");
      await page.click(`#periods [data-p="${B.p}"]`);
      await page.click(`#names [data-id="${B.id}"]`);
      await page.evaluate(() => window.__rejectRegressionCopy(new Error("Synthetic delayed rejection")));
      await waitFrames(page);
      assert.equal(await page.locator("#ipad-backup").isVisible(), false, "previous export was revealed on the next desk");
      assert.equal((await page.inputValue("#ipad-backup")).includes(marker), false, "previous export survived the desk switch");
      assert.equal(await page.locator("#ipad-copyall").textContent(), "Copy all my versions", "stale clipboard callback changed the next desk");
    });

    await test("blocked deletion retains visible versions and reports failure", async () => {
      const page = await fresh();
      await page.evaluate((k) => {
        const remove = Storage.prototype.removeItem;
        Storage.prototype.removeItem = function (candidate) {
          if (candidate === k) throw new DOMException("Synthetic blocked removal", "SecurityError");
          return remove.call(this, candidate);
        };
      }, key());
      await page.click("#ipad-remove");
      await page.click("#ipad-remove-yes");
      assert.equal((await stored(page)).versions.length, 1, "blocked deletion must preserve the record");
      assert.match(await page.locator("#ipad-status").textContent(), /1 version saved/, "blocked deletion falsely reset visible status");
      assert.match(await page.locator("#wb-live").textContent(), /Removal did not finish/, "blocked deletion must announce failure");
    });

    await test("successful removal invalidates a pending clipboard export", async () => {
      const page = await fresh({}, record([version(2, "PRIVATE_SYNTHETIC_REMOVED_VERSION?")]));
      await page.evaluate(() => Object.defineProperty(navigator, "clipboard", { configurable: true, value: {
        writeText: () => new Promise((resolve, reject) => { window.__rejectRegressionCopy = reject; }),
      } }));
      await page.click("#ipad-copyall");
      await page.click("#ipad-remove");
      await page.click("#ipad-remove-yes");
      await page.evaluate(() => window.__rejectRegressionCopy(new Error("Synthetic rejection after removal")));
      await waitFrames(page);
      assert.equal(await page.evaluate((k) => localStorage.getItem(k), key()), null, "successful removal left the record behind");
      assert.equal(await page.locator("#ipad-backup").isVisible(), false, "late clipboard fallback revealed removed data");
      assert.equal(await page.inputValue("#ipad-backup"), "", "late clipboard fallback restored removed data");
    });

    await test("cross-tab pending answers stay attached to their original version", async () => {
      const page = await fresh();
      const other = await otherTab();
      await page.fill("#c-expect", "SYNTHETIC_PENDING_V2");
      await other.evaluate(([k, value]) => localStorage.setItem(k, JSON.stringify(value)), [key(), record([version(2), version(3)])]);
      await page.waitForFunction((k) => JSON.parse(localStorage.getItem(k)).versions.find((v) => v.n === 2)?.sheet.expect === "SYNTHETIC_PENDING_V2", key());
      const data = await stored(page);
      assert.equal(data.versions.find((v) => v.n === 3).sheet.expect, "", "pending answer was assigned to the new version");
      assert.equal(await page.inputValue("#c-expect"), "", "new version displays the old version's answer");
    });

    await test("cross-tab edits preserve the remote version and recover local typed changes", async () => {
      const page = await fresh();
      const other = await otherTab();
      await page.click("#vl-edit");
      await page.fill("#wb-text", "SYNTHETIC_LOCAL_EDITED_VERSION?");
      await page.fill("#wb-why", "SYNTHETIC_LOCAL_EDIT_REASON");
      const remoteVersion = version(2, "SYNTHETIC_REMOTE_EDITED_VERSION?");
      remoteVersion.why = "Synthetic remote edit reason.";
      await other.evaluate(([k, value]) => localStorage.setItem(k, JSON.stringify(value)), [key(), record([remoteVersion])]);
      await page.waitForFunction(() => document.getElementById("wb-form").hidden);
      assert.equal((await stored(page)).versions[0].text, remoteVersion.text, "open local edit overwrote the remote version");
      assert.match(await page.locator("#wb-live").textContent(), /typed changes are in recovery data/, "interrupted edit needs a recovery announcement");
      for (const reload of [false, true]) {
        if (reload) await page.reload();
        const text = await recoveryText(page);
        assert.ok(text.includes("SYNTHETIC_LOCAL_EDITED_VERSION?"), "local edited text was lost");
        assert.ok(text.includes("SYNTHETIC_LOCAL_EDIT_REASON"), "local edit reason was lost");
        assert.equal((await stored(page)).versions[0].text, remoteVersion.text, "recovery interaction changed the remote version");
      }
    });

    await test("partly corrupt versions remain recoverable after an edit and reload", async () => {
      const invalid = version(3, "SYNTHETIC_RECOVERABLE_VERSION?");
      invalid.date = "not-a-date";
      const original = record([version(2), invalid]);
      const raw = JSON.stringify(original);
      const page = await fresh({}, original);
      assert.match(await page.locator("#wb-notice").textContent(), /Some versions could not be read/, "partial corruption must be disclosed");
      await page.locator("#checks .dot").first().click();
      await page.reload();
      assert.equal((await stored(page)).versions.length, 1, "invalid version should not enter active editable versions");
      assert.equal(await recoveryText(page), raw, "the original raw record must remain available after reload");
      assert.equal(await page.evaluate(([prefix, value]) => Object.keys(localStorage).some((k) => k.startsWith(prefix) && localStorage.getItem(k) === value), [badPrefix, raw]), true, "original data was not quarantined");
    });

    await test("failed recovery backup prevents sanitized overwrite", async () => {
      const invalid = version(3, "SYNTHETIC_NO_BACKUP_VERSION?"); invalid.date = "invalid";
      const raw = JSON.stringify(record([version(2), invalid]));
      const page = await fresh({}, null);
      await page.evaluate(([k, value, prefix]) => {
        localStorage.setItem(k, value);
        const write = Storage.prototype.setItem;
        Storage.prototype.setItem = function (candidate, content) {
          if (candidate.startsWith(prefix)) throw new DOMException("Synthetic full backup store", "QuotaExceededError");
          return write.call(this, candidate, content);
        };
      }, [key(), raw, badPrefix]);
      // A full document navigation resets prototype injection; dispatching the hash change loads the selected desk in place.
      await page.evaluate((id) => { location.hash = id; }, A.id);
      await page.waitForFunction(() => document.getElementById("desk").dataset.on === "true");
      assert.equal(await page.locator("#q-open").isDisabled(), true, "editing must stop when the original cannot be backed up");
      assert.match(await page.locator("#ficha-hint").textContent(), /Editing is off/, "backup failure needs the recovery-specific hint");
      assert.doesNotMatch(await page.locator("#ficha-hint").textContent(), /newer Search Guide/i, "backup failure must not claim a schema upgrade");
      await page.locator("#checks .dot").first().click({ force: true });
      assert.equal(await page.evaluate((k) => localStorage.getItem(k), key()), raw, "failed backup allowed original data to be overwritten");
      assert.equal(await recoveryText(page), raw, "memory recovery must still expose the original data");
    });

    await test("a damaged non-array versions field is preserved for recovery", async () => {
      const original = record();
      original.versions = { recovered: "SYNTHETIC_NON_ARRAY_VERSION_DATA" };
      const raw = JSON.stringify(original);
      const page = await fresh({}, original);
      assert.match(await page.locator("#wb-notice").textContent(), /Some versions could not be read/, "invalid collection must not be silently discarded");
      await page.locator("#checks .dot").first().click();
      await page.reload();
      assert.equal(await recoveryText(page), raw, "invalid collection must remain recoverable after an unrelated write");
    });

    await test("revision guard preserves an unseen external record", async () => {
      const page = await fresh();
      const remote = JSON.stringify(record([version(2), version(3)]));
      // Same-window injection produces no storage event, modeling an update not yet observed by the UI.
      await page.evaluate(([k, value]) => localStorage.setItem(k, value), [key(), remote]);
      await page.locator("#checks .dot").first().click();
      assert.equal(await page.evaluate((k) => localStorage.getItem(k), key()), remote, "stale UI overwrote an external record");
      assert.equal(await page.locator("#store-banner").isVisible(), true, "refused write needs visible feedback");
    });

    await test("conflicting or orphaned pending answers go to recovery without polluting versions", async () => {
      const page = await fresh();
      const other = await otherTab();
      await page.fill("#c-expect", "SYNTHETIC_CONFLICTING_ANSWER");
      const remoteVersion = version(2); remoteVersion.sheet.expect = "SYNTHETIC_REMOTE_ANSWER";
      await other.evaluate(([k, value]) => localStorage.setItem(k, JSON.stringify(value)), [key(), record([remoteVersion, version(3)])]);
      assert.ok((await recoveryText(page)).includes("SYNTHETIC_CONFLICTING_ANSWER"), "conflicting answer was not retained for recovery");
      const remote = await stored(page);
      assert.equal(remote.versions.find((v) => v.n === 2).sheet.expect, "SYNTHETIC_REMOTE_ANSWER", "remote answer was overwritten");
      assert.equal(remote.versions.find((v) => v.n === 3).sheet.expect, "", "conflicting answer polluted another version");
      await page.fill("#c-hate", "SYNTHETIC_ORPHANED_ANSWER");
      await other.evaluate(([k, value]) => localStorage.setItem(k, JSON.stringify(value)), [key(), record([version(2)])]);
      await page.waitForFunction(() => document.querySelector("#ficha-num .num-v").textContent === "2");
      assert.ok((await recoveryText(page)).includes("SYNTHETIC_ORPHANED_ANSWER"), "orphaned answer was not retained for recovery");
      assert.equal((await stored(page)).versions[0].sheet.hate, "", "orphaned answer polluted the remaining version");
    });

    await test("simultaneous answer conflicts both survive recovery and reload", async () => {
      const page = await fresh();
      const other = await otherTab();
      await page.fill("#c-expect", "SYNTHETIC_LOCAL_EXPECT_CONFLICT");
      await page.fill("#c-hate", "SYNTHETIC_LOCAL_HATE_CONFLICT");
      const remoteVersion = version(2);
      remoteVersion.sheet.expect = "SYNTHETIC_REMOTE_EXPECT";
      remoteVersion.sheet.hate = "SYNTHETIC_REMOTE_HATE";
      await other.evaluate(([k, value]) => localStorage.setItem(k, JSON.stringify(value)), [key(), record([remoteVersion])]);
      await page.waitForFunction(() => document.getElementById("c-expect").value === "SYNTHETIC_REMOTE_EXPECT");
      for (const reload of [false, true]) {
        if (reload) await page.reload();
        const text = await recoveryText(page);
        assert.ok(text.includes("SYNTHETIC_LOCAL_EXPECT_CONFLICT"), "first conflicting answer was lost");
        assert.ok(text.includes("SYNTHETIC_LOCAL_HATE_CONFLICT"), "second conflicting answer was lost");
      }
      const data = await stored(page);
      assert.equal(data.versions[0].sheet.expect, "SYNTHETIC_REMOTE_EXPECT", "remote expected answer changed");
      assert.equal(data.versions[0].sheet.hate, "SYNTHETIC_REMOTE_HATE", "remote opposing answer changed");
    });

    await test("stored markup is rendered as text rather than executable HTML", async () => {
      const payload = '<img src=x onerror="window.__regressionXSS=1"> Synthetic text?';
      const v = version(2, payload); v.prev = payload; v.why = payload; v.sheet.expect = payload;
      const page = await fresh({}, record([v]));
      const result = await page.evaluate(() => ({
        executed: window.__regressionXSS === 1,
        markup: document.querySelectorAll("#ficha img,#timeline img,#vl img,#compare img").length,
        preserved: document.getElementById("ficha-q").textContent.includes("<img"),
      }));
      assert.equal(result.executed, false, "stored markup executed");
      assert.equal(result.markup, 0, "stored markup created HTML nodes");
      assert.equal(result.preserved, true, "stored text should remain visible verbatim");
    });

    await test("newer schemas remain read-only and byte-for-byte unchanged", async () => {
      const future = record(); future.schema = 2; future.unknownFuture = { keep: "SYNTHETIC_FUTURE_FIELD" };
      const raw = JSON.stringify(future);
      const page = await fresh({}, future);
      assert.equal(await page.locator("#q-open").isDisabled(), true, "newer schema must disable editing");
      assert.equal(await page.locator("#ipad-remove").isVisible(), false, "newer schema must not be removed by this version");
      await page.locator("#checks .dot").first().click({ force: true });
      assert.equal(await page.evaluate((k) => localStorage.getItem(k), key()), raw, "newer schema changed during a read-only interaction");
    });
  } finally {
    await harness.close();
  }
  const failed = results.filter((ok) => !ok).length;
  console.log(`${results.length - failed} regression cases passed, ${failed} failed`);
  if (failed) process.exitCode = 1;
})().catch((error) => {
  console.error("Regression harness failed: " + error.message.split("\n")[0]);
  process.exitCode = 1;
});
