# Room 63 Search Guide: context for Claude

Read this first. It saves re-explaining the project every session.

## Who and what

- Teacher: Mr. Jose Portela, Room 63, Mater Academy. Address him as "Master".
- Students: AP Capstone. AP Seminar (course `S`) and AP Research (course `R`). AP Research is the priority audience for new research tools.
- This repo: the Room 63 Search Guide, a single-file HTML page (`index.html`) published as a claude.ai artifact. See `README.md` for how it works.

## Rules that apply to everything here

1. No tool writes, rewrites, or narrows a student's question. This is College Board and Room 63 policy. Never suggest question wording or "question starters".
2. No student names in outputs, filenames, or commits. Use student codes. Never copy a Drive file about a student into this repo.
3. No human-participant data collection before the ethics review packet is complete (risk screen, consent/assent, data plan, school approval).
4. Every number a student reports traces to their own data file. Nothing invented.
5. Recommend to students only tools listed in `RESOURCES.md`. Add a tool there only after opening and checking it.

## Where things live (Google Drive)

Folder names only. Student records stay in Drive and never come into this repo.

| Drive folder | Holds |
|---|---|
| AP Capstone at Mater Academy - School Year 26 / 27 | Course home for the year |
| Room 63 Project Archive | Documents rotated out of the claude.ai project "AP RESEARCH & AP SEMINAR: AP CAPSTONE PROGRAM"; see its "Project Archive Index" sheet |
| ChatGPT (school Drive and personal Drive) | Folders that connect to ChatGPT. The school one is the most active: recovered work histories, guest-lab and book-fair files, and private student backups |
| Room 63 Claude Handoff, and other "... Claude Handoff" folders | Handoff notes between Claude sessions |
| Room 63 — Approved learning resources — 2026-10-25 | Guest speaker cards |
| Room 63 — Grading working records and recovery — Private | Teacher-only grading records. Active in November 2026: each Claude or Cowork chat saves a backup subfolder here named "[Topic] Chat Backup - [date] - Portela J" |

The claude.ai project also keeps a "Where It Lives" register; it is the fuller map.

## Files

| File | Purpose |
|---|---|
| `index.html` | The search guide page. Student data lives in the `DATA` array. |
| `README.md` | How the page works, storage keys, printing, checks. |
| `RESOURCES.md` | Verified research tools and datasets, with how each fits AP Research. |
| `tools/` | Checks: `check.py` (data), `smoke.cjs` and `workbench.cjs` (browser tests). |

## Before pushing changes to `index.html`

```sh
python3 tools/check.py
NODE_PATH="$(npm root -g)" node tools/smoke.cjs
NODE_PATH="$(npm root -g)" node tools/workbench.cjs
```
