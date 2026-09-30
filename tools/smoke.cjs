// Headless smoke test for index.html. Run: NODE_PATH="$(npm root -g)" node tools/smoke.cjs
// Opens every period and every student slip, then exercises the log copy, the welcome-back bar,
// the question builder, period printing, and phone width. Exits 1 on the first failure.
const { chromium } = require("playwright");
const path = require("path");
const fs = require("fs");

const FILE = "file://" + path.resolve(__dirname, "..", "index.html");
const OUT = process.env.SMOKE_OUT || path.resolve(__dirname, "..", "smoke-out");
const html = fs.readFileSync(path.resolve(__dirname, "..", "index.html"), "utf8");
const DATA = JSON.parse(html.match(/var DATA = (\[.*?\]);\n/s)[1]);
const fails = [];
const check = (ok, msg) => { if (!ok) fails.push(msg); };

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ permissions: ["clipboard-read", "clipboard-write"] });
  const page = await ctx.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push("pageerror: " + e.message));
  page.on("console", (m) => { if (m.type() === "error" && !/fonts\.g|net::ERR|Failed to load resource/.test(m.text())) errors.push("console: " + m.text()); });
  // Fonts are decoration; block them so the test runs offline.
  await ctx.route(/fonts\.(googleapis|gstatic)\.com/, (r) => r.abort());

  await page.goto(FILE);
  check(await page.locator("#guide .slip .search").count() === 3, "example slip does not show 3 searches");

  // Every period, every student.
  let seen = 0;
  for (const p of [1, 2, 3, 4, 5, 6, 7, 8]) {
    await page.click(`#periods .chip[data-p="${p}"]`);
    const roster = DATA.filter((d) => d.p === p);
    const names = page.locator("#names .name");
    check(await names.count() === roster.length, `period ${p}: ${await names.count()} names shown, ${roster.length} in data`);
    for (const st of roster) {
      await page.click(`#names .name[data-id="${st.id}"]`);
      const who = await page.textContent("#guide .who");
      check(who === st.n, `${st.id}: slip shows "${who}"`);
      const hrefs = await page.$$eval("#guide .search a.go", (as) => as.map((a) => a.href));
      check(hrefs.length === 3 && hrefs.every((h) => h.startsWith("https://")), `${st.id}: search links ${JSON.stringify(hrefs)}`);
      seen++;
    }
  }
  check(seen === DATA.length, `opened ${seen} of ${DATA.length} slips`);

  // Log lines follow the last search tapped.
  const st = DATA.find((d) => d.p === 1);
  await page.goto(FILE + "#" + st.id);
  await page.reload();
  await page.locator("#guide .search").nth(1).locator("button.copy").click();
  await page.click("#guide button:has-text('Copy log lines')");
  const clip = await page.evaluate(() => navigator.clipboard.readText());
  check(clip.includes(st.s[1].q) && /^1\. Date: /.test(clip) && clip.split("\n").length === 6, "log lines: " + clip);
  check((await page.inputValue("#myq")) === st.q, "builder not filled with the student's question");

  // Welcome back after reload without a hash.
  await page.goto(FILE);
  await page.reload();
  check(await page.isVisible("#back"), "welcome-back bar hidden after a student was picked");
  await page.click("#back button.go");
  check((await page.textContent("#guide .who")) === st.n, "Open my slip did not open the saved slip");

  // Builder: quoted phrases stay together; topic words pick databases.
  await page.fill("#myq", 'How does "sleep duration" affect grades of high school students in Cuba?');
  const chips = await page.$$eval("#kw button", (bs) => bs.map((b) => b.textContent));
  check(chips.includes('"sleep duration"'), "quoted phrase not kept: " + chips.join("|"));
  const picked = await page.textContent("#picked");
  check(/Google Scholar/.test(picked) && /PubMed|ERIC|SciELO/.test(picked) && /Open Library/.test(picked), "picked: " + picked);

  // Print each period: one slip per page.
  await page.evaluate(() => { window.print = () => {}; });
  for (const p of [1, 2, 3, 4, 5, 6, 7, 8]) {
    await page.click(`#periods .chip[data-p="${p}"]`);
    await page.click("#printp");
    const n = DATA.filter((d) => d.p === p).length;
    check(await page.locator("#printall .slip").count() === n, `period ${p}: print-all slip count`);
    await page.emulateMedia({ media: "print" });
    const pdf = await page.pdf({ path: path.join(OUT, `period${p}.pdf`), format: "Letter" });
    const pages = (pdf.toString("latin1").match(/\/Type\s*\/Page[^s]/g) || []).length;
    check(pages === n, `period ${p} PDF has ${pages} pages for ${n} slips`);
    await page.emulateMedia({ media: "screen" });
    await page.evaluate(() => window.dispatchEvent(new Event("afterprint")));
  }
  check(await page.locator("#printall .slip").count() === 0, "afterprint did not clear the print container");

  // Phone width, both themes: no sideways scroll.
  for (const scheme of ["light", "dark"]) {
    const m = await browser.newPage({ viewport: { width: 375, height: 800 }, colorScheme: scheme });
    await m.route(/fonts\.(googleapis|gstatic)\.com/, (r) => r.abort());
    await m.goto(FILE + "#" + st.id);
    const over = await m.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    check(over <= 0, `${scheme} 375px: ${over}px sideways scroll`);
    await m.screenshot({ path: path.join(OUT, `phone-${scheme}.png`), fullPage: true });
    await m.close();
  }

  check(errors.length === 0, "errors: " + errors.join(" / "));
  await browser.close();
  if (fails.length) { console.error("FAIL\n- " + fails.join("\n- ")); process.exit(1); }
  console.log(`PASS: ${seen} slips across 8 periods, log copy, welcome back, builder, print, phone width`);
})();
