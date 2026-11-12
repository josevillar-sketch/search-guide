// Real Chromium checks for absent-face false positives and actual fallback rendering.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { launchHarness } = require("./browser-harness.cjs");
const { fontSamples, forceFallbackFonts, inspectRenderedFonts } = require("./rendered-fonts.cjs");

(async () => {
  const root = path.resolve(__dirname, "..");
  const harness = await launchHarness(path.join(root, "index.html"));
  const evidence = { scope: "Chromium font-gate checks only; no product or saved student state changed", checks: [] };
  const check = async (name, test) => {
    await test();
    evidence.checks.push(name);
    console.log("ok " + name);
  };
  try {
    const context = await harness.browser.newContext();
    await context.route(/fonts\.(googleapis|gstatic)\.com/, (route) => route.abort());
    const page = await context.newPage();
    await page.setContent('<p id="sample" style="font:20px serif">Font probe only</p><p id="empty"></p>');
    const absent = [{ selector: "#sample", expected: "R63 Definitely Absent Font" }];
    await check("FontFaceSet check alone accepts an absent face", async () => {
      assert.equal(await page.evaluate(() => document.fonts.check('20px "R63 Definitely Absent Font"')), true);
    });
    let rejected;
    await check("glyph gate rejects the absent expected face", async () => {
      rejected = await inspectRenderedFonts(page, absent);
      assert(rejected.failures.some((failure) => failure.startsWith("required font not rendered:")));
    });
    await check("glyph gate accepts the independently reported platform family", async () => {
      const expected = rejected.evidence[0].used[0].familyName;
      assert.deepEqual((await inspectRenderedFonts(page, [{ selector: "#sample", expected }])).failures, []);
    });
    await check("missing proof elements fail", async () => {
      assert((await inspectRenderedFonts(page, [{ selector: "#absent", expected: "missing" }])).failures.length);
    });
    await check("zero rendered glyphs fail", async () => {
      assert((await inspectRenderedFonts(page, [{ selector: "#empty", expected: "empty" }])).failures.length);
    });
    await page.goto(harness.url);
    await page.evaluate(() => document.fonts.ready);
    const samples = await fontSamples(page);
    evidence.blockedWebFontContext = await inspectRenderedFonts(page, samples);
    const fallbackSamples = await forceFallbackFonts(page);
    evidence.forcedFallbackContext = await inspectRenderedFonts(page, fallbackSamples, { fallback: true });
    await check("fallback context removes primary font use and retains glyph evidence", async () => {
      assert.deepEqual(evidence.forcedFallbackContext.failures, []);
      assert.equal(evidence.forcedFallbackContext.evidence.length, 3);
    });
    await check("normal gate refuses the forced fallback fonts", async () => {
      assert.equal((await inspectRenderedFonts(page, fallbackSamples)).failures.length, 3);
    });
    await context.close();
    const output = path.join(root, "test-results", "font-integrity");
    fs.mkdirSync(output, { recursive: true });
    fs.writeFileSync(path.join(output, "regression.json"), JSON.stringify(evidence, null, 2));
    console.log(evidence.checks.length + " font gate checks passed");
  } finally { await harness.close(); }
})().catch((error) => { console.error("Font gate check failed: " + error.message); process.exitCode = 1; });
