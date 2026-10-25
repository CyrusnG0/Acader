# T-021: Release cap and transactional withdrawal

**Pickup:** blocked. **Dependencies:** T-020. Follow [pickup rules](README.md); the board is authoritative for current ownership. Branch: `task/T-021-release-withdrawal` from checker-accepted main. Claim only your row before coding.

## Read first

AGENTS.md, docs/STATUS.md, docs/TASKS.md, EXPECTATIONS.md, docs/OPEN_LOOPS.md, PRODUCT.md, then these spec references (unqualified design filenames are in design/): receipt.md §7; architecture.md §3; event-log.md §6; eng-review-v2.md D10. Read the existing code and dependency handoffs; these tickets do not override the design specs.

## Scope and boundaries

Own a new receipt lifecycle service/repository, its integration points and tests. Coordinate with T-020 and use its accepted commit before starting.

Release at max(deadline, submit+24h, questions-ready), capped at max(deadline, submit+24h)+48h. At cap release pending questions and record the operator alert; late questions are marked added after release. Before release teachers get only the specified compiling state and ready-by time, never receipt contents.

Withdrawal must atomically append record.withdrawn, cancel queued compile/L3/question/release work, delete unreleased receipts and stored outputs and create the teacher-side tombstone. Running workers must check the withdrawn state inside their publication transaction, preventing resurrection. Cover the existing generic /events entry point as well as any dedicated route; it already accepts record.withdrawn. Submitted work remains submitted. After-release withdrawal must not silently become this before-release operation. No new deletion policy.

Use explicit tenant/role/owner scoping at service boundaries and fail closed. Tests can supply synthetic identities; do not present a demo role selector as authentication. Exact UI notices belong to T-022.

## Required evidence

Frozen-clock deadline/24h/cap boundaries; outage then late questions; duplicate release; withdrawal races with queued and running completion/release; rollback atomicity; generic events route cannot bypass cancellation; no teacher payload before release; cross-log access rejection.

Run relevant new tests, full prototype tests with ROOM_LLM=stub, and the kit's 29 regression tests. For UI changes also run web tests, typecheck/build and focused browser checks. Record actual environments and results; never claim unobserved CI. No secrets, real student data, live providers or shared/llm.py behavior changes.

Return commits, a dated docs/handoffs note, files changed, reproduction commands, EXPECTATIONS A plus the relevant C/H requirements, failures and proposed decisions. Set your own row to review. Only the checker merges, marks done and updates shared tracking. M1 human reading and every pilot gate remain separate; this ticket cannot satisfy them.
