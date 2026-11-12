// Infrastructure checks: no application assertions or student content in output.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const net = require("node:net");
const os = require("node:os");
const path = require("node:path");
const { spawn } = require("node:child_process");
const { launchHarness } = require("./browser-harness.cjs");

const root = path.resolve(__dirname, "..");
const helper = path.join(__dirname, "browser-harness.cjs");
const index = path.join(root, "index.html");

const deadline = (promise, label, ms = 45000) => {
  let timer;
  return Promise.race([
    promise,
    new Promise((_, reject) => { timer = setTimeout(() => reject(new Error(`${label} timed out`)), ms); }),
  ]).finally(() => clearTimeout(timer));
};

function closedPort(url) {
  return new Promise((resolve, reject) => {
    const socket = net.connect(Number(new URL(url).port), "127.0.0.1");
    socket.setTimeout(3000, () => socket.destroy(new Error("Preview-port check timed out")));
    socket.once("connect", () => { socket.destroy(); reject(new Error("Preview port remains open after cleanup")); });
    socket.once("error", (error) => error.code === "ECONNREFUSED" ? resolve() : reject(error));
  });
}

function startChild(code, env = process.env) {
  const child = spawn(process.execPath, ["-e", code], {
    cwd: root, env, stdio: ["ignore", "pipe", "pipe", "ipc"],
  });
  let stdout = "", stderr = "";
  child.stdout.on("data", (data) => { stdout += data; });
  child.stderr.on("data", (data) => { stderr += data; });
  const exited = new Promise((resolve, reject) => {
    child.once("error", reject);
    child.once("close", (exitCode, signal) => resolve({ exitCode, signal, stdout, stderr }));
  });
  return { child, exited, output: () => stdout };
}

async function stopChild(run) {
  if (run.child.exitCode !== null || run.child.signalCode !== null) return;
  run.child.kill("SIGTERM");
  try { await deadline(run.exited, "Child cleanup", 5000); }
  catch { run.child.kill("SIGKILL"); await run.exited.catch(() => {}); }
}

(async () => {
  const code = `require(${JSON.stringify(helper)}).launchHarness(${JSON.stringify(index)})`;
  const invalid = startChild(`${code}.then(h=>h.close()).catch(e=>{console.error(e.message);process.exitCode=1})`, {
    ...process.env,
    PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH: path.join(os.tmpdir(), `missing-r63-browser-${process.pid}-${Date.now()}`),
  });
  try {
    const result = await deadline(invalid.exited, "Invalid-browser check");
    assert.equal(result.exitCode, 1);
    assert.match(result.stderr, /PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH must name an executable browser file/);
  } finally { await stopChild(invalid); }
  console.log("ok invalid browser override fails clearly");

  const harness = await launchHarness(index);
  try {
    assert.equal(new URL(harness.url).hostname, "127.0.0.1");
    assert.equal(harness.browser.isConnected(), true);
    await assert.rejects(async () => { throw new Error("Injected callback failure"); }, /Injected callback failure/);
  } finally { await harness.close(); }
  assert.equal(harness.browser.isConnected(), false);
  await closedPort(harness.url);
  await harness.close(); // Repeated cleanup must be safe.
  console.log("ok callback failure closes browser and preview server");

  const fixtures = fs.mkdtempSync(path.join(os.tmpdir(), "r63-surfaces-"));
  let surfaces;
  try {
    const main = path.join(fixtures, "index.html");
    const extra = path.join(fixtures, "surface.html");
    fs.writeFileSync(main, "<!doctype html><p>Main fixture</p>");
    fs.writeFileSync(extra, "<!doctype html><p>Explicit fixture</p>");
    fs.writeFileSync(path.join(fixtures, "unlisted.txt"), "Never served");
    surfaces = await launchHarness(main, { additionalFiles: { "/classroom/fixture.html": extra } });
    const response = await fetch(surfaces.baseURL + "/classroom/fixture.html");
    assert.equal(response.status, 200);
    assert.match(response.headers.get("content-type"), /text\/html; charset=utf-8/);
    assert.equal(await response.text(), "<!doctype html><p>Explicit fixture</p>");
    assert.equal((await fetch(surfaces.baseURL + "/unlisted.txt")).status, 404);
    assert.equal((await fetch(surfaces.baseURL + "/%2e%2e/unlisted.txt")).status, 404);
    assert.equal((await fetch(surfaces.url, { method: "POST" })).status, 405);
  } finally {
    if (surfaces) await surfaces.close();
    fs.rmSync(fixtures, { recursive: true, force: true });
  }
  await closedPort(surfaces.url);
  console.log("ok multiple surfaces serve only explicit files and reject other paths/methods");

  const signal = startChild(`
    process.on('message', s=>{if(s==='SIGTERM')process.emit(s)});
    ${code}.then(h=>{
      process.on('exit',()=>console.log(h.browser.isConnected()?'BROWSER_CONNECTED':'BROWSER_CLOSED'));
      console.log(h.url);
    }).catch(e=>{console.error(e.message);process.exitCode=1});
  `);
  try {
    const url = await deadline(new Promise((resolve, reject) => {
      const ready = () => {
        const line = signal.output().split("\n").slice(0, -1).find((text) => text.startsWith("http://127.0.0.1:"));
        if (line) resolve(line.trim());
      };
      signal.child.stdout.on("data", ready);
      signal.exited.then((result) => reject(new Error("Signal-check child exited before ready: " + result.stderr)), reject);
    }), "Signal-check startup");
    // Windows forcibly terminates on child.kill('SIGTERM'); IPC exercises the
    // same registered Node handler there. POSIX tests an actual OS signal.
    if (process.platform === "win32") signal.child.send("SIGTERM");
    else signal.child.kill("SIGTERM");
    const result = await deadline(signal.exited, "Signal cleanup");
    assert.equal(result.exitCode, 143);
    assert.equal(result.signal, null);
    assert.match(result.stdout, /BROWSER_CLOSED/);
    await closedPort(url);
  } finally { await stopChild(signal); }
  console.log(`ok SIGTERM ${process.platform === "win32" ? "handler (IPC)" : "signal"} closes preview server`);
  console.log("4 harness checks passed");
})().catch((error) => {
  console.error("Harness check failed: " + error.message);
  process.exitCode = 1;
});
