# Results — v0.4 "Does the coherence report separate the four kinds of student?"

Run 2026-10-16 · 30 simulated students (6 per arm, none excluded) · pre-registered in [PREREG-v0.4.md](PREREG-v0.4.md) · scores in `v04/reports/_scores.json`
Simulated students, tiny n, one vendor plays assistant, outside AI and judge. This tests a mechanism and says nothing about real students or the live oral.

## Outcome per endpoint
| # | Endpoint | Result | Verdict |
|---|---|---|---|
| 1 | Sanity: AUC C1 vs C3, composite ≥ 0.90 | **1.00** (CI 1.00–1.00) | Met |
| 2 | **Primary:** AUC C1 vs C4, composite_nostruct ≥ 0.80 | **1.00** (CI 1.00–1.00) | **Met** (v0.3 receipt: 0.33) |
| 3 | Ordering of mean composite C1 > C2 > C4 > C3 | 93.8 > 62.3 > 61.9 > 15.9 | Met on paper, but C2 and C4 are a tie (0.3 points; 55.6 vs 55.2 on no-struct). My prediction "C2 < C4" was also not borne out: they are equal. |
| 4 | C5, AUC C1 vs C5 on composite_nostruct (no threshold) | **0.89** (CI 0.58–1.00) | **My prediction (< 0.70) was wrong.** Covering the swapped-in paragraphs did not fully pass in these runs. See below. |
| 5 | Policy health | law-1: 5 of 355 assistant turns (1.4%, limit 2%); source leaks 0 (see A9); median student turns to a shortlist 2 (limit 3) | Met |
| 6 | Hand audit of 6 reports | **Waiting for Cyrus.** Files in `v04/reports/_audit/AUDIT-1..6.md` (key: `_audit_key.json`, don't open it first) | Open |

## Per-arm table (mean ± sd, 0–100)
| Arm | n | Composite | No-struct | Claim | Source | Cite | Change | Struct | Questions in report (mean) |
|---|---|---|---|---|---|---|---|---|---|
| C1 honest | 6 | 94 ±4 | 93 ±4 | 91 ±9 | 100 ±0 | 97 ±3 | 82 ±21 | 100 | 5.3 |
| C2 lazy honest | 6 | 62 ±5 | 56 ±5 | 31 ±11 | 100 ±0 | 88 ±6 | 21 ±9 | 100 | 23.7 |
| C3 all outside | 6 | 16 ±5 | 19 ±6 | 0 ±0 | 2 ±4 | 87 ±4 | 17 ±36 | 0 | 49.2 |
| C4 partial outside | 6 | 62 ±12 | 55 ±14 | 42 ±25 | 46 ±7 | 85 ±8 | 69 ±11 | 100 | 25.2 |
| C5 partial + covered | 6 | 85 ±5 | 82 ±6 | 66 ±16 | 100 ±0 | 83 ±5 | 96 ±6 | 100 | 14.3 |

Per-run composite_nostruct: C1 88–98 · C2 46–61 · C3 14–30 · C4 36–78 · C5 78–94.

## AUCs (C1 higher than …; 2,000-sample bootstrap)
| Pair | composite | composite_nostruct |
|---|---|---|
| C1 vs C2 | 1.00 (1.00–1.00) | 1.00 (1.00–1.00) |
| C1 vs C3 | 1.00 (1.00–1.00) | 1.00 (1.00–1.00) |
| C1 vs C4 | 1.00 (1.00–1.00) | 1.00 (1.00–1.00) |
| C1 vs C5 | 0.89 (0.58–1.00) | 0.89 (0.58–1.00) |

With n = 6 per arm, "1.00" means no overlap in these 6 runs, not a measured error rate. The closest C4 run (C4-2, 78) sits below the lowest C1 run (88).

## What the report did and didn't separate
- **It separated all three non-covered arms from honest work**, and C4 on the claim and source components, not on the paste signal. C4's swapped-in paragraphs had no ancestor in the Room (claim 42, source 46 against C1's 91 and 100), and the sources they cite were never chosen.
- **The citation check did not separate anything** (C3 87 vs C1 97). The outside AI cites real passages accurately. A correct citation is not evidence of a process.
- **C5 (narrating the swap into the Room) scored 85, between C4 and C1.** It was lifted by source lineage (100) and change lineage (96), because the workers asked for and picked the sources of the swapped-in paragraphs. Claim lineage stayed lower (66 vs 91). **Do not read this as "covering is caught".** The C5 workers were ordinary Sonnet students told to narrate; several paraphrased only loosely, left the assistant's last question unanswered (C5-1, C5-4, C5-5), or submitted an essay whose first and last paragraphs disagree (C5-5, C5-6). A dedicated narrator (an AI with the outside essay in context, answering for the student) was not tested and is the attack we agreed can't be closed by any typed trail. The honest reading is: *in these runs, covering cost real effort and was imperfect, and the report still flagged about 14 questions per run.*
- **C2 and C4 tie.** Lazy honest work and half-swapped work look equally weak on this score. They differ in why: C2's questions are about claims the student never stated (claim 31, change 21); C4's are about sources and claims that never passed through the Room (source 46). The report's questions would be different, not the score.

## Three example question lists (first three of each)
**C1-1 (honest, 6 questions):** "Paragraph 3 says 'Under rent caps, tenants already inside gain while those still outside bear the cost.' This point doesn't appear earlier in your work in the Room. Where did it come from?" · "Paragraph 5 says 'In the same survey, 74 percent would trade for a faster public-housing offer.' …" · "The sentence 'The landlords' association says a hard initial-rent cap is confiscatory… [D5p2]' cites D5p2. Does that passage say this?"
**C4-3 (partial outside, 26 questions):** each swapped-in paragraph's claims ("An elasticity estimate of 0.31 to 0.48 implies a 10 percent cap-induced rent cut removes 3 to 5 percent of stock over five years") come back as "doesn't appear earlier in your work in the Room. Where did it come from?"
**C5-4 (covered, 17 questions):** fewer, mostly about facts the student read but never restated ("About 110,000 households live in subdivided units and pay 15 to 25 percent more per square foot…").

## What the report can and cannot claim
- **Can claim:** *where the final work has no earlier trace in the Room*, as questions for a human. In this simulation it ranked honest, lazy honest, partly outside and all outside work in that order, with no overlap between honest work and the three other arms except the C5 tail.
- **Cannot claim:** that a student understood anything; that work typed into the Room was the student's own thinking (any AI with the same context can type it); that an honest student won't be asked questions (C1 got 5 on average, mostly about figures they read in a passage and quoted, see PREREG design note 1; and a few from judge noise such as the D5p2 citation question in C1-1).
- The live human moment is still the gate (law 5). The report's job is to make that 5-minute conversation sharp.

## Caveats (all disclosed)
- Simulated students. Real students will be messier, slower, anxious or writing in a second language (the "thin honest" attack is untested).
- n = 6 per arm; the C5 bootstrap interval spans 0.58–1.00.
- **Same vendor** plays assistant, outside AI and judge (DeepSeek `deepseek-chat`). Students are Sonnet. The same team designed the test and the product.
- C4 and C5 differ from honest work partly by construction: the outside paragraphs cite sources the worker never requested. A student who picks those sources first is C5.
- **Worker deviations** (kept in): essay length outside the brief in C1-3 (829 words), C4-1 (869), C5-5 (347) and C3-6 (627); C1-3 reported about 14 Room turns (brief: 15–30); C2-1 and C1-2 each finalized more than once and the last file is the one scored. Student turn counts in `runs/*.json` include picks and reads, so the "turns" in the arm briefs are not directly comparable.
- **Not checked:** I did not read the worker transcripts for forbidden-file reads. No worker report mentioned any. Exclusion count: 0 (no C1 or C2 run cited an unread passage).
- **law-1:** all five flagged replies were opposing-claim answers (P-CTR) that attribute a position to a named document (D5, D6, D11) and add detail from an unread document (no numbers, as required). They are by design, so whether they count as violations is a judgement call for Cyrus; the raw rate is reported.
- **Post-hoc amendment A9** (leak check counts echoes of the student's own ids as non-leaks) is in PREREG.
- No claim of accuracy or readiness for real use is made.

## For CLEAR (5 sentences)
We built a governed assistant that only asks questions and offers options, then tested a coherence report on 30 simulated students: honest, lazy, fully outsourced and partly outsourced. The report separated honest work from every other kind it was given, with no overlap in these small runs, because the outsourced paragraphs had no earlier trace in the workspace. A student who also narrated the outside work into the workspace scored closer to honest (AUC 0.89, wide interval), and any typed trail can in principle be imitated by an AI with the same context. So the report doesn't prove understanding; it tells a teacher where to point a short live conversation, and makes learning the cheapest way to be ready for it. We are asking to pilot that conversation with real students and measure it.

## Next
- Cyrus: grade the six `_audit` files (claim-ancestor correctness) and decide PREREG design note 1 (should a `read` of the cited passage count as the ancestor of a factual claim?).
- A dedicated-narrator arm (an AI with the outside essay and the Room's questions in context) is the real test of the agreed limit.
- Pilot with real students; the thin-honest case is the main fairness risk.
- Bookkeeping (STATUS, UPDATE_LOG, CHANGELOG, OL-031) is waiting for your read of this file.
