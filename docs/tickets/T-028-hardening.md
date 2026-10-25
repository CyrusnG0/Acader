# T-028: Hardening after T-027: engine version bump and the one-per-paragraph test

**Pickup:** in progress (worker-T-028, DeepSeek). **Dependencies:** T-025, T-027 (done, merged at b3e6900). Follow [pickup rules](README.md); the board is authoritative for current ownership. Branch: `task/T-028-hardening`, worktree `../Acader-wt-T-028`, from main b3e6900.

## Read first

AGENTS.md, docs/STATUS.md, docs/TASKS.md, EXPECTATIONS.md, then docs/DECISIONS.md D-060, D-063; docs/handoffs/2026-10-25-T-027-more-places.md (PD-T027-4, mutation table); design/receipt.md §6; `engine/receipt/compile.py`, `engine/receipt/questions.py`, `server/tests/test_receipt_more_places.py`.

## Scope and boundaries

Two findings from the Opus review of T-027, both accepted by the founder 2026-10-25 (D-063). Mechanical; no wording, prompt or product choice.

1. **Engine version bump (L3, PD-T027-4 reversed).** `more_places` is an additive receipt field, and an additive field changes the receipt bytes, so the engine stamp must say so. Set `ENGINE_VERSION = "receipt/1 l1/2"` in `engine/receipt/compile.py`. Keep `RECEIPT_SCHEMA = 1` and the receipt `version` semantics (v1/v2 storage key) unchanged. Regenerate any golden or frozen fixture that carries the stamp; record which ones in the handoff. Stored receipts issued under `l1/1` are still returned unchanged.
2. **One-per-paragraph test for `more_places` (L1).** The T-027 mutation that lets `more_places` hold two places from the same paragraph survived. Add a synthetic case with two grounded non-chosen candidates in one paragraph and assert the list keeps exactly one, and that it is the first in candidate (priority) order before the paragraph-order sort. The test must fail when the per-paragraph guard in `select_candidates` is removed.

Out of scope: `artifact_ids` on `more_places` (T-029), the student preview (T-022, OL-059), any other T-027 finding.

## Required evidence

The stamp test and every regenerated golden pass with `l1/2`; byte-identical recompile still holds for the same log and stamp; the new test fails under the one-per-paragraph mutation (paste the mutation and the failing test name). Full prototype tests with ROOM_LLM=stub, the kit's 29, and web tests + typecheck if any web fixture changes. Record actual environments; never claim unobserved CI.

Model: D (well specified, mechanical).

Return the commit, a dated docs/handoffs note, files changed, EXPECTATIONS A and C lines, and the mutation result. Set your own row to `review`. Only the checker merges and marks done.
