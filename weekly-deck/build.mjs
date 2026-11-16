#!/usr/bin/env node
// Room 63 weekly deck builder. No network.
// Usage: node weekly-deck/build.mjs <week-id>        e.g. node weekly-deck/build.mjs 2026-11-16
// Reads weeks/<week-id>.json and template.html, writes dist/<week-id>/index.html, netlify.toml, _headers,
// and dist/"Room 63 Week of <range> Deck - <date> - <owner>.zip".
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const id = process.argv[2];
if (!id) { console.error('Usage: node weekly-deck/build.mjs <week-id>   (a file in weekly-deck/weeks/)'); process.exit(2); }
const week = JSON.parse(fs.readFileSync(path.join(HERE, 'weeks', id + '.json'), 'utf8'));
const errors = [];
const err = m => errors.push(m);

// ---------- house rules on the data ----------
const BAD_CHARS = [
  [/[\u2012\u2013\u2014\u2015]/, 'en or em dash'],
  [/[\u2018\u2019\u201A\u201B\u201C\u201D\u201E\u201F\u2032\u2033]/, 'curly quote (use straight quotes)'],
  [/[\u{1F000}-\u{1FAFF}\u{2600}-\u{27BF}\u{2B00}-\u{2BFF}\u{FE0F}\u{200D}]/u, 'emoji or pictograph'],
];
const PRIVATE_URL = /(zoom\.us|meet\.google|teams\.microsoft|webex\.com|mail\.google|drive\.google|docs\.google|calendar\.google|chatgpt\.com)/i;
(function walk(v, where) {
  if (typeof v === 'string') {
    for (const [re, what] of BAD_CHARS) if (re.test(v)) err(`${where}: ${what} in "${v.slice(0, 60)}"`);
    if (PRIVATE_URL.test(v)) err(`${where}: private or meeting link "${v}"`);
    if (/\bpwd=|passcode\s*[:=]\s*\S/i.test(v)) err(`${where}: meeting credential`);
  } else if (Array.isArray(v)) v.forEach((x, i) => walk(x, `${where}[${i}]`));
  else if (v && typeof v === 'object') for (const [k, x] of Object.entries(v)) walk(x, `${where}.${k}`);
})(week, 'week');
for (const k of ['week', 'bells', 'days', 'slides', 'routes']) if (!week[k]) err(`missing top-level "${k}"`);
for (const [k, u] of Object.entries(week.materials || {})) (u || []).forEach(m => { if (!/^https:\/\//.test(m.url)) err(`materials.${k}: not a public https URL: ${m.url}`); });

// ---------- references and timing ----------
const toMin = t => { const [h, m] = t.split(':').map(Number); return h * 60 + m; };
const dayIds = new Set((week.days || []).map(d => d.id));
for (const [k, s] of Object.entries(week.slides || {})) {
  if (!['cover', 'opener', 'content', 'guest', 'card', 'pair', 'lab'].includes(s.kind)) err(`slide ${k}: unknown kind ${s.kind}`);
  if (s.kind === 'guest' && !week.guests?.[s.guest]) err(`slide ${k}: unknown guest ${s.guest}`);
  if (s.kind === 'pair') (s.pair || []).forEach(p => { if (!week.slides[p]) err(`slide ${k}: unknown pair slide ${p}`); });
  if (s.reading && !week.readings?.[s.reading]) err(`slide ${k}: unknown reading ${s.reading}`);
  if (!['guest', 'pair', 'lab'].includes(s.kind) && !Array.isArray(s.body)) err(`slide ${k}: body must be a list of lines`);
}
for (const [k, p] of Object.entries(week.practice || {})) {
  if (!['core', 'supported', 'extension'].includes(p.tier)) err(`practice ${k}: tier must be core, supported or extension`);
  if (!(p.dok >= 1 && p.dok <= 4)) err(`practice ${k}: dok must be 1 to 4`);
  if (!p.task || !Array.isArray(p.rubric_rows) || !p.rubric_rows.length) err(`practice ${k}: task and rubric_rows are required`);
  if (!(p.minutes > 0)) err(`practice ${k}: minutes required`);
  for (const row of p.rubric_rows || []) if (week.rubric_rows?.[p.task] && !week.rubric_rows[p.task].rows[row]) err(`practice ${k}: rubric row "${row}" not defined under rubric_rows.${p.task}`);
}
const SPECIAL = ['@target', '@donow', '@agenda', '@criteria', '@practice', '@materials', '@glossary', '@exit', '@next', '@absent'];
const report = [];
for (const r of week.routes || []) {
  const rid = `${r.day}/P${r.period}`;
  if (!dayIds.has(r.day)) err(`route ${rid}: unknown day`);
  const b = week.bells[String(r.period)];
  if (!b) { err(`route ${rid}: no bell time for period ${r.period}`); continue; }
  let total = 0, steps = 0;
  const types = new Set();
  for (const s of r.segments || []) {
    if (!['intro', 'slide', 'guest', 'reteach', 'practice', 'info', 'exit', 'absent'].includes(s.type)) err(`route ${rid}: unknown segment type ${s.type}`);
    types.add(s.type);
    for (const st of s.steps || []) {
      steps++; total += st.minutes || 0;
      if (!st.slide.startsWith('@') && !week.slides[st.slide]) err(`route ${rid}: unknown slide ${st.slide}`);
      if (st.slide.startsWith('@') && !SPECIAL.includes(st.slide)) err(`route ${rid}: unknown special step ${st.slide}`);
      if (st.minutes && !['Silent', 'Partner', 'Group'].includes(st.mode)) err(`route ${rid}: step ${st.slide} needs a work mode (Silent, Partner or Group)`);
      if (false) err(`route ${rid}: unknown slide ${st.slide}`);
    }
  }
  const order = (r.segments || []).flatMap(s => s.steps.map(x => x.slide)).filter(x => SPECIAL.includes(x));
  const want = SPECIAL.filter(x => order.includes(x));
  if (order.join() !== want.join() || want.length !== SPECIAL.length) err(`route ${rid}: needs every part, in order: ${SPECIAL.join(' ')} (has ${order.join(' ')})`);
  for (const f of ['target', 'donow', 'exit', 'next', 'criteria', 'glossary']) if (!r[f]) err(`route ${rid}: missing ${f}`);
  const len = toMin(b[1]) - toMin(b[0]);
  if (total !== len) err(`route ${rid}: segments add to ${total} minutes; the bell gives ${len}`);
  if (!types.has('practice')) err(`route ${rid}: needs a practice segment`);
  if (!types.has('absent') || !week.absent?.[r.absent]) err(`route ${rid}: needs an absent segment and absent work`);
  for (const p of r.practice || []) if (!week.practice?.[p]) err(`route ${rid}: unknown practice item ${p}`);
  const tiers = new Set((r.practice || []).map(p => week.practice?.[p]?.tier));
  if (!(tiers.has('core') && tiers.has('supported') && tiers.has('extension'))) err(`route ${rid}: practice needs core, supported and extension`);
  if (r.guest && !week.guests?.[r.guest]) err(`route ${rid}: unknown guest ${r.guest}`);
  report.push(`${rid.padEnd(8)} ${String(steps).padStart(2)} steps  ${total} min  ${r.label}`);
}
if (errors.length) { console.error('BUILD FAILED\n' + errors.map(e => '  ' + e).join('\n')); process.exit(1); }

// ---------- fonts, embedded so the file works offline (the November 9 deck's faces) ----------
const FONTS = [
  ['Fraunces', 'normal', '500 700', 'nov9-Fraunces-normal-500_700.woff2'],
  ['Cormorant Garamond', 'normal', '500 700', 'nov9-CormorantGaramond-normal-500_700.woff2'],
  ['Space Mono', 'normal', '400', 'nov9-SpaceMono-normal-400.woff2'],
  ['Space Mono', 'normal', '700', 'nov9-SpaceMono-normal-700.woff2'],
];
const fontCss = FONTS.map(([fam, style, weight, file]) => {
  const b64 = fs.readFileSync(path.join(HERE, 'fonts', file)).toString('base64');
  return `@font-face{font-family:'${fam}';src:url('data:font/woff2;base64,${b64}') format('woff2');font-style:${style};font-weight:${weight};font-display:swap}`;
}).join('\n');

// ---------- images (embedded WebP), maps (public-domain boundaries), QR codes ----------
const data = JSON.parse(JSON.stringify(week)); delete data.$schema;
let imgBytes = 0;
for (const [k, m] of Object.entries(data.images || {})) {
  for (const f of ['alt', 'source_url', 'license', 'credit', 'item_id', 'rights_statement']) if (!m[f]) { console.error(`image ${k}: missing ${f}`); process.exit(1); }
  const buf = fs.readFileSync(path.join(HERE, m.file));
  imgBytes += buf.length;
  m.src = 'data:image/webp;base64,' + buf.toString('base64');
  delete m.file;
}
const usedImgs = new Set();
JSON.stringify(week.slides) .replace(/"img":"([^"]+)"/g, (_, x) => usedImgs.add(x));
JSON.stringify(week.next_visuals || {}).replace(/"img":"([^"]+)"/g, (_, x) => usedImgs.add(x));
for (const x of usedImgs) if (!data.images?.[x]) { console.error('visual uses unknown image ' + x); process.exit(1); }
data.maps = JSON.parse(fs.readFileSync(path.join(HERE, 'assets', 'maps.json'), 'utf8')).maps;
const qrcode = (await import('./vendor/qrcode-generator-2.0.4.mjs')).default;
const urls = new Set();
for (const list of Object.values(data.materials || {})) for (const m of list || []) urls.add(m.url);
data.qr = {};
for (const u of urls) {
  const q = qrcode(0, 'M'); q.addData(u); q.make();
  const n = q.getModuleCount(); let d = '';
  for (let y = 0; y < n; y++) for (let x = 0; x < n; x++) if (q.isDark(y, x)) d += `M${x} ${y}h1v1h-1z`;
  data.qr[u] = { n, d };
}

// ---------- page, in two variants: the dated archive site and the permanent current-week site ----------
const json = JSON.stringify(data).replace(/</g, '\\u003c').replace(/\u2028/g, '\\u2028').replace(/\u2029/g, '\\u2029');
const esc = t => String(t).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const tpl = fs.readFileSync(path.join(HERE, 'template.html'), 'utf8');
for (const ph of ['/*FONTS*/', '__DATA__', '__TITLE__', '__BRAND__', '__VARIANT__']) if (!tpl.includes(ph)) { console.error('template is missing placeholder ' + ph); process.exit(1); }
const pub = week.week.publish || {};
const VARIANTS = [
  { key: 'archive', brand: `${week.week.brand} · WEEK OF ${week.week.range.toUpperCase()}`, title: `${week.week.brand} | ${week.week.title}`, site: pub.archive_site, zip: `Room 63 Week of ${week.week.range} Deck - ${week.week.date} - ${week.week.owner || 'Portela J'}.zip` },
  { key: 'current', brand: `${week.week.brand} · THIS WEEK`, title: `${week.week.brand} | This week | ${week.week.title}`, site: pub.current_site, zip: `Room 63 Current Week Deck - ${week.week.date} - ${week.week.owner || 'Portela J'}.zip` },
];
const root = path.join(HERE, 'dist', id);
fs.rmSync(root, { recursive: true, force: true });
for (const v of VARIANTS) {
  const out = path.join(root, v.key);
  fs.mkdirSync(out, { recursive: true });
  const html = tpl.replace('/*FONTS*/', () => fontCss).replace('__DATA__', () => json).replace('__TITLE__', () => esc(v.title)).replace('__BRAND__', () => esc(v.brand)).replace('__VARIANT__', () => v.key);
  fs.writeFileSync(path.join(out, 'index.html'), html);
  fs.writeFileSync(path.join(out, 'netlify.toml'), `# Netlify site: ${v.site || '(set in week.publish)'}  (${v.key} variant). Deploy only with Mr. Portela's approval.\n[build]\n  publish = "."\n`);
  fs.writeFileSync(path.join(out, '_headers'), '/*\n  X-Robots-Tag: noindex\n');
  const zipPath = path.join(root, v.zip);
  execFileSync('zip', ['-q', '-X', '-r', zipPath, 'index.html', 'netlify.toml', '_headers'], { cwd: out });
  console.log(`${v.key.padEnd(8)} dist/${id}/${v.key}/index.html  ${(fs.statSync(path.join(out, 'index.html')).size / 1048576).toFixed(2)} MB  ->  ${v.zip}`);
}
console.log(report.join('\n'));
console.log(`\nImages embedded: ${Object.keys(data.images || {}).length} (${(imgBytes / 1048576).toFixed(2)} MB). QR codes: ${urls.size}.`);
