# T-020: Submit and compile orchestration (incl. the D-054 retry cap)

- **Lead:** opus-lead-T-020. **Workers:** DeepSeek ×2 via cc-fleet (F-005): A = queue cap (plus one fix round), B = orchestration. The lead wrote the specs, reviewed the diffs, ran every check below and ran its own mutation pass. The lead wrote no code.
- **Branch:** `task/T-020-compile-jobs`, rebased onto main `76837ab`.
- **Commits:** `ee6d534` (claim), `90db2a1` (queue cap and `on_failed` hook), `3b6c91b` (orchestration), `e2594d5` (D-054 fix: the cap counts retryable failures only), plus the commit that adds this handoff.

## What changed

- **`app/jobs/queue.py`** (D-054; a separate commit as the founder asked):
  - New `max_attempts=5` (`MAX_ATTEMPTS`) and a new column `retry_failures`. The column is added in place to existing databases with `ALTER TABLE`.
  - The cap counts retryable failures only. A job whose fifth retryable failure arrives becomes `failed`.
  - Backoff is now indexed by `retry_failures`: 1, 4, 16, 16 minutes. Without lease recovery this matches the old behaviour.
  - Expired-lease recovery is unchanged from T-019. The job is requeued at once and the recovery uses no try.
  - New `on_failed(db, job)` hook. It runs inside the same transaction whenever a job becomes `failed`, through the cap or a permanent failure. If the hook raises, the failure rolls back.
- **`app/compile_jobs.py`** (new), `CompileJobs`. It builds its queue as `JobQueue(service.db, lock=service._lock, clock=service.clock, on_failed=...)`. There are two job kinds per seal:
  - `receipt.compile`, key `receipt.compile:{log_id}:{seal_hash}`, `backend=None`. It runs replay → mark check → L1 → **receipt v1** with `ask=None, stored={}`, so it never calls a model. It records replay-mismatch operator alerts. If `questions_pending` is true it enqueues the questions job.
  - `receipt.questions`, key `receipt.questions:{log_id}:{seal_hash}`, `backend=default_backend()`. It runs the existing grounded L3e path → **receipt v2**, reusing stored artifacts. A tracker notices `LLMUnavailable`; the answers obtained before the outage are then stored, and `RetryableJobError("llm_unavailable")` is raised.
  - If the model answered but its outputs were rejected twice, v2 is still issued, using the compiler's existing status rule (`questions_pending`). One `questions_incomplete` alert is written (see PD-4).
  - `_on_failed` writes one `operator_alerts` row of kind `compile_failed` or `questions_failed`. It holds identifiers and counts only: job id, kind, attempts, `retry_failures`, `error_kind`, seal seq and doc_rev. The receipt is not touched, so v1 (`questions_pending`) stays the latest.
  - `reconcile()` recovers expired leases. It enqueues a compile job for every `submit` that lacks one, and a questions job for every pending v1 that has no v2. Both use idempotency keys, so a failed or finished job is never requeued.
- **`app/events_service.py`:** `add_seal_hook(fn)`. Hooks run **inside the submit transaction**, both for a new seal and for a replayed submit with the same idempotency key. A hook error rolls back the seal, so there is never a seal without scheduled work. Nothing in the hook calls a provider.
- **`app/receipt_service.py`:**
  - New `build_receipt` (no writes; compiles an explicit seal with `seal_seq`), `stored_receipt` (an explicit seal) and `store_artifacts`.
  - `issue_receipt` gains `seal_hash=None` and is otherwise unchanged. All T-018 tests pass unmodified.
- **`app/receipt_store.py`:** `store_artifacts_in_tx` (insert, skip an identical row, `ReceiptConflict` on a different one). `store_in_tx` now uses it for its artifact loop; its behaviour is unchanged.
- **`app/compile_service.py`:** extracted `ensure_alerts_table`, `insert_alert_in_tx` and `record_alerts`. `compile_log` and `list_alerts` are unchanged.
- **`app/main.py`:** `create_app(..., sources_for=None, start_job_loop=None)`.
  - `app.state.jobs` is always built, so every submit schedules durable work.
  - The lifespan runs the boot ping, then `reconcile()`.
  - A background loop (`run_pending` every 2 s, a daemon thread stopped on shutdown) starts only when a `sources_for` provider is given **and** either `start_job_loop=True` or `ROOM_JOB_LOOP=1`. See PD-1.
- **Tests:** `tests/test_compile_jobs.py` (new, 16 tests) and `tests/test_jobs_queue.py` (+16).
- **Board:** `docs/TASKS.md`, the T-020 row only.

Not touched: `shared/`, `design/`, `engine/`, `prototype/web/`, the kit, dependency files, and the shared tracking docs.

### Dropped from this branch: "Written on N days"

The founder's instruction was to drop the line. The worker did this in a separate commit (formerly `8f89918`). While I was working, main gained D-055 and **T-024**, which owns that change (`summary.py`, `copy.py`, golden outputs, the review README). The board says T-020 and T-024 must not edit each other's files. I therefore removed that commit when I rebased, and the line is **still present on this branch**.

The patch is two lines: delete `SUMMARY_DAYS`, and make the first sentence always `"Written " + src`. T-024 should do it with its own golden regression evidence.

## Receipt version and idempotency boundaries

- **Seal = one `submit` event.** Every job key and receipt key includes `seal_hash`. A resubmission makes a new seal with its own jobs and receipts, and earlier seals' receipts are unchanged (test j).
- **Scheduling:** the compile job is enqueued in the seal transaction. A retried submit with the same key re-enqueues with the same key, which is a no-op. `reconcile()` at boot covers seals that committed before this code ran, or without a hook.
- **Receipt key `(log_id, seal_hash, version)`; first issuance wins (D-053).**
  - **v1** is the L1 receipt, built with no model call. Its status is `questions_pending`, `complete` or `replay_mismatch`, exactly as `compile_receipt` decides. If v1 has no pending question, no v2 is scheduled.
  - **v2** is the question upgrade, built from the same seal, using stored artifacts.
  - Each version gets exactly one `receipt.issued`. Re-running a job, or a lease-expiry re-run, returns the stored bytes. The pre-check makes no model call.
- **Artifacts** are log-scoped. Partial answers from a failed v2 attempt are stored and reused by prompt hash on the retry.
- **Terminal failure** (the fifth retryable failure, or a permanent error): the job becomes `failed`, one alert is written, and the receipt stays v1. `reconcile()` does not requeue it.

## Tests run

Environment: macOS (Darwin 25.6.0), Python 3.14.5. The venv was built fresh in this worktree with `cd prototype && python3 -m venv .venv && .venv/bin/pip install --require-hashes -r requirements.lock`. All runs used `ROOM_LLM=stub`, with no live provider. I claim no CI result; the lock targets Python 3.12.

- `cd prototype && ROOM_LLM=stub .venv/bin/python -m pytest -q server/tests/test_compile_jobs.py server/tests/test_jobs_queue.py` → **74 passed** (run 3 times, passed every time).
- `cd prototype && ROOM_LLM=stub .venv/bin/python -m pytest -q` → **932 passed, 1 warning** (the existing Starlette/httpx deprecation). The baseline on main was 898.
- `cd writing-room-kit && ROOM_LLM=stub python3 -m pytest -q v04/tests web/tests` → **29 passed, 2 warnings**.
- `git diff --check main` is clean. A banned-word grep over the added lines has one hit, the existing `engine["flags"]` key in a test assertion. It is not user-facing.
- I made no UI change, so I did not run the web tests, typecheck/build or browser checks.

### Required evidence → test (`tests/test_compile_jobs.py` unless noted)

| Evidence | Test |
|---|---|
| Submit seals with the provider down | `test_provider_down_issues_v1_then_the_questions_job_retries` |
| Five retryable failures → failed, alert, questions pending (fake clock) | `test_retries_stop_after_five_tries_and_keep_v1`; queue: `test_retry_stops_after_five_attempts`, `test_custom_attempt_limit`, `test_on_failed_*` |
| A recovered lease uses no try | `test_jobs_queue.py` lease-expiry ×3 then 5 failures (attempts 8, retry_failures 5), the expiry-at-4-failures requeue test, and the compile-jobs lease-expiry test (alert `retry_failures == 5`) |
| Queued work survives a restart | `test_queued_work_survives_a_restart` (file DB, close and reopen) |
| No duplicate issuance on a repeated submit or job retry | `test_no_duplicate_issuance_across_retry_and_lease_recovery`, `test_a_retried_submit_after_such_a_crash_schedules_once` |
| Stored outputs are reused, so no extra calls | `test_stored_outputs_are_reused_and_a_finished_upgrade_asks_nothing` |
| L1 fallback, then the later question upgrade | `test_l1_fallback_is_upgraded_and_v1_is_unchanged` (v1 bytes unchanged; `verify` passes for v1 and v2) |
| Replay mismatch | `test_replay_mismatch_still_issues_v1_and_alerts` (browser copy, alert, engine stamp, `l3b` false) |
| Failure between commit and scheduling recovers | `test_a_seal_without_scheduling_is_recovered_and_issues_once`, `test_a_failing_seal_hook_rolls_the_submit_back` |
| No write transaction during a model call | `test_no_write_transaction_is_open_during_a_model_call` |
| Shared lock through HTTP | `test_http_submit_schedules_a_compile_job_on_the_shared_lock` |
| Permanent failure alert | `test_a_non_retryable_compile_failure_writes_a_compile_failed_alert` |
| Migration of a pre-D-054 jobs table | `test_jobs_queue.py` migration test |

### Lead mutation pass

I made each temporary edit, ran the two test files, then restored the file. `git status` was clean afterwards.

| Mutation | Result |
|---|---|
| No hook on a replayed submit | 1 failed |
| No hook on a new submit | 12 failed |
| Skip storing partial artifacts | 1 failed |
| Remove the retry cap | 7 failed |
| Skip `on_failed` | 7 failed |
| v1 calls the model | 5 failed |
| Skip replay alerts | 1 failed |
| Lease recovery counts as a try | 3 failed |

## EXPECTATIONS sections claimed

- **A:** all lines.
  - Scope is the ticket plus the D-054 cap.
  - `shared/llm.py` is unchanged.
  - There are no secrets or real data.
  - New behaviour has tests that fail when it breaks.
  - No new user-facing strings: alert kinds are internal codes, and receipt wording is unchanged.
  - No design doc changed.
- **B:** law 6 holds: a failure never changes a receipt into a verdict, and questions stay pending. Law 7 holds: the jobs and alerts store no timing and no text. The "Written on N days" line (law 7) is left to T-024, as described above.
- **C:** the seal and its whitelist are unchanged (only `receipt.issued` is appended after the seal), and `verify` passes for v1 and v2. Same log + same stamp + stored outputs gives byte-identical bytes, and stored receipts are returned unchanged.
- **H:** no data-line change. Withdrawal and release (9A/D10) remain T-021.
- **Not claimed:**
  - the M2 exit
  - L3a/b/c
  - the leak-checked L3 pipeline
  - release timing or the 48 h cap
  - withdrawal checks inside running handlers
  - mapper cancellation at submit (no mapper jobs exist)
  - any human or pilot gate

## Failures / open

- I saw no test failures.
- The app has no persisted store for source, Coach, import or helper text yet. Handlers therefore take an injected `sources_for(log_id)`, and the production app only schedules work: no loop runs until a provider is configured (PD-1).
- `create_app()` now calls `default_backend()` when it is built. An invalid `ROOM_LLM_BACKEND` therefore fails at app construction rather than later.
- `ensure_alerts_table` still uses `executescript`, which commits, so it must stay outside transactions. It is only called at construction.

## Proposed decisions (for the checker and founder; nothing here is decided)

- **PD-T020-1: the job loop waits for a sources provider.** Submits always schedule durable jobs, but `create_app` starts the in-process loop only with an injected `sources_for` and `ROOM_JOB_LOOP=1` (or `start_job_loop=True`). Compiling against empty sources would mark every non-typed run untraced. *Recommend:* accept. The ticket that persists source and Coach text supplies the provider.
- **PD-T020-2: receipt v1 is L1-only and is issued before questions.** v1 never calls a model and reuses no artifacts (`stored={}`). v2 is the upgrade. This follows architecture.md §3 step 7 ("receipt v1; L3 jobs → receipt v2"). Release decides which version the teacher sees (T-021). *Recommend:* accept.
- **PD-T020-3: scheduling is atomic with the seal.** Seal hooks run inside the submit transaction, so a scheduling error rolls the seal back and the student retries. The alternative is to commit the seal regardless and rely only on `reconcile()`. Neither path involves a provider, so CEO-7 holds. *Recommend:* accept.
- **PD-T020-4: rejected-twice questions still issue v2.** When the model is reachable but a question's output fails validation twice, v2 is issued under the compiler's existing rule (that question `q: null`, status `questions_pending`), and one `questions_incomplete` operator alert is written. The alternative is to fail the job and keep v1. The spec does not cover this case. *Recommend:* accept, because it gives the teacher the questions that did validate.
- **PD-T020-5: the backoff index follows `retry_failures`.** After a lease recovery the next backoff uses the count of retryable failures, not claims. Without recovery the schedule is identical. *Recommend:* accept, as consistent with D-054.
- **PD-T020-6: a permanent failure also alerts.** `on_failed` fires for every terminal failure (cap, permanent error, missing handler), not only at the cap. *Recommend:* accept.
- **PD-T020-7: the "Written on N days" overlap.** The removal belongs to T-024 (D-055), so I dropped it from this branch. *Recommend:* run T-024 as ticketed.

## Review follow-up (2026-10-25): reconcile paths tested

The coordinator's review found two untested paths: startup `reconcile()` in `main.py`, and the questions branch of `reconcile()`. Commit `cd7b1ff` closes both with tests only, written by a DeepSeek worker. No behaviour changed: `git diff` on `prototype/server/app` is empty for that commit.

Three tests were added to `tests/test_compile_jobs.py`:

- `test_startup_reconcile_schedules_a_seal_committed_without_a_job`:
  1. A file DB holds a seal that was committed with no `CompileJobs` attached.
  2. `create_app` is built, and before its lifespan no compile job exists.
  3. Entering `TestClient` creates exactly one queued `receipt.compile` job.
- `test_reconcile_schedules_questions_for_a_pending_v1_without_v2`:
  1. v1 is issued and its questions job row is removed.
  2. `reconcile()` creates exactly one `receipt.questions` job.
  3. A second `reconcile()` creates nothing.
  4. Once v2 is stored, `reconcile()` creates no questions job.
- `test_reconcile_recovers_an_expired_lease`: a claimed compile job whose lease has expired is `queued` again with no lease after `reconcile()`. The test does not call `claim()` before asserting, because `claim()` also recovers expired leases.

I checked each test against a deliberate break, using my own script. Each break restored the file afterwards, and `git status` was clean.

| Break | Test that failed |
|---|---|
| `app.state.jobs.reconcile()` → `pass` in `main.py` | 1 failed: `test_startup_reconcile_schedules_a_seal_committed_without_a_job` |
| `self.queue.recover_expired()` removed from `reconcile()` | 1 failed: `test_reconcile_recovers_an_expired_lease` |
| `continue` at the top of the pending-v1 loop in `reconcile()` | 1 failed: `test_reconcile_schedules_questions_for_a_pending_v1_without_v2` |

Results, same environment as above:

- `cd prototype && ROOM_LLM=stub .venv/bin/python -m pytest -q server/tests/test_compile_jobs.py` → **19 passed** (run 3 times)
- `cd prototype && ROOM_LLM=stub .venv/bin/python -m pytest -q` → **935 passed, 1 warning**
- `cd writing-room-kit && ROOM_LLM=stub python3 -m pytest -q v04/tests web/tests` → **29 passed, 2 warnings**

## Checker review

_Pending. Only the checker merges, marks done and updates shared tracking._
