# Decisions Log

Locked decisions (ADR-lite). Do not re-litigate a decision without new information. To change one, add a new entry that **supersedes** it and mark the old one `Superseded by D-xxx`.

Format: **D-xxx · date · title**. Context, then decision, then consequences.

---

### D-001 · 2026-10-11 · Positioning: "understanding infrastructure", not edtech
- **Context:** Edtech VC is down 26% YoY while AI VC is up 109% (proposal §6). Infrastructure survives budget reviews.
- **Decision:** Position the company as an *AI-native learning engine with outcome evidence* and the school's *evidence layer* ("Report Card 2.0").
- **Consequences:** Copy, decks and the product never describe themselves as an "edtech tool" or a "cheat detector".

### D-002 · 2026-10-11 · First wedge: CS departments (code track) — superseded in part by D-011 (build order only; the wedge itself stands)
- **Context:** Writing process evidence is crowded (Turnitin Clarity, GPTZero …). Code process evidence combined with a mid-work viva is an empty market (proposal §6).
- **Decision:** Phase 1 = code track (variant engine + line-level viva + no-paste editor). Writing track is Phase 2. Beachhead for writing = FYP cohorts.
- **Consequences:** M8 is built before M9. Do not build writing features first.

### D-003 · 2026-10-11 · Helper / Coach split
- **Decision:** There are two voices. The Helper answers the student and removes mechanical friction unconditionally. The Coach asks the student questions grounded in the course graph. Students can tune how often the Coach speaks, but not the End for graded work.

### D-004 · 2026-10-11 · Outside / Door / Room / End model
- **Decision:** The research phase is unsupervised and we never compete with note or research tools. The Door imports anything and is source-neutral. The Room is where proof is earned. The End is an explicit completion with artifacts.

### D-005 · 2026-10-11 · Typing is an entry condition, not proof
- **Decision:** No-paste and typing provide process evidence only. The viva challenge is the gate. Burst-typing escalates challenge intensity and leads to the *Oral-verified* tier, labeled honestly. Instructor-approved alternatives are required for accessibility.

### D-006 · 2026-10-11 · Output is comprehension, never a cheat verdict
- **Decision:** Tiers are Strong / Partial / Oral-verified (or *returned with reasons*). Low process confidence leads to a **recommended** oral check, and humans decide consequences.
- **Consequences:** No automated penalties anywhere in the system. This matches the EU AI Act high-risk posture.

### D-007 · 2026-10-11 · Data ownership and 3-layer isolation
- **Decision:** L1 tenant course graph (per school, encrypted, never global). L2 global concept graph (concepts, prerequisites, openly licensed content). L3 student mastery model (owned by the student). Schools see only derived signals from student process data. See [design/data-isolation.md](../design/data-isolation.md).
- **Consequences:** Isolation and no-training promises must be engineering-auditable.

### D-008 · 2026-10-11 · Visual miner is pixel-based, ML-free at the core
- **Decision:** Board and slide state extraction uses ffmpeg, OpenCV and numpy heuristics (EMA drift, ink argmax). VLMs only spot-check candidates. Validated in the prior session.
- **Consequences:** Ingest cost per lecture is about zero, which supports the promise that schools "keep posting what you already post".

### D-009 · 2026-10-11 · Go-to-market: B2B2C, department-level wedges
- **Decision:** The buyer is the principal, provost or department head. Students are never charged. Pricing is per student per year, with FYP cohort pricing. Wedge order: CS departments, then FYP modules, then secondary schools via hero teachers. Renewal is driven by in-cohort student NPS.

### D-010 · 2026-10-11 · Brand voice locked
- **Decision:** Hero line: "Learn from how the world teaches." Sub-line: *Built to make you think — not to think for you.* Full voice rules in proposal §11. Product name is still open (OL-001).

### D-011 · 2026-10-12 · Build the concierge viva pilot before the full Phase 1 code track
- **Context:** /office-hours diagnostic found no direct demand evidence, no known instructor workaround and no named user (Q1-Q3). A landscape search showed the "EMPTY market" claim for code viva is overstated (ACM 763-educator survey: 68% already changed assessment; SIGCSE 2026 AI oral exam talk).
- **Decision:** Approach A: interview ~5 CS instructors, hand-run one viva, then build only an async viva runner. Full Phase 1 (miner, KG, variants, no-paste editor, Proof) is deferred, not cancelled. Design doc: docs/designs/concierge-viva-pilot.md.
- **Consequences:** OL-002 (recover miner) and OL-003 (variant probe) drop to P1/P2. Next action is five instructor emails.

### D-012 · 2026-10-12 · Premise 3 revised: course graph as differentiator is unproven
- **Decision:** Test it with a blind comparison: graph stand-in (hand-structured notes: concepts, prerequisites, where taught) vs the same notes pasted raw, randomized X/Y, instructor rates, graph must win 6 of 10 or the premise is dropped.

### D-013 · 2026-10-12 · Question generator guardrails
- **Decision:** Student code is quoted data; each question must cite a real line and quote its text or be regenerated (max 2 retries); failures are distinct, logged and visible, with a manual fallback.

### D-014 · 2026-10-12 · Pilot is formative, consent-first
- **Decision:** Ungraded practice viva, consent note naming the LLM provider, opt-out, transcripts only with consent, 30-day deletion, student export. Honors product law 7 (students own process data).

### D-015 · 2026-10-12 · Build the thin viva runner before outreach (founder call)
- **Context:** After the CEO review recommended interviews first, the founder chose to build a demo first so outreach can offer something concrete.
- **Decision:** Build the runner (Python/FastAPI + plain HTML + Claude API, `runner/`), demo-grade, only what the approved pilot plan needs. Outreach starts the day it works. Time-box: about one day of CC work.
- **Consequences:** Risk noted in the review: building before evidence. Mitigation: no features beyond the design doc; do not extend until OL-013 has two answers.

### D-016 · 2026-10-12 · Build a showable Room demo on DeepSeek (founder call)
- **Context:** After the runner, the founder asked for a fuller demo: multiple source-rich rooms, a writing sandbox, Helper and Coach, "everything stated, but as demo", with DeepSeek as the LLM.
- **Decision:** `demo/` (FastAPI + one-page JS app). LLM provider for the demo is DeepSeek (`deepseek-chat`); the pilot runner stays on its own path and policy. Demo content is fictional.
- **Consequences:** This goes beyond the D-015 guardrail (build only what the pilot needs). Treat the demo as a communication asset, not evidence. Student text goes to DeepSeek in the demo, so no real student data. Outreach (OL-013) is still the P0 and is not unblocked by the demo.

### D-017 · 2026-10-12 · Positioning corrected: the viva is a commodity, the wedge is the daily-flow trust layer
- **Context:** Market research (/plan-ceo-review, HOLD SCOPE): NYU Stern Viva is public and costs ~$0.42/student in compute; OralExam.AI, ExamSim, EXAMAI, Socratic Mind exist; Codio has paste flags; Turnitin Clarity is in 2026 campus pilots; "Prova" could not be verified.
- **Decision:** Proposal sections 6 and 14 rewritten (done): the "EMPTY market" claim is removed; differentiation = course-grounded questions + a defensible record + student-owned proof, still unproven (D-012).
- **Consequences:** Outreach and decks must not claim nobody sells code viva.

### D-018 · 2026-10-12 · Pricing is three hypotheses, validated through the interviews
- **Decision:** H1 per-course license, H2 per-student add-on, H3 free pilot then department license (details in proposal section 7). Interview script asks which fits, what they pay today and who signs. No price is pitched until data exists.

### D-019 · 2026-10-12 · First five interviews: 3 Hong Kong university instructors + 2 remote
- **Context:** HKU and PolyU say they will redesign assessment rather than buy detection; HKUST's June 2026 AI-glasses test showed exams can be beaten; the Education Bureau does not provide AI tools; no HK/SG procurement data was found.
- **Decision:** Interview 3 Hong Kong university CS/engineering instructors or FYP supervisors and 2 remote instructors (comparison). Hong Kong secondary schools and global community sampling are deferred.

### D-020 · 2026-10-12 · Test the free-alternative threat directly
- **Decision:** Keep interview Q9 (DIY check) and an optional 10-minute side-by-side with NYU Viva; add "beats the free alternative" (3 of first 5) to pilot success criteria.

### D-021 · 2026-10-12 · Outreach data-handling note and demo sample-text mode
- **Context:** The demo sends text to DeepSeek; the pilot uses Anthropic with consent (D-014). University IT and integrity staff will ask where data goes.
- **Decision:** `docs/outreach-data-note.md` is the one-page answer; demo gets a sticky "never enter real student work" banner and a "Use sample text" button. DeepSeek stays the demo provider (D-016 not reversed).

### D-022 · 2026-10-12 · Eng review of runner/ and demo/: two services stay; 13 hardening decisions
- **Context:** /plan-eng-review (docs/designs/eng-review-runner-demo.md). Live probes found: provider errors escape as raw 500 (breaks D-013), retention clock resets on every save (breaks D-014), untrusted text can close its own prompt delimiter, instructor tokens appear in access logs, demo Helper reply can land in the wrong room, demo Proof is client-computed.
- **Decision:** keep runner/ and demo/ separate (data-policy separation, D-014 vs D-021). Approved: wrap provider errors (R1), created-based retention with hourly lazy purge (R2), per-request random tag suffix in each service, no shared module (R3), rate limits + daily caps + demo access code (R4), header/fragment tokens (R5), Proof labeled self-reported (R6), capture asking room (R7), llm.chat tests (R8), Playwright tests for both front ends (R9), 12-case live prompt eval (R10), request size caps (R11), atomic serialized writes (R13). Deferred: total generation time budget (R12, TODOS.md, depends on OL-017).
- **Accepted shortcuts (Completeness 7/10):** Proof label instead of server-recorded proof (upgrade when verifiable proof is needed); time budget deferred (upgrade when OL-017 gives Anthropic p50/p95).
- **Consequences:** Tasks T1 to T12 (OL-021). The runner must not host real students before T1, T2, T3 and T4 land.

### D-023 · 2026-10-14 · CANDIDATE direction: process-as-proof writing platform + teacher mirror (founder call; confirm after CLEAR meeting)
- **Status:** Candidate, not locked. Does **not** yet supersede D-002 (code-first wedge) or D-011 (concierge viva pilot). Confirm or drop after the CLEAR meeting on 2026-10-16 (OL-022).
- **Context:** The founder argues assessment is an arms race that detection and better checks cannot win. Research (2026-10-14) found: Socratic modes are now default options in ChatGPT, Gemini and Claude; Turnitin Clarity and DraftTrace already record writing process and AI chats; nobody combines a course-grounded staged process with feedback to the teacher. Proposal v2's Meter-via-API and "proxy hole closed" claims did not hold up.
- **Decision (candidate):** Pitch Acader as a school-customised AI learning and writing platform that makes understanding the cheapest path. The AI does retrieval and mechanics; anything that would produce a claim, synthesis or argument structure becomes a question. The instructor sets strictness per stage (AI Assessment Scale). Gaps in the trail lead to a conversation (what you read, where, say it aloud), never an accusation. The same process feeds a **teacher mirror** (class-level misconceptions linked to lecture moments), owned by the teacher, with no rankings and a minimum group size of ~5.
- **Consequences:** Brief is [ultimate-proposal-v3.md](../ultimate-proposal-v3.md). If confirmed, CLAUDE.md §5, the interview script (writing-track and teaching-centre targets) and the design docs change, and M9 (writing) plus a teacher-mirror module move ahead of M8 (code). Product laws 1–10 are unchanged; the teacher mirror extends law 7 (ownership) to teachers.
