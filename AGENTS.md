# Search Guide implementation and finish criteria

Read README.md, CLAUDE.md, DESIGN.md, and QUALITY.md before substantial changes. The current artifact is index.html, a single-file student-facing tool with no required application build step. Preserve the remote's newer design system when reconciling earlier local work.

## Preserve

- Preserve the DATA records unless an explicit task supplies authorized corrections. Never write, rewrite, narrow, reorder, complete, score, or suggest a student's question. Keep the RULE comment and the student-authorship invariant.
- The student's Research Log is the record. Browser storage is device-local convenience, not submission, synchronization, identity verification, or authentication.
- Maintain the existing Fraunces, Atkinson Hyperlegible, Space Mono, pine, paper, and brass system. Refine the approved design instead of replacing it.
- Keep index.html below 360,000 bytes. Preserve print output, both themes, reduced motion, keyboard focus, shared-device exits, data isolation, storage recovery, and clipboard fallbacks.
- Do not add runtime dependencies or transmit student work. Development-only verification tools are separate from the single HTML deliverable.
- `npm run compact:artifact` is an optional formatting maintenance command for the byte cap, not a runtime/build requirement. It preserves DATA/reference content and the RULE comment; JavaScript compression and name mangling are disabled. Verify affected rendered states and behavior after formatting.

## Proactive construction loop

1. Recover the latest source and open findings from QUALITY.md. Define a finite outcome and a falsifiable acceptance case before adding functionality.
2. Inspect the affected user journey and failure/recovery state. For substantial work, use bounded independent reviews of usability, domain/data integrity, and engineering/accessibility as appropriate.
3. Fix causes in the source of truth. Add regression coverage for consequential bugs that existing checks missed, using synthetic text and existing fixture identities rather than duplicating student records.
4. Run the project verification command documented in README.md. Inspect affected screens with actual fonts as well as offline fallbacks; include phone/iPad/desktop and print when changed. Use the supplemental mobile suite for browser-specific coverage: request WebKit explicitly, record unavailable runtimes as blocked, and never substitute a Chromium result for a WebKit pass. Automated checks do not establish full accessibility conformance or real-user usability.
5. Correct failures and rerun the relevant checks. After the final change, reconcile evidence against that exact source version in QUALITY.md. Mark blocked or untested paths explicitly.
6. Deliver the updated artifact and a concise verification result once applicable criteria pass. Optional refinements do not justify an endless loop.

Keep generated screenshots, PDFs, browser state, and per-run logs out of version control. Preserve dependency locks and runnable verification source. Never publish or externally share the embedded student records as a side effect of testing.

## Approved distribution policy

The user resolved and authorized the existing Search Guide repository remaining public on November 12, 2026. Preserve that decision. It covers the existing roster and question records only: add no further kinds of student data, grades, records, Drive files, browser storage, or generated student artifacts. Do not reopen the same visibility decision or ask for the same permission again. Reconsider only if GitHub reports a fork, a new kind of student data is proposed, or the user asks.

Before external delivery, verify the intended destination and current repository identity/access metadata against this policy. `npm run verify:release` accepts the approved public repository with no reported forks; unavailable or inconsistent metadata remains an unverified check, not evidence of a new privacy incident. Do not infer visibility from npm's `private` flag or a failed anonymous request. Ordinary localhost tests remain available with artifacts kept local. Do not delete DATA, rewrite history, or overwrite another owner's branch as a substitute for reconciliation.

The local checkout and the current remote default branch have diverged. Preserve both; reconcile changes in an isolated copy. Confirm the final revision, authorized destination, and policy conditions again before external delivery. The approved repository policy does not itself deploy the local pass or release unrelated publication holds.
