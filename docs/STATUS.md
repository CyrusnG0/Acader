# Current Status

**Last updated:** 2026-10-25 (T-007/T-009/T-018/T-019 checker review; founder answers D-053…D-057)
**Phase:** prototype v1; M1 engineering complete, human reading gate open. M2 infrastructure under way (storage and queue done; orchestration next).

## What works

- T-001…T-006, T-008, T-010…T-017: scaffold, schema, replay, events/seal, L1 provenance, compiler, twelve synthetic golden sessions, DESIGN.md (D-052) and the twelve-receipt renderer with chain navigation.
- **T-018** durable receipts and AI artifacts (first issuance wins, transactional deletion that never touches the chain; D-053).
- **T-019** bounded durable job queue (lease fencing, four per backend, least-served first, 1/4/16 backoff, cancel by log, shared connection lock; D-054).
- **T-007** S3/S4 preregistration (S3 bar, labelling and both-backends rule accepted, D-056) and **T-009** nursing walkthrough + blind-question preregistration (win rule accepted, D-057). Documents only; no evaluation run, no participant.
- **[VALIDATED]** Merged main after all four: prototype suite 898 passed (`ROOM_LLM=stub`, local Python 3.14.5). Kit 29 per the handoffs. No new CI result claimed.

## Single next action

**Claim T-020 (submit and compile orchestration)**, which now includes the five-try retry cap with questions pending and an operator alert (D-054). T-024 (drop "Written on N days", D-055) is small and may run in parallel.

## Outstanding and boundaries

- A person must read at least ten rendered receipts before M1 is complete (T-017 handoff list).
- T-021, T-022 and T-023 remain blocked. T-023 needs T-007 PD-4 (`claim_compare` schema) and S3 prompt approval (OL-050).
- OL-050: proposed decisions not yet asked (T-007 PD-4/6/7/8 + S3 prompt; T-009 PD-3…8, 10; T-019 PD-3…7).
- OL-051: name the S3 labeller, second annotator and adjudicator (a named second labeller is still owed); revise S4 to s4-prereg-v2 because band 4 does not count as traced for C1 (D-056).
- OL-047: T-015 PD1–3, 5–6 and T-016 PD1–4, 6–9 still await the founder (T-016 PD5 decided: D-055).
- OL-049 preview order before T-022; OL-046 mapper corpus/labels. L3b and mapper stay off absent their gates.
- No production release, student preview or access workflow. Kit results remain simulated; shared/llm.py unchanged; code track parked.

## Founder actions / pilot blockers

- Read at least ten rendered receipts and record reader/date/cases.
- Answer OL-050 and OL-047; name the people in OL-051.
- F-001 schedule; F-002 / OL-036 named teacher, class and assignment window by **2026-10-30**.
- F-003 / OL-037 / OL-026 school/provider/processor and ethics approvals; teacher participation for T-009.
- No real student before design/build-plan.md §4 is green.

Latest reviews: handoffs dated 2026-10-25 for T-007, T-009, T-018, T-019 (each has a Checker review section). Product intent: PRODUCT.md and later decisions. Specs: design/README.md. Board: TASKS.md.
