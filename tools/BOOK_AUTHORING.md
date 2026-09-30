# Writing a Room 63 book

Every book in the library is one HTML file that turns pages. The pages live in a list
called `FACES` (front and back of each leaf, so the count is even). The Team Project
(`tp/index.html`, Book S1) is the shell every new book is built from: its styles,
page-turning engine and cover art stay as they are, and only the pages change.

## The loop

1. Write `make_spec.py` that prints a spec (`key`, `title`, `theme`, `colors`, `faces`).
2. `python3 make_spec.py > spec.json && python3 tools/build_book.py spec.json` writes `<key>/index.html`.
3. `node tools/check_book.js <key>` (a server on port 8763 serves the repo root) reports:
   `overflow` (page content taller than the page at its fitted scale), `tight` (fit scale
   under 0.9), bad jumps, bad page numbers, bad tabs. Add a folder as a second argument
   to get a screenshot of every page.
4. Fix and repeat until `overflow` is empty in both views and no page fits below 0.85.

## Page references: never type a page number

Give a face an `"id"`. Chapter boards also take `"folio"` and `"title"` (the tabs are
built from them). The builder fills these in:

| Token | Becomes |
|---|---|
| `[[num]]` | this page's number line |
| `[[pj:ID]]` | an inline link that shows the page number of ID |
| `[[gtag:ID]]` | a "Page N" tag button (glossary rows) |
| `[[jump:ID]]` | `data-jump` and `aria-label` for a button you write yourself (contents rows, steps) |
| `[[pno:ID]]` | the page number of ID as text |

Paper faces from index 2 are numbered 1, 2, 3 and so on. A chapter board has no number
of its own and points readers at the page after it.

## The shape of a book (copy tp's order)

| Faces | What |
|---|---|
| 0 | Cover, class `board lthr`. Copy tp face 0 and change the three `<text>` title lines and the `<h1>`. |
| 1 | `endpaper` "Kept by" page: name, period drawers, a one-box summary, three small lines. |
| 2 to 3 | Contents (paper), folio list with `[[jump:...]]` rows, R and P notes. |
| 4 | Start here: the steps in order, one `gorow` each. |
| 5 | Find it fast: problems to pages. |
| then | For each folio: one chapter board (`board chapter`), then 3 to 6 paper pages. |
| end | Self-check form, Words that fool you, Words in this book (3 to 4 pages), the last page (`endpaper`), `endpaper marbled`, back cover (`board lthr`, copy tp face 61). |

## Building blocks (all already styled; see tp faces for exact markup)

- Paper page: `<div class='grainlayer grain'></div><div class='pg'><div class='head'><span>TITLE IN CAPS</span><span>{{SHORT}}{{PHEAD}}</span></div> ... </div>[[num]]<div class='shade'></div>`
- First page of a folio adds `<p class='folio'>` with the small icon svg (tp face 7).
- Chapter board: tp face 6 (`{{GOLD}}`, `ch-top`, `ch-num`, `ch-title`, two svgs, `ch-target` "BY THE END", `ch-inside` "INSIDE" list with page numbers via `[[pno:ID]]`).
- Tables: `table.stages` with `tight`, `runs`, `four` (tp faces 7, 8, 10).
- Cards: `card2 weak` (a warning), `card2 wait` (WAITING ON A ROOM 63 DECISION), `card2 good`, `card2 try` with a hidden `.ans` (tp faces 21, 48).
- Checklists: `div.form` with `button.tick` rows, `tierlab` groups, the `passstamp` svg and `span.live.srt` (tp faces 31, 45, 53).
- Glossary rows: `div.wrow` with the icon svg, English `<strong>`, Spanish `<em lang='es'>`, one line, and `[[gtag:ID]]` (tp faces 55 to 58).
- Plates (PLATE I, II ...): larger drawn figures (tp faces 13, 17, 29, 38, 43, 47). Reuse their markup patterns with your own words.
- `<div class='R'>` shows only to AP Research students, `<div class='P'>` shows before a period is chosen.
- Engine placeholders you may use: `{{SHORT}}` `{{PHEAD}}` `{{NAME}}` `{{META}}` `{{DRAWERS}}` `{{GOLD}}` `{{TILDE}}` `{{NAMEVAL}}` `{{NLEN}}`.

## Voice (match The Team Project)

- Short, plain sentences. "You" is the student. "I" is Mr. Portela. Room 63, Mater Academy, 2026-27.
- No em dashes, no en dashes, no semicolons. No filler, no hype.
- Every College Board fact is one the fact sheet confirms, with "Checked September 30, 2026." on the page.
- Room 63 dates not yet set go in a `card2 wait` "WAITING ON A ROOM 63 DECISION" card. Never invent a Room 63 date.
- Examples are made up and say so. Links go only to pages the fact sheet lists.
- Point to the other books by name and folio (The Research Log, The AI Manual, Presenting and Defending, The Field Guide to Research Questions, The Research Manual, The Team Project).
- Spanish glosses are for students learning English: correct, common Latin American Spanish.
- A page holds about as much as a tp page (roughly 600 to 1,100 characters of visible text).
