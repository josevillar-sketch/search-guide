// One command runs all existing checks and records reproducible, local results.
const fs = require("node:fs");
const path = require("node:path");
const { spawn } = require("node:child_process");
const { createHash } = require("node:crypto");

const root = path.resolve(__dirname, "..");
const output = path.join(root, "test-results");
const startedAt = new Date().toISOString();
const sourceHash = () => createHash("sha256").update(fs.readFileSync(path.join(root, "index.html"))).digest("hex");
const timeout = Number(process.env.VERIFY_TIMEOUT_MS || 600000);
if (!Number.isFinite(timeout) || timeout <= 0) {
  console.error("VERIFY_TIMEOUT_MS must be a positive number of milliseconds.");
  process.exit(1);
}
fs.mkdirSync(output, { recursive: true });
let child;
let interrupted;
for (const [signal, code] of [["SIGINT", 130], ["SIGTERM", 143]]) {
  process.on(signal, () => {
    interrupted = code;
    if (child) child.kill("SIGTERM");
  });
}

async function step(name, command, args) {
  const start = Date.now();
  const log = fs.createWriteStream(path.join(output, `${name}.log`));
  let timedOut = false;
  let force;
  const result = await new Promise((resolve) => {
    child = spawn(command, args, {
      cwd: root,
      env: { ...process.env, SMOKE_OUT: path.join(output, "smoke") },
      stdio: ["ignore", "pipe", "pipe"],
    });
    const timer = setTimeout(() => {
      timedOut = true;
      child.kill("SIGTERM");
      force = setTimeout(() => child?.kill("SIGKILL"), 10000);
    }, timeout);
    for (const stream of [child.stdout, child.stderr]) stream.on("data", (data) => {
      log.write(data);
      process.stdout.write(data);
    });
    child.once("error", (error) => {
      const message = `Cannot start ${name}: ${error.message}\n`;
      log.write(message);
      process.stderr.write(message);
    });
    child.once("close", (code, signal) => {
      clearTimeout(timer);
      clearTimeout(force);
      child = null;
      log.end(() => resolve({
        name, status: code === 0 && !timedOut ? "passed" : "failed",
        exit_code: code, signal, timed_out: timedOut, elapsed_ms: Date.now() - start,
      }));
    });
  });
  console.log(`${result.status === "passed" ? "PASS" : "FAIL"} ${name} (${result.elapsed_ms} ms)`);
  return result;
}

(async () => {
  const sourceSHA = sourceHash();
  const steps = [
    ["release-gate", process.execPath, [path.join(__dirname, "release-check.test.cjs")]],
    ["consent-gate", process.execPath, [path.join(__dirname, "consent-gate.test.cjs")]],
    ["font-gate", process.execPath, [path.join(__dirname, "font-gate.test.cjs")]],
    ["data", process.env.PYTHON || "python3", [path.join(__dirname, "check.py")]],
    ["harness", process.execPath, [path.join(__dirname, "harness-check.cjs")]],
    ["regressions", process.execPath, [path.join(__dirname, "regressions.cjs")]],
    ["workbench", process.execPath, [path.join(__dirname, "workbench.cjs")]],
    ["download", process.execPath, [path.join(__dirname, "download.test.cjs")]],
    ["smoke", process.execPath, [path.join(__dirname, "smoke.cjs")]],
  ];
  const results = [];
  for (const args of steps) {
    if (interrupted) break;
    results.push(await step(...args));
  }
  const sourceUnchanged = sourceHash() === sourceSHA;
  const passed = !interrupted && sourceUnchanged && results.length === steps.length && results.every((r) => r.status === "passed");
  // Status metadata only: no student names, questions, or browser storage enters the summary.
  fs.writeFileSync(path.join(output, "summary.json"), JSON.stringify({
    passed, started_at: startedAt, source_sha256: sourceSHA, source_unchanged: sourceUnchanged,
    versions: { node: process.version, playwright: require("playwright/package.json").version },
    interrupted: interrupted || null, results,
  }, null, 2) + "\n");
  if (!sourceUnchanged) console.error("index.html changed during verification; rerun against the final source.");
  console.log(`${passed ? "PASS" : "FAIL"} verification. Logs and status: test-results/`);
  process.exitCode = interrupted || (passed ? 0 : 1);
})().catch((error) => {
  console.error("Verification runner failed: " + error.message);
  process.exitCode = 1;
});
