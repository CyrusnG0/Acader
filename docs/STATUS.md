# Current Status

**Last updated:** 2026-10-25 (founder decisions D-059…D-062; tickets T-025…T-027; T-022 unblocked)
**Phase:** prototype v1; M1 engineering complete, human reading gate open. M2 service layer done through release (T-018…T-021). Founder reversed student withdrawal (D-062); four M2 tickets are ready.

## What works

- T-001…T-006, T-008, T-010…T-017: scaffold, schema, replay, events/seal, L1 provenance, compiler, twelve synthetic golden sessions, DESIGN.md (D-052) and the twelve-receipt renderer with chain navigation.
- **T-018** durable receipts and AI artifacts (D-053). **T-019** bounded durable job queue (D-054).
- **T-020** submit and compile orchestration: compile job scheduled inside the seal transaction, receipt v1 (L1, no model call) then v2 (questions), five-try retry cap with questions pending and an operator alert (D-054), startup reconcile.
- **T-021** release cap and transactional withdrawal (withdrawal now reversed by D-062, code removal is T-025): release at `max(deadline, submit + 24 h)` when questions are ready, forced at +48 h; release state in `release_records`, not the chain; withdrawal appends `record.withdrawn`, cancels queued work and deletes unreleased outputs in one transaction; teacher-side tombstone with no reason text (D-058).
- **T-024** "Written on N days" removed from the receipt summary (D-055).
- **T-007** S3/S4 preregistration (D-056) and **T-009** walkthrough + blind-question preregistration (D-057). Documents only; nothing run.
- **[VALIDATED]** Merged main 9f5a874: prototype suite 970 passed, 1 warning (`ROOM_LLM=stub`, fresh `--require-hashes` venv, local Python 3.14.5). CI covers 3.12; no new CI result claimed here.

## In progress

None.

## Single next action

**Start T-025 (remove student withdrawal, D-062)**; it clears `app/lifecycle.py` for T-026 (delayed state + re-check) and then T-022 (preview and teacher views). T-027 ("More places to ask") can run in parallel.

## Outstanding and boundaries

- A person must read at least ten rendered receipts before M1 is complete (T-017 handoff list).
- Founder decisions 2026-10-25: preview = teacher first screen, same order (D-059); "More places to ask" candidate list (D-060); "Ready by" = cap, plus a `delayed` state and re-check (D-061); students cannot remove the process record (D-062). Ready: T-025, T-026, T-022, T-027. T-023 blocked on OL-050.
- Founder decisions owed: OL-058 (confirm law 7 wording in CLAUDE.md §4 / PRODUCT.md §6 and the deletion-on-request / retention rule; D-062 proposes wording, not applied); OL-059 (does the student preview list the "More places" parts); OL-050 (T-007, T-009, T-019, T-020 PDs); OL-047 (T-015/T-016 PDs); OL-051 (S3 people, S4 v2).
- Engineering follow-ups, not yet ticketed: OL-056 runner `worker_id` and release handler wiring; OL-057 invalid `ROOM_LLM_BACKEND` stops `create_app`. OL-055 closed as moot (D-062).
- No `release_records` backfill for seals made before the lifecycle is attached; identity, deadline and scope are injected providers, not a real authentication layer (T-021 handoff).
- OL-046 mapper corpus/labels. L3b and mapper stay off absent their gates. No production release or real student access. Kit results remain simulated; shared/llm.py unchanged; code track parked.

## Founder actions / pilot blockers

- Read at least ten rendered receipts and record reader/date/cases.
- Confirm the law 7 wording and retention rule (OL-058); answer OL-059, OL-050 and OL-047; name the people in OL-051.
- F-001 schedule; F-002 / OL-036 named teacher, class and assignment window by **2026-10-30**.
- F-003 / OL-037 / OL-026 school/provider/processor and ethics approvals; teacher participation for T-009.
- No real student before design/build-plan.md §4 is green.

Latest reviews: handoffs dated 2026-10-25 for T-020, T-021, T-024 (each has a Checker review section). Product intent: PRODUCT.md and later decisions. Specs: design/README.md. Board: TASKS.md.
