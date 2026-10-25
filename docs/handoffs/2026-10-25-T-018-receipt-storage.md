# T-018: Durable receipts and AI artifacts

- **Lead:** worker-T-018   **Workers used:** none (single worker)
- **Branch or worktree:** `task/T-018-receipt-storage` (worktree `Acader-wt-T-018-receipt-storage`)
- **Commit(s):** 5b7e692 (implementation, tests, task claim); this handoff commit follows it

## What changed

- `prototype/server/app/receipt_store.py` (new): durable receipt and artifact storage on the
  existing event-log SQLite connection.
  - Tables: `receipts(log_id, seal_hash, version, receipt_id, seal_seq, receipt_hash, body)`
    with primary key `(log_id, seal_hash, version)`, and
    `receipt_artifacts(log_id, artifact_id, task, prompt_hash, body, hash)` with primary key
    `(log_id, artifact_id)`.
  - Receipt bytes are the compiler's `canonical_json(receipt)` stored as a BLOB;
    `receipt_hash = sha256(body)` (D20/D31). Reads re-check both canonical form and hash and
    raise `CorruptReceipt` on mismatch.
  - Artifacts are validated before insert (`sha256(body) == hash`) and by
    `stored_artifacts()`, which raises `CorruptArtifact`. `artifacts()` returns raw rows for
    verification, so a damaged row is reported rather than hidden.
  - `verify(log_id, ...)` runs `engine.events.verify` with the stored receipt and every stored
    artifact, plus optional `extra_artifacts` for outputs stored by another component
    (for example mapper artifacts referenced by `map.finding`). Missing, corrupt or
    hash-mismatched references fail. A supplied artifact whose id matches a stored row is
    rejected with `ReceiptConflict`, so a caller cannot mask a damaged stored row.
  - `delete_log_in_tx(log_id)` deletes only that log's receipt and artifact rows inside the
    caller's transaction; `delete_log` is the self-owned wrapper. Events are never deleted.
- `prototype/server/app/receipt_service.py`: narrow integration.
  - `issue_receipt` compiles first, with no write transaction open, then writes the receipt,
    all compile artifacts and `receipt.issued` in one `BEGIN IMMEDIATE` transaction. A failed
    event append rolls all of them back.
  - A retry for the same log/seal/version returns the stored receipt and artifacts without
    recompiling or calling a model. If no receipt exists yet, `stored_artifacts(log_id)` is
    passed to the compiler so matching prompts are reused instead of asked again.
  - Optional `receipts=` (inject a store) and `extra_artifacts=` (persist caller-supplied
    outputs atomically) stay within this ticket's persistence boundary.
- `prototype/server/tests/test_receipt_store.py` (new): 16 tests covering every required
  evidence item.
- `docs/TASKS.md`: only the T-018 owner/status row (claim), now `review`.

## Storage API for T-020

All methods take `log_id`, so reads and deletion cannot cross logs.

- `ReceiptStore(service.db)` — uses the existing connection; creates its two tables.
- `store_in_tx(log_id, *, receipt, receipt_hash=None, artifacts=None,
  extra_artifacts=None, seal_hash=None, seal_seq=None, version=None) -> bool` — requires the
  caller's transaction; returns `False` for an identical retry; raises `ReceiptConflict` if
  another receipt would be replaced and `CorruptArtifact` if an artifact body mismatches.
- `store(log_id, ...)` / `delete_log(log_id)` — wrappers that open and commit their own
  transaction. Do not nest them inside a caller transaction.
- `delete_log_in_tx(log_id) -> int` — for T-021: call inside the same transaction that
  appends `record.withdrawn`; a rollback restores the receipt and artifacts.
- `get(log_id, *, seal_hash=None, version=1) -> StoredReceipt | None` — one receipt, or the
  latest seal for that version.
- `latest(log_id) -> StoredReceipt | None` — highest version then seal.
- `artifacts(log_id) -> {artifact_id: artifact}` — raw rows (hashes not rechecked).
- `stored_artifacts(log_id) -> {artifact_id: artifact}` — verified rows for compiler reuse.
- `verify(log_id, *, seal_hash=None, version=1, extra_artifacts=None) -> VerifyResult` —
  chain + receipt integrity + every referenced artifact hash. Supplied artifacts may only add
  ids that are not already stored; a collision raises `ReceiptConflict`.

T-020 should pass mapper artifacts through `extra_artifacts` on issuance or `verify`, because
no mapper job exists yet to store them itself. They must use ids that are not in the store.

## Tests run

Environment: macOS (Darwin 25.6.0), Python **3.14.5**, venv created at `prototype/.venv` and
installed with `pip install --require-hashes -r requirements.lock`. No live model calls; all
runs used `ROOM_LLM=stub`. The kit used the system Python 3.14.5. CI (Python 3.12/Ubuntu) was
not run here.

- `cd prototype && ROOM_LLM=stub .venv/bin/python -m pytest -q server/tests/test_receipt_store.py`
  → **18 passed in 0.13s**
- `cd prototype && ROOM_LLM=stub .venv/bin/python -m pytest -q`
  → **858 passed, 1 warning in 7.78s** (baseline before this ticket: 840)
- `cd writing-room-kit && ROOM_LLM=stub python3 -m pytest -q v04/tests web/tests`
  → **29 passed, 2 warnings in 0.13s**

Required evidence, all in `test_receipt_store.py`:

| Evidence | Test |
|---|---|
| Restart persistence | `test_restart_persistence` (file DB closed and reopened) |
| Rollback on failed issuance | `test_rollback_on_failed_issuance` (event append raises; rows and event are gone) |
| Retry makes no duplicate event/artifact | `test_retry_is_idempotent_and_makes_no_model_calls` |
| Corrupt/missing artifact rejection | `test_corrupt_artifact_is_rejected`, `test_missing_artifact_is_rejected`, `test_store_rejects_a_mismatched_hash_and_a_bad_artifact` |
| Cross-log isolation | `test_cross_log_isolation` |
| Stored-output rebuild is byte-identical with a failing model callable | `test_stored_output_rebuild_is_byte_identical_without_a_model` |
| Transactional deletion | `test_transactional_deletion_can_roll_back_or_commit` |
| No write transaction during a model call | `test_no_write_transaction_during_a_model_call` (`sqlite3.Connection.in_transaction`) |
| Receipt integrity / supplied outputs | `test_issue_persists_canonical_bytes_hash_and_artifacts`, `test_corrupt_receipt_is_rejected`, `test_verify_accepts_outputs_supplied_by_the_caller`, `test_verify_rejects_a_supplied_artifact_that_collides_with_a_stored_row` |
| First issuance wins across a stamp race | `test_concurrent_issuance_with_a_different_stamp_returns_the_first_receipt` |

Mutation spot checks (temporary edits, then restored):

- Skip artifact hash validation in `stored_artifacts` → `test_corrupt_artifact_is_rejected`
  failed (`DID NOT RAISE CorruptArtifact`).
- Remove `log_id` from receipt reads → `test_cross_log_isolation` failed by returning the
  other log's receipt.
- Disabling the pre-compile retry lookup did **not** fail a test: stored outputs still
  prevented model calls and the in-transaction check still prevented a duplicate
  `receipt.issued`. The lookup is an optimization and preserves the first issuance if the
  engine stamp changes; idempotency does not depend on it alone.
- Restoring the old `{**stored, **supplied}` merge → the artifact-collision test failed
  (`DID NOT RAISE ReceiptConflict`).
- Restoring the old "raise on a different stored hash" branch → the stamp-race test failed
  with `ReceiptConflict`.

`git diff --check` is clean. No UI or `prototype/web/` change, so web tests, typecheck and
browser checks were not applicable to this ticket.

## EXPECTATIONS sections claimed

- **A:** all lines. Scope limited to the ticket; `shared/llm.py` untouched; no secrets, real
  student data or live providers; new behaviour has tests; no banned user-facing copy
  (checked in the new and changed files); handoff present. No design doc changed.
- **C (record/verify):** same log + same engine stamp + stored AI outputs gives byte-identical
  receipt bytes (`test_stored_output_rebuild_is_byte_identical_without_a_model`); stored
  receipt and artifact hashes are checked by `verify`, and missing or corrupt rows fail.
- **H (data lines):** unchanged; this ticket only makes the already-compiled receipt JSON
  durable. No receipt wording or question-selection rule changed.
- Not claimed: M2 exit, release timing, student preview, withdrawal UX (T-021), the queued job
  loop (T-019), or any human/pilot gate.

## Not done / open

- Map events whose mapper artifacts were never stored will make `ReceiptStore.verify` fail
  until T-020 supplies them (`extra_artifacts`) or persists them. This is intentional: the
  check must not pass on a missing output.
- Export of receipts and artifacts (M4b) is not implemented; deletion is.
- No release policy, public route, queue, auth shortcut or question-selection change.
- Receipt versions beyond 1 are supported by the schema but not exercised by a caller yet.

## Proposed decisions (the checker takes these to the founder; nothing here is decided)

- **PD-T018-1: the first issuance wins.** `(log_id, seal_hash, version)` is the receipt key.
  If a retry arrives with a different engine stamp (for example a new commit sha), the stored
  receipt is returned unchanged rather than overwritten or rejected. This now also holds when
  two issuances pass the pre-check concurrently: the transaction returns the first stored
  receipt and the caller receives those bytes, not its locally compiled ones
  (`_persist` returns the stored `ReceiptResult`). *Recommend:* accept; it preserves the
  `receipt.issued` evidence and D20's "same stamp" condition.
- **PD-T018-2: mapper artifacts are supplied, not guessed.** No mapper job exists to build
  them, so `verify` accepts them as `extra_artifacts`; a receipt or event that cites an
  artifact absent from both the store and that argument fails verification. *Recommend:*
  accept; T-020 wires the mapper.
- **PD-T018-3: deletion touches rows, never the chain.** `delete_log_in_tx` removes receipts
  and artifacts only; `record.withdrawn` remains the chain event that records the choice.
  *Recommend:* accept, consistent with receipt.md §7 and the post-seal whitelist.
- **PD-T018-4: two API tiers.** `*_in_tx` methods participate in a caller transaction (for
  T-021); `store`/`delete_log` open their own. Calling the latter inside an open transaction
  is a programming error. *Recommend:* accept and document in T-020/T-021.

## Follow-up review (2026-10-25)

Two accepted follow-ups, both fixed with tests in this branch:

1. **Supplied artifacts can no longer mask a stored row.** `verify` previously merged
   `{**artifacts, **extra_artifacts}`, so a caller-supplied output with the same id replaced
   a damaged stored row. It now raises `ReceiptConflict` on any id collision.
   `test_verify_rejects_a_supplied_artifact_that_collides_with_a_stored_row` damages the
   stored row, proves `verify` fails without the argument, and proves the collision is
   rejected with it. Non-colliding supplied ids still work
   (`test_verify_accepts_outputs_supplied_by_the_caller`).
2. **PD-T018-1 now holds across the race.** `_persist` returned `ReceiptConflict` when a
   concurrent issuance with a different engine stamp won the check. It now returns the first
   stored receipt and event, and `issue_receipt` returns that stored `ReceiptResult` rather
   than the locally compiled one. The test
   `test_concurrent_issuance_with_a_different_stamp_returns_the_first_receipt` compiles with a
   different `git_sha`, calls `_persist` as if both callers passed the pre-check, and asserts
   the first bytes, hash, event and artifacts are returned with no duplicate event. A normal
   retry with the other stamp is also asserted.

Final counts after the follow-ups: new store tests **18 passed**, full prototype **858
passed**, kit **29 passed** (commands and environment above).

## Checker review (2026-10-25): passed, merged to `main` (2b7b1a2)

- Independent read-only review by an Opus reviewer (fresh locked venvs, Python 3.14.5, `ROOM_LLM=stub`; no CI result claimed). Merged main: prototype suite **898 passed** (reported by the checker after all four merges); kit 29 per the handoffs.
- Reviewer reproduced 16/16 new tests and 856 full before the follow-ups; both follow-ups (artifact-id collision, first-issuance-wins across the race) were fixed with tests on the branch (18 new tests, 858 full). Scope: own files and own TASKS row only; `shared/llm.py`, design docs and shared tracking untouched; no secrets or student data.
- EXPECTATIONS A ticked; C (byte-identical rebuild from stored outputs; verify fails on missing/corrupt rows) ticked; H data lines unchanged.
- Founder decisions: PD-T018-1…4 accepted as **D-053**.
- Not covered (later): export (M4b), mapper persistence (T-020 supplies via `extra_artifacts`), receipt versions > 1.
