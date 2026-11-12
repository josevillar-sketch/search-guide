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

## How Room 63 chats coordinate

ChatGPT and Claude sessions pass work to each other through Google Docs, not through this repo:

- **Hollis Dot Line - 2026-11-01** (personal Drive): the running message line. Each entry starts with an ID like `ROOM63-DOT-...` or `ROOM63-CLAUDE-...` and a date. Standing approvals are recorded here.
- **Room 63 | Cloud Continuation Ledger** and **Cloud Continuation Protocol for Other Chats**: open items and the rules for picking up another chat's work.
- **AP Research — Conference Command Center — 2026-27 — Teacher Only**: conference records.

All four are teacher-only and hold student names. Read them in Drive when needed; never copy them here.

**Reply style (Mr. Portela's Low-Reading Mode, set 2026-11-01):** at most five short bullets, with DONE / BLOCKED / NEXT where useful. One decision asked at a time. Put detail in the records, not in the reply.

## Standing approval and proactive workflow

On 2026-11-12 Mr. Portela wrote: "Keep it moving at the zenith level and bake proactivity into the workflow across all Work… I grant you all approvals and permissions you need and accept nothing but your absolute best work."

What that means in this repo:

**Do without asking**
- Check, log, and merge additions to `RESOURCES.md`, `BOOKS.md`, and `classroom/`. Open the pull request, run the checks, merge it.
- Fix what you find: a dead link, a wrong edition, a claim a source no longer supports. Say what you fixed.
- After each merge: add a dated copy to the Drive backup folder (never overwrite an earlier copy) and post an entry to the Hollis Dot Line.
- Close your own loose ends before reporting. A reply that ends in a list of things you could have done is unfinished.
- Verify before you state. Run the demo, open the page, hash the file. Say which of those you did.
- Audit after you build. Re-read what you made against the primary source, not against your memory of it. The 2026-11-12 audit found a claim about a College Board guide that had never been checked against the guide; read the document before describing it.

**The approval does not change these**
- Rules 1 to 5 above. Rule 1 is College Board policy; no approval lifts it.
- Student privacy. No names or records leave the teacher-only Drive folders.
- Nothing goes to students or families until Mr. Portela has seen it. Building and merging is not distributing.
- Anything sent in Mr. Portela's name states only facts that are confirmed. Remove a guess before sending.
- Other sessions' files. Grade entry, Pinnacle, Classroom, and other chats' records keep the approval rules written in their own records; this grant was given in the Search Guide session.
- Site access denials and bot checks are not worked around.

**Still follow Low-Reading Mode** for replies: short, DONE / BLOCKED / NEXT, one decision at a time.

## Files

| File | Purpose |
|---|---|
| `index.html` | The search guide page. Student data lives in the `DATA` array. |
| `README.md` | How the page works, storage keys, printing, checks. |
| `RESOURCES.md` | Verified research tools and datasets, with how each fits AP Research. |
| `BOOKS.md` | Book request list with confirmed editions and ISBNs. Move a book to `RESOURCES.md` when it arrives. |
| `classroom/` | AP Research materials. Printable handouts: the own-data-or-public-data guide, the method planning grid, the method section checklist, the SDA lab, and the consent and assent templates (Word, English and Spanish). Also `research-library.html`, the student-facing page of approved resources, published as a private claude.ai artifact at https://claude.ai/artifact/JBuyyEu4YsMEezCL1R3xUG (republish to that address after any change; Mr. Portela decides when to share it); every link on it must be in the verified part of `RESOURCES.md`, and `tools/check_links.py` enforces that. Rebuild with `python3 classroom/build.py`, then `NODE_PATH="$(npm root -g)" node classroom/build-pdf.cjs` (prints the PDFs and fails if a handout changes page count, a font is missing, or content runs off the sheet), and `classroom/build-consent.sh`. One look for everything students see: Fraunces, Atkinson Hyperlegible and Space Mono, in the ink, brass and pine of `index.html`. The Word consent templates stay in a system font on purpose, so they open the same in Word and Google Docs. |
| `tools/` | Checks: `check.py` (data), `smoke.cjs` and `workbench.cjs` (browser tests), `check_links.py` (every link in the resources log and handouts). |

## Before pushing changes to `index.html`

```sh
python3 tools/check.py
NODE_PATH="$(npm root -g)" node tools/smoke.cjs
NODE_PATH="$(npm root -g)" node tools/workbench.cjs
```
