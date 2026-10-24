# Pilot protocol: real students, a live oral (DRAFT, design only)

Status: DRAFT 2026-10-17 · Owner: Cyrus · Written by: Sonnet executor, following PLAN-v0.5 P6 · Nothing here has been run, approved or sent to an ethics office.
Why this exists: [RESULTS-v0.5.md](RESULTS-v0.5.md) tests the report on simulated students. It cannot test the third part of the claim ("a person hears the answer") or how real students behave. This protocol does.

## 1. What the pilot has to answer
The claim: *Every idea in the submission has a derivation the student built in the Room. Where one is missing we ask how they got there, and a person hears the answer. Every path leads either to visible thinking or to an open question, and no path is both cheap and silent.*

| Part | Question | Primary measure |
|---|---|---|
| 1 Fairness | Do honest students rarely get a question they can't answer? | Open items per honest student (E-C6 on real trails); share who answer the top 3 live |
| 2 Economics | Does outside help leave gaps, or cost about as much as the work? | E-C5 / E-A1 on real trails; effort against composite_v2 (E-C7) |
| 3 Gate | Asked live, do the questions separate people who built the work from people who didn't? | Blind-rated live answers, honest vs outside-help conditions |

## 2. Conditions (6–10 students each; recruit 24–30 in total)
| Code | Condition | Instruction to the student |
|---|---|---|
| H | Honest | Do the essay in the Room. Use the course archive through the Room. No outside AI. |
| O | Outside, free | "Use any outside AI however you like, in any order. Then submit through the Room." Consented and paid. Research framing. No grades at stake. |
| T (optional) | Thesis first | As H, but state your position before asking for any source. |

Students are assigned to conditions at random. Nobody is told the report's rules in advance; condition O students are told only that the Room will ask questions about their work afterwards. If a group of O students is later shown the rules, that is a separate follow-up condition (the real version of the white-box attacker).

## 3. Materials
- The Room as built for v0.4–v0.5, with the course archive for the pilot (the same archive format; a real course's graph if Cyrus can supply one).
- The essay question: one question per course, 500–800 words, inline citations to archive passages.
- Time: one 90-minute session in a lab, or two 45-minute sessions. Time on task is recorded for every condition.
- The report is generated after submission. The student sees only the questions, never a score.

## 4. Measures
1. **Open items per student:** the number of items in the report; the number of claims of kind `none`; the number of `explained_after`. For H, this is the number the simulation says is about 6 (Sonnet students) to 28 (the weakest honest simulation). The pilot sets the real figure.
2. **The live gate.** A TA (or lecturer) asks each student the report's top 3 questions for up to 5 minutes, in person or by voice call. The TA does not know the student's condition. Answers are recorded with consent and rated blind on a 0–4 scale by two raters for "shows how the point was reached", with disagreements settled by a third.
3. **E-A1 / E-C5 replicated on real trails:** the trail-swap AUC and F14b/F14c between conditions H and O.
4. **Effort:** student turns, characters typed, reads, check rounds, time on task, outside tools used (self-report plus questions at the end).
5. **Student experience:** a short survey after the session and a 10-minute interview for a subset: Did you feel helped? Did you feel watched? Did the questions feel fair? What would you have done differently if you were graded?
6. **Subgroups for fairness:** English as a second language, self-reported anxiety about oral exams, and students who ask for the accessibility route (below). Reported separately; no subgroup is dropped for being small.

## 5. Ethics, law and product rules
- **Consent and ethics:** informed consent, voluntary participation, the right to leave without penalty, a named ethics contact at the host institution. Approval is needed before any recruiting.
- **Law 7 (students own their process data):** the student can see and export their own trail. The school receives only derived signals (counts, question lists), never the raw trail. Research data is stored without names under a participant code.
- **Law 6 (comprehension tiers, never a verdict; humans decide):** no output in the pilot has any academic consequence. The report produces questions and the TA records the answers. No student is graded, flagged or reported on the basis of any measure here.
- **Accessibility route:** every live question can be answered by voice, in writing, with extra time, or through a translator. Students choose; the choice itself is not scored. A student who prefers not to speak can answer the same questions in writing, and those answers are rated the same way.
- **Wording:** all student-facing text speaks of "questions about your work" and "how you got there". It does not promise the absence of anything and does not use words of suspicion.
- **Outside-help condition:** O students are told the research purpose, paid the same as H students, and told no one is judged for using outside help.

## 6. Success criteria (set before recruiting, mirroring §1)
| Part | Success | Failure that stops the plan |
|---|---|---|
| 1 Fairness | In H, at least 80% of top-3 live answers are rated 3 or 4 ("shows how the point was reached"), and no subgroup is below 60% | Fewer than 60% of H answers rated 3 or 4: the questions are not fair enough to build on |
| 2 Economics | In O, median composite_v2 below the H median by at least 20 points, and no O student reaches the H median with less typed effort | Some O students reach the H median with less effort and their live answers are also rated 3–4: that path is both cheap and open, and the design needs rethinking |
| 3 Gate | Blind-rated live answers separate H from O: AUC at least 0.80 on the mean rating of the top 3 answers | AUC below 0.65: live questions do not separate the groups |

A cheap-and-silent path means a student who scores high, typed little, and when asked cannot say how they got there; that finding goes first in the write-up, whichever way it falls.

## 7. What Cyrus needs to supply
- An instructor and a course (with a course graph or at least the readings), willing to give a lab hour or two.
- An ethics contact and the approval route at the host institution.
- A TA or two for the live questions, and two blind raters (not the TAs).
- Compensation for participants (the plan assumes equal pay across conditions).
- A decision on language: English only, or Cantonese/Mandarin questions with translation.

## 8. Order of work
1. Pick the course and the essay question; build the archive and graph (or use the existing mock one for a dry run).
2. Dry run with 3 volunteers (not data), to fix timing and the TA script.
3. Ethics approval and recruiting.
4. Sessions, then the live oral within 48 hours of submission.
5. Blind rating, then analysis exactly as written in §4 and §6, with predictions recorded before the first session.

## 9. Open questions
- How much of the honest low-scoring seen in RESULTS-v0.5 (C11, thinking silently) appears with real students? This decides how many questions an honest student gets.
- Does the live gate separate H from O when O students are the ones who copy an outside essay and answer by reading it out? The protocol's blind raters score "shows how the point was reached", not fluency.
- Whether to run the white-box version (O students shown the rules) in the first pilot or a second one.
