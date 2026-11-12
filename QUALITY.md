# Search Guide delivery and verification record

## Current source and scope

This change integrates the verified recovery/navigation work with the newer remote design, without replacing independent classroom, resource, book, or design-system changes. Baseline: `847dec07cbbcefcee5569e18091cd3b29eaa9fa8`, default branch `claude/dazzling-hopper-eexjgx`. Integration branch: `codex/search-guide-recovery`.

Current `index.html`: 359,421 bytes; SHA-256 `9e9d81c38f93fd6ffd10d0676994f251df241f397604c841b1af563b00f6cf65`. Student DATA is byte-identical to the baseline, SHA-256 `13650200ffbdcf49b705d6776afbd6ffcd22e3c50d1768c3e98199167d1e3011`. No student question was written, rewritten, narrowed, completed, or suggested. The standalone page requires no application build or runtime dependency.

The user confirmed the existing public-repository policy as resolved and authorized. Keep that decision: the exception covers the existing roster and questions only. Add no further kinds of student data, grades, records, Drive files, browser storage, screenshots, or student print exports. Reconsider only if GitHub reports a fork, a new kind of student data is proposed, or the user asks. The former private-only gate is superseded; do not request the same permission again.

## Implemented changes

- Session-bound clipboard callbacks cannot reopen another student's export or an export after successful deletion. Failed deletion reports failure and preserves visible work.
- Revision guards prevent stale cross-tab overwrites. Pending answers remain attached to their original version; conflicting/orphaned answers and open edits remain recoverable.
- Malformed or partially damaged records retain raw recovery data. Recovery export remains available; editing is read-only when a required backup cannot be saved. Newer schemas remain untouched.
- Standards-mode HTML, UTF-8, language and viewport metadata; accurate rail state, restored keyword-button focus, count-only filter announcements, and a visible focused form field.
- The rail precedes the long context panel on phones. Explicit grid placement preserves desktop columns; the desktop sidebar clears the sticky rail. The newer upstream typography, paper/night surfaces, pressed shadows, boxed numerals, measured widths and compact history behavior remain.
- Pinned development tools, ephemeral loopback browser harnesses, explicit surface allowlists, cleanup checks, synthetic regressions, source-hashed results, and separate Chromium/WebKit commands. Design and PDF tools share the portable browser/transport setup.
- Repository preflight accepts the approved public repository, verifies exact identity and consistent metadata, and notices a reported fork. Unknown metadata is unverified, not a monitoring pass. A failed existing wrapper preflight now stops downstream builds.

## Acceptance and observed checks

| Outcome | Evidence | Result |
|---|---|---|
| Preserve DATA and student authorship | Exact DATA hash; workbench wording/source invariants | Pass |
| Recovery, shared-device and cross-tab behavior | 17 synthetic application regressions; 31 workbench cases; every student slip | Pass |
| Browser/server lifecycle and limited file serving | Four harness checks, including signal cleanup, explicit HTML allowlist, rejected unlisted/traversal paths and POST | Pass |
| Approved public policy without false metadata passes | 20 synthetic repository-gate cases | Pass |
| Stop downstream builds after failed preflight | Four isolated POSIX wrapper cases; no real builds/network/student content | Pass |
| Responsive navigation and focused forms | Six final actual-font contexts at 320, 820 and 1440 pixels, both themes; identity clears the desktop rail | Pass |
| Existing DESIGN.md requirements | All 14 surfaces, zero findings; full sweep includes 88 contexts | Pass with official font-cache setup recorded below |
| Print output | 244 slips/eight period PDFs in application smoke; seven handout PDFs, required page counts and fonts; consent nine-page pagination | Pass |
| Supplemental mobile Chromium journeys | Eight touch-layout, storage, focus, clipboard and recovery scenarios | Pass on exact final source |
| Supplemental WebKit journeys | Explicit engine selection; no silent Chromium substitution | Blocked: runtime unavailable |
| Automated external links | Existing checker attempted all 23 automated links, each returned connection code `000` | Environment-blocked; not evidence of dead links |

The final integrated application run started `2026-11-12T06:45:26.313Z`, after the shared transport changes: all six suites passed, with this exact source hash, `source_unchanged: true`, no timeout and no interruption. Node was `v24.22.1`, Playwright `1.56.1`, with installed Chromium. The exact-source eight-case mobile Chromium rerun started `2026-11-12T06:48:23.076Z` and passed. Evidence: ignored `test-results/summary.json` and `mobile-chromium.json`. Logs and generated student artifacts remain ignored and local.

Independent compaction review compared 12 official-font screenshot pairs across phone/desktop, both themes and home/desk/form: pixels and geometry were identical. Equivalent gradient stop serialization was the only computed-style spelling difference. JavaScript compression and name mangling were disabled; normalized syntax trees matched (source positions/raw spelling and equivalent noncomputed object-key spelling normalized). DATA and database/reference content were unchanged. This comparison identifies the compaction-stage source; the later intentional rail/sidebar CSS corrections are covered separately by final-layout checks. Evidence: `test-results/compaction.json` and `compaction-review/report.json`.

Final layout evidence: `test-results/compaction-review/fixed-grid-report.json` and `final-review-summary.json`. The integrated grid initially reproduced overflow/reversed columns and an obscured desktop identity; both causes were fixed and the failing layouts rerun. The final sidebar identity begins below the rail, and its exit remains visible.

The default browser denied `file://` navigation. Design/PDF tools now use their permanent explicit-allowlist loopback harness. Their final rerun required only cached original font CSS/bytes, with the checker's intentional fallback-font routes still effective; no URL substitution or check override. Seven handout PDFs and all 14 design surfaces passed. Exact setup and safe results: `test-results/upstream-check/transport-rerun/`. The initial default failure and prior independent full sweep are retained separately in `compaction-review/`.

The disposable full-repository run passed data, classroom HTML generation, consent pagination, smoke, and all 31 workbench cases. It did not produce `ALL CHECKS PASS`: links were network-blocked, and anonymous repository metadata was unverified. Subsequent affected PDF/design reruns passed with the permanent transport. Do not relabel the full wrapper as passed. No regenerated classroom artifact was retained in this branch.

## Limits, delivery and recovery

The user's subsequent "Finish" instruction completed repository delivery. [PR #16](https://github.com/josevillar-sketch/search-guide/pull/16) was marked ready and merged as `7917d7a3f5b6112bfc347cbc9ec29d95ea59cd29` into `claude/dazzling-hopper-eexjgx`, with expected-head protection for reviewed head `c8c999e6cab03b584444be451c156aa324033d11`. There were no review threads, submitted reviews, CI statuses or PR workflow runs to resolve. Independent final audit found no consequential code blocker. A fresh fetch confirmed the merged tree exactly matches the reviewed head and the HTML hash above. No generated student artifacts were added.

A new dated HTML backup was saved, without overwriting earlier files, in the existing private Search Guide Research Library backup folder. Drive metadata confirmed the expected parent, 359,421-byte size and user-only permissions. The merge receipt and exact-source publishing handoff were saved to the existing private coordination line and read back successfully.

Live publication is a separate, unverified state: this session has no Claude artifact publishing action, and browser-control initialization failed before an account or page opened. It did not republish either private artifact. The existing Search Guide publisher has a recorded handoff to compare live content, skip a duplicate if already current, or update the existing address while preserving sharing, then return an observed version/time and body hash. This records the handoff; it does not promise unattended execution or claim acceptance. Last reported live Search Guide version was 4 from earlier source `53b3bb8`. Documentation-only delivery receipts do not change the tested HTML hash.

- The application scope is verified in installed Chromium, with authored-font and fallback-font checks. Automated scans do not establish full accessibility conformance, native iPad Safari, on-screen keyboard behavior, or VoiceOver usability.
- Playwright WebKit is absent. The managed network previously denied its official download hosts. Authorization is present; no runtime installation or network-policy change is claimed.
- External links and live CLI repository metadata require a working network/authentication route before their checks can be called verified. These technical limits do not reopen the resolved public-access decision.
- Repository implementation is merged. The live artifact update remains unverified through the existing publisher; this session distributed nothing to students/families. Publication ownership and unrelated holds remain intact.

Reproduce with `npm ci`, `npm test`, `npm run test:mobile:chromium`, `npm run test:upstream-gate`, and `npm run test:design`. Run mutating `sh tools/check_all.sh` in a disposable copy; keep failed/unverified external checks explicit. See `tools/VERIFY.md` for engine selection and optional formatting maintenance. `npm audit --json` reported zero vulnerabilities for the pinned development dependencies on November 12, 2026.

Preserve the original local work at `/workspace/search-guide`. Do not reset it or force-push shared history. Before delivery, verify the remote base has not changed; reconcile in isolation if it has. If rollback is needed, compare against the baseline above in a separate copy. On later edits, reopen the affected acceptance row, reproduce the defect, fix its cause, rerun affected checks, and update this record against the final hash. Stop when applicable outcomes pass and genuine external limitations are documented.

## Consent builder followup: November 12, 2026

Baseline: `c408ab0d8228738a2ebf54915a04ff6b503d4c78`. This is a consent-only source change. The application, student DATA, consent Markdown, current release policy and browser architecture are unchanged.

The builder now requires its conversion dependencies and a supported `soffice` or `libreoffice` renderer. Sequential commands stop after a failed pandoc or Python step. Fresh temporary outputs prevent an old DOCX/PDF or an optional-render skip from producing a pass. Both the DejaVu stress copy and the actual runtime distribution render must have nine pages.

The Spanish guardian form uses 2pt paragraph-after spacing instead of 4pt. Its 10pt text, line spacing, choice boxes, signature heights and wording are preserved. This keeps the form together under the observed Noto Sans/Noto Serif runtime substitutions.

`npm run test:consent-gate` passed eight POSIX actual-shell control-flow cases, including failed pandoc with a stale DOCX, failed Python/rendering, missing renderer/fresh output, and either pagination gate failing. The existing verification runner includes these synthetic cases. A separate fresh build produced two nine-page PDFs. Independent review matched all 18 raster frames to the individually reviewed repaired stress/distribution pages. This is runtime-render evidence; Microsoft Word output is not established. Verification for this edit is scoped to consent, with application bytes unchanged. Generated documents, PDFs and logs remain local and untracked. The POSIX-only suite reports Windows as blocked with exit 2; no Windows pass is implied.

Exact source SHA-256 values before this documentation-only receipt:

- `classroom/build-consent.sh`: `dbfcae08d7572e62706b87953bee1ea8b7311a6970aef6cc261ade02148c862b`
- `tools/consent-gate.test.cjs`: `a825351a229c9efac3af21ef7bed281a4cad3a86c0afdd6cf8e05bd46cb0bafe`
- `package.json`: `7896d30c0293014e94e417babcc1437fe33919504827c381d84c6d671cdf1f97`
- `tools/verify.cjs`: `d74d0b14d93ec0a5e9776adda323797ace9f6a3efecec903748dac95f4e5ce8a`
