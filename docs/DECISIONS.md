# Decisions Log

Locked decisions (ADR-lite). Do not re-litigate a decision without new information. To change one, add a new entry that **supersedes** it and mark the old one `Superseded by D-xxx`.

Format: **D-xxx · date · title**. Context, then decision, then consequences.

---

### D-001 · 2026-10-11 · Positioning: "understanding infrastructure", not edtech
- **Context:** Edtech VC is down 26% YoY while AI VC is up 109% (proposal §6). Infrastructure survives budget reviews.
- **Decision:** Position the company as an *AI-native learning engine with outcome evidence* and the school's *evidence layer* ("Report Card 2.0").
- **Consequences:** Copy, decks and the product never describe themselves as an "edtech tool" or a "cheat detector".

### D-002 · 2026-10-11 · First wedge: CS departments (code track) — superseded in part by D-011, then fully by D-024 and D-030 (2026-10-22)
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
- **Decision:** L1 tenant course graph (per school, encrypted, never global). L2 global concept graph (concepts, prerequisites, openly licensed content). L3 student mastery model (owned by the student). Schools see only derived signals from student process data. See [design/data-isolation.md](../archive/design-v1/data-isolation.md).
- **Consequences:** Isolation and no-training promises must be engineering-auditable.

### D-008 · 2026-10-11 · Visual miner is pixel-based, ML-free at the core
- **Decision:** Board and slide state extraction uses ffmpeg, OpenCV and numpy heuristics (EMA drift, ink argmax). VLMs only spot-check candidates. Validated in the prior session.
- **Consequences:** Ingest cost per lecture is about zero, which supports the promise that schools "keep posting what you already post".

### D-009 · 2026-10-11 · Go-to-market: B2B2C, department-level wedges
- **Decision:** The buyer is the principal, provost or department head. Students are never charged. Pricing is per student per year, with FYP cohort pricing. Wedge order: CS departments, then FYP modules, then secondary schools via hero teachers. Renewal is driven by in-cohort student NPS.

### D-010 · 2026-10-11 · Brand voice locked
- **Decision:** Hero line: "Learn from how the world teaches." Sub-line: *Built to make you think — not to think for you.* Full voice rules in proposal §11. Product name is still open (OL-001).

### D-011 · 2026-10-12 · Build the concierge viva pilot before the full Phase 1 code track — superseded by D-024 / D-030 (parked 2026-10-22)
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

### D-023 · 2026-10-14 · CANDIDATE direction: process-as-proof writing platform + teacher mirror (founder call; confirm after CLEAR meeting) — confirmed by D-024 (2026-10-22)
- **Status:** Candidate, not locked. Does **not** yet supersede D-002 (code-first wedge) or D-011 (concierge viva pilot). Confirm or drop after the CLEAR meeting on 2026-10-16 (OL-022).
- **Context:** The founder argues assessment is an arms race that detection and better checks cannot win. Research (2026-10-14) found: Socratic modes are now default options in ChatGPT, Gemini and Claude; Turnitin Clarity and DraftTrace already record writing process and AI chats; nobody combines a course-grounded staged process with feedback to the teacher. Proposal v2's Meter-via-API and "proxy hole closed" claims did not hold up.
- **Decision (candidate):** Pitch Acader as a school-customised AI learning and writing platform that makes understanding the cheapest path. The AI does retrieval and mechanics; anything that would produce a claim, synthesis or argument structure becomes a question. The instructor sets strictness per stage (AI Assessment Scale). Gaps in the trail lead to a conversation (what you read, where, say it aloud), never an accusation. The same process feeds a **teacher mirror** (class-level misconceptions linked to lecture moments), owned by the teacher, with no rankings and a minimum group size of ~5.
- **Consequences:** Brief is [ultimate-proposal-v3.md](../archive/proposals/ultimate-proposal-v3.md). If confirmed, CLAUDE.md §5, the interview script (writing-track and teaching-centre targets) and the design docs change, and M9 (writing) plus a teacher-mirror module move ahead of M8 (code). Product laws 1–10 are unchanged; the teacher mirror extends law 7 (ownership) to teachers.

### D-024 · 2026-10-22 · Direction locked: The Writing Room, process as evidence (founder call)
- **Context:** The demo was shown to professors and researchers on 2026-10-21; they called it a potential startup and gave the nursing case (40-page Copilot log, repeated meetings). The CLEAR meeting has happened (founder, 2026-10-22). Kit v0.4/v0.5 (simulated) showed claim lineage separates outside-written work where typing signals failed (v0.3).
- **Decision:** Acader is a writing platform that schools buy and students write in. Every word in the final piece has a traceable origin (source span, lecture moment, Coach exchange, declared import) or is shown as untraced. The teacher gets a receipt with the proportion and process insights as evidence. Confirms D-023; supersedes D-002 (code-first wedge) and D-011 (viva pilot as current focus).
- **Consequences:** Product design is [docs/designs/writing-platform-v1.md](designs/writing-platform-v1.md), engineering design is [docs/designs/provenance-engine.md](designs/provenance-engine.md). CLAUDE.md §1, §4, §5 updated. The teacher mirror (D-023) stays in the direction but comes after v1.

### D-025 · 2026-10-22 · The receipt shows where to ask, never a verdict; proportions only of recorded traces
- **Context:** The founder wants an AI-use proportion as evidence. Outside AI can't be measured: a retyped hybrid scored 92 vs 91 for honest work (v0.3). Closes OL-032.
- **Decision:** The receipt's core promise is "where to ask". Proportions are shown only as bands of recorded traces: traced to source/lecture, traced to a Coach exchange, declared outside help, polish only, untraced. Never "% AI". "Untraced" is printed with its meaning: no record here, not evidence of AI. The Coach record shows outcomes, including "declined to answer", as facts, not penalties. "Bulletproof" means a tamper-evident log and receipt lines that cite events; it does not mean proving where a thought came from.
- **Consequences:** No velocity, stylometry or cosine-threshold verdicts (provenance-engine.md §8). Proportions are computed over words and over claims.

### D-026 · 2026-10-22 · Assume outside AI is present; declared channel; the Coach helps, not judges
- **Context:** Founder: "we assume outsider LLM", the Coach's job is to make the idea stronger so the student understands and uses their own brain.
- **Decision:** The design assumes outside AI is always available. A declared channel (the Door) imports logs, outlines and ideas as unanchored claims; declaring is never penalised. The Helper answers and the Coach asks, in five cases: A blank page, B arrived with outside AI, C untraced text, D weak reasoning in the student's own work, E confident mode.
- **Consequences:** Internal wording is "assume outside AI is present"; no UI, copy or pitch ever says or implies "suspect the student" (law 10).

### D-027 · 2026-10-22 · Help students read; never summarise
- **Context:** Researchers agreed nobody should read 40 pages cold when tools exist; the founder: use AI in the platform "like Google Scholar" to help them read while still aiding their thinking. Moves OL-033 to design.
- **Decision:** Sources are teacher uploads, lecture material, student-found papers (scholarly search) and pasted outside sources. The reading aid gives places to read (support, skeptical, limitation, data, method, definitions…) plus Triad recommendations, and pointers, not conclusions. The student writes the takeaway as an anchored idea card. Citation verification is feedback to the student, not a provenance signal (v0.4).
- **Consequences:** Pointer text goes through the law-1 leak check. A PDF parsing spike is needed (S2).

### D-028 · 2026-10-22 · Product laws 5 and 9 amended
- **Decision:** Law 5: typing is not proof; process tracing is evidence of the student's thinking (writing traced back to its mind map) and of where to ask; when a conversation is needed the trace gives the grounds; the conversation is still the gate. Law 9: the platform is a writing platform for school work (graded or practice); writing first; still not a general notes app.
- **Consequences:** CLAUDE.md §4 updated.

### D-029 · 2026-10-22 · Prototype v1: real pilot + researcher follow-up, 2 weeks, DeepSeek
- **Decision:** Prototype v1 serves a real student pilot (English, several classes: nursing/health, a HK writing course, CS/FYP, the researchers' courses) and a follow-up with the researchers. Built solo with Claude in about 2 weeks (target 2026-11-05). LLM: DeepSeek behind a provider interface. Stack decided in /plan-eng-review (OL-008).
- **Consequences:** Tensions flagged for review (writing-platform-v1.md §10): the timeline vs. real-pilot hardening, DeepSeek consent for HK students (OL-037), and no committed class yet (OL-036).

### D-030 · 2026-10-22 · Code track parked
- **Decision:** The concierge viva pilot, code-track MVP and `runner/` are parked, not deleted. The lecture miner (M2) stays as a future input for lecture sources (law 8).
- **Consequences:** design/README.md marks them PARKED. OL-003, OL-009, OL-015 and OL-017 are parked with them.

### D-031 · 2026-10-23 · Repo restructured for the v1 prototype; PRODUCT.md and design/ are the working specs
- **Context:** The founder asked to "formulate this repo into the new repo for making the prototype" and rewrite all specs and design docs after D-024 to D-030.
- **Decision:**
  - `PRODUCT.md` replaces `ultimate-proposal.md` as the source of truth for product intent.
  - `design/` holds the v1 engineering set: architecture, event-log, provenance, receipt, reading-aid, coach-helper, privacy, evaluation, build-plan.
  - `docs/designs/` keeps the 2026-10-22 drafts as review inputs, marked superseded.
  - Earlier proposals, design v1, `demo/` and `runner/` move to `archive/`.
  - `shared/llm.py` becomes the single LLM client.
  - `prototype/` is where v1 code goes.
  - Law 6 in CLAUDE.md and PRODUCT.md now says "never a verdict; the receipt is a process profile with no score", in line with D-025. Comprehension tiers (Strong / Partial / Oral-verified) are no longer a v1 output.
- **Consequences:** CLAUDE.md, README.md and GLOSSARY.md rewritten. OL-010 closed (no tiers). The stack in design/architecture.md §4 is a **recommendation**, not locked (OL-008 stays open until /plan-eng-review). The founder should confirm the law 6 wording.

### D-032 · 2026-10-23 · CEO review of v1: receipt-first thin slice, one class, pilot gate hardened
- **Context:** /plan-ceo-review (SCOPE REDUCTION) on PRODUCT.md + design/build-plan.md. Landscape: Turnitin Clarity and Grammarly Authorship already track who typed what, with the same retype blind spot we measured (v0.3). Our difference is claim lineage plus "where to ask" questions. Record: [docs/designs/ceo-review-v1.md](designs/ceo-review-v1.md).
- **Decision:**
  - **Build:** the receipt and chain view first on golden sessions, then the writing flow, for one class. 2026-11-05 = build ready (CEO-1).
  - **Deferred:** scholarly search, LLM pins, Coach A/D/E, graph view, polish band, policy dial, receipt PDF, further classes (CEO-1, 3, 4, 5).
  - **Rules:**
    - A second LLM backend is ready behind the boundary (CEO-6).
    - Submit always seals; questions follow later (CEO-7).
    - Roster + magic-link sign-in; Blackboard LTI is the first item after the pilot (CEO-8).
    - The Door never fetches URLs (CEO-9).
    - Receipts are released to the teacher at the deadline (CEO-10).
    - A named teacher must be found by 10-30, or the hosting work is skipped (CEO-11).
    - Ethics approval and an assignment window join the pilot gate (CEO-12).
    - Reworded text that hasn't been checked counts as untraced (CEO-13).
    - S3 must pass or L3b stays off (CEO-14).
    - The nursing walkthrough happens mid-build (CEO-15).
    - The event log takes one append at a time per log (CEO-16).
- **Consequences:**
  - build-plan.md is rewritten; PRODUCT.md §7 is updated.
  - Override boxes are added to the design docs until /plan-eng-review folds them in (P-14).
  - TODOS.md lists the deferrals.
  - /plan-eng-review is the required next step.

### D-033 · 2026-10-23 · Second outside review (Opus) of v1: no self-asserted "traced", real humans first, blind test of the core bet
- **Context:** The founder asked for an Opus reviewer instead of Codex. It read the full plan and found 16 issues. Record: [docs/designs/ceo-review-v1.md](designs/ceo-review-v1.md) (CEO-17 to CEO-24).
- **Decision:**
  - Student-made links show as "linked by student, not checked" unless the AI check confirms them (CEO-17).
  - 3–5 real people try the flow before any graded pilot, with a stop rule (CEO-18).
  - A blind test: process-grounded vs essay-only questions, plus the hard case, in the walkthrough and the pilot (CEO-19).
  - The student preview shows spans and facts, not question text (CEO-20).
  - Release to the teacher at the latest of: deadline, submit + 24 h, questions compiled (CEO-21; supersedes the CEO-10 rule).
  - The pilot gate adds platform-as-processor approval (CEO-22).
  - Schedule re-estimated bottom-up: 11-05 = engine + receipt + walkthrough ready (CEO-23).
  - Stronger S3, an adversarial leak set, and no link-UI cut while the check is off (CEO-24).
- **Consequences:**
  - build-plan.md is rewritten.
  - The founder's new point is open as OL-043 (P0): if guidance makes traces uniform, something besides the trail must estimate AI involvement.

### D-034 · 2026-10-23 · Eng review of v1: stack locked, receipt hardened against forged traces, schedule re-baselined
- **Context:** /plan-eng-review on the whole v1 plan set, plus an outside review by an Opus Plan agent (the founder asked for Opus, not Codex). 35 decisions, D1 to D35. Record: [docs/designs/eng-review-v1.md](designs/eng-review-v1.md).
- **Decision:**
  - **Stack (closes OL-008):** Python 3.12 + FastAPI; Vite + TS + TipTap + PDF.js with one `web/schema.json`; SQLite (WAL) everywhere on one machine (D3); DB job rows with a bounded queue (D23); hosted PDF parsing with caps and status (D4); no embeddings in v1 (D1); DeepSeek + a generic OpenAI-compatible backend (D14); `shared/llm.py` wrapped, not changed (D22).
  - **Code arrangement:** server = app/, engine/ (pure; CLI), sources/, coach/ (D2).
  - **The receipt can't be gamed into "traced":** marks are checked against their source at compile, quotes per block with a minimum length (D5, D29); pasting inside cards and Coach answers is tracked (D26); student-made links get their own band "linked by student, not checked" (D27).
  - **The record:** the server replays steps with prosemirror-py, with checkpoint checks and a labelled fallback (D6, D28); seal = the submit event, with a post-seal whitelist (D8); AI outputs behind a receipt are stored, so every line can be rebuilt (D31); receipts carry an engine stamp (D20).
  - **Privacy:** batch times rounded to 5 minutes and batches merged per 5 minutes (D12, D30); no reading dwell (D16).
  - **Operations:** release capped at +48 h with "questions pending" (D7, reopens CEO-21); edit lease and stale-queue rule (D10, D32); scanner-safe magic link (D11); the security set (D9); AI error classes and a boot ping (D13); monitoring (D15); deploy freeze in the window (D34).
  - **Tests:** S1 widened (D21); golden sessions generated by driving the real editor, regenerated in CI (D19, D33).
  - **Schedule (D25):** re-estimated bottom-up at about 28 build days. Engine + receipt + walkthrough ready about **2026-11-08** (was 11-05). Ways to pull it back are proposed in build-plan §2a; none are applied.
- **Consequences:**
  - The design docs are rewritten with every CEO and eng decision, and the override boxes are removed (D24).
  - TODOS gains L2 embeddings and "move to Postgres".
  - The kit is frozen.
  - Next: the founder picks a §2a option; then M0 (scaffold + S1) on 10-24.


### D-035 · 2026-10-24 · The live map is the product; a mapper builds it as the student writes; the model maps meaning, never trust
- **Context:** At the start of /plan-design-review the founder proposed: build the map bottom-up during writing with a small model on each change ("a trust ladder"), so nothing has to be reconstructed at the end; flag, never interrupt, never a timed question; a golden set of ~100 papers with real sources and a textbook. Claude agreed with the direction and proposed one hard line. The founder agreed totally.
- **Decision:**
  - **The live map is the product.** The student's claims, sources and Coach answers come together as they write. The receipt is a snapshot of the map at submission, not a reconstruction.
  - **A mapper** (its own role, not the Helper or the Coach) runs a small model on each 5-minute batch (D30 windows, the D23 job queue). It proposes meaning links: this sentence argues claim N; this paraphrases passage P.
  - **The model maps meaning, never trust.** Provenance bands come only from recorded facts (origin marks, the quote check, paste). A model link never raises a band. It shows as its own state, "linked by model, not checked", next to student_linked (D27), and is stored as a compile artifact (D31).
  - **Flags go to the student, not the teacher.** Mapper findings surface as Coach questions in the student's panel, grounded in the trail (law 2). Never an interruption, never time-limited. The teacher sees only the receipt, where flags feed the 2–3 "where to ask" questions. There is no running flag log for schools.
  - **Golden set:** real sources plus an open-licence textbook (e.g. OpenStax), 15–20 hand-scripted sessions in the D19 YAML format, and a generator for variants up to ~100. Labelled simulated; it tests the engine, not students.
- **Consequences:**
  - PRODUCT.md §5 updated. The design docs (provenance, receipt, coach-helper, evaluation, architecture, build-plan) need the mapper folded in (OL-044).
  - /plan-design-review re-centres on the map as the student's main screen.
  - The founder considers build hours not the constraint (more sessions as needed); the D25 schedule stands until re-planned. The real constraints are a named teacher, the school calendar and spike results.

### D-036 · 2026-10-24 · Design review of the live-map workspace and the receipt (1A–20A)
- **Context:** /plan-design-review on the workspace (re-centred on the live map by D-035), the receipt, the student preview and P-15. All 7 passes; one Opus subagent as the outside voice (Codex skipped). Mockups blocked (no OpenAI key). Every item was its own question; the founder took the recommended option each time. Record: [docs/designs/design-review-v1.md](designs/design-review-v1.md).
- **Decision (highlights):**
  - **Layout (1A):** editor is the anchor; the live map is a left outline wired to the text both ways; Coach right; v1 "map" = outline (graph stays deferred).
  - **Map suggestions (4A, 5A):** named "suggested by the map, not checked"; the student confirms (→ student-linked, never traced) or rejects (never on the receipt); never shown on the teacher's bars or chain. L3b links read "checked against the source".
  - **Receipt (2A, 3A, 10A, 12A, 20A):** four-part first screen, details folded, seal in About; alphabetical submissions list with no band columns; a document, not cards; one-hue band scale (untraced = outline only); plain rounded chain labels.
  - **Student side (6A, 7A, 8A, 9A, 17A, 18A):** full state table; trail off by default with "Show my trail"; preview framed "Be ready to explain your thinking"; P-15 withdrawal allowed with plain notices both sides; one Coach budget shared with mapper findings; case C copy about the map, never the student.
  - **Access (14A, 15A, 16A, 11A):** three columns / drawers / one-column writing mode, writing never blocked (zoom); landmarks, F6, quiet counts, no live announcements; only student-triggered motion.
  - **Wording (19A):** the filter runs on every surface; "flag" banned everywhere.
  - **Design system (13A):** /design-consultation produces DESIGN.md before the receipt UI (M1) and M3.
- **Consequences:** new design/workspace.md; receipt.md, coach-helper.md, provenance.md, privacy.md, event-log.md, build-plan.md, PRODUCT.md §5 and GLOSSARY updated. D-035's label "linked by model, not checked" is superseded by "suggested by the map, not checked". P-15 closed. Design score 3/10 → 7/10; the rest waits on DESIGN.md and real mockups.

### D-037 · 2026-10-24 · Eng review v2: the mapper made safe to build; the pilot tests the student-built outline
- **Context:** /plan-eng-review on the branch diff, scoped to what D-034 had not seen: D-035 (mapper) and D-036 (workspace). Native Plan subagent as the outside voice (Codex skipped at founder request); it found a Critical hole: one click on a suggestion could move pasted outside text out of untraced. 21 decisions, one question each; the founder took the recommended option every time except D2. Record: [docs/designs/eng-review-v2.md](designs/eng-review-v2.md).
- **Decision:**
  - **Sequencing (D1, D16):** mapper in a new milestone M4m (~11-18 → 11-21, after H), behind `mapper_enabled`, not required by the pilot gate. H runs with the flag off.
  - **Structure (D2):** own packages `server/mapper/` and `server/trail/`; trail holds no band logic and calls the engine's L1 (D8, golden parity test).
  - **Record (D3, D14, D15):** chained `map.suggestion` (doc_rev, sentence_hash, claim_id, artifact ids), `map.finding` (only `unconnected_paragraph`, `claim_without_source`; never about a "Not this" sentence) and `map.answer`. A stale suggestion is not shown. Late results after the seal are discarded (D4).
  - **Never trust, enforced (D12, D13, D19):** an accepted suggestion is a student link carrying `suggestion_id`, shown as a sub-count; a sentence ≥ 50% `paste_ext` never enters band 4 by any link; the v1 mapper never links to source passages, and a model link can never make text traced.
  - **Privacy (D5, D20):** minimum payload (changed paragraphs + claim texts + block titles); two consent versions; the flag is fixed per record at `log.open`.
  - **Budget (D6, D18):** lowest priority, skip < 30 changed words, one queued job per log, cap 40 calls; at most 3 open suggestions shown.
  - **Eval (D7, D17):** labelled `expected_links`; precision ≥ 0.80, recall ≥ 0.50, ≤ 1 per batch, both backends, ≥ 5 held-out sessions, 3 separate human sessions with second-person labels.
  - **Teacher and withdrawal (D9, D10):** "discussed" stored teacher-side; withdrawal cancels queued jobs in the same transaction and deletes any unreleased receipt.
  - **Framing (D21):** the pilot tests the live outline the student builds; the mapper is a flagged experiment. D-035's "the model maps meaning, never trust" is unchanged.
- **Consequences:** event-log.md, provenance.md, architecture.md, privacy.md, evaluation.md, build-plan.md, receipt.md, coach-helper.md, workspace.md, PRODUCT.md §5/§7 and GLOSSARY updated. OL-044 closed. Build total ≈ 35–36 build days; M4m off the pilot-gate path. Eng review status: clean.

### D-038 · 2026-10-24 · Every new idea gets the same Coach treatment; one pillar question at a time
- **Context:** The founder proposed treating a shower thought and an outside AI's thought the same, with the same Helper and Coach treatment, and using the four pillars to question the student so they can't one-shot an outside LLM and have to think first. Claude agreed, with three changes: say "thinking is the easier path", never "they can't cheat"; ask, never block; one pillar per idea, not four. The founder agreed ("exactly").
- **Decision:**
  - Coach cases B (declared import) and C (paste > 40 words, unconnected paragraph) and mapper findings are **triggers for one "new idea" case**. The Coach never asks where an idea came from (law 6: untraced is not AI).
  - Questions come from **four pillars**: reading, logic, writing, communication. **One pillar per idea**, chosen by fit, grounded in the student's own sources and claims (law 2). Same Coach budget (17A).
  - **Never blocking:** the student writes the idea freely; the question comes later in the panel; declining is a recorded fact.
  - The record is unchanged: declared help still shows as declared on the receipt, so declaring keeps paying off (law 4).
- **Consequences:** coach-helper.md §3 (pillar table), event-log.md (`coach.ask` gains trigger_ref and pillar), PRODUCT.md §5 step 5, GLOSSARY ("Four pillars") updated.

### D-039 · 2026-10-24 · DeepSeek workers may read the repo (F-005)
- **Context:** The multi-agent flow (CLAUDE.md §8) uses DeepSeek workers for mechanical pieces. A DeepSeek worker sends repo code and docs to a China-based provider. The repo holds no secrets and no student data.
- **Decision:** Approved by the founder. Tasks marked **D** in TASKS.md may use DeepSeek workers.
- **Consequences:** Limits stay: DeepSeek workers never receive `.env` or anything outside the repo, and no student data ever enters the repo. F-005 done.

### D-040 · 2026-10-24 · Locked Python dependencies; Node 22.12+ for the front end (T-001 PD-1, PD-2)
- **Context:** T-001 left Python dependencies unpinned. D20/D31 promise a byte-identical receipt from the same log and engine stamp, which needs reproducible engine dependencies. Current Vite and Vitest need Node 22.12+.
- **Decision:** (1) Python dependencies get a lock file (pip-tools or uv) that CI installs, and the lock file's hash goes into the engine stamp. Done inside T-003. (2) Node 22.12+ is the front-end floor.
- **Consequences:** T-003 scope grows by the lock file and CI install change; the engine stamp includes the lock hash once the stamp exists (M1).

### D-041 · 2026-10-24 · The chain and the receipt's numbers (spike S5, PD-S5-1…4)
- **Context:** Spike S5 (T-005) built the chain and `verify`, and found four gaps in the spec.
- **Decision:** (1) `prev_hash` enters the hash as its lowercase hex text (UTF-8). (2) An id in `event_ids` is the event's `seq`. (3) The receipt JSON has no floats: band shares are integer word counts (plus `total_words`) and the renderer rounds, so `receipt_hash` is well defined. (4) The seal covers the record up to submission; later notes and links are chained and dated, not sealed, and "About this receipt" says so. No anchoring of the post-seal head in v1.
- **Consequences:** event-log.md §3/§6, receipt.md §3/§6 updated. EXPECTATIONS C already carries the caveat. OL-035 closed.

### D-042 · 2026-10-24 · LLM boundary details (T-003 PD-1…4)
- **Decision:** (1) Per-task output schemas are provisional; each feature task (Coach, receipt, provenance L3, reading aid, mapper) owns its schema and stub fixture and may change them with its prompt, without a new decision. (2) Error mapping: network errors, 408 and 5xx → `LLMTimeout`; 402 → `LLMAuth`; other 4xx (for example a content filter) → `LLMRefusal`. (3) The deepseek backend takes `[system, user]` only, until a task needs multi-turn; then `shared.chat` gains an optional `messages=` keyword (allowed by D22). (4) uv is the lock tool (`prototype/requirements.lock`, universal, hash-checked).
- **Consequences:** none beyond what T-003 shipped.

### D-043 · 2026-10-24 · PDF parsing: Docling (spike S2, T-006 PD-1…5)
- **Decision:** (1) Docling is the v1 parser: OCR off, table structure on, in the jobs loop, models baked into the image, one converter per worker. (2) A pypdfium2 text-layer check runs first: < 50 characters per page → status "scan", no model loaded. (3) No PyMuPDF in product code while it is AGPL-3.0. (4) At least 8 GB RAM and one parse at a time; before M2, measure peak memory and time a 300-page reading on the real host, and parse in page ranges if it misses the 300 s cap. (5) GROBID for reference metadata waits (TODOS #12).
- **Consequences:** reading-aid.md §3, TODOS updated. OL-045 (limitation remarks outside Discussion) stays open.

### D-044 · 2026-10-24 · Editor and replay rules (spike S1, PD-S1-1, 3…7; T-002 PD-1)
- **Decision:** (1) Node set: `doc`, `paragraph`, `heading` (1–3), `bullet_list`, `ordered_list`, `list_item`, `blockquote`, `hard_break`, `text`, plus marks `em` and `strong`; no tables, images, code, links or footnotes in v1. (2) The step log holds only primitive step types both replays know; the editor flattens `markSet`. (3) `doc_hash = sha256(canonical_json(doc.toJSON()))`. (4) `@tiptap/pm` 3.32.0 and prosemirror-py 0.6.1 are pinned as a pair and recorded in the engine stamp; upgrading either re-runs the S1 parity fixtures. (5) `input_kind` is what the browser reports; the replacement count is a lower bound and the receipt says "reported by the browser". (6) Playwright with a pinned Chromium joins CI at M3.
- **Consequences:** event-log.md §4/§5, receipt.md §6 (engine stamp) updated. Implemented in T-011 together with D-045, before any golden log exists (D33).

### D-045 · 2026-10-24 · Links to claims belong to paragraphs, not words (replaces S1 PD-S1-2 and T-002 PD-2)
- **Context:** Spike S1 proposed that typed words inside a linked sentence never carry the claim mark. The founder rejected it: adding "a" or "to", or a sentence of elaboration, shouldn't cut a link; an academic paragraph turns around one unit (claim, evidence, elaboration); word-level links stripe the text and read as micromanagement (law 3). Under the old rules, elaboration sentences with no claim mark also landed in "untraced", which inflates untraced for exactly the students who think while they write (and the H gate).
- **Decision:**
  - A link is an attribute of the paragraph: `links: [{claim_id, by, suggestion_id?}]`. A paragraph may link to several claims. The inline `claim` mark leaves the schema. Origin marks stay per character (law 7: record what changed in the text).
  - Typing, rewording or adding sentences inside a linked paragraph never changes its links; every sentence shares them, so elaboration counts as "linked by the student, not checked" (band 4), not untraced.
  - Links change only by an explicit student action or by structure: a split keeps the links on both halves, a new empty paragraph has none, a join keeps both sets.
  - A paragraph link alone never makes a sentence traced, whatever its `by`. D13 still applies per sentence: a sentence ≥ 50% `paste_ext` stays untraced, so a bulk outside paste into a linked paragraph is still shown.
  - No link breaks because of what a sentence means (that would need a model to rule on the student's text). L3b, if on, names an `added` proposition, which can only become a pillar question.
- **Consequences:** event-log.md §4, provenance.md §3/§4/§6, workspace.md (claim↔paragraph highlight, suggestions per paragraph; the "Not this" key is settled in M4m), architecture.md, build-plan.md, receipt.md, EXPECTATIONS (C, D, G) updated. Code: T-011 replaces the claim mark in `schema.json`, `schema.ts`, the input plugin and the S1 replay fixtures.

### D-046 · 2026-10-24 · Construction order is never a signal; elaboration is questioned forward, never traced back
- **Context:** An outside chat proposed a "source-first vs draft-first ratio" (did the card come before the paragraph, or was it added afterwards?). The founder rejected it: a scripted outside-AI workflow fakes the order (open a pin, make a card, then paste), and honest writers often find their structure while drafting. Elaboration raises the same problem: strong students elaborate without cards and often can't explain how; outside AI also writes elaboration; asking where it came from is over-accusation.
- **Decision:**
  - Construction order is never computed as a ratio, shown as a signal, or used to pick Coach or receipt questions. Dated thinking moments (provenance §7) stay as facts the student can point to.
  - Elaboration is taken at face value. The Coach and the receipt's "where to ask" questions test the idea forward through one of the four pillars, grounded in course material (D-038); never "how did you think of this?"
  - Coach outcomes (answered / revised / disagreed with a reason / declined) and the student's answer are recorded and shown as facts. Nothing grades whether an answer "resolved" the question: that would be a verdict (law 6); the teacher reads it.
  - **OL-043 answer:** we don't estimate an AI proportion. What tells trails apart is how the student engages with pillar questions, and then the conversation with the teacher (law 5).
- **Consequences:** provenance.md §5/§8 (two signals dropped), coach-helper.md §3, receipt.md §4, EXPECTATIONS E updated. OL-043 closed.

### D-047 · 2026-10-24 · The events layer for M1 (T-012 PD 1–7)
- **Decision:** accepted as built: (1) at most two `editor.batch` per 5-minute window when a checkpoint falls inside it; (2) events may precede the merged batch for their window; (3) a batch carries `base_rev` and the revision must follow on, else 409 `rev_conflict`; (4) one checkpoint per window and only when `doc_rev` changed, else `skipped`; (5) a retried submit with the same key returns the stored result even if the lease expired; (6) the 0-word block counts words on the server; (7) `/events` payload validation is added by each feature task.
- **Consequences:** event-log.md §5. The editor client must send `base_rev`. Auth, the jobs loop, the seal email and cancelling mapper jobs at submit are later tasks.

### D-048 · 2026-10-24 · Paragraph-link editing rules (T-011 PD 1–5; follows D-045)
- **Decision:** (1) A fragment pasted inside a non-empty paragraph leaves its links unchanged; whole pasted paragraphs keep their links; multi-paragraph pastes combine links where they join. (2) A paragraph deleted whole loses its links (undo restores them). (3) Headings carry no links. (4) External paste keeps bold and italic; the text stays `paste_ext`. (5) event-log.md §4 and §5 say so.
- **Consequences:** event-log.md §4. Known limits stay on the list: turning a linked paragraph into a heading drops its links; dragging part of a paragraph into an empty one does not carry links.

### D-049 · 2026-10-24 · Replay and the mark check (T-013 PD 1–8)
- **Decision:** (1) Replay starts at rev 0 from the empty document; (2) Coach-answer offsets are in code points and the client converts; (3) quotes match as substrings; (4) whitespace and quote characters are normalised for all four kinds (ligatures, soft hyphens and dashes later); (5) a Coach run must lie inside one typed range (fails closed); (6) reason codes stay internal, the chain view shows one plain sentence; (7) a stored browser snapshot that does not match its sent hash counts as a replay mismatch; (8) a minimal `operator_alerts` table until the operator page exists.
- **Consequences:** event-log.md §5.

### D-050 · 2026-10-24 · L1 provenance details; reference lists are "mechanics" (T-014 PD 1–11)
- **Context:** A sentence made only of Helper text (for example a formatted reference list) came out untraced, which inflates the untraced share for any student with a reference list.
- **Decision:** (1) Sentences made entirely of confirmed Helper text are left out of the word and claim counts and shown as "mechanics" (founder chose option b). Also accepted: (2) `via_ref` on card events and `import_id` on `claim.extracted` (fixture fields, added to the spec when the event payloads are validated); (3) a declared claim is re-anchored when a `claim.edit` gives it a live card anchored to a block; (4) any confirmed quote makes a clean sentence traced to its source; (5) an unconfirmed label counts like a paste for the 50% rule; (6) a map-suggestion link is never traced, even if L3b confirms it; (7) L3b `added` propositions also block the Coach band; (8) a claim unit takes the band with the most words, a tie going to the more cautious band; (9) headings are banded like any sentence; (10) the sentence-split rule is v1 and is tuned on the golden set; (11) the smaller choices (anchors accumulate, card "pasted" threshold, thinking-moment details) stay as built.
- **Consequences:** provenance.md §6 gets a "mechanics" line when T-016 lands; T-016 carries the change to the counts.

### D-051 · 2026-10-24 · Golden set sources (T-008)
- **Decision:** the golden corpus is three S2 papers (nursing, social science, CS, all CC BY 4.0) plus one Open Oregon textbook chapter (CC BY 4.0, original text only). OpenStax is excluded: its books are CC BY-NC-SA, and Biology 2e pages prohibit use in generative-AI offerings without written permission. Labels are `(paragraph_id, claim_id)` pairs (D-045). The 15 mapper-label seeds are drafts until a second person reviews them; holdout labels come from someone other than the prompt author (T-007 names that person).
- **Consequences:** prototype/fixtures/{sources.yaml, README.md, mapper_seed_labels.yaml}; evaluation.md §2/§2a. Licence checks were read from the publisher pages by the T-008 lead on 2026-10-24; I did not re-check them, so confirm the licences before the corpus is used outside the repo.

### D-052 · 2026-10-25 · Exact T-010 design candidate approved
- **Context:** The founder answered “A — Approve exact candidate” and subsequently authorized T-017 to proceed on that candidate so both branches could be reviewed together.
- **Decision:** Promote docs/designs/T-010-DESIGN.proposed.md unchanged to DESIGN.md. Approved tokens, Source Sans 3/Literata typography, focus, light/dark, patterns and motion rules govern receipt/workspace presentation.
- **Validation:** Both files SHA256 `08a1c28cf47d36610d8e1dc6c069665fd7572b603f1359cc8f51f50e20267d18`; format validator passes. Checker accepted T-010/T-017 engineering scope, not the human M1 gate or outstanding T-015/T-016 proposals.
- **Consequences:** design/workspace.md and design/build-plan.md no longer describe DESIGN.md as pending; index updated. Product intent and provenance rules unchanged.

### D-053 · 2026-10-25 · Receipt storage rules (T-018 PD 1–4)
- **Decision:** accepted as built: (1) the receipt key is `(log_id, seal_hash, version)` and the first issuance wins, also across a concurrent race with a different engine stamp; (2) mapper artifacts are supplied by the caller (`extra_artifacts`) until a mapper job stores them, and may never reuse a stored artifact id; (3) deletion removes receipt and artifact rows only and never touches the event chain (`record.withdrawn` records the choice); (4) two API tiers: `*_in_tx` joins a caller transaction, `store`/`delete_log` open their own and must not be nested.
- **Consequences:** T-020 passes mapper outputs through `extra_artifacts`; T-021 calls `delete_log_in_tx` inside the `record.withdrawn` transaction. Handoff: docs/handoffs/2026-10-25-T-018-receipt-storage.md.

### D-054 · 2026-10-25 · Job queue rules; retries stop after five tries (T-019 PD 1, 2, 8, 9)
- **Context:** D23 gives backoff 1/4/16 minutes but nothing ends retries. T-019 as built retries forever at 16 minutes.
- **Decision:** (1) **changes the built behaviour:** a job stops after its fifth try that ends in a retryable failure; it becomes `failed`, the receipt keeps those questions as "questions pending" (nothing invented), and an `operator_alerts` row is written. Expired-lease recovery does not count toward the five (the founder did not choose the option to count it). (2) One running job = one provider slot; handlers make at most one concurrent provider call. (8) Fairness is least-served submission first, not a strict ring. (9) Expired-lease recovery returns the job to `queued` with no backoff.
- **Consequences:** the cap is built inside T-020 (it owns the handlers, `compile_service.py` and the `operator_alerts` table; the queue change is a small `max_attempts` addition). T-019 PD 3–7 were not asked (OL-050).

### D-055 · 2026-10-25 · Drop "Written on N days" from the receipt (T-016 PD 5)
- **Context:** the summary counted distinct dates of `editor.batch`, a fact derived from edit timing. Law 7 records what changed, not how or when you typed; the pitch is thinking, never time.
- **Decision:** remove the clause from the receipt summary. No session, day or duration count appears in the summary.
- **Consequences:** receipt.md §2 and §8 examples no longer open with a session count. Code change is T-024 (`engine/receipt/copy.py`, the summary builder, golden receipts, the review README). T-016 PD 1–4 and 6–9 remain open in OL-047.

### D-056 · 2026-10-25 · S3 pass bar and labelling; band 4 is not traced in S4; provenance §5 follows §6 (T-007 PD 1, 2, 3, 5, 9)
- **Decision:** (1) S3 uses 48 evaluation + 12 development pairs and all five conditions of the S3 §11 bar as written (≥ 40 of 48 pairs scoreable and human-resolved; false-traced ≤ 10% with one-sided 95% Wilson upper ≤ 20%; false-added ≤ 15% with upper ≤ 35%; no family with ≥ 6 scoreable pairs above 25% error; both backends). s3-prereg-v1 keeps its version number. (2) One independent labeller who is neither the founder nor the prompt author, a 12-pair blind audit by a second independent annotator with Cohen's κ ≥ 0.60, and a third independent adjudicator. (3) Both `deepseek` and `openai_compat` must pass independently; one missing backend means S3 is incomplete and L3b stays off. (5) **Rejects the proposal:** S4's "C1 mostly traced" does **not** count band 4 (student-linked) as traced; C1 measures checked sources, Coach and declared only (D27). (9) provenance.md §5 now uses the §6 wording: an `added` proposition never changes the paragraph link but keeps the sentence out of bands 2 and 3.
- **Consequences:** S3 thresholds freeze at these values; a change needs a new preregistration version. `prototype/spikes/S4/PREREG.md` (s4-prereg-v1, §7.1) reads C1 the rejected way and needs a v2 before any S4 run (OL-051). A named second labeller is still owed (OL-051). T-007 PD 4, 6, 7, 8 and the S3 prompt are not yet decided (OL-050).

### D-057 · 2026-10-25 · Blind-question win rule (T-009 PD 1, 2, 9)
- **Decision:** "50-vs-50" means 50 essays with one platform-grounded and one essay-only question each (50 pairs). Platform-grounded wins only with ≥ 45 complete pairs, ≥ 15 discordant pairs, one-sided exact McNemar p < 0.05 and a paired Yes-rate difference ≥ +10 points (plus the missing-pair, compliance and leak guards in the preregistration). OL-047 stays open; the walkthrough uses the receipt as rendered.
- **Consequences:** docs/research/blind-question-preregistration.md is fixed at these values. T-009 PD 3–8 and 10 are not yet decided (OL-050).
