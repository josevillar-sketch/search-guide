# Room 63 Search Guide

A personalized search slip for every AP Capstone student in Room 63: the student's question on record, the chair their source table still needs, the field's words for their words, three searches built for free databases, a tip drawn from their own search history, and the six-line log entry.

Single-file HTML, vanilla JS, no build step. Published as a claude.ai artifact; `index.html` here is the page source.

## What a student does

1. Tap their period, then their name (or open `index.html#<student-id>`).
2. Run the three searches, find one source, and tap **Copy log lines** to paste a pre-dated entry into their log. Line 3 fills in with the last search they tapped.
3. Changed question? The builder at the bottom starts from their question on record, keeps "quoted phrases" together, and picks databases from the words in the question (health words send it to PubMed, school words to ERIC, law words to the Legal Information Institute, and so on).

The page remembers the last slip opened on that device (`localStorage` key `r63sg_last`) and offers it back with a **Not you?** escape for shared iPads.

## Printing

- Ctrl+P / Share, Print prints the open slip on one page, with each database's address in place of the buttons.
- After picking a period, the footer button prints every slip in that period, one per page.

## Checks

```sh
python3 tools/check.py                          # data: ids, searches, databases, quotes, course by period
NODE_PATH="$(npm root -g)" node tools/smoke.cjs # headless Chromium: all slips, log copy, welcome back, builder, print page counts, phone width in both themes
```

## Updating student data

Student records live in the `DATA` array in `index.html` (one line). Fields: `id`, `n` name, `p` period, `c` course (`R` Research, `S` Seminar), `q` question, `qf` where it came from, `tp` topic, `f` field, `ch` the chair to fill, `sw` word swaps, `s` three searches `{db, q}`, `tip`, `es` show the Spanish-search note, `nt` no topic yet. Database keys are defined in `DB`.
