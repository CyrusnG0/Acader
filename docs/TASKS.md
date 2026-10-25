# TASKS.md: the task board

One task = one lead conversation. A cold worker may pick **any unowned `ready` task whose dependencies are `done`**. Read the [pickup instructions and executable tickets](tickets/README.md), then write your conversation tag in **Owner** and set only your task to `in progress` before starting. Coordinate claims: edits on separate branches alone do not prevent duplicate ownership. Codex is the planner/checker; the founder supplies implementation workers.

**Recommended next pickup: T-018 (receipt storage) or T-019 (job queue).** Both are unowned and ready with separate file boundaries. T-007/T-009 remain independently ready. T-010/T-017 passed checker review; M1 still needs a person to read at least ten receipts. Synthetic infrastructure work may proceed while that gate is open; this is not M1 completion or permission for real student use.

**Only the checker changes a status to `done`.** A lead sets `review` and writes a handoff (docs/handoffs/). The checker reviews it against [EXPECTATIONS.md](../EXPECTATIONS.md).

Statuses: `ready` · `blocked` (dependency not done) · `in progress` · `review` (handoff written) · `done` (checker passed) · `founder` (needs the founder, not an agent).

Model hint: **S** = Sonnet worker is fine · **D** = DeepSeek worker is fine (well-specified, mechanical, no wording or design choices) · **O** = keep with the Opus lead (judgment, wording, prompts).

## Now: M0 (build-plan.md, ~10-24 → 10-28)

| ID | Task | Read first | Done when (EXPECTATIONS) | Depends on | Model | Owner | Status |
|---|---|---|---|---|---|---|---|
| T-001 | Scaffold `prototype/` per architecture.md §6 (server/app, engine, sources, coach, mapper, trail, tests; web Vite+TS; fixtures; spikes) + CI that runs prototype tests and the kit's 29 | architecture.md §4, §6 | A; I-M0 (scaffold + CI) | — | D/S | lead-opus-T001 | done |
| T-002 | `web/schema.json`: origin marks (closed list), claim mark `{claim_id, by}` with optional `suggestion_id` | event-log.md §4 | A; C (typed rules) | T-001 | S | lead-opus-T002 | done |
| T-003 | LLM boundary `complete(task, messages, schema)` wrapping `shared/llm.py`: stub, error classes, boot ping, backend-2 slot, task enum incl. `map_suggest`; plus a Python lock file that CI installs (D-040) | architecture.md §5 | A (shared/llm.py unchanged) | T-001 | S | lead-opus-T003 | done |
| T-004 | Spike S1 (widened): TipTap marks + input plugin + Python replay parity; write the go/no-go note | evaluation.md §1, event-log.md §4 | A; C (typed rules); I-M0 (S1 written) | T-001, T-002 | O+S | lead-opus-T004 | done |
| T-005 | Spike S5: tamper-evident log, seal, whitelist, verify | event-log.md §6 | A; C (seal, verify) | T-001 | S | lead-opus-T005 | done |
| T-006 | Spike S2: pick the PDF parser (Docling / GROBID / PyMuPDF) incl. one scanned PDF | reading-aid.md §3 | A | T-001 | S | lead-opus-T006 | done |
| [T-007](tickets/T-007-preregistration.md) | Preregister S3 (≥ 40 pairs, labelled by someone other than the founder) and S4 | evaluation.md §1 | A | — | O | | ready |
| T-008 | Golden set sources: choose real readings + an open-licence textbook (e.g. OpenStax), check licences, draft the D19 YAML format incl. `expected_links` | evaluation.md §2, §2a; D-035 | A; F (eval labels) | — | O | codex-lead-T008 | done |
| [T-009](tickets/T-009-walkthrough.md) | Design the nursing walkthrough + blind question test | evaluation.md §5, receipt.md §8 | A | — | O | worker-T-009 | review |
| [T-010](tickets/T-010-design-system.md) | /design-consultation → `DESIGN.md` (type, scale, spacing, focus ring, dark mode). Must finish before the receipt UI in M1 | design-review-v1.md 13A | A; G, H (tokens) | — | O | codex-lead-T010 | done |

## Founder-only (agents can't do these)

| ID | Task | Status |
|---|---|---|
| F-001 | Pick a schedule option (build-plan.md §2a) | founder |
| F-002 | Teacher outreach; named teacher, class and assignment window (deadline checkpoint 10-30) | founder |
| F-003 | Processor approval, provider approval, ethics request | founder |
| F-004 | Add an OpenAI key for the gstack designer (`$D setup`) so mockups can be generated | founder |
| F-005 | Decide whether the DeepSeek worker may read the repo (it sends code and docs to a China-based provider; no secrets or student data are in the repo) | done (D-039) |

## Next: M1 (build-plan.md, ~10-29 → 11-03; written 2026-10-24 after D-041…D-046)

| ID | Task | Read first | Done when (EXPECTATIONS) | Depends on | Model | Owner | Status |
|---|---|---|---|---|---|---|---|
| T-011 | Paragraph links + node set: replace the inline `claim` mark with a paragraph `links` attribute `[{claim_id, by, suggestion_id?}]`; add the D-044 node set (headings 1–3, lists, blockquote, hard break, `em`, `strong`); link rules (split keeps both, join keeps both, new empty paragraph none, internal paste keeps, typing never changes links); regenerate the S1 parity fixtures (JS and Python `doc_hash` equal) | event-log.md §4, §5; D-044, D-045 | A; C (typed rules); D (paragraph links line) | — | O+S | lead-opus-T011 | done |
| T-012 | Events for M1: append API, staging table + one merged `editor.batch` per 5-minute window (timestamps rounded down), checkpoints with `doc_hash`, submit with idempotency key → seal, post-seal whitelist enforced by the store, `verify` endpoint | event-log.md §3, §5, §6; D-041 | A; C (5-min merge, seal, verify) | — | S | lead-opus-T012 | done |
| T-013 | Replay + mark check at compile: rebuild the doc from checkpoint + steps (prosemirror-py), replay-mismatch path (D28), check every non-typed run against its origin; a failed run is untraced | provenance.md §4.1; event-log.md §5 | A; C (mark check) | T-011, T-012 | S | lead-opus-T013 | done |
| T-014 | L1 provenance: sentence split, origin mix, chains through paragraph links, bands in order (D13, D27, D-045), receipt facts §7 (no construction-order ratio, D-046), thresholds into the engine stamp | provenance.md §3–§7 | A; C; D | T-013 | O+S | lead-opus-T014 | done |
| T-015 | Golden YAML scripts + Playwright generator + ingest builder (D19); 10 golden sessions incl. forged quote and coach marks and an elaborating honest writer | evaluation.md §2, §2a | A; C | T-008, T-011, T-012 | O+S | codex-lead-T015 | done |
| T-016 | Receipt compiler: (first, per D-050: sentences made only of confirmed Helper text leave the word and claim counts and show as \"mechanics\"); JSON with integer counts, `event_ids` = seq, `receipt_hash`; pillar-form question rules with L3e stubbed and "questions pending" mode; wording filter; engine stamp (lock hash, editor pair) | receipt.md §4–§6; D-041, D-044, D-046 | A; B; H (data lines) | T-014 | O+S | lead-opus-T016 | done |
| [T-017](tickets/T-017-receipt-ui.md) | Receipt UI + chain view (HTML, print stylesheet, first screen) | receipt.md §2–§3; DESIGN.md | A; H rendering lines (preview/withdrawal remain M2; OL-048); I-M1 human gate separate | T-010, T-016 | O | codex-lead-T017 | done |

## M2 implementation tickets

These tasks prepare the existing M2 design. Ready infrastructure tasks are independent of human evaluation; dependent tasks remain blocked until their prerequisite rows are done. No milestone exit is waived.

| ID | Task | Depends on | Model | Owner | Status |
|---|---|---|---|---|---|
| [T-018](tickets/T-018-receipt-storage.md) | Durable receipts and AI artifacts | T-012, T-016 | S | | ready |
| [T-019](tickets/T-019-job-queue.md) | Bounded durable job queue | T-012, T-003 | S | | ready |
| [T-020](tickets/T-020-compile-jobs.md) | Submit and compile orchestration | T-018, T-019 | O+S | | blocked |
| [T-021](tickets/T-021-release-withdrawal.md) | Release cap and transactional withdrawal | T-020 | O+S | | blocked |
| [T-022](tickets/T-022-receipt-preview.md) | Student preview and teacher lifecycle views | T-017, T-021; OL-049 preview order clarification | O+S | | blocked |
| [T-023](tickets/T-023-s3-harness.md) | Executable preregistered S3 evaluation harness | T-007 + frozen S3 protocol/threshold approval | O+S | | blocked |

## Remaining wave planning

- Full L3a/c/e leak-checked integration, the actual independently labelled S3 run and gated L3b need separate tickets after T-007 and the storage/job contracts land. T-020 does not claim those done.
- Nursing walkthrough execution requires T-009, a person reading at least ten M1 receipts, usable generated questions and an actual teacher. Protocol writing is ready now; human results cannot be fabricated by workers.
- M3–M5 and M4m follow design/build-plan.md. No real student before its §4 pilot gate.
