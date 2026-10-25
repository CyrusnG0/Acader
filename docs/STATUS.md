# Current Status

**Last updated:** 2026-10-25 (checker: T-020, T-021, T-024 merged; D-058; OL-052…OL-057)
**Phase:** prototype v1; M1 engineering complete, human reading gate open. M2 service layer done through release and withdrawal (T-018…T-021); student preview and teacher views (T-022) wait on a founder answer.

## What works

- T-001…T-006, T-008, T-010…T-017: scaffold, schema, replay, events/seal, L1 provenance, compiler, twelve synthetic golden sessions, DESIGN.md (D-052) and the twelve-receipt renderer with chain navigation.
- **T-018** durable receipts and AI artifacts (D-053). **T-019** bounded durable job queue (D-054).
- **T-020** submit and compile orchestration: compile job scheduled inside the seal transaction, receipt v1 (L1, no model call) then v2 (questions), five-try retry cap with questions pending and an operator alert (D-054), startup reconcile.
- **T-021** release cap and transactional withdrawal: release at `max(deadline, submit + 24 h)` when questions are ready, forced at +48 h; release state in `release_records`, not the chain; withdrawal appends `record.withdrawn`, cancels queued work and deletes unreleased outputs in one transaction; teacher-side tombstone with no reason text (D-058).
- **T-024** "Written on N days" removed from the receipt summary (D-055).
- **T-007** S3/S4 preregistration (D-056) and **T-009** walkthrough + blind-question preregistration (D-057). Documents only; nothing run.
- **[VALIDATED]** Merged main 9f5a874: prototype suite 970 passed, 1 warning (`ROOM_LLM=stub`, fresh `--require-hashes` venv, local Python 3.14.5). CI covers 3.12; no new CI result claimed here.

## In progress

None.

## Single next action

**Founder answers OL-049 (student preview section order)**, which is the only thing blocking T-022 (student preview and teacher lifecycle views).

## Outstanding and boundaries

- A person must read at least ten rendered receipts before M1 is complete (T-017 handoff list).
- T-022 blocked on OL-049 only. T-023 blocked on OL-050 (PD-T007-4 `claim_compare` schema + S3 prompt).
- Founder decisions owed: OL-049; OL-050 (T-007, T-009, T-019, T-020 PDs); OL-047 (T-015/T-016 PDs); OL-051 (S3 people, S4 v2); OL-052 "Ready by" shows the cap time; OL-053 nothing compiled by the cap leaves the record `compiling` indefinitely (a real gap); OL-054 refuse removal after release.
- Engineering follow-ups, not yet ticketed: OL-055 alerts after withdrawal; OL-056 runner `worker_id` and release handler wiring; OL-057 invalid `ROOM_LLM_BACKEND` stops `create_app`.
- No `release_records` backfill for seals made before the lifecycle is attached; identity, deadline and scope are injected providers, not a real authentication layer (T-021 handoff).
- OL-046 mapper corpus/labels. L3b and mapper stay off absent their gates. No production release or real student access. Kit results remain simulated; shared/llm.py unchanged; code track parked.

## Founder actions / pilot blockers

- Read at least ten rendered receipts and record reader/date/cases.
- Answer OL-049, OL-050, OL-052…OL-054 and OL-047; name the people in OL-051.
- F-001 schedule; F-002 / OL-036 named teacher, class and assignment window by **2026-10-30**.
- F-003 / OL-037 / OL-026 school/provider/processor and ethics approvals; teacher participation for T-009.
- No real student before design/build-plan.md §4 is green.

Latest reviews: handoffs dated 2026-10-25 for T-020, T-021, T-024 (each has a Checker review section). Product intent: PRODUCT.md and later decisions. Specs: design/README.md. Board: TASKS.md.
