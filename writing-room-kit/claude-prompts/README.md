# Arm prompts (v0.2) — one file per arm

Workers read ONLY: their arm file, `data/corpus-for-sims.md` (A1–A4 only), and the tool usage below.
They must NOT read `scripts/score.js`, `scripts/validate.js`, `PLAN.md`, `PREREG.md`, `RESULTS.md`, or anything in `runs/`.
No prompt mentions scoring. Structure (paste/bursts) is set by `finalize.js` from the arm rule; workers never report it.

Tools (run from `writing-room-kit/`):
- Ask the librarian (the ONLY way to get passages): `node scripts/librarian.js work/<ARM>-<N>.draft.json "your question"`
- Finalise: `node scripts/finalize.js work/<ARM>-<N>.draft.json --essay work/<ARM>-<N>.txt --arm <ARM> --n <N> --struct <rule> --writer <name> [--notes work/<ARM>-<N>.notes.txt]`
- Outside AI: `python3 scripts/outside.py write|bare|coach ...`

Task: "Should Hong Kong tighten rent control on subdivided units? Take a position and defend it with evidence from the course archive."
Citations in essays are written inline as `[D6p4]`.

| Arm | File | Struct rule |
|---|---|---|
| A1 honest | A1-honest.md | typed |
| A2 lazy-honest | A2-lazy.md | typed |
| A3 hybrid, pasted | A3-hybrid-pasted.md | pasted |
| A4 hybrid, retyped | A4-hybrid-retyped.md | retyped |
| A5 outside-coached | A5-outside-coached.md | retyped |
| A6 outsourced floor | A6-outsourced.md | pasted |
