# T-022: Student preview and teacher lifecycle views

**Pickup:** ready (2026-10-25: OL-049 answered by D-059). **Dependencies:** T-017, T-021 (done). The delayed-state rendering uses the status from T-026; if T-026 has not landed, build the wording and view against the `delayed` status value and integrate when it merges. Coordinate with T-025/T-026 (both touch `app/lifecycle.py`) and T-027 (teacher receipt view). Follow [pickup rules](README.md); the board is authoritative for current ownership. Branch: `task/T-022-receipt-preview` from checker-accepted main. Claim only your row before coding.

## Read first

AGENTS.md, docs/STATUS.md, docs/TASKS.md, EXPECTATIONS.md, docs/OPEN_LOOPS.md, PRODUCT.md, then these spec references (unqualified design filenames are in design/): receipt.md §§2, 2a, 5, 7; docs/DECISIONS.md D-059, D-061, D-062; DESIGN.md; EXPECTATIONS H; event-log.md post-seal whitelist. Read the existing code and dependency handoffs; these tickets do not override the design specs.

## Scope and boundaries

Own preview DTO/routes and web preview components plus teacher receipt state integration. Reuse T-017 rendering tokens and T-021 lifecycle service. Preview order is decided (D-059): identical to the teacher's first screen, in the same order (summary, the parts the teacher may ask about, then the bars with the "Untraced is not AI" line), with no hidden version; the student sees which parts, never the question wording.

Project student data server-side: facts, bands and question target spans only, never question text or raw teacher artifacts (including nested payloads/network responses). Use exact spec copy, Nothing here is a grade, and the untraced gloss. Post-submit notes/links are new allowed events, labelled added after submit or release; never change sealed bands. **Do not build** a withdrawal confirm dialog, a `record removed` status or a tombstone view: student withdrawal is dropped from v1 (D-062; T-025 removes the code).

Teacher list remains alphabetical/status-only, shows "Ready by" (the cap time, D-061) while compiling, and respects release. Word and render the **delayed** state (D-061) on the list and in place of the receipt: plain and honest, about the system and never about the student or the work, no verdict wording, wording-filter clean; the lead proposes the exact copy in the handoff for the founder to confirm. Persist Mark as discussed teacher-side with teacher ID and audit entry; never in the student log or student response. No scores, sorting by bands or fake persistence. Require explicit scoped access checks and tests; school roster/magic-link provisioning remains later work. Keep use synthetic/local until the pilot gate passes.

## Required evidence

Student response contains no teacher question text/artifacts; cross-role/log denial; exact labels/gloss; post-submit note/link cannot change bands; no withdrawal UI or `record removed` anywhere; preview order equals the teacher first screen; delayed-state copy and view; teacher status and discussed audit isolation; keyboard, narrow/dark/print and network payload checks.

Run relevant new tests, full prototype tests with ROOM_LLM=stub, and the kit's 29 regression tests. For UI changes also run web tests, typecheck/build and focused browser checks. Record actual environments and results; never claim unobserved CI. No secrets, real student data, live providers or shared/llm.py behavior changes.

Return commits, a dated docs/handoffs note, files changed, reproduction commands, EXPECTATIONS A plus the relevant C/H requirements, failures and proposed decisions. Set your own row to review. Only the checker merges, marks done and updates shared tracking. M1 human reading and every pilot gate remain separate; this ticket cannot satisfy them.
