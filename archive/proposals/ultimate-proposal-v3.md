# Acader — Proposal v3: Understanding is the cheapest path
### Brief for the CLEAR meeting (Fri 2026-10-16) · Cyrus Ng, CUHK · 2026-10-14

> Replaces v2 for Friday. v2's Meter-and-credential framing did not survive fact-checking (see §9). This version is the backbone the founder actually means.

---

## §0 In one paragraph

Assessment has become an arms race: every new check is beaten by the next model. We stop raising the wall and **change the price**. Acader is a school-customised AI learning and writing platform. It starts from the instructor's topic and walks the student through the whole process: brainstorm, find sources, read, meet other people's ideas, build the argument. **The AI does the legwork; the student does the thinking.** Doing the work honestly inside the platform becomes cheaper than faking it, because faking it means faking a whole trail *and* then explaining it out loud. The same trail gives the teacher something they have never had: a weekly view of what the class actually misunderstood. **Assessment that teaches the teacher too.**

---

## §1 The premise

1. **Detection is a losing game.** Any modelable signal gets modelled. Australia's regulator calls detection "not viable"; Sydney's two-lane model accepts that unsupervised work can't be secured.
2. **So change the economics, not the wall.** Make understanding the student's cheapest route to a good grade:
   - Inside, everything is provided: sources, page lookup, citation checks, a course-aware AI.
   - Faking it requires a coherent trail *plus* a conversation about it. A ghostwriter can't sit the conversation.
3. **Even if the idea came from an outside AI, it has to pass through the student's head.** We don't need to know where an idea was born. We need evidence that the student can carry it: what you read, where you read it, and whether you can say it out loud.

---

## §2 What the platform is

The instructor sets the topic (plus rubric, readings, lecture recordings). The student works through stages:

| Stage | AI does (legwork) | AI asks (thinking stays with the student) |
|---|---|---|
| Topic → brainstorm | Clarifies the brief; surfaces terms from the course | "What's your first instinct, and why?" |
| Resource gathering | Finds sources, formats citations, checks they exist | "Why this source and not that one?" |
| Source reading | "Which page talks about X?" → p.47, p.112 | "What's the main claim of chapter 3, in one line?" |
| Other people's ideas | Shows where sources and classmates' public positions differ | "Lee and Wong disagree. Where do you stand?" |
| Blind spots | Notices what's missing against the rubric and readings | "You haven't addressed the counter-argument in Reading 2. Want to?" |
| Building the argument | Restructures *the student's own* words | "What's your argument in one sentence? Let's test it." |
| Fact errors | Holds the book, so it can check | "Look at p.47 again. Does it say that?" (said openly, never marked silently) |

### The boundary rule
**AI does retrieval and mechanics. Anything that would produce a claim, a synthesis or an argument structure turns into a question.** "Summarise this", "connect these for me" and "write my intro" all become questions, each with the relevant passages attached.

### The instructor's dial
How strict the boundary is per stage is the **instructor's** choice, using the AI Assessment Scale (Perkins, Furze, Roe & MacVaugh; five levels, from no AI to AI exploration). AIAS is a design tool with no enforcement; Acader enforces the level the instructor picks, e.g. brainstorm at level 3, drafting at level 2.

---

## §3 The trail, and what happens at a gap

- Work done inside leaves a coherent trail: sources opened, pages read, questions answered, drafts revised.
- Work from outside (another AI, a friend, a notebook, a walk) shows up as a gap. **A gap is an invitation, not an accusation.** Outside is allowed. We ask more about it, side by side:
  - What did you read? Where? Show me the page.
  - Why this, not that?
  - Say it out loud (a short conversation, with a human deciding anything that matters).
- Typing is never the proof. The conversation is. Accessible alternatives are always available.

---

## §4 Two mirrors: the gold

One process produces two views. **Students see their own understanding; teachers see their own teaching; nobody sees anyone else's.**

**The teacher mirror (weekly, zero setup):**

| Signal | Example |
|---|---|
| Misconceptions | "60% read chapter 3 as arguing X; it argues Y." |
| Tied to the lecture | "This starts at your lecture, 34:12, where Y was introduced." (uses the lecture miner) |
| Questions nobody asks in class | Top 10 things students asked the AI this week, anonymised. Hong Kong students stay quiet in lectures but ask the AI everything. |
| Reading use | "Nobody opened Reading 4. Everyone leans on pp. 40–55 of Reading 2." |
| Stuck points | "Most students stalled moving from sources to argument." |
| Rubric mirror | "70% fell short on the same criterion." That points to the brief or the teaching, not the students. |

**Why it matters:** teachers get almost no evidence about their own teaching beyond end-of-term satisfaction surveys, which measure popularity, arrive too late and are known to be biased. This is evidence of *learning*, while the course is still running.

**Rules that keep it gold:**
1. The teacher owns their mirror. The department sees it only if the teacher shares it (e.g. in a teaching award or promotion file).
2. No teacher rankings, ever.
3. A class pattern is shown only when at least ~5 students share it, so no student can be identified.
4. The student mirror follows the same polarity: the student owns their record and shares it by choice.

---

## §5 Why this isn't just another Socratic AI

ChatGPT Study Mode (Jul 2025), Gemini Guided Learning (Aug 2025), Claude's Learning Mode and Khanmigo's writing coach already "ask instead of tell". All are optional toggles, and none know the assignment. Turnitin Clarity and the DraftTrace research (arXiv 2609.36544) already record the writing process and AI chats for instructors.

What none of them combine:
1. **Knows the assignment:** the instructor's topic, rubric, readings and lectures.
2. **Knows the stage:** the right help in "source reading" is different from "drafting".
3. **Holds the sources:** "which page?" and "that's not what p.47 says" need the book.
4. **The course sets the rules,** not the student's toggle.
5. **The teacher mirror:** process data turned into teaching feedback, not integrity flags.

**Evidence the backbone matters:** Bastani et al., *PNAS* 2025 (about 1,000 high-school maths students). Plain GPT-4 raised practice scores 48% but **cut exam scores 17%** once removed. A guardrailed tutor raised practice scores 127%, and its exam scores matched the control group. AI that answers can harm learning; AI that guides avoids the harm. (One field study in maths; generalising to writing is our open question.)

---

## §6 What exists today (honest)

| Piece | State |
|---|---|
| Room demo (`demo/`) | Runs on DeepSeek: spaces, sources, Helper, Coach, coverage map, citation check, Proof. A communication asset, not evidence. |
| Lecture miner | Validated in a prior session (MIT 18.06 L1 → 159 board states, ~0.3 s accuracy on synthetic ground truth). Code is not in this repo (OL-002); bring it on the laptop. |
| Viva runner (`runner/`) | Built and tested offline; the real-LLM path is untested. |
| Teacher mirror | Not built. Mock it with demo data for Friday, labelled as a mock. |

---

## §7 The ask for CLEAR

**One course, one assignment, one semester slice.**
- The instructor gets the teacher mirror weekly.
- **Primary success measure:** did the teacher change something in their teaching because of it? (Interview the teacher.)
- **Validity check:** for a sample of students, compare what the platform's conversation shows with a 5-minute TA oral on the same work. Do they agree?
- **Question quality:** 50 platform questions vs 50 TA questions, rated blind.
- Ask CLEAR how ethics approval works if results go to the Teaching and Learning Innovation Expo.

Hooks: the Expo (2025's was Dec 1–2; the 2024 call closed Oct 28, so the 2026 call may close soon; check expo-cfp@cuhk.edu.hk). Introductions to Prof. Hargreaves (Law; 2023 paper on ChatGPT and law assessment, and large classes with no TAs) and Dr. Pang.

---

## §8 Risks, said out loud

1. **Students leave for ChatGPT.** Outside is free; the inside has to be better, and instructors must grade the stages, not just the final essay.
2. **The boundary annoys students.** "Just tell me" frustration is real. The legwork the AI does must feel generous.
3. **Question quality.** If the platform's questions are worse than a TA's, nobody trusts the conversation.
4. **The mirror becomes surveillance.** Of students *or* of teachers. The ownership rules in §4 are load-bearing.
5. **No claim of "no cheating", ever.** The claim is: the honest path is the cheapest one, and every gap gets a conversation.

**Words to avoid:** detect, catch, cheat, "we would know". **Say:** gap, conversation, evidence, mirror.

---

## §9 What changed from v2 (and why)

- **Dropped "the Meter plugs into ChatGPT Edu / Gemini via API".** ChatGPT Edu export is per member; the admin Compliance API is documented for Enterprise eDiscovery (and is surveillance-shaped); CUHK appears to run its own chatbots plus M365 Copilot, not ChatGPT Edu.
- **Dropped "the whole-package proxy hole stays closed".** A typed, unsupervised check can be answered live by pasting into another AI (GPT-4 answers 88% of questions about a learner's own code, Lehtinen 2024). The conversation is the gate.
- **Dropped "Layer 4 is empty".** Clarity already shows instructors students' AI chat activity; DraftTrace does the same in research. Our gap is the course-grounded process plus the teacher mirror.
- **Corrected citations:** the UNESCO quote is a guest article (Desai, May 2025), not UNESCO policy. Hargreaves' 26%/9% detector figures are OpenAI's own published numbers. Unfound sources ("beyond surveillance" blog, Legal Journal on Technology) are removed.

---

## Sources
- Bastani et al. 2025, PNAS 122(26), doi:10.1073/pnas.2422633122 · https://knowledge.wharton.upenn.edu/article/without-guardrails-generative-ai-can-harm-education
- ChatGPT Study Mode / Gemini Guided Learning: https://techcrunch.com/2025/08/06/google-takes-on-chatgpts-study-mode-with-new-guided-learning-tool-in-gemini/
- Turnitin Clarity: https://guides.turnitin.com/hc/en-us/articles/37195716344205-Introduction-to-the-Clarity-Assignment
- DraftTrace: https://arxiv.org/abs/2609.36544
- AIAS + two-lane: https://www.craigbellamy.net/2025/09/29/bridging-the-two-lane-approach-and-the-ai-assessment-scale-a-comprehensive-framework-for-higher-education/
- NYU voice-AI orals ($15 / 36 exams; validity not established): https://arxiv.org/html/2603.18221v1
- Self-report vs performance, r ≈ .055: https://arxiv.org/abs/2609.15624
- CUHK AI services: https://cuhk-edt.knowledgeowl.com/docs/ai-services-for-teaching-and-learning
- ChatGPT Edu export: https://help.openai.com/en/articles/20001279
- CLEAR Expo 2025 call: https://clear.cuhk.edu.hk/web/professional-development-pd/seminars-workshops-events/teaching-and-learning-innovation-expo-2025/
- Earlier research: `reports/AI era understanding assessment tools.md`
