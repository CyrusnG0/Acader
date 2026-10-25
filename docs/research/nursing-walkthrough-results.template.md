# Nursing walkthrough results: UNFILLED TEMPLATE

> **THIS IS AN UNFILLED TEMPLATE. IT CONTAINS NO RESULTS.**
> It is not evidence, not a summary and not a finding. Fill a copy only after a real session run under the [protocol](nursing-walkthrough-protocol.md). Do not put real student logs, names, numbers, screenshots or essays in this file or in Git. Use role codes only. The filled copy is not committed if it contains anything identifying; the checker decides what summary, if any, goes into UPDATE_LOG.
>
> The walkthrough's blind portion is **descriptive only**. It is not the 50-vs-50 pilot result and must not be reported as one.

**Protocol version:** ____________________  **Preregistration version:** ____________________  **Template version:** 2026-10-25

---

## 1. Session record

| Field | Entry |
|---|---|
| Date (ISO) | |
| Session ID | |
| Facilitator role code | |
| Key holder role code | |
| Observer role code | |
| Teacher role code (no name) | |
| Teacher's prior exposure to the product | none / read about it / used a demo / other: |
| Site / setting (anonymised) | |
| Consent version and date | |
| Quote consent (separate) | yes / no |
| Audio consent | yes / no / not used |
| Ethics / approval reference | |
| Retention date | |
| Receipt render source (commit, engine stamp) | |
| Backend and run ID for question output | |
| Question source | live release run / stub dry run (dry run only: no blind result) |
| Key SHA-256 recorded before session | |
| Key opened at (time) / by | |
| Analysis script hash (rehearsal counts) | |

**Stopping or deviation?** yes / no. If yes, fill §10 before anything else.

---

## 2. Consent confirmation

- [ ] The teacher received the consent form and kept a copy.
- [ ] The teacher was told the cases are fictional reconstructions, not their real file or a real student's work.
- [ ] The teacher was told the session tests the page, not the teacher and not the student.
- [ ] The teacher was told they could stop, skip any question and withdraw.
- [ ] Quote consent: yes / no. If no, do not record verbatim quotes; paraphrase only.
- [ ] Audio deleted after transcription (if used): yes / no / not used.
- [ ] No real student identifiers were seen or transcribed.

**Consent problems or missing approvals:** ______________________________

---

## 3. Materials and rendering check

| Item | Confirmed | Notes |
|---|---|---|
| Case A first screen from `honest-nursing.yaml` | yes / no | |
| Case A details and chain view | yes / no | |
| Case B1 from `ai-expanded-card.yaml` | yes / no | |
| Case B2 from `thin-honest.yaml` | yes / no | |
| Receipt not hand-edited | yes / no | |
| Pending / mismatch state visible if present | yes / no / n/a | |
| Blind packets opaque, no arm labels | yes / no | |
| Balanced first position (actual: __ P-first, __ E-first) | yes / no | |
| Four different blind essays | yes / no | |
| Wording-filter replacements logged | yes / no / none | |

**Rendering or material problem:** ______________________________

---

## 4. Case observations

Use the teacher's own words. Do not write what the teacher "should" have said. Mark prompts with `[prompt]`.

### 4.1 Case A: honest nursing reconstruction

- First reaction: ______________________________________________
- Summary understood as: ______________________________________
- Bars understood as: _________________________________________
- "Untraced is not AI" line noticed: yes / no / after prompt
- "Where to ask" found: yes / no / after prompt
- Span(s) named: _____________________________________________
- Question(s) the teacher would ask: ___________________________
- Details drawer changed the reading? yes / no / unclear. How: ______
- Blind-spot line found: yes / no / after prompt
- Time to first named span (descriptive only): ______ minutes

### 4.2 Case B1: outside expansion inside the student's card

- What the teacher thought happened: __________________________
- What the page could not tell them: __________________________
- Would ask about it? yes / no / maybe. What: ___________________
- Read the untraced sentence as an authorship conclusion? yes / no. Evidence: ____

### 4.3 Case B2: quiet honest writer

- What the teacher thought happened: __________________________
- What the page could not tell them: __________________________
- Would ask about it? yes / no / maybe. What: ___________________
- Read the untraced closing line as a problem with the student? yes / no. Evidence: ____

### 4.4 Hard pair after the histories are revealed

- Did knowing the history change how the page was read? yes / no. How: ______
- Which line, if any, would have misled? ________________________
- Did the teacher end with lingering doubt plus a question, or with certainty? ____
- Was the receipt treated as resolving the question? yes / no. Evidence: ____

---

## 5. Practical-use observations

Record unaided / after a neutral prompt / not observed. Quote the teacher.

| Code | Observation | Result | Teacher's words |
|---|---|---|---|
| P1 | Process, not verdict | met / partly / not observed | |
| P2 | Untraced ≠ outside | met / partly / not observed | |
| P3 | Names a place to ask, unaided | met / partly / not observed | |
| P4 | Connects a question to its span and says why | met / partly / not observed | |
| P5 | Names at least two blind spots | met / partly / not observed | |
| P6 | Says whether it would change what they ask, and how | met / partly / not observed | |

**Pattern note (no score, no judgment of the teacher):** __________________________

---

## 6. Misreadings

Every line below needs the element, the teacher's exact words and the consequence. Do not argue with the teacher.

| # | Element / line | Teacher's words (verbatim, if quote consent) | Criterion | Severity (blocking / material / minor) | Consequence or proposed fix |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |

**Blocking misreadings (any band or seal turned into an authorship conclusion, a score, a judgment about the student, or a replacement for the conversation):** ______________________________

---

## 7. Neutral questions

| Question | Answer (teacher's words) |
|---|---|
| What is unclear? | |
| What could be misread, by you or a colleague? | |
| What evidence would you still want? | |
| Which line would you have misread without the details? | |
| What would you ask the student in five minutes? | |
| Would this have changed the original conversation? What would have been the same? | |
| What does the page not see? | |
| What should we change before another teacher sees it? | |
| What should we keep? | |
| Anything that would embarrass a student? | |

**Original-case answer in one line (including "nothing would have changed"):** ______________________________

---

## 8. Blind rehearsal (descriptive only)

**Status:** initial walkthrough sample. **Not** the 50-vs-50 pilot result. No win rule is applied.

| Pair | Essay ID (fixture/opaque) | First item | Second item | First rating (Yes/Maybe/No/Could not judge) | Second rating | Teacher's guess: platform item | Guess correct? |
|---|---|---|---|---|---|---|---|
| W01 | | | | | | | |
| W02 | | | | | | | |
| W03 | | | | | | | |
| W04 | | | | | | | |

**Descriptive counts:** platform-grounded Yes __ / Maybe __ / No __ / Could not judge __; essay-only Yes __ / Maybe __ / No __ / Could not judge __.

**Procedure problems noticed:** ______________________________

**Blinding observations:** ______________________________

**Teacher's free-text reasons (themes, not scores):** ______________________________

**Do not write:** a winner, a p-value, a "win", or "the blind test shows". Those belong only to the separately preregistered 50-vs-50 pilot.

---

## 9. Verbatim quotes with consent

Only if quote consent is yes. Show the teacher the proposed wording and attribution before publication. Attribute by role only.

| # | Quote (verbatim) | Context | Quote consent | Approved wording | Attribution | Used where |
|---|---|---|---|---|---|---|
| 1 | | | yes / no | | a nursing teacher | |
| 2 | | | yes / no | | a nursing teacher | |

**Quotes refused or withdrawn:** ______________________________

---

## 10. Stopping conditions and deviations

| # | Condition or deviation | What happened | Effect on the session / data | Follow-up |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |

**Condition reveal or leak?** yes / no. If yes: blind portion stopped / ratings labelled unblinded / no win claim. Details: ______

**Key hash checked before opening?** yes / no. **Hash matched?** yes / no.

---

## 11. Unresolved questions and follow-ups

| # | Question | Owner (role) | Needed before | Status |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |

**Proposed product/copy changes (for the checker/founder, not decided here):**

1. ______________________________________________
2. ______________________________________________

**Open loops touched (IDs only):** ______________________________

---

## 12. Sign-off

| Role | Code | Confirms | Date |
|---|---|---|---|
| Facilitator | | Notes and observations are accurate; no condition label was revealed | |
| Key holder | | Key hash recorded before the session; key opened after ratings were frozen | |
| Analyst / second checker | | Join and counts reproduced from raw sheets and key | |
| Founder / coordinator | | Consent, retention and approvals checked | |

**This file is a filled result only when every section above is complete and signed. Until then it is an unfilled template.**
