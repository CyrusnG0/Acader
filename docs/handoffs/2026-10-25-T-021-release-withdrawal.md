# T-021: Release cap and transactional withdrawal

- **Worker:** worker-T-021 (continuation of a killed worker; reviewed and completed its uncommitted work)
- **Branch:** `task/T-021-release-withdrawal` (worktree `Acader-wt-T-021`)
- **Commits:** `87dd495` (implementation, tests, board row), plus the commit that adds this handoff.
- **Dependencies used:** T-018 (`delete_log_in_tx`), T-019 (`cancel_by_log(conn=)` with the shared lock), T-020 (`CompileJobs`, questions hook, job handlers, alerts), D-053/D-054.

## What changed

- **`prototype/server/app/lifecycle.py`** (new), `ReceiptLifecycle`.
  - On the seal, inside the submit transaction, records `release_records(log_id, seal_hash,
    tenant_id, owner_id, submit_at, deadline_at, base_at, cap_at, seal_seq, doc_rev, ...)`.
    `base = max(deadline, submit + 24h)`; `cap = base + 48h`; a missing deadline becomes the
    submit time. It enqueues `receipt.release` base and cap jobs with stable keys
    (`receipt.release:{log}:{seal}:{phase}`) using `JobQueue(..., conn=db)`.
  - `questions_ready(log, seal)` enqueues a questions-phase release job at
    `max(now, base)` after a complete receipt version commits. A hook failure is swallowed:
    the cap job remains the guarantee.
  - `handle_release` / `_release_in_tx` publish only when `now >= base` and the latest
    receipt has no pending questions, or when `now >= cap`. At the cap with pending
    questions it releases the newest stored version, records `release_cap` once, and leaves
    the receipt bytes unchanged. Repeated release returns the first state without events or
    alerts. Release is **not** a chain event (not in the post-seal whitelist); state lives in
    `release_records`.
  - If no receipt exists at the cap it records `release_no_receipt` and leaves the record
    unreleased; it never invents a receipt.
  - `teacher_view` requires an explicit `Identity(tenant, role, owner)` and returns only
    `{"status": "compiling", "ready_by": cap_at}` before release. After release it returns
    the released receipt, and any newer complete receipt's questions as
    `late_questions` with `added_after_release: true`. A tombstone returns
    `record_removed`.
  - `withdraw` requires an owning student identity and runs one caller-owned
    `BEGIN IMMEDIATE` transaction: append `record.withdrawn`, `cancel_by_log(...,
    conn=self.db)`, `delete_log_in_tx`, insert the `record_tombstones` row
    `(log_id, seal_hash, tenant_id, owner_id, withdrawn_at; no reason)` and mark the release
    rows withdrawn. Replays return the first event/timestamp and do not add an event. The
    student's free-text reason stays only in the chain event, never on the school side. A released record raises `AfterRelease` before any change. The event chain and
    submitted snapshots are never touched.
  - Constructor refuses a queue or receipt store that does not share
    `EventService.db` / `EventService._lock`.
- **`prototype/server/app/withdrawal.py`** (new): `is_withdrawn_in_tx` /
  `assert_not_withdrawn_in_tx` read `record.withdrawn` inside a caller-owned transaction and
  raise `RecordWithdrawn`.
- **`prototype/server/app/receipt_service.py`**: `_persist` and `store_artifacts` call
  `assert_not_withdrawn_in_tx` inside their publication transaction. A running compile or
  question job that finishes after withdrawal writes no receipt, artifact or event.
- **`prototype/server/app/compile_jobs.py`**: `add_questions_hook` /
  `_notify_questions_ready`, called only after a complete v1/v2 is stored. `_on_failed` now
  labels release failures `release_failed` (and other kinds `job_failed`) instead of calling
  every non-compile failure `questions_failed`.
- **`prototype/server/app/routes_events.py`**: the generic `POST /logs/{id}/events` entry
  point routes `record.withdrawn` through `lifecycle.withdraw`, so it cannot append the
  event without cancelling jobs and deleting outputs. Without a lifecycle it fails closed
  with 403 `access_denied`. Adds `POST /logs/{id}/withdraw` and 403/409 handlers for
  `AccessDenied`, `AfterRelease` and `LifecycleConflict`. Identity comes from an app-supplied
  `identity_for(log_id)` provider; this is a synthetic, already-authenticated identity, not
  an authentication layer or role selector.
- **`prototype/server/app/main.py`**: `create_app(..., deadline_for, scope_for,
  identity_for, enable_lifecycle)`. The lifecycle is opt-in (attached when a deadline/scope
  provider is given or `enable_lifecycle=True`), and the job loop's runner gets the release
  handler. Compile-only apps keep their previous behaviour.
- **`prototype/server/tests/test_release_withdrawal.py`** (new, 23 tests).
- **`prototype/server/tests/test_events_m1.py`**: one test adapted. `record.withdrawn` over
  the generic HTTP route now needs the lifecycle; the test still proves the event is
  whitelisted after the seal through `EventService.append_event`, and asserts the route's
  403 when no lifecycle is configured.
- **`docs/TASKS.md`**: only the T-021 row (`worker-T-021`, now `review`).

Not touched: `shared/`, `design/`, `engine/`, `prototype/web/`, the kit, dependency files,
other task rows or shared tracking docs.

## Tests run

Environment: macOS (Darwin 25.6.0), Python **3.14.5**, venv at `prototype/.venv` built from
`prototype/requirements.lock`; the kit used system Python 3.14.5. All runs used
`ROOM_LLM=stub`; no live provider, no secrets, no student data. **No CI result is claimed**;
the lock targets Python 3.12.

```
cd prototype && ROOM_LLM=stub .venv/bin/python -m pytest -q
  -> 970 passed, 1 warning (Starlette/httpx deprecation)
cd prototype && ROOM_LLM=stub .venv/bin/python -m pytest -q server/tests/test_release_withdrawal.py
  -> 23 passed (three consecutive runs)
cd writing-room-kit && ROOM_LLM=stub python3 -m pytest -q v04/tests web/tests
  -> 29 passed, 2 warnings
```

Baseline on this branch before the ticket's new tests was 935 prototype / 29 kit (T-020
handoff); the uncommitted T-021 work already accounted for the rest.

### Required evidence -> test (`tests/test_release_withdrawal.py`)

| Required evidence | Test |
|---|---|
| Frozen-clock deadline / submit + 24 h / +48 h cap boundaries | `test_deadline_later_than_24h_sets_base_and_release_waits_for_it`, `test_submit_plus_24h_sets_base_when_deadline_is_earlier`, `test_cap_releases_pending_questions_once_and_alerts_an_operator` |
| Outage, then late questions | `test_outage_then_questions_arrive_before_cap_and_release_early`, `test_outage_through_cap_late_questions_are_marked_added_after_release` |
| Duplicate release | `test_duplicate_release_does_not_change_state_alerts_or_events` |
| Withdrawal races with queued and running completion/release | `test_withdrawal_cancels_work_deletes_unreleased_outputs_and_keeps_submitted_work`, `test_a_running_compile_cannot_publish_after_withdrawal`, `test_partial_question_outputs_cannot_be_stored_after_withdrawal`, `test_a_running_release_cannot_publish_after_withdrawal` |
| Rollback atomicity | `test_withdrawal_rolls_back_atomically_when_cancellation_fails` |
| Generic events route cannot bypass cancellation | `test_generic_events_route_cannot_bypass_cancellation_and_deletion`, `test_generic_events_route_fails_closed_without_lifecycle` |
| No teacher payload before release | `test_no_teacher_receipt_contents_before_release` |
| Cross-log access rejection | `test_cross_log_and_cross_tenant_access_is_rejected` (wrong owner, wrong tenant with the same owner, wrong role, unknown log, and the other log left untouched) |
| Other covered branches | `test_cap_with_no_receipt_alerts_and_never_invents_one`, `test_repeated_withdrawal_is_idempotent_and_keeps_one_event`, `test_a_failed_release_job_alerts_as_release_not_questions`, `test_lifecycle_refuses_a_queue_that_does_not_share_the_event_lock`, `test_dedicated_withdrawal_route_and_fail_closed_identity`, `test_withdrawal_route_after_release_returns_after_release`, `test_release_loop_runs_release_jobs_through_the_app_runner` |

## Mutation checks (temporary edits, all restored)

Script `/tmp/mutate_t021.py` applied each break, ran the named test, and restored the file.
`git status` was clean afterwards. **All 22 mutations failed the tests as expected.**

| Break | Test that failed |
|---|---|
| Ignore the deadline in `base` | deadline test |
| Set the 24 h delay to 1 h | submit + 24 h test |
| Set the cap to 47 h | cap test |
| Remove the pre-base wait | deadline test |
| Remove the pending-questions wait through the cap | cap test |
| Remove both duplicate-release guards (early return and `released_at IS NULL`) | duplicate-release test |
| Do not mark late questions | late-questions test |
| Force `_questions_ready` false | early-release-after-outage test |
| Remove the withdrawn check in `_persist` | running-compile test |
| Remove the withdrawn check in `store_artifacts` | partial-question test |
| Remove the withdrawn check in release | running-release test |
| Skip `cancel_by_log` | withdrawal test |
| Skip `delete_log_in_tx` | withdrawal test |
| Skip the tombstone insert | withdrawal test |
| Disable the generic-route interception | both generic-route tests |
| Remove the pre-release early return | no-payload-before-release test |
| Remove the tenant check | cross-tenant test |
| Remove the owner check | cross-owner test |
| Remove the withdrawal transaction | rollback test |
| Skip the cap alert | cap test |
| Remove the no-receipt branch | no-receipt test |
| Remove the replayed-withdrawal branch | repeated-withdrawal test |

`git diff --check` is clean. A banned-word grep over the new files and added lines has no
user-facing hit; the only match is the test comment "identifiers and flags only" (not
copy).

## EXPECTATIONS sections claimed

- **A:** all lines. Scope is the ticket; `shared/llm.py`, design docs, the kit and
  `prototype/web/` are untouched; no secrets or real data; new behaviour has tests; the
  handoff is present. The only change outside the new files is the documented route
  behaviour and its one existing test.
- **B:** law 6 holds (the tombstone is neutral and says the work is unchanged, not a
  verdict); law 7 holds (no new timing or typing data; only chain event timestamps and
  `withdrawn_at`); the receipt is never blocked or altered by a withdrawal choice.
- **C:** the seal and whitelist are unchanged; `record.withdrawn` is whitelisted and
  `verify` passes after withdrawal. Receipt/artifact deletion removes rows only, never the
  chain. Stored-output rebuild and receipt bytes are unchanged (T-018/T-020 tests pass
  unmodified).
- **H:** the withdrawal line's service side: queued jobs cancelled, unreleased receipts and
  outputs deleted, never released, teacher-side tombstone. The exact UI notices and receipt
  rendering belong to T-022; the pre-release teacher state is only `compiling` + `ready_by`.

Not claimed: M1–M5 gates, student preview, the receipt UI, real authentication, mapper
cancellation (no mapper jobs exist; `cancel_by_log` will cover them when they do), or any
pilot gate.

## Failures / open

- No test failures. One self-inflicted test failure was fixed while adding the fail-closed
  route test (the request needed an explicit `payload`), then all runs passed.
- The previous worker's uncommitted test file imported and passed before review; gaps fixed
  here were the missing lifecycle-disabled route case and the untested no-receipt and
  replayed-withdrawal branches.
- There is no reconciliation/backfill for `release_records` on a database whose seals
  predate the lifecycle being attached. In production the lifecycle must be attached before
  the first submit; a later enablement needs a follow-up.
- Identity, deadline and record scope are all injected providers. The real roster/magic-link
  layer is not built and this ticket does not authenticate anyone.
- The teacher view does not render the notices or mark post-release notes; T-022 owns that.
- Late questions are marked at view time (`added_after_release: true`), not written into the
  receipt bytes. That keeps the released receipt immutable and verifiable.

## Proposed decisions (checker takes these to the founder; nothing here is decided)

- **PD-T021-1: release is not a chain event.** The post-seal whitelist has no release event,
  so release state lives in `release_records`; the receipt stays sealed and verifiable.
  *Recommend:* accept.
- **PD-T021-2: `ready_by` before release is the cap time.** The teacher's "Ready by [time]"
  is `max(deadline, submit + 24 h) + 48 h`, the guaranteed time, not the base. T-022 can
  word it; the service returns exactly the guarantee. *Recommend:* accept.
- **PD-T021-3: the cap never invents a receipt.** If nothing was compiled by the cap, the
  operator gets `release_no_receipt` and the record stays unreleased so a later compile can
  still release. This is the only case where the cap guarantee is missed, and it is already
  a compile failure. The alternative is releasing an explicit error state. *Recommend:*
  accept.
- **PD-T021-4: the lifecycle is opt-in and the generic route fails closed without it.**
  `create_app` attaches it only with a deadline/scope provider (or explicitly); compile-only
  apps keep their scheduling. A `record.withdrawn` sent to the generic route on such an app
  now returns 403 instead of appending a bare event, because a bare event cannot cancel
  queued work or delete outputs. The event whitelist itself still permits the event through
  the service. The existing M1 test was adapted to this. *Recommend:* accept.
- **PD-T021-5: after-release removal is refused.** It returns 409 `after_release` and
  changes nothing; the ticket explicitly says it must not become the before-release
  operation, and there is no new deletion policy. *Recommend:* accept.
- **PD-T021-6: repeated withdrawal is idempotent.** It returns the first
  `record.withdrawn` event and timestamp, does not append a second event, and re-runs the
  cancellation/deletion cleanup. *Recommend:* accept.

## Review follow-up (2026-10-25)

Two fixes from the coordinator's review, both with the guarded line checked by breaking it
and restoring it:

1. **Tenant-only withdrawal rejection is tested.** `test_cross_log_and_cross_tenant_access_is_rejected`
   adds `Identity("tenant-2", "student", OWNER)` (same owner, other tenant). Deleting the
   tenant half of the withdraw check made that test fail; the check was restored.
2. **No withdrawal reason on the school side.** `record_tombstones` no longer has a `reason`
   column and the insert no longer writes one; the reason remains only in the student's
   `record.withdrawn` payload. `test_repeated_withdrawal_is_idempotent_and_keeps_one_event`
   asserts the mapped row has no `reason`, the table has no such column (`PRAGMA
   table_info`), and the chain event carries it. Restoring the column made the test fail; it
   was removed again.

Results after the fixes: T-021 **23 passed**, full prototype **970 passed**, kit **29
passed** (same commands/environment above).

## Checker review

_Pending. Only the checker merges, marks done and updates shared tracking._
