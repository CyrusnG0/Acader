# Understanding Infrastructure — The Ultimate Proposal
### A complete vision & build brief (handoff document)
*Compiled 2026-10-11 · Distilled from a full product/market working session, incl. a validated technical prototype and live market research (all claims sourced at bottom).*

---

## 0. How to read this document

This is the single source of truth for the project, written so an AI agent (or a new teammate) can pick it up cold and continue building. It contains: the validated technical core, the philosophy, the product spec, the market evidence, the go-to-market, the risks, and the roadmap. Sections marked **[VALIDATED]** were prototyped and tested in-session. Everything else is design intent agreed during the session.

---

## 1. The vision (one paragraph)

We are building the **understanding infrastructure for schools in the AI era**: a platform where schools simply *throw their existing materials* (lecture recordings, notes, assignments, rubrics — the same way they post to Google Classroom / Blackboard today), and from that we automatically build a **teaching knowledge graph** mined from how their own instructors actually teach. Students do their real work — writing and coding — inside the platform's **Room**: a coach challenges their thinking, a helper lowers mechanical friction (finding, citing, verifying sources), and every finished work earns a **Proof of Understanding** — a portable, evidence-backed certificate that the student *actually understands what they submitted*. Schools get integrity by construction (no more fake-citation fear, no more essay-detective work), visible teaching quality (concept heatmaps, who is behind on what), and their own private teaching brain. We are not a barrier students want to bypass; we are the tunnel that makes doing the work properly the *easiest* path — and the proof is the student's to keep.

**North star:** become the school's *evidence layer* — "Report Card 2.0": for two centuries schools issued grades + guesswork; we make it grades + verified understanding + an evidence chain.

---

## 2. The validated core: lecture mining **[VALIDATED]**

The technical wedge that no competitor has: **automatically extracting structured "board states" from real lecture videos** — including the hard case of progressive chalkboard writing.

**Prototype results (this session):**
- Real video: MIT 18.06 Lecture 1 (Gilbert Strang, chalkboard, 40 min, archive.org `MIT18.06S05_MP4/01.mp4`, 480×360).
- Pipeline: ffmpeg 1 fps sampling → 32×32 grayscale grid + EMA (α=0.08) → auto-tuned drift thresholds from the video's own stats → segment close on confirmed drift OR sustained low-ink (wipe) → **representative = argmax ink** (the *fullest board before it is erased*) → dedupe-keep-fullest merge.
- Result: **159 board states** with timestamps, zero ML cost (~1 min of CPU), pure OpenCV/numpy.
- Ground truth: a synthetic chalkboard video with known answers — snapshots landed within ~0.3 s of truth; re-shown boards merged into their fullest version.
- Hard-won calibration lessons (do not rediscover these): dHash is **blind to thin chalk** (≤6/64 bits between different boards); professor walk-throughs are transients only EMA absorbs; naive auto-thresholds break under constant motion (EMA-drift, not raw drift); title cards game ink metrics (cap board-like ink at 0.45).

**Files (delivered):** `lecture_miner.py` (working extractor), `make_sheet.py` (contact sheets), `gen_synth.py` (ground-truth generator), `strang_out/states.csv` (159 states), demo sheets.

**Why it matters strategically:** ingest = mining. Every lecture a school posts becomes structured knowledge automatically. This turns "please adopt our platform" into "keep posting your materials like you already do — we do the rest."

---

## 3. Design philosophy (the non-negotiables)

1. **Help you think — never think for you.** The product sells *thinking*, never time-saving as the headline. (Chegg is the cautionary tale: anything an LLM+document can replicate gets commoditized; ~99% market value lost.)
2. **Scaffolding, not shortcuts.** The coach's every question is grounded in the course knowledge graph ("you learned eigenvectors in Lecture 7 — answer me: why center the data first?"), never a system-prompt ChatGPT.
3. **Make the right thing the easiest path.** Students don't cheat because they're evil; they cheat because doing it right is *hard* (five tabs to find sources, APA formatting, reading every citation). We crush the mechanical cost (find/cite/verify) and preserve the thinking cost (argue, defend, answer). Integrity becomes a *byproduct of the easy path*.
4. **Outside is free; the Room is where proof is earned.** Research phase = completely unsupervised (NotebookLM, Elicit, whatever — we do NOT compete there and never will). The Door = import *anything*, source-neutral, no judgment (this is deliberate: it makes "how you researched outside" irrelevant). The Room = helper + coach. The End = the work + the Proof. Like a library: nobody watches you study, but you must stand at the viva yourself.
5. **AI touches structure, never content (unsupervised phase).** Re-cluster, rename, order, surface gaps and conflicts, suggest connections, turn notes into self-test questions — **always using the student's own words**. The AI never writes its own sentences there.
6. **Amplify professors, never replace them.** Concept explanations point first to how *their own* instructors taught it (mined graph), then to general explanations. Professors are the heroes; we are the multiplier.
7. **Students own their data.** Keystroke timelines, coach dialogues = student property. School sees derived signals only. The vault (student's) vs the school's tenant: never conflated.
8. **Clear end.** Every AI study tool today is an infinite scroll; our product *ends*: manuscript + citation-confidence report + Proof (writing), or working code + defense record + Proof (code). "You have arrived" is itself the product.
9. **Proof is earned, not bought by typing.** Typing by hand is not treated as proof of authorship — it is only the *entry condition* for process evidence. The viva-style challenge is the real gate. (Preserves accessibility; survives the "wrote it outside, retyped it inside" attack.)
10. **Never a cheat report.** Output is comprehension: *Strong / Partial / Oral-verified*. Low process confidence → *recommend* (never auto-decide) an oral check; humans decide consequences. This is also the safest posture under the EU AI Act (education = high-risk category; human-in-the-loop, formative framing).

---

## 4. The product

### 4.1 The workspace (the "Arc browser for a course")
- **Spaces** = one course / one project each (a FYP is a room; a CS assignment is a room).
- **Sources are first-class citizens:** papers, lecture recordings, handouts, rubrics, repos — draggable, connectable, all in one place. (Not competing with Heptabase: it's a beautiful container that "doesn't participate in your thinking" — ours *participates*: the coach lives in the canvas, wired to the course graph.)
- **Command bar:** ask anything in context — "is this source relevant to my claim?" / "why did they use this function?"
- **The clear end:** explicit completion state with artifacts.

### 4.2 Helper vs Coach (two voices, both required)
| | **Helper** | **Coach** |
|---|---|---|
| Direction | answers the student's questions | asks the student questions |
| Posture | unconditional, friction-killing | opinionated, proof-making |
| Examples | debug error messages, fix citation formats, find sources (via Scite/Semantic Scholar integrations), explain a concept (course-graph first), smooth a sentence | "why this argument direction?", "does this citation actually support this sentence?", "why is this line here?" |
| Triggered by | the student | the system (and the rubric) |

One-liner: **Helper helps you fight the work; Coach makes you face yourself.** Coach frequency is student-tunable; the End (for graded work) is not.

### 4.3 Code track (the first wedge)
- **Variant engine:** teacher supplies ONE reference solution (they already have it) → platform auto-generates N **isomorphic variants** (different scenario/parameters/constraints, same core concept) → teacher one-click reviews (nothing ships unreviewed) → each student gets a different variant. Testing transfer: if you can only solve the original, you memorized it.
- Kills three cheating vectors at once: web solution-banks (no original to find), classmate copying (different variants), one-shot AI solving (research shows LLMs strain on multi-function/class cohesion — design for it deliberately).
- **Line-level viva (no paste):** typing one-by-one only, at key lines the system **stops the student**: "why this approach here? what does this function do? what breaks without it?" Questions come from the course graph — it feels like *their* teacher asking, not a quiz bank.
- **End:** runnable code + defense record + Proof.

### 4.4 Writing / research track (science FYP, English major, final-year projects)
- **Claim cards:** import anything from Outside; each source becomes a card tied to a claim.
- **Coverage map:** "argument A has 4 sources, argument B has 1", "your methods section has no notes" — spoken as questions, never answers.
- **Conflict surfacing:** source X vs source Y disagree → flagged as "worth writing about" (a thinking prompt).
- **Course-graph connections:** this note ↔ that lecture ↔ that paper (our exclusive layer — notes tools have no course).
- **Co-built outline:** coach challenges direction (built-in argumentation patterns + teacher-customized angles on the rubric).
- **In-place citation with live verification:** while writing, each citation is verified in real time (existence via DOI/Crossref → full-text pull → does it actually support the claim?). Green light per sentence. **Teachers never fear fake citations again** — that fear is auto-resolved by construction (the fake-citation problem is exploding: a Lancet-covered study found a six-fold rise).
- **Burst-typing escalation:** large unedited input in a short window → challenge intensity escalates (where did this direction come from? why this structure? defend this citation) → Proof is issued as **"orally verified"** tier, honestly labeled.
- **Submission is channel-gated but friction-free:** LMS-deep-integrated (Canvas / Google Classroom / Blackboard) so "submitting here" is the *path of least resistance*, not a new rule.

### 4.5 The Proof of Understanding (the crown jewel)
A verifiable, evidence-backed document — not a score:
- the artifact (paper/code),
- process evidence (writing timeline, revision history, challenge-response record) — summarized to signals; raw stays with the student,
- comprehension dimensions ("can explain every line", "can restate course concepts in own words", "citations real & supportive"),
- optional oral spot-check (5 min) when process confidence is low.

**Tiers:** Standard (rich process) / Oral-verified (challenged) / none (returned with reasons — e.g., failed citation checks).
**Student ownership:** portable vault item — verified-portfolio badge for university admissions (secondary) or the job market (university). In a grade-inflation + AI-saturation world, *verified understanding* beats a transcript. **This flips monitoring into an asset the student wants** — the answer to "how do students accept this without feeling forced."

### 4.6 School dashboard (what the principal sees)
- **Concept heatmap per class:** who is stuck on which concept (secondary: homework mapped to the lecture graph — "§3.2 taught Tuesday, homework 3.2 due Friday" → *who is behind AND where*; university: class-wide misconception patterns → next lecture targeting).
- TA relief: incoming papers arrive with citations pre-verified.
- **School Teaching Brain:** every mined lecture accumulates into the school's private graph — new/substitute teachers teach from the same graph; students revise with their own school's voice. Switching cost = re-teaching everything (retention moat).
- Whole-school layer: understanding reports for parents, boards, accreditors.

### 4.7 Data isolation (the sales-meeting table)
| Data | Owner | School sees | Enters global graph |
|---|---|---|---|
| Course materials (recordings/assignments/rubrics) | School | only own school | **never** |
| Student process data | **Student** | derived signals only | anonymized stats, opt-out |
| Proof of Understanding | both | yes | no |
| Concept graph + openly-licensed content | Platform | all | yes |

Three layers: **L1** tenant course graph (encrypted, per-school) · **L2** global concept graph (concepts + prerequisite edges + openly-licensed canonical explanations, e.g. MIT OCW under CC BY-NC-SA) · **L3** student mastery model (student-owned). Five cross-checks run across them: course alignment (L1), citation authenticity (L2), concept-consistency (L2×L3 — claims about unmastered prerequisites trigger the coach *before* the teacher ever sees a problem), code challenge grounding (L1×L2), process-consistency (L3 → viva recommendation).

---

## 5. Users

| | **Secondary school** | **University** |
|---|---|---|
| Pain | assignment trust crisis, exam pressure (HKDSE/A-level), parent communication | ghostwritten essays, fake citations, TA overload, FYP supervision bottleneck (6–8 projects per supervisor — sometimes *unpaid* workload), employers distrust transcripts |
| Tone | gamified coach + teacher dashboard + parent-visible progress evidence | citation-verified submissions + viva records + department analytics |
| Integration | Google Classroom | Canvas / Blackboard, library APIs |
| Proof use | admissions portfolio | employment skill verification |
| Privacy | guardian-visible layer (explicitly marked) | adult autonomy, student-owned |

**Beachhead = Final Year Projects:** capacity bottleneck is acute (one supervisor, 6–8 students, ~30-min meetings), one-semester cycle (the Room becomes home), ends in a viva natively (Clear End already exists), and departments already treat it as capability evidence. For students: the FYP is the only large graded work where *nobody watches the process* — the feedback-gap extreme. Decision-maker = department head, not central procurement (6–18-month sales cycles avoided).

**Each school is different** → a small config surface: rubric upload, policy toggles (challenge frequency, viva thresholds, language, course mapping). Configuration itself becomes switching cost — but never let it become an implementation burden on day one.

---

## 6. Market evidence (researched 2026-10, sources in §13)

- **Market:** AI-in-education ≈ USD 6.9–18.9B (2025, estimates vary widely) → ~$41–57B by 2030–33; CAGR ~20–43% depending on scope. Fastest segments: generative AI (48.3%), corporate training (44.8%), APAC (44.2%). Higher-ed AI specifically: $4.1B (2026) → $13.5B (2030). Top driver named by analysts: demand for personalized learning ecosystems.
- **Student behavior (demand is already there):** 57% of US college students use AI weekly for coursework (Gallup, 2026-04); 85% used genAI for coursework in the past year (Inside Higher Ed, 2025-08); UK: 53% → 88% YoY for assessments (HEPI, 2025-02). "Upload lecture → notes/flashcards" is a *proven paid behavior*: Turbo AI (ex-Turbolearn) reached ~$13M revenue, ~10M students, on only $750K raised.
- **Efficacy (the science backs the coach):** Harvard RCT (N=194, *Scientific Reports* 2025): a carefully designed AI tutor produced **>2× the learning gains** of in-class active learning, in *less* time (median 49 min vs 60), with higher engagement (p<10⁻⁸). Effective designs = targeted prompt engineering + pedagogy (active learning, cognitive-load management, growth mindset) — exactly what our graph-grounded coach architecture embodies. Same paper warns: unguided AI lets students skip thinking — our design law #1 is the answer.
- **Funding climate (name matters):** edtech VC H1-2026 ≈ $1B, **down 26% YoY** (HolonIQ); 2025 total ~$2.8B, still low (Crunchbase). Meanwhile overall AI VC **up 109%** to 2021-record levels (OECD), AI ≈ 60% of all North American funding. **Position as "AI-native learning engine with outcome evidence," never as "edtech."**
- **Teacher-side pain (our second buyer):** viva/oral exams are being revived *because* AI broke written assessment (The Conversation 2026-08; Guardian on Univ. of South Australia) — but human vivas don't scale; AI-conducted oral exams already ran at **$0.42 per student** (arXiv 2026) — our daily-flow coach is the scalable micro-viva. Fake citations up **6×** (STAT/Lancet study, 2026-05); professors issue automatic zeros (r/Professors). 71% of K-12 teachers have had no formal AI training while 83% already use genAI (NEA) — the school-side enablement gap is real.

### Competition map (the honest scan)
| Pillar | Players | Verdict |
|---|---|---|
| Writing process evidence | **Turnitin Clarity** (TIME Best Inventions 2025; as of 2026-10 campus **pilots** at UCLA, UQ, CU Boulder, Sonoma State, Fresno State and others, not broad rollouts), GPTZero Authorship, Kritik VisibleAI, Process Feedback (free, learning-first), Draftback (teacher DIY) | crowded; **do not enter here first** |
| Writing coach | Khanmigo Writing Coach (free w/ Microsoft, K-12) | proven, no proof/integrity layer |
| **Code process evidence + viva** | Codio (paste flags, only inside its own IDE; no AI-code detection found), PasteTrace (open-source research tool), Watcher (2022); AI oral exams now reach code work (SIGCSE 2026 talk) | **Thin for the daily-flow, course-grounded version; not empty** (revised 2026-10-12, D-017) |
| AI oral exams at scale | **NYU Stern Viva** (public, ~$0.42/student compute), OralExam.AI (Tulane-linked startup), ExamSim (Bayreuth), EXAMAI (Eindhoven), Georgia Tech Socratic Mind (pilot). "Prova" and "Professr" could not be verified in 2026-10 research | crowded and cheap to build; **the viva itself is a commodity**. Mostly exam-moment products, not connected to daily work/course content |
| **Student-owned proof + lecture-mined course graphs** | nobody | **EMPTY — our moat** |
| Note tools (Outside) | Gemini Notebook (ex-NotebookLM; renamed 2026-07; free), Turbo AI, Knowt, Heptabase | **do not compete** — we import from them |

**Closest threat & differentiation:** Turnitin Clarity = teacher-vs-student surveillance framing, product-blind to *what the course taught*, no code, no student-side value. Ours = student-asset framing + course-grounded coach + code. Teacher communities already hand-made our core loop ("show them the keystroke replay, make them explain it" is the top teacher recommendation for Draftback) — demand is hand-validated by teachers, not yet by buyers. **The viva is a commodity (a professor ran 36 AI orals for $15). The open slot is the daily-flow trust layer: course-grounded questions, a record an instructor can defend in an integrity hearing, and a proof the student owns.** (Corrected 2026-10-12, D-017; earlier text claimed code viva was unsold.)

### The wrapper test (vertical, not a thin LLM wrapper)
- LLM off → what remains? Mined course graphs, mastery models, keystroke/process records, citation-verification pipeline (DOI/Crossref/full-text — engineering, not prompting), board-state visual assets. ✔
- Copy time? Prompt = one night; graphs+mastery+mining = months of accrued data. ✔
- Killed by model upgrades? No — we *consume* model improvements; our lock is student/school *state*. ✔
- Data flywheel? Every answer, essay, uploaded course improves the instance. ✔
Vertical = **discipline (CS first) × workflow (write→stop→ask→answer) × assets (course KG + mastery + proofs)**. Generality risk comes from scope creep, not from feature count.

---

## 7. Go-to-market (B2B2C)

- **Buyer:** the principal / provost / department head. Student access rides on the school license; students are never charged individually.
- **Mandatory adoption is fine — but renewal is earned by student benefit.** Forced-but-a-gift: vault, coach, portable proof. **In-cohort student NPS is the renewal predictor and goes into the north-star metrics.**
- **The pitch that sells:** schools buy the antidote to three fears — fear of AI (integrity by construction), fear of parents (visible understanding evidence), fear of superiors (accreditation-ready reports). Frame: **Report Card 2.0** / *understanding infrastructure* (infrastructure survives budget reviews; tools don't).
- **Wedges in order:** (1) CS departments — variant engine + line-level viva (empty market, fastest value, mining shines on algorithm courses); (2) FYP modules per department (fast cycle, department-level decision); (3) secondary schools via hero-teachers first, school-wide licenses later.
- **Adoption motion:** "keep posting to us what you post to Classroom/Blackboard — the platform does the rest." Zero-behavior-change ingest; mined graph is the instant wow.
- **Pricing (hypotheses to test, none validated; all `[estimated]`, revised 2026-10-12, D-018):** H1 per-course instructor license, ~$500-1,500/course/yr (anchor: ~30 TA hours of manual orals for 36 students, ~$21/student, NYU paper). H2 per-student add-on, ~$3-8/student/yr (anchor: Turnitin Feedback Studio ~$6.70/FTE, reported, unverified). H3 free pilot, then department license. Floor reality: DIY AI oral compute is ~$0.42/student/exam, so price on trust, defensibility and student-owned proof, never on compute. Nothing is committed until interviews give willingness-to-pay data (OL-013).
- **What we promise (wording discipline):** promise *evidence on every submission* and *visibility into who is behind and where*; **never** promise "no cheating" or "no student left behind" — one false-positive scandal burns the trust; capability-visibility language survives contracts and the EU AI Act.

### Flywheels
- Cross-school: more schools → more lectures mined → sharper global concept graph → better cross-checks/proofs → more schools.
- In-school: longer use → thicker teaching brain → more "theirs" → switching = re-teaching → renewal >90% target.

---

## 8. Risks & honest limits (say these out loud internally)
1. **Deliberately shrinking the market:** banning paste scares off would-be Chegg users — intentional; growth story must run on outcome evidence (the Harvard-RCT playbook), not user counts.
2. **Surveillance feel:** keystroke records must ship as *learning journal / understanding proof*, never "cheat detector" (also: keeps us away from AI-Act high-risk *proctoring* framing; viva features remain human-decision, formative).
3. **Accessibility:** forced retyping can never be the *only* path — reasonable adjustments required (instructor-approved alternatives; the design already treats typing as entry-condition, not proof).
4. **Privacy = procurement question #1:** tenant isolation and no-training promises must be **engineering-auditable**, not a slide.
5. **The "easier" knife-edge:** citation-finding can get easier; *argument-formation* must never be automated (co-build = student types, coach challenges). Cross this line and we become the shortcut we exist to prevent.
6. **Canvas gravity:** the workspace serves graded work only — two project types, not a general notes app. Lose the scope, lose the vertical.
7. **School sales cycles 6–18 months:** hence department-level wedges above.
8. **Miner limits today:** state lists are fine-grained "ladders" (right for a teaching KB; production needs a semantic-clustering pass); sub-8s board re-appearances can slip; title cards need VLM QA (hybrid: pixels to scan, VLM to judge — keeps cost ~zero).
9. **Commoditization:** everything surface-level gets eaten by Gemini Notebook; the defensible layers are exactly the ones it refuses to build: course graphs, process evidence, proofs, school brains.

---

## 9. Technical build plan (module states)
| # | Module | Status |
|---|---|---|
| M1 | Ingest (upload / server-side video download) | trivial (gsk aidrive-style downloader exists) |
| M2 | **Visual miner** (board/slide states) | **[VALIDATED]** prototype done |
| M3 | Transcript (Whisper, sentence timestamps) | standard |
| M4 | Alignment (state ↔ speech overlap) | standard |
| M5 | Topic structuring (LLM groups states+transcript into teaching units) | one cheap LLM pass |
| M6 | QA watcher (random-timestamp VLM spot-checks on candidates only) | hybrid cheap |
| M7 | **Course KG + 3-layer isolation + mastery model** | design done (§4.7), build next |
| M8 | **Code track**: variant engine + line-level viva + no-paste editor | **next build** (wedge MVP) |
| M9 | **Writing track**: claim cards, in-place citation verification (DOI/Crossref → full-text → support judgment), burst-escalation | second build |
| M10 | Proof issuance + school dashboard + parent layer | third |
| M11 | LMS integrations (Canvas / Classroom / Blackboard) | with first pilots |

**Prototype repo files (this session):** `lecture_miner.py`, `make_sheet.py`, `gen_synth.py`, `strang_out/` (159 states), demo contact sheets, `states.csv`. Run: `python3 lecture_miner.py VIDEO.mp4 --outdir out [--fps 1] [--max-seconds 600]`.

---

## 10. Roadmap
- **Phase 0 (done):** lecture-mining prototype validated on real + synthetic video.
- **Phase 1 (next):** CS viva-coach MVP — upload course videos → KG; no-paste editor; reference-solution → reviewed variants; line-level challenges; defense record; per-student understanding summary. *Acceptance: one real course assignment completed end-to-end by non-founders.*
- **Phase 2:** writing/research room — claim cards, in-place citation verification, burst-escalation, Proof tiers. Pilot: one FYP cohort (one supervisor, 6–8 students, one semester).
- **Phase 3:** school dashboard (concept heatmaps), parent layer (secondary), LMS integrations.
- **Phase 4:** school teaching brain (substitute-teacher mode), cross-school global graph, Report-Card-2.0 accreditation reports.
- **Parallel:** outcome measurement from day one (pre/post concept tests, viva pass rates) — the Harvard-RCT marketing playbook.

---

## 11. Brand voice (locked)
- Hero: **"Learn from how the world teaches."** Sub: *Built to make you think — not to think for you.*
- Standbys: *Scaffolding, not shortcuts.* · *Great professors, multiplied — not replaced.* · *Don't just learn from your university. Learn from the world's.* · *Master the course, not just the notes.* · *LMS counts who submitted; we see who understands.* · zh-TW: 幫你思考，不替你思考。/ 不是捷徑，是鷹架。/ 教授被放大，不是被取代。
- Voice rules: selling point is always *thinking*, never time-saving; professors are heroes; structure words (connection / prerequisite / whole subject) everywhere; never surveillance vocabulary.

---

## 12. Open questions (next session)
1. Naming + domain for the platform.
2. Variant-engine quality bar: generate 3 variants from one real reference solution and grade difficulty parity (proposed next step).
3. Which citation backend to integrate first (Scite Smart Citations vs Crossref/Semantic Scholar direct).
4. First design-partner school: FYP department (universities) vs hero-teacher (secondary) — who signs first?
5. Pricing calibration (per-student/year band by segment).
6. EU AI Act classification review before first EU pilot.

---

## 13. Key sources (all claims above trace here)
- Harvard AI-tutor RCT: https://www.nature.com/articles/s41598-025-97652-6 (and https://news.harvard.edu/gazette/story/2024/09/professor-tailored-ai-tutor-to-physics-course-engagement-doubled/)
- Market size: https://www.mordorintelligence.com/industry-reports/ai-in-education-market · https://www.grandviewresearch.com/industry-analysis/artificial-intelligence-ai-education-market-report · https://www.thebusinessresearchcompany.com/report/artificial-intelligence-ai-in-higher-education-global-market-report
- Student adoption: https://news.gallup.com/poll/704090/routine-college-students-despite-campus-limits.aspx · https://www.insidehighered.com/news/students/academics/2025/08/29/survey-college-students-views-ai · https://www.hepi.ac.uk/reports/student-generative-ai-survey-2025/
- Funding: https://www.holoniq.com/notes/1b-in-edtech-venture-capital-to-date-funding-falls-short-of-last-years-midpoint-asia-mena-buck-the-trend · https://news.crunchbase.com/venture/edtech-funding-stays-low/ · https://www.oecd.org/en/publications/venture-capital-investments-in-artificial-intelligence-through-2025_a13752f5-en/full-report.html
- Chegg cautionary tale: https://fortune.com/2023/05/02/chegg-shares-tumble-students-fleeing-chatgpt-a-i/
- Turbo AI: https://techcrunch.com/2025/10/23/20-year-old-dropouts-built-ai-notetaker-turbo-ai-to-5-million-users/ · https://www.inc.com/diana-bocco/student-founders-entrepreneurs-ai-startup-venture-capital-funding/91380311
- Gemini Notebook (ex-NotebookLM): https://notebooklm.google/plans
- Competitors: https://www.turnitin.com/products/feedback-studio/clarity · https://www.khanmigo.ai/writingcoach · https://aithority.com/machine-learning/ai-detection-platform-gptzero-releases-authorship-tools-to-preserve-original-writing/ · https://www.kritik.io/visibleai · https://processfeedback.org/ · https://www.codio.com/features/code-plagiarism-detection-cheating-prevention · https://arxiv.org/html/2506.17355 (PasteTrace) · https://prova.education/ai-oral-exam-software · https://lifetimelearning.gatech.edu/node/25 (Socratic Mind) · https://trampgeek.github.io/moodle-qtype_coderunner/ (CodeRunner variants)
- Oral-exam revival: https://theconversation.com/oral-exams-are-making-a-comeback-to-stop-ai-cheating-but-they-have-their-own-problems-289707 · https://www.theguardian.com/australia-news/2024/nov/25/back-to-the-futurum-how-one-university-is-countering-ai-with-ancient-examination-techniques
- Fake citations: https://www.statnews.com/2026/05/07/lancet-study-finds-steep-rise-fraudulent-citations-academic-papers/ · https://www.reddit.com/r/Professors/comments/1j4hk3j/ai_hallucinating_my_example_reference/
- FYP supervision load: https://strathprints.strath.ac.uk/83757/1/Liaskos_CEP_2023_An_alternative_supervision_model_for_postgraduate_projects.pdf · https://www.mcgill.ca/dise/files/dise/masters_project_supervision_guidelines.pdf
- Feedback gap: https://learning-analytics.info/index.php/JLA/article/view/7184 · https://www.tandfonline.com/doi/full/10.1080/02602938.2025.2449891
- Writing-by-hand / generation effect: https://pmc.ncbi.nlm.nih.gov/articles/PMC11943480/
- LLM assignment-security research: https://arxiv.org/html/2410.09318v2
- MIT OCW license (seed corpus): https://ocw.mit.edu/terms/
- Heptabase positioning critique: https://www.slashspace.ai/compare/heptabase-alternative · Scite Smart Citations: https://scite.ai/
- Replit education exit: https://www.datawars.io/articles/replit-teams-for-education-deprecation-all-you-need-to-know

---

## 14. The one-page summary (if you read nothing else)
**What:** the understanding infrastructure for schools — throw your materials in; we mine every lecture into a teaching graph; students write and code in a coach-guarded Room; every submission earns a portable Proof of Understanding.
**Why now:** AI broke written assessment (viva revival, fake-citation surge); schools' #1 fear is unprovable integrity; students already live in AI tools; Harvard proved designed AI tutors double learning gains.
**Why us and not them:** Turnitin watches, NotebookLM answers, Khanmigo teaches writing — orals are a commodity, and nobody yet combines course-mined graphs, a defensible daily record and a proof the student owns. Parts are sold; the machine is not. (Unproven: see D-012 blind test.)
**How:** CS departments first (variants + line-level viva), FYP cohorts second, whole schools third. Sell to the buyer with the three fears; win renewals with student love.
**Moat:** mining pipeline (validated) + course graphs + process data + proofs + each school's teaching brain. Every model upgrade makes us stronger; every semester makes us switchable-proof.
**Slogan:** *Learn from how the world teaches — built to make you think, not to think for you.*
