# T-019: Bounded durable job queue

**Pickup:** ready. **Dependencies:** T-012, T-003. Follow [pickup rules](README.md); the board is authoritative for current ownership. Branch: `task/T-019-job-queue` from checker-accepted main. Claim only your row before coding.

## Read first

AGENTS.md, docs/STATUS.md, docs/TASKS.md, EXPECTATIONS.md, docs/OPEN_LOOPS.md, PRODUCT.md, then these spec references (unqualified design filenames are in design/): architecture.md §4; docs/designs/eng-review-v1.md D23; docs/designs/eng-review-v2.md D4/D6. Read the existing code and dependency handoffs; these tickets do not override the design specs.

## Scope and boundaries

Own new `prototype/server/app/jobs/` and its tests. Avoid receipt_service.py, compile_service.py, main.py and routes_events.py; T-020 owns integration. Use existing SQLite conventions and make caller-owned transactions possible.

Implement durable idempotent enqueue, claim/lease, completion, cancellation by log and restart recovery. Fence stale workers so a lost lease cannot publish results. Enforce four concurrent LLM calls per backend, round-robin by submission, backoff 1/4/16 minutes. Inject clock and handlers for deterministic tests; never call providers while holding a write transaction. Preserve slots for future lowest-priority mapper jobs without implementing the mapper. Return a documented queue API for T-020 and transactional cancel API for T-021. No new retry policy beyond the spec: report ambiguities before choosing terminal behavior.

## Required evidence

Concurrent claims do not duplicate jobs; expired leases recover; stale completion is rejected; fairness and per-backend cap; exact retry schedule with fake clock; cancel-by-log and rollback; restart retains idempotency. No sleeps or live calls.

Run relevant new tests, full prototype tests with ROOM_LLM=stub, and the kit's 29 regression tests. For UI changes also run web tests, typecheck/build and focused browser checks. Record actual environments and results; never claim unobserved CI. No secrets, real student data, live providers or shared/llm.py behavior changes.

Return commits, a dated docs/handoffs note, files changed, reproduction commands, EXPECTATIONS A plus the relevant C/H requirements, failures and proposed decisions. Set your own row to review. Only the checker merges, marks done and updates shared tracking. M1 human reading and every pilot gate remain separate; this ticket cannot satisfy them.
