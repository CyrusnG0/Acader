# AI-powered oral assessment / viva / "interrogate the submission" tools (as of 2026-10-14)

Scope note: research done 2026-10-14 with about 21 search and fetch calls. Several vendor sites blocked fetching (prova.education returned 403/429, and washingtonpost.com returned 403), so some entries rely on search-engine summaries of vendor pages. Treat everything sourced from a vendor page or a vendor-authored comparison blog as a **[MARKETING CLAIM]** unless it is marked otherwise. The most-used landscape source, the SnapSDR "19 platforms" comparison (published 2026-07-18), is **vendor-authored**: SnapSDR runs on Tough Tongue AI infrastructure and ranks Tough Tongue first.

## Which products exist, and what each does and does NOT do

### Takeaway
By late 2026 there is a crowded field of "AI oral exam" products. It splits into (a) **submission-anchored viva tools** (Viva/vivaproof, Rocketproof, Prova, Eduface, Vocina, Integrevise, Sherpa's "student paper" mode), (b) **course-material-anchored oral exams or check-ins** (Professr, OralExam.AI, Tough Tongue AI, Socratic Mind, the NYU Stern voice-agent exam), (c) **human-led oral assessment with AI assistance** (FeedbackFruits, Cadmus), (d) **practice and role-play platforms** (InStage, Yoodli, Bodyswaps, VirtualSpeech and others), and (e) **code-platform LLM graders** (PrairieLearn, Codio, CodeGrade) that grade written explanations but do not run vivas. Only one product (Viva/vivaproof) publicly shows questions anchored to specific passages of the submission. I found no commercial product that publicly claims line-level code anchoring combined with course-lecture grounding.

### Cited Findings

**A. Submission-anchored viva tools**

- **Viva (vivaproof.com, "Viva Proof, Inc.", © 2026)**
  - **What it does:** runs a 5–10 minute voice conversation after submission, in English and Korean, and the demo also accepts typed replies. — [vivaproof.com](https://www.vivaproof.com/)
  - **Inputs:** PDF, DOCX, images, code and XLSX (essays, lab reports, slides, posters, spreadsheets). — [vivaproof.com](https://www.vivaproof.com/)
  - **Anchoring:** questions are anchored to specific parts of the work, for example "You chose a t-test in section 3" and a poster question about "4 to 6 grams". Report claims "link to highlighted passages in the actual submission", with OCR for scanned posters. — [vivaproof.com](https://www.vivaproof.com/)
  - **Output:** an Understanding rating and an Authenticity rating ("High / Clean / Concern"), per-topic ratings such as "Owns the core tradeoff" or "Shaky", "integrity signals", and blind re-scoring by AIs from other providers. Grades return through LTI 1.3. A "Viva Card" credential is SHA-256 sealed and can be revoked by the school. Instructors decide outcomes. — [vivaproof.com](https://www.vivaproof.com/)
  - **Anti-paste measures:** a voiceprint identity check in every session, natural-pace adaptive follow-ups, "generated visual probes" that the page says answers read from a second screen don't hold up to, optional camera and tab-focus checks (off by default), and a human-run 1:1 alternative for any student. — [vivaproof.com](https://www.vivaproof.com/)
  - **Pricing and traction:** licensed per student per year, with pilot pricing on request. The page says it is "now piloting with schools and universities on three continents". Its testimonials name an MIT lecturer, and Harvard appears only in an example dashboard. Its stats block shows placeholder values ("0%", "0 independent AIs"), so treat its metrics as unfinished or unverified. — [vivaproof.com](https://www.vivaproof.com/)
  - **What it does NOT do (from the page):** it shows no grounding in course lecture materials, it names no founders, and it publishes no funding.
- **Prova (prova.education) — EXISTS [VERIFIED as a live site; details are MARKETING]**
  - **What it does:** "AI-powered oral exams for higher education" that run adaptive spoken examinations at scale with rubric-aligned grading. — [prova.education](https://prova.education/)
  - **Workflow:** students complete work in a "recorded workflow session" and then explain their reasoning in a short AI oral exam. — [Prova Trust Center](https://trust.prova.education/) (via search summary; the fetched page returned only its title)
  - **Output:** transcripts plus quoted evidence for each rubric line, and the instructor keeps final say ("the final grade is always yours"). — [prova.education](https://prova.education/)
  - **Compliance:** claims SOC 2 and FERPA. — [prova.education/oral-assessment-platform](https://prova.education/oral-assessment-platform)
  - **CS page:** "spoken code walkthroughs" where students walk through their own code after submitting work that autograders still check. — [prova.education/oral-assessment-computer-science](https://prova.education/oral-assessment-computer-science)
  - **Unknown:** I could not confirm line-level anchoring, use of course materials, pricing, customers, founders or funding, because the site blocked fetching.
- **Rocketproof:** an oral defense of the student's own paper, deck or reading response. It builds a question plan from the submission (for example, about 12 questions for a 40-page thesis) and outputs a recording, transcript, rubric scores and "integrity flags", with LTI 1.3 grade passback to Canvas, Blackboard, Moodle and D2L. — [SnapSDR comparison (vendor blog)](https://www.snapsdr.com/blog/ai-oral-exam-roleplay-platforms-universities-2026). A direct search for "Rocketproof" returned no primary pages, so **[UNVERIFIED beyond one vendor-authored listing]**.
- **Eduface:** offers "three AI oral exam formats" with questions generated from student work, plus rubric support and LMS delivery, but public detail is thin. — [SnapSDR](https://www.snapsdr.com/blog/ai-oral-exam-roleplay-platforms-universities-2026) **[UNVERIFIED]**
- **Viva by Vocina (viva.vocina.ai):** generates questions from a student's uploaded work for "checking learners understanding through conversation". It states it is not an AI detector, and a third-party roundup notes it declares third-party data sharing and Australian hosting. — [viva.vocina.ai](https://viva.vocina.ai/); [aieducator.tools roundup](https://blog.aieducator.tools/posts/ai-resistant-assessment-tools)
- **Integrevise:** pairs a submitted written artifact with a short adaptive viva in which students explain their work in their own words. It was piloted at a Midwest liberal arts college (Lindenwood faculty paper), and the authors call the results preliminary. — [Lindenwood Digital Commons](https://digitalcommons.lindenwood.edu/faculty-research-papers/814)
- **Sherpa (Stanford-origin) — CONFIRMED Stanford-origin**
  - **Origin:** built by Stanford undergraduates Joseph Tey and Shaurya Sinha. — [EdSurge 2023-10-05](https://www.edsurge.com/news/2023-10-05-as-ai-chatbots-rise-more-educators-look-to-oral-exams-with-high-tech-twist)
  - **How it works:** the instructor uploads an assigned reading, or the student uploads their own paper. Sherpa asks questions using the Depth-of-Knowledge framework, with instructor-written or AI-generated questions. It records audio, or audio plus video, through the webcam, transcribes the answers, and flags off-point answers for teacher review. — [EdSurge](https://www.edsurge.com/news/2023-10-05-as-ai-chatbots-rise-more-educators-look-to-oral-exams-with-high-tech-twist)
  - **Known weakness:** a Maine teacher noted that students had notes in front of them, possibly from a chatbot. — [EdSurge](https://www.edsurge.com/news/2023-10-05-as-ai-chatbots-rise-more-educators-look-to-oral-exams-with-high-tech-twist)
  - **2025 activity:** an August 2025 K-12 district PD session promoted "Sherpa Labs AI" for voice-enabled discussion and assessment. — [RJUHSD PD sched](https://rjuhsdaugustpd2025.sched.com/list/descriptions/venue/Oak+305). The "Sherpa Labs" learner-uploads-submission flow is described on a thin third-party page. — [industryprofessor.ai](https://industryprofessor.ai/ai-sherpa-labs/)
  - **Status:** I found no 2026 product news, pricing or funding. It appears to have drifted toward K-12 **[INFERENCE]**.

**B. Course-material-anchored AI oral exams and check-ins**

- **Professr (professr.io) — EXISTS, but only through third-party listings [PARTIALLY VERIFIED]**
  - **What it does:** weekly AI-avatar interviews before class, grounded in the syllabus, objectives, rubrics and assignments the professor uploads. It outputs individual and class-wide "understanding signals", and students meet the avatar in Professr's app. — [SnapSDR](https://www.snapsdr.com/blog/ai-oral-exam-roleplay-platforms-universities-2026); [Tough Tongue AI blog](https://www.toughtongueai.com/blog/best-ai-roleplay-oral-assessment-platforms-higher-education/)
  - **Positioning:** "built for formative checks more than graded finals". — [Tough Tongue AI blog](https://www.toughtongueai.com/blog/best-ai-roleplay-oral-assessment-platforms-higher-education/)
  - **Traction (claimed):** educators from Duke, USC, Boston College and CUNY are cited on its site, according to SnapSDR. — [SnapSDR](https://www.snapsdr.com/blog/ai-oral-exam-roleplay-platforms-universities-2026)
  - **Not found:** I could not find its own site in search, and found no pricing or funding. **Does NOT** appear to anchor to an individual student's submission.
- **NYU Stern voice-AI oral exam (Panos Ipeirotis and Konstantinos Rizakos), with the platform at viva.stern.nyu.edu**
  - **Format:** a voice exam with an ElevenLabs agent and a "council" of three LLMs (Claude, Gemini, GPT-5) that grade each transcript, then deliberate, with Claude chairing the final grade. Instructors review and publish the results. — [arXiv 2603.18221](https://arxiv.org/html/2603.18221); [viva.stern.nyu.edu](https://viva.stern.nyu.edu/)
  - **Inputs:** the agent received each student's **capstone project summary** as session variables and asked about goals, data, modeling, evaluation and failure modes, plus a case discussion drawn from a library of course cases. It **could not access the submitted files (slides and code)**, and the authors list that as future work. — [arXiv 2603.18221](https://arxiv.org/html/2603.18221)
  - **Results:** 36 students in Fall 2025 and 37 in Spring 2026. Council agreement (Krippendorff's α on the 0–20 score, after deliberation) was 0.83 and then 0.95, and about 3% of exams were escalated to human audit. Cost was about $15 total, or $0.42 per student, for Fall 2025. 83% and then 63% of students found it more stressful than written exams, while 70% and then 66% agreed it tested real understanding. — [arXiv](https://arxiv.org/html/2603.18221); [The Decoder](https://the-decoder.com/nyu-professor-fights-ai-cheating-with-ai-powered-oral-exams-that-cost-42-cents-per-student/); [NYU News 2026-01-28](https://nyunews.com/news/2026/01/28/stern-professors-ai-exams/)
  - **Validation:** the authors report no formal human-AI agreement statistic and call the instructor comparison informal. — [arXiv](https://arxiv.org/html/2603.18221)
- **Socratic Mind (Georgia Tech, with UC San Diego):** an AI examiner using Socratic follow-ups. Students answer by speech or text, and teachers author questions in a web interface. It was piloted with about 2,000 students and won a $50k Catalyst Award (MIT Solve). It is described as a research project becoming a for-profit, targeting higher education and recruiting. — [Georgia Tech IC news](https://www.ic.gatech.edu/external-news/ai-oral-assessment-tool-uses-socratic-method-test-students-knowledge); [MIT Solve](https://solve.mit.edu/solutions/90692); [socraticmind.com](https://www.socraticmind.com/). Its questions come from instructor templates, **not from the student's submission**.
- **Tough Tongue AI:** multimodal conversational agents configured with persona, goals, rubrics and course knowledge. They can show visuals mid-conversation and join Google Meet, Zoom or phone calls. Kellogg ran a voice exam over Google Meet, and SMU Dallas is also a customer (both self-reported in its affiliate blog). — [SnapSDR](https://www.snapsdr.com/blog/ai-oral-exam-roleplay-platforms-universities-2026); [Tough Tongue guide](https://www.toughtongueai.com/blog/ai-oral-exams-guide-for-professors)
- **OralExam.AI** (personalized voice exams tied to course content, with Canvas integration), **Coraltalk** (voice-first oral exams) and **Claire Labs** (custom audio-native agents) appear only in the vendor listing. — [SnapSDR](https://www.snapsdr.com/blog/ai-oral-exam-roleplay-platforms-universities-2026) **[UNVERIFIED]**
- **UPDADA**, **AiLearn360**, **StudierAI** and **LearnCast** are student-side oral-exam *simulators* for practice, not institutional assessment. — [ailearn360 blog](https://ailearn360.com/en/blog/best-ai-apps-to-simulate-an-oral-exam-ailearn360-studierai-appuntoai-and-alternatives); [updada.com](https://www.updada.com/); [learncastai](https://learncastai.com/en/tools/oral-exam-simulator)
- **OLLE (TUM):** instructors or students upload lecture notes and the AI generates exam questions. It is a study tool, not an integrity viva. — [TUM edtech](https://www.edtech.tum.de/?p=3153)

**C. Human-led oral assessment with AI assistance**

- **FeedbackFruits:** the AI suggests questions, flags moments to probe and writes a post-session summary, while **the human conducts the exam and grades it**. Output includes recordings, structured evidence and LMS grade return. — [SnapSDR](https://www.snapsdr.com/blog/ai-oral-exam-roleplay-platforms-universities-2026). This is the closest commercial match to "a question sheet for a human examiner" **[vendor-blog description; not verified on the FeedbackFruits site]**.
- **Cadmus:** asynchronous recorded oral submissions with consistent marking and human moderation. — [SnapSDR](https://www.snapsdr.com/blog/ai-oral-exam-roleplay-platforms-universities-2026)
- **Bongo:** in-LMS video Q&A in which the learner answers a prompt on camera within a set window, followed by AI analysis and peer or instructor feedback. — [SnapSDR](https://www.snapsdr.com/blog/ai-oral-exam-roleplay-platforms-universities-2026)

**D. Practice and role-play (adjacent, not submission interrogation)**

- **InStage:** 5–15 minute voice conversations for mock interviews and check-ins. It claims more than 300k sessions and SOC 2 Type II, and names Waterloo, Toronto, UBC and Northeastern as customers. — [SnapSDR](https://www.snapsdr.com/blog/ai-oral-exam-roleplay-platforms-universities-2026)
- **Other platforms:** Yoodli, Bodyswaps, VirtualSpeech, Ovation (which can simulate thesis defenses), Virti and Mursion. Infrastructure layers include ElevenLabs and Anam. — [SnapSDR](https://www.snapsdr.com/blog/ai-oral-exam-roleplay-platforms-universities-2026)

**E. Code-platform LLM graders (they grade explanations, not viva)**

- **PrairieLearn AI grading:** evaluates source code, **code explanations** and written reasoning against item-level rubric scores, with instructor review or override. Student identities are withheld from the model, and submissions are not used for training. A pull request added submitted code files (labeled with filenames) into AI grading. — [PrairieLearn docs](https://docs.prairielearn.com/aiGrading/); [PR #15763](https://github.com/PrairieLearn/PrairieLearn/pull/15763). It does NOT run an oral or conversational follow-up.
- **Codio LLM Rubric Auto-grader:** grades submissions with an LLM-generated rubric and can show feedback to students without instructor approval. — [Codio docs](https://docs.codio.com/instructors/authoring/assessments/llm-based-auto-rubric.html). It does NOT question the student.
- **CodeGrade:** offers prompt-writing exercises (students write prompts, an LLM generates code and CodeGrade tests it) and a configurable AI assistant (hints only, conceptual only, or full help) whose logs are visible to instructors. — [CodeGrade](https://www.codegrade.com/solutions/teach-efficient-prompting); [CodeGrade blog](https://www.codegrade.com/blog/how-to-configure-an-ai-assistant-for-code). I found **no "explain your code" viva feature**.

**F. Academic prototypes**

- **Dartmouth (Tregubov and Traore), SIGCSE TS 2026 lightning talk:** an AI conversational assessment about students' own code, integrated into Classmoji, a GitHub-native LMS. It asks about implementation choices and algorithmic reasoning with adaptive follow-ups, delivered by **text chat**. The abstract gives no empirical results and does not say whether questions are line-anchored. — [SIGCSE 2026](https://sigcse2026.sigcse.org/details/sigcse-ts-2026-lightning-talks/17/AI-Driven-Oral-Examinations-for-Code-Assessment-Evaluating-Understanding-Beyond-the-)
- **AutoViva / "Automated Viva Voce Using Generative AI for Student Coursework Authentication" (ACM, 2025):** the student uploads a PDF of their work before an automated viva. — [ACM DL](https://dl.acm.org/doi/10.1145/3766557.3766564)
- **Viva voce simulator (Church, Drake and Harris; arXiv 2511.05530):** generates the questions an examiner might ask from a written submission and produces a transcript **for a human examiner's judgment**. — [arXiv 2511.05530](https://arxiv.org/html/2511.05530v1)
- **Engineering-lab framework (arXiv 2509.25258):** after a student submits, the AI asks questions based on the student's allocated problem. — [arXiv 2509.25258](https://arxiv.org/pdf/2509.25258)
- **"Questions about Learners' Code" (QLC) line of work (Aalto, ICSE-SEET 2024):** automatically generated comprehension questions about a learner's own program. This study tested whether LLMs can answer them and found they can trace execution but make novice-like errors. — [arXiv 2404.11734](https://arxiv.org/pdf/2404.11734)
- **Line-by-line code explanation assessment (Oli et al., arXiv 2401.05399):** LLMs compare student line-by-line explanations against expert ones and perform comparably to fine-tuned models. — [arXiv 2401.05399](https://arxiv.org/abs/2401.05399v1)
- **Tool-invariant computational methods course (arXiv 2607.15518):** a 10-minute one-on-one human defense of AI-permitted code. **The instructor strips the comments first**, students walk through chosen sections, and the examiner asks "why should I believe this?" probes. — [arXiv 2607.15518](https://arxiv.org/pdf/2607.15518)

**G. Hiring and coding-interview adjacent**

- **HackerRank, CoderPad and CodeSignal:** have added "AI-off" modes. HackerRank's July 2026 documentation describes AI-assisted IDE interviews meant to observe reasoning, and its August 2026 "AI Fluency Evaluation" reviews both AI interactions and IDE activity. — [techinterview.org](https://www.techinterview.org/post/3233475415/ai-coding-interviews-rules-2026/) (a secondary source)
- **Candidate prep advice:** advice sites now tell candidates to "be ready to explain every line you submit", because follow-up questioning is the practical integrity check. — [techinterview.org](https://www.techinterview.org/post/3233475415/ai-coding-interviews-rules-2026/); [formation.dev](https://formation.dev/blog/ai-assisted-coding-interviews)
- **Prevalence (vendor-compiled):** 38.5% of 19,368 interviews between July 2025 and January 2026 were flagged for AI assistance, rising to 48% for technical roles. — [metaintro](https://www.metaintro.com/blog/employers-rebuild-interviews-38-percent-ai-flagged-2026)
- **Interview-integrity protocols:** see [Humanly](https://www.humanly.io/blog/ai-interview-anti-cheating-protocol-2026) and [Evidenced](https://www.evidenced.app/blog/how-to-detect-ai-generated-answers-in-job-interviews). These are vendor blogs.

### Inferences
- The "AI viva on submitted work" category went from a few prototypes in 2023 (Sherpa) to a **crowded 2026 field** (at least 8 named submission or course-anchored vendors, plus several academic systems). The Acader Coach therefore cannot differentiate on "AI asks you about your work" alone.
- **Differentiation gap:** no product found combines (1) **line-level or claim-level anchoring** in code, (2) **grounding in the instructor's own lecture materials**, and (3) **comprehension-tier output with no integrity verdict**.
  - Viva/vivaproof comes closest on (1) for documents, but its output includes an "Authenticity: Clean / Concern" rating, which is a cheat-adjacent signal that Acader rule 6 forbids.
  - Professr, OralExam.AI and Tough Tongue cover (2) but not (1).
  - The NYU Stern system explicitly lacked access to code and slides.
- Several competitors frame output as "integrity flags" or "authenticity" (Viva and Rocketproof). This is a positioning opening for a non-surveillance "comprehension tier" framing that is EU AI Act-friendly.
- Code platforms (PrairieLearn, Codio, CodeGrade) are well placed to add a viva step because they already hold the code. PrairieLearn adding submitted files to AI grading in 2026 is a step in that direction, which makes it a likely fast follower.

### Gaps
- **Prova:** the site exists, but I could not fetch it (403/429). Founders, location, pricing, customers, funding, launch date, and whether questions reference specific code lines are all unknown.
- **Professr:** its own site was not found by search. Every detail is second-hand from vendor-authored comparison blogs, and the named universities (Duke, USC, Boston College, CUNY) are "educators cited on site", not confirmed contracts.
- **Rocketproof, Eduface, OralExam.AI, Coraltalk and Claire Labs:** each is known only from one vendor-authored list, with no primary page found.
- **Pricing:** only the NYU Stern research cost (about $0.42 per student) and Viva's "per student per year" model are public. I found no price lists.
- **Funding and size:** I found no Crunchbase or TechCrunch funding data for any of these vendors in this session.
- **Not researched with sources this session:** Gradescope, Karat, interviewing.io, HireVue, Khanmigo, Studiosity, Akindi and Cadmus's own site. From prior knowledge, which is **unverified here**:
  - Gradescope is grading workflow only, with no viva.
  - Akindi is bubble-sheet multiple choice and not relevant.
  - Studiosity is writing feedback and tutoring, not oral checks.
  - Khanmigo is a Socratic tutor, not assessment of a submission.
  - Karat and interviewing.io use live human interviewers.
  - HireVue is asynchronous video interviewing.
- **Washington Post, 2025-12-12** ("College professors use oral exams to combat AI"): the article returned 403, so I don't know which tools and universities it names.

## Which tools anchor questions to the student's own citations or code lines, and which use course materials?

### Takeaway
Anchoring to specific passages is publicly shown only by Viva (vivaproof), at section and passage level for documents. Prova and Dartmouth's Classmoji tool claim "your own code" walkthroughs, but neither shows line-level anchoring. **No product found anchors questions to the student's citations.** Course-material grounding is offered by Professr, Tough Tongue, OralExam.AI and (via case libraries) the NYU Stern system, none of which anchor to the individual submission.

### Cited Findings
- Viva report claims "link to highlighted passages in the actual submission", and its example questions cite a section ("t-test in section 3") and specific values. — [vivaproof.com](https://www.vivaproof.com/)
- Prova offers "spoken code walkthroughs" of the student's own code, with no line-level detail found. — [prova.education CS page](https://prova.education/oral-assessment-computer-science)
- The Dartmouth Classmoji tool generates questions about "implementation choices, algorithmic reasoning" from the student's code, and the abstract does not specify line anchoring. — [SIGCSE 2026](https://sigcse2026.sigcse.org/details/sigcse-ts-2026-lightning-talks/17/AI-Driven-Oral-Examinations-for-Code-Assessment-Evaluating-Understanding-Beyond-the-)
- The NYU Stern agent had only a project summary, not the code or slides. — [arXiv 2603.18221](https://arxiv.org/html/2603.18221)
- Professr grounds questions in the uploaded syllabus, objectives, rubrics and assignments, and Tough Tongue grounds them in "course knowledge". — [SnapSDR](https://www.snapsdr.com/blog/ai-oral-exam-roleplay-platforms-universities-2026)
- Academic work on line-by-line explanations (Oli et al.) and QLCs shows the research basis for line-anchored code questions exists. — [arXiv 2401.05399](https://arxiv.org/abs/2401.05399v1); [arXiv 2404.11734](https://arxiv.org/pdf/2404.11734)

### Inferences
- The combination "submission-anchored AND course-graph-grounded" appears unoccupied in public positioning as of 2026-10. That supports Acader's planned blind comparison (graph versus raw notes) as the key test of whether course grounding matters to instructors.
- Citation-anchored questioning (asking a student about a source they cited) appears to be an open niche for the writing track.

### Gaps
- Vendor demos could show line-level anchoring that their marketing doesn't describe. That needs hands-on trials of Prova, Viva and Rocketproof.

## How do tools handle the "student pastes the question into ChatGPT" attack?

### Takeaway
The main defenses are **real-time voice** (latency makes relaying answers hard), **adaptive follow-ups** on the student's own words, **identity checks** (voiceprint, roster or personal URL), **optional camera and tab-focus** checks, **generated visual probes**, and **human fallback**. Every serious source admits the defenses are incomplete: notes or live AI coaching off-camera cannot be fully prevented.

### Cited Findings
- **Viva:** voiceprint every session, natural-pace adaptive follow-ups, generated visual probes ("answers read from a second screen don't hold up"), optional camera and tab focus that is off by default, and a human 1:1 alternative. — [vivaproof.com](https://www.vivaproof.com/)
- **NYU Stern:**
  - **Deterrents:** webcam and audio recording were required, identity was checked by NetID (Fall) and then a personal URL (Spring), and follow-ups responded to the student's own answers.
  - **Admitted limit:** "live AI coaching and a second person off-camera cannot be fully prevented". The authors also argue that because questions are dynamic, the exam structure can be shared in advance.
  - Sources: [arXiv 2603.18221](https://arxiv.org/html/2603.18221); [Lindenwood/arXiv search summary](https://arxiv.org/pdf/2603.18221)
- **Sherpa:** in a 2023 pilot, students had notes in front of them that "could have come from a chatbot". — [EdSurge](https://www.edsurge.com/news/2023-10-05-as-ai-chatbots-rise-more-educators-look-to-oral-exams-with-high-tech-twist)
- **Hiring:** platforms use "AI-off" modes plus live follow-up questioning ("explain every line you submit"). — [techinterview.org](https://www.techinterview.org/post/3233475415/ai-coding-interviews-rules-2026/)
- **Human defense:** strip comments from the code before the human defense so narrated AI code can't be read aloud. — [arXiv 2607.15518](https://arxiv.org/pdf/2607.15518)
- **Text-chat format:** Socratic Mind and Dartmouth's Classmoji tool allow typed answers, which offer the least protection against paste attacks. — [GT news](https://www.ic.gatech.edu/external-news/ai-oral-assessment-tool-uses-socratic-method-test-students-knowledge); [SIGCSE 2026](https://sigcse2026.sigcse.org/details/sigcse-ts-2026-lightning-talks/17/AI-Driven-Oral-Examinations-for-Code-Assessment-Evaluating-Understanding-Beyond-the-)
- **Caution against detection framing:** in a 38-student graphic design study, 71.1% showed inconsistencies between their work and their oral explanation, and the authors warn that language anxiety and prior instruction are alternative explanations. — [journals.calstate.edu](https://journals.calstate.edu/ijaipil/article/download/7225/5447/24017)

### Inferences
- Async text vivas (such as Acader's planned "thin async viva runner") are the most exposed to the paste attack. Questions anchored to specific lines and to the student's own prior answers raise the cost, but don't eliminate it. A voice or human-run option for low-confidence cases matches what competitors do and Acader's "recommended oral check" rule.

### Gaps
- I found no independent measurement of how well any of these defenses work against a student relaying questions to an LLM.

## Does any product produce a question sheet for a human TA to run a short oral?

### Takeaway
No commercial product is clearly marketed as "AI-generated viva question sheet for a TA". The closest are FeedbackFruits, where AI suggests questions and probe moments to a human examiner (per a vendor blog), and the academic viva-voce simulator, which produces a transcript for a human examiner. This looks like a gap that fits Acader's concierge pilot and its "a human decides" posture.

### Cited Findings
- FeedbackFruits: "AI suggests questions, flags moments to probe, writes post-session summary; human conducts and grades". — [SnapSDR](https://www.snapsdr.com/blog/ai-oral-exam-roleplay-platforms-universities-2026)
- The viva voce simulator (arXiv 2511.05530) generates the questions an examiner might ask from a written submission, and its output supports the human examiner's judgment. — [arXiv 2511.05530](https://arxiv.org/html/2511.05530v1)
- The VV / "viverly" site claims "AI analyzes submitted essays to extract key concepts and generate personalized viva questions", but only staging URLs were found. — [test.viverly.johnlocke.com](https://test.viverly.johnlocke.com/) **[UNVERIFIED; staging site]**
- Human-run defenses of AI-permitted code are documented in course design papers, but without a tool that generates the questions. — [arXiv 2607.15518](https://arxiv.org/pdf/2607.15518)

### Inferences
- A "TA viva sheet" (line-anchored questions plus expected-answer cues drawn from the instructor's lectures) is a low-competition wedge product and matches Acader's Approach A concierge pilot directly.

### Gaps
- I did not confirm on the FeedbackFruits site whether its question suggestion is anchored to the submission or generic.
