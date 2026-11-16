# Room 63 weekly deck

The weekly class site for Room 63 (AP Seminar and AP Research, Mr. Portela, Mater Academy) as a master template plus one data file per week. Each week is a JSON file and one build command. The output is a single HTML file that works offline, plus `netlify.toml` and `_headers` (noindex), in two variants, each zipped.

Nothing here deploys anything. Going live always needs Mr. Portela's approval.

## Files

| File | What it is |
|---|---|
| `template.html` | The shell: week overview, day tabs, period and jump controls, previous and next, progress dots, segment timer with ring, work-mode badge, full screen, Agenda, Sources, Library, Guest and Tools panels, annotation layer, print layouts. The look is the November 9 deck's tokens (`--bg #14110d`, `--panel #1d1913`, `--ink #efe7d6`, `--mute #cdc3ad`, `--line #4a3f2e`, `--brass #e0ab49`, `--teal #6fc7b9`, `--warn #e88e6a`, `--rule #806b4c`) with Fraunces, Cormorant Garamond (600) and Space Mono. Dark is the only screen theme; print is light. |
| `week.schema.json` | Every field a week can hold. |
| `weeks/example.json` | A documented one-route example. Copy it to start a week. |
| `weeks/<week>.json` | The real weeks. `weeks/<week>.visuals.md` is that week's visual manifest for approval. |
| `build.mjs` | Node, no network. Checks the house rules, embeds fonts, images, maps and QR codes, writes `dist/<week>/archive/` and `dist/<week>/current/`, zips both. |
| `qa.cjs` | Playwright. Renders every route at 1920x1080, 380x800 and 390x844 and tests behavior, print and motion. Must end with `QA PASS`. |
| `fonts/` | The November 9 deck's embedded fonts (SIL Open Font License). |
| `assets/img/` | Tri-tone WebP photographs, each recorded with its source page, item ID and rights statement in the week JSON. |
| `assets/maps.json` | Offline SVG map paths (U.S. Census Bureau boundaries via us-atlas, Natural Earth via world-atlas; public domain). |
| `vendor/qrcode-generator-2.0.4.mjs` | QR encoder by Kazuhiko Arase (MIT), used only at build time. |

## Make a new week

1. Thursday: copy `weeks/example.json` (or last week) to `weeks/<monday-date>.json`.
2. Fill it in. Slide words are copied verbatim from the source decks. Readings are citations only. No student names, grades, accommodations, pull-out schedules, guest meeting links, emails or passcodes. Bell times are 24-hour (`13:05`).
3. Every route lists its steps in this order, with minutes that add up to the bell:
   `@target` (learning target and why), `@donow` (warm-up, own timer), `@agenda`, `@criteria` (rubric rows in student words), the slides (each step has minutes and a work mode: Silent, Partner or Group), `@practice` (core shows first; supported and extension open on tap; each tagged with task, rubric rows, minutes and DOK), `@materials` (QR codes), `@glossary` (English and Spanish flip cards), `@exit` (prompt plus "Write it in your current work."; set `carry: true` to show it again as the next class's do-now), `@next`, `@absent`.
4. Propose the visual set in `weeks/<week>.visuals.md`: every photograph with source page, item ID, rights statement as the source gives it, credit line and alt text. Order of sources: Mr. Portela's Drive libraries and `RESOURCES.md`, then public-domain archives (Library of Congress, Smithsonian Open Access, NASA, NARA, the Met), then Creative Commons with credit, then original illustrations (stylized, never photorealistic, credited "Original illustration, Room 63"). Drop any item whose rights are restricted or not evaluated. Mr. Portela approves the set with the Thursday draft.
5. Build: `node weekly-deck/build.mjs <week>`
6. QA: `NODE_PATH="$(npm root -g)" node weekly-deck/qa.cjs <week> --shots <folder>` until it prints `QA PASS`. Look at the screenshots.
7. Sunday: final build, QA again, and hand the two zips to Mr. Portela.
8. Deploy only after his approval: drag `dist/<week>/archive/` to the dated site (`room-63-week-of-<month>-<day>-<year>`) and `dist/<week>/current/` to the permanent current-week site named in `week.publish.current_site`. Both send `X-Robots-Tag: noindex`.

Cadence: Thursday draft, Sunday final.

## House rules (build.mjs and qa.cjs enforce them)

- Nothing on screen brighter than paper `#f6efd8`. Contrast 4.5:1 for body text, 3:1 for large text, measured.
- No emoji, no en or em dashes (hyphens for ranges), straight quotes only. Never Inter, Roboto or Arial.
- Inline SVG icons only; no icon fonts, no CDN, no external scripts or fonts. The file works offline.
- At 380px: no horizontal scroll, every touch target 44px or more, no text under 16px, no console errors.
- Body text at least 28px at 1920x1080.
- Slide words verbatim. Reading citations only, no reading text, no anthology covers or pages.
- No student names or work anywhere. The name picker takes initials only, from a pasted list held in the browser tab; it is never stored or sent and never ships with names.
- Guest slides show name, affiliation, topic and time; guest panels use an image of the field and a map. No headshots until the guest gives permission. No logos.
- Every image has alt text (read aloud uses it), a credit line on the slide and a full entry on the Library's Credits tab.
- Video is linked or streamed, captioned only, never embedded. Audio is off by default.

## Presenting

- Keys: Right, Down, Space or PageDown next (builds lines in first); Left, Up or PageUp back; type a number and Enter to jump; Home for the day, then the week; End for absent work; B or `.` blackout; A reveals every build; F full screen; T timer; P pen and highlighter.
- Touch and smart boards: large buttons and swipe left or right.
- The timer chimes softly at zero (once sound is on) and waits; it never advances by itself.
- Two windows on one computer (presenter and projector) follow each other through `BroadcastChannel`.
- Tools: English or Spanish for directions and absent work (slides stay English), text size A, A+, A++, wide reading spacing, builds on or off, sound, print, name picker, teacher mode.
- Teacher mode opens with a passcode and shows scripts and timing cues only. A passcode on a static site is not security: anyone who reads the file can find the cues. Never put student names, meeting links or grades there.

## Print (US Letter)

From Tools, or the buttons on the week and day pages: slides (one landscape page each), the absent-work sheet for one class, every absent sheet (one page per class per day), practice cards at 5x7 (two per page with crop marks; print double-sided, flip on the long edge; front text 14pt or larger), the day handout (target, agenda, tasks, exit prompt) and the student week packet.

## To do

- Phone as a remote: a static site cannot relay between a phone and the classroom computer. It needs a small relay (for example a WebSocket service or a hosted realtime database) that both pages join with a room code; the deck would send the same messages it now sends over `BroadcastChannel`. Not built.
- Room poll from phones: the deck ships a local tally the teacher taps on the board. A real phone poll needs a backend (a form service or a small serverless function with a store) and a privacy review. Not built.
- Video clips: placeholders only until Mr. Portela approves specific captioned clips.
