# PREREG v0.5: controls and adaptive-attacker round

Written by: Sonnet executor, following [PLAN-v0.5.md](PLAN-v0.5.md). Status: §A written 2026-10-17 **before** `v04/controls.py` was run. §B and §C follow later.

## §A. P0 controls on the existing 66 runs (C1–C10, n = 6 each)

Nothing here needs a new student. Reports in `v04/reports/` are read-only. All outputs go to `v04/reports-v05/`.

### A.1 Permutation test (O1)
- For each comparison below, 10,000 label shuffles within the two pooled arms. Report the one-sided p of the observed AUC (honest side expected higher on composite_nostruct, lower on F13).
- Comparisons: composite_nostruct, C1 vs each of C4, C5, C6, C7, C8, C9. F13, C1 vs each of C6–C9 and C10 vs each of C6–C9.
- Also report the smallest AUC that reaches p < 0.05 at 6 vs 6.
- **Prediction:** p < 0.01 for every observed AUC ≥ 0.95.

### A.2 Trail swap (O2)
Hybrid runs are built in memory only. Writing side (essay, citations, drafts, struct) comes from owner *i*; thinking side (turns, src_requests, picks, unlocked_docs, read_passages, counters, question_kinds) comes from owner *j*, where *j* is the next run in sorted order within the same arm (wrapping). Reports are made with the v0.4 judge and `lineage.report()`, written to `v04/reports-v05/swap/`.

- S1: C1 essays with other C1 trails (6) and C10 essays with other C10 trails (6).
- S2: each C8 essay with C1 trail *k* (6).
- S3: C1 essays with C8 trails (6).

Endpoints:
- **E-A1:** AUC of matched honest (C1 + C10, 12 runs) vs S1 (12 runs) on composite_nostruct, and on the claim component. Pass ≥ 0.80.
- **E-A2:** mean drop in claim lineage, matched minus S1, with a 2000-sample bootstrap CI.
- **E-A3:** S2 composite_nostruct vs the same essays' own C8 composite_nostruct. Does a borrowed honest trail rescue an outside essay?

Predictions (planner): E-A1 ≥ 0.80 for C1 and weaker for C10 (the six C10 students opened with near-identical positions, so a swapped trail may look like a fit). S2 stays low (claim lineage below 40).

**Stop rule:** if E-A1 < 0.70, the report is measuring topic, not derivation. Stop after P0, write it up, tell Cyrus. Do not run P3.

### A.3 Essay-only baseline (O3, part 1)
AUC of C1 vs each other arm on:
- Stylometry, no LLM: mean sentence length; type–token ratio over the first 400 words; citations per 100 words; share of sentences with a number; mean paragraph length.
- A blind LLM read, one call per essay with only the essay shown: json `{"process": 0-100}`, 0 meaning produced in one pass by a writing tool, 100 meaning developed step by step by a student who researched it.

**Prediction:** at least one stylometric feature gives AUC ≥ 0.80 (or ≤ 0.20) for C1 vs the relay arms, because honest essays are Sonnet's and outside essays are DeepSeek's. This is the confound the P3 model swap is built to break. Finding it is expected and will be reported plainly.

### A.4 Judge swap (O5)
- **J1, other model from the same vendor:** claim and ancestor calls only, on all 66 runs, with `DEEPSEEK_MODEL=deepseek-reasoner` in the process environment. Smoke test one `claims` call first; if the model rejects json mode or temperature, retry without; if it still fails, record the failure here and skip J1.
- **J2, different vendor:** 24 runs (4 each from C1, C10, C4, C6, C8, C9, picked by seed 7) as stripped packets P01–P24 with the v0.4 claim list fixed; 3 Sonnet judge workers, 8 packets each, using the v0.4 ancestor system prompt verbatim.
- **E-A5:** per-run Spearman between the v0.4 judge and each of J1, J2 on claim lineage.
- **E-A6:** AUC of C1 + C10 vs C6 + C8 + C9 on claim lineage under each judge.
- **Prediction:** Spearman ≥ 0.6 and AUC ≥ 0.80 under both judges.

### A.5 Reporting rule
Every prediction above is reported next to its outcome, wrong ones included. Anything that departs from this text goes in §C with the reason, not into the code silently.

## §B. P3 arms, F14, endpoints (written 2026-10-17 before any P3 run and before any test-set F14 number)

### B.1 Arms (n = 6 each, 24 runs, new paths: `v04/runs-v05/`, `v04/sessions-v05/`, reports in `v04/reports-v05/`)

| Arm | Who | Essay | Purpose |
|---|---|---|---|
| C11 honest-ds | DeepSeek operator, no essay, the C1 instruction text | its own, written from what it read | Model swap: the honest side is not Sonnet |
| C12 relay-claude | DeepSeek operator, `careful` style | written by a Claude worker given only the `outside.py v4` prompt text | Model swap: the outside side is not DeepSeek |
| C13 loop | DeepSeek operator, white-box rules summary, up to 3 `check` rounds, outside revisions, cap 80 actions | `outside.py v4`, revised by `outside.py revise` | Founder's direction (a): paste the Coach back, redo the passage |
| C14 stubborn | DeepSeek operator, at least 6 research actions, then one `check`; the outside writer answers each question | `outside.py v4`, never changed | Founder's direction (b): insist on the final paragraph |

Every run sets `ROOM_RUNS_DIR=v04/runs-v05`, `ROOM_SESSIONS_DIR=v04/sessions-v05`, `ROOM_RUN_ID=<id>` (relay.py sets the last itself). Struct rule: C11 typed; C12, C13, C14 retyped.

### B.2 F14 (derivation graph), frozen
- Definitions as in PLAN-v0.5 P1.2: F14a step size (mean new units per statement with at least one unit; honest direction low), F14b parentage (share of units with a non-`none` parent; high), F14c grounded chains (share of essay claims of kind `derived` whose ancestor unit has a parent chain reaching a passage within 3 edges; high), F14d refinement (descriptive only).
- Dev set: runs `-1` and `-2` of every arm. Test set: runs `-3` to `-6`. Only test-set numbers are reported as results. `derive.py` refuses test ids unless its sha256 appears in this file.
- **Frozen `v04/derive.py` sha256: `3a79b4815f633fc0703c7fbcf0bfa69127f15a73cdfea5987f3c34b3d2449bea`** (computed 2026-10-17 on the file as it stands after the dev checks in §C item 10). Any later edit to `derive.py` voids test-set F14 numbers produced after it.

### B.3 Endpoints (AUC; bar 0.80; 2000-sample bootstrap CI; one-sided permutation p; composite_v2 is the no-struct composite with claim_v2)
- **E-C1 model swap:** composite_v2, C11 vs C12. Prediction (planner): AUC at least 0.80. If it fails, the v0.4 separation was largely writer-model style; RESULTS-v0.5 says so in its first line.
- **E-C2 model-swap essay-only:** the A.3 stylometric and blind-read baselines on C11 vs C12. Prediction: they separate less than on C1 vs the relay arms, which would show the trail carries signal the essay does not.
- **E-C3 loop:** composite_v2, honest (C1 + C10 + C11) vs C13 after its final round. Planner prediction: AUC at least 0.80. Per-round trajectory of C13 (composite_v2, open questions, effort) is reported as well.
  - *Executor note, written before the runs:* the live smoke run (`DRY-C13`, §C item 9) scored 78.1, with 14 of 21 claims derived, so I expect E-C3 may FAIL on composite_v2. If so, the headline is the cost axis (E-C7), not the AUC.
- **E-C4 stubborn:** C14 open questions. Prediction: every C14 run ends with at least 3 questions in `explained_after` plus `none`, and composite_v2 below 60.
- **E-C5 F14 (test set only):** honest (C1, C10, C11) vs outside (C6-C9, C12-C14) on F14a, F14b, F14c. Prediction: AUC at least 0.80 on F14b or F14c; F14a may fail.
- **E-C6 fairness:** share of honest runs (C1, C10, C11) with at least one open question of kind `none`, and the median open questions per honest run. Not pass/fail; it is the number the pilot has to beat with real students.
- **E-C7 cost of passing:** per arm, effort (student characters typed and outside calls) against composite_v2, C13 per round. Pass is a shape: no outside arm reaches the honest median composite_v2 with less student effort than the honest median. Planner prediction: holds. If C13 sits below the honest effort line, that is the headline weakness.

### B.4 Exclusions and reporting
Runs that fail `finalize`; C11 runs with an essay under 400 words; any run whose `law1` audit shows more than 2 violations (reported, not silently dropped). Failed or stuck relay runs are rerun once with the same id and reported. No result is removed because it is inconvenient.

## §C. Amendments
Pre-run amendments (made while executing P0, recorded here, none changes an endpoint):
1. **Run count.** The plan says 66 existing runs. `v04/runs/` holds 60 (C1–C10, n = 6 each). All P0 numbers are on 60.
2. **Trail swap reuses essay-only judge calls.** For each hybrid, the claim list (`claims`) and the citation check (`cite`) depend only on the essay, so they are taken from the essay owner's v0.4 report (temperature 0, same inputs). The new LLM calls are the ancestor and change judgements, which are the ones that depend on the trail. This is a cost saving and also makes the claim lists identical across matched and swapped versions.
3. **J1 (deepseek-reasoner) failed and is skipped.** Smoke test on one run: the `claims` call works without json mode; the `ancestor` call returned either empty content (token budget 700×8) or a dropped connection (`RemoteProtocolError`, token floor 24,000) on two repeats. Fallbacks tried: no json mode, larger token budget. `demo/llm.py` was not edited. J1 is recorded as **not run**. O5 is therefore answered by J2 (Claude judges) alone.
4. **Blind LLM read** was run as written (one call per essay, 60 calls).

P1 amendments (made while building the tooling, before PREREG §B and before any P3 run):
5. **Timing results on the 60 existing runs (E-B1).** Re-scoring with the timing rule changes honest composites by 0.3 points on average (C1 and C10 pooled; limit 10, stop at 15), so the rule is fair as specified. Prediction was about 5, so this was lower than predicted. `composite_v2` is defined as the no-struct composite with `claim_v2` in place of `claim` (the same basis as `composite_nostruct`); `composite_v2_struct` is also written.
6. **Check snapshots count as drafts** (`drafts[].check = true`) so the v0.4 change lineage and the birth-turn search treat them like saved drafts. A check adds one student turn of kind `check`. A check computes the full report (including citation checks) so that per-round `composite_v2` can be stored in `session.checks`; the student sees only the questions.
7. **Answers.** `lineage.student_statements` now also takes turns of kind `answer` (label "answer to a question"). No v0.4 run has such a turn, so v0.4 reports are unchanged.
8. **Attacker prompts changed after the live smoke test** (`DRY-C13`, `DRY-C14`, in `v04/dryrun/`, which are debugging runs and not results): the operator is shown the Room's reply to its last action; reads of locked or already-read passages count as refusals (stop after 8 in a row); the loop operator must check at least once before finishing; the stubborn operator must do at least 6 research actions; both are told to write as a student and never mention the essay, the report or the rules to the assistant; the loop cap is 80 actions. An action trace (names only) is written to `<sessions>/<id>-trace.txt`.
9. **Smoke-test observation (not a result).** `DRY-C14` (stubborn): all 7 claims it was asked about ended as `explained_after` or `none`, composite_v2 34.9. `DRY-C13` (loop, white-box): composite_v2 78.1 with 14 of 21 claims `derived`, at 45 student turns, 24 reads and 1 check round. The operator did the research first, saved drafts late (turn 58), then rewrote and narrated before submitting. If this holds in P3 it is the E-C7 headline: the white-box attacker can reach a high composite, but only by doing about the work an honest student does. Hand check of 5 claims' birth turns: correct.
10. **F14 dev numbers** (looked at on dev runs only, to fix bugs): C1-1 F14b 0.70, F14c 0.87; C8-1 F14b 0.62, F14c 0.00. Test-set runs (-3 to -6) are refused by `derive.py` until its sha256 is written into §B.
11. `effort.py` reports `outside_calls = null` for the 60 v0.4 runs (they predate the `run` field in the call log) and `0` for C1, C2, C10 and C11 by construction.
12. After the hash was written into §B, `derive.py C1-3` was run once to confirm that the guard accepts a frozen file. That is the only test-set F14 number computed so far; it was computed after the freeze, so it stands (C1-3: F14b 0.69, F14c 0.95).
