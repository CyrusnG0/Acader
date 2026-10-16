# Evidence base: oral/viva assessment at scale and LLM-generated questions for verifying understanding of a student's own work (as of 2026-10-14)

Scope note: about 20 search and fetch calls. Where I read only an abstract or a search snippet, the item says so. **[PREPRINT]** marks work not confirmed as peer-reviewed. Several numbers come from search-engine summaries of pages and should be spot-checked before they go into external copy. They are marked "(snippet-level)".

## Q1. Time, cost, reliability and validity of vivas and interactive orals; examples at scale

### Takeaway
A 10–15 minute interactive oral (IO) costs about 15–20 assessor-minutes per student. That is roughly the cost of marking a mid-length essay, and IOs have reportedly been run with up to about 800 students. CS "code interviews" have been squeezed to about 5 minutes per student in courses with 200+ students, but only by triple-staffing TA sections. Reliability evidence is thin and mostly qualitative. Its main lever is standardised, structured questions, which is exactly what anchored, pre-generated questions supply.

### Cited Findings
**Time and cost**
- Griffith-linked guidance from Logan-Fleming and Sotiriadou: a 10–15 minute IO assesses roughly what a 3,000-word essay does. Budget about 20 minutes per student at first, falling to about 15 with experience (practitioner blog, snippet-level). — [Univ. of Sydney, "Five myths about interactive oral assessments"](https://educational-innovation.sydney.edu.au/teaching@sydney/five-myths-about-interactive-oral-assessments-and-how-to-get-started/)
- A common template is 15 minutes per student: a 10-minute conversation plus 5 minutes for rubric grading and feedback. — [Univ. of Melbourne CSHE, Implementing IOAs](https://melbourne-cshe.unimelb.edu.au/resources/implementing-interactive-oral-assessments)
- Melbourne's worked example: 100 students × 15 min = 25 hours of assessor time, or about 50 hours with setup and coordination. That is "roughly comparable to marking 1,000-word written tasks", but the load is concentrated on the coordinator (worked calculation, not a study; snippet-level). — [Univ. of Melbourne CSHE](https://melbourne-cshe.unimelb.edu.au/resources/implementing-interactive-oral-assessments)
- IOs have reportedly been run with up to about 800 students (practitioner claim, snippet-level; primary source not located). — [Univ. of Sydney blog](https://educational-innovation.sydney.edu.au/teaching@sydney/five-myths-about-interactive-oral-assessments-and-how-to-get-started/)
- Kannam, Yang, Dharm and Lin (Univ. of Washington), "Code Interviews", **SIGCSE TS 2025** experience report:
  - Setting: an intermediate Python data science course of typically 200+ students.
  - Format: 5-minute in-person interviews on each of five weekly take-home assignments, held during 50-minute sections staffed at 3 TAs per 30 students so that three interviews could run in parallel.
  - Spring question types: trace a test case, compare approaches, find a bug, write code for an isomorphic problem.
  - Time pressure cut the number of questions from 3 to 2 to 1 over the quarter.
  - The authors say triple-staffing "is not sustainable long term". They also say it is still likely less work than grading a paper exam. — [arXiv 2410.01010](https://arxiv.org/html/2410.01010)
- Reckinger and Reckinger (2021, **ASEE**), "Oral proficiency exams in high-enrollment CS courses": three one-on-one oral exams per semester in intro CS courses of 75–275 students at a minority-serving public university. — [ASEE PEER](https://peer.asee.org/oral-proficiency-exams-in-high-enrollment-computer-science-courses)
- Rizakos and Ipeirotis (NYU Stern), "Scalable and Personalized Oral Assessments Using Voice AI" **[PREPRINT]**, arXiv 2603.18221 v2 (May 2026):
  - Setting: an AI voice agent examined 73 students over two semesters (36 + 37). Mean exam length was 22 min (range 9–41) in Fall 2025 and 30 min (range 19–43) in Spring 2026.
  - Cost: about $3.40–$4.10 per student all-in, versus about $21 per exam for a two-human-grader comparator (2 × $25/h, 25 min).
  - Human interviewing alone would have taken about 13–19 examiner-hours per cohort. — [arXiv 2603.18221](https://arxiv.org/html/2603.18221v2)

**Reliability and validity**
- Huxham, Campbell and Westwood (2012), *Assessment & Evaluation in Higher Education*:
  - Design: a randomised study of 99 biology students answering the same questions orally or in writing, plus a 29-student cohort who sat both formats.
  - Results: marks were significantly higher in the oral. There was no evidence that particular groups were disadvantaged. Students were more nervous, but many judged orals more useful.
  - Not found: inter-rater statistics. — [Edinburgh Napier repository](https://napier-repository.worktribe.com/output/436445/oral-versus-written-assessments-a-test-of-student-performance-and-attitudes)
- University of Antwerp teaching guidance says oral tests involve more variable factors and fewer questions, so they "are characterised by lower levels of reliability and validity". It recommends structure and standardisation as mitigation. — [UAntwerpen, Oral tests objectivity](https://uantwerpen.be/en/centres/centre-expertise-higher-education/didactic-information/teaching-tips/assessing-students/oral-tests-objectivity)
- The UW code-interview paper summarises the prior literature this way: structured oral exams are claimed to be reliable and valid *because* questions and prompts are standardised across students, but "issues of oral exam reliability, validity, and scalability have not been fully addressed" and results are "mixed". The paper itself reports no inter-rater reliability. — [arXiv 2410.01010](https://arxiv.org/html/2410.01010)
- Grade distributions in UW's code interviews: Winter 76% Exemplary / 24% Satisfactory (no fixed questions, group format). Spring 30% Exemplary / 63% Satisfactory / 7% Approaching (specific question types, with both correctness and explanation graded). In other words, structured questions produced far more discrimination. — [arXiv 2410.01010](https://arxiv.org/html/2410.01010)
- NYU voice-AI orals, grading reliability across three LLM graders **[PREPRINT]**:
  - Before deliberation the graders disagreed widely: Gemini 16.3/20, GPT-5 13.7, Claude 13.0.
  - After a deliberation round, Krippendorff's α rose from 0.52 to 0.86 (Fall) and from 0.65 to 0.90 (Spring). Overall-score α was 0.83 and 0.95.
  - Human comparison was informal. The instructor's holistic grades were closest to the most lenient model, but the instructor conceded most of the stricter scores after reading the transcript evidence. — [arXiv 2603.18221](https://arxiv.org/html/2603.18221v2)
- Fowles, Falor, Bhattarai, Edwards and Poulsen, "Allowing Generative AI in CS1 with Code Review Interviews and a Flipped Classroom" **[PREPRINT]** (arXiv 2605.21374, v2 Oct 2026). Abstract only:
  - Over three semesters, there was no statistically significant change in average exam scores after GenAI was allowed alongside code-review interviews.
  - Keystroke logs showed a significant rise in the ratio of pasted to typed characters.
  - Student sentiment toward the code reviews was positive. Negatives were mostly scheduling and TA training. — [arXiv 2605.21374](https://arxiv.org/abs/2605.21374)

**Policy context**
- TEQSA (Australia), *Assessment Reform for the Age of AI* (2023), principle 2: "Forming trustworthy judgements about student learning requires multiple, inclusive and contextualised approaches." Its 2025 follow-up, *Enacting Assessment Reform in a Time of AI*, moves from principles to pathways. — [TEQSA 2025 PDF](https://www.teqsa.gov.au/sites/default/files/2025-09/enacting-assessment-reform-in-a-time-of-artificial-intelligence.pdf)
- The University of Sydney's "two-lane" model lists in-person interactive orals and viva voces as Lane 1 (secure) assessment examples. — [Sydney two-lane FAQ](https://educational-innovation.sydney.edu.au/teaching@sydney/?p=21264)
- Sotiriadou, Logan, Daly and Guest, *Studies in Higher Education* (online 2019, cited as 2020):
  - Setting: IOs as the capstone of sequenced assessments, run as a face-to-face mock job interview (Sports Management, n = 90) and a mediated client briefing (international management, n = 22).
  - Results: IOs rated highest on all employability items.
  - The authors argue that authentic tasks requiring unique responses reduce contract cheating (an argument, not a measured effect). — [Griffith resource](https://app.secure.griffith.edu.au/exlnt/entry/9569/view)

### Inferences
- A 2–5 minute TA oral sits in the same envelope as UW's 5-minute code interviews. For 300 students, that is about 10–25 TA-hours of pure talk time per assignment before scheduling overhead. The bottleneck is scheduling and staffing, not the talking. Pre-generated anchored questions mainly cut TA prep time and raise standardisation, the one reliability lever the literature agrees on.
- UW's Winter-to-Spring shift suggests unstructured orals inflate grades. Structured, submission-anchored questions plus a rubric should improve discrimination. A product that gives TAs specific, line-anchored prompts is directly addressing the documented weakness. **[ASSUMPTION]**
- The NYU result is two-edged. It shows LLM grading needs a deliberation or human audit step, which supports the product rule that a human decides.

### Gaps
- I found no inter-rater reliability coefficients for human-run IOs or CS code vivas. Huxham et al. 2012 report means, not agreement.
- I found no peer-reviewed source for the "800 students" IO claim.
- Dutch and European oral-exam traditions: I found no recent (2022–2026) empirical reliability or cost studies in this pass. This remains a gap, not evidence of absence.
- Ohmann and Novak's reported 2025 follow-up on oral exams in intro CS at two institutions could not be located. Only the SIGCSE 2023 and 2025 Birds-of-a-Feather sessions surfaced. — [SIGCSE 2025 BoF](https://sigcse2025.sigcse.org/details/sigcse-ts-2025-birds-of-a-feather/20/Oral-Exams-in-Computer-Science-Education-Amidst-ChatGPT-Dependency)

## Q2. LLM-generated viva and comprehension questions about a student's code or essays; quality; can LLMs answer them; AI vs instructor questions

### Takeaway
Several systems now generate viva questions from a submission: TAMIGO (2024), the Church et al. viva simulator (2025) and NYU's voice-AI oral (2026). Question generation is reported as good when the LLM has enough context. Grading answers is the weak point: hallucinated feedback and lenient or variable LLM graders. No study cleanly compares AI-generated with instructor-written *viva* questions on a submission. LLMs answer most "questions about learners' code" correctly (GPT-4 at 88%), so an *async written* answer channel is not secure. The live oral is the gate.

### Cited Findings
- **TAMIGO** (Anishka, Sethi, Gupta, Sharma, Jain, Singhal, Kumar; 2024) **[PREPRINT/venue unconfirmed]**:
  - Setup: GPT-3.5-Turbo helped TAs generate viva questions and evaluate answers for take-home programming assignments in an advanced computing course.
  - Questions: the authors report LLMs were "highly effective at generating viva questions when given enough context".
  - Feedback on viva answers was "mixed", with occasional hallucinations reducing accuracy (snippet-level; full PDF unreadable in this session). — [arXiv 2407.16805](https://arxiv.org/pdf/2407.16805)
- **Church, Drake and Harris (Oct 2025), "Using LLMs to support assessment of student work in higher education: a viva voce simulator"** **[PREPRINT]**:
  - Design: a proof of concept that takes a written submission, generates questions a human examiner might ask, and judges likely authorship from the answers. The transcript goes to a human examiner for the final judgement.
  - Not reported in the abstract: quantitative accuracy. — [arXiv 2511.05530](https://arxiv.org/abs/2511.05530)
- **NYU "Viva" voice-AI oral (Rizakos and Ipeirotis, 2026)** **[PREPRINT]**. Questions are generated dynamically during the exam. Failure modes:
  - Question stacking: 31.2% of agent turns in Fall, down to 10.9% after a programmatic validator was added.
  - Paraphrasing a question when the student asked for a repeat.
  - Non-random case selection: one case was chosen in 86% of exams during one week despite a "randomly select" instruction. Moving selection into code fixed it, bringing the maximum share to 22%.
  - A 5-second silence timeout cut students off mid-thought. The authors recommend 30 seconds.
  - A cloned professor voice was perceived as harsh. — [arXiv 2603.18221](https://arxiv.org/html/2603.18221v2)
- **Lehtinen, Santos and Sorva (2021), "Let's Ask Students About Their Programs, Automatically"**, ICPC 2021. This discussion paper proposes that after a program passes unit tests, students get auto-generated questions about *their own* code, built by program analysis rather than an LLM. — [Aalto research portal](https://research.aalto.fi/en/publications/lets-ask-students-about-their-programs-automatically/)
- **Lehtinen, Koutcheme and Hellas (2024), "Let's Ask AI About Their Programs"**, ICSE-SEET 2024:
  - Overall accuracy on 399 Questions about Learners' Code (QLCs): GPT-3.5 69%, GPT-4 88%.
  - By question type: GPT-4 ranged from 100% (parameter names, line purpose) down to 70% (variable trace). GPT-3.5 fell to 40% on loop-end questions.
  - Errors: miscounted line numbers, hallucinated justifications, illogical execution steps.
  - Accuracy fell as task complexity rose. — [arXiv 2404.11734](https://arxiv.org/html/2404.11734v1)
- **AI vs human-written questions (adjacent evidence, MCQs rather than vivas)**:
  - Doughty et al., ACE 2024, compared 651 GPT-4 MCQs with 449 human-crafted MCQs across six Python courses. GPT-4 items had clear wording, a single correct answer and strong distractors, and aligned well with learning objectives. — [arXiv 2312.03173](https://arxiv.org/pdf/2312.03173)
  - Witsken, Crk and Gultepe, AAAI 2025: students could not distinguish LLM-aided questions from instructor-written ones (p = .309), but scored almost 9% lower on the LLM-authored items. — [AAAI 2025](https://ojs.aaai.org/index.php/AAAI/article/view/34984)
- **Student-centred evaluation of an LLM-generated test** **[PREPRINT]**: a GPT-4o-mini-generated test for an NLP course showed good psychometric properties in student and expert evaluation. — [arXiv 2505.06591](https://arxiv.org/abs/2505.06591v1)
- **Automated grading of code-comprehension answers**: Oli et al. (2024), "Automated Assessment of Students' Code Comprehension using LLMs" (PMLR v257). Details not read. — [PMLR](https://proceedings.mlr.press/v257/oli24a.html)

### Inferences
- An LLM answers the questions correctly 69–88% of the time, and the misses fall on tracing and line-number types. Written or async "explain your code" questions therefore offer little authorship assurance. The live, timed, follow-up-capable oral is what carries the evidential weight. This supports keeping a human TA in the loop and limiting AI to *generating* anchored questions.
- Anchoring to specific lines and claims probably reduces the generic-question problem. The documented failure modes (stacking, paraphrase drift, poor randomisation) argue for deterministic code-side control of question selection, with the LLM used only for wording. **[ASSUMPTION]**

### Gaps
- No study found that runs a head-to-head of LLM-generated vs instructor-written *viva or oral* questions anchored to the student's own submission, measuring discrimination (understanders vs non-understanders).
- No study found on question *anchoring* (line-level or claim-level) vs generic questions as an experimental variable.
- No published results found yet from AIED, LAK or L@S 2025–2026 specifically on viva question generation. My search coverage of those venues was shallow.

## Q3. "Explain your own code" questions as a signal of missing understanding or authorship

### Takeaway
Questions about a student's *own* passing code expose fragile understanding in a sizeable minority: about 20–27% of students with correct programs fail at least one simple question. These questions measure comprehension. They were not validated as authorship detectors, and framing them that way would breach the product's wording rules anyway.

### Cited Findings
- Lehtinen, Seppälä and Korhonen (ITiCSE 2023), "Automated Questions about Learners' Own Code Help to Detect Fragile Prerequisite Knowledge": QLCs were generated from each passing submission and kept intentionally simple, yet 27% of students failed at least one. — [Aaltodoc](https://aaltodoc.aalto.fi/items/403399e9-4ec3-4e50-8f47-8f1520a6677f)
- Lehtinen's 2024 doctoral dissertation, *Questions About Learners' Code*, reports that up to 20% of students who create a correct program may answer incorrectly about concepts critical to reasoning about how it works (snippet-level, from the defence announcement). — [Aalto public defence](https://www.aalto.fi/en/events/public-defence-in-computer-science-msc-tech-teemu-lehtinen); [QLC project page](https://users.aalto.fi/~lehtint6/qlcs.html)
- Prior studies, as summarised in Lehtinen et al. 2024: student success above 70% on syntax-focused QLCs, but only 30–50% on tracing questions. — [arXiv 2404.11734](https://arxiv.org/html/2404.11734v1)
- In UW's code interviews, students said explaining their code deepened understanding. Failure modes included converging solutions (repetitive interviews), isomorphic-problem questions taking too long, and difficulty for English-language learners (about 40% of the cohort). — [arXiv 2410.01010](https://arxiv.org/html/2410.01010)
- Reckinger and Reckinger: students across nearly all demographic groups reported that oral exams improved their understanding and pushed them toward more independent work. — [ASEE PEER](https://peer.asee.org/oral-proficiency-exams-in-high-enrollment-computer-science-courses)

### Inferences
- The 20–27% "correct program, fragile understanding" rate is a strong, citable product hook. It is a *comprehension* signal, consistent with the product's tiers (Strong / Partial / Oral-verified), and not a cheat signal.
- Tracing and "what happens at this line" questions discriminate best, both for students and against LLM answering (GPT-4 was weakest on variable tracing). That makes them good default anchored question types. **[ASSUMPTION]**

### Gaps
- No study found that validates "explain your code" questions against ground-truth authorship (for example, known AI-written vs self-written code) with sensitivity and specificity.

## Q4. Writing-process data (keystrokes, revision history) as authorship evidence

### Takeaway
In controlled settings with paste disabled, keystroke features separate authentic composition from transcription very well (about 99% in one EDM 2024 study). Evidence is lab-like, mostly English-only and from small samples, and paraphrase or retyping attacks are only starting to be studied. Process data is best treated as supporting context, not proof. This matches the product rule that "typing is not proof".

### Cited Findings
- Crossley, Tian et al. (EDM 2024 short paper), Vanderbilt:
  - Result: a random forest on keystroke logs separated authentic from transcribed essays with about 99% accuracy.
  - Setting: paste was disabled, so transcribed text had to be retyped from an external source such as AI output.
  - Signals: authentic writing showed more pauses, insertions, deletions and revisions. Transcription was more linear and bursty. — [EDM 2024](https://educationaldatamining.org/EDM2024/proceedings/2024.EDM-short-papers.47/index.html)
- Follow-up **[PREPRINT]**: the authors report that keystroke-aware models detect both verbatim and paraphrased transcription. — [arXiv 2511.12468](https://arxiv.org/pdf/2511.12468v1)
- **[PREPRINT]** (ETS-related): text-only AI detectors lose power once AI essays are substantially edited, and process data can help. — [arXiv 2411.13699](https://arxiv.org/pdf/2411.13699)
- Kundu et al. **[PREPRINT]**, "Keystroke Dynamics Against Academic Dishonesty in the Age of LLMs" (2024). — [arXiv 2406.15335](https://arxiv.org/html/2406.15335v1)
- Korean-language keystroke study **[PREPRINT]**:
  - Limitation it notes: most keystroke detection models are trained exclusively on English data.
  - Student reactions: most students viewed logging positively, but some reported increased anxiety and privacy concerns. — [arXiv 2507.22956](https://arxiv.org/html/2507.22956v1)
- Condrey (WritersLogic) **[PREPRINT]** reports an 85–95% discrimination figure. It is an analytical estimate under stated assumptions, not an empirical validation. — [arXiv 2603.00177](https://arxiv.org/pdf/2603.00177)
- Fowles et al. used CS1 keystroke logs (ratio of pasted to typed characters) as a population-level indicator of AI use rather than an individual verdict **[PREPRINT]**. — [arXiv 2605.21374](https://arxiv.org/abs/2605.21374)
- Context on text-only detectors: Liang et al. (2023, *Patterns*) found GPT detectors classified more than 61% of TOEFL essays by non-native writers as AI-generated (cited here via a secondary review; primary not fetched). — [secondary review, UNISI journal](https://ejournal-fkip.unisi.ac.id/shelves/article/download/3557/1886/12086)

### Inferences
- Typing traces are trivially defeated by retyping AI output in environments that allow it, and they are biased by language, disability and writing style. They work best as *entry evidence*, with the oral as the gate. That is exactly the product's rule 5. **[ASSUMPTION]**

### Gaps
- No peer-reviewed field study found on revision history (Google Docs history, Grammarly Authorship, Turnitin Clarity) as authorship evidence with error rates.
- No study found on keystroke-feature fairness for students with motor disabilities or students using assistive tech or dictation.

## Q5. Anxiety, accessibility and accommodations for orals

### Takeaway
Orals reliably raise anticipatory stress, especially the first one and especially for some under-represented groups, women and English-language learners. Stress drops with repetition and with low-stakes or formative framing. I found no systematic review of accommodations specific to oral assessment. Accommodation evidence is practitioner guidance.

### Cited Findings
- Reckinger and Reckinger (2021):
  - Students found the first oral exam very stressful, but the stress did not carry over to later ones.
  - Some under-represented groups (reported as women and some first-generation or minority students) reported higher stress than majority peers. — [ASEE PEER](https://peer.asee.org/oral-proficiency-exams-in-high-enrollment-computer-science-courses)
- NYU voice-AI orals **[PREPRINT]**:
  - Found the oral more stressful than written exams: 83% (Fall), falling to 63% (Spring) after design fixes.
  - Agreed the exam tested real understanding: about 70% and 66%.
  - Found it fair: rose from 33% to 56%.
  - Preferred an AI oral: only 13% and 25% (written: 57% and 53%). — [arXiv 2603.18221](https://arxiv.org/html/2603.18221v2)
- UW code interviews:
  - Group interviews lowered stress for some students, while others preferred individual interviews.
  - Unknown questions were stressful, and students who had not finished the assignment felt extra pressure.
  - English-language learners had language difficulties (about 40% of the cohort; about 10% reported disabilities). — [arXiv 2410.01010](https://arxiv.org/html/2410.01010)
- Huxham et al. (2012): students were more nervous about orals, with no evidence of particular groups being disadvantaged in marks. — [Napier](https://napier-repository.worktribe.com/output/436445/oral-versus-written-assessments-a-test-of-student-performance-and-attitudes)
- UCL (May 2026) guidance, "Making oral assessments inclusive": orals can heighten stress, bias and barriers if poorly designed. It provides inclusive-design practice. — [UCL](https://www.ucl.ac.uk/teaching-learning/publications/2026/may/making-oral-assessments-inclusive)
- A 2025 Thai EFL study (survey): high-stakes graded speaking tasks were the main anxiety trigger, and low-stakes formative orals helped. A 2026 systematic review in EFL found a consistent inverse association between communicative anxiety and oral performance. — [AJATeL](https://ejournal.upsi.edu.my/index.php/AJATeL/article/view/11908)
- The 2026 CS1 code-review study notes orals can add stress for students anxious about interpersonal confrontation **[PREPRINT]**. — [arXiv 2605.21374](https://arxiv.org/pdf/2605.21374)

### Inferences
- Design levers with support in this evidence:
  - Frequent, short, low-stakes orals rather than one high-stakes viva (stress decays after the first).
  - Questions anchored to the student's own work, which reduces fear of "unknown questions".
  - Generous silence and think time (NYU's 5-second-to-30-second lesson).
  - Typed or async alternatives for accommodations.
  - Calm, non-confrontational framing.
- Mandatory accessibility alternatives (product rule 5) have regulatory backing in inclusive-assessment guidance but little empirical testing. **[ASSUMPTION]**

### Gaps
- No systematic review found on accommodations (extra time, written alternative, interpreter, recorded or async) for vivas, or on whether alternatives preserve validity.
- No data found on orals for students who stutter, are autistic or are deaf, in CS contexts.

## Q6. What has NOT been studied or built

### Takeaway
The intersection the product targets is effectively unstudied: LLM-generated questions anchored to specific lines, claims and citations in a student's submission, *run by a human TA in 2–5 minutes*, with measured discrimination and reliability. Neighbouring pieces exist: program-analysis QLCs, LLM viva generators, AI-run orals and keystroke process data.

### Cited Findings
- Existing pieces and their limits:
  - Program-analysis QLCs: no LLM, fixed templates. — [Aalto](https://research.aalto.fi/en/publications/lets-ask-students-about-their-programs-automatically/)
  - TAMIGO: GPT-3.5, single course, mixed feedback quality. — [arXiv 2407.16805](https://arxiv.org/pdf/2407.16805)
  - Viva simulator: proof of concept, no reported accuracy. — [arXiv 2511.05530](https://arxiv.org/abs/2511.05530)
  - NYU AI oral: AI-run rather than TA-run, 73 students, 20–30 minute exams, one course. — [arXiv 2603.18221](https://arxiv.org/html/2603.18221v2)
  - UW code interviews: TA-run, but with no generated or anchored questions and no reliability statistics. — [arXiv 2410.01010](https://arxiv.org/html/2410.01010)

### Inferences (each a gap)
- No found study tests whether *course-material grounding* (a course knowledge graph) improves question quality or discrimination over generic LLM questions. This is the product's core differentiation hypothesis and a genuine research gap.
- No found validation of very short (2–5 minute) orals: how many anchored questions are needed for a stable comprehension judgement.
- No found inter-rater reliability study of TAs using AI-generated rubrics and question sets.
- No found study of claim-level and citation-level viva questions for *essays* (as opposed to code), such as "why did you cite X for this claim?".
- No found longitudinal evidence on whether expected orals change how students use AI while doing the work (the deterrence or learning effect). Fowles et al. hint that scores held steady while paste ratios rose. — [arXiv 2605.21374](https://arxiv.org/abs/2605.21374)
- No found study on students using real-time AI assistance *during* remote orals (earpieces, second screen) and how anchored follow-ups resist it.

### Gaps
- Coverage of AIED, LAK and L@S 2025–2026 proceedings and of European (Dutch, Nordic, German) oral-exam research was shallow in this pass. A targeted ACM DL or Scopus search is recommended before any claim of "no prior work" goes into external materials.
