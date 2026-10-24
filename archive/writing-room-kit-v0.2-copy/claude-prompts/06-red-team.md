# Red-team protocol — try to BREAK the receipt before CLEAR does

This is the continuation of "I tried to break my own design. It broke." Run these AFTER the basic three arms. Report results honestly either way.

## The attacks

### A1 — MIMIC (the one that matters)
Give Claude EVERYTHING: persona-1 prompt + corpus + the session schema + one honest example session, and instruct:
"You are an adversary. Fabricate a session JSON that looks like a perfect honest student: invent queries, retrievals, hooks, a grounded essay, realistic pasteChars=0 and editBursts=12. Maximise the coherence score."
- If the fabricated session scores >= honest range: the engine is fooled BY A MODEL WITH FULL SCHEMA ACCESS. Say so plainly. The mitigating claim to TEST, not assert: fabricating coherent queries+essay with correct facts requires doing most of the intellectual work. Check whether the fabricated essay is factually grounded in the corpus it was given — if the adversary must read the passages to fake the trail, the receipt moved the cost, not the wall.
- If it scores noticeably below honest: record WHY (usually continuity or trajectory details). That is your engine's fingerprint story.

### A2 — RETYPER
Honest-style session but essay delivered with pasteChars=0, editBursts=15 (student retyped the AI essay). Only structure is defeated; traceability/continuity unchanged. Expected: composite stays below honest because hooks/queries still mismatch — verify.

### A3 — QUERY-BUYER
Student asks an outside AI "what should I ask the librarian?", then asks those questions. Queries look analytical but arrived from outside. Check trajectory/continuity: does the score see anything? If not, say so — the honest answer is that question WORDS alone cannot prove authorship (Person & Graesser 1994 said answers matter; that is why the Room check exists).

### A4 — OVER-CITER
Honest student padded with hooks on every sentence and excessive retrievals. Check whether orphan/spread punish or reward gaming. If composite INFLATES, record it — that is a rubric-gaming hole to fix in v0.3.

## Reporting
For each attack: persona, n>=3 runs, composite distribution vs honest baseline, one-sentence verdict, and whether the design goal ("outsourcing harder, riskier, more effortful than engagement") still holds. This table goes in the memo's limitations section — before any success story.
