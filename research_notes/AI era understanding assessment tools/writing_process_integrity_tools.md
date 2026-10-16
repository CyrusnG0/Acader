# Writing-process, authorship and academic-integrity platforms for universities (as of 2026-10-14)

Scope note: about 20 searches and fetches. Vendor marketing claims are marked **[VENDOR CLAIM]**. Items I could not confirm from a primary source are marked **[UNVERIFIED]**. Two key pages returned HTTP 403 and could not be read in full: Turnitin's Feb 2026 press release and HKBU *Young Reporter*'s May 2026 article. Their content below comes from search-result summaries only.

## Q1. Competitor map: what each tool does and does not do, paste handling, citation checks, questioning, pricing, customers, launches

### Takeaway
The market splits into three layers.
- **Process capture:** Turnitin Clarity, Grammarly Authorship, GPTZero Writing Replay, Brisk Inspect Writing, Cadmus, PowerNotes Insight.
- **"AI that helps but won't write" coaches:** Clarity's assistant, Khanmigo Writing Coach, Packback, Studiosity Writing Feedback+, Claude Learning Mode, ChatGPT Study Mode, Gemini Guided Learning.
- **Post-hoc detection and similarity:** Turnitin AI detection, Copyleaks, GPTZero, Originality.ai, VeriGuide AWD.

Paste handling is almost always "flag the paste in a replay or report". None of the tools I found turns pasted or outside-AI text into a comprehension check. Citation *existence* checks are emerging from GPTZero and Copyleaks. Questioning the student is emerging only through oral-assessment add-ons (Cadmus Oral Assessment, Viva/Vocina startups).

### Cited Findings

**Turnitin Clarity (process + in-environment AI assistant)**
- General availability was announced 2025-07-15. Clarity is a writing environment where students write, optionally with an built-in AI assistant, then revise and reflect. Educators get insight into how the writing was built from creation to final submission. — [Turnitin press: Turnitin Delivers Turnitin Clarity](https://www.turnitin.com/press/turnitin-delivers-turnitin-clarity); [itbrief.com.au](https://itbrief.com.au/story/turnitin-launches-clarity-to-bolster-academic-integrity-with-ai)
- Preview features:
  - a writing report showing writing time, edits and **pasted content**
  - a playback tool
  - an AI assistant that is English-only and optional for the institution
  - delivery as an add-on to Feedback Studio

  — [Turnitin Educator Network: Clarity feature highlights](https://turnitin.forumbee.com/t/60yk2kp/turnitin-clarity-feature-highlights-ai-support-writing-reports-and-more)
- Licensing: a paid add-on that needs a Feedback Studio licence and is "licensed separately at an additional cost". No public price is listed. — [Turnitin admin FAQ for Clarity](https://guides.turnitin.com/hc/en-us/articles/37670935742989-FAQs-for-administrators-using-Turnitin-Clarity)
- Pricing reference point: a third-party blog cites a May 2026 US public procurement schedule listing Feedback Studio Essential at **$6.70 per FTE including AI detection** (this is not Clarity pricing). **[UNVERIFIED, single contract]** — [edusageai.com](https://www.edusageai.com/blogs/turnitin-pricing-for-teachers-and-schools-in-2026-what-you-can-actually-buy)
- Feb 2026 Turnitin press release, per the search summary only (page returned 403):
  - Since Oct 2025, about 15% of essay submissions had more than 80% AI-generated writing.
  - It promotes Clarity's AI assistant that "helps, but refuses to write for, the student".

  — [Turnitin press: transparency about AI use](https://www.turnitin.com/press/turnitin-data-shows-transparency-about-ai-use-benefits-students-and-educators)
- Oct 2026: AI writing detection expanded to German, Dutch and Turkish via Turnitin Originality, and as an add-on for iThenticate 2.0. — [Turnitin product updates](https://guides.turnitin.com/hc/en-us/articles/29645383597965-Turnitin-product-updates); [press via webdisclosure](https://www.webdisclosure.com/press-release/turnitin-etr-turnitin-now-offers-ai-writing-detection-for-german-dutch-and-turkish-language-submissions-mtQWZ2Cweax)
- Third-party blogs claim a 2026 "AI bypasser/humanizer detection" update and multimodal detection. **[UNVERIFIED, not on Turnitin pages I reached]** — [humanizeaiwork.com](https://www.humanizeaiwork.com/blog/turnitin-2026-update-ai-detection-features)
- What Clarity does NOT do (from the feature lists above): I found no evidence that it asks the student questions about their sources or reasoning, or verifies citations against the sources. **[absence of evidence, not confirmed absence]**

**Grammarly (Authorship, Grammarly for Education, AI agents)**
- Authorship tracks whether text is typed, copied/pasted, or AI-generated, and produces a replay or report the student can choose to share. Grammarly says it works in Google Docs, Word, Chrome, Edge and Firefox, and integrates with Canvas and Blackboard. — [Grammarly Authorship](https://www.grammarly.com/edu/authorship)
- Conflict: a CDW reseller listing says Google Docs is live, Word is in beta, and LMS integration is only planned. The listing may be older. Institutional licence has a **1,000-licence minimum**. — [CDW listing](https://www.cdw.com/product/grammarly-for-education-institution-subscription-license/7455003?pfm=srh)
- Vendor case study: Rowan-Cabarrus CC reported a 96% drop in integrity violations. **[VENDOR CLAIM]** — [Grammarly Authorship](https://www.grammarly.com/edu/authorship)
- Texas State is offering Grammarly to up to 5,000 faculty and students for Fall 2026, with "Authorship for transparency in the writing process" training sessions on 2026-08-21 and 2026-08-28. — [Texas State signup](https://signup.txstate.edu/topics/2562-8-28-2026-grammarly-authorship-for-transparency-in-the-writing-process)
- Aug 2025: AI agents launched in Grammarly Docs. Sources disagree on the count (8 or 9).
  - **Citation Finder** finds sources for claims and formats citations.
  - **AI Grader** grades a draft against an uploaded rubric and instructor information.
  - Both are available on Free and Pro. The AI detector and plagiarism checker are Pro-only.

  — [SiliconANGLE 2025-08-18](https://siliconangle.com/2025/08/18/grammarly-leans-writing-assistance-agents-students-professionals/); [Tom's Guide](https://www.tomsguide.com/ai/grammarly-just-added-9-ai-agents-heres-how-they-can-help-your-writing)
- University at Buffalo's teaching centre calls AI Grader "one of the more invasive" tools, because it looks up instructors' public profiles. — [UB CATT](https://www.buffalo.edu/catt/ai-resources/ai-in-practice/grammarlys-new-ai-tools-what-faculty-should-know.html)
- Note: Grammarly's Citation Finder *supplies* sources for claims, which is the opposite of verifying the student's own sources.

**GPTZero (detector + Docs Writing Replay + citation check)**
- The Chrome/Google Docs extension offers Writing Replay (how text was written, edited and pasted, including multi-author shares), activity insights (paste and burst flags), live AI detection, feedback comments, and a bibliography/fact-check tool. GPTZero positions it against Draftback, Brisk Replay, Grammarly Authorship and Turnitin Clarity. — [Chrome Web Store listing](https://chromewebstore.google.com/detail/gptzero-ai-detector-and-h/kgobeoibakoahbfnlficpmibdbkdchap)
- GPTZero's citation/hallucination checker reportedly found 19 hallucinated citations among 141 in a 234-page report, and over 50 hallucinations in ICLR 2026 submissions. **[VENDOR CLAIM]** — [gptzero.me/sources](https://gptzero.me/sources); [GPTZero news](https://gptzero.me/news/latest/page/14/)
- GPTZero's own FAQ says no detector is 100% accurate and results should not be used for punishment. — [knightli review 2026-07](https://knightli.com/en/2026/07/06/gptzero-ai-detector-writing-authenticity-tool/)

**Brisk Teaching (Inspect Writing)**
- Replays Google Docs version history, marks key events, flags "suspicious copy and pastes", and shows revision after feedback. — [Brisk Inspect Writing](https://www.briskteaching.com/inspect-writing)

**Cadmus (in-LMS assessment environment + new oral layer)** — the most direct comparable to Acader's thesis
- An edit-tracking assessment platform. The University of Melbourne is a foundational shareholder and early adopter, and Arizona State's RealmSpark backed its latest round. — [Cadmus news](https://cadmus.io/news/cadmus-secures-backing-to-safeguard-university-learning-in-the-age-of-ai)
- 2026 pilots:
  - **University of Queensland**, Semester 1 2026, for written and group assessments. Data may support integrity processes. — [UQ ITaLI](https://itali.uq.edu.au/node/11841)
  - **Warwick**, 2026/27, with "no decision" on adoption. — [Warwick](https://warwick.ac.uk/services/digitallearning/strategicprojects/cadmus/)
  - **LSE**, edit-tracking proof of concept in 2025/26. — [LSE wiki](https://lse.atlassian.net/wiki/spaces/AG/pages/2929623049/Cadmus+Assessment+Edit+Tracking+Proof+of+Concept)
- **Cadmus Oral Assessment, Phase 1 (April/May 2026):**
  - Educators write the oral questions, aligned to learning outcomes.
  - Students record asynchronous video answers tied to their written work and the rubric.
  - Marking uses the existing rubrics.
  - The page describes no AI in Phase 1.
- **Cadmus Oral Assessment, Phase 2 (late 2026/2027):** Cadmus is "exploring" AI-personalised prompts based on the student's prior written work, rubrics and educator prompts. Cadmus says its AI will not mark or grade.
- Co-designed with unnamed Australian and UK universities. No pricing is published.

  — [Cadmus: Introducing Oral Assessment](https://cadmus.io/news/introducing-cadmus-oral-assessment-scalable-assurance-for-an-aienabled-world/); [product page](https://cadmus.io/product/oral_assessment/)

**PowerNotes (Insight)**
- Logs student research activity and AI interactions. Produces a downloadable activity log and a score comparing the process to the final submission. Positioned as "appropriate vs inappropriate AI use" rather than AI detection. **[VENDOR CLAIM, relayed by press]** — [Campus Technology 2023-10-31](https://campustechnology.com/articles/2023/10/31/powernotes-adds-tools-to-assist-students-research-and-writing-process.aspx); [PowerNotes Insight](https://powernotes.com/insight)

**Packback**
- Real-time AI feedback during drafting on structure, reasoning, research quality and mechanics, plus "Packback Originality" for plagiarism and GenAI. It claims up to 30% less grading time. **[VENDOR CLAIM]**
- Customer count conflicts: an aggregator says 2,300 institutions, while a 2023 press release said 600+ in the US and Canada.

  — [Packback higher ed](https://www.packback.co/higher-ed); [Packback institutions](https://packback.co/institutions)

**Studiosity (Writing Feedback+)**
- AI review of drafts covering structure, grammar, language, referencing and critical thinking, delivered inside the LMS.
- Licensed by Australian, UK and NZ universities (JCU, Deakin, Bedfordshire, Sheffield Hallam, Waikato).
- I found no Hong Kong licensee.

  — [JCU](https://www.jcu.edu.au/learn/guides/studiosity); [Deakin 2026-04-02](https://blogs.deakin.edu.au/deakinlife/2026/04/02/access-studiosity-from-your-unit-sites-24-7-personalised-academic-and-study-feedback/); [Bedfordshire](https://beds.ac.uk/academy-for-learning-teaching-excellence/learningdevelopment/studiosity); [Waikato](https://www.waikato.ac.nz/students/eresources/more-elearning-resources/studiosity-online-writing-feedback-tool)

**Khanmigo Writing Coach**
- Free tool that guides outlining, drafting and revising, with feedback in five categories: thesis, evidence and reasoning, structure, conclusion, style. It "won't tell students exactly what to write". Teachers track progress. Mainly K-12. — [Khan Academy blog](https://blog.khanacademy.org/making-essay-practice-easier-and-feedback-better-with-writing-coach); [THE Journal 2024-07-22](https://thejournal.com/articles/2024/07/22/khan-academy-launches-khanmigo-writing-coach.aspx)

**Frontier-lab education tiers**
- **Claude for Education** (April 2025): Learning Mode asks questions to test understanding rather than giving answers. Early customers were Northeastern and Champlain College. — [TechRadar](https://www.techradar.com/computing/artificial-intelligence/claude-goes-to-college-and-wants-to-be-your-study-buddy)
- **ChatGPT Edu** (May 2024), and Study Mode / "Study and Learn" (2025-07-29) for all users. Google's Gemini Guided Learning followed about a week later, along with free AI Pro offers for students. — [UPCEA](https://upcea.edu/ai-companies-roll-out-educational-tools); [TechCrunch](https://techcrunch.com/?p=2988353)
- These are general tutors. They have no process evidence and no link to a specific assignment's sources.

**Detection and similarity vendors**
- **Copyleaks:** native D2L Brightspace Assignments integration from 2025-09-30. Sheridan College is consolidating on Copyleaks as its sole plagiarism tool from Winter 2026. Copyleaks has a **Citation Checker** that finds each reference, resolves it against a trusted source, and flags works that cannot be found. — [Copyleaks/D2L press](https://www.streetinsider.com/Press+Releases/Copyleaks+Now+Natively+Integrated+in+D2L%E2%80%99s+Brightspace+Assignments/25376620.html); [Sheridan](https://ltsa.sheridancollege.ca/digital-learning-support-hub/?p=26512); [Copyleaks docs](https://docs.copyleaks.com/concepts/features/citation-checker)
- **Originality.ai:** probability score for AI generation, with weaker LMS integration than Turnitin. Only blog sourcing was found. **[weak source]** — [drmattlynch.com](https://www.drmattlynch.com/7-ai-tools-that-will-save-academic-integrity-in-2026/)
- **Honorlock / Proctorio:** exam proctoring, not writing process. The only sources were a proctoring-alternative vendor's blog citing litigation and CSU's 2022 room-scan case. **[UNVERIFIED]** — [forasoft blog](https://www.forasoft.com/blog/article/online-proctoring-anti-cheating-2026)

**AI oral / viva startups (questioning the student about their own submission)**
- **Viva (vivaproof.com):** the student uploads work, then holds a 5–10 minute voice conversation with adaptive follow-ups that "probe the reasoning behind every claim", plus a voiceprint identity check. **[VENDOR CLAIM]** — [vivaproof.com](https://www.vivaproof.com/)
- **Viva Vocina:** generates tailored questions from the uploaded file. Instructors review the audio, transcript and feedback. **[VENDOR CLAIM]** — [viva.vocina.ai](https://viva.vocina.ai/)
- **InitialView "Viva":** used by Caltech for admissions, and piloted by one high school for learning. — [Episcopal Academy CTL](https://episcopalacademyctl.substack.com/p/when-assessment-becomes-a-conversation)

### Inferences
- **Process replay is commoditised.** Turnitin, Grammarly, GPTZero, Brisk and Cadmus all ship it, and several are free or bundled. A replay alone is not a differentiator for Acader.
- **The common "paste" answer is to label the paste.** That pushes students who use outside AI toward retyping, which matches Acader's own rule that typing is not proof. A viva over the pasted or imported material is the open space.
- **Cadmus is the closest threat.** It has university-embedded assessment, edit tracking, and now oral questions tied to the written submission, with AI-personalised prompts planned for late 2026/2027. Its Phase 1 questions are teacher-written. The planned AI prompts draw on the student's work and rubric, not on how the course was taught (lectures). Acader's course-graph grounding remains distinct **[inference]**.
- **No vendor I found combines all three:** (1) an in-platform coach that refuses to write, (2) process evidence, and (3) questioning the student about *their cited sources*.
  - Turnitin Clarity has (1) and (2).
  - Cadmus has (2) and a non-AI version of (3) about the essay, not the sources.
  - Viva startups have (3) without (1) or (2).
  - GPTZero and Copyleaks verify that citations exist but ask no questions.

### Gaps
- No public pricing for Clarity, Cadmus, Packback, PowerNotes, Studiosity or the viva startups (except the single unverified Turnitin $6.70 per FTE data point).
- Not researched or not found:
  - Draftback and the Revision History extension: no results returned
  - Microsoft Copilot for Education
  - MagicSchool, Writable, NoRedInk: K-12-focused, not searched
  - Notebook-style tools (NotebookLM)
- Whether Clarity asks students reflection questions about sources: not confirmed either way.
- Grammarly Authorship LMS integration status: the vendor and the reseller conflict.

## Q2. Hong Kong / Asia market: who uses what

### Takeaway
Hong Kong universities are on Turnitin (including the AI writing report) plus CUHK's home-grown VeriGuide, which now has an AI Writing Detector. Policy is moving from "permission required" (2023) to "AI literacy", while trust in detectors is publicly eroding (HKBU student press, May 2026). I found no HK licensee of Cadmus, Studiosity, Clarity or Grammarly Authorship.

### Cited Findings
- **VeriGuide:** developed by CUHK Computer Science and Engineering for assignment collection, similarity detection and readability. By a 2008 CUHK Senate decision, all undergraduate and postgraduate assignments must be submitted via VeriGuide. — [CUHK academic honesty](https://cuhk.edu.hk/policy/academichonesty/Eng_htm_files_(2013-14)/p09.htm); [VeriGuide intro](https://veriguide1.cse.cuhk.edu.hk/portal/page/materials/veriguide_introduction.pdf)
- VeriGuide is also used by PolyU's Research and Innovation Office. — [PolyU RIO VeriGuide](https://polyu.edu.hk/rio/guidelines-forms-and-systems/online-systems/veriguide)
- **VeriGuide AI Writing Detector (AWD)** is described as the newest feature. It outputs a probability of AI authorship with ">90% accuracy". **[VENDOR CLAIM, no independent evaluation found]** — [keep.edu.hk AWD page, 2025-02-26](https://keep.edu.hk/?p=79577)
- In 2023, CUHK said it would enhance VeriGuide to detect AI use. Press reported possible expulsion for improper AI use. — [Young Post 2023](https://www.youngpostclub.com/yp/discover/news/hong-kong/article/3213450/chinese-university-hong-kong-students-be-expelled-if-caught-using-chatgpt-or-ai-tools-new-guide)
- **HKUST** has had Turnitin AI writing detection in Feedback Studio since 2023-04-05 under its existing licence. — [HKUST CEI](https://cei.hkust.edu.hk/en-hk/turnitin)
- **CityU:** the Turnitin AI writing detection report is in Feedback Studio inside Canvas and is visible to teachers only. — [CityU DL support](https://cityu.edu.hk/dlsupport/teacher-canvas-turnitin-ai-writing-detection.html)
- **Lingnan:** Turnitin (in Moodle) has been mandatory for all written assignments since Term 2, 2016-17. — [Lingnan TLC](https://ln.edu.hk/tlc/support-for-staff/plagiarism-minimization-and-detection)
- **PolyU** has an "open and forward-looking" GenAI stance and recommends assessment redesign. PolyU CPCE (its continuing-education arm) says the Turnitin AI score must not be the sole basis for adverse action. — [PolyU EDC GenAI](https://www.polyu.edu.hk/en/edc/explore-a-topic/generative-ai/); [CPCE IT training](https://it-training.cpce-polyu.edu.hk/mod/book/view.php?id=1496)
- **HKU:**
  - In 2023 it moved from a ban to allowing GenAI, with a 20-prompt-per-month cap. — [The Standard](https://www.thestandard.com.hk/news/article/54903/HKU-makes-U-turn-to-allow-ChatGPT-use)
  - Its Senate later endorsed AI as a "fifth literacy" (date not shown in the snippet). — [HKU SPACE news](https://hkuspace.hku.hk/news/detail/hku-policy-on-use-of-generative-artificial-intelligence-for-teaching-and-learning)
  - I found no HKU-specific statement on the Turnitin AI detector.
- **HKBU *The Young Reporter* (2026-05-31), from search summary only (page 403):**
  - A HK nursing student failed a course in 2025 after an AI flag, and his appeal was rejected.
  - Of 12 HK institutions contacted, CUHK acknowledged false positives and cited appeal via "fact-checking interviews".
  - HKBU said teachers may request AI-use records and early drafts.
  - Others did not respond.

  — [The Young Reporter](https://tyr-jour.hkbu.edu.hk/2026/05/31/ai-detection-tools-spark-false-plagiarism-fears-among-university-students/)
- Australia and UK adoption of process and oral tools:
  - Cadmus: Melbourne, UQ, Warwick, LSE (see Q1).
  - Studiosity: many AU and UK universities.
  - Curtin published an "update on Turnitin AI detection tool" (content not read). — [Curtin](https://www.curtin.edu.au/news/oasis-news/update-on-turnitin-ai-detection-tool/)

### Inferences
- **HK institutions already fall back on interviews when a detector flag is disputed.** CUHK uses "fact-checking interviews" and HKBU asks for drafts and AI records. That is a manual, ad hoc version of a viva plus process evidence, which is the workflow Acader would formalise. This is a strong local wedge **[inference]**.
- **VeriGuide is a home-grown, Senate-mandated incumbent at CUHK.** Selling at CUHK likely means complementing VeriGuide rather than replacing it **[inference]**.

### Gaps
- Not found:
  - HKU's current AI-detector setting
  - HKBU's official policy
  - EdUHK and HKMU tools
  - whether any HK university has disabled Turnitin AI detection
- Which HK institutions beyond CUHK and PolyU use VeriGuide.
- Wider Asian adoption (Singapore NUS/NTU, mainland, Japan) was not researched.

## Q3. Which products already combine in-platform AI-guided writing, process evidence, and questioning the student about sources?

### Takeaway
None that I found does all three. The closest partial combinations are Turnitin Clarity (guided AI plus process), Cadmus (process plus teacher-set oral questions, with AI questions planned for late 2026/2027), and GPTZero (process replay plus citation-existence check, with no questioning).

### Cited Findings
- **Clarity:** process report and playback, plus an AI assistant that refuses to write. — [Turnitin forum](https://turnitin.forumbee.com/t/60yk2kp/turnitin-clarity-feature-highlights-ai-support-writing-reports-and-more); [Turnitin press](https://www.turnitin.com/press/turnitin-data-shows-transparency-about-ai-use-benefits-students-and-educators)
- **Cadmus:** edit tracking plus Oral Assessment tied to the written work. AI-personalised prompts are planned and explicitly "exploring". — [Cadmus Oral Assessment](https://cadmus.io/news/introducing-cadmus-oral-assessment-scalable-assurance-for-an-aienabled-world/)
- **GPTZero:** Writing Replay plus bibliography/fact-check. — [Chrome Web Store](https://chromewebstore.google.com/detail/gptzero-ai-detector-and-h/kgobeoibakoahbfnlficpmibdbkdchap)
- **PowerNotes:** research and AI-interaction log plus score. No questioning found. — [PowerNotes Insight](https://powernotes.com/insight)
- **Viva startups:** questioning about the submission ("probe the reasoning behind every claim"), but no writing environment. — [vivaproof.com](https://www.vivaproof.com/); [viva.vocina.ai](https://viva.vocina.ai/)

### Inferences
- The likely convergence path is Turnitin adding oral or reflection questions to Clarity, or Cadmus shipping its Phase 2 AI prompts. Acader's window is roughly 12–18 months **[ASSUMPTION]**.
- No competitor found grounds questions in *lecture-derived course knowledge*. All of them ground questions in the submission, the rubric or a generic LLM.

### Gaps
- No independent evaluations of any viva-style AI tool's fairness or accuracy were found.

## Q4. Evidence on AI-detection false positives and universities disabling detectors

### Takeaway
The evidence base is consistent:
- Detectors misclassify non-native English writing at high rates in the key study (61% average across seven detectors).
- Major universities (Vanderbilt in 2023, Waterloo in Sept 2025) have switched off Turnitin's AI detector.
- Others (Yale, JHU, Melbourne, PolyU CPCE) forbid detector scores as sole evidence.

This matters greatly for Hong Kong, where most students write in English as a second language.

### Cited Findings
- **Liang et al. (Stanford), *Patterns* 2023:**
  - Seven GPT detectors misclassified 61.3% of 91 TOEFL essays (from a Chinese forum) as AI-written.
  - About 19.8% of those essays were flagged unanimously.
  - The detectors made near-zero errors on native-speaker essays.
  - Turnitin was not tested.

  — [The Markup 2023-08-14](https://themarkup.org/machine-learning/2023/08/14/ai-detection-tools-falsely-accuse-international-students-of-cheating); [Business & Human Rights summary](https://www.business-humanrights.org/en/latest-news/stanford-study-finds-ai-detection-tools-to-be-biased-against-international-students/)
- **Vanderbilt** disabled Turnitin's AI detector in Aug 2023. It cited the claimed 1% false-positive rate (about 750 papers per year wrongly flagged at its 2022 volume) and a lack of transparency. — [Vanderbilt Brightspace](https://www.vanderbilt.edu/brightspace/2023/08/16/guidance-on-ai-detection-and-why-were-disabling-turnitins-ai-detector/)
- **Waterloo** discontinued Turnitin AI detection in Sept 2025. It cited unreliability, bias against non-native English writers, and inconclusive internal testing. — [Waterloo EdTech Hub](https://uwaterloo.ca/educational-technology-hub/news/discontinuing-use-ai-detection-functionality-turnitin)
- **Yale and Johns Hopkins:** reportedly told faculty not to use detector scores as evidence. One aggregator claims 12+ elite institutions (Yale, JHU, Northwestern, Georgetown, Pitt, NYU) have disabled the detector. **[UNVERIFIED, aggregators citing FT]** — [aiweekly.co](https://aiweekly.co/alerts/yale-johns-hopkins-waterloo-pull-back-on-ai-detection-tools); [pasqualepillitteri.it](https://pasqualepillitteri.it/en/news/14726/ai-detector-scores-banned-evidence-universities)
- **University of Cape Town** reportedly dropped AI detection (per the HKBU article). **[UNVERIFIED]** — [The Young Reporter](https://tyr-jour.hkbu.edu.hk/2026/05/31/ai-detection-tools-spark-false-plagiarism-fears-among-university-students/)
- **Glasgow:** Turnitin made AI detection opt-out after sector lobbying. — [Glasgow](https://www.gla.ac.uk/myglasgow/apg/aisoftwareupdate)
- **Melbourne:** high detector scores are "not proof" of misconduct. — [UniMelb academic integrity](https://academicintegrity.unimelb.edu.au/staff-resources/artificial-intelligence/university-policy-and-actions)
- **Arcadia University** posted a "6/1/2026 Update: Turnitin AI Writing Detection" (content not read). — [Arcadia helpdesk](https://helpdesk.arcadia.edu/hc/en-us/articles/46307380128397-6-1-2026-Update-Turnitin-AI-Writing-Detection)

### Inferences
- **Detector distrust plus ESL-heavy student bodies make a strong case in Hong Kong** for evidence-and-viva over detection, which supports Acader's "never a cheat report" posture.

### Gaps
- No 2025–2026 peer-reviewed benchmark of Turnitin's current model or VeriGuide AWD was found.
- No authoritative list of universities that have disabled the detector was found.

## Q5. Citation-verification tools used in assessment

### Takeaway
Citation *existence* checking is now productised (Copyleaks Citation Checker, GPTZero, open-source CheckIfExist). Scite Reference Check screens for retractions and contested work. None of these checks whether the student actually *understood or used* the source. No tool I found pairs citation verification with questioning the student.

### Cited Findings
- **Scite Reference Check** flags cited works that have been retracted, corrected or heavily disputed. Stanford provides it via SUNet for analysing bibliographies. — [Stanford Teaching Commons](https://teachingcommons.stanford.edu/opportunities/scite); [educatorstechnology review 2026-09](https://www.educatorstechnology.com/2026/09/scite-review.html)
- **Copyleaks Citation Checker** resolves each reference against trusted sources and flags works that cannot be found. — [Copyleaks docs](https://docs.copyleaks.com/concepts/features/citation-checker)
- **CheckIfExist** (open source) validates references against CrossRef, Semantic Scholar and OpenAlex. — [arXiv 2602.15871](https://arxiv.org/abs/2602.15871)
- A **GESIS 2026 paper** evaluates CheckIfExist, HalluCiteChecker, Hallucinator, HalRef and RefChecker. Only the abstract was seen. — [arXiv 2607.22693](https://arxiv.org/pdf/2607.22693)
- **GPTZero** has a hallucinated-citation checker. **[VENDOR CLAIM on results]** — [gptzero.me/sources](https://gptzero.me/sources)
- **Grammarly Citation Finder** supplies citations for claims, which is generation, not verification. — [SiliconANGLE](https://siliconangle.com/2025/08/18/grammarly-leans-writing-assistance-agents-students-professionals/)

### Inferences
- **Citation-existence checking is cheap and commoditising.** The defensible step is "does the claim match what the source says, and can the student explain it?" That is the source-grounded viva no one ships yet **[inference]**.

### Gaps
- GESIS paper findings were not read.
- No evidence was found on whether Elicit or Consensus are used in assessment workflows.
- No evidence was found of Scite being used inside grading workflows at HK universities.
