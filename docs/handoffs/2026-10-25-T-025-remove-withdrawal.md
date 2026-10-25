# T-025: Remove student withdrawal (D-062)

- **Worker:** worker-T-025
- **Branch:** `task/T-025-remove-withdrawal` (worktree `Acader-wt-T-025`)
- **Commits:** implementation + this handoff (single commit on the branch; checker merges).
- **Dependencies used:** T-021 (release/withdrawal build), T-018 (`ReceiptStore`), T-019
  (`cancel_by_log`), D-053/D-058 (amended), D-062.

## What changed

- **`prototype/server/app/lifecycle.py`**: removed `withdraw`, `_withdrawal_event`,
  `is_withdrawn`, `_tombstone`/`_tombstone_row`, `record_tombstones`, the
  `release_records.withdrawn_at` column, the `AfterRelease` exception and every
  withdrawn/tombstone branch in `questions_ready`, `_release_in_tx` and `teacher_view`.
  Release scheduling, the base/cap rule, `release_records`, `release_kind`, alerts and
  `teacher_view` are unchanged otherwise.
- **`prototype/server/app/routes_events.py`**: removed `POST /logs/{id}/withdraw`,
  `WithdrawBody`, the `record.withdrawn` branch of the generic events route, the
  `record.withdrawn` entry in `CLIENT_EVENT_TYPES`, the lifecycle/identity lookups and the
  `after_release` error handler. Unknown event types on a sealed log now return 409
  (`{"error": "sealed"}`) before the client-type check; unsealed logs still return 422
  `type_not_allowed`.
- **`prototype/server/app/receipt_service.py`**: removed the `app.withdrawal` import and the
  two `assert_not_withdrawn_in_tx` calls; publication no longer checks withdrawal.
- **`prototype/server/app/withdrawal.py`**: deleted.
- **`prototype/server/app/receipt_store.py`**: removed `delete_log_in_tx`/`delete_log`
  (withdrawal was the only production caller; no deletion path remains under D-062).
- **`prototype/server/app/main.py`**: removed the withdrawal-only `identity_for` parameter
  and app state; release lifecycle attachment is unchanged.
- **`prototype/server/app/jobs/{queue,__init__}.py`**: docstrings no longer describe
  withdrawal; `cancel_by_log` and its tests are kept (generic queue tooling).
- **`prototype/server/engine/events/chain.py`**: `record.withdrawn` removed from
  `POST_SEAL_WHITELIST`; the store now refuses it after a seal with `SealedError`.
- **Tests**: `tests/test_release_withdrawal.py` renamed to `tests/test_release.py` with the
  release tests kept, withdrawal tests deleted (refusal tests added instead), and the
  cross-log test narrowed to `teacher_view`. `test_events_m1.py`, `test_events_s5.py`,
  `test_jobs_queue.py` and `test_receipt_store.py` updated as described below.
- **Stale docs**: removed withdrawal from `prototype/web/review/README.md` and the S5 result
  whitelist (both are non-design prototype docs, updated so `grep` shows only refusal tests).
- **`docs/TASKS.md`**: only the T-025 row, owner `worker-T-025`, status `review`.

The event chain is append-only; no deletion or rewrite path was added. No golden or fixture
contained `record.withdrawn`, so none was regenerated. `verify` needed no legacy tolerance.

## Tests run (actual environments; no CI claimed)

Environment: macOS Darwin 25.6.0, system Python 3.14.5 (no prototype `.venv` in this
worktree), all runs `ROOM_LLM=stub`; no secrets, real student data or live provider calls.

```
cd prototype && ROOM_LLM=stub python3 -m pytest -q
  -> 960 passed, 2 warnings (7 s)
cd prototype && ROOM_LLM=stub python3 -m pytest -q server/tests/test_release.py \
    server/tests/test_events_s5.py::test_store_refuses_withdrawal_after_the_seal \
    server/tests/test_events_m1.py::test_whitelist_after_seal
  -> 16 passed
cd writing-room-kit && ROOM_LLM=stub python3 -m pytest -q v04/tests web/tests
  -> 29 passed, 2 warnings
```

**Test count change: 970 -> 960 (net -10).** Removed 12 tests (11 withdrawal behaviour tests
in the renamed file plus `test_transactional_deletion_can_roll_back_or_commit`), added 3
refusal tests (`test_withdrawal_route_is_gone`,
`test_generic_events_route_refuses_withdrawal_after_the_seal`,
`test_store_refuses_withdrawal_after_the_seal`), and the parametrised
`test_whitelisted_post_seal_events_verify` now covers one fewer whitelist entry because
`record.withdrawn` left the whitelist.

One failure during development: `test_outage_through_cap_late_questions_are_marked_added_after_release`
needed the `KIND_QUESTIONS` import retained; fixed. Final suite green.

## Required evidence -> test

| Required evidence | Test |
|---|---|
| `record.withdrawn` after the seal -> 409 on the generic route | `test_release.py::test_generic_events_route_refuses_withdrawal_after_the_seal`, `test_events_m1.py::test_whitelist_after_seal` |
| ... and from the store | `test_events_s5.py::test_store_refuses_withdrawal_after_the_seal` (also `test_whitelist_after_seal` via `EventService.append_event`) |
| No `/withdraw` route | `test_release.py::test_withdrawal_route_is_gone` (404) |
| Release still at base/cap with frozen clocks | `test_deadline_later_than_24h_sets_base_and_release_waits_for_it`, `test_submit_plus_24h_sets_base_when_deadline_is_earlier`, `test_cap_releases_pending_questions_once_and_alerts_an_operator` |
| Duplicate release still idempotent | `test_duplicate_release_does_not_change_state_alerts_or_events` |
| No teacher payload before release | `test_no_teacher_receipt_contents_before_release` |
| Cross-log access still rejected | `test_cross_log_and_cross_tenant_access_is_rejected` |
| `grep -rn withdraw prototype/` | Only refusal-test names remain under `prototype/server/tests/`; no non-test hit (the two stale prototype docs were corrected). |

## Mutation checks (temporary edits, all restored; `git status` clean after)

| Break | Test that failed |
|---|---|
| Re-add `record.withdrawn` to `POST_SEAL_WHITELIST` | `test_store_refuses_withdrawal_after_the_seal`, `test_whitelist_after_seal` (2 failed) |
| Drop the sealed-precedence branch in `post_event` | `test_generic_events_route_refuses_withdrawal_after_the_seal` |
| Re-add a `/logs/{id}/withdraw` route | `test_withdrawal_route_is_gone` |
| Release delay 24 h -> 1 h | `test_submit_plus_24h_sets_base_when_deadline_is_earlier` |
| Cap 48 h -> 47 h | `test_cap_releases_pending_questions_once_and_alerts_an_operator` |
| Remove both duplicate-release guards (early return and `released_at IS NULL`) | `test_duplicate_release_does_not_change_state_alerts_or_events` |
| Remove the pre-release early return in `teacher_view` | `test_no_teacher_receipt_contents_before_release` |
| Remove the tenant check in `_require_teacher` | `test_cross_log_and_cross_tenant_access_is_rejected` |

## EXPECTATIONS claimed

- **A**: task scope followed; full prototype and kit suites green under `ROOM_LLM=stub`; each
  required behaviour has a test that fails when its guarded line is broken; `shared/llm.py`
  untouched; no secrets or student data; no banned words in user-facing strings; no design
  doc changed; this handoff.
- **C**: the seal and post-seal whitelist rule (D8) now excludes `record.withdrawn`; the
  store refuses it and `verify` needs no legacy tolerance.
- **H**: the receipt has no student-removal path (D-062); this ticket removes the backend
  path only (T-022 owns the views).

## Proposed decisions

- **PD-T025-1:** The generic events route now answers 409 `sealed` for *any* unknown type on
  a sealed log (before the 422 `type_not_allowed` client-type check). This is the smallest
  way to satisfy "409 on the generic route" after removing `record.withdrawn` from the
  accepted list; unsealed logs keep 422, and existing whitelisted-type behaviour is
  unchanged. No product wording or user-facing copy is involved.
- **PD-T025-2:** `ReceiptStore.delete_log` was removed with `delete_log_in_tx` because the
  latter was withdrawal's only production caller and no deletion path should remain under
  D-062. Deletion on request and school-retention contracts stay open in OL-058; if a
  retention job needs a scoped delete later, it should be designed there rather than
  restored from this code.
- **PD-T025-3:** The withdrawal-only `identity_for` parameter was removed from `create_app`.
  T-022's student preview / teacher views will need an identity or view-context provider;
  reintroduce it there with that ticket's contract rather than keeping an unused hook.
- **PD-T025-4:** Two non-design prototype docs (`prototype/web/review/README.md`,
  `prototype/spikes/S5/RESULT.md`) still mentioned withdrawal after the checker's doc pass.
  They were corrected minimally so the required grep has no non-test hit; no design doc,
  DECISIONS, STATUS, CHANGELOG or OPEN_LOOPS file was edited.
