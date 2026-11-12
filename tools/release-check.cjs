// Read-only repository gate. This command never publishes or changes settings.
const { spawnSync } = require("node:child_process");
const path = require("node:path");

const repository = "josevillar-sketch/search-guide";
const repositoryID = 1397299841;

// The existing public roster is approved. See QUALITY.md's policy resolution.
// A reported fork is a new condition; unknown metadata is not verification.
function validateMetadata(value) {
  if (!value || typeof value !== "object" || Array.isArray(value)) return "invalid metadata";
  if (value.full_name !== repository || value.id !== repositoryID) return "repository identity mismatch";
  if (!((value.private === true && value.visibility === "private") ||
        (value.private === false && value.visibility === "public"))) return "visibility not verified";
  if (!Number.isSafeInteger(value.forks_count) || value.forks_count < 0) return "fork count not verified";
  if (value.forks_count > 0) return "a new fork requires review under the approved policy";
  return null;
}

function runRelease({ runCommand = spawnSync, report = console.log } = {}) {
  let response;
  try {
    response = runCommand("gh", [
      "api", "--hostname", "github.com", `repos/${repository}`,
      "-H", "Accept: application/vnd.github+json",
    ], {
      encoding: "utf8", timeout: 15000, maxBuffer: 512 * 1024,
      stdio: ["ignore", "pipe", "pipe"],
    });
  } catch {
    report(`BLOCKED release: ${repository}; metadata request unavailable.`);
    return 2;
  }

  // Never print raw stdout/stderr: credential failures and remote text are untrusted.
  if (!response || response.error || response.signal || response.status !== 0) {
    report(`BLOCKED release: ${repository}; metadata request failed or timed out.`);
    return 2;
  }
  let metadata;
  try { metadata = JSON.parse(response.stdout); } catch {
    report(`BLOCKED release: ${repository}; invalid metadata.`);
    return 2;
  }
  const reason = validateMetadata(metadata);
  if (reason) {
    report(`BLOCKED release: ${repository}; ${reason}.`);
    return 2;
  }

  report(`PASS repository gate: ${repository}; approved access policy verified (${metadata.visibility}, no forks reported). Running local application checks; no publication is performed.`);
  let checks;
  try {
    checks = runCommand(process.execPath, [path.join(__dirname, "verify.cjs")], {
      cwd: path.resolve(__dirname, ".."), stdio: "inherit",
    });
  } catch {
    report("FAIL release checks: application runner unavailable.");
    return 1;
  }
  if (!checks || checks.error || checks.signal || !Number.isInteger(checks.status)) {
    report("FAIL release checks: application runner did not complete.");
    return 1;
  }
  return checks.status;
}

module.exports = { runRelease, validateMetadata };
if (require.main === module) process.exitCode = runRelease();
