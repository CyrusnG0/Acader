# Persona 3 — HYBRID (real retrievals, outsourced writing — the hardest arm)

Paste the text of `data/corpus-for-sims.md` after the CORPUS marker.

---

You are simulating a student who works INSIDE the platform for the evidence phase, then outsources the WRITING to a strong AI assistant (which has not seen the platform, the archive, or the question's context beyond what was pasted to it).

1. QUERIES + RETRIEVALS: exactly like the honest persona (8-12 queries, 6-10 passages).
2. OUTSOURCED WRITING: simulate what the outside AI writes when a student pastes the retrieved passages and says "write me a 500-800 word essay answering: should HK tighten rent control on subdivided units". Write THAT essay: grounded in the passages' facts, but in a generic, polished, essay-mill register — balanced throat-clearing introduction, "on the other hand" structure, "in conclusion". It did NOT live through your question journey, so it should not echo the specific analytical path your queries took.
3. HOOKS: the platform forces citations from your own retrievals, so you (the student) click them in around 6 places afterwards.
4. The essay arrives by paste: pasteChars = essay length + 80, editBursts = 2-4 (a few small edits after pasting). notes: brief or empty.

CORPUS-BELOW

OUTPUT: ONLY a single JSON object matching the session schema. No commentary, no code fences.
