# Blind question preregistration (T-009)

**Status:** preregistered protocol for review, written 2026-10-25. **No ratings have been collected.** This document is fixed before the first rating; every change after that is a dated deviation in §12. It does not report a result and must not be cited as evidence.

**Scope.** This registration covers two uses of the same procedure:

1. **The pilot validity test:** 50 platform-grounded questions versus 50 essay-only questions, one pair per essay, 50 essays (OL-026).
2. **The walkthrough rehearsal:** a small descriptive rehearsal with four pairs, run inside the [nursing walkthrough](nursing-walkthrough-protocol.md). It tests whether the procedure can be run without revealing the condition and gives the teacher a concrete task. It is **not** the 50-vs-50 result and cannot be reported as one.

**Not in scope.** Student understanding, learning, authorship, honesty, the accuracy of the receipt bands, and the quality of any Coach answer. The test rates questions, and only a teacher's judgment of their usefulness. No student takes part, no student answer is collected, and no model or person grades a Coach answer. Student understanding is outside what this test can see (receipt.md §2 item 10; law 5).

---

## 1. Research question and hypothesis

**Question.** For the same final essay, is a teacher more likely to say they would ask a question generated with the student's platform trail than a question generated from the essay alone?

**H1 (directional).** The platform-grounded question is rated "would ask" more often than the essay-only question, pair by pair.

**H0.** There is no direction to the difference; the platform-grounded question is not more often rated "would ask".

The test is one-sided because the product claim is directional: the trail should make the questions more useful to the teacher, not merely different. A two-sided result is not the primary outcome, and a difference in the other direction is reported as an essay-only win under §6.

**What a win would mean.** The platform questions were rated more useful by the named teacher in this sample. It would not prove that students understand more, that the receipt ends disputes, or that any student did or did not use outside help.

---

## 2. Conditions and comparability

| | **Platform-grounded (P)** | **Essay-only (E)** |
|---|---|---|
| Assignment brief | Same brief | Same brief |
| Final essay | Same bytes | Same bytes |
| Source list | Same titles | Same titles |
| Student's claim list (their words) | Yes | No |
| Paragraph → claim links | Yes | No |
| Grounding items: claim text plus anchored block excerpts, up to 6, each excerpt ≤ 400 characters | Yes, as used by the receipt compiler | No |
| Coach answer text or Coach outcome counts | No; the current receipt question path does not use them for these candidates | No |
| Receipt bands, summary, seal, event log | No | No |
| Student identity, teacher identity, marks | No | No |
| Model, backend, parameters | Same | Same |
| Output shape | One pillar; about the idea or the student's choice; 5–30 words; answerable in about 30 seconds; no question about the trace or where an idea came from | Same |
| Attempts | At most 2, same retry rule | At most 2, same retry rule |
| Wording filter | Same filter; failures replaced before rating | Same filter; failures replaced before rating |

**Same essay/context constraints.**

- The two questions for an essay are generated and rated against the **same final essay** and the **same assignment brief**. Neither arm sees the other arm's output.
- The teacher sees both questions for an essay together, in the randomised order, with the essay and no receipt. The receipt's bands, summary and chain are hidden during the blind portion so the platform context does not leak into the rating.
- Both questions are rendered identically: same font, spacing, length of answer box, and no label that could reveal the arm.
- Neither question shows its grounding IDs. The teacher rates the question text, not its citation format. This prevents the rating from rewarding internal IDs or penalising the essay-only arm for lacking them.
- The same teacher rates both arms in the same session. No teacher rates only one arm.
- The same time limit and the same free-text prompts apply to both arms.

**The treatment is the context.** P is allowed to use the trail; E is deliberately limited to the submission alone, which is the strongest comparator a teacher would have without the platform. The essay-only prompt is not a weak prompt: it gets the same model, the same pillar rule, the same length rule and the same number of attempts. Only the context block differs.

**Question selection for the primary test.** Each essay contributes **exactly one P question and one E question** to the primary analysis:

- P: the first question in the receipt compiler's fixed candidate order for that essay that passed the wording filter and was generated.
- E: the first question returned by the essay-only prompt (in its fixed order) that passed the wording filter.
- Extra questions are not shown and do not enter the primary outcome. This rule is fixed before generation; it is not a choice made after seeing the questions.
- If an arm has no valid question for an essay, the essay is excluded **before** allocation, and the count is reported. No replacement essay is added after ratings begin.
- The question source, run ID, model/backend and stored artifact IDs are recorded in the session log before rating. `ROOM_LLM=stub` output is a dry run only and cannot enter the primary analysis (T-009 ticket; T-016 handoff).

**Generation implementation is an execution gate.** The essay-only prompt and the key-allocation script do not exist yet. They must be written, versioned and hashed before the pilot, and they must implement exactly this section. Writing them is not part of T-009 and no claim is made that they are ready.

---

## 3. Sample, randomisation and hidden labels

### 3.1 Pilot sample

- **Target:** 50 essays, one pair each, giving **50 P ratings and 50 E ratings** (100 ratings in total). This is the OL-026 target and is not reduced for convenience.
- **Selection before ratings:** if more than 50 consented essays have both questions, select exactly 50 with a seeded random draw before any rating. The rest are held out and are not used in the primary test.
- **Minimum for a win claim:** at least **45 complete pairs** (90% of 50). If fewer than 45 pairs are complete, report the shortfall and call the result **under target / inconclusive**; do not describe a smaller sample as the 50-vs-50 test.
- **No early stopping for a favourable result.** The analysis runs once, after all ratings are frozen. There are no interim looks and no adding essays after seeing ratings.
- **One rater per pilot cohort.** The named pilot teacher rates all pairs. If more than one teacher rates, each is reported separately as an independent replication; ratings are not pooled and the first named teacher's result is the primary one. No post-hoc choice of the "better" teacher.

### 3.2 Walkthrough rehearsal sample

- **Four pairs**, one question per arm per essay, from four different essays not shown as receipts in the qualitative part. The walkthrough protocol names the fixtures.
- **Descriptive only.** Report the counts, the free text and any obvious problem with the procedure. Do not compute a win rule, do not call it a result for the product, and do not pool it with the pilot. Its purpose is to let another person run the procedure without the author and to find leaks or ambiguities.

### 3.3 Balanced randomisation

- **Within each pair:** a seeded coin flip decides whether the P question or the E question is presented first. Across the 50 pilot pairs, the allocation is constrained to **25 P-first and 25 E-first** (24/26 is the maximum permitted deviation and must be reported).
- **Across essays:** the order in which essays are presented is a seeded random permutation, so the arms do not drift with fatigue or practice.
- **Stratification:** the randomisation is stratified by essay only. There is no stratification by student, class, score, language background or question length, because those are not outcomes in this test.
- **Recorded:** the seed, the allocation script version, the script hash and the allocation table are sealed with the key before the session. The facilitator sees only opaque item IDs.
- **Rehearsal:** four pairs, two P-first and two E-first if the four-pair draw allows; report the actual order.

### 3.4 Hidden condition labels

- Item IDs are opaque (for example `Q-001-A`, `Q-001-B`; the prefix is a packet series, not an arm). No sheet, file name, document property, page order, font, colour, spacing, length or answer-box size reveals the arm.
- The key holder, not the facilitator, prepares the packets. The key lists `item_id`, `essay_id`, `arm`, `first_in_pair`, `generated_artifact_id` and is stored offline, outside the repository and outside any synced folder the facilitator or teacher can open.
- The key's SHA-256 is recorded in the session log before the first rating. The key content itself is not in Git.
- The facilitator, observer and teacher do not know the key. The analyst may be the key holder, but opens the key only after the ratings and the analysis script are frozen.
- If a packet reveals the arm, or the facilitator or observer states it, the blind portion stops and no win claim is made (protocol §9; §12 here).

---

## 4. Raters, instructions and the rating rubric

**Rater.** The named teacher. The rater must not have written the questions, worked on the question prompt or seen the key. Record any prior exposure to the product or the cases.

**Instructions to the rater, read aloud.**

> "For each essay you will see two questions. Rate each question on its own. The question is: would you ask this question in a five-minute conversation with this student? Answer yes, maybe or no. There is no correct answer. Rate whether the question would be useful to you for a conversation, not whether the student wrote the essay and not whether the essay is any good. I cannot tell you where the questions came from. You can say you cannot judge a question; that is not a no."

**Primary item.**

| Rating | Meaning | Primary coding |
|---|---|---|
| **Yes** | I would ask this question, as written or close to it | 1 |
| **Maybe** | I might ask it, but I would need to change it or I am unsure | 0 |
| **No** | I would not ask it | 0 |
| **Could not judge** | I cannot form a view from what I have | missing |

- The primary outcome uses **Yes = 1, Maybe/No = 0**. Maybe is reported separately and is never counted as a win.
- Free-text prompts, not used for the primary outcome: "What would you hope to learn by asking it?" and "What, if anything, is wrong with it?"
- The rater is not asked to rate the student, the essay, the receipt or the teacher's own skill.

**Independent compliance check (not the teacher).** Before rating, a person who does not know which arm each item belongs to checks each presented question against the receipt rules:

- about the student's idea or choice, not about the trace or where an idea came from;
- one of the four pillars (reading, logic, writing, communication);
- 5–30 words;
- answerable in about 30 seconds;
- passes the wording filter.

Compliance is a secondary description by arm. A question that fails the wording filter is replaced before rating by the next valid question in the fixed order, and the replacement is logged. A non-compliance on the other checks is not removed after the fact; it is reported, because removing it would bias the comparison.

**No automated grading.** No model scores a question, and no model or person grades a Coach answer in this test. The free-text answers are read by two people for themes; disagreements are resolved by discussion. A single reader is labelled exploratory.

---

## 5. Primary outcome and analysis

**Primary outcome.** The paired difference in the proportion of **Yes** ratings between P and E over the matched pairs:

`difference = (number of P Yes - number of E Yes) / M`, where `M` is the number of complete pairs.

**Primary analysis, fixed before data.**

1. Build the paired 2×2 table over the `M` complete pairs: both Yes, P Yes / E not Yes (`b`), P not Yes / E Yes (`c`), both not Yes.
2. `N = b + c` is the number of discordant pairs.
3. Run the **one-sided exact McNemar test**: under H0, `b` is Binomial(`N`, 0.5); report the exact p-value for `b/N > 0.5`.
4. Report the risk difference `(b - c) / M` with a **95% paired bootstrap percentile interval** (10,000 resamples of pairs, seed `20261025`). If the bootstrap script is unavailable, use Newcombe's paired method and say so; do not choose the method after seeing the result.
5. Report the full table, `M`, `N`, `b`, `c`, the p-value, the difference and the interval, plus the counts of Yes / Maybe / No / could-not-judge by arm.
6. Run the analysis once, after all ratings are frozen. A second person reproduces it from the raw sheets and the key.

**Secondary descriptions, not part of the win rule.**

- Maybe and could-not-judge counts; free-text themes by arm; compliance by arm; the teacher's stated reasons.
- The blinding check: after all ratings, the teacher is asked, for each pair, which question they think came from the platform. Report the number correct out of `M`. If at least **64% of complete pairs** are guessed correctly and a one-sided exact test against 0.5 gives p < 0.05, label the result **possibly unblinded** and require an independent replication before quoting it as evidence. This is a limitation, not an automatic void.
- Prior exposure to the product, and the facilitator's notes on any ambiguity in the procedure.

**No other primary test.** No subgroup win claims, no multiple outcomes, no repeated looks, no changing the outcome, the win rule or the sample after the first rating. Any such change is a deviation and must be reported; it does not become the registered analysis.

---

## 6. Fixed win rule

The rule is applied once, after the ratings are frozen.

### 6.1 Platform-grounded wins if **all** of the following hold

1. **Complete pairs:** `M ≥ 45`.
2. **Discordant pairs:** `N = b + c ≥ 15`.
3. **Direction and exact test:** `b > c` and the one-sided exact McNemar p-value is **< 0.05**.
4. **Practical difference:** `(b - c) / M ≥ +0.10` (at least 10 percentage points more Yes among all complete pairs).
5. **Missingness:** at most 5 pairs missing from the 50-pair target; no arm has more than 5 questions marked "could not judge".
6. **Compliance guard:** the P arm's pass rate on the independent "about the idea, not the trace" check is not more than 5 percentage points below the E arm's, or both arms pass at least 95%.
7. **No condition leak:** the key was not opened early and no label was revealed. A leak stops the blind portion and voids the win claim; it does not convert into a loss.

### 6.2 Essay-only wins if the mirror holds

`M ≥ 45`, `N ≥ 15`, `c > b`, exact one-sided p < 0.05 in favour of E, `(c - b) / M ≥ +0.10`, the same missingness and compliance conditions, and no leak. This is a real possible outcome and is reported plainly.

### 6.3 Otherwise

The result is **no difference / inconclusive**. In particular:

- A tie in the Yes rate is not a win.
- `N < 15` is inconclusive even if the point difference is large, because the exact test has too little information.
- `M < 45` is under target and inconclusive; it is not relabelled "the walkthrough result".
- Missingness over 5 pairs is inconclusive.
- A leak makes the blind test void, not a win for either arm.
- A possibly unblinded result (at least 64% of complete pairs guessed correctly, §5) is reported with the limitation and needs replication.

### 6.4 Ties, Maybe and missing answers

- **Both Yes** or **both not Yes** is a concordant pair: no difference for that essay. It stays in `M` for the risk difference but not in `N`.
- **Maybe** is not a Yes. A pair with P Maybe and E No is concordant at the primary coding (both 0); report it in the descriptive counts so the reader can see the near-miss.
- **Could not judge**, a blank sheet, or a missing question is **missing**: the pair is excluded from `M`. It is never imputed, never counted as a No, and never replaced after ratings begin.
- If an item is missing because the generator produced no valid question, the essay is excluded **before** selection. If it goes missing after selection, it counts against the missingness rule.

---

## 7. Sample-size rationale

The 50-pair target is fixed by OL-026 and by the pilot design; it is not chosen after seeing any ratings. Its limits are stated here so the result is not over-sold.

[ASSUMPTION: exact binomial calculations below; independent pairs; not a simulation of the real clustering, because there is one pair per essay.]

- With `N = 50` discordant pairs, the one-sided exact test reaches p < 0.05 at 32 or more pairs favouring P (alpha 0.0325); power is about 0.86 if 70% of discordant pairs favour P, and about 0.97 at 75%.
- With `N = 30`, the test needs 20 or more; power is about 0.73 at 70% and 0.89 at 75%.
- With `N = 25`, it needs 18 or more; power is about 0.51 at 70% and 0.73 at 75%.
- With `N = 20`, it needs 15 or more; power is about 0.42 at 70% and 0.62 at 75%.

So the pilot can show a clear preference (roughly 70–75% of discordant pairs) if enough essays are discordant, but it is underpowered for a small difference. An inconclusive result is a possible and reportable outcome and is not a failed session. If the founder wants reliable evidence about a difference smaller than about 20 percentage points, the sample must be fixed larger **before** the pilot; it cannot be enlarged after a disappointing look. The walkthrough's four pairs cannot support any win rule and are not used in this calculation.

**Why one question per essay.** One pair per essay keeps the 50-vs-50 target literal and the analysis paired and simple. Taking two or three questions per essay from fewer essays would add clustering without increasing the number of independent essays, and would make the effective sample smaller than it looks.

---

## 8. Sealed condition-key procedure

1. **Before the session,** the key holder runs the versioned allocation script with the pre-recorded seed. It writes two files: an allocation table (item IDs, essay IDs, arm, first-in-pair, artifact IDs) and the packet manifest. Both are stored offline, outside the repository.
2. **Hash and log:** the key holder computes SHA-256 of the allocation table and records the hash, the seed and the script hash in the session log before any rating. The log entry contains no arm information.
3. **Packets:** the key holder prepares the printed or PDF packets from the manifest. Every packet uses the same layout; metadata is stripped; file names are opaque; no arm word appears anywhere the teacher or facilitator can see.
4. **Handover:** the facilitator receives only the packets and the manifest of item IDs in presentation order. The facilitator does not receive the allocation table or the key.
5. **Ratings frozen:** after the last sheet is collected, the facilitator records the time and hands the sheets to the key holder. No sheet is changed after this point.
6. **Analysis script frozen:** the analyst hashes the analysis script and the win rule before the key is opened. The hash is recorded.
7. **Open the key:** the key holder re-computes the key hash, confirms it matches the pre-session value, and only then opens the allocation table. If the hash does not match or the key was opened earlier, the blind test is void.
8. **Join and analyse:** the analyst joins the sheets to the key and runs the frozen script. A second person repeats the join and the counts from the raw sheets and the key and confirms the numbers.
9. **Publish the key and the result:** after the analysis is frozen, the key, the raw rating table (opaque IDs only), the analysis script and the output are archived with the study record. The result and every deviation are reported together.
10. **Deviation log:** any change to the packet, the order, the sample, the rubric, the outcome, the win rule or the analysis after the first rating is dated, reasoned and reported. No change to the win rule after the first rating is permitted; a change makes the result exploratory.

---

## 9. Distinguishing teacher usefulness from student understanding

- **What is measured:** the teacher's judgment that a question would be worth asking in a five-minute conversation. This is a rating of the question, not of the student.
- **What is not measured:** whether the student understands the work, learns anything, wrote the essay, used outside help, or would answer well. None of those is an outcome here.
- **Coach answers:** the receipt records what happened after a Coach question (answered, revised, disagreed, declined) as facts. Those outcomes are not grades and are not scored in this test. No model grades them, and no person grades them here.
- **The conversation is the gate.** Law 5 says the trace is evidence of the student's thinking and of where to ask; the conversation is what settles a human decision. This test only checks whether the questions are worth that conversation. It must not be reported as showing that students understood more.
- **A future understanding study** would need its own preregistration, consent, outcome and analysis. It could not reuse these ratings as a substitute, and it must not introduce automated grading of student answers under the product laws.

---

## 10. Blinding and leak checks

- The teacher is told the test compares two ways of choosing questions, not which is which. They are asked not to try to guess during the task.
- After the ratings, the guess check in §5 is run. A high accuracy is reported; it is not hidden.
- The facilitator logs any moment when a label could have been inferred: a file name, a metadata property, a question that mentions an internal claim ID, a packet with different margins, or a comment from the observer.
- If the observer, facilitator or teacher sees the key before the ratings are frozen, the blind test is void and the session is reported as unblinded.
- The analysis reports the key hash and the time it was opened.

---

## 11. Execution gates and stopping conditions

**Gates (all required before the pilot).**

- T-017 rendered receipts exist and have been read; the question path produces stored artifacts from an approved live backend.
- The essay-only prompt, the allocation script and the analysis script exist, are versioned and hashed, and implement §2–§8.
- The named teacher is recruited and consented; the school/ethics approvals in the walkthrough protocol §3 are in place.
- The 50 essays are consented, have both valid questions, and are selected before ratings.
- The protocol, rubric, win rule and sample are frozen; the key is sealed and hashed.
- The wording filter passes on every presented question; replacements are logged.

**Stopping conditions.**

1. Consent, approval or quote permission missing: do not start or do not record.
2. Condition label revealed: stop the blind portion; no win claim.
3. Key opened early or hash mismatch: blind test void.
4. Real student data appears outside the consented set: stop and delete the note.
5. Teacher withdraws or asks to stop: stop; no persuasion.
6. Fewer than 45 complete pairs in the pilot: report under target / inconclusive.
7. More than 5 missing pairs: inconclusive.
8. Stub-only or unapproved question output: dry run only; no blind result.
9. Analysis script or win rule not frozen before the first rating: stop.
10. Teacher fatigue or the agreed session limit: stop; unused items are missing, not rushed.

---

## 12. Deviations and amendments

| Date | Change | Reason | Made before or after first rating? | Effect on the registered analysis |
|---|---|---|---|---|
|  |  |  |  |  |

No row is filled at the time of writing. After the first rating, a change to the outcome, win rule, sample or analysis is reported as a deviation and makes the affected result exploratory; it is not presented as the preregistered test.

---

## 13. References

- `design/evaluation.md` §4 (human sessions and the blind test) and §6 (nursing walkthrough).
- `design/receipt.md` §§1–5 (job, layout, question rules, wording filter) and §8 (nursing example).
- `design/build-plan.md` M2 and §4 (pilot gate).
- `docs/OPEN_LOOPS.md` OL-026 (50-vs-50 and ethics), OL-034, OL-040, OL-041.
- `docs/handoffs/2026-10-24-T-016-receipt-compiler.md` (question candidates, grounding, stub-not-evidence).
- [Nursing walkthrough protocol](nursing-walkthrough-protocol.md); [results template](nursing-walkthrough-results.template.md).
