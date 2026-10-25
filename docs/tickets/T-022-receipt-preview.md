# T-022: Student preview and teacher lifecycle views

**Pickup:** blocked. **Dependencies:** T-017, T-021; OL-049 preview order clarification. Follow [pickup rules](README.md); the board is authoritative for current ownership. Branch: `task/T-022-receipt-preview` from checker-accepted main. Claim only your row before coding.

## Read first

AGENTS.md, docs/STATUS.md, docs/TASKS.md, EXPECTATIONS.md, docs/OPEN_LOOPS.md, PRODUCT.md, then these spec references (unqualified design filenames are in design/): receipt.md §§2a, 5, 7; DESIGN.md; EXPECTATIONS H; event-log.md post-seal whitelist. Read the existing code and dependency handoffs; these tickets do not override the design specs.

## Scope and boundaries

Own preview DTO/routes and web preview components plus teacher receipt state integration. Reuse T-017 rendering tokens and T-021 lifecycle service. Resolve OL-049 before choosing the preview section order; other independent data-boundary work may proceed after dependencies land.

Project student data server-side: facts, bands and question target spans only, never question text or raw teacher artifacts (including nested payloads/network responses). Use exact spec copy, Nothing here is a grade, and the untraced gloss. Post-submit notes/links are new allowed events, labelled added after submit or release; never change sealed bands. Wire withdrawal confirmation and teacher record-removed notice to the real transaction, not local UI state.

Teacher list remains alphabetical/status-only, shows ready-by while compiling, and respects release. Persist Mark as discussed teacher-side with teacher ID and audit entry; never in the student log or student response. No scores, sorting by bands or fake persistence. Require explicit scoped access checks and tests; school roster/magic-link provisioning remains later work. Keep use synthetic/local until the pilot gate passes.

## Required evidence

Student response contains no teacher question text/artifacts; cross-role/log denial; exact labels/gloss; post-submit note/link cannot change bands; real withdrawal UI/tombstone; teacher status and discussed audit isolation; keyboard, narrow/dark/print and network payload checks.

Run relevant new tests, full prototype tests with ROOM_LLM=stub, and the kit's 29 regression tests. For UI changes also run web tests, typecheck/build and focused browser checks. Record actual environments and results; never claim unobserved CI. No secrets, real student data, live providers or shared/llm.py behavior changes.

Return commits, a dated docs/handoffs note, files changed, reproduction commands, EXPECTATIONS A plus the relevant C/H requirements, failures and proposed decisions. Set your own row to review. Only the checker merges, marks done and updates shared tracking. M1 human reading and every pilot gate remain separate; this ticket cannot satisfy them.
