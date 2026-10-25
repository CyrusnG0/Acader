# Current Status

**Last updated:** 2026-10-25 (T-025, T-027, T-028 merged; founder decision D-063; ticket T-029)
**Phase:** prototype v1; M1 engineering complete, human reading gate open. M2 service layer done through release (T-018…T-021), withdrawal removed (T-025), "More places to ask" built (T-027). Hardening T-028 done (engine `receipt/1 l1/2`); T-029, T-026, T-022 ready.

## What works

- T-001…T-006, T-008, T-010…T-017: scaffold, schema, replay, events/seal, L1 provenance, compiler, twelve synthetic golden sessions, DESIGN.md (D-052) and the twelve-receipt renderer with chain navigation.
- **T-018** durable receipts and AI artifacts (D-053). **T-019** bounded durable job queue (D-054).
- **T-020** submit and compile orchestration: compile job scheduled inside the seal transaction, receipt v1 (L1, no model call) then v2 (questions), five-try retry cap with questions pending and an operator alert (D-054), startup reconcile.
- **T-021** release cap: release at `max(deadline, submit + 24 h)` when questions are ready, forced at +48 h; release state in `release_records`, not the chain (D-058).
- **T-025** student withdrawal removed (D-062): no `/withdraw` route, no tombstone, `record.withdrawn` off the post-seal whitelist; the chain stays append-only. A sealed log answers 409 `sealed` to any event type a client may not send (D-063).
- **T-027** "More places to ask" (D-060): every grounded non-chosen candidate kept in receipt field `more_places` (inside `receipt_hash`, paragraph order, one per paragraph, no generated wording, no provider call) and rendered in one closed disclosure under the questions, open in print. Teacher receipt only.
- **T-024** "Written on N days" removed (D-055). **T-007** S3/S4 preregistration (D-056) and **T-009** walkthrough + blind-question preregistration (D-057); documents only, nothing run.
- **[VALIDATED]** Merged main (T-025, T-027, then T-028), Opus review MERGE with no blockers on each: checker re-ran merged main from a fresh clone and `--require-hashes` venv (Python 3.14.5, `ROOM_LLM=stub`): prototype 996 passed. The reviewers' per-branch runs: T-027 alone 1006 / kit 29 / web 150 with typecheck clean. T-025 alone, fresh `--require-hashes` venv, Python 3.14.5: 960 / 29 / 145; its whitelist, 24 h and 48 h mutations fail tests. T-027: 6 of 7 review mutations fail tests (the survivor is fixed in T-028). CI covers 3.12; no new CI result claimed. Local main is not yet pushed; the checker pushes.

## In progress

Nothing. No worker is running and no worktree holds unmerged work (T-025, T-027, T-028 are merged).

## Single next action

**Dispatch T-029 (`more_places` artifact ids) and T-026 (delayed state + re-check), then T-022 (student preview and teacher views).** Only T-026 must land before T-022 (both edit `app/lifecycle.py`); T-029 is independent of both. T-022 must add a real student-preview boundary test (OL-061) and leaves the More places parts out of the preview until OL-059 is answered.

## Founder decisions open

- OL-058: confirm law 7 wording (CLAUDE.md §4 / PRODUCT.md §6; D-062 proposes wording, not applied), unsubmitted drafts, deletion on request, retention.
- OL-059: does the student preview list the "More places to ask" parts (blocks that part of T-022).
- OL-050: T-007, T-009, T-019, T-020 proposed decisions and the S3 prompt (T-023 blocked on PD-T007-4). OL-051: S3/S4 people and S4 v2. OL-047: T-015/T-016 proposed decisions.
- F-001 schedule; F-002 / OL-036 named teacher, class and assignment window by **2026-10-30**; F-003 / OL-037 / OL-026 approvals; F-004 designer key.
- Read at least ten rendered receipts and record reader, date and cases (M1 human gate).

## Outstanding and boundaries

- Engineering follow-ups: OL-056 runner `worker_id` and release handler wiring; OL-057 invalid `ROOM_LLM_BACKEND` stops `create_app`; OL-060 wipe T-021-era dev databases holding `record.withdrawn`; OL-062 receipt_store.py:182 lint. One T-025 refusal test passes even with the whitelist restored; two others cover it.
- No `release_records` backfill for seals made before the lifecycle is attached; identity, deadline and scope are injected providers, not a real authentication layer.
- OL-046 mapper corpus/labels. L3b and mapper stay off absent their gates. No production release or real student before design/build-plan.md §4 is green. Kit results remain simulated; shared/llm.py unchanged; code track parked.
- Housekeeping 2026-10-25: 17 merged worktrees and old `/private/tmp` scratch removed; branches kept.

Latest reviews: handoffs 2026-10-25 for T-025 and T-027. Product intent: PRODUCT.md and later decisions. Specs: design/README.md. Board: TASKS.md.
