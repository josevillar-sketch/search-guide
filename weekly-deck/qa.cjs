#!/usr/bin/env node
// Room 63 weekly deck QA.
//   NODE_PATH="$(npm root -g)" node weekly-deck/qa.cjs <week-id> [--shots <dir>]
// Serves dist/<week-id>/archive over local HTTP and renders every route step and every week and day page
// at 1920x1080 (projector), 380x800 and 390x844 (phones). Fails on: overflow, horizontal scroll, text under
// 16px on a phone (SVG labels measured as rendered), touch targets under 44px on a phone, console errors,
// contrast under 4.5:1 (3:1 for large text), any surface brighter than #f6efd8, banned fonts, emoji,
// en or em dashes, curly quotes, meeting links, images without alt text or license records.
// Then checks behavior: keyboard, number jump, builds, day tabs, panels, timer, sound off by default,
// swipe, two-window sync, poll, sort, chart, flip cards, annotation, name picker, teacher mode,
// Spanish toggle, text size, every print mode (page counts with pdfinfo), and animation smoothness under
// a 4x CPU throttle.
const fs = require('fs');
const path = require('path');
const http = require('http');
const { execFileSync } = require('child_process');
const { chromium } = require('playwright');

const id = process.argv[2];
if (!id) { console.error('Usage: node weekly-deck/qa.cjs <week-id> [--shots <dir>]'); process.exit(2); }
const shotsAt = process.argv.indexOf('--shots');
const SHOTS = shotsAt > 0 ? path.resolve(process.argv[shotsAt + 1]) : null;
const DIR = path.join(__dirname, 'dist', id, 'archive');
const FILE = path.join(DIR, 'index.html');
if (!fs.existsSync(FILE)) { console.error('Build first: node weekly-deck/build.mjs ' + id); process.exit(2); }
const VIEWS = [
  { name: 'projector 1920x1080', w: 1920, h: 1080, phone: false },
  { name: 'phone 380x800', w: 380, h: 800, phone: true },
  { name: 'phone 390x844', w: 390, h: 844, phone: true },
];
const fails = [];
const tally = {};
const fail = (where, msg) => fails.push(`${where}: ${msg}`);

// ---------- 1. the file itself ----------
const src = fs.readFileSync(FILE, 'utf8');
const text = src.replace(/base64,[A-Za-z0-9+/=]+/g, 'base64,');
const FILE_RULES = [
  [/\b(Inter|Roboto|Arial)\b/g, 'banned font name'],
  [/[\u2012\u2013\u2014\u2015]/g, 'en or em dash'],
  [/[\u2018\u2019\u201C\u201D]/g, 'curly quote'],
  [/[\u{1F000}-\u{1FAFF}\u{2600}-\u{27BF}\u{2B00}-\u{2BFF}\u{FE0F}]/gu, 'emoji or pictograph'],
  [/(zoom\.us|meet\.google|teams\.microsoft|webex\.com|mail\.google|drive\.google|docs\.google|pwd=)/gi, 'meeting or private link'],
  [/<script[^>]+src=|<link[^>]+href="http|@import|url\(['"]?https?:/gi, 'external script, stylesheet or font (the file must work offline)'],
];
const fileHits = {};
for (const [re, what] of FILE_RULES) { const m = text.match(re) || []; fileHits[what] = m.length; if (m.length) fail('file', `${m.length} x ${what}: ${[...new Set(m)].slice(0, 5).join(' ')}`); }
{ const m = src.match(/<script id="deckdata" type="application\/json">([\s\S]*?)<\/script>/); const data = JSON.parse(m[1]);
  for (const [k, im] of Object.entries(data.images || {})) { const y = (im.credit.split(' \u00b7 ')[1] || ''); if (!/^(\d{4}|\d{4}-\d{4}|c\. \d{4})$/.test(y)) fail('credits', `${k}: year field "${y}" is not YYYY, YYYY-YYYY or c. YYYY`); for (const f of ['alt', 'source_url', 'item_id', 'rights_statement', 'license']) if (!im[f]) fail('credits', `${k}: missing ${f}`); }
  fileHits['credit lines with a bad year'] = fails.filter(f => f.startsWith('credits')).length; }
const sizeMB = fs.statSync(FILE).size / 1048576;
if (sizeMB > 25) fail('file', `size ${sizeMB.toFixed(1)} MB is over the 25 MB target`);

// ---------- local server ----------
const server = http.createServer((req, res) => {
  const p = decodeURIComponent(req.url.split('?')[0]);
  const f = path.join(DIR, p === '/' ? 'index.html' : p);
  if (!f.startsWith(DIR) || !fs.existsSync(f)) { res.writeHead(404); res.end(); return; }
  res.writeHead(200, { 'Content-Type': f.endsWith('.html') ? 'text/html; charset=utf-8' : 'application/octet-stream' });
  fs.createReadStream(f).pipe(res);
});

// ---------- in-page probe ----------
const PROBE = `(() => {
 const PAPER = 0.8628370212647565;
 const lum = c => { const v = c.slice(0,3).map(x => { x /= 255; return x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4); }); return 0.2126*v[0] + 0.7152*v[1] + 0.0722*v[2]; };
 const parse = s => { const m = s.match(/rgba?\\(([^)]+)\\)/); if (!m) return [0,0,0,0]; const p = m[1].split(/[ ,\\/]+/).filter(Boolean).map(Number); return [p[0],p[1],p[2],p.length>3?p[3]:1]; };
 const blend = (f, b) => [0,1,2].map(i => f[i]*f[3] + b[i]*(1-f[3])).concat(1);
 const bgOf = el => { const stack = []; for (let e = el; e; e = e.parentElement) { const c = parse(getComputedStyle(e).backgroundColor); if (c[3] > 0) { stack.push(c); if (c[3] >= 1) break; } } let b = [20,17,13,1]; for (let i = stack.length - 1; i >= 0; i--) b = blend(stack[i], b); return b; };
 const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x,y) + 0.05) / (Math.min(x,y) + 0.05); };
 const visible = e => { if (e.closest('[hidden],#print,.vh,.leave')) return false; const r = e.getBoundingClientRect(); if (r.width < 2 || r.height < 2) return false; const s = getComputedStyle(e); return s.visibility !== 'hidden' && s.display !== 'none' && +s.opacity > 0.05; };
 const ownText = e => [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
 const phone = innerWidth <= 900;
 const out = { overflow: [], hscroll: null, small: [], targets: [], contrast: [], bright: [], fonts: [], alt: [] };
 const de = document.documentElement;
 if (de.scrollWidth > de.clientWidth + 1 || document.body.scrollWidth > document.body.clientWidth + 1) out.hscroll = 'page ' + de.scrollWidth + ' > ' + de.clientWidth;
 const main = document.getElementById('main'); if (main.scrollWidth > main.clientWidth + 1) out.hscroll = 'stage ' + main.scrollWidth + ' > ' + main.clientWidth;
 const slide = document.querySelector('#content > .slide:not(.leave)');
 if (slide) {
  const sr = slide.getBoundingClientRect(), mr = main.getBoundingClientRect();
  if (!phone) {
   if (slide.scrollHeight > slide.clientHeight + 1) out.overflow.push('slide content ' + slide.scrollHeight + ' > ' + slide.clientHeight);
   if (sr.bottom > mr.bottom + 1) out.overflow.push('slide runs below the stage');
   if (main.scrollHeight > main.clientHeight + 1) out.overflow.push('stage scrolls ' + main.scrollHeight + ' > ' + main.clientHeight);
  }
  slide.querySelectorAll('*').forEach(e => { if (!visible(e) || e.closest('.doc,.amb,.grain,.map svg *,.fly')) return; const r = e.getBoundingClientRect();
   if (r.right > sr.right + 1 || r.left < sr.left - 1 || (!phone && (r.bottom > sr.bottom + 1 || r.top < sr.top - 1))) out.overflow.push((e.getAttribute('class') || e.tagName) + ' ' + Math.round(r.left) + ',' + Math.round(r.top) + ' ' + Math.round(r.width) + 'x' + Math.round(r.height));
   if (!(e instanceof SVGElement) && e.scrollHeight > e.clientHeight + 2 && ['hidden','auto','scroll'].includes(getComputedStyle(e).overflowY) && !e.closest('.doc,.spot,.crop,.exhibit,.map')) out.overflow.push('clipped ' + (e.getAttribute('class') || e.tagName)); });
 } else {
  document.querySelectorAll('#content *').forEach(e => { if (!visible(e) || e.closest('.amb')) return; const r = e.getBoundingClientRect(); if (r.right > innerWidth + 1) out.overflow.push((e.getAttribute('class') || e.tagName) + ' runs off the right edge'); });
 }
 document.querySelectorAll('body *').forEach(e => {
  if (!visible(e)) return;
  const s = getComputedStyle(e);
  if (/\\b(Inter|Roboto|Arial)\\b/i.test(s.fontFamily)) out.fonts.push(e.tagName + ': ' + s.fontFamily);
  const bg = parse(s.backgroundColor); if (bg[3] > 0 && lum(bg) > PAPER + 1e-6) out.bright.push((e.id || e.getAttribute('class') || e.tagName) + ' ' + s.backgroundColor);
  if (e.tagName === 'IMG' && !(e.getAttribute('alt') || '').trim()) out.alt.push(e.src.slice(0, 40));
  if (ownText(e) && !e.closest('select')) {
   let size = parseFloat(s.fontSize);
   if (e instanceof SVGElement) { const m = e.getScreenCTM(); if (m) size = size * Math.abs(m.a); }
   if (phone && size < 15.9) out.small.push(e.tagName + '.' + (e.getAttribute('class') || '') + ' ' + size.toFixed(1) + 'px "' + e.textContent.trim().slice(0, 30) + '"');
   if (!(e instanceof SVGElement) && !e.disabled && !e.closest('button:disabled') && !e.closest('.doc')) {
    const fg = parse(s.color), b = bgOf(e), c = ratio(blend(fg, b), b);
    const large = size >= 24 || (size >= 18.66 && +s.fontWeight >= 700);
    if (c < (large ? 3 : 4.5)) out.contrast.push(e.tagName + '.' + (e.getAttribute('class') || '') + ' ' + c.toFixed(2) + ' "' + e.textContent.trim().slice(0, 30) + '"');
   }
  }
  if (phone && e.matches('a[href],button,select,[role=tab],input[type=range],input[type=checkbox]')) {
   const r = e.getBoundingClientRect(), p = e.parentElement;
   const inSentence = e.tagName === 'A' && [...p.childNodes].some(n => n !== e && n.textContent.trim());
   const box = e.matches('input[type=checkbox]') ? e.closest('label').getBoundingClientRect() : r;
   if (!inSentence && (box.width < 44 || box.height < 44)) out.targets.push(e.tagName + ' "' + (e.textContent.trim() || e.getAttribute('aria-label') || '').slice(0, 24) + '" ' + Math.round(box.width) + 'x' + Math.round(box.height));
  }
 });
 const bs = parse(getComputedStyle(document.body).backgroundColor); if (lum(bs) > PAPER + 1e-6) out.bright.push('body');
 return out;
})()`;

function record(where, r) {
  const t = where.split(' @ ')[1];
  tally[t] = tally[t] || { checked: 0, failed: 0 };
  tally[t].checked++;
  let bad = false;
  const push = (k, list) => { if (list && list.length) { bad = true; fail(where, `${k}: ${[...new Set(list)].slice(0, 4).join(' | ')}${list.length > 4 ? ' (+' + (list.length - 4) + ')' : ''}`); } };
  push('overflow', r.overflow);
  if (r.hscroll) { bad = true; fail(where, 'horizontal scroll ' + r.hscroll); }
  push('text under 16px', r.small);
  push('touch target under 44px', r.targets);
  push('contrast', r.contrast);
  push('surface brighter than #f6efd8', r.bright);
  push('banned font', r.fonts);
  push('image without alt text', r.alt);
  if (bad) tally[t].failed++;
  return bad;
}
const pdfPages = buf => { const f = path.join(require('os').tmpdir(), 'r63qa-' + process.pid + '.pdf'); fs.writeFileSync(f, buf); const o = execFileSync('pdfinfo', [f]).toString(); fs.unlinkSync(f); return +(o.match(/Pages:\s+(\d+)/) || [0, 0])[1]; };

(async () => {
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const BASE = `http://127.0.0.1:${server.address().port}/index.html`;
  const browser = await chromium.launch();
  const consoleErrors = [];
  const routeRows = {};
  const listen = (page, tag) => { page.on('console', m => { if (m.type() === 'error') consoleErrors.push(`${tag}: ${m.text()}`); }); page.on('pageerror', e => consoleErrors.push(`${tag}: ${e.message}`)); };
  const settle = page => page.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))));

  // ---------- 2. every route, every view ----------
  for (const v of VIEWS) {
    const ctx = await browser.newContext({ viewport: { width: v.w, height: v.h } });
    const page = await ctx.newPage(); listen(page, v.name);
    await page.goto(BASE + '#week'); await page.evaluate(() => document.fonts.ready);
    await page.evaluate(() => window.DECK_TEST.still(true));
    const { routes, days } = await page.evaluate(() => ({ routes: window.DECK_TEST.routes.map(r => ({ day: r.day, period: r.period, n: r.steps.length })), days: window.DECK_TEST.data.days.map(d => d.id) }));
    const hashes = ['#week', ...days.map(d => '#' + d)];
    for (const r of routes) for (let i = 0; i < r.n; i++) hashes.push(`#${r.day}/P${r.period}-${i}`);
    for (const h of hashes) {
      await page.evaluate(h => { location.hash = h; }, h);
      await page.waitForFunction(h => location.hash === h, h, { timeout: 3000 }).catch(() => {});
      await page.evaluate(() => window.DECK_TEST.revealAll()); await settle(page);
      const got = await page.evaluate(() => location.hash);
      if (got !== h) fail(`${h} @ ${v.name}`, 'route did not load (hash is ' + got + ')');
      const bad = record(`${h} @ ${v.name}`, await page.evaluate(PROBE));
      const key = h.includes('/') ? h.split('-')[0] : 'pages';
      routeRows[key] = routeRows[key] || {};
      const row = routeRows[key][v.name] = routeRows[key][v.name] || { steps: 0, bad: 0 };
      row.steps++; if (bad) row.bad++;
      if (v.w === 1920 && h.includes('/')) {
        const size = await page.evaluate(() => { const li = document.querySelector('#content > .slide:not(.leave) .stage2 .lines li, #content > .slide:not(.leave) > .body .lines li, #content > .slide:not(.leave) .body > .lines li'); return li ? parseFloat(getComputedStyle(li).fontSize) : null; });
        if (size !== null && size < 28) fail(`${h} @ ${v.name}`, `body text ${size.toFixed(1)}px is under 28px at 1920x1080`);
      }
    }
    for (const [btn, panel] of [['#agbtn', '#agenda'], ['#resbtn', '#res'], ['#libbtn', '#lib'], ['#guestbtn', '#guest'], ['#toolsbtn', '#tools']]) {
      await page.evaluate(() => { location.hash = '#wed/P8-0'; }); await settle(page);
      if (v.phone && ['#resbtn', '#libbtn', '#guestbtn'].includes(btn)) await page.evaluate(b => document.querySelector(b).click(), btn); else await page.click(btn);
      if (!(await page.isVisible(panel))) fail(`${panel} @ ${v.name}`, 'panel did not open');
      record(`${panel} panel @ ${v.name}`, await page.evaluate(PROBE));
      if (SHOTS && v.w !== 390) { fs.mkdirSync(SHOTS, { recursive: true }); await page.screenshot({ path: path.join(SHOTS, `${v.phone ? 'phone' : 'desk'}-panel-${panel.slice(1)}.png`) }); }
      await page.keyboard.press('Escape');
      if (await page.isVisible(panel)) fail(`${panel} @ ${v.name}`, 'Escape did not close the panel');
    }
    await ctx.close();
  }

  // ---------- 3. behavior ----------
  const behave = [];
  const ok = (cond, label, detail) => { behave.push(`${cond ? 'PASS' : 'FAIL'}  ${label}${detail ? ': ' + detail : ''}`); if (!cond) fail('behavior', `${label}${detail ? ': ' + detail : ''}`); };
  const ctx = await browser.newContext({ viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage(); listen(page, 'behavior');
  const hashIs = async (label, want) => { const h = await page.evaluate(() => location.hash); ok(h === want, label, h); };
  const st = () => page.evaluate(() => window.DECK_TEST.state());
  const go0 = page.goto.bind(page);
  page.goto = async (u, o) => { const r = await go0(u, o); await page.reload(); await page.waitForTimeout(150); return r; };
  await page.goto(BASE + '#mon/P2-0'); await page.evaluate(() => document.fonts.ready);
  const IX = await page.evaluate(() => Object.fromEntries(window.DECK_TEST.routes.map(r => [r.id, r.steps.map(s => s.slide)])));
  const ix = (rid, slide) => IX[rid].indexOf(slide);
  ok(await page.evaluate(() => !window.DECK_TEST.snd().chime && !window.DECK_TEST.snd().trans && !window.DECK_TEST.snd().scape && !window.DECK_TEST.snd().ac), 'all sound off by default, no audio context created');
  await page.focus('#main');
  await page.keyboard.press('ArrowRight'); await hashIs('ArrowRight moves on from a step with no builds', '#mon/P2-1');
  let s0 = await st();
  await page.keyboard.press('ArrowRight'); let s1 = await st();
  ok(s0.items > 0 && s1.built === s0.built + 1 && s1.i === 1, 'Next builds the next line in before moving on', `${s0.built} -> ${s1.built} of ${s1.items}`);
  await page.keyboard.press('a'); s1 = await st(); ok(s1.built === s1.items, 'A reveals every build on the slide');
  await page.keyboard.press('PageDown'); await hashIs('PageDown (clicker) moves on', '#mon/P2-2');
  await page.keyboard.press('PageUp'); await hashIs('PageUp (clicker) goes back', '#mon/P2-1');
  await page.keyboard.press('1'); await page.keyboard.press('0'); await page.keyboard.press('Enter'); await hashIs('number jump 1 0 Enter', '#mon/P2-10');
  await page.keyboard.press('End'); await hashIs('End goes to absent work', '#mon/P2-15');
  await page.keyboard.press('b'); ok(await page.isVisible('#blk'), 'B blacks out the screen'); await page.keyboard.press('b'); ok(!(await page.isVisible('#blk')), 'B again brings it back');
  await page.keyboard.press('Home'); await hashIs('Home goes to the day page', '#mon');
  await page.keyboard.press('Home'); await hashIs('Home again goes to the week overview', '#week');
  await page.waitForTimeout(500);
  const cells = await page.evaluate(() => [document.querySelectorAll('#content > :not(.leave) .cell:not(.empty):not(.fri)').length, window.DECK_TEST.routes.length]);
  ok(cells[0] === cells[1], 'week overview has a cell for every route', `${cells[0]} cells, ${cells[1]} routes`);
  for (const d of ['tue', 'wed', 'thu', 'fri', 'mon']) {
    await page.click(`#days button[data-day=${d}]`); await hashIs(`day tab ${d}`, '#' + d);
    const x = await page.evaluate(d => ({ pressed: document.querySelector(`#days button[data-day=${d}]`).getAttribute('aria-pressed'), cards: document.querySelectorAll('#content > :not(.leave) .choice').length, routes: window.DECK_TEST.routes.filter(r => r.day === d).length }), d);
    ok(x.pressed === 'true' && x.cards === x.routes, `day tab ${d} state`, `${x.cards} period cards for ${x.routes} routes`);
  }
  await page.click('#content .choice'); await hashIs('a period card opens its route', '#mon/P2-0');
  await page.selectOption('#jump', '4'); await hashIs('jump control', '#mon/P2-4');
  await page.selectOption('#route', '4'); await hashIs('period control', '#mon/P4-0');
  await page.goto(BASE + '#mon/P2-1');
  const t0 = await page.textContent('#timer'); await page.click('#play'); await page.waitForTimeout(2300); const t1 = await page.textContent('#timer');
  ok(t0 === '05:00' && t1 < t0, 'segment timer counts down from the step minutes', `${t0} then ${t1}`);
  const off = await page.evaluate(() => getComputedStyle(document.querySelector('#tring .fg')).strokeDashoffset);
  ok(parseFloat(off) > 0, 'timer ring sweeps', off);
  await page.click('#reset'); ok((await page.textContent('#timer')) === '05:00', 'timer reset');
  // the timer never advances on its own
  await page.goto(BASE + '#mon/P2-0'); await page.evaluate(() => { sessionStorage.setItem('r63-week-timer', JSON.stringify({ '2026-11-16/mon-p2/0': { end: Date.now() + 1500 } })); });
  await page.reload(); await page.waitForTimeout(2600);
  ok((await page.evaluate(() => location.hash)) === '#mon/P2-0' && (await page.textContent('#timer')) === '00:00', 'at zero the timer stops and waits for the teacher');
  // interactives
  await page.goto(BASE + '#mon/P2-' + ix('mon-p2', 'sem-5')); await page.evaluate(() => window.DECK_TEST.revealAll());
  await page.click('[data-opt="A"]'); await page.click('[data-opt="A"]'); await page.click('[data-opt="C"]');
  ok((await page.evaluate(() => [...document.querySelectorAll('.prow .pn')].map(x => x.textContent).join(','))) === '2,0,1', 'room poll tallies taps locally');
  await page.goto(BASE + '#tue/P1-' + ix('tue-p1', 'r1-lab')); await page.waitForTimeout(200);
  const chartA = await page.evaluate(() => document.querySelector('[data-lib="2"] .val').textContent);
  await page.click('[data-var="a"]'); const chartB = await page.evaluate(() => document.querySelector('[data-lib="2"] .val').textContent);
  ok(chartA === '1,200' && chartB === '6', 'chart toggles the variable', `${chartA} -> ${chartB}`);
  await page.fill('#libn', '1'); await page.dispatchEvent('#libn', 'input');
  ok((await page.evaluate(() => document.querySelector('[data-lib="2"] .val').textContent)) === '', 'slider hides libraries');
  await page.click('[data-chip="0"]'); ok(await page.evaluate(() => !!document.querySelector('[data-bin="in"] [data-chip="0"]')), 'tap moves a claim into a bin');
  const chip = await page.$('[data-chip="1"]'); const bin = await page.$('[data-bin="out"]'); const cb = await chip.boundingBox(), bb = await bin.boundingBox();
  await page.mouse.move(cb.x + 20, cb.y + 10); await page.mouse.down(); await page.mouse.move(bb.x + 40, bb.y + 60, { steps: 8 }); await page.mouse.up();
  ok(await page.evaluate(() => !!document.querySelector('[data-bin="out"] [data-chip="1"]')), 'drag moves a claim into a bin');
  const gl = ix('mon-p2', '@glossary');
  await page.goto(BASE + '#mon/P2-' + gl); await page.evaluate(() => window.DECK_TEST.revealAll());
  await page.click('.gflip'); ok(await page.evaluate(() => document.querySelector('.gflip').classList.contains('on')), 'glossary card flips');
  await page.keyboard.press('p'); ok(await page.isVisible('#ink'), 'P opens the annotation layer');
  await page.mouse.move(700, 500); await page.mouse.down(); await page.mouse.move(900, 600, { steps: 6 }); await page.mouse.up();
  ok(await page.evaluate(() => { const c = document.getElementById('ink'); const d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data; for (let i = 3; i < d.length; i += 4) if (d[i]) return true; return false; }), 'pen draws on the slide');
  await page.click('#inkbar [data-ink=off]'); ok(!(await page.isVisible('#ink')), 'Done closes the annotation layer');
  // tools: picker, teacher mode, language, text size
  await page.click('#toolsbtn');
  await page.fill('#pickin', 'AB, cd; E.F.G., Jonathan Smith'); await page.click('#pickload');
  const pm = await page.textContent('#pickmsg'); ok(/^3 initials loaded\. 2 entries skipped/.test(pm), 'name picker keeps initials only', pm);
  ok((await page.inputValue('#pickin')) === '', 'the pasted list is cleared from the box');
  await page.click('#pickgo'); await page.waitForTimeout(1100); const picked = await page.textContent('#pickout'); ok(['AB', 'CD', 'EFG'].includes(picked), 'picker draws an initial', picked);
  ok(await page.evaluate(() => !JSON.stringify(localStorage).includes('EFG') && !JSON.stringify(sessionStorage).includes('EFG')), 'initials are never stored');
  await page.fill('#tpass', 'wrong'); await page.click('#tgo'); await page.waitForTimeout(100); ok(/did not open/.test(await page.textContent('#tmsg')), 'wrong passcode keeps teacher mode closed');
  await page.fill('#tpass', 'room63'); await page.click('#tgo'); await page.waitForTimeout(150); ok(await page.evaluate(() => document.querySelectorAll('#toolsbody .cue li').length > 5), 'teacher passcode opens scripts and timing cues');
  const cueText = await page.textContent('#toolsbody'); ok(!/zoom\.us|meet\.google|@/.test(cueText), 'teacher mode holds no links or emails');
  await page.click('[data-pref=lang][data-v=es]'); await page.keyboard.press('Escape');
  await page.goto(BASE + '#mon/P2-' + ix('mon-p2', '@absent')); ok(await page.evaluate(() => document.querySelectorAll('#content .es').length >= 3), 'Spanish toggle adds Spanish directions and absent work');
  await page.evaluate(() => window.DECK_TEST.setPref('lang', 'en'));
  await page.evaluate(() => window.DECK_TEST.setPref('ts', 2)); ok(await page.evaluate(() => document.documentElement.classList.contains('ts2')), 'text size A++');
  await page.evaluate(() => window.DECK_TEST.setPref('ts', 0)); await page.evaluate(() => window.DECK_TEST.setPref('dys', true)); ok(await page.evaluate(() => document.documentElement.classList.contains('dys')), 'wide reading spacing'); await page.evaluate(() => window.DECK_TEST.setPref('dys', false));
  // print: every mode, page counts and nothing clipped
  const PRINTS = [['#tue/P1-0', 'slides', null], ['#tue/P1-0', 'absent-one', 1], ['#week', 'absent-all', null], ['#tue/P1-0', 'cards', 4], ['#mon', 'day', 4], ['#week', 'week', null]];
  for (const [h, mode, want0] of PRINTS) {
    await page.goto(BASE + h); await page.evaluate(() => document.fonts.ready);
    const want = want0 || await page.evaluate(m => m === 'slides' ? window.DECK_TEST.routes.find(r => r.id === 'tue-p1').steps.length : m === 'absent-all' ? window.DECK_TEST.routes.length : window.DECK_TEST.routes.length + 2, mode);
    await page.evaluate(m => window.DECK_TEST.renderPrint(m), mode);
    await page.emulateMedia({ media: 'print' });
    const info = await page.evaluate(() => { const pages = [...document.querySelectorAll('#print > .slide, #print > .lp')]; return { clipped: pages.map((p, i) => (p.scrollHeight > p.clientHeight + 2 || [...p.querySelectorAll('.c57')].some(c => c.scrollHeight > c.clientHeight + 2)) ? i : -1).filter(i => i >= 0), front: Math.min(...[...document.querySelectorAll('#print .c57:not(.back) li')].map(l => parseFloat(getComputedStyle(l).fontSize)), 99) }; });
    const pdf = await page.pdf({ preferCSSPageSize: true, printBackground: true });
    await page.emulateMedia({ media: 'screen' });
    const n = pdfPages(pdf);
    ok(n === want && !info.clipped.length, `print ${mode} (${h})`, `${n} pages, expected ${want}${info.clipped.length ? ', clipped pages ' + info.clipped.join(',') : ''}`);
    if (mode === 'cards') ok(info.front >= 18.6, 'practice card fronts at 14pt or larger', (info.front * 0.75).toFixed(1) + 'pt');
    if (SHOTS) fs.writeFileSync(path.join(SHOTS, `print-${mode}.pdf`), pdf);
  }
  await ctx.close();

  // swipe on a touch screen
  const tctx = await browser.newContext({ viewport: { width: 390, height: 844 }, hasTouch: true });
  const tp = await tctx.newPage(); listen(tp, 'touch');
  await tp.goto(BASE + '#mon/P2-2'); await tp.waitForTimeout(200);
  await tp.evaluate(() => { const m = document.getElementById('main'); const mk = (type, x) => { const t = new Touch({ identifier: 1, target: m, clientX: x, clientY: 400 }); m.dispatchEvent(new TouchEvent(type, { touches: type === 'touchend' ? [] : [t], changedTouches: [t], bubbles: true })); }; mk('touchstart', 320); mk('touchend', 120); });
  await tp.waitForTimeout(150);
  ok((await tp.evaluate(() => location.hash)) === '#mon/P2-3', 'swipe left moves to the next slide (builds are off on phones)');
  await tctx.close();

  // two windows on one computer stay in step
  const sctx = await browser.newContext({ viewport: { width: 1280, height: 720 } });
  const a = await sctx.newPage(), b2 = await sctx.newPage(); listen(a, 'sync A'); listen(b2, 'sync B');
  await a.goto(BASE + '#mon/P2-0'); await b2.goto(BASE + '#mon/P2-0');
  await a.evaluate(() => { location.hash = '#mon/P2-5'; }); await b2.waitForTimeout(500);
  ok((await b2.evaluate(() => location.hash)) === '#mon/P2-5', 'second window follows the first (BroadcastChannel)');
  await a.keyboard.press('b'); await b2.waitForTimeout(300); ok(await b2.isVisible('#blk'), 'blackout reaches the second window');
  await sctx.close();

  // ---------- 4. motion under a school-laptop CPU (4x throttle) ----------
  const mctx = await browser.newContext({ viewport: { width: 1920, height: 1080 } });
  const mp = await mctx.newPage(); listen(mp, 'motion');
  await mp.goto(BASE + '#mon/P4-0'); await mp.evaluate(() => document.fonts.ready);
  const cdp = await mctx.newCDPSession(mp); await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 });
  const frames = [];
  for (let k = 0; k < 10; k++) {
    const f = await mp.evaluate(() => new Promise(res => { const ts = []; let t0 = performance.now(); const tick = t => { ts.push(t); if (t - t0 < 900) requestAnimationFrame(tick); else res(ts); }; window.DECK_TEST.revealAll(); document.getElementById('next').click(); requestAnimationFrame(tick); }));
    for (let i = 1; i < f.length; i++) frames.push(f[i] - f[i - 1]);
  }
  await cdp.send('Emulation.setCPUThrottlingRate', { rate: 1 });
  frames.sort((x, y) => x - y);
  const avg = frames.reduce((x, y) => x + y, 0) / frames.length, p95 = frames[Math.floor(frames.length * 0.95)], worst = frames[frames.length - 1];
  const fps = 1000 / avg;
  ok(fps >= 30 && p95 < 50, 'slide transitions under 4x CPU throttle', `${fps.toFixed(0)} fps average, p95 frame ${p95.toFixed(1)} ms, worst ${worst.toFixed(0)} ms over ${frames.length} frames`);
  await mctx.close();

  // ---------- 5. screenshots of each distinct type ----------
  if (SHOTS) {
    fs.mkdirSync(SHOTS, { recursive: true });
    const r = await (async () => { const c = await browser.newContext(); const p = await c.newPage(); await p.goto(BASE); const x = await p.evaluate(() => window.DECK_TEST.routes.map(r => ({ id: r.id, steps: r.steps.map(s => s.slide) }))); await c.close(); return x; })();
    const idx = (rid, slide) => r.find(x => x.id === rid).steps.indexOf(slide);
    const T = (rid, slide, label) => [rid.replace('-p', '/P') + '-' + idx(rid, slide), label];
    const TYPES = [['week', 'week overview'], ['mon', 'day page'], ['fri', 'Friday card'],
      T('mon-p4', '@target', 'learning target'), T('mon-p4', '@donow', 'do now'), T('mon-p4', '@agenda', 'agenda'), T('mon-p4', '@criteria', 'success criteria'), T('mon-p4', 'r-cover', 'cover'), T('mon-p4', 'r-studio', 'proposal work'), T('mon-p4', 'g-kohler', 'guest exhibit and map'),
      T('mon-p4', '@practice', 'practice tiers'), T('mon-p4', '@materials', 'materials and QR'), T('mon-p4', '@glossary', 'glossary'), T('mon-p4', '@exit', 'exit ticket'), T('mon-p4', '@next', 'next class'), T('mon-p4', '@absent', 'absent work'),
      T('mon-p2', 'sem-1', 'do now from the deck'), T('mon-p2', 'sem-2', 'meter'), T('mon-p2', 'sem-3', 'reading citation and timeline'), T('mon-p2', 'sem-4', 'reasoning chain'), T('mon-p2', 'sem-5', 'room poll'), T('mon-p2', 'sem-6', 'credibility check'), T('mon-p2', 'sem-7', 'peer check'), T('mon-p2', '@exit', 'Seminar exit'),
      T('tue-p1', 'r1-open', 'R1 opener'), T('tue-p1', 'r1-1', 'record exhibit'), T('tue-p1', 'r1-23', 'R1.2 with R1.3'), T('tue-p1', 'r1-lab', 'lab'), T('tue-p1', 'r1-4', 'R1.4 timeline'), T('tue-p1', '@exit', 'R1.5 exit'),
      T('wed-p2', '@donow', 'Workshop 2 do now'), T('wed-p2', 'sem-11', 'Carr citation'), T('wed-p2', 'sem-12', 'matrix'), T('wed-p2', 'sem-13', 'concept map'), T('wed-p2', 'sem-15', 'merge'), T('wed-p2', 'sem-16', 'report plan chain'), T('wed-p2', '@next', 'Book Fair map'),
      T('wed-p8', 'g-obejas', 'guest editorial'), T('thu-p3', 'g-rosales', 'guest world map'), T('tue-p3', 'g-cooper', 'guest Miami map'), T('thu-p1', 'g-piao', 'guest US map')];
    for (const v of [VIEWS[0], VIEWS[1]]) {
      const c = await browser.newContext({ viewport: { width: v.w, height: v.h } });
      const p = await c.newPage(); await p.goto(BASE + '#week'); await p.evaluate(() => document.fonts.ready);
      for (const [h] of TYPES) { await p.evaluate(h => { location.hash = '#' + h; }, h); await p.evaluate(() => window.DECK_TEST.revealAll()); await p.waitForTimeout(3200); await p.screenshot({ path: path.join(SHOTS, `${v.phone ? 'phone' : 'desk'}-${h.replace('/', '_')}.png`) }); }
      await c.close();
    }
    fs.writeFileSync(path.join(SHOTS, 'types.json'), JSON.stringify(TYPES));
  }
  await browser.close(); server.close();

  if (consoleErrors.length) fail('console', consoleErrors.slice(0, 5).join(' | '));
  console.log(`File: ${path.relative(process.cwd(), FILE)} (${sizeMB.toFixed(2)} MB)`);
  console.log('File checks (hits):');
  for (const [k, n] of Object.entries(fileHits)) console.log(`  ${n === 0 ? 'PASS' : 'FAIL'}  ${k}: ${n}`);
  console.log('\nRoutes (steps rendered, steps failing) per view:');
  const vn = VIEWS.map(v => v.name);
  console.log('  ' + 'route'.padEnd(10) + vn.map(n => n.padEnd(26)).join(''));
  for (const [k, row] of Object.entries(routeRows)) console.log('  ' + k.padEnd(10) + vn.map(n => row[n] ? `${row[n].bad ? 'FAIL' : 'PASS'} ${row[n].steps} renders, ${row[n].bad} bad`.padEnd(26) : ''.padEnd(26)).join(''));
  console.log('\nRenders per view (including panels):');
  for (const [k, t] of Object.entries(tally)) console.log(`  ${k}: ${t.checked} checked, ${t.failed} failing`);
  console.log('\nBehavior:\n  ' + behave.join('\n  '));
  console.log(`\nConsole errors: ${consoleErrors.length}`);
  if (fails.length) { console.log(`\nQA FAILED: ${fails.length} problem(s)`); fails.slice(0, 120).forEach(f => console.log('  ' + f)); process.exit(1); }
  console.log('\nQA PASS');
})().catch(e => { console.error(e); server.close(); process.exit(1); });
