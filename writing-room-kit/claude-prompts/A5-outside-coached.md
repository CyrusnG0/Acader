# A5 — Outside-coached (outside AI suggests the questions AND writes)
1. Run `python3 scripts/outside.py coach work/A5-<N>.coach.txt`. It asks an outside AI which questions to put to a librarian (it has never seen the archive).
2. Put each of those questions, verbatim, to the librarian via `scripts/librarian.js` (all of them, in order).
3. Run `python3 scripts/outside.py write work/A5-<N>.draft.json work/A5-<N>.txt`.
4. Finalise with `--struct retyped --writer deepseek-chat`. Do not use your own judgment on any step.
