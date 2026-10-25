# T-025: Remove student withdrawal of the process record

**Pickup:** ready. **Dependencies:** T-021 (done). Follow [pickup rules](README.md); the board is authoritative for current ownership. Branch: `task/T-025-remove-withdrawal` from checker-accepted main. Claim only your row before coding. Touches `app/lifecycle.py` like T-026 and T-022: the coordinator sequences them (T-025 first is simplest) or the later branch rebases.

## Read first

AGENTS.md, docs/STATUS.md, docs/TASKS.md, EXPECTATIONS.md, docs/OPEN_LOOPS.md, PRODUCT.md, then these spec references (unqualified design filenames are in design/): docs/DECISIONS.md D-062 (and the amended D-053, D-058); receipt.md §2a, §7; event-log.md §3, §6, §8; privacy.md §5; docs/handoffs/2026-10-25-T-021-release-withdrawal.md. Read the existing code and dependency handoffs; these tickets do not override the design specs.

## Scope and boundaries

The founder dropped student withdrawal from v1 (D-062): students can see and export their process record but cannot remove it, before or after release. Remove the withdrawal feature; keep the release cap, `release_records`, the release job and everything else T-021 built for release.

Remove: `POST /logs/{id}/withdraw`; the `record.withdrawn` branch of the generic `POST /logs/{id}/events` route and the type from its accepted list; `ReceiptLifecycle.withdraw`, `_withdrawal_event`, `is_withdrawn`, the tombstone table/columns and the `record_removed` teacher status; `app/withdrawal.py` and its calls in `receipt_service.py` (publication no longer needs the withdrawn check) and in the release path; `withdrawn_at` from `release_records` if nothing else reads it. Take `record.withdrawn` out of the post-seal whitelist in `engine/events/chain.py`, so the store refuses it like any other non-whitelisted post-seal event (409). Remove `receipt_store.delete_log_in_tx` only if withdrawal was its sole caller; keep `JobQueue.cancel_by_log` (generic queue tooling) and its tests, renaming the test reason strings if they say `record.withdrawn`.

The event chain stays append-only: never delete or rewrite stored events, and do not add any deletion path. There is no production data, so no migration of old `record.withdrawn` events is required; if a stored fixture or golden contains one, regenerate it and say so. If `verify` would need legacy tolerance for any reason, stop and write a proposed decision instead of choosing. Tests that asserted withdrawal behaviour are deleted or turned into refusal tests; every other test keeps passing. Docs are already updated by the checker; do not edit design docs, DECISIONS, STATUS or other tickets.

No product wording changes; no UI (there is none for withdrawal yet).

## Required evidence

`record.withdrawn` after the seal → 409 on the generic route and from the store; no `/withdraw` route (404/405); release still happens at base/cap with frozen clocks; duplicate release still idempotent; no teacher payload before release; cross-log access still rejected; `grep -rn withdraw prototype/` shows only test names for refusal or nothing. Note the test count change and why.

Run relevant new tests, full prototype tests with ROOM_LLM=stub, and the kit's 29 regression tests. Record actual environments and results; never claim unobserved CI. No secrets, real student data, live providers or shared/llm.py behavior changes.

Model: O+S (an Opus lead checks the removal list and the chain rule; a Sonnet or DeepSeek worker may do the mechanical removal, D-039).

Return commits, a dated docs/handoffs note, files changed, reproduction commands, EXPECTATIONS A plus the relevant C/H requirements, failures and proposed decisions. Set your own row to review. Only the checker merges, marks done and updates shared tracking. M1 human reading and every pilot gate remain separate; this ticket cannot satisfy them.
