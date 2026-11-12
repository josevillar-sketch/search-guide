// Exercise the actual POSIX consent builder with synthetic commands and a stale DOCX.
// No application data, network, or document conversion is used in these control-flow cases.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

if (process.platform === 'win32') {
  console.error('BLOCKED consent gate checks: POSIX /bin/sh is required.');
  process.exit(2);
}
const script = fs.readFileSync(path.join(__dirname, '..', 'classroom', 'build-consent.sh'));

function runCase(options = {}) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'r63-consent-gate-'));
  try {
    const bin = path.join(root, 'bin'), output = path.join(root, 'output'), trace = path.join(root, 'trace');
    fs.mkdirSync(bin); fs.mkdirSync(output);
    fs.mkdirSync(path.join(output, 'prior'));
    fs.writeFileSync(path.join(output, 'prior', 'check.pdf'), 'stale previous PDF');
    fs.writeFileSync(path.join(root, 'build-consent.sh'), script);
    fs.writeFileSync(path.join(root, 'consent-templates.md'), 'Synthetic input');
    fs.writeFileSync(path.join(root, 'consent-templates.docx'), 'stale DOCX');
    const programs = {
      pandoc: `if(+process.env.PANDOC_EXIT)process.exit(+process.env.PANDOC_EXIT);fs.writeFileSync('consent-templates.docx','fresh synthetic DOCX');`,
      python3: `if(+process.env.PYTHON_EXIT)process.exit(+process.env.PYTHON_EXIT);if(process.argv[3])fs.writeFileSync(path.join(process.argv[3],'check.docx'),'synthetic check DOCX');`,
      pdfinfo: `console.log('Pages: '+(process.argv[2].includes('distribution')?process.env.ACTUAL_PAGES:process.env.STRESS_PAGES));`,
      pdffonts: `console.log('synthetic font listing');`,
      soffice: `if(+process.env.RENDER_EXIT)process.exit(+process.env.RENDER_EXIT);if(process.env.NO_PDF!=='1'){const a=process.argv.slice(2),out=a[a.indexOf('--outdir')+1],input=a[a.length-1];fs.writeFileSync(path.join(out,path.basename(input,'.docx')+'.pdf'),'%PDF-synthetic-gate');}`,
    };
    for (const [name, body] of Object.entries(programs)) {
      if (name === 'soffice' && options.missingRenderer) continue;
      const code = `#!${process.execPath}\nconst fs=require('node:fs'),path=require('node:path');fs.appendFileSync(process.env.CONSENT_TRACE,'${name}\\n');${body}\n`;
      fs.writeFileSync(path.join(bin, name), code, { mode: 0o755 });
    }
    const result = spawnSync('/bin/sh', [path.join(root, 'build-consent.sh')], {
      cwd: root,
      env: { ...process.env,
        PATH: options.missingRenderer ? bin : bin + path.delimiter + process.env.PATH,
        CONSENT_OUT: output, CONSENT_TRACE: trace,
        PANDOC_EXIT: String(options.pandocExit || 0), PYTHON_EXIT: String(options.pythonExit || 0),
        RENDER_EXIT: String(options.renderExit || 0), NO_PDF: options.noPDF ? '1' : '0',
        STRESS_PAGES: String(options.stressPages || 9), ACTUAL_PAGES: String(options.actualPages || 9),
      },
      encoding: 'utf8', timeout: 15000, maxBuffer: 256 * 1024,
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    assert.ifError(result.error);
    assert.equal(result.signal, null);
    const commands = fs.existsSync(trace) ? fs.readFileSync(trace, 'utf8').trim().split('\n') : [];
    const fresh = fs.readdirSync(output).filter(name => name.startsWith('consent-'));
    return { status: result.status, commands, output: result.stdout,
      docx: fs.readFileSync(path.join(root, 'consent-templates.docx'), 'utf8'),
      freshStress: fresh.some(name => fs.existsSync(path.join(output, name, 'check.pdf'))),
      freshActual: fresh.some(name => fs.existsSync(path.join(output, name, 'distribution', 'consent-templates.pdf'))),
    };
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
}

let passed = 0, failed = 0;
function check(name, test) {
  try { test(); passed++; console.log('ok ' + name); }
  catch (error) { failed++; console.error('FAIL ' + name + ': ' + String(error.message).split('\n')[0]); }
}
check('failed pandoc cannot render the stale DOCX', () => {
  const r = runCase({ pandocExit: 17 });
  assert.equal(r.status, 17); assert.deepEqual(r.commands, ['pandoc']); assert.equal(r.docx, 'stale DOCX');
});
check('failed Python formatting stops before rendering', () => {
  const r = runCase({ pythonExit: 23 });
  assert.equal(r.status, 23); assert.deepEqual(r.commands, ['pandoc', 'python3']);
});
check('missing renderer is blocked before any build', () => {
  const r = runCase({ missingRenderer: true });
  assert.notEqual(r.status, 0); assert.deepEqual(r.commands, []); assert.equal(r.docx, 'stale DOCX');
});
check('renderer failure cannot pass', () => {
  const r = runCase({ renderExit: 31 });
  assert.equal(r.status, 31); assert(!r.commands.includes('pdfinfo'));
});
check('old PDF cannot satisfy a missing fresh conversion', () => {
  const r = runCase({ noPDF: true });
  assert.notEqual(r.status, 0); assert.equal(r.freshStress, false); assert(!r.commands.includes('pdfinfo'));
});
check('stress page overflow is rejected before distribution conversion', () => {
  const r = runCase({ stressPages: 10 });
  assert.notEqual(r.status, 0); assert.equal(r.commands.filter(x => x === 'soffice').length, 1);
});
check('actual distribution overflow cannot hide behind a nine-page stress copy', () => {
  const r = runCase({ actualPages: 10 });
  assert.notEqual(r.status, 0); assert.equal(r.commands.filter(x => x === 'soffice').length, 2);
});
check('success requires both fresh nine-page render paths', () => {
  const r = runCase();
  assert.equal(r.status, 0); assert(r.freshStress && r.freshActual);
  assert.equal(r.commands.filter(x => x === 'pdfinfo').length, 2);
});
console.log(`${passed} consent gate checks passed, ${failed} failed`);
process.exitCode = failed ? 1 : 0;
