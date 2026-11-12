// Synthetic POSIX control-flow checks for the actual upstream verification wrapper.
// Every external command is stubbed; no application data, builds, or network are used.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { spawnSync } = require("node:child_process");

if (process.platform === "win32") {
  console.log("SKIP upstream wrapper checks: POSIX /bin/sh is required.");
  process.exit(0);
}

const wrapper = fs.readFileSync(path.join(__dirname, "check_all.sh"), "utf8");
const expected = [
  "python3:tools/check_privacy.py",
  "python3:tools/check.py",
  "python3:classroom/build.py",
  "node:classroom/build-pdf.cjs",
  "sh:consent",
  "python3:tools/check_links.py",
  "node:tools/smoke.cjs",
  "node:tools/workbench.cjs",
  "node:tools/design_check.cjs",
];

function runCase(privacyExit, failCommand = "") {
  const temporary = fs.mkdtempSync(path.join(os.tmpdir(), "r63-upstream-gate-"));
  try {
    const bin = path.join(temporary, "bin");
    const trace = path.join(temporary, "commands.log");
    fs.mkdirSync(bin);
    fs.mkdirSync(path.join(temporary, "tools"));
    fs.mkdirSync(path.join(temporary, "classroom"));
    const copy = path.join(temporary, "tools", "check_all.sh");
    fs.writeFileSync(copy, wrapper);
    function stub(name, contents) {
      fs.writeFileSync(path.join(bin, name), "#!/bin/sh\n" + contents, { mode: 0o755 });
    }
    stub("npm", 'printf "%s\\n" "$TEST_MODULES"\n');
    for (const name of ["python3", "node"]) {
      stub(name, `command_id='${name}:'"$1"
printf '%s\\n' "$command_id" >> "$TEST_TRACE"
if [ "$command_id" = 'python3:tools/check_privacy.py' ]; then
  exit "$TEST_PRIVACY_EXIT"
fi
if [ "$command_id" = "$TEST_FAIL_COMMAND" ]; then exit 1; fi
exit 0
`);
    }
    // The nested consent shell is a stub too, so its script can never run.
    stub("sh", `printf '%s\\n' 'sh:consent' >> "$TEST_TRACE"
if [ "$TEST_FAIL_COMMAND" = 'sh:consent' ]; then exit 1; fi
exit 0
`);
    const result = spawnSync("/bin/sh", [copy], {
      cwd: temporary,
      env: {
        ...process.env,
        PATH: bin,
        TEST_MODULES: path.join(temporary, "modules"),
        TEST_TRACE: trace,
        TEST_PRIVACY_EXIT: String(privacyExit),
        TEST_FAIL_COMMAND: failCommand,
      },
      encoding: "utf8",
      timeout: 15000,
      maxBuffer: 256 * 1024,
      stdio: ["ignore", "pipe", "pipe"],
    });
    assert.ifError(result.error);
    assert.equal(result.signal, null, "wrapper must finish without a signal");
    const commands = fs.existsSync(trace)
      ? fs.readFileSync(trace, "utf8").trim().split("\n").filter(Boolean)
      : [];
    return { status: result.status, commands };
  } finally {
    fs.rmSync(temporary, { recursive: true, force: true });
  }
}

let passed = 0;
let failed = 0;
function check(name, test) {
  try {
    test();
    passed++;
    console.log(`ok ${name}`);
  } catch (error) {
    failed++;
    console.error(`FAIL ${name}: ${String(error.message).split("\n")[0]}`);
  }
}

for (const code of [1, 2]) {
  check(`privacy exit ${code} stops all downstream checks`, () => {
    const result = runCase(code);
    assert.notEqual(result.status, 0, "failed privacy must fail the wrapper");
    assert.deepEqual(result.commands, [expected[0]], "no downstream command may start");
  });
}
check("privacy pass allows every downstream check", () => {
  const result = runCase(0);
  assert.equal(result.status, 0, "all passing checks must pass the wrapper");
  assert.deepEqual(result.commands, expected, "every configured check must run in order");
});
check("downstream failure aggregates and reaches the final check", () => {
  const result = runCase(0, "python3:tools/check.py");
  assert.notEqual(result.status, 0, "downstream failure must fail the wrapper");
  assert.deepEqual(result.commands, expected, "later checks must still run after a downstream failure");
});

console.log(`${passed} upstream wrapper checks passed, ${failed} failed`);
process.exitCode = failed ? 1 : 0;
