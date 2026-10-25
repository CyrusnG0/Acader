# T-027: "More places to ask": the full candidate list

**Pickup:** ready. **Dependencies:** T-016, T-017, T-020 (done). Follow [pickup rules](README.md); the board is authoritative for current ownership. Branch: `task/T-027-more-places` from checker-accepted main. Claim only your row before coding. Coordinate with T-022 if both touch the teacher receipt view.

## Read first

AGENTS.md, docs/STATUS.md, docs/TASKS.md, EXPECTATIONS.md, docs/OPEN_LOOPS.md (OL-059), PRODUCT.md, then these spec references (unqualified design filenames are in design/): docs/DECISIONS.md D-060, D-046, D-053; receipt.md §2 item 3, §4, §5, §6; DESIGN.md; `engine/receipt/questions.py`, `engine/receipt/compile.py`. Read the existing code and dependency handoffs; these tickets do not override the design specs.

## Scope and boundaries

The teacher receipt keeps the top 2–3 questions on the first screen and adds one closed disclosure, "More places to ask", listing every other candidate place the question step considered (D-060), so a teacher can find something the system would not ask.

What is known (checker, 2026-10-25): `select_candidates` builds the full ordered candidate list (untraced claims that carry the argument, declared claims not anchored, student-linked claims that carry the argument, mapper findings) and returns only the first three with grounding, one per paragraph; the others are discarded, are not in the receipt JSON and get no question text. Candidates with no grounding are only counted (`skipped`).

Build: keep every grounded candidate not chosen as a top question in a new receipt JSON field (spans, plain reason code, grounding ids, `event_ids`; integers only, no floats, D-041), included in `receipt_hash`, so the receipt stays byte-identical for the same log and stamp. Render it under the questions, closed by default and expanded in print, in paragraph order, with the reason in plain words from the existing copy, no numbering by priority, no score, and nothing in the submissions list. Every string passes the wording filter (receipt.md §5). Candidates without grounding stay out (law 2).

Unknown, write as proposed decisions, do not choose: (a) whether extra candidates get generated question wording (one provider call each, D-054 slots, leak check) or only place plus reason (suggested v1: place plus reason, no extra calls); (b) whether the student preview lists these places too (OL-059; founder decision, do not build it either way until answered); (c) whether to cap the list length; (d) the schema/version bump.

## Required evidence

Golden receipts: the list contains exactly the grounded non-chosen candidates, in paragraph order; top three unchanged from before; byte-identical recompile; `receipt_hash` covers the new field; wording-filter test over every new string; disclosure closed on first screen, open in print; keyboard, narrow, dark checks; no student response contains the list until OL-059 is decided.

Run relevant new tests, full prototype tests with ROOM_LLM=stub, and the kit's 29 regression tests. For UI changes also run web tests, typecheck/build and focused browser checks. Record actual environments and results; never claim unobserved CI. No secrets, real student data, live providers or shared/llm.py behavior changes.

Model: O+S (wording and reason copy stay with the Opus lead).

Return commits, a dated docs/handoffs note, files changed, reproduction commands, EXPECTATIONS A plus the relevant B/H requirements, failures and proposed decisions. Set your own row to review. Only the checker merges, marks done and updates shared tracking. M1 human reading and every pilot gate remain separate; this ticket cannot satisfy them.
