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
- **This iPad:** copy every version as text, or remove them.

**The rule.** College Board and Room 63 both say no tool writes, rewrites or narrows a student's question. Every question string on the page comes from the `DATA` record or from text the student typed. The workbench never suggests wording, fills a dot, or types into the student's fields; notes and repairs are the Field Guide's generic moves. The rule is written as a comment at the top of the workbench code.

**Privacy.** Versions live only in this browser's `localStorage`, one key per student: `r63sg_wb_<id>` (schema 1). Nothing goes online and Mr. Portela cannot see it. Anyone who taps the student's name on the same iPad can see it, which the page tells students. The desk never lists other students, the question never goes in the URL, and **Done on this iPad** / **Not you?** clear the desk and the builder. An unreadable record is copied to `r63sg_bad_<id>_<time>` before anything is written; a record from a newer schema shows read-only and is never overwritten. When storage is off or full, everything keeps working for the session and the page says so.

**Keyboard.** The skip link goes to the period picker, or after a pick to the question. The rail (Versions, Checks, Searches) moves focus to each section's heading. The Circle it words take the arrow keys, Home and End. The rail stops sticking while a field has focus, so the iPad keyboard never covers it.

**Storage keys**

| Key | Holds |
|---|---|
| `r63sg_last` | the last student id opened on this device |
| `r63sg_probe` | written and removed once at startup to test storage |
| `r63sg_wb_<id>` | that student's record: the record question, their versions, dots, circles, answers, and an unsaved draft |
| `r63sg_bad_<id>_<epoch>` | a best-effort copy of a record that could not be read |

## Printing

- Ctrl+P / Share, Print prints the open slip on one page, with each database's address in place of the buttons. It shows the student's newest version.
- After picking a period, the footer button prints every slip in that period, one per page, from the record. The button appears only when the file is opened locally: printing does nothing inside the claude.ai viewer, so the hosted page never shows it.

## Checks

```sh
python3 tools/check.py                          # data: ids, searches, databases, quotes, course by period
NODE_PATH="$(npm root -g)" node tools/smoke.cjs # headless Chromium: all slips, log copy, welcome back, builder, print page counts, phone width in both themes
NODE_PATH="$(npm root -g)" node tools/workbench.cjs # headless Chromium: the workbench acceptance tests
```

## Updating student data

Student records live in the `DATA` array in `index.html` (one line). Fields: `id`, `n` name, `p` period, `c` course (`R` Research, `S` Seminar), `q` question, `qf` where it came from, `tp` topic, `f` field, `ch` the chair to fill, `sw` word swaps, `s` three searches `{db, q}`, `tip`, `es` show the Spanish-search note, `nt` no topic yet. Database keys are defined in `DB`.
