# Batch protocol — "Can the process tell?" (model-only feasibility test)

## Setup
- 3 personas x >=5 runs each (fresh chat per run, so runs are independent).
- Run order per chat: paste persona prompt, then paste `data/corpus-for-sims.md` (personas 1 and 3 ONLY; persona 2 never sees the corpus).
- Save every output as `runs/<persona>-<n>.json`. If Claude wraps it in code fences, keep them — score.js strips them. If it adds commentary, keep only the JSON object (or re-ask: "output ONLY the JSON").

## Score
```
node scripts/score.js runs/*.json
```

## What success looks like (write this down BEFORE looking at results)
- honest and pasted distributions separate by a wide margin (the engine test already shows 87 vs 5 on hand-made sessions);
- hybrid is the informative arm: if its continuity/structure sit clearly below honest while its traceability stays high, the score catches outsourced writing that real retrievals try to launder;
- honest-but-lazy (low citations) is an EXPLAINABLE low score, not a false positive — the flag list says why.

## Record per run
persona, composite, trace, cont, orphan, struct, flags, plus one manual check: for honest runs, verify the essay uses no specific fact from unretrieved passages (persona-adherence check — discard the run if Claude broke role).

## Honest reporting to CLEAR
- n is tiny; this is a feasibility test of the MECHANISM, not a detector and not a deployment claim.
- personas are model-simulated; real students will be messier (that is what the classroom pilot is for).
- No claim of 100% anti-cheat: the design goal is making outsourcing harder, riskier and more effortful than genuine engagement (Winstone et al. 2026).
