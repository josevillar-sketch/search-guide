# Local verification

Requirements: Node.js 18+, Python 3 (`PYTHON` can select its executable), and Chromium.

These are local application checks, not publication approval. Keep their artifacts
local. The approved distribution policy in [AGENTS.md](../AGENTS.md) applies
separately: the existing public repository is authorized, with no further kinds
of student data. Verify the destination and current metadata before release work.
Current policy and verification evidence are in [QUALITY.md](../QUALITY.md).

```sh
npm ci
npx playwright install chromium
npm test
```

Playwright is pinned in `package-lock.json`. Browser selection prefers
`PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH` when supplied, then the pinned Playwright
browser, then Chromium/Chrome on `PATH` (or the standard Chrome application on
macOS). An explicit override must exist and be executable; it never silently
falls back. A system browser can differ from Playwright's bundled revision, so
use the bundled revision for a consistent cross-machine result when available.

Each browser suite starts its own ephemeral HTTP server bound to `127.0.0.1`.
By default it serves only the selected page; the design and handout-PDF checks
add an explicit allowlist of their HTML surfaces. It sends UTF-8 and closes with the browser on
success, failure, `SIGINT`, or `SIGTERM`. No persistent server, fixed port,
global package, absolute user path, or temporary adapter is required. The
hosted-page test still uses its separate `claude.ai` route.

`npm test` runs synthetic release-guard tests, the data check, harness recovery checks, focused regression checks,
all 31 workbench cases, and the smoke suite
(every slip, clipboard, search builder, welcome back, eight period PDFs, and
phone screenshots in both themes). It continues through independent failures
and returns a nonzero status if any check fails. Each step has a ten-minute
deadline; `VERIFY_TIMEOUT_MS` changes it. Interrupting stops subsequent steps.

Ignored `test-results/` contains per-suite logs, smoke PDFs/screenshots, and
`summary.json` with statuses, exit codes, signals, timings, source SHA-256,
start time, and runtime versions only. The run fails if `index.html` changes
while checks are running, so a passing summary identifies the tested source. PDFs,
screenshots, and failure logs may contain real student content. Keep these
local; do not commit or publish them. The summary contains no student content.

Direct and focused commands remain available:

```sh
python3 tools/check.py
node tools/release-check.test.cjs
node tools/harness-check.cjs
node tools/regressions.cjs
node tools/workbench.cjs
node tools/workbench.cjs 25 27 28
node tools/smoke.cjs
```

`WB_INDEX` selects another HTML copy for the workbench suite. `SMOKE_OUT` selects
the smoke artifact directory for direct runs; `npm test` always keeps artifacts
under `test-results/smoke/`. Browser suites block Google Fonts and verify the
fallback fonts. Inspect the rendered design separately with its authored fonts.

`npm run test:harness` checks an invalid browser override, browser/server cleanup
after an injected callback failure, and `SIGTERM` cleanup with exit 143 and a
closed preview port. POSIX uses an actual OS signal; Windows uses IPC to invoke
the same Node handler because its process termination semantics differ. The additional synthetic surface check verifies allowed HTML, rejects
unlisted/traversal paths and POST, and confirms server cleanup. These
checks do not navigate the student page or copy student content into their
output. They do not recursively invoke the verification runner. A separate
one-off short-deadline check can verify runner timeout metadata before the final
full run; it is not part of the maintained harness suite.

## Repository gate before release work

```sh
npm run verify:release
```

This command makes one read-only GitHub CLI request to the fixed `github.com`
repository endpoint. It requires successful JSON with the exact repository name
and ID, consistent public/private visibility, and an explicit zero fork count
before invoking the existing local verification runner. The existing public
repository is approved. A missing CLI, denied request, timeout, malformed or
mismatched response, unknown fork count, reported fork, or HTTP 404 returns a nonzero blocked
result before downstream checks run. Raw CLI output and credentials are not
printed. The CLI must already be configured with access to the repository.

The command never changes settings or publishes. A pass verifies the repository's
current metadata under the resolved policy; it does not authorize adding further
student data or releasing unrelated publication holds. Destinations still require
review before external delivery. `npm test` stays available for offline repairs. Its
`release-gate` suite uses synthetic metadata only, so its pass is not a live
visibility result. `npm run test:release-gate` runs those 20 tests directly.

## Supplemental WebKit and mobile checks

```sh
npx playwright install webkit
npm run test:webkit
```

This targeted suite checks touch-sized layouts, station navigation, form focus,
local saves/reloads, version comparison, checks and circles, clipboard rejection,
shared-device isolation, and recovery. It requests WebKit explicitly and never
substitutes Chromium. Missing WebKit is a blocked result with a nonzero exit, not
a skipped pass. Its status-only result is `test-results/mobile-webkit.json`.

`npm run test:mobile:chromium` exercises the same supplemental scenarios with
installed Chromium and writes `test-results/mobile-chromium.json`. This validates
the test paths; it does not establish WebKit behavior. These commands are
separate from `npm test`, whose Chromium PDF and clipboard-permission checks
cannot be relabeled as equivalent WebKit coverage.

The Linux WebKit runtime with touch/device emulation is not native iPad Safari.
It does not simulate the on-screen keyboard or run VoiceOver, and it cannot
generate the Chromium-only PDF artifacts. A native-device review remains a
separate requirement for any claim about those behaviors.

If the environment uses a domain allowlist, the pinned WebKit download currently
starts at `cdn.playwright.dev`; Playwright also lists
`playwright.download.prss.microsoft.com` as a download fallback. Enable the
necessary official download domains in environment settings before installation.
Keep the supplied proxy and TLS verification settings.

## Existing whole-repository checks and compaction

`npm run test:design` runs the existing DESIGN.md checker across all 14 surfaces.
The design and handout-PDF tools share browser selection, explicit local HTML
allowlists, ephemeral loopback transport, and guaranteed server/browser cleanup.
Neither serves the repository directory or uses file URLs. Authored-font checks
still require the official fonts to load; a blocked network is not a font pass.

`sh tools/check_all.sh` retains privacy reporting, data, classroom HTML/PDF and
consent builds, links, browser acceptance, and design checks. Run it in a disposable
copy because builds rewrite generated files. A failed privacy preflight now stops
downstream builds. `npm run test:upstream-gate` verifies this with four isolated
POSIX command-stub cases; Windows reports an explicit POSIX-only skip. The
application suite does not replace these whole-repository checks.

`npm run compact:artifact` is optional maintenance for the size cap. It preserves
DATA and the database/reference prefix, retains the RULE comment, disables
JavaScript compression/name mangling, and compacts CSS. It is not required to open
the standalone artifact. Check the source diff, data, behavior, and affected
rendered states after running it. The integrated compaction was independently
compared across 12 font-loaded screenshot pairs with identical pixels and geometry.
