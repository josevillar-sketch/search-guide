# Classroom materials: what to use when

For Mr. Portela. These are teacher notes, not a student page. Every piece is built from `build.py` and checked by `tools/design_check.cjs` and `build-pdf.cjs`. Nothing here writes or changes a student's research question.

## The order, across the AP Research year

| When | The student is | Hand out | It gives you back |
|---|---|---|---|
| Method choice | deciding how to answer the question | `own-data-or-public-data` (1 page) | A first decision: collect data, or analyze data that exists. |
| Method choice, one period | finding out what public data exists | `sda-lab` (2 pages: teacher page, student sheet) | A filled record box: dataset, variable, exact question asked, valid cases. |
| Before the Inquiry Proposal Form | planning the method in detail | `method-planning-grid` (2 pages: blank grid, worked example) | A grid a classmate could run the study from. |
| With the Inquiry Proposal Form, studies with people | preparing for your ethics review | `risk-screen`, `data-plan`, `question-check` (1 page each), then `consent-templates.docx` | The packet College Board asks you to review: risks, instrument, consent forms, data handling. Your decision goes on the risk screen. |
| Drafting the paper | writing the method section | `method-section-checklist` (1 page) | A self-check and a peer check against College Board's wording. |
| Before a draft is submitted | checking the whole paper | `paper-elements-check` (1 page) | The six required elements located by page, and the word count, in College Board's own words. |
| After the paper | preparing to present | `oral-defense-questions` (2 pages: the official questions, a notes page) | A map from each question group to evidence in the student's own portfolio. No scripted answers. |
| Any time | looking for a source or a tool | `research-library.html` (the published page) | Nothing to collect. It points only to resources verified in `RESOURCES.md`. |

## What College Board requires of you

From the AP Research Course and Exam Description, pages 46 to 47, read on 2026-11-12:

- Review every proposal for ethical considerations before data collection.
- Review any surveys, interview questions, or questionnaires the student will use.
- Do not approve a proposal that poses more than minimal risk to participants.
- Your approval is sufficient unless the student will publish, compete, or present publicly. Then a federally registered institutional review board must also approve.
- The Process and Reflection Portfolio must hold documentation of permissions and approvals.
- For the oral defense, ask three questions from the published list, one from each group; you may tailor the wording, and a fourth may clarify an earlier answer (pages 61 to 62).
- Do not assign, provide, or generate research questions, and do not write, revise, or correct anything that is part of the submitted work (page 63, "Role of the Teacher").

The risk screen, the data plan, and the question check are how a student brings you those four things on paper. The Room 63 forms add what your own packet asks for: a logged start date and a deletion date.

## Before any of this reaches students

- Read the consent templates. The Spanish was written by Claude and has not been checked by a fluent reader.
- Fill in the school email and school phone on the consent forms. They are still in brackets.
- Open the Research Library page and share it only when you are satisfied.
- The open methods textbook and OpenIntro Statistics were listed from their landing pages. Open each book once before assigning from it.

## Rebuilding

```sh
python3 classroom/build.py
NODE_PATH="$(npm root -g)" node classroom/build-pdf.cjs
classroom/build-consent.sh
NODE_PATH="$(npm root -g)" node tools/design_check.cjs
```
