# The Missing Layer — Ultimate Proposal v2
### An assessment insertion-layer for school-controlled AI · for discussion with CLEAR (Fri)

**Prepared by Cyrus Ng, final-year CS, CUHK · 2026-10-14 · working brief for my other AI (Claude) — not a product, not a pitch.**

---

## §0 One-page summary

Schools will all run school-controlled AI by 2026–27 (ChatGPT Edu, Gemini for Education). The AI itself is becoming a commodity. Four things are already sold: school AI platforms, academic tool suites, usage tracking, and oral exams. **One thing is missing everywhere**: a layer that measures how WELL students used AI — from what they actually did, anchored to outcomes, not from how they feel (questionnaires) or whether they used it (detectors).

The literature names this gap. UNESCO (2025): assessments should "evaluate students' ability to use AI tools effectively and ethically" — no instrument exists. Jones 2026 (scoping review): everything current measures how students FEEL about AI, not what they can do. The behavioral research that exists (keystroke provenance, DraftTrace) is detection-framed — it hunts overreliance.

**We build the missing layer, and we point it at learning, not at students:**

1. **The Meter** — process telemetry inside the school's AI. It never asks "did you use AI?" (a cop); it records what AI contributed and what the student added (an invoice). Student-owned first. Never an accusation.
2. **The Room** — a typed, untimed, one-sitting understanding check. Questions are computed from in-platform state (the lecture's mined board states + the student's own session log). Passing it mints a **Proof of Understanding** receipt — student-held, verifiable by reading, aligned to Open Badges 3.0 / W3C Verifiable Credentials in production.
3. **The Graph** — lecture recordings mined into per-course teaching memory (validated prototype: MIT 18.06 Lecture 1 → 159 board states). The Room's questions anchor to the professor's own board. The loop closes: Meter + Room data → class-level confusion map (derived from real process, not self-report) → the next lecture adjusts.

**The three pitch lines:**
> *"Everyone measures how students feel about AI, or whether they used it. Nobody measures how well — from what they actually did."*
> *"Clarity points the meter at the student. We point it at the learning."*
> *"We don't detect outside AI. Inside the room, outside work doesn't get caught — it just doesn't count, because it leaves no trail."*

**The core mechanism (first in every telling):** even if the work was AI-produced, inside the platform the student must understand what they submit at least once — the Room is where understanding happens, and the receipt is its byproduct. Fabricating the trail is the learning: the only way to fake a coherent in-platform process is to actually do the understanding.

---

## §1 Context: how this idea earned its current shape

This is v3.5 of a design that kept breaking under its own attacks. Each version died honestly:

- **v1 — Detection + honesty pledges.** Died: detectors fail (Hargreaves 2023 executed them: OpenAI detector 26% recall / 9% false positives; "probability suggestion… will not solve the fundamental conundrum"). Any modelable signal becomes an arms race.
- **v2 — Process verification.** A coach asks questions while you type, so understanding must happen at least once. Worked until the attack: paste the whole package (notes + question + transcript) into one long-context LLM and it answers the coach with the same memory. Fix: the synchrony layer — questions computed from in-platform state, staggered/late questions, mutation challenges. Concede the perimeter, hold the center.
- **v3 — Unlimited AI, school-controlled, metered.** The user's move: stop gating AI entirely. School-controlled room, unlimited usage, process in view. Not enforcement — *metering*. Then the market scan (§5) revealed the deeper truth: the platform layer is Google/OpenAI's commodity, and the tracking layer is Turnitin's (with a surveillance backlash). What survives is the **insertion layer**: meter → understanding → credential.
- **v3.5 — The missing layer (this document).** Don't build the AI. Don't build the tracker. Build the thing both kinds of vendor structurally cannot: an outcome-anchored, course-grounded, student-owned assessment layer that plugs into whatever the school already bought.

---

## §2 The market map (verified 2026-10-14, 16 queries over 4 rounds)

### Layer 1 — School-controlled AI (commodity, crowded, expanding)
| Who | Evidence |
|---|---|
| OpenAI ChatGPT Edu (May 2024) | https://openai.com/index/introducing-chatgpt-edu/ ; U of Utah deployed Nov 2025 (https://attheu.utah.edu/facultystaff/u-launches-chatgpt-edu-a-university-centered-generative-ai-tool-for-campus-use/) |
| Google Gemini for Education | https://blog.google/products-and-platforms/products/education/higher-education-gemini-notebooklm/ ; U of Houston Apr 2026 (private infrastructure) |
| Gemini for Students (free, unlimited class-material uploads) | https://gemini.google/students/ |

### Layer 2 — Academic tool suites inside school AI (commodity)
Research, news, summarize, brainstorm, connect-dots: NotebookLM, Gemini in Workspace, ChatGPT Edu connectors. **Design law: never compete here.**

### Layer 3 — Usage tracking (crowded, and pointed the wrong way)
| Product | What it does | The tell |
|---|---|---|
| Turnitin Clarity (Jul 2025) | School-controlled writing environment, process visible to both sides; UCLA/Fresno State adopted; ISTE SEAL | Students call it "digital surveillance" (Reddit); "surveillance of academic cognition" (Legal Journal on Technology, Sep 2026); Turnitin itself now blogs "beyond surveillance" |
| GPTZero Writing Replay | Reconstructs edit history — "every keystroke, pause, and paste — then scores how natural the typing looks" | Detection in replay clothing |
| Grammarly Authorship (Aug 2024) | Records typed/pasted/AI-assisted; "you'll always have receipts"; deliberately no detection (Jisc review) | Closest to our meter — but stops at provenance, no outcome anchor, no course grounding; took the word "receipts" |
| SchoolAI Mission Control | Real-time K-12 conversation monitoring | Surveillance用途, governance tool |
| Draftback / Revision History | Google Docs replay | Interop toys |

### Layer 4 — "How WELL did they use AI?" (THE GAP — empty, and named)
- UNESCO (May 2025): "Assessments should therefore evaluate students' ability to use AI tools effectively and ethically" — https://www.unesco.org/en/articles/whats-worth-measuring-future-assessment-ai-age
- Jones 2026 scoping review (IJAIPIL): current measures = self-report confidence, not capability — https://journals.calstate.edu/ijaipil/article/view/6920
- All validated scales are questionnaires: SAID (2025, α≈0.87), multidimensional dependency scales (2026). None observe behavior.
- Behavioral research exists but is detection-framed: Davalos & Zhang 2026, "Does AI Assistance Leave a Temporal Fingerprint?" (CoAuthor corpus, character provenance → overreliance detection) — https://arxiv.org/abs/2609.17883 ; DraftTrace 2026 (multi-view analytics environment) — https://arxiv.org/abs/2609.36544 ; TWFF event-log format — https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7272718 ; "The Invisible Author: the Auditability Gap" — https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7024098

### Adjacent crowded quadrants (avoid)
- **Oral/viva**: mainstream advice now (Inside Higher Ed, Jun 2026: "Rather than attempt to police AI usage, pair the take-home essay with oral assessments"); Voice-AI vivas at $15/36 exams ≈ $0.42 each (arXiv 2603.18221). Multiple startups.
- **Lecture video analytics (teacher-facing)**: Tcherly (JLA 2022) — class-level confusion dashboard but **self-reported**; TeachActive (2021). Deriving confusion from real AI-use process data + lecture mining: **nobody**.
- **Lecture mining into teaching graphs**: nobody (our validated prototype is the seed).

### Standards that make the receipt land (production, not v1)
- **Open Badges 3.0** (1EdTech) built on **W3C Verifiable Credentials 2.0** — de facto signed-credential standard 2026; CLR Standard 2.0 for learner records. https://www.1edtech.org/standards/open-badges
- **LTI 1.3 / LTI Advantage** — the LMS insertion standard (Canvas/Moodle/Blackboard/D2L). https://www.1edtech.org/standards/lti
- Implication: the Proof of Understanding has a standard to be issued in, and the layer has a standard to be plugged in with. This is what makes "insertion layer" real instead of rhetorical.

---

## §3 The gap, stated precisely

Three gaps, all named by others, all unfilled by anyone:

1. **Outcome-anchored metering.** Provenance reports (Authorship) and detection scores (GPTZero) stop at process. Self-report scales stop at feelings. Nobody closes the loop process → understanding → evidence. Without the outcome anchor, any usage metric collapses to Goodhart (performative prompting).
2. **Course-grounded verification.** Every competitor is course-blind. Our Room anchors questions to the professor's own mined board states — the lecture itself is the verification surface, and the moat ChatGPT structurally cannot have.
3. **Student-owned polarity.** The whole Layer-3 market faces educators (integrity frames) and is paying for it in backlash and dropped contracts. Student-held receipts, never-an-accusation, "record — not a grade": nobody else has this polarity, and it is the reason the Clarity path fails.

Positioning lines against the two nearest neighbors:
> **vs Turnitin Clarity:** "Clarity points the meter at the student. We point it at the learning."
> **vs Grammarly Authorship:** "Authorship proves who wrote it. This proves you understood it. Provenance is not understanding."

---

## §4 Hard constraints (design laws — quote verbatim, keep first in every telling)

1. **Help you think, never think for you.**
2. **Make the right thing the easiest path.** (No gating; the inside must be genuinely better.)
3. **AI touches structure, never content.** (Structure edits, organization, sources; the student's words are the student's.)
4. **Students own their process data.** (The meter reads for the student first; the professor sees student-shared artifacts and aggregates, never a surveillance view.)
5. **Never a cheat report.** (The meter's output is a receipt, not an accusation. Always an exit: the Room.)
6. **Professors amplified, not replaced.** (Aggregate confusion map, zero-config; grading stays human.)
7. **Outside research is unsupervised; the Room is where proof is earned.** (Concede the perimeter; the perimeter was never the product.)
8. **Never compete with NotebookLM.** (And never compete with ChatGPT Edu / Gemini Edu — meter whatever they buy.)
9. **The core mechanism:** even if everything was AI-produced coming in, understanding still has to happen once before anything goes out.
10. **Fabricating the trail is the learning.** (Attack surface = learning surface. The only remaining attack — a proxy sitting in the room — is an identity problem, covered by L3 risk-sampled vivas in production.)
11. **No 100% anti-cheat claim, ever.** (Honest boundary, said out loud: the goal is fraud cost > learning cost, honest effort → portable value, system never accuses.)

---

## §5 Architecture — the three instruments and the two receipts

### 5.1 Insertion (width: the platform question answered)
- Ships as an **LTI 1.3 app** inside the LMS; meters the school's AI via its API surface (ChatGPT Edu / Gemini Edu) or its own school-keyed model endpoint. **Model-agnostic meter protocol**: log prompts, tool-calls, retrieved sources, citations, draft revisions, with timestamps and content hashes. If the school switches AI vendors, the meter survives — we are a protocol, not a model.
- Zero professor config on day one. The meter auto-classifies the task (brainstorm / draft / cite-verify / code) and profiles use against the task's demand.

### 5.2 The Meter — "how well" decomposed (depth: the taxonomy)
A **profile, never a score** — read against what the task demanded:

| Component | What it measures | How it's derived | Displayed as |
|---|---|---|---|
| Grounding rate | Claims traced to real sources | Citation check against course graph + live retrieval logs | % claims with provenance |
| Question quality | Interrogation before generation | Prompt taxonomy: clarifying / challenging / sourcing prompts before drafting | timeline strip |
| Verification behavior | Did they check the AI? | Edits after AI output; cross-checks against course materials | check events |
| Escalation judgment | When NOT to use AI | First-attempt-before-AI ratio; retrieval-before-generation | attempt ordering |
| Integration honesty | Provenance coherence | Born-inside vs pasted segments (birth-history of every passage) | coherent /断层 gaps (descriptive, never accusatory) |
| Transformation depth | What they added to the AI draft | Revision distance + addition type (structure vs substance) | revision ribbon |

- **Goodhart defense (the design hole that kills naive versions):** the meter's verdict is never "prompt looks nice". Every component feeds the Room's question selection; the Room's receipt is the outcome anchor. Performative prompting produces beautiful telemetry and fails the Room — which is exactly the diagnosis the receipt shows.
- **Dark-pattern self-policing:** the meter never gamifies usage into points, never nudges "use AI more", never ranks students. Those are vendor behaviors; ours is an instrument.

### 5.3 The Room — where proof is earned (built at v0.1)
- Typed, untimed, one sitting. No oral (fair to anxiety + non-native speakers). No clock (understanding is not speed). One receipt.
- Three phases: The material (mined lecture, real timestamps) → The room (anchored questions; coach follow-ups branch on the student's words) → The receipt.
- **Question generation from in-platform state** (v2 threat model, now structural): questions computed from (a) the Graph's board states for the lecture, (b) the student's own Meter log (where they hesitated, what they pasted, what the AI wrote). An external LLM cannot pre-generate or proxy these — it does not have the student's in-platform state. The whole-package-proxy hole stays closed.
- v0.1 exists: offline single-file HTML, real MIT 18.06 data (159 board states; 15 real frames; timestamps from states.csv), scripted coach honestly labeled, receipt with verbatim transcript, "record — not a grade" stamp. Mining real, coach scripted, receipt local — the labels are on the page.
- Production delta: coach becomes a model (reads student words, branches), receipt becomes a school-signed W3C VC / Open Badges 3.0 assertion, room questions become variant-engine generated (open question §13).

### 5.4 The Graph — the course's memory (the moat)
- Lecture recording → board states (validated: perceptual-hash dedupe, EMA α=0.08 drift smoothing, argmax-ink representative frames, 0.3s error vs synthetic ground truth; dHash blind to chalk is a known limitation ≤6/64 bits — ink-based detection carries it).
- 159 states with real timestamps are already extracted from MIT 18.06 Lecture 1 — the Graph's first nodes.
- Grows: board states + coach follow-ups + confusion events → per-course knowledge graph → the Room's anchors and the professor's confusion map.

### 5.5 The two receipts (width: the credential surface)
Every session mints two records, together the **Proof of Understanding**:
1. **Process receipt** (Meter): what AI contributed, what the student added, provenance coherence. Descriptive.
2. **Understanding receipt** (Room): what they can defend — exchanges, hints used, verbatim answers. Verifiable by reading.
- Student-held; shared BY CHOICE (Grammarly Authorship's sharing model, pointed at outcomes instead). Professor sees shared receipts + class aggregates. Semester trajectory = receipts compound → understanding portfolio.
- Production: signed (school as issuer, W3C VC), anchored to SIS identity. v1 receipt forgery (self-generated HTML) is a known and honest limitation of the prototype.

### 5.6 The loop that closes (width: the teaching surface)
Meter + Room data → **class-level confusion map derived from real process** (where the class's coach follow-ups clustered, which board states generated the most struggle) → professor adjusts the next lecture → the Graph grows. Tcherly proved teachers want this dashboard but built it on self-report; deriving it from actual process data is open, and it operationalizes "professors amplified" and "Learn from how the world teaches" in one surface.

---

## §6 Threat model v3 (each attack and its structural answer)

| Attack | Answer |
|---|---|
| Whole-package proxy (notes+question+transcript → one long-context LLM) | Room questions computed from in-platform state the proxy doesn't have; staggered/late questions; mutation challenges |
| Performative prompting (Goodhart) | Outcome anchor: Room receipt is the verdict; meter only feeds question selection |
| Retype attack (paste outside, retype inside) | Provenance coherence shows no birth-history; the Room catches what typing can't carry — follow-ups branch on words the typist didn't write |
| Collusion / prompt sharing | Receipts are personal-state-anchored; sharing a prompt doesn't transfer a receipt |
| Perimeter escape (phone photo, outside accounts) | **Conceded by design** — law 7. Outside work isn't caught; it doesn't count (no trail, no receipt). The product is the inside's pull, not the perimeter's wall |
| Surveillance drift (professor pressure → monitoring view) | Structural: meter is student-first, professor view is shared-artifacts + aggregates only; "never a cheat report" is law 5 |
| Receipt forgery (self-issue) | Prototype: honest limitation. Production: school-signed W3C VC |
| Proxy-in-the-room (someone else does the Room) | Identity problem, not understanding problem — L3 risk-sampled vivas on one's own submission (≈$0.42/exam per arXiv 2603.18221) |

---

## §7 Why anyone comes (the two honesty tables)

**Students — the inside must be better, not policed:**
| Inside the room | Outside (ChatGPT) |
|---|---|
| Knows the course (Graph: lectures, readings, notation) | Generic, course-blind |
| Unlimited usage, no caps | Caps |
| Every session compounds YOUR receipt (portable, student-owned) | A wall of text, zero evidence |
| Think-aid that asks before it answers | Dumps answers |

**Professors — amplified, zero config:**
- One-page class aggregate (confusion map), receipts only from students who chose to share.
- Assessment redesign that answers their governance problem: school-controlled AI, student-owned data, never an accusation.
- The take-home isn't graded; it's audited. The exam isn't a date; it's a hazard rate.

---

## §8 What could kill it (honest failure modes)

1. **The pull isn't strong enough.** If course-grounded AI + receipts don't beat the friction of the LMS login, students leak outside and the meter measures an empty room. Mitigation: the meter only ever certifies the inside (conceded perimeter), and the pilot measures the pull directly.
2. **Coach/variant-engine quality.** Scripted follow-ups are brittle (the pilot's failure list will show it). The model coach is the whole game — if its questions are worse than a TA's, professors won't credit the receipt.
3. **"Well" is discipline-relative.** A brainstorm and a cite-verify demand opposite patterns. Wrong task-mode classification → wrong profile. Mitigation: profile-not-score + auto-classification + professor override.
4. **Institutional friction.** LTI integration, privacy review, procurement cycles — slow. Mitigation: start as a research pilot with one course and CLEAR's cover; the sandboxed prototype already runs offline.
5. **The receipt has no relying parties.** If no one accepts Proof of Understanding, it's decoration. Mitigation: phase it — professor (grade signal) → department (portfolio) → external (internships); Open Badges 3.0 gives it a verifiable envelope from day one of production.
6. **We accidentally become Clarity.** The moment the meter is pointed at students for enforcement, the backlash lands on us. Mitigation: the design laws are load-bearing, not decorative; "never a cheat report" must survive contact with an angry professor.

---

## §9 The 48-hour pilot (what Friday's one-pager carries)

**Claim under test:** "unlimited AI + think-aid protocol" beats "bare vibe writing" on understanding — measured by the Room's receipt.

- One writing task; two groups of five. A: bare ChatGPT, unrestricted (dry vibe writing). B: ChatGPT + our think-aid protocol card (ask-before-answer, ground sources, restate-then-write).
- Both groups then take a blind Room session (material they haven't seen, same coach) → receipts = understanding score (exchanges, hints, verbatim answers).
- Deliverables: a stack of real receipts; one page of stats (n, median exchanges, hint distribution, completion); **the scripted coach's failure list** (every place a student's answer broke the follow-up rules) — simultaneously proof of feasibility, research practice, and self-falsification discipline.
- Framing, said out loud: **feasibility pilot, not efficacy study**. n=10 is the point of a pilot; the next step is the real study.

---

## §10 Friday positioning (discipline included)

- Bring: the v0.1 instrument (professor plays the student, 3 minutes, no oral from us), the pilot one-pager, the Graph's 159-node seed. No pitch deck. Say "platform" at most once. No commercial talk.
- Open with the evolution, honestly: "I wrote to you; then I attacked my own design; it broke; what survived is this."
- The CLEAR hooks: their CFP's Assessment Redesign strand; Teaching and Learning Innovation Expo 2026 (Dec 14–15) call for presentations — offer the pilot results as a student-coauthored submission.
- Ask: a pilot course (FYP or large lecture), and introductions to Dr. Pang (the takeover question: after scaffolding is withdrawn, how do we know takeover happened?) and Prof. Hargreaves (his four ideas blocked by "a lecture of 80 or more students and zero teaching assistants" — this layer is the instrument that unblocks them; his 2023 paper is the Room's assigned reading).

---

## §11 Open questions (keep visible)

1. Variant-engine quality: can the Room's question generator match a TA? (Test: 50 generated vs 50 human questions, blind-rated.)
2. Who defines "well" per discipline — auto-classify task modes or let professors pin them?
3. Meter protocol: which signals survive each vendor's API limits (ChatGPT Edu vs Gemini Edu)?
4. Receipt relying parties beyond the professor — who signs, who accepts?
5. Cost model: school pays for AI (already budgeted in Edu plans); our layer is thin — but what does the Room's model-coach cost per session?
6. Hong Kong context: CLEAR CFP alignment; TDG/FITE joint application with Dr. Pang as PI; the December Expo as first public artifact.

---

## §12 Source index (all verified 2026-10-14)

School AI: openai.com/index/introducing-chatgpt-edu/ · attheu.utah.edu (Nov 2025) · blog.google higher-education-gemini-notebooklm/ (Jun 2026) · gemini.google/students/ · edtechinnovationhub.com (Houston, Apr 2026)
Tracking: turnitin.com/products/feedback-studio/clarity · turnitin.com/blog (Clarity launch Mar 2025; "beyond surveillance" Dec 2025) · prnewswire.com (Jul 2025 launch; Feb 2026 data report) · cms-live-media.iste.org ISTE SEAL report (Apr 2026) · gptzero.me/chrome (Writing Replay) · grammarly.com/authorship (Aug 2024) · nationalcentreforai.jiscinvolve.org (Nov 2024) · businesswire.com (Authorship launch) · reddit.com r/CheckTurnitin "feels like digital surveillance" · thelegaljournalontechnology.com (Sep 2026)
The gap: unesco.org "What's worth measuring?" (May 2025) · journals.calstate.edu/ijaipil Jones 2026 · ojcmt.net SAID 2025 · tandfonline dependency scale 2026 · arxiv.org/abs/2609.17883 (Davalos & Zhang) · arxiv.org/abs/2609.36544 (DraftTrace) · papers.ssrn.com 7272718 (TWFF) · papers.ssrn.com 7024098 (Invisible Author) · aliciaguo.com Process as Poetic Provenance
Viva: insidehighered.com (Jun 2026) · arxiv.org/html/2603.18221v1 ($15/36) · tandfonline 02602938.2026.2644516 (Perkins 2026)
Confusion analytics: learning-analytics.info JLA 7555 (Tcherly, Chavan 2022) · files.eric.ed.gov EJ1375381 · dr.lib.iastate.edu (TeachActive, 2021)
Standards: 1edtech.org/standards/open-badges (OB 3.0, W3C VC 2.0, CLR 2.0) · 1edtech.org/standards/lti (LTI 1.3) · imsglobal.org/spec/ob/v3p0 · moderncampus.com (Jun 2026)
Hargreaves 2023: https://www8.austlii.edu.au/cgi-bin/viewdoc/au/journals/LegEdRev/2023/4.html · SSRN 4864589 (detector execution; four ideas; resource wall)
Built: lecture_miner.py + strang_out/ (159 states, states.csv) · proof-of-understanding/index.html (v0.1, delivered) · cuhk-clear-email-final.md · hargreaves-email.md
