// Synthetic metadata only. Never contacts GitHub or opens the student artifact.
const assert = require("node:assert/strict");
const { runRelease } = require("./release-check.cjs");
const privateRepo = {
  id: 1397299841, full_name: "josevillar-sketch/search-guide",
  private: true, visibility: "private", forks_count: 0,
};
const publicRepo = { ...privateRepo, private: false, visibility: "public" };
const successful = (value) => ({ status: 0, stdout: JSON.stringify(value) });
let passed = 0;

function scenario(label, response, expected, expectedCalls = 1, applicationResult = { status: 0 }) {
  const calls = [];
  const messages = [];
  const status = runRelease({
    report: (message) => messages.push(message),
    runCommand: (command, args, options) => {
      calls.push({ command, args, options });
      if (calls.length > 1) return applicationResult;
      if (response instanceof Error) throw response;
      return response;
    },
  });
  assert.equal(status, expected, label);
  assert.equal(calls.length, expectedCalls, `${label}: downstream execution`);
  assert.equal(calls[0].command, "gh");
  assert.deepEqual(calls[0].args, [
    "api", "--hostname", "github.com", "repos/josevillar-sketch/search-guide",
    "-H", "Accept: application/vnd.github+json",
  ]);
  assert.equal(calls[0].options.timeout, 15000);
  assert.deepEqual(calls[0].options.stdio, ["ignore", "pipe", "pipe"]);
  assert.equal(messages.join("\n").includes("SENSITIVE_FIXTURE"), false, `${label}: diagnostics leak`);
  if (expectedCalls === 2) {
    assert.equal(calls[1].command, process.execPath);
    assert.match(calls[1].args[0], /[/\\]verify\.cjs$/);
    assert.equal(calls[1].options.stdio, "inherit");
  }
  console.log(`PASS release gate: ${label}`);
  passed++;
}

scenario("approved public repository permits application checks", successful(publicRepo), 0, 2);
scenario("a reported fork requires review", successful({ ...publicRepo, forks_count: 1 }), 2);
scenario("unknown fork count is not a monitoring pass", successful({ ...publicRepo, forks_count: undefined }), 2);
scenario("invalid negative fork count stays blocked", successful({ ...publicRepo, forks_count: -1 }), 2);
scenario("text fork count stays blocked", successful({ ...publicRepo, forks_count: "0" }), 2);
scenario("nonintegral fork count stays blocked", successful({ ...publicRepo, forks_count: 0.5 }), 2);
scenario("wrong repository blocks downstream checks", successful({ ...privateRepo, full_name: "example/other" }), 2);
scenario("recreated repository blocks downstream checks", successful({ ...privateRepo, id: 1 }), 2);
scenario("missing private flag blocks downstream checks", successful({ id: privateRepo.id, full_name: privateRepo.full_name, visibility: "private" }), 2);
scenario("conflicting visibility blocks downstream checks", successful({ ...privateRepo, visibility: "internal" }), 2);
scenario("inconsistent public metadata stays blocked", successful({ ...publicRepo, private: true }), 2);
scenario("malformed metadata stays blocked without raw output", { status: 0, stdout: "SENSITIVE_FIXTURE" }, 2);
scenario("null metadata stays blocked", successful(null), 2);
scenario("403 or 404 is not a privacy pass", { status: 1, stdout: "SENSITIVE_FIXTURE", stderr: "SENSITIVE_FIXTURE HTTP 404" }, 2);
scenario("missing CLI stays blocked", { status: null, error: new Error("SENSITIVE_FIXTURE ENOENT") }, 2);
scenario("timeout stays blocked even with partial private metadata", { ...successful(privateRepo), signal: "SIGTERM", error: new Error("SENSITIVE_FIXTURE timeout") }, 2);
scenario("thrown command error stays blocked", new Error("SENSITIVE_FIXTURE"), 2);
scenario("verified private identity permits application checks", successful(privateRepo), 0, 2);
scenario("application failure propagates", successful(privateRepo), 1, 2, { status: 1 });
scenario("application interruption is a failure", successful(privateRepo), 1, 2, { status: null, signal: "SIGTERM" });
console.log(`PASS ${passed} synthetic release-gate checks; no network or student artifacts used.`);
