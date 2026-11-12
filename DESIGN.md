---
name: Room 63 Search Guide
description: One look for everything an AP Capstone student in Room 63 sees, on screen and on paper.
colors:
  ground: "#ece4d2"
  card: "#fbf7ee"
  card-2: "#f3ead6"
  ink: "#1d1812"
  ink-soft: "#4a3f31"
  hair: "#c9b996"
  edge: "#7d6a45"
  brass-text: "#6d4f14"
  brass-fill: "#d6ad55"
  pine: "#245e55"
  on-pine: "#fbf7ee"
  oxide: "#9c3322"
  plum: "#6d3a73"
  night-ground: "#07201b"
  night-card: "#0f2a25"
  night-card-2: "#15392f"
  night-ink: "#f3ead6"
  night-ink-soft: "#c9bb9c"
  night-hair: "#2f5a50"
  night-edge: "#b8995a"
  night-brass-text: "#e2b964"
  night-pine: "#7fd1c0"
  night-oxide: "#f08a74"
  night-plum: "#d9a5dc"
  night-focus: "#f0c56a"
typography:
  display:
    fontFamily: "Fraunces, Georgia, 'Times New Roman', serif"
    fontSize: "28px"
    fontWeight: 900
    lineHeight: "32px"
    letterSpacing: "0.02em"
  headline:
    fontFamily: "Fraunces, Georgia, 'Times New Roman', serif"
    fontSize: "21px"
    fontWeight: 650
    lineHeight: "26px"
  title:
    fontFamily: "Fraunces, Georgia, 'Times New Roman', serif"
    fontSize: "18px"
    fontWeight: 650
    lineHeight: "24px"
  body:
    fontFamily: "'Atkinson Hyperlegible', Verdana, system-ui, sans-serif"
    fontSize: "17px"
    fontWeight: 400
    lineHeight: "26px"
  label:
    fontFamily: "'Space Mono', 'Courier New', ui-monospace, monospace"
    fontSize: "13px"
    fontWeight: 700
    lineHeight: "18px"
    letterSpacing: "0.12em"
  print-body:
    fontFamily: "'Atkinson Hyperlegible', Verdana, system-ui, sans-serif"
    fontSize: "10pt"
    fontWeight: 400
    lineHeight: 1.4
rounded:
  control: "6px"
  stamp: "3px"
  pill: "999px"
spacing:
  xs: "8px"
  sm: "16px"
  md: "24px"
  lg: "32px"
  xl: "48px"
components:
  button-brass:
    backgroundColor: "{colors.brass-fill}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "14px 20px"
    height: "52px"
  button-ghost:
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    height: "44px"
  button-pine:
    backgroundColor: "{colors.pine}"
    textColor: "{colors.on-pine}"
    rounded: "{rounded.control}"
    height: "44px"
  card:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "16px 24px"
  ruled-note:
    backgroundColor: "{colors.card-2}"
    textColor: "{colors.ink}"
    padding: "8px 12px"
---

# Design System: Room 63 Search Guide

## Overview

**Creative North Star: "The reading room at night, the index card by day."**

Room 63 has two surfaces and one voice. The night surface is deep pine with a scatter of brass points: it holds the welcome, the period picker and the student's own desk. The paper surface is cream card stock with an ink edge: it holds the question, the checks, the searches and every printed handout. A student should feel they have sat down at a real desk with a real card in front of them, and that the card is theirs.

The pages are working tools and reading matter, so the world lends type, palette, density and one signature move, and nothing else. Controls are the standard ones a student already knows. Running text is calm and set in a face built for legibility. Expression lives in the frame: the masthead, the paper card with its date stamp, the inked stamps on a library card, the `63` seal on a handout.

This name was drawn from the built pages on 2026-11-12. Mr. Portela may rename it.

**Key Characteristics:**
- Ink, brass and pine on warm paper. Nothing on screen is brighter than the paper.
- Fraunces speaks, Atkinson Hyperlegible explains, Space Mono labels.
- Paper objects have an ink edge and a pressed shadow. Nothing floats on a soft blur.
- One brass button on screen at a time.
- Screen and print share every token. A handout is the same world with the lights on.

## Colors

A warm, low-chroma paper palette with three inks: brass for the one action and for labels, pine for links and selection, oxide for warnings and "do not".

### Primary
- **Brass**: the fill of the single primary button, the selected drawer tab, the date on the question card. As text it is the darker brass, used for labels and list markers.

### Secondary
- **Pine**: links, the filled search button, the pledge panel, the night surface itself.

### Tertiary
- **Oxide**: warnings, removals, the "Don't cite" stamp, the top edge of Road A on the decision guide.
- **Plum**: "Ask first" and the Seminar judgment pen. Never decoration.

### Neutral
- **Ground**: the page behind everything.
- **Card** and **Card-2**: paper, and the slightly deeper paper of a ruled note or a table head.
- **Ink** and **Ink-soft**: text, and secondary text. Secondary text is tinted from the ink, never gray.
- **Hair** and **Edge**: hairline dividers, and the stronger outline of a control.

### Named Rules
**The Paper Ceiling Rule.** No surface on screen is lighter than card. Pure white appears only on a printed sheet.

**The One Brass Rule.** One brass-filled button is visible at a time. A second action is a ghost button.

**The Measured Contrast Rule.** Body text holds 4.5:1 and large text 3:1 against its real ground, in light and in dark. `tools/design_check.cjs` measures every text element; nobody eyeballs it.

## Typography

**Display Font:** Fraunces (with Georgia, Times New Roman)
**Body Font:** Atkinson Hyperlegible (with Verdana, system-ui)
**Label/Mono Font:** Space Mono (with Courier New)

**Character:** A heavy, slightly eccentric serif for the voice, over a sans drawn so that no two letters can be confused. The mono face is for labels, call numbers, search strings and dates: things a student copies exactly.

### Hierarchy
- **Display** (900): page titles. Uppercase on screen. The Search Guide welcome runs from 40px to 88px before a period is picked and folds to 20px on the desk; the Library masthead runs up to 6rem; a handout title is 31pt.
- **Headline** (650, 21px/26px): section headings such as "Seven checks".
- **Title** (650, 18px/24px): card and block titles.
- **Body** (400, 17px/26px on screen, 10pt/1.4 in print): everything a student reads. Measure 45 to 75 characters.
- **Label** (700, 13px/18px, 0.12em, uppercase): field labels, call numbers, stamps, the slug under a handout title.

### Named Rules
**The No Eyebrow Rule.** No small tracked label sits above a heading. The heading carries its own weight. What a label would have said goes in a strip or slug under the title.

**The Measure Rule.** Text that wraps never runs past 75 characters, even where the container is wider. Cap the text, not the box.

**The Banned Faces Rule.** Inter, Roboto and Arial never appear, in any file.

**The Fallback Rule.** Where a web font cannot load, the named fallbacks carry the page: Georgia for Fraunces, Verdana for Atkinson Hyperlegible, Courier New for Space Mono. The Word consent forms are set in Georgia and Verdana on purpose, because families open them on any computer. Every page must still fit a phone with the web fonts blocked.

**The Plain Punctuation Rule.** No en dash, no em dash, no emoji, in pages or in the source.

## Layout

An 8px grid: 8, 16, 24, 32, 48. One column on a phone with a 16px gutter, reflowing down to 320px without a sideways scroll. From 700px the shell is 808px wide; from 1024px it is 1184px and the desk sits beside the work in two columns. The Library is one reading column up to 62rem with a sticky drawer label beside it on wide screens.

Printed handouts are US letter with 0.5in by 0.55in margins. Each `.page` is one sheet; on screen it is drawn as a sheet of paper on the ground color. A one-page handout stays one page: `classroom/build-pdf.cjs` fails the build if the count changes.

Related things sit close; distinct groups get clear space. There is more space above a heading than below it.

## Elevation & Depth

Depth is pressed, not floated. A raised paper object has a 1.5px ink edge and a hard, zero-blur shadow offset down and to the right, in ink on paper and in brass on the night surface. This is the system's chosen depth language, not a default.

### Shadow Vocabulary
- **Pressed** (`box-shadow: 4px 4px 0 var(--drop)`): the brass button, period cards, drawer tabs.
- **Card** (`box-shadow: 6px 6px 0 var(--drop)`): library cards and the pledge panel.
- **Down** (`box-shadow: 1px 1px 0 var(--drop)` with a 3px translate): the selected or pressed state.

### Named Rules
**The Pressed Shadow Rule.** One hard offset shadow per raised object. No soft blur, no glow, no stacked shadows.

**The Flat Sheet Rule.** Print has no shadows. Borders and rules do the work.

## Shapes

Corners are barely eased (6px) on controls and cards; stamps are tighter (3px) and sit a degree or two off level. Pen chips are pills. Printed sheets are square. Rules are ink: a heavy rule over a hairline under every handout title, a hairline above and below a ruled note, a full frame around a rule box. A block never carries a thick stripe down one side; the one exception is the quotation bar beside a student's own question.

## Components

### Buttons
- **Shape:** eased rectangle (6px), 1.5px edge, at least 44px tall; the brass button is 52px with an ink edge.
- **Primary:** brass fill, ink text, pressed shadow. One per screen.
- **Hover / Focus:** a 3px focus ring in pine (brass on night), offset 2px. The pressed state moves 3px into its shadow.
- **Secondary / Ghost:** no fill, an edge-colored outline, no shadow. Pine fill for "Search" on a slip.

### Chips
- **Style:** paper ground, 1.5px edge, a small boxed letter in Space Mono.
- **State:** selected is brass, pressed down into its shadow. Pens on the desk are pills with a dashed or dotted edge per pen.

### Cards / Containers
- **Corner Style:** 6px.
- **Background:** card on ground; on night, the deep pine panel.
- **Shadow Strategy:** see Elevation. Slip cards inside a page are flat with a hairline.
- **Border:** 1px hairline for flat cards, 1.5px ink for raised ones.
- **Internal Padding:** 16px to 24px.

### Inputs / Fields
- **Style:** card ground, 1.5px edge, 6px corners, a visible label above every field.
- **Focus:** the 3px ring. The caret is pine.
- **Selection:** brass ground, ink text, on every page.

### Navigation
- The Search Guide has a three-part rail (Versions, Checks, Searches) that sticks under the header and stops sticking while a field has focus. The Library has lettered drawer tabs that scroll sideways on a phone.

### Signature components
- **The ficha.** The student's question on a cream card with a large Fraunces date, a red margin rule and a row of seven dots.
- **The slip.** One paper card with an ink edge and a pressed shadow. An oxide rule under its head, the student's question in Fraunces at 23px to 32px beside its quotation bar, then the three searches as numbered rows divided by hairlines, each with a boxed Fraunces numeral. The searches are rows on the card, never cards inside it. On paper the slip prints flat on one page.
- **The stamp.** A double-edged inked label, slightly rotated: Cite it, Don't cite, Ask first, Tool, Example. On a handout it marks the page a student must not copy.
- **The ruled note.** Deeper paper between two hairlines, for "Mind this" and for the notes on a handout.
- **The 63 seal.** A double ring with a Fraunces `63`, top right of every printed sheet.
- **The numeral.** A boxed Fraunces numeral with a small pressed shadow marks anything a student does in order: the three searches, the seven checks. A check that passes inks its numeral.
- **The plate.** A brass square with a Fraunces letter: the Library's drawers, the two roads on the decision guide.
- **The rule box.** A sheet's one rule, in Fraunces, inside a full ink frame. A sign-off line inside the frame keeps the reading face, and each label stays with its blank.
- **The slug.** One mono line under a handout's title rule saying who the sheet is for.

## Do's and Don'ts

### Do:
- **Do** run `NODE_PATH="$(npm root -g)" node tools/design_check.cjs` before any page or handout is pushed. It must print PASS. `sh tools/check_all.sh` runs it with every other check.
- **Do** frame a warning in oxide all the way round, and rule a note above and below.
- **Do** design the states a student reaches by acting (form open, version saved, a check passed), not only the page as it loads.
- **Do** draw every icon as inline SVG, stroked at about 2px in the current color.
- **Do** give every tinted block a rule or border too, so a printer with background graphics off loses nothing.
- **Do** make every tap target on a phone at least 44px in both directions, apart from a link inside a sentence.
- **Do** balance headings (`text-wrap: balance`) and let body copy wrap `pretty`.
- **Do** theme what the browser draws: selection, caret, focus ring, underline offset.
- **Do** set columns of figures with tabular numerals. Leave numbers inside a sentence alone: tabular figures pull "12" apart.
- **Do** keep handout wording, student question text and every claim exactly as written. Design moves words; it does not change them.

### Don't:
- **Don't** put a small uppercase label above a heading.
- **Don't** mark a note, card or list item with a thick colored stripe down one side.
- **Don't** set display type above 6rem or track it tighter than -0.04em.
- **Don't** use Inter, Roboto or Arial, an en or em dash, or an emoji.
- **Don't** use a font glyph (an arrow, a check mark, a box) as an icon.
- **Don't** add a soft drop shadow, a glow, a gradient on text, or glass blur.
- **Don't** link to an icon font or any script from a CDN. Fonts come from Google Fonts with named fallbacks; everything else is inline.
- **Don't** add a second brass button to a screen.
