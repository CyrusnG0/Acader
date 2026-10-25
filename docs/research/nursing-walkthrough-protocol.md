# Nursing walkthrough protocol (T-009)

**Status:** protocol for review, written 2026-10-25. **No session has been run.** Nothing in this file is a result, and no teacher has been contacted. Execution waits for actual rendered receipts, question output produced by an approved live release run, a recruited participant and the approvals in §3. The companion [blind-question preregistration](blind-question-preregistration.md) and [results template](nursing-walkthrough-results.template.md) are part of this protocol.

**Evidence status:** the cases here are **synthetic reconstructions**. They are not real student logs, not real student data and not evidence about any student. The kit and golden sessions are simulated (evaluation.md §7).

**What this session is for.** The university team supplied a real use case and pain point (the 2026-10-21 nursing case). This protocol prepares a walkthrough in which that teacher reads reconstructed receipts and we learn where the page is usable and where it is misread (OL-034; evaluation.md §6; receipt.md §8). It does **not** test whether the receipt would have settled the real dispute, and it does not decide that question.

**What this session is not.**

- It is not the 50-vs-50 validity test. The pilot target is specified separately in the [preregistration](blind-question-preregistration.md); the walkthrough's blind portion is a small rehearsal and is reported as descriptive only.
- It is not a measure of student understanding, learning or authorship. No student takes part and no student text is graded.
- It is not a verdict about the teacher. Nothing here rates the teacher's skill or changes their standing.
- It is not evidence until it has actually been run with consent. The results template stays empty until then.

---

## 1. Objective and the questions the session answers

**Objective.** Find out whether a teacher can use the receipt's first screen for its stated job, and where its wording or layout invites a misreading, before the 50-vs-50 pilot test and before any real student use.

The receipt's job is stated in receipt.md §1: in under three minutes, a teacher should be able to see what happened inside the platform, what the student said came from outside, what has no trace, and the two or three questions worth asking. It is a process profile, never a verdict.

**Session questions, in order of importance.**

1. **Practical use.** Without being led, can the teacher locate the summary, the two bars, the "Where to ask" questions and the "untraced is not AI" line; say what each is for; and name at least one place they would ask about?
2. **Misreading.** Which line or element is read as something it does not say, especially as a judgment about the student, a score or an authorship conclusion?
3. **Remaining uncertainty.** What is still unclear after reading the first screen and the details? What evidence would the teacher still want, and what would they ask the student in a five-minute conversation?
4. **Conversation value, without assuming it.** If this page had been available in the original case, what, if anything, would have been different? "Nothing" and "I would still have asked for the same log" are valid and important answers.
5. **Blind rehearsal (descriptive).** For a separate small set of essays, are platform-grounded questions rated more useful than essay-only questions? This rehearses the pilot procedure; it is not the pilot result.

**Pre-specified practical-use observations** (recorded yes / partly / no / not observed, each with the teacher's own words):

- P1: states the receipt is about the process, not a judgment about the student.
- P2: distinguishes "untraced" from "written outside the platform" and reads the "untraced is not AI" line.
- P3: identifies at least one span the teacher would ask about, unaided.
- P4: connects a "Where to ask" question to its span and can say why it might be worth asking.
- P5: says what the record cannot see (retyped text, work done offline, undeclared outside help, the student's understanding).
- P6: says whether the page would change what they ask, and how, or that it would not.

These are observations, not a test the teacher passes. A session where the teacher says "this would not have helped" is a successful session if we learn why.

**Misreading criteria.** A statement counts as a misreading when it contradicts the labelled meaning of an element. The full list and severity rule are in §7.

**What the session can change.** Wording, order, labels and the script may be revised afterward. Any change to receipt.md, DESIGN.md or product copy is a checker/founder decision, not a worker decision; this protocol records proposals in the handoff. OL-047 (existing T-015/T-016 proposals, including "Written on N days") is still open: use the receipt exactly as rendered and do **not** silently change copy or assume a proposal is accepted.

---

## 2. Participants and roles

The minimum viable session is four roles. One person may not hold two roles that would reveal a condition label or lead the teacher.

| Role | Code | Does | Must not |
|---|---|---|---|
| **Teacher participant** | T1 | Reads the cases, uses the receipt, answers the neutral questions, rates the blind questions | Be told which questions are platform-grounded; be asked to defend the original decision |
| **Facilitator** | F1 | Runs the script in §6, keeps time lightly, records observations | Know the condition key; defend the product; suggest what the teacher "should" see |
| **Key holder** | K1 | Prepares the opaque rating packets, allocates conditions and order, keeps the sealed key, records its hash | Be present during ratings; rate; tell the facilitator or teacher anything about the arms |
| **Observer / note-taker** (recommended) | O1 | Records verbatim notes against the template; marks misreads | Prompt, interpret aloud or know the condition key |
| **Analyst** (may be K1 after the session) | A1 | Opens the key only after ratings and the analysis script are frozen; joins and analyses | Open the key early; change the win rule after seeing ratings |
| **Founder / coordinator** | — | Recruitment, consent, approvals, retention, decides follow-ups with the checker | Delegate recruitment or consent to a worker |

- The **facilitator must not be the author of this protocol** if another trained person is available; the acceptance condition is that another person can run it without the author present.
- The **teacher's name and institution do not go into Git**. Use role codes in every note and in the results file. Quote only with the separate quote consent in §3.
- If the session is run with more than one teacher, run separate sessions with separate keys; do not pool them into one win claim without a new preregistration.
- No worker books, contacts, messages or travels to a participant. The founder owns recruitment and approvals (T-009 ticket).

---

## 3. Consent, approvals and data minimisation

**Approval gates (all before any session).**

- Named teacher and agreement to take part (founder; OL-036).
- School/provider and processor approvals where required (OL-037); research-ethics approval if notes, quotes or findings will be reported beyond internal product work (OL-026).
- A consent form the teacher keeps, with a contact for withdrawal and questions.
- Confirmation that the case material used is the reconstruction in §4, not a real log or real student identity.

**Consent elements, in plain language.**

- Purpose: learn whether the receipt page is usable and where it is misread; this is product research, not an evaluation of the teacher or the student.
- Voluntary: the teacher may stop at any time, skip any question, and ask for notes or quotes to be removed.
- What is recorded: the observer's notes, the teacher's ratings and free-text comments, and (only with separate consent) audio. No video and no screen capture.
- Retention: audio is deleted after transcription; the anonymised notes and ratings are kept only as long as needed for the product decision and are named by role code. The founder names the retention date on the consent form.
- Access: the product team and the checker; no student, no school manager and no one outside the approved team.
- Quotes: used only with the separate quote-consent box; the teacher sees the proposed wording and attribution before publication; attribution is role-only ("a nursing teacher").
- No consequence: taking part, declining or stopping has no effect on teaching, employment or the student's standing.
- Withdrawal: the teacher can withdraw up to the point the findings are published; the founder records the date.

**Data minimisation.**

- Use synthetic fixtures only (§4). Do not ask the teacher to bring the real 40-page log, real student scripts, names, student numbers or screenshots.
- Do not record the teacher's face, voice (unless separately consented), keystrokes, reading dwell or timing of individual actions. Approximate time to the first question may be noted as one descriptive observation about the page, not as a measure of the teacher.
- If a real student identifier appears in conversation or in a document, stop that part, do not transcribe it, and delete the note. The session can continue with the synthetic cases if the teacher agrees.
- The filled results file is stored with role codes only. Do not commit it if it contains anything identifying. The unfilled template is in Git; the filled copy is not.
- Verbatim quotes are stored only after quote consent and approval. Paraphrase when consent for a quote is refused.

---

## 4. Reconstructed synthetic case material

All cases are fictional reconstructions assembled from the golden fixtures and receipt.md §8. They use invented text and no real student data. The rendered receipts must be the **actual compiler output** for these fixtures; do not hand-edit numbers, wording or spans to make the story fit.

### Case A: the honest nursing reconstruction (main case)

- **Story shown to the teacher:** a care-plan rationale of about 1,200 words with three readings and four sessions. The student reads the results and the limitation, anchors two cards, revises a claim after the limitation pin, sets one source aside with a reason, quotes the paper twice, answers a Coach question and moves the answer into the draft, and ends with one unlinked typed sentence.
- **Fixture that grounds it:** `prototype/fixtures/golden/honest-nursing.yaml`. The bands, layout and chain are the actual compiler output for that session; a stub render is acceptable for those. The "Where to ask" question text shown to the teacher must come from an approved live release run for the same session (backend, run ID and stored artifact IDs recorded), or be clearly labelled as stub output and not discussed as live question quality. Do not hand-edit numbers, wording or spans. Its expected shape is: 61 words, bands by words `traced_source 34 / traced_coach 11 / student_linked 8 / untraced 8`, two traced claims and one untraced closing unit, with a question target at p4. The short fixture is the truthful analogue of the longer §8 story; the 1,200-word story must be labelled as the intended scenario, not as the size of the rendered file.
- **What it is for:** can the teacher find the two places worth asking about, see the declared Coach answer, and read the untraced closing sentence without turning it into a judgment?

### Case B: the hard / ambiguous pair (required)

The hard case is deliberately not one receipt. It is a pair that both show an untraced band for different histories, so the teacher can see that the page shows where to ask and not what happened.

- **B1: the outside expansion inside the student's card.** Fixture `prototype/fixtures/golden/ai-expanded-card.yaml`. The student types a short card note, pastes an outside expansion into the card, moves it into the draft, adds a typed sentence and writes a second typed paragraph on the same claim. Expected shape: 32 words, `student_linked 15 / untraced 17`, the first sentence untraced and the claim unit untraced. The pasted part remains paste-marked; the moved text is not an editor paste event. L3b is off, so added propositions inside otherwise traced sentences are not checked. The receipt can point to p1; it cannot say whether the student understood the expansion.
- **B2: the quiet honest writer.** Fixture `prototype/fixtures/golden/thin-honest.yaml`. Everything is typed; one card, one claim, a short linked paragraph and a one-line unlinked closing paragraph. Expected shape: 21 words, `student_linked 17 / untraced 4`, with questions at p2 and p1. This is an honest gap: the closing line has no link, not an outside source.
- **Why the pair:** B1 and B2 produce a visible untraced band for different reasons. The teacher should be able to say "I would ask here" in both, and should not be able to say from the page alone which history is which. If the teacher reads B1's untraced sentence as proof of outside help, or B2's untraced line as a problem with the student, the page has been misread. The correct outcome of the hard case is **lingering doubt plus a question**, not certainty.

### Blind rehearsal material

Four different fixtures, one question per arm per essay, used only for the small blind rehearsal (descriptive; §3.2 of the preregistration): `pasted-rewritten.yaml`, `declared-outside.yaml`, `elaborating-honest.yaml`, `reference-list.yaml`. They are not shown as receipts in the qualitative part, which reduces priming. The essay shown is the plain final document text produced by the replay path, with no origin marks, actions, expected bands, fixture metadata or receipt; the same plain text goes to both question generators. The preregistration fixes the generation, pairing, order and key.

### What the teacher is told about the material

Say plainly: "These are fictional reconstructions built for this session. They are not your student's file and not anyone's real work. We are testing the page, not you and not the student." Do not present the reconstruction as the real case.

---

## 5. Materials checklist

Before the session, the key holder and facilitator confirm every item.

**Rendered artefacts**

- [ ] Case A first screen, details drawer, chain view and "About this receipt", printed and on screen, from the actual compiler output for `honest-nursing.yaml` (bands/layout may be stub; question text must be live, or labelled stub and not judged as live quality).
- [ ] Case B1 and B2 first screens and chain views, from `ai-expanded-card.yaml` and `thin-honest.yaml`.
- [ ] The receipt shows the correct engine stamp and, where relevant, `questions_pending`, `replay_note` or mechanics; do not hide a pending state.
- [ ] A fallback: if rendering fails, stop the session rather than describing a receipt that is not on screen.

**Question output**

- [ ] The blind rehearsal uses questions from an **approved live release run** (backend named, run ID and stored artifact IDs recorded) and not `ROOM_LLM=stub` output. Compiled stub questions are not evidence of live question quality (T-009 ticket; T-016 handoff).
- [ ] If only stub questions exist, run the session as a **protocol dry run**, label it as such, and do not report a blind result.
- [ ] Both arms pass the wording filter; replaced questions are logged.

**Rating packets**

- [ ] Opaque item IDs only (for example `W01-A`, `W01-B`); no arm names, no colour, font or spacing differences, no condition words in file names or document metadata.
- [ ] The four essays as plain final text with no marks or metadata, in a seeded presentation order; within each essay the two questions in a seeded order; balanced first position (§3 of the preregistration).
- [ ] A sealed key, offline and outside the repo, with its SHA-256 hash recorded in the session log before the session.
- [ ] Blank rating sheets per essay: Yes / Maybe / No, free-text box, and a "could not judge" option.
- [ ] The analysis script and the win rule are frozen and hashed before the first rating; no edits after.

**Session pack**

- [ ] This protocol, the preregistration, the unfilled results template, the facilitator script (§6), the neutral question list (§6), the glossary of bands and labels, and the one-page "what the record can't see" text.
- [ ] Consent form and quote-consent box; approved retention date; approval references.
- [ ] Observer note sheet keyed to the template.
- [ ] A clock visible only to the facilitator; no countdown, no pressure language, no timing of the teacher.
- [ ] Water, breaks and a stop signal the teacher can use without explaining.

**Prohibited at the session**

- Real student logs, names, numbers, screenshots or essays; condition labels on any sheet; the key in the room; anyone who will defend the product; live LLM calls; recording of faces or screens.

---

## 6. Facilitator script and neutral questions

The script is read close to verbatim. Bracketed text is an instruction, not something to say. Do not add leading phrases such as "you'll see that…", "the important thing is…", "this is much clearer than a log" or "this proves…". Do not answer a question about authorship from the page; say what the page does and does not record.

### 6.1 Opening (about 5 minutes)

> "Thank you for making time. We are testing a one-page process record, not you and not your student. The cases today are fictional reconstructions, not your real file. There are no right answers. I am interested in what you notice, what is unclear, what you might misread and what you would still want to know. You can stop at any time or skip any question. May I take notes? [Confirm consent and quote consent.]"

> "The record is not a judgment about the student. It shows what happened inside the platform and where the platform has no record. A person decides what to do with it."

**Rules to state:** think aloud if comfortable; ask me to stop at any point; I will not tell you what I think the page means; I may ask the same question in different ways.

### 6.2 Case A, first screen (about 10 minutes, no explanation before reading)

Hand over the first screen only. Let the teacher read in silence. Do not point.

Neutral prompts, in order, only as needed:

1. "What do you see here?"
2. "What is this page telling you?"
3. "What, if anything, is unclear?"
4. "What could be misread here, by you or by a colleague?"
5. "Where, if anywhere, would you want to ask this student something?"
6. "What would you ask, in your own words?"
7. "What evidence would you still want before you were satisfied?"
8. "What does this page not see?"

Then open the details and the chain view for the same case:

9. "Does the detail change anything you thought on the first screen?"
10. "Which line would you have misread if you had not opened the details?"
11. "Is there anything here that reads as a judgment about the student?"

Do not say "the untraced line means it isn't AI" before the teacher has had a chance to read it. If the teacher asks directly what a band means, read the on-page label and the "untraced is not AI" sentence, then ask what they take it to mean.

### 6.3 The original case, without assuming an answer (about 5 minutes)

> "The case that prompted this work involved a long log and several meetings. I am not going to ask you to relive the details, and I am not assuming this page would have solved it. If a page like this had existed at the time, what, if anything, would have been different? What would you still have needed?"

Follow-ups:

- "What would have been the same?"
- "Would it have changed what you asked, or just how quickly you got there?"
- "Is there anything you would still not have been able to find out?"
- "Would you have trusted it? Why or why not?"

Record "nothing would have changed" as a finding, not a failure.

### 6.4 Hard case (about 10 minutes)

Show B1 and B2 first screens without saying which is which beyond the case labels. Do not tell the teacher the history.

1. "What do you think happened here?"
2. "What can this page not tell you?"
3. "Which of these two would you ask about first, and why?"
4. "If you had to explain the difference between these two pages to a colleague, what would you say?"
5. "What would you still want to see before forming a view?"

After the teacher has answered, reveal the fixture histories. Ask: "Did knowing the history change how you read the page? Which line would have misled you?" The point is not to make the teacher feel tricked; it is to test whether the page over-claims.

### 6.5 Blind rehearsal (about 15–20 minutes)

> "Now I will show you four short essays, one at a time. For each, you will see two questions written about the essay. Please rate each question on its own: would you ask it in a five-minute conversation with this student? Yes, maybe or no. There is no correct answer. I cannot tell you where the questions came from, and I would rather you did not try to guess. The rating is about whether the question would be useful to you, not about whether the student wrote the essay."

Hand over the packet for essay 1 only. The teacher reads the essay, then both questions in the printed order, then rates both. Collect the sheet before the next essay. Do not discuss the questions between essays. Do not reveal the key. If the teacher asks which question is "ours", say: "I can't say until all the ratings are in; that is part of the test."

At the end, one optional question: "Without trying to be right, was there anything about the two questions that made you think one came from a different source than the other?" Record the answer as a blinding observation; do not explain the arms.

### 6.6 Close (about 5 minutes)

1. "What should we change before another teacher sees this?"
2. "What should we keep?"
3. "Is there anything you would not want a colleague to see, or any wording that would embarrass a student?"
4. "May I follow up if I need to check a quote?"

Then: thank the teacher, confirm what will be stored, confirm quote consent and the withdrawal route, and give the contact.

### 6.7 Things the facilitator must not do

- Do not say the receipt proves authorship, resolves the case, decides that the text came from outside, or puts the student in the clear.
- Do not use any wording the receipt's filter blocks (law 10; receipt.md §5); the on-page filter already applies, and the facilitator's speech must match it.
- Do not explain a band before the teacher has read it.
- Do not ask "Would this have ended the dispute faster?" as a yes/no question. Ask what would have been different, including "nothing".
- Do not praise or correct the teacher's reading during the session; note it and ask a neutral follow-up.
- Do not reveal the condition key, the arm names or the generation method.

---

## 7. Practical-use and misreading criteria

### 7.1 Practical use

Record each observation with the teacher's own words. A criterion is **met** only if the teacher does it unaided; **partly** if a neutral prompt is needed; **not observed** otherwise.

| Code | Observation | Met when |
|---|---|---|
| P1 | Process, not verdict | Says the page describes how the work was built / where to ask, not whether the student is honest or whether the text is outside work |
| P2 | Untraced ≠ outside | Reads "untraced" as "no record here", not as "written outside the platform" or a conclusion |
| P3 | A place to ask | Names a specific span or question worth following up, without being told one |
| P4 | Question ↔ span | Connects a "Where to ask" question to its span and says why it might be worth asking |
| P5 | Blind spots | Names at least two of: retyped text, work offline, undeclared outside help, the student's understanding |
| P6 | Change in the conversation | Says whether the page would change what they ask and how, or that it would not |

Practical use is not a score and is not a pass/fail for the teacher. Report the pattern and the quotes.

### 7.2 Misreadings

A misreading is a statement that contradicts an on-page label or the "untraced is not AI" line. Record the element, the teacher's exact words and the consequence. Severity:

- **Blocking (fix before the pilot):** any reading that turns a band or the seal into an authorship conclusion, a judgment about the student, or a measure of honesty; any reading of "untraced" as "written outside the platform"; any reading of a bar as a score or grade; any reading that the receipt replaces the conversation. Also any statement that the page decides the student did the work themselves or proves that someone else did.
- **Material (fix or explain before the next session):** reads "linked by the student, not checked" as checked; reads a declined Coach question as a mark against the student; reads the seal as proof that the content is true; reads the summary as a verdict; cannot find the blind-spot line; treats a pending question as a failure of the student.
- **Minor (log and triage):** a label that takes extra time; a layout element mistaken for another; a term that needs a gloss but does not change the meaning.

Do not argue with the teacher about a misreading. Note what the page said and ask what they understood.

---

## 8. Reporting and storage

Use [nursing-walkthrough-results.template.md](nursing-walkthrough-results.template.md). It is unfilled and must stay labelled as unfilled until the session happens.

- Observations, ratings and approved quotes go in the filled copy; role codes only, no names.
- The filled copy is not committed if it contains anything identifying. The checker decides what summary, if any, goes into UPDATE_LOG; the protocol author does not write UPDATE_LOG.
- Report at least: the practical-use observations, every misreading with severity, the neutral-question answers, the hard-case outcome, the blind rehearsal's descriptive counts, the stopping conditions triggered, and every deviation from this protocol.
- Do not report a blind "win" from the walkthrough. The only permitted description is "initial walkthrough sample, n pairs, descriptive only; not the 50-vs-50 pilot result".
- A single session is not a trend. Do not write "teachers find" from one teacher.

---

## 9. Stopping conditions

Stop the session, or the affected part, immediately when any of these occurs. Record which one and what happened.

1. **Consent or approval missing** (including quote consent): do not start or do not record.
2. **Condition label revealed** — by a sheet, file name, facilitator slip or the teacher guessing and being confirmed: stop the blind portion. Ratings are labelled "unblinded" and do not enter any win calculation. The qualitative part may continue only with the teacher's agreement.
3. **The key is opened or seen** by the facilitator, observer or teacher before ratings are frozen: the blind test is void.
4. **Real student data appears** (name, script, log, screenshot): stop, do not transcribe, delete the note.
5. **The teacher asks to stop, shows distress, or withdraws:** stop; no persuasion; follow the withdrawal terms.
6. **Rendering failure, missing receipt artifact, or a hand-edited receipt:** stop the affected case; do not describe a page that is not on screen.
7. **Only stub questions are available:** stop the blind portion; the session may proceed as a dry run, clearly labelled, with no blind result.
8. **Key or analysis script not frozen before the first rating:** stop the blind portion.
9. **Fewer than four complete blind pairs in the rehearsal:** report the qualitative part; do not report a blind result.
10. **More than 10% of rated pairs missing or "could not judge":** report the blind result as inconclusive, not as a win or loss.
11. **Teacher fatigue or the agreed session limit is reached:** stop; unused items are missing, not rushed. Do not extend the session to reach a count.

There is no early-stop rule for a favourable result in the pilot; see the preregistration. The walkthrough has no win rule at all.

---

## 10. After the session

1. The facilitator hands the raw rating sheets to the key holder; the key holder checks that the packet count matches and records the time the ratings were frozen.
2. The analyst opens the key only after the ratings and the analysis script are frozen, records the key hash, joins the ratings and produces the descriptive counts (walkthrough) or the preregistered analysis (pilot).
3. A second person reproduces the join and the counts from the raw sheets and the key.
4. The facilitator fills the results template from the notes, with approved quotes only.
5. The session owner writes a short handoff with observations, proposed copy/layout changes and proposed decisions. Product and design changes go to the checker/founder; the session owner does not edit receipt.md, DESIGN.md or shared tracking.
6. The blinding check and every deviation are reported even if they weaken the result.

---

## 11. References

- `design/evaluation.md` §§4–7 (human sessions, blind test, pilot measures, walkthrough, what counts as evidence).
- `design/receipt.md` §§1–4, 7–8 (job, layout, chain view, question rules, release/student view, nursing example).
- `design/build-plan.md` M1/M2 and §4 (pilot gate).
- `PRODUCT.md` §§2–3, 5–6 (problem, promises, laws).
- `docs/OPEN_LOOPS.md` OL-026 (ethics and validity, 50-vs-50), OL-034 (nursing case), OL-040 (false clears and false gaps), OL-041 (score misreading), OL-047 (pending wording proposals).
- `docs/handoffs/2026-10-24-T-016-receipt-compiler.md` (question candidates, stub-not-evidence caveat, PD-T016-4 and PD-T016-5).
- Fixtures: `prototype/fixtures/golden/honest-nursing.yaml`, `thin-honest.yaml`, `ai-expanded-card.yaml`, `pasted-rewritten.yaml`, `declared-outside.yaml`, `elaborating-honest.yaml`, `reference-list.yaml`.
- [Blind-question preregistration](blind-question-preregistration.md); [results template](nursing-walkthrough-results.template.md).
