# T-018: Durable receipts and AI artifacts

**Pickup:** ready. **Dependencies:** T-012, T-016. Follow [pickup rules](README.md); the board is authoritative for current ownership. Branch: `task/T-018-receipt-storage` from checker-accepted main. Claim only your row before coding.

## Read first

AGENTS.md, docs/STATUS.md, docs/TASKS.md, EXPECTATIONS.md, docs/OPEN_LOOPS.md, PRODUCT.md, then these spec references (unqualified design filenames are in design/): architecture.md §§3–5; receipt.md §6; event-log.md §6; D31 in docs/designs/eng-review-v1.md. Read the existing code and dependency handoffs; these tickets do not override the design specs.

## Scope and boundaries

Own new `prototype/server/app/receipt_store.py` and its tests, with narrow persistence integration in `app/receipt_service.py`. T-019 owns the queue; do not edit its files. T-020 owns submit/orchestration changes.

Persist canonical receipt bytes/hash, log/seal/version and AI artifacts (task, prompt hash, body, hash). Use the existing SQLite connection/transaction conventions, not another database. Receipt storage, artifacts and `receipt.issued` must succeed atomically and be idempotent on retry. Do not hold a DB write transaction during a model call. Reads and deletion must be log-scoped, with an API that can participate in a caller-owned transaction for later withdrawal. Preserve compiler output and receipt hashes.

Expose stored-output retrieval so rebuilding the same log with the same stamp can avoid model calls. Verify referenced artifact hashes as well as receipt integrity. Document the storage API in the handoff so T-020 can integrate it. No public routes, release policy, question-selection changes or auth shortcut.

## Required evidence

Restart persistence; rollback on failed issuance; retry creates no duplicate event/artifact; corrupt/missing artifact rejection; cross-log isolation; stored-output rebuild byte-identical with a model callable that fails if invoked; transactional deletion.

Run relevant new tests, full prototype tests with ROOM_LLM=stub, and the kit's 29 regression tests. For UI changes also run web tests, typecheck/build and focused browser checks. Record actual environments and results; never claim unobserved CI. No secrets, real student data, live providers or shared/llm.py behavior changes.

Return commits, a dated docs/handoffs note, files changed, reproduction commands, EXPECTATIONS A plus the relevant C/H requirements, failures and proposed decisions. Set your own row to review. Only the checker merges, marks done and updates shared tracking. M1 human reading and every pilot gate remain separate; this ticket cannot satisfy them.
