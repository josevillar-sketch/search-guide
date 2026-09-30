// Render-check a Room 63 book: every page fits, every jump lands, no console errors.
// Usage: node tools/check_book.js <key> [shotsDir]   (serves from http://localhost:8763/<key>/)
const path = require('path');
const { chromium } = require(process.env.PW || '/opt/node22/lib/node_modules/playwright');
(async () => {
  const key = process.argv[2], shots = process.argv[3];
  const b = await chromium.launch();
  const report = { key, errors: [], pages: [] };
  for (const [vw, vh, label] of [[1366, 900, 'desk'], [820, 1180, 'ipad']]) {
    const p = await b.newPage({ viewport: { width: vw, height: vh } });
    p.on('pageerror', e => report.errors.push(label + ' pageerror: ' + e.message));
    p.on('console', m => { if (m.type() === 'error' && !/netlify|favicon|fonts\.g/.test(m.text())) report.errors.push(label + ' console: ' + m.text()); });
    await p.goto(`http://localhost:8763/${key}/`, { waitUntil: 'load' });
    await p.waitForTimeout(3500);
    const res = await p.evaluate(async () => {
      const faces = window.FACES, out = [];
      // wait for the engine to fit every page, then re-measure each page the way the engine does
      for (let t = 0; t < 200; t++) { const pend = [...document.querySelectorAll('.leaf .pg')].filter(x => x.dataset.fit !== '1'); if (!pend.length) break; await new Promise(r => setTimeout(r, 100)); }
      const book = document.getElementById('book');
      const C = parseFloat(book.style.width), F = C / .72;
      const floor = document.body.classList.contains('none') ? .72 : .8;
      const pgs = [...document.querySelectorAll('.leaf .face')];
      for (let i = 0; i < pgs.length; i++) {
        const face = pgs[i], pg0 = face.querySelector('.pg');
        const info = { i, label: faces[i] && faces[i].label };
        if (pg0) {
          const g = parseFloat(pg0.style.getPropertyValue('--g')) || 1;
          const n = face.cloneNode(true); n.classList.add('probe', 'live'); n.classList.remove('back');
          n.style.cssText = `position:fixed;left:-30000px;top:0;width:${C}px;height:${F}px;transform:none;backface-visibility:visible;visibility:hidden;pointer-events:none`;
          document.body.appendChild(n);
          const pg = n.querySelector('.pg'); pg.querySelectorAll('.fill').forEach(e => e.style.marginTop = '0');
          const top = pg.getBoundingClientRect().top, lim = pg.getBoundingClientRect().bottom - top - parseFloat(getComputedStyle(pg).paddingBottom) - .012 * C;
          pg.style.setProperty('--g', g);
          let m = 0, wide = 0; const right = pg.getBoundingClientRect().right;
          for (const x of pg.querySelectorAll('*')) { const r = x.getBoundingClientRect(); if (r.height > 0 && r.bottom - top > m) m = r.bottom - top; if (r.width > 0 && r.right > right + 2) wide++; }
          info.g = g; info.over = Math.round(m - lim); info.hOverflow = wide;
          n.remove();
        }
        out.push(info);
      }
      // jumps
      const bad = [];
      faces.forEach((f, i) => { (f.html.match(/data-jump='(\d+)'/g) || []).forEach(m => { const t = +m.match(/\d+/)[0]; if (t < 0 || t >= faces.length) bad.push([i, t]); }); });
      // page numbers: paper faces from index 2 count 1,2,3...; a chapter board takes the number of the next paper page
      const pno = []; let c = 0;
      faces.forEach((f, i) => { if (i >= 2 && /\bpaper\b/.test(f.cls)) pno[i] = ++c; });
      for (let i = faces.length - 1, nxt = null; i >= 0; i--) { if (pno[i]) nxt = pno[i]; else if (/chapter/.test(faces[i].cls)) pno[i] = nxt; }
      const lab = [];
      faces.forEach((f, i) => { const re = /data-jump='(\d+)'[^>]*aria-label='Go to page (\d+)'/g; let m; while ((m = re.exec(f.html))) if (+m[2] !== pno[+m[1]]) lab.push([i, +m[1], +m[2], pno[+m[1]]]); });
      const num = [];
      faces.forEach((f, i) => { const m = f.html.match(/class='num'>&middot; (\d+) &middot;/); if (m && +m[1] !== pno[i]) num.push([i, +m[1], pno[i]]); });
      // visible page numbers on buttons (pn/gpn/gtag/pj text) should match the aria label
      faces.forEach((f, i) => { const re = /data-jump='(\d+)' aria-label='Go to page (\d+)'>(?:Page )?(\d+)</g; let m; while ((m = re.exec(f.html))) if (m[2] !== m[3]) lab.push([i, +m[1], 'text', m[3], m[2]]); });
      // TABS must point at chapter boards
      const tabs = (window.TABS || []).filter(t => !/chapter/.test(faces[t.f] && faces[t.f].cls)).map(t => t.f);
      return { out, bad, lab, num, tabs, N: faces.length };
    });
    report[label] = { N: res.N, badJumps: res.bad, badLabels: res.lab, badNums: res.num, badTabs: res.tabs,
      overflow: res.out.filter(x => x.over > 0).map(x => [x.i, x.over, x.g]), tight: res.out.filter(x => x.g !== undefined && x.g < .9).map(x => [x.i, x.g]),
      hOverflow: res.out.filter(x => x.hOverflow).map(x => [x.i, x.hOverflow]) };
    if (shots) {
      for (let i = 0; i < res.N; i += 1) {
        await p.evaluate(i => window.__rl && window.__rl.go(i), i);
        await p.waitForTimeout(450);
        if (label === 'desk' && i % 2 === 1) continue;
        await p.screenshot({ path: path.join(shots, `${key}-${label}-${String(i).padStart(2, '0')}.png`) });
      }
    }
    await p.close();
  }
  await b.close();
  console.log(JSON.stringify(report, null, 1));
})();
