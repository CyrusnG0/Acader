# T-020: Submit and compile orchestration

**Pickup:** blocked. **Dependencies:** T-018, T-019. Follow [pickup rules](README.md); the board is authoritative for current ownership. Branch: `task/T-020-compile-jobs` from checker-accepted main. Claim only your row before coding.

## Read first

AGENTS.md, docs/STATUS.md, docs/TASKS.md, EXPECTATIONS.md, docs/OPEN_LOOPS.md, PRODUCT.md, then these spec references (unqualified design filenames are in design/): architecture.md §3; receipt.md §§4–7; event-log.md §§5–6. Read the existing code and dependency handoffs; these tickets do not override the design specs.

## Scope and boundaries

Own app/receipt_service.py, compile_service.py, submit integration in events_service/routes_events/main, and concrete job handlers. Rebase on accepted T-018/T-019 APIs before coding.

Wire durable scheduling to sealed submission without depending on an LLM. A retry must recover scheduling without another seal or duplicate issue. Produce persisted L1/questions-pending output first, then run the existing grounded L3e receipt-question path as a queued upgrade using stored outputs. Keep replay mismatch behavior and engine stamp intact; L3b stays off. Preserve the current compiler rules and OL-047 wording. Define receipt version/idempotency boundaries explicitly in the handoff.

Do not add L3a/c/b models or invent missing prompts. Full leak-checked L3 pipeline remains a separately planned M2 dependency before real evaluation; this ticket is infrastructure, not the M2 exit. No production auth, emails or deployment.

## Required evidence

Submit seals with provider down; queued work survives restart; repeated submit/job retry causes no duplicate receipt issuance; stored output reuse avoids extra calls; L1 fallback and later question upgrade; replay mismatch; failure between commit and scheduling recovers.

Run relevant new tests, full prototype tests with ROOM_LLM=stub, and the kit's 29 regression tests. For UI changes also run web tests, typecheck/build and focused browser checks. Record actual environments and results; never claim unobserved CI. No secrets, real student data, live providers or shared/llm.py behavior changes.

Return commits, a dated docs/handoffs note, files changed, reproduction commands, EXPECTATIONS A plus the relevant C/H requirements, failures and proposed decisions. Set your own row to review. Only the checker merges, marks done and updates shared tracking. M1 human reading and every pilot gate remain separate; this ticket cannot satisfy them.
