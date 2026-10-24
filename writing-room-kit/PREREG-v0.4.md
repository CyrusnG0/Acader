# Pre-registration — v0.4 "Does the coherence report separate the four kinds of student?"

Written 2026-10-16, **before any P3 run** (the 30 worker runs). Status: DRAFT for Cyrus at gate 1. Plan: [PLAN-v0.4.md](PLAN-v0.4.md). Design: [process-evidence-room.md](../docs/designs/process-evidence-room.md).
Simulated students, tiny n. This tests a mechanism, not a way to judge students, and says nothing about real students or the live oral.

## What is tested
A governed assistant (`v04/room.py`, DeepSeek behind policy modules) and a coherence report (`v04/lineage.py`) that checks whether submitted work fits the process in the Room. The report only verifies and asks questions; it never judges. Students are Sonnet workers who know nothing about the topic (fictional archive). The judge is DeepSeek with the arm label and run id stripped.

## Arms (n = 6 each, 30 runs; ids C1-1 … C5-6)
| Arm | Behaviour | Struct rule |
|---|---|---|
| C1 honest | 15–30 turns; chooses with reasons; reads; own claims; answers counters; ≥ 2 drafts; writes 500–800 words; ≥ 6 citations to passages it read | typed |
| C2 lazy honest | 4–8 turns; vague; reasons of 3–6 words; 1–2 drafts; 400–550 words; ≥ 3 citations | typed |
| C3 all outside | 2–3 turns for show; outside AI writes everything; unchanged | pasted |
| C4 partial outside | lighter honest process (10–15 turns) + own draft; ≥ 2 body paragraphs (about half) swapped for outside paragraphs; never discussed | retyped |
| C5 partial + covered | as C4, then narrates, sources and defends each swapped-in paragraph in the Room before finalising | retyped |

Structure comes from the arm rule (typed/retyped: paste 0, bursts max(6, words/60); pasted: paste = essay length + 100, bursts 1–3), never from the worker.

## Report
Components 0–100: claim lineage, source lineage, citation check, change lineage, structure. Composite = 0.35 claim + 0.20 source + 0.15 cite + 0.15 change + 0.15 struct. **composite_nostruct** renormalises the first four. Weights are a first guess and are not tuned.
Judge calls: `claims`, `ancestor` (batches of 10 claims), `cite` (one per citation, against the hand-readable answer key `data/answer-key.json`), `change` (one per pair of consecutive snapshots).

## Endpoints
1. **Sanity:** AUC of C1 vs C3 on composite ≥ 0.90. If it fails, stop and report.
2. **Primary:** AUC of C1 vs C4 on composite_nostruct ≥ 0.80. (The v0.2/v0.3 receipt got 0.33.) 2,000-sample bootstrap 95% CI reported.
3. **Ordering:** mean composite in the order C1 > C2 > C4 > C3.
4. **C5:** AUC of C1 vs C5 on composite_nostruct, reported with no threshold.
5. **Policy health:** law-1 "yes" on ≤ 2% of assistant turns; source leaks = 0; median student turns to a shortlist ≤ 3.
6. **Hand audit:** Cyrus grades claim-ancestor correctness on 6 seeded random reports (≥ 1 per arm, arm stripped).

## Predictions (written before the runs)
- Sanity: met.
- **Primary: met.** The swapped-in paragraphs have no ancestor in the Room, so claim lineage and change lineage should fall for C4.
- **Ordering: likely NOT met** between C2 and C4. Lazy honest work has few ancestors; half-swapped work keeps its other half. I expect mean C2 < mean C4.
- **C5: AUC < 0.70**, i.e. covering the swapped-in paragraphs inside the Room passes as coherent. This is the agreed limit: anything typed can be produced by an AI with the same context. We report it, we don't fix it.
- Policy health: law-1 ≤ 2% likely met on DeepSeek; source leaks 0 by construction.

## Exclusions (counted and reported)
- a run that fails `finalize.py`
- an honest arm (C1, C2) that cites a passage it never `read`
- a worker whose transcript shows it read forbidden files

## Open design notes (for gate 1)
1. **Facts read from a passage show up as questions.** In DRY-1 the report asked "Where did 'Mr Chan pays 5,800 dollars' come from?" although the student had read it in D3p1. By the plan's definition an ancestor is a student statement, a pick reason or a confident statement; a `read` turn is not. It applies equally to every arm, but it lowers honest scores. Option for Cyrus: count a `read` of the cited passage as the ancestor of a factual claim. I have **not** changed it.
2. **The question-kind tag is loose** (the router called "find me a source" `wants_answer`). It is used only for routing and the student mirror (Q10), so this has no effect on the endpoints.
3. **Same vendor** plays assistant, outside AI and judge. The same team designed the test and the product.

## Amendments (every change made after the first live run, with reason)
| # | Change | Why |
|---|---|---|
| A1 | `config.json` gets `P-SRC.stable_overlap = 2` (was implicitly 3: top-3 set unchanged) | With the LLM picker the top-3 shifted by one doc between turns, so every request ran to the cap. A shortlist now serves when 2 of the top 3 repeat. The cap is still 3. **Cyrus to confirm at gate 1.** |
| A2 | Router sees the assistant's previous message; while a clarify question is open, any answer continues it (except write/argue/structure/citation requests) | In DRY-1 an answer was mis-routed and the source request stalled |
| A3 | A source request while a shortlist is still open gets a fixed reminder first; a second one opens a new request (the old one is `abandoned`) | DRY-3 reopened clarifying instead of pointing at the open list |
| A4 | `P-SRC-describe`: kind of material and vantage point only, never a finding or number | First smoke run described findings ("3–5% stock loss") |
| A5 | `P-WRT`: no facts, documents or positions in the shape options | First smoke run mentioned Berlin and Hong Kong data in a write reply |
| A6 | `P-CTR`: states the opposing position only, no figures or quotations | An unread document's numbers reached a student through the counter-claim |
| A7 | Hints in tool replies no longer show a command line | Neutral wording for the workers |
| A8 | `finalize.py` derives the struct from the arm rule and refuses a worker-supplied value that disagrees | Plan §2 (v0.2 lesson F1) |

Test suite: 13 tests (the plan's 11 plus a leak-check test and a shortlist-reminder test), all pass on the stub LLM.

## Amendments made after the runs (disclosed, none changes an endpoint)
| # | Change | Why |
|---|---|---|
| A9 | The source-leak check no longer counts a doc id or title that the student had already typed earlier in the session ("You've said D6p1…"). Raw count kept in each audit file as `clarify_echoes_raw`. | The first scoring pass counted 9 "leaks", all echoes of ids the student had just used. The clarify prompt holds no corpus text by construction (test 3). Raw 9, refined 0. |
| A10 | Gate 1 was passed by Cyrus with "go". The A1 `stable_overlap = 2` setting was therefore kept for all 30 runs. | — |
