# Current Status

**Last updated:** 2026-10-25 (T-010/T-017 checker review; next worker tickets)
**Phase:** prototype v1; M1 engineering complete, human reading gate open. Synthetic M2 infrastructure can proceed in parallel.

## What works

- T-001…T-006 and T-011…T-016: scaffold, schema, replay, events/seal, L1 provenance, compiler and twelve synthetic golden sessions. T-008 sources accepted.
- T-010: founder-approved exact candidate promoted to DESIGN.md; checker accepted. Source Sans 3/Literata, light/dark tokens, patterns, focus and print rules (D-052).
- T-017: all twelve actual compiler receipts render with separate synthetic context and sentence-to-chain navigation. No fabricated evidence; unsupported history is explicit. Local gallery: `cd prototype/web && npm run review:receipts` after installing the documented dependencies.
- **[VALIDATED] Fresh independent checker run:** prototype 840 passed, web 145 passed plus typecheck/build, kit 29 passed. DESIGN.md matches the approved candidate byte-for-byte; format validator and diff check pass. Python 3.14.5 / Node 25.9.0 locally; no new CI result claimed.
- Prior T-017 browser evidence: 221 assertions, wide/narrow light/dark and print screenshots. Not rerun in this review; see the handoff for exact scope and the viewport-equivalent zoom limitation.

## Single next action

**Claim T-018 (durable receipt/artifact storage) or T-019 (bounded job queue)** using [pickup tickets](tickets/README.md). Their files are separate and both are unowned/ready. T-007 preregistration and T-009 walkthrough protocol remain independently ready.

## Outstanding and boundaries

- A person must read at least ten rendered receipts before M1 is complete. Use the unchecked twelve-case list in the T-017 handoff; no human completion inferred from AI/browser review.
- T-020 compile integration, T-021 release/withdrawal, T-022 student preview/teacher states and T-023 S3 harness have explicit dependencies and remain blocked. Full L3 integration and actual human evaluation still need later tickets.
- OL-048 scope mapping is resolved: T-017 covers H rendering; T-021/T-022 own the unimplemented withdrawal/preview lines. This does not mark those features complete.
- OL-047 remains open: existing T-015/T-016 product proposals, including “Written on N days”, await founder disposition. No silent wording change.
- OL-049: preview-order conflict in receipt.md §7 needs resolution before T-022 layout. OL-046 mapper corpus/labels remains open. L3b and mapper stay off absent their evaluation gates.
- No production receipt release, student preview or access workflow exists yet. The gallery is synthetic and local. Kit results remain simulated; shared/llm.py unchanged; code track parked.

## Worker handoff

Read AGENTS → STATUS → TASKS → EXPECTATIONS → OPEN_LOOPS → your ticket and cited specs. Claim only one unowned ready row, coordinate ownership, branch from accepted main, implement only that ticket, and return commit + dated handoff + actual checks at review. Codex checks/merges and owns shared tracking. Preserve the founder’s untracked AGENTS.md.

## Founder actions / pilot blockers

- Read at least ten rendered receipts and record reader/date/cases. The university team has supplied a real pain point/use case; this review does not replace the teacher walkthrough.
- F-001 schedule; F-002 / OL-036 named teacher, class and assignment window by **2026-10-30**.
- F-003 / OL-037 / OL-026 school/provider/processor and applicable ethics approvals; independent labeller and teacher participation for T-007/T-009.
- No real student before design/build-plan.md §4 is green.

Latest review: [checker handoff](handoffs/2026-10-25-T-010-T-017-checker.md). Product intent: PRODUCT.md and later decisions. Implementation specs: design/README.md. Board: TASKS.md.
