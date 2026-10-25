# T-017: receipt UI and chain view

Blocked until T-010 and T-016 are checker-accepted done. Follow [pickup rules](README.md). This ticket is an execution brief; design docs remain authoritative.

## Then pickup: T-017 receipt UI and chain view

Goal: let a teacher read the real golden receipt and follow a sentence to the evidence behind it. This makes the engine inspectable and prepares the nursing walkthrough.

Read first: finalized DESIGN.md; design/receipt.md §§2–3, 5–7; design/build-plan.md M1/M2; EXPECTATIONS A/H/I-M1; T-016 handoff; OL-047. Continue on a new `task/T-017-receipt-ui` branch or worktree based on checker-accepted main. Claim T-017's own row before coding.

### Scope and implementation sequence

1. **Establish the data boundary.** Add a deterministic, stub-only golden export command using the existing builder, not hand-authored substitute receipts. Export all twelve sessions for a local development gallery. Include the unchanged compiled receipt, hash and a separately named view context containing synthetic header metadata, final text, sentence/paragraph references and the evidence needed for chain display. Read actual L1/document/event structures before defining this context. Keep fixture metadata visibly synthetic; do not imply the compiler produced a student name or assignment title it does not contain. Exclude secrets and provider credentials. No live LLM calls or fetching reading URLs.
2. **Render the receipt document.** Use the existing vanilla TypeScript/Vite setup, semantic HTML and the approved tokens. Keep one reading column at most 72ch, headings/rules and no boxed dashboard sections. Header: synthetic student/assignment, submitted date, body words, sources. Then factual compiled summary, Where to ask, both band bars and the exact blind-spot gloss. Keep hashes in About this receipt at the foot. Details start closed, expand in print. Include compiler mechanics and source titles accurately; do not recalculate provenance or modify counts in JavaScript.
3. **Implement sentence-to-chain navigation.** Any displayed sentence must offer a keyboard-accessible route to its own evidence. Include final text, actual source passage/card/claim steps where present, event sequence IDs, date/hour, and relevant recorded draft differences where supported. Preserve actual missing links. Use the spec's rounded narrative and checked/student-linked distinctions; never invent a source, draft history or confirmed relationship. A paragraph ID alone is insufficient to invent sentence correspondence. If available records cannot support a required step, document the precise missing fields and proposed resolution before expanding engine behavior.
4. **Handle real states.** Cover complete, questions pending, replay mismatch, empty counts, missing chain links, declared help, accepted suggestions and confirmed Helper mechanics. Pending questions must not render null or fabricated text. Mapper-only suggestions do not become traced evidence. Use DOM text insertion for document/source/card strings; never interpolate untrusted prose into HTML. Apply the existing wording policy to newly rendered UI and contextual evidence as required by receipt.md §5; do not change compiler copy policy silently.
5. **Apply design/accessibility.** Self-host the approved font assets with their licences for the application. Light/dark, visible focus, keyboard operation, labelled patterned bars, reduced motion and greyscale print must work. Do not use colour as a judgment. The full first-screen content and gloss should fit at 1440×900 for the baseline nursing golden; narrow/zoom views must remain readable without horizontal scrolling or clipped content. Do not hide substantive questions merely to meet a viewport target.
6. **Add a reproducible local review gallery.** Provide one documented command to prepare the actual golden data and launch the UI, plus a link/selection for every session. Any submission-style list is alphabetical by synthetic student name and status only; no band sorting, ranking, filters or averages. Do not display release deadlines or operational statuses that the system has not computed. Static development examples must be identified as such.

### Scope boundary requiring explicit checklist accounting

M1 in build-plan.md is receipt/chain rendering on golden sessions. M2 owns production student preview, jobs, persistence/release windows and caps. Do not build those subsystems inside T-017 or claim them complete through a static demo. No student route may receive teacher question text under the guise of a preview. Do not add a fake working withdrawal or Mark as discussed control without persistence.

The board currently assigns all of H to T-017, including preview and withdrawal. Report this discrepancy in the handoff. The checker must explicitly map rendering requirements to T-017 and remaining behavior to M2 before marking the task done; do not quietly treat an unchecked touched line as passed. This brief proposes that mapping and does not override the spec.

Out of scope: full writing workspace, mapper enablement, new provenance thresholds/question rules, database release pipeline, school accounts, hosting/deployment, server PDF generation, real student data and changing shared/llm.py. Do not resolve OL-047's existing product proposals through presentation changes.

### Suggested work split for a lead using workers

- Worker A: deterministic golden export and contract tests; own only agreed server/golden/export files and tests.
- Worker B: receipt renderer/styles after the export contract is agreed; own agreed web receipt files.
- Lead: chain adapter semantics, exact copy/design choices, integration and handoff. Use an independent review worker after integration. Keep ownership boundaries explicit and avoid concurrent edits to entry points/lockfiles.

### Acceptance evidence to return

- All twelve golden receipts render through the same application renderer; their displayed word/claim counts, mechanics, sources and question targets match compiler/export data. No hand-edited expected receipts or recorded sessions.
- At least one real browser interaction for each meaningful chain condition: source path, Coach path, declared import, student-only link, broken/failed mark and edited paragraph. Assert identifiers and evidence, not just that a panel opens. Missing history stays explicit.
- Browser checks for pending and replay-mismatch states, zero-word/claim denominators, text escaping, keyboard/focus, light/dark and print. If a golden does not cover a state, use a narrowly scoped derived test fixture and label it as such.
- Screenshots at 1440×900 and 375px, both themes; print evidence with details expanded and patterns/labels legible. Check 200% zoom and no horizontal overflow. Record first-screen measurements for the baseline receipt.
- Run with ROOM_LLM=stub: prototype suite from prototype; web tests/typecheck/build from prototype/web; kit's `python3 -m pytest -q v04/tests web/tests` from writing-room-kit. Use installed supported environments; record actual Python/Node versions. Report failures rather than replacing the frozen expectations to obtain a pass.
- Run golden projection checks after export integration. Regenerate Chromium recordings only if the editor/recorder changed; UI-only work should not alter them. Do not claim an unobserved CI run passed.
- Handoff `docs/handoffs/YYYY-MM-DD-T-017-receipt-ui.md`: branch/commits, files, reproducible start/export commands, tests/results, screenshots, exact EXPECTATIONS coverage, deferred M2 lines, unresolved questions and a twelve-session reading checklist. Set T-017 to review, never done; leave checker-owned shared files alone.

## Review and milestone ownership

Codex reviews the branch diff, data lineage, product wording and access boundary; reruns appropriate tests and the gallery; and accepts or returns concrete failing items. Only the checker merges and updates STATUS/UPDATE_LOG/CHANGELOG/OPEN_LOOPS/DECISIONS.

M1 completion requires at least ten rendered golden receipts read by a person. Browser automation or an AI review does not satisfy that human gate. Supply the gallery and reading checklist for the founder; keep M1 open until that reading is recorded.

Parallel work available after the UI assignment is settled: T-007 preregistration and T-009 nursing walkthrough/blind-test protocol, each on its own branch. Both are ready but neither should distract the receipt worker. Teacher/class/assignment window by 2026-10-30 and provider/school approvals remain founder-owned blockers.
