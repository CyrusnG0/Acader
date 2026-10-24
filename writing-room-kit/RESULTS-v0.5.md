# Results — v0.5 "Is it working as designed, or luck?"

Run 2026-10-17 · 60 existing simulated runs (C1–C10) re-examined with four controls, plus 24 new runs (C11–C14, 6 per arm) · pre-registered in [PREREG-v0.5.md](PREREG-v0.5.md) (§A before the controls ran, §B before any new run) · scores in `v04/reports-v05/_controls.json`, `_scores.json`, `_curve.json`
Simulated students, tiny n, one API vendor plus Claude workers, one planner-defined feature. This tests a mechanism and says nothing about real students or the live oral.

**First line, because it matters most:** the separation is not luck and not just topic, and no outside path got through cheaply. But three results are weaker than the story we were telling. (1) The honest DeepSeek student (C11) scores 49, far below the honest Sonnet students (C1 92, C10 87), so "honest" scores depend on how much the student thinks out loud in the Room. (2) The essay alone separates the arms by writer model, more sharply than the trail does, so any claim must rest on the model swap, which holds. (3) The white-box loop attacker passes only barely under the pre-registered test (AUC 0.81, CI 0.61–0.96) and the figure is 0.76 on the four runs that completed a check.

## Outcome per objection
| # | Objection | Verdict | Evidence |
|---|---|---|---|
| O1 | AUC 1.00 at n = 6 is luck | **Answered** | Exact permutation p ≤ 0.012 for every AUC ≥ 0.95 (0.0011 for 6 vs 6). Two F13 comparisons (vs C9, n = 3) gave 0.012, so my "p < 0.01 for all" was slightly wrong. |
| O2 | The judge likes on-topic essays; the trail link doesn't matter | **Answered, with a caveat** | Pairing an essay with another honest student's trail drops composite_nostruct (matched 90 vs swapped 77; AUC 0.96, CI 0.87–1.00). A mirror check (honest essay + outside trail) falls to 48. Caveat: a stolen honest trail gives an outside essay +15 points (55 → 70), more than I predicted. |
| O3 | You're separating model style, not honesty | **Partly answered** | The confound is real: essay stylometry alone separates the arms (AUC 0.00–0.03 on sentence length). The model swap breaks it: with DeepSeek as the honest student and Claude as the outside writer, composite_v2 still separates them (AUC 0.89, CI 0.64–1.00, p 0.013) while the style direction flips sign (sentence length: honest Sonnet shorter, honest DeepSeek longer). Caveat: C11's absolute scores are low (see below). |
| O4 | The attacker didn't know the rules | **Partly answered** | Stubborn (answer the questions through the outside writer): all 6 runs end with ≥ 15 open items, composite_v2 22–45. Loop (white-box, revise with the questions): composite_v2 37–72, median 52 vs honest 86; it typed as many characters as an honest student (6.4k vs 4.7k median) and made ~60 outside calls. Caveat: no loop run used more than 1 of its 3 check rounds. |
| O5 | One judge model | **Partly answered** | Claude judges on 24 runs agree with the DeepSeek judge (Spearman 0.87; AUC honest vs relay 1.00 under both). The second DeepSeek model (reasoner) could not be run (§C item 3). |

## P0 controls (60 existing runs)
| Control | Result | Prediction | Verdict |
|---|---|---|---|
| A.1 permutation, composite_nostruct, C1 vs C4/C6/C7/C8/C9 | AUC 1.00, p = 0.0011 each; C1 vs C5 0.89, p = 0.013 | p < 0.01 for AUC ≥ 0.95 | Held for composites; F13 vs C9 (n = 3) p = 0.012: **slightly wrong** |
| A.1 smallest AUC at p < 0.05, 6 vs 6 | 0.78 | — | — |
| A.2 E-A1 trail swap, matched (C1 + C10) vs S1 | composite_nostruct **0.96** (CI 0.87–1.00); claim component 0.84 (CI 0.66–0.98); C1 alone 1.00 / 0.90; C10 alone 0.86 / 0.75 | ≥ 0.80; weaker for C10 | **Held.** Stop rule (< 0.70) did not fire |
| A.2 E-A2 claim-lineage drop | 88.3 → 73.5 (−14.8, CI 6.9–22.8) | — | — |
| A.2 E-A3 stolen honest trail on a relay essay | composite_nostruct 69.8 vs the same essays' own 54.7; claim lineage 60.4 | claim < 40 | **Wrong** |
| A.3 essay-only | Stylometry separates (sentence length 0.00–0.03 vs C3, C4, C6–C9); blind LLM read does not (0.42–0.58) | ≥ 1 stylometric AUC ≥ 0.80 | Held (the blind-read result was not predicted) |
| A.4 J1 deepseek-reasoner | Failed; skipped | — | — |
| A.4 J2 Claude judges, 24 runs | Spearman 0.87; AUC honest vs relay 1.00 under both judges | ≥ 0.6; ≥ 0.80 | **Held** |
| E-B1 timing rule, honest drop | 0.3 points (C1 + C10) | about 5; limit 10 | Held (lower than predicted) |

Why the swapped honest essays still score ~74 on claims: all students answer one question about one archive, so honest students converge on similar claims. The trail link is real but partly shared across honest trails. The report is a question generator, and the consequence of this overlap is that a stolen, topically matching trail earns partial credit.

## P3 per-arm table (composite_v2 = no-struct composite with claim_v2, mean ± sd, 0–100)
| Arm | n | composite_v2 | Claim_v2 | Source | Cite | Change | Items in report (mean) |
|---|---|---|---|---|---|---|---|
| C1 honest (Sonnet, read first) | 6 | 92 ±5 | 89 ±12 | 100 ±0 | 97 ±3 | 82 ±21 | 5.7 |
| C10 honest, thesis first | 6 | 87 ±2 | 85 ±6 | 100 ±0 | 91 ±5 | 69 ±21 | 11.2 |
| **C11 honest, DeepSeek operator** | 6 | **49 ±12** | 8 ±11 | 100 ±0 | 74 ±10 | 54 ±38 | 26.2 |
| C6–C9 relay (v0.4) | 24 | 38 / 45 / 55 / 47 | 22 / 21 / 31 / 13 | 44 / 55 / 78 / 64 | ~80–88 | 25 / 44 / 55 / 67 | 29–39 |
| **C12 relay, Claude writes the essay** | 6 | 36 ±8 | 13 ±9 | 44 ±11 | 84 ±5 | 29 ±15 | 40.5 |
| **C13 loop (white-box)** | 6 | 54 ±12 | 28 ±16 | 94 ±15 | 82 ±4 | 35 ±33 | 29.8 |
| **C14 stubborn** | 6 | 35 ±9 | 11 ±10 | 41 ±10 | 81 ±7 | 40 ±32 | 39.2 |

## Endpoints
| # | Endpoint | Result | Prediction | Verdict |
|---|---|---|---|---|
| E-C1 | composite_v2, C11 vs C12 (model swap) | AUC **0.89** (CI 0.64–1.00), p = 0.013 | ≥ 0.80 | **Met**, wide CI. Context: C1 + C10 vs C12 is 1.00. |
| E-C2 | Essay-only baselines, C11 vs C12 | sentence length 1.00, citations/100 words 0.00, blind LLM read **0.04** | They separate less than on C1 vs relay | **Wrong.** The essay alone separates the two writer models almost perfectly, more than the trail does. The direction flips against v0.4's (sentence length: C1 vs relay 0.00, C11 vs C12 1.00), which is what a model-style signal would do and what the trail score did not. |
| E-C3 | composite_v2, honest (C1 + C10 + C11) vs C13 after its final round | all 6: AUC **0.81** (CI 0.61–0.96), p = 0.015. Runs with ≥ 1 check round (4): **0.76** (CI 0.54–0.94), p = 0.059. C1 + C10 only vs those 4: 1.00 | ≥ 0.80 (executor note: may fail) | **Met at the margin on the pre-registered set, not met on the 4 that checked.** Two C13 runs (C13-1, C13-2) never completed a check even on rerun (operator stuck on refused reads). |
| E-C4 | C14 open items ≥ 3 and composite_v2 < 60 | 6/6: open items 15–22, composite_v2 22–45 | every run | **Met** |
| E-C5 | F14, test set, honest (C1, C10, C11; 12) vs outside (C6–C9, C12–C14; 28) | F14b parentage **0.88** (CI 0.75–0.97), F14c grounded chains **0.85** (CI 0.69–0.98), F14a step size **0.28** (honest steps are larger, not smaller) | ≥ 0.80 on F14b or F14c; F14a may fail | **Met** on F14b and F14c; F14a fails as allowed |
| E-C6 | Fairness: honest runs with ≥ 1 claim of kind `none` | C1 5/6, C10 6/6, C11 6/6. Median `none` claims per run: 1.5, 2.5, 18.5. Median report items per run: 5.5, 11.5, 28 | not pass/fail | Reference numbers for the pilot |
| E-C7 | Cost of passing: any outside run at/above the honest median composite_v2 with less typed effort | **None** (0 of 42 outside runs, v0.4 arms included), with the honest median taken over C1 + C10 + C11 (85.8) or over C1 + C10 only (88.0) | holds | **Held** |

### Cost of passing (median per arm)
| Arm | composite_v2 | Student characters typed | Student turns | Outside-AI calls |
|---|---|---|---|---|
| C1 | 92.7 | 5,807 | 42 | 0 |
| C10 | 86.5 | 5,924 | 41 | 0 |
| C11 | 49.1 | 1,157 | 60 | 0 (it simulates the student) |
| C6 | 36.3 | 976 | 23 | not logged in v0.4 |
| C7 | 42.0 | 1,158 | 34 | not logged |
| C8 | 54.6 | 2,524 | 49 | not logged |
| C9 | 50.1 | 1,918 | 51 | not logged |
| C12 | 33.5 | 498 | 30 | 34 |
| **C13** | 51.8 | **6,415** | 48 | 63 |
| C14 | 36.2 | 3,121 | 18 | 18 |

C13 (the loop attacker) typed as much as an honest student, made about 60 outside calls, and still scored well below the honest median. That is the shape the claim needs: no outside path reaches honest scores for less than honest effort.

Loop trajectory (check round 1 vs the final submission): C13-3 70 → 53, C13-4 59 → 51, C13-5 65 → 72, C13-6 82 → 65. Revising after the Coach's questions mostly added new claims with no earlier step, so the final report was worse than the first check in three of four runs. Every operator stopped after one check (limit three).

## Ablation (honest vs all 7 outside arms; AUC)
| Drop | C1 + C10 as honest | C1 + C10 + C11 as honest |
|---|---|---|
| nothing | 1.00 | 0.87 |
| claim_v2 | 0.97 | 0.92 |
| source | 1.00 | 0.80 |
| cite | 1.00 | 0.89 |
| change | 1.00 | 0.87 |

No single component carries the result when the honest side is C1 + C10. With C11 in, source lineage carries a lot (0.87 → 0.80 without it), and dropping the claim component helps (0.87 → 0.92) because C11's claim scores are low. Citation correctness separates nothing, again.

## Mechanism traces (3 runs)
- **C14-3 (stubborn, composite_v2 22):** claim_v2 0 vs honest 87; source 42 vs 100; change 0 vs 75. Its three lowest claims were born in the single draft at turn 15 with no ancestor, and several cited passages were never read or read after the claim existed. The answers it typed afterwards are `explained_after`, not derivation.
- **C13-5 (loop, the best attacker, composite_v2 72):** source 100 and change 77, matching honest, because the operator picks every cited source and talks through the changes. Claim_v2 stays at 48: the claims about elasticity and rent burden still have no earlier step. The loop attacker is held back on exactly the component that records derivation.
- **C11-2 (honest DeepSeek operator, composite_v2 34):** claim_v2 0. The claims about household counts and rent premiums are in the essay but the operator never said them in the Room; its essay was written in one call from notes. The trail shows reading but no thinking aloud. This is the cleanest evidence that the report measures visible thinking, not honesty, and it is also the largest limit on the "honest" side of the claim.

## What this does and doesn't show
- **It shows:** the v0.4 result survives a permutation test, a trail swap, a second judge vendor, a writer-model swap, and two adaptive attackers. No outside path reached the honest median composite_v2 for less than honest effort.
- **It doesn't show the live gate.** Nothing here asks a person a question. The part of the claim that a person hears the answer is untested (see PILOT-PROTOCOL.md).
- **Honest scores depend on how much the student says.** C11 had 60 student turns and 1,157 characters typed against C1's 42 turns and 5,807 characters. A real student who thinks silently and writes a good essay would look like C11. The report's questions for that student would be fair ("how did you get there?"), but the score would be low. The pilot has to measure how often that happens with real students. C11's operator is a weak simulation of an honest thinker, and I would not read its 49 as a rate.
- **Stolen trail:** copying a classmate's whole Room trail would earn partial credit. Students own their trail, so a school never sees one, but the point stands for peer-to-peer copying.
- **The loop attacker was weak at looping.** One check round each, two runs where the operator got stuck. A stronger operator might do better. The pre-registered AUC of 0.81 is a marginal pass and should be read that way.

## Limits
- All simulated: AI students, AI operators, AI judges (plus 3 Claude judge workers on 24 runs).
- n = 6 per arm; CIs are wide (E-C1 0.64–1.00).
- One API vendor for the Room, the operators, the judge and the second-stage checks; Claude workers for C12 essays and the 24-run judge swap. J1 (a second DeepSeek model) did not run.
- F14 is defined by the planner; test-split protected, with one test number (C1-3) computed after the freeze to confirm the guard.
- C13-1 and C13-2 never completed a check round even after a rerun (the first attempts are kept in `v04/runs-v05/_attempt1/`).
- C11 hit the 60-action cap in every run (none submitted voluntarily), so its essays were written at the cap; 542–679 words, none excluded.
- Three C12 essays are slightly over 800 words (804, 826, 831); the outside writer was not length-enforced in v0.4 either.
- Law-1 audit on the 24 new runs: 1 violation in 278 assistant turns (0.4%), one run (C13-6, 1 violation, within the 2 limit); source leaks 0.

## For investors / for CLEAR
The system's claim is that every idea in a submission has a derivation the student built in the Room, and where one is missing it asks "how did you get there?" for a person to hear. In a 84-run simulation, honest work with visible thinking scored 87–92 and every outside route had a median of 34–55, and the separation held through a permutation test, a trail swap, a second judge vendor, a writer-model swap and two adaptive attackers. The adaptive attacker that reads the rules and loops on the Coach's questions had to type as much as an honest student and still scored well below one. The same data show the limit: a student who thinks silently gets many questions, so the real test is a pilot with real students and a live oral, which this study does not provide.
