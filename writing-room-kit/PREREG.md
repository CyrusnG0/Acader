# Pre-registration — "Can the process tell?" v0.2
Written 2026-10-16, BEFORE any run is generated. Do not edit after P3 starts; add a dated "Amendments" section instead.

## Question
Does the v1 coherence score separate students who do the thinking inside the platform (A1) from students who keep the archive evidence but outsource the writing (A3, A4, A5)?

## Arms (n = 6 each, 36 runs; each from a fresh worker context)
A1 honest · A2 lazy-honest · A3 hybrid-pasted · A4 hybrid-retyped · A5 outside-coached · A6 outsourced floor.

## Primary endpoint
AUC(A1 vs A4) on **composite_nostruct** (trace, continuity, orphan; weights .35/.30/.15 renormalised). Structure is excluded because the arm rule sets it by construction.
- **Supported:** AUC ≥ 0.80.
- **Not supported:** AUC < 0.80.
- **Founder-side prediction (Claude's):** AUC < 0.70. An outside writer given the retrieved passages reuses their vocabulary, so continuity will not separate retyped-hybrid from honest.

## Secondary
1. AUC(A1 vs A5) on composite_nostruct.
2. AUC(A1 vs A3) on composite WITH structure. Expected high but trivially so; **not to be cited as evidence**.
3. Every A2 run carries ≥ 1 flag explaining its low score (an explainable low score, not a verdict).
4. A6 composite < 20 in every run (sanity floor only).

## Exclusions (report counts)
A1 runs marked `invalid_adherence` by validate.js; any run failing validate.js. Excluded runs are regenerated once, then reported as excluded.

## Interpretation rules, fixed in advance
- Supported → "in this simulation the receipt separates outsourced writing", with the caveats below, and nothing stronger.
- Not supported → report as a finding: the receipt alone is not the gate; the conversation is (law 5). That is the honest answer to give CLEAR.
- Never reported as detection accuracy or a deployment claim.

## Caveats stated up front
Simulated students; n = 6; mechanical librarian (keyword overlap); one outside-writer model (DeepSeek); the engine and the scenario were designed by the same team; hand-made example sessions in `sessions/` are not part of the test.

## Amendments
- 2026-10-16 (after runs generated, BEFORE any scoring): validate.js leak check now treats the document title of every retrieved passage as seen, because the librarian prints it with each answer. Before this, names such as "Wong" and "Berlin" in A1 essays were false positives (5 of 6 A1 runs flagged). No thresholds, weights or endpoints changed.
- Run-generation deviations (reported in RESULTS.md): A1 workers asked 12–16 questions (spec 8–12) after misses; several workers finalised twice after trimming word count or removing a citation to an unretrieved passage; A3-3 and A4-6 logged a "--id" miss from a mis-ordered first call.
- 2026-10-16 (before scoring): validate.js now strips [DxPy] citation markers before the leak check (A1-5 was flagged on the digits of its own "[D10p1]" marker). A1-4 remains flagged on the word "Counsel" (a role word from D9p2; the claim it supports is in the retrieved D9p1). Adjudicated by hand as not a factual leak; the primary AUC is reported both with and without A1-4.
