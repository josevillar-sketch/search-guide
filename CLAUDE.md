# Room 63 Search Guide: context for Claude

Read this first. It saves re-explaining the project every session.

## Who and what

- Teacher: Mr. Jose Portela, Room 63, Mater Academy. Address him as "Master".
- Students: AP Capstone. AP Seminar (course `S`) and AP Research (course `R`). AP Research is the priority audience for new research tools.
- This repo: the Room 63 Search Guide, a single-file HTML page (`index.html`) published as a claude.ai artifact. See `README.md` for how it works.

## Rules that apply to everything here

1. No tool writes, rewrites, or narrows a student's question. This is College Board and Room 63 policy. Never suggest question wording or "question starters".
2. No student names in outputs, filenames, or commits. Use student codes.
3. No human-participant data collection before the ethics review packet is complete (risk screen, consent/assent, data plan, school approval).
4. Every number a student reports traces to their own data file. Nothing invented.
5. Recommend to students only tools listed in `RESOURCES.md`. Add a tool there only after opening and checking it.

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
