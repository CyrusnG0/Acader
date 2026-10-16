# Results — "Can the process tell?" v0.2 + v0.3 repair

> **Superseding update (v0.3, same day): the harness artifact described below was fixed and A3/A4 re-run. The receipt then shows NO separation of the retyped hybrid from honest work (composite 92 vs 91). Read the "v0.3 repair" section first; the v0.2 sections are kept as the record of how the artifact was found.**

Run 2026-10-16 · 36 simulated students (6 per arm) · pre-registered in [PREREG.md](PREREG.md) · raw scores in `runs/_scores.json`
Simulated students, tiny n, keyword-overlap librarian. This tests a mechanism, not a detector, and says nothing about real students.

## One-line outcome
**Pre-registered primary endpoint: met on paper (AUC 0.83 ≥ 0.80). But I do not think it shows what it appears to show.** The gap comes from a harness artifact, and on the parts of the score that measure *understanding* the retyped hybrid cannot be told from honest work. This supports "the conversation is the gate" (law 5), not "the receipt is the gate."

## Per-arm scores (mean ± sd [min–max])
| Arm | n | Composite | No-structure | Trace | Continuity | Orphan | Struct |
|---|---|---|---|---|---|---|---|
| A1 honest | 6 | 91 ±2 | 89 ±2 | 100 | 70 ±7 | 99 | 100 |
| A2 lazy-honest | 6 | 67 ±7 | 58 ±8 | 65 | 43 ±9 | 72 | 100 |
| A3 hybrid, pasted | 6 | 79 ±3 | 86 ±4 | 98 | 79 ±10 | 70 | 50 |
| A4 hybrid, retyped | 6 | 87 ±3 | 84 ±3 | 98 | 72 ±10 | 75 | 100 |
| A5 outside-coached | 6 | 79 ±3 | 73 ±4 | 72 ±7 | 62 ±4 | 100 | 100 |
| A6 outsourced floor | 6 | 9 ±3 | 0 | 0 | 0 | 0 | 45 |

## Pre-registered tests
| Test | Result | Verdict |
|---|---|---|
| **Primary:** AUC A1 vs A4, no-structure | **0.83** (identical with or without A1-4; bootstrap 95% CI **0.56–1.00**) | Met, but the CI includes "barely better than chance", and see below |
| AUC A1 vs A5, no-structure | 1.00 | Met |
| AUC A1 vs A3, with structure | 1.00 | Trivial, as pre-registered; not evidence (structure is set by the arm rule) |
| Every A2 run has ≥ 1 flag | Met (all six carry "only N of 6 required linked citations") | A2's low score is an explainable gap, not a verdict |
| A6 composite < 20 | Met (5–11) | Sanity floor only |

## Why the primary result should not be trusted as it stands
Component-level breakdown, run **after** the pre-registered analysis (post-hoc, labelled as such):

| Component | AUC A1 vs A4 | AUC A1 vs A3 | AUC A1 vs A5 |
|---|---|---|---|
| Trace + Continuity only (the part about understanding) | **0.42** | **0.35** | 1.00 |
| Continuity only | 0.42 | 0.24 | 0.88 |
| Trace only | 0.58 | 0.58 | 1.00 |
| Orphan only | 0.90 | 0.90 | 0.42 |

- **The A1-vs-A4 gap lives entirely in "orphan" (retrieved passages never cited).** A1 workers cited about 9.8 passages (they cited everything they retrieved); A3 and A4 averaged 5.8 hooks because my `click_citations` helper caps outside-written essays at 6 citations, mirroring the "6 required" rule. It rewards the honest arm for a number I chose. That is a harness artifact, not evidence about understanding.
- **On trace and continuity, A4 and even A3 look as coherent as honest, or more so.** Continuity (essay vocabulary found in the student's own questions plus retrieved passages) is *higher* for the pasted hybrid (79) than for honest (70). An outside AI fed the retrieved passages reuses their vocabulary. This is the prediction written in PREREG before the runs: continuity does not catch a hybrid.
- **A5 (outside AI chose the questions) is separated** (AUC 1.00), but through weaker evidence of engagement, not through deeper understanding: only ~3 distinct passages retrieved, because the outside AI's questions were broad. Its composite (79) is still within 12 points of honest.

## What this tells us
1. A receipt that measures *coherence of the trail* is easy to satisfy with retrieved passages + an outside writer. It separates **no-engagement** (A6, A2) clearly and **engagement without understanding** (A3/A4) hardly at all.
2. This is the strongest argument yet for law 5 and for the master brief's §10: the receipt is the **entry condition and the question generator**; **the short conversation about the student's own claims is the gate**. It also argues for building the part the receipt cannot supply: questions anchored to the student's own claims and sources.
3. Structure (paste, bursts) is the only signal that separates A3 from A1, and A4 (retyping) erases it. Do not sell structure as proof.

## Caveats and deviations (all disclosed)
- **Simulated students.** Real students will be messier; this is a mechanism test only.
- **n = 6 per arm.** The bootstrap interval on the primary endpoint is 0.56–1.00.
- **Same team designed engine and experiment.** Weights are the v1 guess and were not tuned.
- **One outside writer** (DeepSeek, `deepseek-chat`, temperature 0.7). Honest and lazy students were Claude Sonnet workers, so writer model differs between inside and outside arms, a confound that cuts both ways.
- **Retrieval is keyword overlap.** Many questions miss or return the same passage (D1p1, D1p4 recur). That limits how much evidence any arm can gather.
- **Deviations from spec:** A1 workers asked 12–16 questions (spec 8–12) after misses; several workers finalised twice after trimming word count or removing a citation to an unretrieved passage; A3-3 and A4-6 logged a `--id` miss from a mis-ordered first call. A2-1 was 602 words (limit 600). A1-4 was flagged `invalid_adherence` by the leak check on the word "Counsel" (a role word); adjudicated by hand as not a factual leak, and the primary AUC is the same with or without it. Validator fixes made after generation but before scoring are listed in PREREG.md "Amendments".
- No claim of detection, accuracy or deployment readiness is made or implied.

## For CLEAR (draft, 5 sentences)
We tried to break our own design with 36 simulated students and an outside AI as the ghost writer. A student who does no work inside the platform shows a clear gap, and a student who does thin work shows an explainable one. But a student who gathers real passages inside, has an outside AI write the essay and retypes it leaves a trail that looks as coherent as honest work. So the trail alone cannot be the gate. The short conversation about the student's own claims and sources is, and that is the part we are asking to pilot.

## Next
- (done, see v0.3 repair) Fix the harness artifact and re-run A3/A4.
- Test the actual gate: generate claim-anchored questions from each run's essay and check whether A1 vs A4 can answer them (needs a responder model that sees only the trail). This is the experiment CLEAR would care about.
- Hinge documents and the question budget in the engine (master brief §5–§7).

---

## v0.3 repair — A3/A4 re-run without the 6-citation cap
Pre-registered in [PREREG-v0.3.md](PREREG-v0.3.md) before regenerating. Same 12 drafts (identical questions and retrievals); only the outside essay and citation clicking were regenerated. v0.2 runs are preserved in `runs-v0.2/`. **Caveat:** the fix was motivated by v0.2 results, so this is a repair test, not an independent replication.

| Arm | n | Composite | No-structure | Trace | Continuity | Orphan | Struct | Mean hooks |
|---|---|---|---|---|---|---|---|---|
| A1 honest | 6 | 91 | 89 | 100 | 70 | 99 | 100 | 9.8 |
| A3 hybrid, pasted | 6 | 78 | 89 | 98 | 73 | 100 | 35 | 8.8 |
| A4 hybrid, retyped | 6 | **92** | 90 | 98 | 75 | 100 | 100 | 8.0 |

| Pre-registered endpoint | Result |
|---|---|
| **Primary:** AUC A1 vs A4, trace + continuity | **0.33** (bootstrap 95% CI 0.03–0.67). Needed ≥ 0.80 for "the receipt tells". **Not met.** My prediction (< 0.70) held. |
| AUC A1 vs A4, no-structure composite | 0.31 |
| AUC A1 vs A3, no-structure composite | 0.46 |
| Mean hooks A1 / A3 / A4 (artifact check, within 2 of A1) | 9.8 / 8.8 / 8.0. A4 is 1.8 below A1, so within tolerance. |

**Conclusion.** Once the artifact is gone, the retyped hybrid scores *above* honest on the composite and indistinguishable on every component. Only the **paste** structure signal (A3: 35) separates a student, and retyping removes it. So, in this simulation, the coherence receipt cannot separate a student who did the thinking from one who retrieved passages inside the platform and had an outside AI write and retyped the essay. The receipt is the entry condition; the conversation about the student's own claims and sources is the gate.

**What this does and doesn't say.** It says nothing about real students, and nothing about question-based gates, which were not tested (OL-029). It says the v1 weights (traceability, continuity, orphan, structure) are not a defensible proxy for understanding. They measure engagement and coherence of a trail, and an outside AI given the retrieved passages produces both.

**Updated "For CLEAR" box (replaces the v0.2 draft).** We tried to break our own design with 36 simulated students and an outside AI as ghost writer. A student who does no work inside the platform leaves an obvious gap. But a student who gathers real passages inside the platform, has an outside AI write the essay and retypes it leaves a trail indistinguishable from honest work, so the trail cannot be the gate. The short conversation about the student's own claims and sources is, and that is the part we want to pilot and measure.
