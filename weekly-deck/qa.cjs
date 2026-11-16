#!/usr/bin/env node
// Room 63 weekly deck QA.  NODE_PATH="$(npm root -g)" node weekly-deck/qa.cjs <week-id> [--shots <dir>]
// Renders every route step and every day page at 1920x1080 (projector), 380x800 and 390x844 (phones).
// Fails on: overflow, horizontal scroll, text under 16px on a phone, touch targets under 44px on a phone,
// console errors, contrast under 4.5:1 (3:1 for large text), any surface brighter than #f6efd8,
// banned fonts (Inter, Roboto, Arial), emoji, en or em dashes, curly quotes; and checks keyboard
// navigation, day tabs, panels, the timer and print.
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const id = process.argv[2];
if (!id) { console.error('Usage: node weekly-deck/qa.cjs <week-id> [--shots <dir>]'); process.exit(2); }
const shotsAt = process.argv.indexOf('--shots');
const SHOTS = shotsAt > 0 ? path.resolve(process.argv[shotsAt + 1]) : null;
const FILE = path.join(__dirname, 'dist', id, 'index.html');
if (!fs.existsSync(FILE)) { console.error('Build first: node weekly-deck/build.mjs ' + id); process.exit(2); }
const URL0 = 'file://' + FILE;
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
  [/<script[^>]+src=|<link[^>]+href="http/gi, 'external script or stylesheet (file must work offline)'],
];
const fileHits = {};
for (const [re, what] of FILE_RULES) { const m = text.match(re) || []; fileHits[what] = m.length; if (m.length) fail('file', `${m.length} x ${what}: ${[...new Set(m)].slice(0, 5).join(' ')}`); }

// ---------- in-page probes ----------
const PROBE = `(() => {
 const PAPER = 0.8628370212647565;
 const lum = c => { const v = c.slice(0,3).map(x => { x /= 255; return x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4); }); return 0.2126*v[0] + 0.7152*v[1] + 0.0722*v[2]; };
 const parse = s => { const m = s.match(/rgba?\\(([^)]+)\\)/); if (!m) return [0,0,0,0]; const p = m[1].split(/[ ,\\/]+/).filter(Boolean).map(Number); return [p[0],p[1],p[2],p.length>3?p[3]:1]; };
 const blend = (f, b) => [0,1,2].map(i => f[i]*f[3] + b[i]*(1-f[3])).concat(1);
 const bgOf = el => { const stack = []; for (let e = el; e; e = e.parentElement) { const c = parse(getComputedStyle(e).backgroundColor); if (c[3] > 0) { stack.push(c); if (c[3] >= 1) break; } } let b = [7,32,27,1]; for (let i = stack.length - 1; i >= 0; i--) b = blend(stack[i], b); return b; };
 const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x,y) + 0.05) / (Math.min(x,y) + 0.05); };
 const visible = e => { if (e.closest('[hidden],#print,.vh')) return false; const r = e.getBoundingClientRect(); if (r.width < 2 || r.height < 2) return false; const s = getComputedStyle(e); return s.visibility !== 'hidden' && s.display !== 'none' && +s.opacity > 0; };
 const ownText = e => [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
 const phone = innerWidth <= 900;
 const out = { overflow: [], hscroll: null, small: [], targets: [], contrast: [], bright: [], fonts: [] };
 const de = document.documentElement;
 if (de.scrollWidth > de.clientWidth + 1 || document.body.scrollWidth > document.body.clientWidth + 1) out.hscroll = 'page ' + de.scrollWidth + ' > ' + de.clientWidth;
 const main = document.getElementById('main'); if (main.scrollWidth > main.clientWidth + 1) out.hscroll = 'stage ' + main.scrollWidth + ' > ' + main.clientWidth;
 const slide = document.querySelector('#content > .slide');
 if (slide) {
  const sr = slide.getBoundingClientRect(), mr = main.getBoundingClientRect();
  if (!phone) {
   if (slide.scrollHeight > slide.clientHeight + 1) out.overflow.push('slide content ' + slide.scrollHeight + ' > ' + slide.clientHeight);
   if (sr.bottom > mr.bottom + 1) out.overflow.push('slide runs below the stage');
   if (main.scrollHeight > main.clientHeight + 1) out.overflow.push('stage scrolls ' + main.scrollHeight + ' > ' + main.clientHeight);
  }
  slide.querySelectorAll('*').forEach(e => { if (!visible(e)) return; const r = e.getBoundingClientRect();
   if (r.right > sr.right + 1 || r.left < sr.left - 1 || (!phone && (r.bottom > sr.bottom + 1 || r.top < sr.top - 1))) out.overflow.push((e.className || e.tagName) + ' ' + Math.round(r.left) + ',' + Math.round(r.top) + ' ' + Math.round(r.width) + 'x' + Math.round(r.height));
   if (e.scrollWidth > e.clientWidth + 1 && getComputedStyle(e).overflowX !== 'visible') out.overflow.push('clipped ' + (e.className || e.tagName)); });
 } else {
  document.querySelectorAll('#content *').forEach(e => { if (!visible(e)) return; const r = e.getBoundingClientRect(); if (r.right > innerWidth + 1) out.overflow.push((e.className || e.tagName) + ' runs off the right edge'); });
 }
 document.querySelectorAll('body *').forEach(e => {
  if (!visible(e)) return;
  const s = getComputedStyle(e);
  if (/\\b(Inter|Roboto|Arial)\\b/i.test(s.fontFamily)) out.fonts.push(e.tagName + ': ' + s.fontFamily);
  const bg = parse(s.backgroundColor); if (bg[3] > 0 && lum(bg) > PAPER + 1e-6) out.bright.push((e.id || e.className || e.tagName) + ' ' + s.backgroundColor);
  if (ownText(e) && !e.closest('select')) {
   const size = parseFloat(s.fontSize);
   if (phone && size < 16) out.small.push(e.tagName + '.' + e.className + ' ' + size + 'px "' + e.textContent.trim().slice(0, 30) + '"');
   if (!e.disabled && !e.closest('button:disabled')) {
    const fg = parse(s.color), b = bgOf(e), c = ratio(blend(fg, b), b);
    const large = size >= 24 || (size >= 18.66 && +s.fontWeight >= 700);
    if (c < (large ? 3 : 4.5)) out.contrast.push(e.tagName + '.' + e.className + ' ' + c.toFixed(2) + ' "' + e.textContent.trim().slice(0, 30) + '"');
   }
  }
  if (phone && e.matches('a[href],button,select,[role=tab]')) {
   const r = e.getBoundingClientRect(), p = e.parentElement;
   const inSentence = e.tagName === 'A' && [...p.childNodes].some(n => n !== e && n.textContent.trim());
   if (!inSentence && (r.width < 44 || r.height < 44)) out.targets.push(e.tagName + ' "' + (e.textContent.trim() || e.getAttribute('aria-label')).slice(0, 24) + '" ' + Math.round(r.width) + 'x' + Math.round(r.height));
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
  if (bad) tally[t].failed++;
}

(async () => {
  const browser = await chromium.launch();
  const consoleErrors = [];
  const routeRows = {};
  for (const v of VIEWS) {
    const ctx = await browser.newContext({ viewport: { width: v.w, height: v.h } });
    const page = await ctx.newPage();
    page.on('console', m => { if (m.type() === 'error') consoleErrors.push(`${v.name}: ${m.text()}`); });
    page.on('pageerror', e => consoleErrors.push(`${v.name}: ${e.message}`));
    await page.goto(URL0 + '#mon');
    await page.evaluate(() => document.fonts.ready);
    const { routes, days } = await page.evaluate(() => ({ routes: window.DECK_TEST.routes.map(r => ({ day: r.day, period: r.period, n: r.steps.length })), days: window.DECK_TEST.data.days.map(d => d.id) }));
    const hashes = [...days.map(d => '#' + d)];
    for (const r of routes) for (let i = 0; i < r.n; i++) hashes.push(`#${r.day}/P${r.period}-${i}`);
    for (const h of hashes) {
      await page.evaluate(h => { location.hash = h; }, h);
      await page.waitForFunction(h => location.hash === h, h, { timeout: 3000 }).catch(() => {});
      await page.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))));
      const got = await page.evaluate(() => location.hash);
      if (got !== h) fail(`${h} @ ${v.name}`, 'route did not load (hash is ' + got + ')');
      const res = await page.evaluate(PROBE);
      record(`${h} @ ${v.name}`, res);
      const key = h.split('-')[0];
      routeRows[key] = routeRows[key] || {};
      routeRows[key][v.name] = routeRows[key][v.name] || { steps: 0, bad: 0 };
      routeRows[key][v.name].steps++;
      if (fails.some(f => f.startsWith(`${h} @ ${v.name}`))) routeRows[key][v.name].bad++;
      if (v.w === 1920 && /-\d+$/.test(h)) {
        const size = await page.evaluate(() => { const li = document.querySelector('#content .slide .lines li'); return li ? parseFloat(getComputedStyle(li).fontSize) : null; });
        if (size !== null && size < 28) fail(`${h} @ ${v.name}`, `body text ${size}px is under 28px at 1920x1080`);
      }
    }
    // panels, open on a route
    await page.evaluate(() => { location.hash = '#wed/P8-3'; });
    await page.waitForTimeout(100);
    for (const [btn, panel] of [['#agbtn', '#agenda'], ['#resbtn', '#res'], ['#libbtn', '#lib']]) {
      await page.click(btn);
      const open = await page.isVisible(panel);
      if (!open) fail(`${panel} @ ${v.name}`, 'panel did not open');
      record(`${panel} panel @ ${v.name}`, await page.evaluate(PROBE));
      if (SHOTS && v.w !== 390) { fs.mkdirSync(SHOTS, { recursive: true }); await page.screenshot({ path: path.join(SHOTS, `${v.phone ? 'phone' : 'desk'}-panel-${panel.slice(1)}.png`) }); }
      await page.keyboard.press('Escape');
      if (await page.isVisible(panel)) fail(`${panel} @ ${v.name}`, 'Escape did not close the panel');
    }
    await ctx.close();
  }

  // ---------- behavior: keyboard, tabs, timer, print ----------
  const ctx = await browser.newContext({ viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();
  page.on('pageerror', e => consoleErrors.push('behavior: ' + e.message));
  page.on('console', m => { if (m.type() === 'error') consoleErrors.push('behavior: ' + m.text()); });
  await page.goto(URL0 + '#mon/P2-0');
  const behave = [];
  const expectHash = async (label, want) => { const h = await page.evaluate(() => location.hash); const ok = h === want; behave.push(`${ok ? 'PASS' : 'FAIL'}  ${label}: ${h}`); if (!ok) fail('behavior', `${label}: wanted ${want}, got ${h}`); };
  await page.focus('#main');
  await page.keyboard.press('ArrowRight'); await expectHash('ArrowRight moves to the next slide', '#mon/P2-1');
  await page.keyboard.press('PageDown'); await expectHash('PageDown moves to the next slide', '#mon/P2-2');
  await page.keyboard.press(' '); await expectHash('Space moves to the next slide', '#mon/P2-3');
  await page.keyboard.press('ArrowLeft'); await expectHash('ArrowLeft moves back', '#mon/P2-2');
  await page.keyboard.press('PageUp'); await expectHash('PageUp moves back', '#mon/P2-1');
  await page.keyboard.press('End'); await expectHash('End jumps to the last step (absent work)', '#mon/P2-11');
  await page.keyboard.press('ArrowRight'); await expectHash('ArrowRight stops at the last step', '#mon/P2-11');
  await page.keyboard.press('Home'); await expectHash('Home returns to the day page', '#mon');
  await page.click('#next', { trial: true }).catch(() => {});
  for (const d of ['tue', 'wed', 'thu', 'fri', 'mon']) {
    await page.click(`#days button[data-day=${d}]`);
    await expectHash(`day tab ${d}`, '#' + d);
    const st = await page.evaluate(d => ({ pressed: document.querySelector(`#days button[data-day=${d}]`).getAttribute('aria-pressed'), cards: document.querySelectorAll('.choice').length, routes: window.DECK_TEST.routes.filter(r => r.day === d).length }), d);
    const ok = st.pressed === 'true' && st.cards === st.routes;
    behave.push(`${ok ? 'PASS' : 'FAIL'}  day tab ${d}: pressed=${st.pressed}, ${st.cards} period cards for ${st.routes} routes`);
    if (!ok) fail('behavior', `day tab ${d} state ${JSON.stringify(st)}`);
  }
  await page.click('.choice'); await expectHash('period card opens the route', '#mon/P2-0');
  await page.selectOption('#jump', '4'); await expectHash('jump control', '#mon/P2-4');
  await page.selectOption('#route', '4'); await expectHash('period control', '#mon/P4-0');
  await page.goto(URL0 + '#mon/P2-1');
  const t0 = await page.textContent('#timer');
  await page.click('#play'); await page.waitForTimeout(2300);
  const t1 = await page.textContent('#timer');
  const ok = t0 === '05:00' && t1 < t0;
  behave.push(`${ok ? 'PASS' : 'FAIL'}  timer counts down from the step's minutes: ${t0} then ${t1}`);
  if (!ok) fail('behavior', `timer ${t0} -> ${t1}`);
  await page.click('#reset');
  const t2 = await page.textContent('#timer');
  behave.push(`${t2 === '05:00' ? 'PASS' : 'FAIL'}  reset: ${t2}`); if (t2 !== '05:00') fail('behavior', 'reset ' + t2);
  // print: one page per step, nothing clipped
  for (const h of ['#tue/P1-0', '#wed/P8-0', '#mon/P6-0']) {
    await page.goto(URL0 + h); await page.evaluate(() => document.fonts.ready);
    const n = await page.evaluate(() => window.DECK_TEST.routes.find(r => location.hash.startsWith('#' + r.day + '/P' + r.period + '-')).steps.length);
    await page.emulateMedia({ media: 'print' });
    const clipped = await page.evaluate(() => [...document.querySelectorAll('#print .slide')].map((s, i) => s.scrollHeight > s.clientHeight + 1 ? i : -1).filter(i => i >= 0));
    await page.emulateMedia({ media: 'screen' });
    const pdf = await page.pdf({ width: '13.333in', height: '7.5in', printBackground: true, preferCSSPageSize: true });
    const pages = (pdf.toString('latin1').match(/\/Type\s*\/Page[^s]/g) || []).length;
    const good = pages === n && !clipped.length;
    behave.push(`${good ? 'PASS' : 'FAIL'}  print ${h}: ${pages} pages for ${n} steps${clipped.length ? ', clipped steps ' + clipped.join(',') : ''}`);
    if (!good) fail('print', `${h}: ${pages} pages for ${n} steps, clipped ${clipped.join(',')}`);
    if (SHOTS && h === '#tue/P1-0') fs.writeFileSync(path.join(SHOTS, 'print-tue-P1.pdf'), pdf);
  }
  await ctx.close();

  // ---------- screenshots of each distinct slide type ----------
  if (SHOTS) {
    fs.mkdirSync(SHOTS, { recursive: true });
    const TYPES = [['mon', 'day page'], ['mon/P4-0', 'cover'], ['mon/P4-1', 'content'], ['mon/P4-2', 'guest'], ['mon/P4-3', 'practice tiers'], ['mon/P4-5', 'absent work'], ['mon/P2-0', 'opener'], ['mon/P2-2', 'long list'], ['mon/P2-3', 'reading citation'], ['mon/P2-4', 'statement'], ['tue/P1-2', 'R1 opener'], ['tue/P1-4', 'R1.2 with R1.3'], ['wed/P8-3', 'guest in Workshop 2'], ['wed/P8-12', 'absent with guest note'], ['fri', 'Friday card']];
    for (const v of [VIEWS[0], VIEWS[1]]) {
      const c = await browser.newContext({ viewport: { width: v.w, height: v.h } });
      const p = await c.newPage(); await p.goto(URL0 + '#mon'); await p.evaluate(() => document.fonts.ready);
      for (const [h, label] of TYPES) {
        await p.evaluate(h => { location.hash = '#' + h; }, h); await p.waitForTimeout(80);
        await p.screenshot({ path: path.join(SHOTS, `${v.phone ? 'phone' : 'desk'}-${h.replace('/', '_')}.png`), fullPage: false });
      }
      await c.close();
    }
    fs.writeFileSync(path.join(SHOTS, 'types.json'), JSON.stringify(TYPES));
  }
  await browser.close();

  if (consoleErrors.length) fail('console', consoleErrors.slice(0, 5).join(' | '));
  // ---------- report ----------
  console.log('File checks (hits):');
  for (const [k, n] of Object.entries(fileHits)) console.log(`  ${n === 0 ? 'PASS' : 'FAIL'}  ${k}: ${n}`);
  console.log('\nRoutes (steps rendered, steps failing) per view:');
  const vn = VIEWS.map(v => v.name);
  console.log('  ' + 'route'.padEnd(10) + vn.map(n => n.padEnd(24)).join(''));
  for (const [k, row] of Object.entries(routeRows)) console.log('  ' + k.padEnd(10) + vn.map(n => row[n] ? `${row[n].bad ? 'FAIL' : 'PASS'} ${row[n].steps} steps, ${row[n].bad} bad`.padEnd(24) : ''.padEnd(24)).join(''));
  console.log('\nRenders per view:');
  for (const [k, t] of Object.entries(tally)) console.log(`  ${k}: ${t.checked} checked, ${t.failed} failing`);
  console.log('\nBehavior:\n  ' + behave.join('\n  '));
  console.log(`\nConsole errors: ${consoleErrors.length}`);
  if (fails.length) { console.log(`\nQA FAILED: ${fails.length} problem(s)`); fails.slice(0, 80).forEach(f => console.log('  ' + f)); process.exit(1); }
  console.log('\nQA PASS');
})().catch(e => { console.error(e); process.exit(1); });
