# Room 63 Search Guide

A personalized search slip for every AP Capstone student in Room 63: the student's question on record, the chair their source table still needs, the field's words for their words, three searches built for free databases, a tip drawn from their own search history, and the six-line log entry.

Single-file HTML, vanilla JS, no build step. Published as a claude.ai artifact; `index.html` here is the page source.

## What a student does

1. Tap their period, then their name (or open `index.html#<student-id>`).
2. Run the three searches, find one source, and tap **Copy log lines** to paste a pre-dated entry into their log. Line 3 fills in with the last search they tapped.
3. Question changed in their log? They tap **My question changed** on the desk (below), and the slip, the builder and the checks all switch to the newest version. The builder keeps "quoted phrases" together and picks databases from the words in the question (health words send it to PubMed, school words to ERIC, law words to the Legal Information Institute, and so on). Typing in the builder never saves a version.

The page remembers the last desk opened on that device (`localStorage` key `r63sg_last`) and offers it back with a **Not you?** escape for shared iPads.

## The Question Workbench

After a pick, the pickers fold away and the student's desk opens:

- **The ficha:** their newest question on a paper card: the question on record from September 29, or the newest version saved on this iPad.
- **My question changed:** an inline form. The box starts with the student's own last version, and they type the new version word for word from their log, plus one sentence on what they changed and why, the version number and the date. Saving shows the version line to copy into the log in pen, and **I wrote it in my log** stamps it. Until then, **Fix a typo** and **Remove this version** stay available.
- **All your versions** and **Compare two versions:** every saved version stays in the history, and a word diff shows what changed between any two.
- **Seven checks:** the course's Plate VI checks. The student taps a dot when a check passes; each check has its Plate VII repair behind **If it fails**. **Circle it** labels the who, where and when (plus the judgment word for Seminar, or the verb and the variable for Research), and **What the page notices** points out patterns such as a yes-or-no opening.
- **This iPad:** copy every version as text, download a private copy of the saved data, or remove them. A downloaded JSON file preserves the current desk's saved record and recovery text; it excludes unsaved fields. Keep the file private. There is no in-app import or Undo; your Research Log remains the record.

**The rule.** College Board and Room 63 both say no tool writes, rewrites or narrows a student's question. Every question string on the page comes from the `DATA` record or from text the student typed. The workbench never suggests wording, fills a dot, or types into the student's fields; notes and repairs are the Field Guide's generic moves. The rule is written as a comment at the top of the workbench code.

**Privacy.** New versions live only in this browser's `localStorage`, one key per student: `r63sg_wb_<id>` (schema 1). The app does not upload those versions or give Mr. Portela remote access to them. The original roster and questions are embedded in the HTML; access to those depends on where the file is distributed. Anyone who taps the student's name on the same iPad can see saved versions, which the page tells students. The desk never lists other students, the question never goes in the URL, and **Done on this iPad** / **Not you?** clear the desk and the builder. Delayed copy callbacks cannot reopen a previous desk's export. A record from a newer schema shows read-only and is never overwritten. When storage is off or full, everything keeps working for the session and the page says so.

**Recovery.** Unreadable or partially damaged records are preserved under `r63sg_bad_<id>_<time-and-random-digits>` before sanitized data can replace them. **Show recovery data** under **This iPad** selects the original data for copying; **Copy all my versions** includes it. If that backup cannot be saved, editing is disabled and the original remains intact. Recovery text can still be copied during the session. Successful device removal clears that student's main record and recovery copies; a failed removal reports failure and leaves the displayed work available. The export is text for recovery, not an import feature.

**Other tabs.** Pending answers remain attached to the version on which they were typed when another tab updates the desk. Conflicting answers are kept in recovery data. A stale write is refused rather than overwriting another tab's saved record. Copy unsaved work before reloading after a conflict. This is same-browser coordination; the student's log remains the record across devices.

**Keyboard.** The skip link goes to the period picker, or after a pick to the question. The rail (Versions, Checks, Searches) moves focus to each section's heading. The Circle it words take the arrow keys, Home and End. The rail stops sticking while a field has focus, so the iPad keyboard never covers it.

**Storage keys**

| Key | Holds |
|---|---|
| `r63sg_last` | the last student id opened on this device |
| `r63sg_probe` | written and removed once at startup to test storage |
| `r63sg_wb_<id>` | that student's record: the record question, their versions, dots, circles, answers, and an unsaved draft |
| `r63sg_bad_<id>_<time-and-random-digits>` | original unreadable data or conflicting typed answers for recovery |

## Printing

- Ctrl+P / Share, Print prints the open slip on one page, with each database's address in place of the buttons. It shows the student's newest version.
- After picking a period, the footer button prints every slip in that period, one per page, from the record. The button appears only when the file is opened locally: printing does nothing inside the claude.ai viewer, so the hosted page never shows it.

## Reproducible local verification

```sh
npm ci
npm test
npm run test:mobile:chromium
npm run test:design
```

Playwright is locked as a development dependency. Chromium selection uses an explicit executable override, the bundled browser, or installed Chromium/Chrome; see [tools/VERIFY.md](tools/VERIFY.md). The application remains standalone HTML with no runtime dependencies. Local tests cover cleanup, storage/recovery, all 31 workbench acceptance cases, private-copy download checks, 244 slips, and eight period print sets. Generated browser artifacts stay under ignored `test-results/` and must remain local.

These application checks supplement the existing whole-repository checks below. They do not replace classroom builds, link checks, consent pagination, or the required DESIGN.md audit. Run mutating builds in a disposable copy and never stage regenerated files as a side effect of checking this change.

The Chromium design and PDF gates inspect the font families actually used for representative text glyphs. Required fonts may come from the web or local installation. The fallback context removes the primary families explicitly, so locally installed fonts cannot make a blocked-web-font test silently exercise the normal faces. The existing `npm test` runner includes these font regressions; `npm run test:font-gate` runs them separately. They cover absent-face false positives, missing/empty proof elements and forced fallback behavior. This checks representative family use, not every glyph, weight or typography role.

`npm run verify:release` verifies the exact repository metadata against the approved existing public-repository policy before app checks. It never publishes. Unknown metadata is unverified; a reported fork requires review. No further kinds of student data are authorized. `npm run test:release-gate` tests that control flow with synthetic metadata only.

`npm run test:webkit` requests WebKit explicitly and reports a missing runtime as blocked; Chromium emulation does not establish native iPad Safari or VoiceOver behavior. `npm run compact:artifact` optionally compacts CSS and JavaScript formatting to retain the 360,000-byte cap without changing DATA, reference content, identifiers, or the RULE comment. JavaScript compression and name mangling are disabled. The delivered HTML requires no build step.

[QUALITY.md](QUALITY.md) records the exact source, observed checks, limits, and recovery path. [AGENTS.md](AGENTS.md) describes the ongoing inspect, repair, verify, and deliver workflow.

## Checks

```sh
python3 tools/check.py                          # data: ids, searches, databases, quotes, course by period
NODE_PATH="$(npm root -g)" node tools/smoke.cjs # headless Chromium: all slips, log copy, welcome back, builder, print page counts, phone width in both themes
NODE_PATH="$(npm root -g)" node tools/workbench.cjs # headless Chromium: the workbench acceptance tests
sh tools/check_all.sh                           # every check below plus privacy, builds, page counts and links, in order
NODE_PATH="$(npm root -g)" node tools/design_check.cjs # the DESIGN.md floor on every page and handout: contrast, measure, tap targets, type limits, no eyebrow, no side stripe
```

## Updating student data

Student records live in the `DATA` array in `index.html` (one line). Fields: `id`, `n` name, `p` period, `c` course (`R` Research, `S` Seminar), `q` question, `qf` where it came from, `tp` topic, `f` field, `ch` the chair to fill, `sw` word swaps, `s` three searches `{db, q}`, `tip`, `es` show the Spanish-search note, `nt` no topic yet. Database keys are defined in `DB`.

## Also in this repository

- `RESOURCES.md`: the verified research resources log. Students are sent only to what is listed there.
- `BOOKS.md`: the methods book request list, with confirmed editions and ISBNs.
- `classroom/`: AP Research handouts, the consent templates, and the student Research Library page. `classroom/README.md` says what to use when.
- `DESIGN.md`: the design standard for everything students see.
- `CLAUDE.md`: context and rules for any Claude session working here.

This repository holds the student roster inside `index.html`, and it is public by Mr. Portela's decision of 2026-11-12. `python3 tools/check_privacy.py` reports the current state. Add no other student data here.
