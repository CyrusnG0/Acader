# Pre-registration v0.3 — re-run A3/A4 without the citation cap
Written 2026-10-16, BEFORE regenerating anything. v0.2 results are preserved in `runs-v0.2/` and RESULTS.md.

## Why
v0.2's A1-vs-A4 gap sat in "orphan" because `outside.py` capped outside-written essays at 6 citations while honest workers cited ~10. The cap is now 12 (every retrieved passage can be cited). **Honest disclosure:** this change was motivated by looking at v0.2 results, so v0.3 is a repair test, not an independent replication.

## What is re-run
A3 and A4, 6 each, **reusing the same 12 drafts** (identical questions and retrievals; only the outside essay and citation clicking are regenerated). A1, A2, A5, A6 are unchanged (A5 retrieved ~3 passages, so the cap never bound).

## Endpoints (fixed now)
- **Primary:** AUC A1 vs A4 on **trace + continuity only** (weights .35/.30 renormalised), because it is the part that speaks to understanding and is not affected by citation counts as orphan is.
  - Receipt "tells" the retyped hybrid apart: AUC ≥ 0.80.
  - Founder-side prediction (Claude's): AUC < 0.70, i.e. it does not.
- **Secondary:** AUC A1 vs A4 and A1 vs A3 on no-structure composite; mean hooks per arm (to confirm the artifact is gone: expect A3/A4 within 2 of A1).
- Same exclusion and reporting rules as PREREG.md. Same caveats.

## Interpretation
If primary < 0.80 the v0.2 conclusion stands (the receipt alone is not the gate). If ≥ 0.80, report that the trail did separate them and re-examine my v0.2 reading.
