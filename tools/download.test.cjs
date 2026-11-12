// Current-desk private saved-data copy. Disposable synthetic storage; no network or student-record output.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { createHash } = require('node:crypto');
const { launchHarness } = require('./browser-harness.cjs');
const INDEX = path.resolve(__dirname, '..', 'index.html');
const source = fs.readFileSync(INDEX);
const output = path.resolve(__dirname, '..', 'test-results', 'download');
fs.mkdirSync(output, { recursive: true });
const evidence = { source_sha256: createHash('sha256').update(source).digest('hex'), checks: [], layouts: [] };
const DATA = JSON.parse(source.toString('utf8').match(/var DATA = (\[.*?\]);\n/s)[1]);
const [A, B] = DATA.filter(student => student.c === 'R');
const key = student => 'r63sg_wb_' + student.id;
const sheet = () => ({ dots: [0,0,0,0,0,0,0], circles: [], lenses: [], purpose: '', expect: '', hate: '' });
const record = () => ({ schema: 1, id: A.id, course: A.c,
  rec: { q: A.q, asof: '2026-09-29', leads: false, sheet: sheet() },
  versions: [{ k: 'download-synthetic', n: 2, date: '2026-11-10', text: 'Synthetic saved version café 🧪?',
    prev: 'Synthetic earlier version?', why: 'Synthetic reason.', reason: '', rc: 0, saved: 1, penned: false, sheet: sheet() }],
  draft: null, updated: 1 });
const frames = page => page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));

(async () => {
  const harness = await launchHarness(INDEX);
  let context, page, passed = 0, failed = 0;
  async function fresh(raw = JSON.stringify(record()), recovery = '', options = {}) {
    if (context) await context.close();
    context = await harness.browser.newContext({ viewport: { width: 1180, height: 900 }, reducedMotion: 'reduce', ...options });
    context.setDefaultTimeout(15000);
    await context.route(/fonts\.(googleapis|gstatic)\.com/, route => route.abort());
    page = await context.newPage();
    await page.goto(harness.url);
    await page.evaluate(([own, other, raw, recovery]) => {
      localStorage.clear();
      if (raw !== null) localStorage.setItem(own, raw);
      localStorage.setItem(other, 'OTHER_DESK_SENTINEL');
      if (recovery) localStorage.setItem('r63sg_bad_' + own.slice(9) + '_synthetic', recovery);
    }, [key(A), key(B), raw, recovery]);
    await page.goto(harness.url + '#' + A.id);
    await frames(page);
    return page;
  }
  async function watch() {
    await page.evaluate(() => {
      window.__downloadWrites = []; window.__downloadReads = []; window.__downloadCount = 0;
      const get = Storage.prototype.getItem, set = Storage.prototype.setItem, remove = Storage.prototype.removeItem;
      Storage.prototype.getItem = function(k) { window.__downloadReads.push(k); return get.call(this, k); };
      Storage.prototype.setItem = function(k, v) { window.__downloadWrites.push(k); return set.call(this, k, v); };
      Storage.prototype.removeItem = function(k) { window.__downloadWrites.push(k); return remove.call(this, k); };
    });
    page.on('download', () => { page.__copies = (page.__copies || 0) + 1; });
  }
  async function copy() {
    const [file] = await Promise.all([page.waitForEvent('download'), page.click('#ipad-download')]);
    assert.equal(file.suggestedFilename(), 'room63-private-copy.json', 'filename must remain generic');
    const stream = await file.createReadStream(), chunks = [];
    for await (const chunk of stream) chunks.push(chunk);
    return JSON.parse(Buffer.concat(chunks).toString('utf8'));
  }
  async function check(name, fn) {
    try { await fn(); passed++; evidence.checks.push({name, status:'passed'}); console.log('ok ' + name); }
    catch (error) { failed++; evidence.checks.push({name, status:'failed'}); console.error('FAIL ' + name + ': ' + String(error.message).split('\n')[0]); }
    finally { if (context) await context.close(); context = null; }
  }
  try {
    await check('current desk offers an explicit private-copy action', async () => {
      await fresh(); assert.equal(await page.locator('#ipad-download').count(), 1, 'private-copy action is absent');
    });
    if (!process.argv.includes('--presence-only') && !failed) {
      await check('own saved bytes and recovery survive without writes or other-desk reads', async () => {
        const raw = JSON.stringify(record()), original = 'Synthetic malformed recovery { café';
        await fresh(raw, original); await watch();
        await page.evaluate(() => { document.getElementById('wb-text').value = 'UNSAVED_SYNTHETIC_TEXT'; });
        const out = await copy();
        assert(!JSON.stringify(out).includes('UNSAVED_SYNTHETIC_TEXT'), 'unsaved fields must not be exported');
        assert(out.saved === raw, 'saved record bytes changed'); assert(out.recovery === original, 'raw recovery changed');
        assert.deepEqual(Object.keys(out).sort(), ['format','recovery','saved','version']);
        assert.equal(out.format, 'room63-saved-data'); assert.equal(out.version, 1);
        const state = await page.evaluate(() => ({ writes: window.__downloadWrites, reads: window.__downloadReads }));
        assert.equal(state.writes.length, 0, 'copy must not write or clear storage');
        assert(state.reads.every(k => k === key(A)), 'copy read another storage key');
        evidence.payload = { keys: Object.keys(out).sort(), saved_bytes_preserved: out.saved === raw,
          recovery_bytes_preserved: out.recovery === original, storage_writes: state.writes.length,
          reads_current_key_only: state.reads.every(k => k === key(A)), unsaved_fields_excluded: true };
      });
      await check('large newer-schema data remains complete and read-only', async () => {
        const raw = JSON.stringify({ schema: 2, id: A.id, course: A.c, versions: [], future: 'é🧪'.repeat(75000) });
        await fresh(raw); await watch(); const out = await copy();
        assert(out.saved === raw, 'large raw record was truncated or sanitized');
        assert.equal((await page.evaluate(() => window.__downloadWrites)).length, 0, 'newer schema must not be rewritten');
      });
      await check('malformed saved JSON is copied verbatim rather than sanitized', async () => {
        const raw = '{unreadable synthetic JSON café';
        await fresh(raw); await watch(); const out = await copy();
        assert(out.saved === raw, 'malformed original changed'); assert(out.recovery.includes(raw), 'quarantined original missing');
        assert.equal((await page.evaluate(() => window.__downloadWrites)).length, 0, 'malformed recovery copy mutated storage');
      });
      await check('foreign-record identity blocks a copy', async () => {
        const foreign = record(); foreign.schema = 2; foreign.id = B.id;
        await fresh(JSON.stringify(foreign)); await watch(); await page.click('#ipad-download'); await frames(page);
        assert.equal(page.__copies || 0, 0, 'foreign record must not be downloaded');
        assert.equal((await page.evaluate(() => window.__downloadWrites)).length, 0, 'foreign-record rejection changed storage');
      });
      await check('recovery entry boundaries prevent pretty-JSON foreign records leaking', async () => {
        const foreign = '{"id":"foreign-synthetic-desk",\n\n"text":"OTHER_DESK_ONLY_SYNTHETIC"}';
        await fresh(undefined, foreign);
        await page.evaluate(([own, extra]) => localStorage.setItem('r63sg_bad_' + own.slice(9) + '_second', extra),
          [key(A), 'Own malformed recovery {']);
        await page.reload(); await frames(page); await watch();
        await page.click('#ipad-download'); await frames(page);
        assert.equal(page.__copies || 0, 0, 'foreign recovery record must not be downloaded');
        assert.equal((await page.evaluate(() => window.__downloadWrites)).length, 0, 'identity rejection changed storage');
      });
      await check('unpaired Unicode is rejected without replacement or storage changes', async () => {
        await fresh('Synthetic broken ' + String.fromCharCode(0xd800)); await watch();
        await page.click('#ipad-download'); await frames(page);
        assert.equal(page.__copies || 0, 0, 'invalid Unicode must not be exported');
        assert.equal((await page.evaluate(() => window.__downloadWrites)).length, 0, 'Unicode rejection changed storage');
      });
      await check('denied storage and unsupported download fail without a file', async () => {
        await fresh(); await watch();
        await page.evaluate(() => { Storage.prototype.getItem = () => { throw new DOMException('Synthetic denial', 'SecurityError'); }; });
        await page.click('#ipad-download'); await frames(page); assert.equal(page.__copies || 0, 0);
        assert.equal((await page.evaluate(() => window.__downloadWrites)).length, 0);
        await fresh(); await watch(); await page.evaluate(() => { URL.createObjectURL = () => { throw Error('Synthetic unavailable'); }; });
        await page.click('#ipad-download'); await frames(page); assert.equal(page.__copies || 0, 0);
      });
      await check('same-session revision change cannot download stale data', async () => {
        await fresh(); await watch();
        await page.evaluate(([k, changed]) => {
          const create = URL.createObjectURL.bind(URL);
          URL.createObjectURL = blob => { const url = create(blob); localStorage.setItem(k, changed); return url; };
        }, [key(A), 'NEW_REMOTE_SAVED_BYTES']);
        await page.click('#ipad-download'); await frames(page); assert.equal(page.__copies || 0, 0);
        assert(await page.evaluate(k => localStorage.getItem(k) === 'NEW_REMOTE_SAVED_BYTES', key(A)), 'remote bytes were overwritten');
      });
      await check('desk exit invalidates an in-flight object URL', async () => {
        await fresh(); await watch(); await page.evaluate(() => {
          const create = URL.createObjectURL.bind(URL);
          URL.createObjectURL = blob => { const url = create(blob); document.getElementById('who-not').click(); return url; };
        });
        await page.click('#ipad-download'); await frames(page); assert.equal(page.__copies || 0, 0);
        assert.equal(await page.locator('#ipad-backup').isVisible(), false, 'desk exit revealed private contents');
      });
      await check('keyboard action fits all widths themes and explicit fallback fonts', async () => {
        for (const width of [320, 820, 1440]) for (const colorScheme of ['light', 'dark'])
          for (const fontMode of ['authored', 'fallback']) {
          await fresh(undefined, '', { viewport: { width, height: 1000 }, colorScheme }); await watch();
          if (fontMode === 'fallback') await page.addStyleTag({ content:
            ':root{--body:Verdana,system-ui,sans-serif;--display:Georgia,"Times New Roman",serif;--mono:"Courier New",ui-monospace,monospace}' });
          await page.evaluate(() => document.fonts.ready); await frames(page);
          const button = page.locator('#ipad-download'); await button.focus();
          const [download] = await Promise.all([page.waitForEvent('download'), page.keyboard.press('Enter')]);
          assert.equal(download.suggestedFilename(), 'room63-private-copy.json');
          const box = await button.boundingBox(); assert(box && box.width >= 44 && box.height >= 44, 'private-copy target is too small');
          assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'layout overflows');
          const cdp = await context.newCDPSession(page); await cdp.send('DOM.enable'); await cdp.send('CSS.enable');
          const { root } = await cdp.send('DOM.getDocument');
          const { nodeId } = await cdp.send('DOM.querySelector', { nodeId: root.nodeId, selector:'#ipad-download' });
          const { fonts } = await cdp.send('CSS.getPlatformFontsForNode', { nodeId });
          const names = fonts.filter(f => f.glyphCount).map(f => f.familyName);
          assert(names.length, 'actual glyph font evidence is absent');
          if (fontMode === 'fallback') assert(names.every(n => !/Atkinson|Fraunces|Space Mono/i.test(n)), 'primary fonts remain in fallback test');
          if (fontMode === 'authored' && process.env.DOWNLOAD_REQUIRE_PRIMARY_FONTS === '1')
            assert(names.some(n => /Atkinson Hyperlegible/.test(n)), 'authored body font unavailable');
          evidence.layouts.push({ width, theme:colorScheme, font_mode:fontMode, actual_glyph_fonts:names,
            button_width:box.width, button_height:box.height, no_overflow:true, keyboard_download:true });
          await cdp.detach();
          if (width === 320) {
            await page.locator('#ipad').screenshot({ path:path.join(output, `private-copy-${fontMode}-${colorScheme}-320.png`) });
          }
        }
      });
    }
    console.log(`${passed} private-copy checks passed, ${failed} failed`);
    evidence.passed = passed; evidence.failed = failed;
    evidence.source_unchanged = fs.readFileSync(INDEX).equals(source);
    fs.writeFileSync(path.join(output, 'evidence.json'), JSON.stringify(evidence, null, 2) + '\n');
    process.exitCode = failed || !evidence.source_unchanged ? 1 : 0;
  } finally { if (context) await context.close(); await harness.close(); }
})().catch(() => { console.error('Private-copy suite could not initialize.'); process.exitCode = 1; });
