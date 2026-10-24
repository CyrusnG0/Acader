# TASKS.md: the task board

One task = one Opus lead conversation. Pick the first task whose status is `ready` and whose dependencies are `done`. Write your name/conversation tag in **Owner** before you start, so two leads never take the same task.

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
| T-007 | Preregister S3 (≥ 40 pairs, labelled by someone other than the founder) and S4 | evaluation.md §1 | A | — | O | | ready |
| T-008 | Golden set sources: choose real readings + an open-licence textbook (e.g. OpenStax), check licences, draft the D19 YAML format incl. `expected_links` | evaluation.md §2, §2a; D-035 | A; F (eval labels) | — | O | codex-lead-T008 | done |
| T-009 | Design the nursing walkthrough + blind question test | evaluation.md §5, receipt.md §8 | A | — | O | | ready |
| T-010 | /design-consultation → `DESIGN.md` (type, scale, spacing, focus ring, dark mode). Must finish before the receipt UI in M1 | design-review-v1.md 13A | A; G, H (tokens) | — | O | codex-lead-T010 | in progress |

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
| T-017 | Receipt UI + chain view (HTML, print stylesheet, first screen) | receipt.md §2–§3; DESIGN.md | A; H; I-M1 | T-010, T-016 | O | | blocked |

## Next waves (detail is added by the checker when M1 is done)

- **M2:** S3 run; L3 jobs with stored outputs; preview; job queue; release rule + cap; walkthrough + blind test.
- **M3–M4:** editor, reader, cards, workspace layout and states (workspace.md), Door, Coach (one "new idea" case, four pillars), leak sets.
- **M4b, H, M4m, M5:** see build-plan.md.
