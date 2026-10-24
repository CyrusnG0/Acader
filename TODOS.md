# TODOS

## Writing Room v1: deferred by /plan-ceo-review (2026-10-23)

Context: the CEO review chose a receipt-first thin slice for one class by 2026-11-05 (docs/designs/ceo-review-v1.md, CEO-1). These items wait until the first class is using v1. Pick them up in this order unless pilot feedback says otherwise.

| # | Item | Why deferred | Upgrade trigger | Effort | Priority |
|---|---|---|---|---|---|
| 1 | Coach case D (contradiction, scope creep, cherry-picking) | Needs L3 contradiction check and its own leak audit | First class running; S3 passed | M | P1 |
| 2 | Polish-only band on the receipt (CEO-3) | A false "just polish" label would clear AI-added reasoning; depends on spike S3 | S3 passes its preregistered bar | M | P1 |
| 3 | LLM-directed reading pins (support / skeptical) | v1 ships section-kind pins only (limitation, method, data, results) | Students in the pilot ask for "where does it disagree?" | M | P2 |
| 4 | Coach cases A (blank page) and E (confident mode) | B and C cover the receipt; A and E are experience | After first-class feedback | S | P2 |
| 5 | Student scholarly search (OpenAlex / Crossref) | Teacher readings + the Door cover one class | A teacher wants students to bring their own papers | M | P2 |
| 6 | Teacher policy dial per assignment (CEO-4) | One class needs one policy; levels multiply the leak-audit matrix | A second class with different AI rules | M | P2 |
| 7 | Claim map graph view | List view carries the same data | After v1 | S | P3 |
| 8 | Server-side receipt PDF with receipt hash (CEO-5) | Browser print covers the pilot | A teacher needs the receipt in a formal file | S | P3 |
| 0 | Blackboard LTI 1.3 launch + roster sync (CEO-8, D9.1) | Needs the university's LMS admin to register the tool; can't fit 13 days | Pilot school's IT contact found; first post-pilot item, raise early | L | P1 |
| 9 | Further pilot classes | One class first (CEO-1) | First class completes one assignment | S per class | P1 |
| 10 | L2 embeddings for candidate claim nodes (eng D1) | Needs an embedding provider (another processor) and pgvector; L3b can take all claim nodes or the BM25 top 5 | Real claim maps exceed ~30 nodes per essay | M | P3 |
| 11 | Move to Postgres (eng D3, D35) | SQLite on one machine fits one class | More than one class or more than one app machine. Steps: same SQLAlchemy schema; append = unique (log_id, seq) + retry; jobs via SELECT … FOR UPDATE SKIP LOCKED; managed backups; name the DB host in consent | M | P2 |

## Runner (viva pilot)

### Bound total wait for question generation

**What:** Put a total time budget on question generation (across retries) and show a timeout message on the student page.

**Why:** Worst case today is 3 attempts x 60 s = 180 s per question set (360 s in blind mode) behind a spinner with no message (`runner/viva.py` `MAX_RETRIES`, `anthropic_complete` timeout; `runner/static/student.html`).

**Context:** Deferred by /plan-eng-review R12 (`docs/designs/eng-review-runner-demo.md`, answer D11 "A"). The right number should come from measured Anthropic p50/p95 latency, which does not exist yet because the real-LLM path has never been run (OL-017). Start by measuring, then set the budget to roughly 2-3x p95, keep the existing "generation failed" message, and add a timeout-path test. Accepted shortcut: Completeness 7/10, upgrade when OL-017 reports latency.

**Effort:** S
**Priority:** P3
**Depends on:** OL-017 (run the runner with a real Anthropic key and record latency)

## Completed
