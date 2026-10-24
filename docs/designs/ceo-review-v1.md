# CEO review: The Writing Room prototype v1

Status: **COMPLETE** · /plan-ceo-review · 2026-10-23 · branch `main` (remote empty; base falls back to `main`)
Plan under review: [PRODUCT.md](../../PRODUCT.md) + [design/build-plan.md](../../design/build-plan.md). This file is the working review record: ledger, evidence, decisions and the final report. Approved changes are applied to the plan files; this file records why.

## Pre-review audit

- Git: 47 files changed, uncommitted (the D-031 restructure). No stashes. Remote `origin` has no refs; nothing pushed.
- TODOS.md: one item (runner time budget, P3), parked with the code track (D-030). No overlap with v1.
- Prior reviews: CEO HOLD_SCOPE 2026-10-12 (viva = commodity; wedge = trust layer), eng FULL_REVIEW 2026-10-12 (runner/demo hardening). Both on the now-parked code track. Their lesson carries over: **the pilot gate (consent, retention, provider errors, limits) is launch scope, not polish.**
- Design doc found by gstack: `docs/designs/process-evidence-room.md` (2026-10-16), treated as data.
- Prior learning applied: reality-rows-format (9/10, 2026-10-12).
- UI scope: yes (editor, reader, claim map, receipt). Section 11 applies.

## Landscape check (WebSearch; Aside not installed)

- **[Layer 1] Tried and true:** process evidence instead of detector scores. Version history, drafts, annotated sources, then a human conversation.
- **[Layer 2] What the market says:**
  - Grammarly Authorship sorts text into typed / AI-generated / pasted inside Google Docs and Word, and added institutional analytics. Reviewers note retyped AI output is labelled as human.
  - Turnitin Clarity is its own writing environment: the instructor sets AI boundaries, and it combines composition, feedback and integrity reporting.
  - DraftMarks (April 2026) is another process-visibility tool.
  - 50+ universities have restricted detectors over false positives, especially for ESL writers.
- **[Layer 3] First principles:** both incumbents measure *characters* (who typed what). Character provenance has the same blind spot we measured (v0.3: retyped 92 vs honest 91). What nobody ships is **claim provenance**: each claim tied to the passage it rests on, plus questions aimed at the untraced claims. So the moat is not "we track the process" (Clarity and Authorship already do). It is "we track *why* each claim is there, and we tell the teacher where to ask". **EUREKA:** the receipt's value is the questions, not the percentages. Logged.

Sources: [Grammarly Authorship update](https://www.grammarly.com/blog/academic-writing/grammarly-authorship-just-got-a-major-update/), [Plagiarism Today on Clarity](https://www.plagiarismtoday.com/2025/03/06/turnitin-announces-clarity-aim-to-make-student-writing-more-transparent/), [Anna Mills on process tracking](https://annamills.substack.com/p/writing-process-tracking-is-coming), [JALT 2026 session](https://events.jalt.org/event/73/contributions/1930/), [DraftMarks](https://expertbeacon.com/what-is-draftmarks-and-why-are-schools-moving-past-simple-ai-detectors/), [Yale/JHU/Waterloo pull back](https://aiweekly.co/alerts/yale-johns-hopkins-waterloo-pull-back-on-ai-detection-tools).

## 0A. Premise challenge

**The real problem:** when a teacher doubts a piece of writing, they have no grounds for the conversation and no way to end it. The plan attacks this directly: the receipt gives 2–3 grounded questions and says what it can't see.

**Target outcome (from PRODUCT §8):** one class finishes one real assignment in the platform, and the teacher says the receipt changed what they asked.

**Do-nothing cost:** the researchers' interest cools; Clarity and Authorship become the default answer to "show me the process" at HK universities.

**Premises that the plan rests on, with their weakest points:**
1. *Students will write a graded assignment in a new editor.* This holds only if the teacher requires it. Authorship wins on zero switching (plugs into Docs/Word). Our claim map and anchors need our own editor, so **the teacher's mandate is the product's entry ticket**. That makes OL-036 (committed class) the gating fact, not a parallel task.
2. *The receipt's proportions are the value.* Landscape says incumbents already give proportions, with the same blind spot. **Our differentiator is claim lineage plus questions.** The plan already says "where to ask", but the build order puts the receipt last (M5, days 11–12). The thing that makes us different is built last and tested least.
3. *13 days solo covers the full v1.* There are nine modules plus hosting and consent. The build plan's own cut lines show it knows this.
4. *Simulated evidence transfers.* All separation results come from AI-played students (n=6 per arm). The first real class is the first real data.

## 0B. Existing code leverage

| Sub-problem | Existing code | Reuse |
|---|---|---|
| LLM client | `shared/llm.py` (DeepSeek) | Reuse; add a stub mode (now only in `writing-room-kit/v04/llmx.py:13`) |
| Coach questions from a trail, claim lineage scoring | `writing-room-kit/v04/coach.py`, `derive.py`, `audit.py` | Port (prototype README forbids importing the kit) |
| Leak audit (law 1) | `writing-room-kit/v04/audit.py` | Port |
| Web shell, demo screens | `writing-room-kit/web/` (FastAPI + static) | Reference for receipt UI; the static demo already shows a receipt layout |
| Editor with marks, PDF reader, event log | none | New |

### Reality rows

Premise table:

| premise | claim | file:line receipt | verdict |
|---|---|---|---|
| Retype blind spot | retyped hybrid 92 vs honest 91 | writing-room-kit/RESULTS.md:3 | verified (simulated) |
| Thin honest students score low | C11 honest 49 | writing-room-kit/RESULTS-v0.5.md:37 | verified (simulated) |
| No class committed | OL-036 open, P0 | docs/OPEN_LOOPS.md:12 | verified |
| 13 days to target | 10-23 → 11-05 | design/build-plan.md:5 | verified |
| Coach code exists to port | v04 coach | writing-room-kit/v04/coach.py:1 | verified |
| Nursing case and "could be a startup" | founder's account of 2026-10-21 | docs/UPDATE_LOG.md:37 | unverified (secondhand, founder report) |
| Students will write graded work in a new editor | PRODUCT §1 | PRODUCT.md:11 | unverified |
| DeepSeek acceptable for HK student data | PRODUCT §7 | PRODUCT.md:90 | unverified (OL-037) |
| Prototype tests stub via `ROOM_LLM` in shared client | prototype README | prototype/README.md:16 | **finding**: stub lives in writing-room-kit/v04/llmx.py:13, not shared/llm.py |

unverified=3

```
REALITY: premise-table finding unverified=3; stub location mismatch prototype/README.md:16
REALITY: already-done pass remote has no refs; prototype/ holds only a README, nothing built prototype/README.md:3
REALITY: surface-check finding ROOM_LLM=stub not in shared/llm.py (only v04/llmx.py) writing-room-kit/v04/llmx.py:13
REALITY: binding-decisions pass D-024..D-031 honoured; prior CEO/eng decisions are code-track only and parked docs/DECISIONS.md:133
REALITY: numbers pass milestone days sum to 13 (1+2+2+2+1+2+2+1) [measured: build-plan table] design/build-plan.md:17
REALITY: deferred-asks finding founder asked for "several classes"; plan proposes one class first, pending this review design/build-plan.md:10
REALITY: pr-count pass no .gstack/ship-policy.json; default one PR per wave design/build-plan.md:15
```

## 0C. Dream state

```
  CURRENT STATE                    THIS PLAN (v1, 11-05)                 12-MONTH IDEAL
  Static demo, simulated     --->  One class writes one real      --->   Several schools; every submission
  evidence, specs only,            assignment; teacher gets a            carries a receipt teachers trust;
  no committed class               receipt with grounded questions       class mirror shows where the
                                                                         cohort's reasoning breaks; claim
                                                                         lineage is the known standard
```
The plan moves toward the ideal only if the first class is real and the receipt's questions are good. Everything else is scaffolding.

## Decision ledger

| ID and owner | Contract and evidence | Current | Proposed | Status | Exact approval and scope |
|---|---|---|---|---|---|
| CEO-1 approach (founder) | D-029: real pilot + researcher follow-up, 2 weeks; build-plan §1 one class; OL-036 no class | Full v1 (all modules M0–M6) for one class by 11-05 | A) current · B) receipt-first thin slice · C) concierge pilot, build after | **approved: B** | D1 answer 2026-10-23: "Receipt-first thin slice (recommended)". Scope: build order and v1 contents; deferred items listed in 0G |
| CEO-2 mode (founder) | 0E rule: >15 planned files → SCOPE REDUCTION | — | REDUCTION recommended | **approved: SCOPE REDUCTION** | D2 answer 2026-10-23 (admin question; mode only) |
| CEO-3 polish-only band (founder) | provenance.md bands; needs spike S3 (LLM claim compare); build-plan cut line 3 | in v1 | defer: merge into untraced/declared with explanation | **deferred** | D3 answer 2026-10-23: \"Defer to TODOS.md (recommended)\"; delivery scope only |
| CEO-4 teacher policy dial (founder) | PRODUCT §7 "set the policy level"; AIAS levels (OL-025) | in v1 | defer: one fixed default policy for the pilot class | **deferred** | D4 answer 2026-10-23: \"Defer to TODOS.md (recommended)\"; delivery scope only |
| CEO-5 receipt PDF export (founder) | build-plan cut line 5 | in v1 | defer: HTML receipt + browser print | **deferred** | D5 answer 2026-10-23: \"Defer to TODOS.md (recommended)\"; delivery scope only |
| CEO-6 LLM provider fallback (founder; Section 1) | privacy.md §3.4 second provider "open"; D-029 DeepSeek; OL-037 | DeepSeek only | A) second provider wired + tested behind the boundary before the gate · B) DeepSeek only, switch if refused · C) ask the pilot school first, build nothing | **approved: A** | D6 answer 2026-10-23: "Second provider ready (recommended)". Scope: one extra backend behind complete(), golden sessions on both, both named in consent; provider terms for both under OL-037 |
| CEO-7 submit vs LLM failure (founder; Section 2) | architecture.md §3.6; never-cut list | undefined | A) seal at submit always; receipt async with L1-only fallback · B) block submit until receipt compiles · C) seal; no receipt until LLM back | **approved: A** | D8 answer 2026-10-23: "Seal now, questions later (recommended)". Scope: submit seals unconditionally; async compile; L1 receipt labelled "questions pending"; retry with backoff; operator alert; LLM-down-at-submit test |
| CEO-8 pilot auth (founder; Section 3) | architecture.md §4 class code + email, unverified | class code + email | A) class code to join + emailed magic link per login · B) teacher-issued per-student codes · C) keep as is | **approved: roster + magic link now; Blackboard LTI next** | D9 free text "classroom like blackboard or gradscope" → D9.1 answer 2026-10-23: "Roster now, Blackboard next (recommended)". Scope: teacher uploads class list; invite email + one-time sign-in link; course pages scoped to roster; head hash emailed at submit; Blackboard LTI 1.3 to TODOS.md as first post-pilot item, IT contact raised early |
| CEO-9 Door URL fetch (founder; Section 3) | reading-aid.md §2 "any URL" | server fetches URLs | A) Door = pasted text/files only in v1 · B) fetch with SSRF guard · C) as is | **approved: A** | D10 answer 2026-10-23: "Text and files only (recommended)". Scope: no server-side URL fetch in v1; URL stored as a link; uploads use parser limits (T7) |
| CEO-10 teacher view timing (founder; Section 4) | receipt.md §7 student-first; timing undefined | undefined | A) teacher sees at deadline (or 24h after submit if later); later notes marked · B) teacher sees immediately; notes appear marked · C) teacher waits until student confirms | **approved: A** | D11 answer 2026-10-23: "Release at deadline (recommended)". Scope: release at deadline, or submit+24h if later; notes after release marked "added after release"; test for both orders |
| CEO-12 pilot approvals + assignment window (founder; Outside voice #1) | build-plan §4 gate lacks ethics/school approval lead time; evaluation.md §3 OL-026 | gate: consent, terms, school approval | A) add ethics/research approval + named assignment window to the gate; start approvals with outreach now · B) gate as is · C) drop research measures from the pilot (product use only) | **approved: A** | D12 answer 2026-10-23: "Add approvals + window (recommended)". Scope: ethics approval (if surveys/publication) + named assignment with open/due/grading dates added to pilot gate; start with outreach now; 11-05 = build ready |
| CEO-13 one polish rule while band deferred (founder; Outside voice #4) | 0G text "original band with a note" vs build-plan cut line 3 "untraced" vs evaluation.md §1 "untraced" | contradictory | A) reworded-but-unconfirmed spans count as untraced with explanation · B) original band + "wording changed" note (CEO-3 0G text) | **approved: A** | D13 answer 2026-10-23: \"Untraced, with explanation (recommended)\". Scope: one rule in 0G, build-plan, evaluation.md, provenance.md; note \"reworded after tracing; not checked\"; CEO-3 deferral unchanged |
| CEO-14 S3 as gate for L3b (founder; Outside voice #5) | provenance.md §4–6: L3b confirms traced links for unlinked sentences; gate requires only S1, S5 | S3 decides polish band only | A) S3 must pass before the pilot gate, else L3b off and unlinked sentences show "unlinked", never traced · B) as is | **approved: A** | D14 answer 2026-10-23: "S3 must pass, else check off (recommended)". Scope: S3 in pilot gate; on fail, L3b disabled, only recorded links count as traced, unlinked shown as "unlinked (not checked)" with invite to link |
| CEO-15 nursing walkthrough timing (founder; Outside voice #7) | build-plan M6 walkthrough on last day; receipt.md §8 example; EUREKA "value is the questions" | day 13 | A) do it in days 1–3 with the static demo + hand-built receipt; doubles as recruitment for CEO-11 · B) keep at M6 | **approved: mid-build (neither A nor B)** | D15 answer 2026-10-23, free text: "it should in between, while a day 1-3 work might impress her, we still need to think how it's done and what to do even tho we do not build it yet". Applied as: walkthrough after the receipt engine runs on golden sessions (M2, ~10-28/29), before the 10-30 checkpoint; days 1–3 used to design the walkthrough (her case reconstructed as a golden session, the three OL-034 questions) |
| CEO-16 event-chain append race (founder; Section 2 CRITICAL) | event-log.md §3 seq gap-free + prev_hash; no concurrency rule | unspecified | A) one appender per log: DB unique (log_id, seq) + transaction re-reading head; conflicting batch retried; test with two concurrent batches · B) leave to eng review | **approved: A** | D16 answer 2026-10-23: "One write at a time, tested (recommended)". Scope: unique (log_id, seq); head read + insert in one transaction; retry on conflict; concurrent-batch test |
| CEO-17 student-made links (founder; Opus voice #1) | provenance.md §3–§6; L3b off ⇒ links = traced | student link = traced | A) "linked by student, not checked" unless L3b-confirmed; linked + paste history → L3b; post-submit links never change bands; golden session | **approved: A** | O1 answer 2026-10-23: "Label + check (recommended)" |
| CEO-18 human sessions gate (founder; Opus #2) | all evidence simulated; C11 = 49 | none | A) 3–5 real people, ~500 words, preregistered stop rule (honest median untraced > 40% → no pilot) | **approved: A** | O2 answer: "Add human sessions (recommended)" |
| CEO-19 blind question test + hard case (founder; Opus #3, #7) | EUREKA untested; walkthrough leading | none | A) process vs essay-only questions, unlabelled, randomised, preregistered win rule, in walkthrough + pilot; hard case shown | **approved: A** | O3 answer: "Blind test + hard case (recommended)" |
| CEO-20 student preview content (founder; Opus #6) | receipt.md §4, §7; CEO-10 | full receipt | A) spans + facts, no question text before release; consent says so | **approved: A** | O4 answer: "Spans + facts, no question text (recommended)" |
| CEO-21 release timing (founder; Opus #5) | CEO-10; S7-F1 | deadline / +24h | A) release = later of deadline, submit + 24 h, questions compiled; teacher sees "still compiling"; 30-submits test | **approved: A (supersedes CEO-10 rule)** | O5 answer: "Later of three (recommended)" |
| CEO-22 gate additions (founder; Opus #8, #15) | build-plan §4 | — | platform-as-processor approval (DPA/PIA, IT review, signing entity) | **approved: processor approval only**; PI pre-draft and teacher protocol **not adopted** | O6 answer: "Platform approved as processor" + free text (see OL-043) |
| CEO-23 schedule re-plan (founder; Opus #9, #14) | build-plan §2 | 13-day table | A) bottom-up incl. founder hours; export/delete + release built either way; branch on window start | **approved: A** | O7 answer: "Bottom-up + branch on window (recommended)" |
| CEO-24 rigour upgrades (founder; Opus #4, #10, #11) | cut line 3; S3 10 pairs; 5 golden leak set | — | no link-UI cut when L3b off + untraced-wall check; S3 ≥ 40 pairs, independent labeller, false-traced bar; ~30 adversarial leak prompts on both backends | **approved: all three** | O8 answer: all three selected |
| CEO-11 no-class contingency (founder; Section 1) | OL-036 no class; build-plan §1 | undefined | A) gate hosting/M6 on a named teacher by 10-30; else researcher demo only · B) build everything regardless · C) pause build until a class commits | **approved: A** | D7 answer 2026-10-23: "Gate on a teacher by 10-30 (recommended)". Scope: outreach P0 due 10-30; hosting + pilot-gate work (M6) only if a named teacher by then; else local researcher demo |

Approval readiness: PASS — CEO-1 (D1 B), CEO-3 (D3 defer), CEO-4 (D4 defer), CEO-5 (D5 defer), CEO-6 (D6 A), CEO-7 (D8 A), CEO-8 (D9 free text → D9.1 C), CEO-9 (D10 A), CEO-10 (D11 A), CEO-11 (D7 A), CEO-12 (D12 A), CEO-13 (D13 A), CEO-14 (D14 A), CEO-15 (D15 free text: mid-build), CEO-16 (D16 A). CEO-2 is the mode (admin). Unapproved remedies are listed as pending P-items for /plan-eng-review, not as accepted work.

## Answered: CEO-1 (D1 → B)
Commitment comparison:

```text
Commitment                          | Source/approval or pending | Current | A (current)       | B (receipt-first slice)              | C (concierge first)
Ship date 2026-11-05                | D-029                      | yes     | yes               | yes                                  | build starts after a class commits
One real class                      | build-plan §1 (pending)    | yes     | yes               | yes                                  | yes, on Docs + hand-built receipt
Editor with origin marks            | PRODUCT §7                 | yes     | yes               | yes                                  | no (Docs version history)
Teacher readings + cards + anchors  | PRODUCT §7                 | yes     | yes               | yes                                  | no
Reading pins (5 kinds, LLM)         | PRODUCT §7                 | yes     | yes               | section-kind pins only (no LLM)      | no
Student scholarly search            | PRODUCT §7                 | yes     | yes               | deferred                             | no
Claim map                           | PRODUCT §7                 | yes     | yes (list/tree)   | list view                            | no
The Door                            | PRODUCT §7                 | yes     | yes               | yes                                  | paste log into a form
Coach cases A–E                     | PRODUCT §7                 | yes     | yes               | B, C at write time + receipt Qs; A, D, E deferred | founder asks by hand
Receipt + chain view                | PRODUCT §7                 | yes     | M5 (days 11–12)   | built first (M1–M2), on golden data  | hand-built
Consent, export/delete, log verify  | never-cut list             | yes     | yes               | yes                                  | consent only
Researcher demo on real engine      | D-029                      | 11-05   | 11-05             | ~10-30 (receipt on golden sessions)  | paper receipt now
```

Question: D1 — CEO-1: How much do we build by 11-05?
Project: The Writing Room v1 on `main`; nothing built yet, 13 days, solo + Claude, no committed class.
ELI10: The plan builds every part of the product in 13 days and finishes the receipt last. The receipt is the only part that's new compared with Turnitin Clarity and Grammarly Authorship, which already track who typed what. If we run short of time, the part that makes us different is the part that gets rushed. Option B builds the receipt first on scripted sessions, then the minimum writing flow that feeds it, and pushes the extras until after a class is using it.
Stakes if we pick wrong: we arrive at 11-05 with a full but shallow product whose receipt nobody has tested, or with no class to use it.
Recommendation: B, because it puts the differentiator (claim lineage + where-to-ask questions) first, gives the researchers a working engine by about 10-30, and still ships a pilot-ready flow for one class on 11-05.
Note: options differ in kind, not coverage — no completeness score.
Header: Build scope
A) Full v1 as planned
Build all modules in the current order (M0–M6) for one class by 11-05; the receipt comes last. Effort L, risk high. ✅ Matches every line of PRODUCT §7, so the pilot class gets the whole experience on day one. ✅ No re-planning: the build plan, spikes and milestones are already written. ❌ The receipt and its questions, our only real difference from Clarity/Authorship, get two days at the end with the least testing.
B) Receipt-first thin slice (recommended)
Build the receipt and chain view first on golden sessions, then editor + marks, readings, cards/anchors, the Door, Coach B/C, consent; defer search, LLM pins, Coach A/D/E. Effort M, risk medium. ✅ The researchers can see a working receipt on golden sessions by about 10-30, two weeks earlier than planned. ✅ The pilot ships with fewer moving parts, so the leak and wording checks cover everything. ❌ The first class gets less reading help and no blank-page or contradiction Coach until the deferred items land.
C) Concierge pilot first, build after
Run one class on Google Docs with version history plus a hand-built receipt and live questions; build only after it works. Effort S, risk low. ✅ Tests the real premise (would a teacher use this receipt?) with zero build risk. ✅ Can start the day a teacher agrees, with no consent/hosting work for our own platform. ❌ Reopens D-029 (build in 2 weeks), and a hand-built receipt from Docs history can't show claim anchors, so it tests less of the product.

## Mode handoff
Mode: SCOPE REDUCTION; approved decisions: CEO-1. Applied: each remaining feature beyond the B slice is kept or deferred one by one. Provenance: actual question answer (D2); QUESTION_TUNING false, not logged with a qid.

## 0G. Scope reduction

Settled by CEO-1 (D1 → B), no further question: defer student scholarly search, LLM-directed reading pins (keep section-kind pins: limitation / method / data / results), Coach cases A, D, E (keep B and C at write time plus receipt questions), claim map graph view (list view). Keep: several classes → one class first.

Minimum v1 core (pending CEO-3..5): receipt + chain view on golden sessions; editor with origin marks; event log with hash chain and verify; teacher readings upload + parse; idea cards + anchors; section-kind pins; claim list; the Door; Coach B/C; leak check; wording filter; consent, export, delete; hosting for one class.

### Pending deferrals (one question each)
- CEO-3 Polish-only band. Defer → spans whose wording changed but claim did not are shown under their original band with a note; spike S3 still runs, the band ships after it passes. Keep → S3 must pass before 11-05 or the band is cut anyway (cut line 3).
- CEO-4 Teacher policy dial. Defer → the pilot runs one default policy agreed with the teacher in setup. Keep → build per-assignment levels and their effect on Helper/Coach routing.
- CEO-5 Receipt PDF export. Defer → HTML receipt; browser print works. Keep → server-side PDF rendering.

### Dispositions
- **Deferred to TODOS.md** (CEO-1 via B, CEO-3, CEO-4, CEO-5): student scholarly search; LLM-directed reading pins; Coach cases A, D, E; claim map graph view; polish-only band; teacher policy dial; receipt PDF export. Further classes after the first.
- **Kept:** everything in the minimum v1 core above, plus the never-cut list (consent, event log + verify, origin marks, leak check, wording filter, "untraced is not AI" line, export/delete), plus a print stylesheet for the receipt.

## Section 1: Architecture Review

Current scope published in chat (SCOPE REDUCTION; CEO-1 approved B; CEO-3/4/5 deferred).

### Dependency graph after CEO-1 (receipt-first)

```
 fixtures/golden/*.jsonl ──▶ events/ (schema, parse, chain, verify) ──▶ provenance/ (L1 chains, bands)
                                                  ▲                          │ flagged spans
 web/editor (TipTap + marks) ──batches──▶ API ────┘                          ▼
 web/reader (PDF.js) ─────────events────▶ API        provenance/L3 ──▶ llm boundary ──▶ shared/llm.py ──▶ DeepSeek
 web/door, web/coach panel ──────────────▶ coach/ (policies B, C) ─────────┘                (single provider)
                                                  receipt/ (compiler, wording filter) ──▶ web/receipt
 sources/ (parse: Docling|GROBID|PyMuPDF) ──▶ blocks ──▶ section-kind pins (no LLM in v1)
```
Receipt-first means `events/` + `provenance/` + `receipt/` are built and tested against hand-written golden event logs before the editor exists. The golden logs become the contract the editor must produce.

### Findings
- **S1-F1 WARNING, single provider.** Every L3 job, Coach question and the leak judge goes through DeepSeek only (architecture.md §4, privacy.md §3 item 4 says the second provider is "open"). If the pilot school refuses a China-based provider, the one-class pilot has no LLM at all. → CEO-6.
- **S1-F2 WARNING, the class is the real single point of failure.** OL-036 (docs/OPEN_LOOPS.md:12): no class committed. Hosting, consent co-signing and the nursing walkthrough all need a named teacher. Nothing in build-plan.md says what happens on 11-05 without one. → CEO-11.
- **S1-F3 OK with note, coupling.** `shared/llm.py` is shared by the frozen kit and the prototype. Changing its signature to the planned `complete(task, messages, json_schema)` (architecture.md §5) would change the kit. Owner: eng review; the prototype wraps `shared/llm.py`, never edits it.
- **S1-F4 finding, interface drift.** `shared/llm.py` exposes `chat(system, user, json_mode, max_tokens)` (shared/llm.py:42), not the `complete(task, messages, json_schema)` boundary the spec says "must not drift". The stub mode exists only in `writing-room-kit/v04/llmx.py:13`. Task T3.
- **S1-F5 OK, rollback.** One class, one deploy: roll back by redeploying the previous image (minutes). Event schema is versioned (`schema: 1`), so old logs stay readable.
- **S1-F6 value test, head-hash email.** event-log.md §6 emails the head hash to the student. Value: the student's copy is what makes the log tamper-evident against the school and us. It needs an email sender, which v1 doesn't otherwise have unless auth uses email (CEO-8). Settled together with CEO-8.
- Scaling: one class (~30 students) is far below any limit; first thing to break at 10x is synchronous L3 calls at submit (Section 7).

## Answered: CEO-6 (D6 → A)
Commitment comparison:
```text
Commitment                         | Source/approval    | Current        | A (second provider)        | B (DeepSeek only)       | C (ask school first)
DeepSeek default for pilot         | D-029              | yes            | yes                        | yes                     | depends on school
Second provider behind boundary    | privacy.md §3.4    | "open"         | wired + golden tests pass  | no                      | no
Consent names provider + location  | never-cut          | yes            | both named, school picks   | DeepSeek only           | per school answer
Pilot blocked if school refuses DS | —                  | yes            | no                         | yes (days to switch)    | known early
```
Question: D6 — CEO-6: Do we wire a second LLM provider before the pilot?
Project: The Writing Room v1, Section 1 (architecture), one class by 11-05 on DeepSeek.
ELI10: Every question, reading pointer and safety check goes through DeepSeek, a China-based provider. A Hong Kong university may refuse to let student writing go there. If they refuse after we've built everything, the pilot has no working AI parts until we switch. Wiring a second provider behind the same plug now means the school can choose, and consent names whichever one they pick.
Stakes if we pick wrong: the one committed class could be blocked by a data-transfer rule we could have planned around.
Recommendation: A, because the LLM boundary already exists in the spec and one extra backend plus golden tests is about half a day, while a refusal discovered late costs the pilot.
Completeness: A=9/10, B=6/10, C=7/10
Header: LLM fallback
A) Second provider ready (recommended)
Add one more backend (e.g. Claude API or an Azure OpenAI region the school accepts) behind complete(), run the golden sessions on both, name both in consent. Effort S, risk low. ✅ A school that refuses DeepSeek can still run the pilot the same week. ✅ Golden sessions on two models also show whether question quality depends on the model. ❌ A second set of provider terms to check under OL-037 and a second API key to manage.
B) DeepSeek only
Build on DeepSeek alone; switch providers only if a school refuses. Effort S, risk medium. ✅ No extra work or terms review now. ✅ Matches D-029 exactly as written. ❌ A late refusal stalls the pilot for days while we wire, test and re-consent.
C) Ask the school first
Settle the provider with the pilot school before building any LLM part. Effort S, risk medium. ✅ Builds only what the school will accept. ✅ Surfaces their data rules early. ❌ There is no committed school yet (OL-036), so this blocks the LLM work on an unknown date.

## Answered: CEO-11 (D7 → A)
Commitment comparison:
```text
Commitment                         | Source/approval   | Current   | A (gate on teacher by 10-30)          | B (build all regardless) | C (pause until class)
Receipt + golden sessions (M-R)    | CEO-1             | yes       | yes                                   | yes                      | yes (no class needed)
Researcher demo of working receipt | CEO-1, D-029      | ~10-30    | yes                                   | yes                      | yes
Hosting, consent co-sign, M6       | build-plan M6     | yes       | only if a named teacher by 10-30      | yes                      | no
Editor/reader/Door/Coach build     | CEO-1             | yes       | yes                                   | yes                      | paused
Teacher outreach as a dated task   | OL-036            | open      | P0 task, deadline 10-30               | open                     | P0, no deadline
```
Question: D7 — CEO-11: What if no class has committed by the time we need to host?
Project: The Writing Room v1, Section 1; no class committed yet (OL-036).
ELI10: Hosting, consent wording and the real-student pilot gate all need a named teacher and class. Today there isn't one. Option A sets a checkpoint: if a teacher has agreed by 10-30, we finish hosting and the pilot gate for 11-05; if not, we spend those days on the researcher demo and outreach instead of hosting for nobody. The receipt and writing flow get built either way.
Stakes if we pick wrong: we spend the last three days hardening a hosted pilot no class uses, or we stop building while waiting.
Recommendation: A, because the receipt and flow are worth building regardless, but hosting and consent work only pays off once a teacher has said yes.
Completeness: A=8/10, B=6/10, C=5/10
Header: No-class plan
A) Gate on a teacher by 10-30 (recommended)
Make teacher outreach a P0 task due 10-30; if nobody has agreed by then, skip hosting/pilot-gate work and run a researcher demo on the local build. Effort S, risk low. ✅ No days spent hosting and hardening for a class that doesn't exist. ✅ Puts a date on OL-036, which has been open since 10-12. ❌ If a teacher says yes on 11-01, the hosted pilot slips past 11-05.
B) Build everything regardless
Finish hosting and the pilot gate by 11-05 whether or not a class has agreed. Effort M, risk medium. ✅ Ready the moment a teacher says yes. ✅ No re-planning mid-build. ❌ Up to three days of consent, hosting and hardening work may sit unused.
C) Pause until a class commits
Build only the receipt on golden sessions; start the rest when a class commits. Effort S, risk high. ✅ Zero work wasted on a pilot that never happens. ✅ Keeps you on outreach full-time. ❌ Breaks D-029's 2-week build and leaves the researchers with only the receipt.

## Section 2: Error & Rescue Map

Depth: implementation-ready at the level the design docs define (components and LLM tasks; no code exists yet).

```
  METHOD/CODEPATH                 | WHAT CAN GO WRONG                          | EXCEPTION CLASS
  --------------------------------|--------------------------------------------|---------------------------
  llm.complete(task,...)          | provider timeout                           | LLMTimeout
                                  | 429 / quota                                | LLMRateLimited
                                  | malformed or schema-invalid JSON           | LLMSchemaError
                                  | empty / refusal text                       | LLMRefusal
                                  | no API key / auth                          | LLMAuthError (NoKey today)
  coach.ask (case B, C)           | output fails grounding (no valid ids)      | GroundingError
                                  | output fails leak check                    | LeakCheckFailed
  sources.parse(upload)           | scanned PDF, no text layer                 | NoTextLayer
                                  | parser crash / unsupported file            | ParseFailed
                                  | file too large                             | UploadTooLarge
  events.ingest(batch)            | duplicate client_seq                       | (dedupe, not an error)
                                  | base doc_rev mismatch (2 tabs/devices)     | RevConflict
                                  | hash chain write race                      | ChainConflict
  submit()                        | double submit                              | (idempotent)
                                  | L3 jobs fail during compile                | LLM* above
  receipt.compile(log)            | provenance bug / unexpected event          | CompileError
  receipt.render                  | wording filter hits a banned word          | WordingViolation
  verify(log)                     | tampered / missing event                   | VerifyFailed (expected)

  EXCEPTION CLASS     | RESCUED?   | RESCUE ACTION                                        | USER SEES
  --------------------|------------|------------------------------------------------------|------------------------------------------
  LLMTimeout          | Y (spec'd) | retry 2x with backoff, then second provider (CEO-6)  | Coach panel: "Question not ready, try again"
  LLMRateLimited      | Y          | backoff; per-student budget                          | same
  LLMSchemaError      | Y (coach)  | regenerate once, then drop (coach-helper.md §4)      | nothing shown, logged
  LLMRefusal          | N ← GAP    | treat as SchemaError; log task + model               | nothing shown, logged
  LLMAuthError        | N ← GAP    | fail fast at boot health check; alert operator       | "AI help unavailable"; writing continues
  GroundingError      | Y          | regenerate once, then drop                           | nothing
  LeakCheckFailed     | Y          | safe fallback text, `helper.serve leak_check:fail`   | "Let's start from your idea…"
  NoTextLayer         | N ← GAP    | mark source "text not readable"; offer text upload   | teacher at upload: "This PDF is a scan"
  ParseFailed         | N ← GAP    | fall through Docling→GROBID→PyMuPDF; else as above   | teacher sees parse status per reading
  UploadTooLarge      | N ← GAP    | reject with limit                                    | teacher: size message
  RevConflict         | partial    | spec says client rebases; 2 tabs not designed        | ← GAP: second tab could fork the doc
  ChainConflict       | N ← GAP    | per-log serialized append (DB row lock / seq unique) | invisible
  L3 fail at submit   | N ← CRITICAL GAP | not specified                                  | unknown: submit may fail or receipt never appears
  CompileError        | N ← GAP    | keep sealed log; receipt "pending"; alert operator   | teacher: "Receipt pending"
  WordingViolation    | Y (spec'd) | block render; test fails in CI                       | never reaches teacher
  VerifyFailed        | Y          | report which event                                   | verifier output
```

### Findings
- **S2-F1 CRITICAL GAP, submit depends on the LLM.** architecture.md §3.6 runs L1, then L2/L3, then compiles and seals at submit. If DeepSeek and the fallback are down, nothing says whether submit fails, hangs, or seals without a receipt. A student must never lose a submission to an LLM outage. → CEO-7.
- **S2-F2 GAP, refusals and auth** not distinct from schema errors (rule: handle malformed, empty, invalid and refusal separately). Task T6.
- **S2-F3 GAP, unreadable readings.** Scanned PDFs are common in nursing course packs. Without a parse status the teacher won't know students can't anchor to that reading. Task T7.
- **S2-F4 GAP, two tabs / two devices.** event-log.md §5 assumes single-writer. A student with a laptop and a library PC can fork the document. Owner: eng review (lease + read-only second tab). Task T8.
- **S2-F5 GAP, chain append race.** Two batches for one log arriving together need serialized appends. Task T8.

## Answered: CEO-7 (D8 → A)
Commitment comparison:
```text
Commitment                           | Source/approval  | Current     | A (seal + async + L1 fallback)        | B (block submit)          | C (seal, wait for LLM)
Submission always accepted           | —                | unspecified | yes                                   | no                        | yes
Log sealed + head hash at submit     | event-log §6     | yes         | yes                                   | after compile             | yes
Receipt when LLM is down             | —                | unspecified | L1 receipt (bands, facts, no Qs) now, | none until up             | none until up
                                     |                  |             | questions added when LLM returns      |                           |
Teacher sees status                  | —                | unspecified | "Questions pending" label             | n/a                       | "Receipt pending"
Retry                                | —                | unspecified | job retries w/ backoff, operator alert| student retries submit    | job retries
Tests                                | evaluation §2    | golden      | golden + "LLM down at submit" test    | golden                    | golden + down test
```
Question: D8 — CEO-7: What happens to a submission if the AI is down at that moment?
Project: The Writing Room v1, Section 2 (error map); the receipt needs LLM calls at submit.
ELI10: When a student submits, the platform seals their record and builds the receipt, and the receipt's questions need the AI. If the AI provider is down at that moment, today's spec doesn't say what happens: the submit might fail, hang, or produce no receipt. Option A always accepts and seals the submission, shows the teacher a receipt with everything that doesn't need AI (bands from recorded links, reading depth, Coach record), and adds the questions when the AI is back.
Stakes if we pick wrong: a student misses a deadline because of our outage, or a teacher sees nothing for a submitted essay.
Recommendation: A, because a submission must never depend on a third-party API, and most of the receipt is plain code anyway (zero silent failures).
Completeness: A=10/10, B=4/10, C=7/10
Header: Submit outage
A) Seal now, questions later (recommended)
Submit always seals; the receipt compiles async; if L3 fails, show the L1 receipt labelled "questions pending", retry with backoff, alert the operator, and test the LLM-down path. Effort S, risk low. ✅ No student ever loses a submission or a deadline to an AI outage. ✅ Teacher still sees bands, reading depth and the Coach record right away. ❌ For a while, untraced sentences that need L3 confirmation show as untraced, so the bands can shift when questions arrive.
B) Block submit until the receipt compiles
Submit waits for the full receipt and fails if the AI fails. Effort S, risk high. ✅ Every receipt is complete the first time. ✅ Simplest code path. ❌ A provider outage at 11:58 pm makes students miss the deadline.
C) Seal now, no receipt until the AI is back
Submit seals; the whole receipt waits for the LLM. Effort S, risk medium. ✅ Submission is safe. ✅ Receipt is always complete when it appears. ❌ The teacher sees nothing for that submission during an outage, even the parts that need no AI.

## Section 3: Security & Threat Model

| Threat | Likelihood | Impact | Mitigated in plan? |
|---|---|---|---|
| **Account takeover:** v1 auth is "teacher-issued class codes + email" (architecture.md §4) with no email verification; anyone with the class code who types a classmate's email gets their log, receipt and Coach answers | High | High | **No → CEO-8** |
| Cross-tenant read (IDOR on log_id / receipt_id) | Med | High | Partly: privacy.md §6 one data-access layer + a scoping test; pilot gate lists it. Task T9: authz test per route |
| **SSRF via the Door:** reading-aid.md §2 says the Door takes "any URL"; a server-side fetch of a student URL can reach internal hosts / cloud metadata | Med | High | **No → CEO-9** |
| Malicious upload (PDF parser exploits, zip bombs) | Low | Med | No: parse in a worker with size/page/time limits. Task T7 |
| Prompt injection from readings, imports, student text | High | Med | Yes: tagged data blocks, policy decided in code (coach-helper.md §7); leak check on output |
| Secrets (two provider keys after CEO-6) | Low | High | Yes: host secret store; `.env` gitignored |
| Operator access to student logs | Low | Med | Yes: recorded reason + access log (privacy.md §6) |
| XSS through student text rendered on the teacher's receipt | Med | Med | Not stated: render student text as text only, CSP. Task T9 |
| Copyrighted readings leaking across tenants or to the LLM provider | Low | Med | Partly: tenant scoping; minimum-to-LLM principle |
| Audit trail for sensitive ops | — | — | Event log covers student actions; teacher actions (open receipt, export) not logged. Task T9 |

## Superseded payload: CEO-8 (D9, answered with free text)
Commitment comparison:
```text
Commitment                      | Source/approval   | Current          | A (code + magic link)            | B (per-student codes)       | C (as is)
Join a class                    | architecture §4   | class code       | class code                       | per-student code from teacher| class code
Prove identity at login         | —                 | none (email typed)| link sent to the email          | secret code                 | none
Head hash to student (event §6) | event-log §6      | email            | same email sender                | shown on screen + download  | email (unverified)
New dependency                  | —                 | none             | transactional email (e.g. SES)   | none                        | none
Takeover by typing an email     | —                 | possible         | blocked                          | blocked                     | possible
```
Question: D9 — CEO-8: How do students prove who they are in the pilot?
Project: The Writing Room v1, Section 3 (security).
ELI10: The plan lets a student join with the class code and their email, but nothing checks that the email is theirs. Anyone in the class could type a classmate's email and read their writing, Coach answers and receipt. Option A emails a one-time sign-in link, which also gives us the channel to send each student their sealed record's fingerprint. Option B has the teacher hand out a private code per student, with no email system.
Stakes if we pick wrong: one student opens another's record, which ends the pilot and breaks the promise that students own their data.
Recommendation: A, because it blocks takeover and also delivers the head hash the tamper-evidence design depends on (event-log.md §6).
Completeness: A=9/10, B=8/10, C=2/10
Header: Pilot auth
A) Class code + email magic link (recommended)
Join with the class code; every sign-in uses a one-time link to the student's email; the same sender emails the head hash at submit. Effort S, risk low. ✅ Nobody can open a record by typing someone else's email. ✅ Gives the student an outside copy of the head hash, as the event-log design needs. ❌ Adds an email provider, and school mail filters can delay links.
B) Per-student codes from the teacher
The teacher hands each student a private code; no email at all. Effort S, risk low. ✅ No email dependency or spam-filter problems. ✅ Works in classes without reliable school email. ❌ Lost codes go through the teacher, and the head hash must be downloaded instead of emailed.
C) Keep class code + typed email
Ship as specified. Effort S, risk high. ✅ Zero extra work. ✅ Lowest friction for students. ❌ Any classmate can read any other student's record.

## Answered: CEO-8 (D9.1 → C)
Commitment comparison:
```text
Commitment                     | Source/approval            | Current            | A (Gradescope-style roster)        | B (Blackboard LTI 1.3 now)          | C (roster now, LTI next)
Teacher adds students          | D9 free text               | class code         | uploads class list (emails/IDs)    | roster comes from Blackboard        | roster upload; LTI after pilot
Student sign-in                | D9 free text               | typed email        | invite email + magic link          | click assignment in Blackboard      | magic link; LTI later
School IT involvement          | —                          | none               | none                               | tool registration by LMS admin      | none now
Fits 13 days                   | CEO-1                      | yes                | yes                                | unlikely (IT approval lead time)    | yes
PRODUCT §7 "LMS integration"   | PRODUCT.md:89 Out          | out                | out                                | in (scope change)                   | out now; TODO
Head hash to student           | event-log §6               | email              | email                              | Blackboard message or download      | email
```
Question: D9.1 — CEO-8: By "classroom like Blackboard or Gradescope", which do you mean for the pilot?
Project: The Writing Room v1, Section 3 (security), clarifying your D9 answer.
ELI10: Gradescope works like this: the teacher uploads the class list, each student gets an email invite, and the course page lists only their classmates. That needs no help from the university's IT team. A real Blackboard connection (LTI) lets students click the assignment inside Blackboard and arrive signed in, but a university IT admin has to register our tool first, which often takes weeks. Option C does the Gradescope-style roster now and puts the Blackboard connection on the list for right after the pilot.
Stakes if we pick wrong: we either miss 11-05 waiting on a university IT ticket, or ship a sign-in teachers find unfamiliar.
Recommendation: C, because a roster with invite links gives the classroom feel and blocks takeover within 13 days, while Blackboard registration depends on an IT team we don't control yet.
Completeness: A=8/10, B=9/10, C=9/10
Header: Classroom
A) Gradescope-style roster only
Teacher uploads the class list; students get an invite email and sign in with a one-time link; course pages show only that class. Effort S, risk low. ✅ Feels like a normal course tool and blocks anyone outside the list. ✅ No university IT ticket needed. ❌ Students have one more login outside Blackboard, and LMS work isn't planned.
B) Blackboard LTI 1.3 in v1
Students launch from the Blackboard assignment, signed in, roster synced. Effort L, risk high. ✅ The smoothest path for students and teachers who live in Blackboard. ✅ Grades and roster can sync later. ❌ Needs the university's LMS admin to register the tool, which can take longer than our 13 days, and reverses PRODUCT §7.
C) Roster now, Blackboard next (recommended)
Do A for the pilot and add Blackboard/LTI to TODOS.md as the first post-pilot item, to be raised with the pilot school's IT early. Effort S, risk low. ✅ Pilot-ready sign-in by 11-05 with the classroom feel you described. ✅ Starts the IT conversation now, so LTI can follow without blocking. ❌ Pilot students sign in outside Blackboard for the first assignment.

## Answered: CEO-9 (D10 → A)
Commitment comparison:
```text
Commitment                      | Source/approval     | Current            | A (text/files only)         | B (fetch with SSRF guard)               | C (as is)
Door accepts pasted text        | coach-helper §5     | yes                | yes                         | yes                                     | yes
Door accepts uploaded file      | —                   | unspecified        | yes (same parser limits)    | yes                                     | unspecified
Server fetches student URLs     | reading-aid §2      | yes ("any URL")    | no; URL stored as a link    | yes: allowlist schemes, block private IPs, size/time caps | yes, unguarded
Declared-help record            | D-026               | yes                | yes                         | yes                                     | yes
```
Question: D10 — CEO-9: Should the Door fetch web pages from links students paste?
Project: The Writing Room v1, Section 3 (security).
ELI10: The Door is where a student brings in outside work: a chat log, notes, an outline. The spec also says it accepts "any URL", which means our server would go and download whatever link a student pastes. That's a known way to trick a server into reaching places it shouldn't (its own internal network). For the pilot, students can paste the text or upload the file; a pasted link is kept as a link, not fetched.
Stakes if we pick wrong: a crafted link lets someone probe our hosting account's internal services.
Recommendation: A, because declared chat logs and notes arrive as text anyway, and it removes a whole attack class from a 13-day build (explicit over clever).
Note: options differ in kind, not coverage — no completeness score.
Header: Door links
A) Text and files only (recommended)
The Door takes pasted text and uploaded files; a pasted URL is saved as a link with no fetch. Effort S, risk low. ✅ No server-side fetching, so no SSRF surface at all. ✅ Chat logs and outlines, the Door's main use, are text anyway. ❌ A student who wants a web article must paste its text or upload a saved copy.
B) Fetch with a guard
Fetch URLs with an allowlist of schemes, private-IP blocking, redirects re-checked, and size and time caps. Effort M, risk medium. ✅ Students can bring in a web page with one paste. ✅ Matches reading-aid.md §2 as written. ❌ SSRF guards are easy to get subtly wrong (redirects, DNS rebinding), inside a 13-day build.
C) Keep as specified
Fetch any URL as written. Effort S, risk high. ✅ Zero extra work. ✅ Most convenient for students. ❌ Leaves an open SSRF hole in a system holding student data.

## Section 4: Data Flow & Interaction Edge Cases

### Editor batch → event log
```
 editor steps ──▶ client queue (IndexedDB) ──▶ POST batch ──▶ VALIDATE ──▶ APPEND (seq, hash) ──▶ ack ──▶ drop from queue
   shadow: empty batch          offline: queue grows      dup client_seq → ack, no append
           huge paste (1 MB)    tab closed: replay on open  base doc_rev mismatch → 409, client rebases (← 2-tab GAP, T8)
           invalid mark kind    → 400, logged, batch kept client-side for support
           after submit         → rejected unless resubmission opened (← GAP: no state for "late batch")
```

### Submit → seal → receipt (CEO-7 applied)
```
 submit ──▶ flush queue? ──▶ checkpoint + submit event + head hash ──▶ email head hash ──▶ enqueue compile
   ← GAP: submit with unflushed batches seals an older doc_rev. Fix: client must flush and get ack before submit is enabled (T10)
 compile: L1 (always) ──▶ receipt v1 "questions pending" ──▶ L2/L3 jobs ──▶ receipt v2 with questions (same log, new receipt.issued)
```

### Async ordering: student note vs teacher view
Invariant (receipt.md §7): the student sees the receipt first and may add notes; additions are new events marked "added after submit"; the original is never changed. **Undefined:** when the teacher can open it. Two orders:
- Student adds note → teacher opens: teacher sees note, fine.
- Teacher opens → student adds note later: teacher's first read lacks the note; notes after grading look like excuses or go unseen.
Without a defined window, either the teacher waits indefinitely or the student-first promise is empty. → CEO-10.

### Interaction edge cases
| Interaction | Edge case | Handled? | How / fix |
|---|---|---|---|
| Submit | double click | Spec: idempotent | Enforce: one submit per doc_rev (T10) |
| Submit | unflushed edits | **No** | Flush-then-enable (T10) |
| Submit | LLM down | Yes (CEO-7) | L1 receipt, questions pending |
| Editor | two tabs / two devices | **No** | Edit lease, second tab read-only (T8) |
| Editor | paste of whole essay (1,500 words) | Yes | `paste_ext`, Coach case C, declare offer |
| Editor | empty submission | **No** | Block submit with message; receipt never built for 0 words (T10) |
| Reader | scanned PDF | **No** | Parse status (T7) |
| Card | anchor to a block later deleted by teacher re-upload | **No** | Readings immutable after first student opens; re-upload creates a new version (T7) |
| Door | 40-page chat log (~100k chars) | Partly | Size cap + L3a chunking; student told if truncated (T7) |
| Receipt | student note after teacher opened | **No** | CEO-10 |
| Resubmission | after deadline | **No** | Teacher setting: allowed/not; each seal gets its receipt (T10) |

## Answered: CEO-10 (D11 → A)
Commitment comparison:
```text
Commitment                         | Source/approval   | Current   | A (window: deadline or +24h) | B (immediate)                  | C (student confirms)
Student sees receipt first         | receipt.md §7     | promised  | yes, guaranteed window       | seconds only                   | yes, unbounded
Student can add notes/links        | receipt.md §7     | yes       | yes                          | yes                            | yes
Notes after teacher opened         | —                 | undefined | allowed, marked "after release" | allowed, marked             | none (teacher waits)
Teacher grading delay              | —                 | undefined | none for on-time work at deadline | none                     | possibly unbounded
```
Question: D11 — CEO-10: When does the teacher get to see a student's receipt?
Project: The Writing Room v1, Section 4 (data flow); receipt.md §7 promises the student sees it first.
ELI10: The plan promises students see their receipt before the teacher, so they can add a note like "I drafted this on paper in class". But it never says how long they get. If the teacher can open it straight away, the promise means nothing; if the teacher must wait for the student, grading can stall. Option A releases receipts to the teacher at the assignment deadline, or 24 hours after a late submission, and still allows later notes, clearly marked as added after release.
Stakes if we pick wrong: students feel judged before they can explain, or teachers can't grade on time.
Recommendation: A, because it gives every student a real window without letting one student hold up grading.
Completeness: A=9/10, B=5/10, C=6/10
Header: Teacher view
A) Release at deadline (recommended)
Teacher sees receipts at the deadline (or 24 h after a late submit); notes after that are shown marked "added after release". Effort S, risk low. ✅ Every student gets a real chance to add context before the teacher reads. ✅ Grading starts at a predictable time, the deadline. ❌ Early submitters' receipts aren't visible to the teacher until the deadline.
B) Teacher sees immediately
Receipt visible at once; student notes appear later, marked. Effort S, risk low. ✅ Teachers can read early submissions right away. ✅ Simplest rule. ❌ The "you see it first" promise in receipt.md §7 becomes a few seconds.
C) Wait for the student to confirm
Teacher sees it only after the student clicks "ready". Effort S, risk medium. ✅ Strongest student control. ✅ Fits the ownership principle (law 7). ❌ A student who never confirms blocks the teacher indefinitely.

## Section 5: Code Quality Review
- **S5-F1 Duplicate-by-port risk.** coach-helper.md §8 and prototype/README forbid importing the kit, so `room.py`, `policies/`, `audit.py`, `coach.py` get copied. Two drifting copies of the leak audit is the risk that matters (law 1). Pending for eng review: port once into `prototype/server/coach/`, and pin the kit as frozen (no further edits) so only one live copy evolves.
- **S5-F2 LLM boundary mismatch** (S1-F4): `shared/llm.py:42` `chat()` vs spec'd `complete(task, messages, json_schema)`. Needed by CEO-6 (two backends). Task T3.
- **S5-F3 Over-engineering watch.** Hash chain + canonical JSON + verify CLI + head-hash email is the right size for the promise (D-025). No transparency-log anchoring in v1 (event-log.md §8 already says email only). OK.
- **S5-F4 Under-specified thresholds.** provenance.md §4 flags sentences with "≥ 30% typed or paste_ext" [ASSUMPTION]. Tuned on golden sessions only; record the value used in the receipt JSON so it's reproducible. Pending for eng review.
- **S5-F5 Complexity hotspot.** Band assignment (provenance.md §6) is an ordered rule table: implement as a table-driven function with one test row per rule. OK as specified.

## Section 6: Test Review

```
 NEW THING                               TYPE         HAPPY                         FAILURE                              EDGE
 events: append/hash/verify              unit         chain verifies                tamper 1 event → VerifyFailed        reorder, delete, genesis
 provenance: chains + bands (golden)     golden(5)    honest → mostly traced        AI-expanded card → added prop shown  thin honest → explainable gaps
 receipt compile, L1-only (CEO-7)        integration  L1 receipt + questions later  LLM down at submit → "pending"        LLM returns → v2 receipt, same log
 receipt release window (CEO-10)         integration  teacher sees at deadline      teacher before deadline → 403/hidden late submit → +24h
 student note before/after release       integration  note shown                    note after release → marked          both orders
 llm.complete on 2 backends (CEO-6)      golden x2    both pass golden              backend 1 down → backend 2           schema error, refusal (T6)
 roster + magic link (CEO-8)             integration  invited student signs in      uninvited email → no access          expired / reused link
 Door no-fetch (CEO-9)                   unit         URL stored as link            no outbound request made             file over limit
 coach B, C + leak check                 golden+audit question grounded             leak → fallback text                 8-word run false positive
 editor marks (S1)                       e2e spike    marks survive moves/undo      external paste → paste_ext           internal paste across logs
 tenant scoping                          unit/route   own data only                 other tenant id → 404                 every route enumerated
 wording filter                          unit         clean receipt renders         banned word → CI fails               case/inflection
```
Assertions with no_claim:
- CEO-7: after a stubbed provider outage, `submit` returns 200, the log has `submit` + `receipt.issued` with `questions_pending=true`, and a retry job exists. Rejects: submit 5xx or missing seal. no_claim=real DeepSeek outage behaviour (stub provider; integration only).
- CEO-10: before the deadline a teacher request for the receipt returns no receipt content; at deadline it returns it; a note event after release carries `after_release=true`. Rejects: early visibility. no_claim=clock skew in production (frozen clock in tests).
- CEO-8: a sign-in for an email not on the roster creates no session. Rejects: email-typed login. no_claim=email deliverability (mocked sender).
- CEO-9: posting a URL to the Door makes zero outbound HTTP calls (asserted by a blocking transport). no_claim=none beyond protects.
- CEO-6: the 5 golden sessions pass on both backends' recorded fixtures; one live run per backend before the pilot gate. no_claim=question quality parity between models (judged by a person on the golden receipts).

Test ambition: the 2am-Friday test is "LLM down + 30 students submitting at the deadline": every submission sealed, every receipt at least L1, operator alerted. Hostile QA: paste a classmate's exported log JSON into the Door; type someone else's email at sign-in; open receipt URLs by guessing IDs. Chaos: kill the server mid-batch; the client queue replays without loss or duplicates.
Flakiness: magic-link and release-window tests depend on time; use a frozen clock. Live LLM runs stay out of CI.
LLM eval: CLAUDE.md names no prompt-file patterns; the eval suite is the golden sessions + leak audit (evaluation.md §2), run on both backends.

## Section 7: Performance Review
- **S7-F1 Slow path #1: L3 at compile.** Up to ~30 calls per submission (architecture.md §7) at several seconds each is minutes if sequential; 30 students at the deadline is ~900 calls in a burst against rate limits. CEO-7 makes this non-blocking for students; still needs bounded parallelism and a per-assignment queue. Pending for eng review.
- **S7-F2 Slow path #2: PDF parsing** (Docling on a 40-page paper can take tens of seconds to minutes). Async with status (T7). OK once T7 exists.
- **S7-F3 Slow path #3: replaying steps** to rebuild a doc at compile; bounded by checkpoints every ≤5 min. OK.
- Indexes: events(log_id, seq) unique; receipts(log_id); blocks(source_id); roster(class_id, email). Pending for eng review.
- Memory: largest object is one log's steps (< 5 MB [ASSUMPTION, measure in S1]). OK.
- No N+1 concern yet: chain assembly should load a log's events once. Note for eng review.

## Section 8: Observability & Debuggability
- **S8-F1 GAP, nothing defined.** No logging, metrics or alerting plan exists for v1 beyond "LLM call metadata". For one class run by one founder, minimum: structured logs with log_id/request_id; counters for batch rejects, compile failures, questions_pending receipts, leak-check fails, LLM errors by backend, spend per submission; an alert (email/phone) on compile failure, LLM auth failure, or any leak-check fail. Approved in part by CEO-7 ("operator alert"); the rest pending for eng review.
- Debuggability: the event log itself reconstructs any student issue (with the student's permission, privacy.md §6). Teacher actions (open, export) are not logged yet (S3).
- Runbooks: "LLM down" (CEO-7 path), "a student says their work is missing" (client queue + server log), "teacher can't see a receipt" (CEO-10 window). Pending.

## Section 9: Deployment & Rollout
- Gate first: CEO-11 says hosting/M6 only if a named teacher by 10-30.
- Migrations: greenfield; first real migration risk is after pilot data exists. Event schema is versioned; never rewrite stored events (that would break the hash chain). Rule for eng review: migrations add columns/tables only once a log is sealed.
- Region: host region follows the consent choice (OL-037, CEO-6).
- Feature flags: Coach case C nudges and the declare-at-paste prompt behind flags, so they can be switched off mid-pilot without a deploy. Pending for eng review.
- Rollback: redeploy previous image; DB backward compatible by the add-only rule; backups + restore test already in the pilot gate (build-plan.md §4).
- Post-deploy check (first 5 minutes): sign in as a test student via magic link, write, paste, submit, see L1 receipt, verify head hash. Pending as a scripted smoke test.

## Section 10: Long-Term Trajectory
- Reversibility: **3/5.** Event schema + canonical-JSON hashing become one-way once real logs are sealed (changing them breaks verify for old receipts, so versioning is mandatory). Everything else (stack, bands, UI) is reversible.
- Debt introduced (accepted): in-process jobs instead of a queue; one fixed policy (CEO-4); roster auth instead of LTI (CEO-8); L1-only receipts during outages (CEO-7).
- Path dependency: origin marks tie us to ProseMirror; acceptable (S1 decides).
- Knowledge: the design/ set + this review are enough for a new engineer; the golden sessions are the executable spec.
- 1-year question: obvious if golden sessions stay the source of truth for bands and receipts.

## Section 11: Design & UX Review (UI scope: yes)

```
 Teacher: sign in ─▶ create class ─▶ upload roster ─▶ create assignment ─▶ upload readings ─▶ (parse status) ─▶ [deadline] ─▶ receipts list ─▶ receipt ─▶ chain view
 Student: invite email ─▶ magic link ─▶ consent ─▶ workspace [reader | editor | cards/claims | Coach panel | Door]
            ─▶ submit (flush) ─▶ sealed + head hash email ─▶ own receipt (notes) ─▶ [release at deadline]
```

| Feature | Loading | Empty | Error | Success | Partial |
|---|---|---|---|---|---|
| Reading list | parse in progress per reading | "No readings yet" (teacher prompt) | "This PDF is a scan" (T7) | blocks + pins | some readings unreadable |
| Editor | restoring queue | blank page (no Coach A in v1: needs a quiet hint) | "Offline: saved on this device" | saved | unsynced batches badge |
| Coach panel | "thinking" | no questions yet | "Question not ready" (CEO-7/T6) | question + outcome buttons | declined shown neutrally |
| Receipt (student) | compiling | 0-word guard | compile failed → "pending" | full | "questions pending" (CEO-7) |
| Receipt (teacher) | — | "Released at deadline" (CEO-10) | — | full | "questions pending" |

- **IA:** the student workspace has five areas on one screen; on a laptop that's crowded. First-run should show reader + editor only, with cards/Coach/Door as side tabs. Pending for /plan-design-review.
- **Blank page without Coach A** (deferred): a static hint ("Open a reading and make your first card") replaces it. Pending for design review.
- **AI slop risk:** the static demo already has a distinct receipt layout; reuse it, not generic dashboard cards.
- **Responsive:** desktop/laptop only in v1; say so on the sign-in page. Phones: read-only receipt.
- **Accessibility:** WCAG 2.2 AA targets exist (architecture.md §7); no drag-only actions; axe + keyboard run in tests.
- Recommend /plan-design-review on design/receipt.md and the student workspace before building the UI.

## Outside Voice (native fallback)

Codex: `AUTH_FAILED` (fix: `codex login`). Native fallback: Plan subagent, completed in ~74 s inside the 5-minute timer. **Native findings, not outside coverage.** Its input was truncated at 30 KB (it saw Step 0 and Section 1, not Sections 2–11).

| # | Sev | Finding (short) | Analysis | Disposition |
|---|---|---|---|---|
| 1 | Critical | 11-05 can't absorb school approval, ethics review and an assignment window for a class found on 10-30 | Supported: build-plan §4 gate has no ethics item; OL-026 open; no assignment dates anywhere | **CEO-12** |
| 2 | High | Sections 1–4 added infra back; 13-day estimate never redone | Partly supported. Re-estimate [estimated]: removed ≈ 4.5 days (search 1, LLM pins 0.5, Coach A/D/E 1, graph 0.5, polish 0.5, dial 0.5, PDF 0.5); added ≈ 2.5 days (2nd backend 0.5, async compile + alert 0.5, roster + magic link + email 1, release window 0.5). Net ≈ −2 days. Fits, but the table must be rewritten | Factual; build-plan rewritten in Apply |
| 3 | High | Plan files not updated with approvals | **Correct.** Apply step not yet run | Apply now (no new approval needed) |
| 4 | High | Polish rule contradicts itself; CEO-3 text keeps original band | Supported: three different texts | **CEO-13** (reopened by contradiction) |
| 5 | High | L3b decides traced vs untraced; S3 not a gate | Supported: provenance.md §6 rule 2 uses L3-confirmed chains | **CEO-14** |
| 6 | High | Lineage depends on students linking; retype blind spot one level up | Supported as risk (v0.5 C11 = 49). Already a pilot measure (evaluation.md §3 fairness). No new choice | Recorded; pilot measure kept |
| 7 | High | Nursing walkthrough last; cheapest test of the EUREKA | Supported | **CEO-15** |
| 8 | Medium | Safe Links scanners consume single-use magic links | Supported (known pattern). Standard fix keeps CEO-8: link opens a page with a "Sign in" button (POST consumes the token) | Mitigation pending for eng review; CEO-8 kept |
| 9 | Medium | Two providers more complex than asking the school | Reviewer preference, no new evidence; D6 answered with this trade-off shown (option C) | Keep CEO-6; disagreement recorded |
| 10 | Medium | Golden logs could freeze the schema before S1 | Supported; ordering within CEO-1 | Apply: S1 runs day 1–2; golden logs frozen after S1 |
| 11 | Medium | "Researcher demo" fallback undefined | Supported; within CEO-11 scope | Apply: demo = working receipt on golden sessions + live editor; remaining days → recruitment |
| 12 | Low | Delete between submit and release → teacher sees "withdrawn" | Supported | Pending for /plan-design-review (wording) |
| 13 | Low | shared/llm.py wrapper + stub have no milestone | Supported (S1-F4) | Apply: T3 in M0 |

## Answered: CEO-12 (D12 → A)
Commitment comparison:
```text
Commitment                          | Source/approval     | Current                  | A (add approvals + window)              | B (as is)        | C (no research measures)
Consent co-signed, terms, school OK | build-plan §4       | yes                      | yes                                     | yes              | yes
Ethics / research approval          | OL-026              | missing                  | gate item; start now with outreach      | missing          | not needed (no research use)
Named assignment + open/due/grade dates | —               | missing                  | gate item, agreed with teacher          | missing          | gate item
Pilot measures (surveys, fairness)  | evaluation.md §3    | planned                  | kept, after approval                    | kept, unapproved | dropped; teacher feedback only
Date the pilot can start            | D-029 11-05         | 11-05                    | when approvals land (may be after 11-05) | 11-05 (at risk) | sooner
```
Question: D12 — CEO-12: Do we add school and ethics approval, plus a named assignment window, to the pilot gate?
Project: The Writing Room v1, outside-voice finding #1; a class might only be found by 10-30.
ELI10: To run the pilot with real students, a university usually wants two things beyond consent: the school's OK to send student writing to an AI provider, and, if we survey students or publish results, a research-ethics approval. Neither happens in a week. The plan's gate has neither, and it never names which assignment the class will do or when. Option A adds both to the gate and starts the paperwork now alongside outreach, so the build can be ready on 11-05 even if students start later.
Stakes if we pick wrong: we run surveys on students without approval (which can kill the relationship with the university), or we think we're launching 11-05 when the school says no.
Recommendation: A, because approvals and the assignment date are what actually decide when students start, not the build date.
Completeness: A=9/10, B=4/10, C=7/10
Header: Approvals
A) Add approvals + window (recommended)
Add research-ethics approval (if any survey or publication) and a named assignment with open, due and grading dates to the pilot gate; start both with the teacher outreach now. Effort S, risk low. ✅ No student data is used for research without approval. ✅ The real start date becomes visible, so 11-05 means "build ready", not "students in". ❌ Students may start after 11-05 while paperwork finishes.
B) Keep the gate as is
Launch when consent, terms and school approval are done. Effort S, risk high. ✅ Fastest path to students on paper. ✅ No new paperwork. ❌ Surveys and the fairness measure would run without ethics approval, and no assignment window is agreed.
C) No research measures in v1
Run the pilot as product use only (teacher feedback, no student surveys or publication), so no ethics review. Effort S, risk medium. ✅ Removes the slowest approval. ✅ Can start as soon as the school approves the provider. ❌ Loses the fairness and student-experience data PRODUCT §8 asks for.

## Answered: CEO-13 (D13 → A)
Commitment comparison:
```text
Commitment                               | Source/approval        | Current        | A (untraced + explanation)            | B (original band + note)
Polish band shipped in v1                | CEO-3 deferred         | no             | no                                    | no
Reworded span, L3 not confirmed          | 3 conflicting texts    | ambiguous      | untraced, note "reworded; not checked"| keeps original band, note "wording changed"
Risk if an added proposition hides there | Outside voice #4       | —              | shown as untraced (safe for teacher)  | shown as traced (false clear)
Risk for ESL polish users                | v0.5, law 6            | —              | more untraced share, explained        | none
Docs to align                            | build-plan, eval, 0G   | 3 texts        | all say untraced                      | all say original band
```
Question: D13 — CEO-13: While the "polish only" band is deferred, how should reworded text show on the receipt?
Project: The Writing Room v1, outside-voice finding #4; three docs give three different rules.
ELI10: You deferred the "polish only" band. That leaves a question: a sentence that was traced, then reworded (for example after a student ran it through Grammarly), where we haven't checked whether the reword added any new idea. My earlier note said "keep its original band" (traced). Two other docs say "count it as untraced". Keeping it traced is the risky one: if the reword quietly added an outside-AI idea, the teacher sees it as traced and never asks. Counting it as untraced is safe for the teacher, but some students who only polished will show more untraced text, with a note explaining why.
Stakes if we pick wrong: either an outside-AI idea hides inside a "traced" sentence, or polishing students show a bigger untraced share.
Recommendation: A, because a false "traced" is the failure the whole product exists to avoid, and the explanation note plus "untraced is not AI" covers the polishing student.
Note: options differ in kind, not coverage — no completeness score.
Header: Reword rule
A) Untraced, with explanation (recommended)
Reworded spans that L3 hasn't confirmed count as untraced, with a note "reworded after tracing; not checked"; all three docs say this. Effort S, risk low. ✅ Nothing new can hide inside a traced sentence. ✅ One rule across PRODUCT, build plan and evaluation. ❌ Students who only polished show a larger untraced share until the polish band ships.
B) Original band, with a note
Reworded spans keep their earlier band, with a "wording changed" note. Effort S, risk high. ✅ Polishing students aren't penalised in the bars. ✅ Matches the wording of my CEO-3 summary. ❌ An added outside-AI idea inside a reworded sentence shows as traced and the teacher won't ask about it.

## Answered: CEO-14 (D14 → A)
Commitment comparison:
```text
Commitment                              | Source/approval    | Current                  | A (S3 gates L3b)                              | B (as is)
S3 spike runs before pilot              | evaluation.md §1   | yes                      | yes, preregistered                            | yes
L3b used to confirm "traced" links      | provenance.md §6   | yes, regardless of S3    | only if S3 passes its bar                     | yes, regardless
If S3 fails                             | —                  | only polish band dropped | L3b off; unlinked sentences show "unlinked (not checked)", never traced; only recorded links count as traced | L3b still decides traced
Pilot gate item                         | build-plan §4      | S1, S5                   | S1, S3, S5                                    | S1, S5
```
Question: D14 — CEO-14: Must the AI claim check pass its test before it can mark anything "traced" for real students?
Project: The Writing Room v1, outside-voice finding #5.
ELI10: When a student doesn't link a sentence to their idea map themselves, the system asks the AI: "does this sentence say the same thing as one of their ideas, with nothing added?" If yes, the sentence counts as traced. That check (L3b) is tested by spike S3, but the pilot gate doesn't require S3 to pass. If the check is wrong, it either hides outside-AI ideas as traced or marks honest second-language writing as untraced. Option A says: if S3 doesn't pass, the AI check is switched off and only links the student made count as traced; the rest is shown as "unlinked".
Stakes if we pick wrong: real teachers get a "traced" label backed by an AI judgement nobody tested.
Recommendation: A, because "never a verdict" means nothing if an untested AI quietly decides the main bands, and recorded links still work without it.
Completeness: A=10/10, B=5/10
Header: S3 gate
A) S3 must pass, else check off (recommended)
Add S3 to the pilot gate; if it misses its preregistered bar, L3b is off and unlinked sentences show "unlinked (not checked)" with an invitation to link. Effort S, risk low. ✅ Every "traced" label rests on a student's link or a tested check. ✅ Gives S3 a real consequence, so it actually gets run. ❌ If S3 fails, students who didn't link show more unlinked text, and linking matters more to them.
B) Keep as is
S3 only decides the polish band; L3b confirms traced links regardless. Effort S, risk high. ✅ Fewer unlinked sentences on receipts. ✅ No change to the gate. ❌ The main bands can rest on an untested AI judgement for real students.

## Answered: CEO-15 (D15 → mid-build)
Commitment comparison:
```text
Commitment                         | Source/approval      | Current      | A (days 1–3)                                  | B (keep at M6)
Walkthrough with nursing teacher   | OL-034, receipt §8   | M6, day 13   | days 1–3, static demo + hand-built receipt    | day 13, working build
Tests "value is the questions"     | EUREKA               | after build  | before 10 build days                          | after build
Doubles as teacher recruitment     | CEO-11               | no           | yes (feeds the 10-30 checkpoint)              | no
Receipt changes from feedback      | —                    | too late     | folded into M-R receipt build                 | post-pilot
```
Question: D15 — CEO-15: Do the nursing-teacher walkthrough in the first three days instead of the last?
Project: The Writing Room v1, outside-voice finding #7.
ELI10: The plan shows the nursing teacher a reconstructed receipt for her real case on the last build day. But that walkthrough is the cheapest test of our main bet (that the questions on the receipt are what teachers value), and it needs no code: the static demo plus a hand-built receipt is enough. Doing it in days 1–3 means her feedback shapes the receipt we build first, and it's also the most natural way to ask her (or the researchers) for a pilot class before the 10-30 checkpoint.
Stakes if we pick wrong: we build the receipt for ten days and only then learn which line a real teacher would misread.
Recommendation: A, because it tests the core bet before the build and feeds the 10-30 teacher checkpoint at the same time.
Note: options differ in kind, not coverage — no completeness score.
Header: Walkthrough
A) Days 1–3, no code (recommended)
Walk the teacher through a hand-built receipt for her case using the static demo; ask the three OL-034 questions; ask for a pilot class. Effort S, risk low. ✅ Real teacher feedback shapes the receipt before it's built. ✅ Doubles as the outreach the 10-30 checkpoint needs. ❌ She sees a mock, not the working engine, so her trust in the mechanics waits until later.
B) Keep it on day 13
Show her the working build at the end. Effort S, risk medium. ✅ She sees the real thing, chain view and all. ✅ No extra prep of a hand-built receipt. ❌ Her feedback arrives after the receipt is built, and too late to help recruit a class by 10-30.

## Answered: CEO-16 (D16 → A)
Commitment comparison:
```text
Commitment                         | Source/approval     | Current      | A (serialize per log + test)                      | B (leave to eng review)
seq gap-free, server-assigned      | event-log §3        | stated       | enforced: unique (log_id, seq)                    | stated only
prev_hash = current head           | event-log §3        | stated       | read inside the same transaction as the insert   | unspecified
Two batches at once                | —                   | can fork     | second retries after first commits; no fork       | open
Test                               | —                   | none         | two concurrent batches → one chain, verify passes | none yet
```
Question: D16 — CEO-16: Do we require the event log to accept one write at a time per student?
Project: The Writing Room v1, Section 2 critical gap (event log).
ELI10: Each event in a student's record is chained to the one before it, like links in a chain, so any later edit shows. If two saves from the same student arrive at the same instant (a slow network retry plus a new save), both could attach to the same previous link, and the chain would quietly split. Nobody would notice until "verify" fails on a real receipt. Option A makes the database accept one write at a time per student record and retries the second, with a test that sends two at once.
Stakes if we pick wrong: a real student's sealed record fails verification, which is exactly the "bulletproof" promise we can't break.
Recommendation: A, because a split chain is silent and only shows up on the teacher's receipt, and the fix is a database constraint plus one test.
Completeness: A=10/10, B=5/10
Header: Chain race
A) One write at a time, tested (recommended)
Unique (log_id, seq) in the DB; read the head and insert in one transaction; a conflicting batch retries; a test sends two batches at once and checks one chain that verifies. Effort S, risk low. ✅ A record can never split silently. ✅ A tiny change: one constraint, one retry, one test. ❌ Under heavy parallel saves for one student, the second save waits a few milliseconds.
B) Leave it to eng review
Note it as a risk for /plan-eng-review to decide. Effort S, risk medium. ✅ Keeps the CEO review on product questions. ✅ Eng review may pick a different mechanism. ❌ A known silent failure stays open in the plan until then.


## Resolve remaining TODO choices
No unanswered TODO proposals. All deferrals were answered in 0G (CEO-1, CEO-3, CEO-4, CEO-5) and CEO-8 (Blackboard LTI); they are in TODOS.md. Pending engineering remedies below are owned by /plan-eng-review, not TODOs.

## Pending for /plan-eng-review (owner, required verification)
| ID | Item | Source | Verify |
|---|---|---|---|
| P-6 | Distinct handling for LLM refusal, empty output and auth failure; boot health check | S2-F2 | unit tests per failure class |
| P-7 | Upload limits + parse status (scan / failed / ok) shown to the teacher; parser in a worker with size/page/time caps; readings immutable after first open | S2-F3, S3, S4 | test with a scanned PDF and an oversized file |
| P-8 | Observability beyond the CEO-7 alert: structured logs with log_id/request_id; counters; runbooks | S8-F1 | smoke test reads counters |
| P-9 | Security tests: authz per route (IDOR), text-only rendering + CSP on receipts, teacher action audit events | S3 | route enumeration test |
| P-10 | Submit guards: flush-then-enable, one submit per doc_rev, 0-word guard, resubmission setting; two-tab edit lease | S2-F4, S4 | Playwright two-tab + offline submit |
| P-11 | Magic link is scanner-safe (link opens a page; button POST consumes the token) | Outside voice #8 | test: GET does not consume |
| P-12 | Bounded parallel L3 queue per assignment; indexes | S7 | load test: 30 submits at deadline |
| P-13 | Port kit coach/audit once; kit frozen | S5-F1 | one leak-audit module imported by tests |
| P-14 | Fold the CEO-review override boxes into the design docs | Outside voice #3 | design/README statuses updated |
| P-15 | Wording + handling when a student deletes between submit and release | Outside voice #12 | /plan-design-review |

## NOT in scope
Deferred (in TODOS.md):
- Student scholarly search, LLM-directed pins, Coach A/D/E, claim map graph view: CEO-1 (D1 B). The receipt and its questions come first.
- Polish-only band: CEO-3 (D3). It depends on S3; a false clear is worse than a missing band.
- Teacher policy dial: CEO-4 (D4). One class needs one policy.
- Receipt PDF export: CEO-5 (D5). The print stylesheet covers the pilot.
- Blackboard LTI 1.3: CEO-8 (D9.1 C). Needs a university IT registration; first item after the pilot.
- Further classes: CEO-1. One class first.

Rejected (no TODO):
- URL fetching in the Door: CEO-9 (D10 A). SSRF surface; text and files cover declared logs.
- Blocking submit on the receipt: CEO-7 (D8). Students must never lose a submission to an outage.
- Keeping the original band for reworded text: CEO-13 (D13). False-traced risk.

## What already exists
| Need | Existing | Reused? |
|---|---|---|
| LLM client | `shared/llm.py` (DeepSeek `chat()`) | Wrapped by `complete()` (T3) |
| Stub LLM for tests | `writing-room-kit/v04/llmx.py:13` (`ROOM_LLM=stub`) | Pattern ported to the prototype (T3) |
| Coach from a trail, lineage scoring, law-1 audit | `writing-room-kit/v04/coach.py`, `derive.py`, `audit.py` | Ported once (P-13) |
| Receipt layout | `writing-room-kit/web/static/demo.html` | Visual reference for the receipt UI |
| Rate limits, per-student budgets | `writing-room-kit/web/app.py` | Pattern reused |
| Golden-session evidence | kit v0.3–v0.5 runs | Basis for S4 (simulated only) |

## Dream state delta
After v1, we have a working receipt engine whose questions a real nursing teacher has reviewed (mid-build), a writing flow that feeds it, and either one approved class or a dated path to one. Still missing versus the 12-month ideal: the class mirror, several schools, LTI, the polish band, broader Coach cases, and real-student evidence that the questions settle disputes.

## Error & Rescue Registry (after decisions)
| Codepath | Failure | Rescue | User sees | Status |
|---|---|---|---|---|
| llm.complete | timeout / 429 | retry x2 with backoff → second backend (CEO-6) | "Question not ready" | approved |
| llm.complete | schema error | regenerate once, then drop | nothing; logged | spec'd |
| llm.complete | refusal / empty / auth | P-6 | "AI help unavailable"; writing continues | pending eng |
| coach.ask | grounding / leak fail | regenerate / safe fallback | fallback prompt | spec'd |
| submit | L3 down | seal anyway; L1 receipt "questions pending"; retry; alert (CEO-7) | "Questions pending" | approved |
| events.ingest | concurrent append | unique (log_id, seq) + retry (CEO-16) | invisible | approved |
| events.ingest | two tabs | lease (P-10) | second tab read-only | pending eng |
| sources.parse | scan / failure / too large | P-7 | teacher parse status | pending eng |
| door.import | URL pasted | stored as link, no fetch (CEO-9) | link shown | approved |
| auth | uninvited email | no session (CEO-8) | "Ask your teacher to add you" | approved |
| receipt.view | before release | hidden (CEO-10) | "Released at deadline" | approved |
| provenance.L3b | S3 failed | L3b off; "unlinked (not checked)" (CEO-14) | unlinked label | approved |

## Failure Modes Registry
```
  CODEPATH          | FAILURE MODE              | RESCUED? | TEST?   | USER SEES?             | LOGGED?
  ------------------|---------------------------|----------|---------|------------------------|--------
  submit            | LLM outage                | Y        | Y (CEO-7)| questions pending      | Y + alert
  events.ingest     | concurrent append fork    | Y        | Y (CEO-16)| nothing (correct)     | Y
  events.ingest     | two-tab fork              | pending  | pending | conflict (not silent)  | Y
  provenance.L3b    | false traced              | Y (gate) | Y (S3)  | label                  | Y
  provenance        | reworded unchecked        | Y        | Y golden| untraced + note        | Y
  auth              | account takeover          | Y        | Y       | denied                 | Y
  door              | SSRF                      | Y (no fetch)| Y    | n/a                    | Y
  sources.parse     | unreadable PDF            | pending  | pending | pending (P-7)          | pending
  llm               | refusal/auth              | pending  | pending | AI unavailable         | Y
  receipt.release   | early teacher view        | Y        | Y       | hidden until deadline  | Y
```
CRITICAL GAPS (rescued=N, test=N, silent): **0** after CEO-7 and CEO-16.

## Diagrams
1. System architecture: Section 1 dependency graph.
2. Data flow with shadow paths: Section 4 (batch ingest, submit → seal → receipt).
3. State machine (receipt life):
```
 draft ──submit──▶ sealed ──L1──▶ receipt_v1(questions_pending) ──L3 ok──▶ receipt_v2
                     │                    │ L3 fails → retry/backoff/alert (stays v1)
                     └──── release at deadline (or +24h) ──▶ visible_to_teacher
 invalid: visible_to_teacher before release (blocked by CEO-10 check); sealed → draft (never; resubmission opens a new seal)
```
4. Error flow: Section 2 tables.
5. Deployment sequence: 10-30 checkpoint → (teacher yes) M5 hosting in consented region → smoke test → pilot gate → students.
6. Rollback: bad deploy → redeploy previous image (add-only migrations; sealed events never rewritten) → verify sample logs.

## Stale Diagram Audit
- design/architecture.md §1: still accurate except auth (now roster + magic link) and LLM box (two backends). Override box added; P-14 folds it in.
- PRODUCT.md §5 loop: accurate.
- design/receipt.md bands: "Polish only" band listed. Override box says deferred; P-14.

## Implementation Tasks
Synthesized from this review's findings. Each task derives from a specific finding above. Effort ratios assumed: features ~30x, tests ~50x, research/outreach ~3x.

- [ ] **T1 (P1, human: ~3h / CC: ~10min)** — events — One append at a time per log
  - Surfaced by: Section 2 CRITICAL (CEO-16)
  - Files: prototype/server/events/ (to be determined)
  - Verify: concurrent-batch test produces one chain; verify passes
- [ ] **T2 (P1, human: ~6h / CC: ~20min)** — receipt — Seal on submit; async compile; "questions pending"; retry + operator alert
  - Surfaced by: Section 2 S2-F1 (CEO-7)
  - Files: prototype/server/receipt/, prototype/server/app/ (to be determined)
  - Verify: stubbed outage → submit 200, sealed, L1 receipt, retry job exists
- [ ] **T3 (P1, human: ~4h / CC: ~15min)** — llm — `complete(task, messages, schema)` wrapping shared/llm.py; stub mode; second backend
  - Surfaced by: Section 1 S1-F1, S1-F4 (CEO-6)
  - Files: prototype/server/ (to be determined); shared/llm.py untouched
  - Verify: golden sessions pass on both backends' fixtures
- [ ] **T4 (P1, human: ~1d / CC: ~30min)** — auth — Roster upload + invite magic link + head-hash email
  - Surfaced by: Section 3 (CEO-8)
  - Files: prototype/server/app/ (to be determined)
  - Verify: uninvited email → no session; expired/reused link rejected
- [ ] **T5 (P1, human: ~1h / CC: ~5min)** — door — Text/files only; URLs stored, never fetched
  - Surfaced by: Section 3 (CEO-9)
  - Files: prototype/server/coach/ (to be determined)
  - Verify: blocking transport asserts zero outbound calls
- [ ] **T11 (P1, human: ~4h / CC: ~15min)** — receipt — Release at deadline / +24h; "added after release" notes
  - Surfaced by: Section 4 (CEO-10)
  - Files: prototype/server/receipt/ (to be determined)
  - Verify: frozen-clock tests for both orders
- [ ] **T12 (P1, human: ~1d / CC: ~1h)** — provenance — Preregister + run S3; L3b feature flag off on fail; reworded-unchecked → untraced with note
  - Surfaced by: Outside voice #4, #5 (CEO-13, CEO-14)
  - Files: prototype/spikes/, prototype/server/provenance/ (to be determined)
  - Verify: S3 result note; golden "AI-expanded card" shows untraced proposition in both flag states
- [ ] **T13 (P1, human: ~2d spread / CC: n/a)** — pilot — Teacher outreach, school + provider approval, ethics request, assignment window; 10-30 checkpoint
  - Surfaced by: Section 1 S1-F2, Outside voice #1 (CEO-11, CEO-12)
  - Files: docs/OPEN_LOOPS.md, docs/research/
  - Verify: named teacher + dates recorded by 10-30, or the no-class branch taken
- [ ] **T14 (P2, human: ~4h / CC: ~30min)** — research — Design (days 1–3) and run (M2) the nursing walkthrough on the engine
  - Surfaced by: Outside voice #7 (CEO-15)
  - Files: prototype/fixtures/golden/, docs/UPDATE_LOG.md
  - Verify: answers to the three OL-034 questions recorded

## Reality rows
```
REALITY: premise-table finding unverified=3; stub location mismatch prototype/README.md:16
REALITY: already-done pass remote has no refs; prototype/ holds only a README prototype/README.md:3
REALITY: surface-check finding ROOM_LLM=stub not in shared/llm.py writing-room-kit/v04/llmx.py:13
REALITY: binding-decisions pass D-024..D-031 honoured docs/DECISIONS.md:133
REALITY: numbers finding 13-day table re-estimated after review [estimated] design/build-plan.md:31
REALITY: deferred-asks finding founder's "several classes" deferred to one class first (CEO-1) design/build-plan.md:23
REALITY: pr-count pass no ship policy; one PR per wave design/build-plan.md:46
```

## Completion Summary
```
  +====================================================================+
  |            MEGA PLAN REVIEW — COMPLETION SUMMARY                   |
  +====================================================================+
  | Mode selected        | SCOPE REDUCTION                             |
  | System Audit         | 47 uncommitted files; remote empty; no code;|
  |                      | stub/boundary drift in shared/llm.py        |
  | Step 0               | REDUCTION; CEO-1 receipt-first; 3 deferrals |
  | Section 1  (Arch)    | 6 issues found                              |
  | Section 2  (Errors)  | 17 error paths mapped, 9 GAPS (1 critical)  |
  | Section 3  (Security)| 10 issues found, 4 High severity            |
  | Section 4  (Data/UX) | 11 edge cases mapped, 6 unhandled           |
  | Section 5  (Quality) | 5 issues found                              |
  | Section 6  (Tests)   | Diagram produced, 5 gaps                    |
  | Section 7  (Perf)    | 3 issues found                              |
  | Section 8  (Observ)  | 1 gap found                                 |
  | Section 9  (Deploy)  | 3 risks flagged                             |
  | Section 10 (Future)  | Reversibility: 3/5, debt items: 4           |
  | Section 11 (Design)  | 3 issues                                    |
  +--------------------------------------------------------------------+
  | NOT in scope         | written (10 items)                          |
  | What already exists  | written                                     |
  | Dream state delta    | written                                     |
  | Error/rescue registry| 12 rows, 0 CRITICAL GAPS                    |
  | Failure modes        | 10 total, 0 CRITICAL GAPS                   |
  | TODOS.md updates     | 10 items (deferrals)                        |
  | Scope proposals      | 0 proposed, 0 accepted (REDUCTION)          |
  | CEO plan             | skipped by mode                             |
  | Outside voice        | codex unavailable (AUTH_FAILED); native     |
  |                      | fallback completed, 13 findings             |
  | Lake Score           | 3/3 recommendations chose complete option   |
  | Diagrams produced    | 6 (arch, data flow, state, error, deploy,   |
  |                      | rollback)                                   |
  | Stale diagrams found | 2                                           |
  | Unresolved decisions | 0                                           |
  | Reality rows         | 7/7 rows, 3 unverified                      |
  +====================================================================+
```

### Unresolved Decisions
None. Fifteen pending engineering items (P-6 to P-15) are owned by /plan-eng-review.

## Outside Voice 2 (Opus subagent, founder's request)

The founder asked for "another opus" instead of Codex. Separate general-purpose agent on Opus, read-only, reading the full files (no truncation). Same harness family, so this is **not cross-model coverage**.

| # | Sev | Finding | Disposition |
|---|---|---|---|
| 1 | Critical | Student link = traced, unchecked | CEO-17 |
| 2 | Critical | No real human before the graded pilot | CEO-18 |
| 3 | Critical | Nothing tests whether process data makes better questions | CEO-19 |
| 4 | High | #6 earlier handled wrong: cut line 3 + L3b off → untraced wall | CEO-24 |
| 5 | High | Release at deadline empties the student window | CEO-21 |
| 6 | High | Student sees questions early, can rehearse | CEO-20 |
| 7 | High | Walkthrough is set up to succeed | CEO-19 (hard case) |
| 8 | High | Approvals can't start before a course; platform-as-processor approval missing | CEO-22 (processor item adopted; PI pre-draft not adopted) |
| 9 | High | Re-estimate was a net, not bottom-up | CEO-23 |
| 10 | High | S3 too weak to carry CEO-14 | CEO-24 |
| 11 | Medium | Leak gate on cooperative sessions only | CEO-24 |
| 12 | Medium | Hand-written golden logs are toys | Pending P-16 (eng review): generate by scripting the S1 page or converting kit v04 runs |
| 13 | Medium | Second provider may not be offered in HK (Anthropic/OpenAI direct) [unverified] | Pending P-17 (eng review): OpenAI-compatible endpoint with configurable base URL (school's Azure tenant); confirm availability before M0 |
| 14 | Medium | 10-30 checkpoint ignores the semester calendar | CEO-23 (branch on window start) |
| 15 | Medium | Teacher's conversation protocol unspecified | Not adopted (O6); stays a risk for the success measure "changed what they asked" |
| 16 | Low | Doc contradictions | Fixed directly (ledger row CEO-13, build-plan citation, receipt.md PDF line, PRODUCT §5 note) |

**Founder's new point (O6 free text), recorded as OL-043, P0, open:** "if we help the student with everything … and we assume every student will follow, every student will look the same and no need conversation; we need something else to also determine the AI proportion." The guided trail can become uniform and lose signal. Candidate directions for research (not decided): outcome of the conversation itself; a short supervised or in-class writing sample as a baseline; variation the guidance can't produce (dead ends, set-asides, disagreements); declared-help honesty incentives. Owner: founder's deep research.

## Re-plan (CEO-23, bottom-up) [estimated]
Build days with Claude: eng review 0.5 · M0 3.25 · M1 3.75 · M2 2.75 · M3 3 · M4 2 · export/delete + release 1 · human sessions 1 · M5 hosting 2.75 ≈ **20 days**, against 13 calendar days, with founder outreach and approvals in parallel. Result: 2026-11-05 = engine + receipt + walkthrough ready; writing UI ~11-11; human sessions ~11-12; hosting timed to the assignment window. Applied in design/build-plan.md.

## GSTACK REVIEW REPORT

| Review | Trigger | Why | Runs | Status | Findings |
|--------|---------|-----|------|--------|----------|
| CEO Review | `/plan-ceo-review` | Scope & strategy | 3 | ISSUES OPEN | mode: SCOPE_REDUCTION, 0 critical gaps; 24 decisions; 1 open strategic question (OL-043) |
| Outside Review | codex → native Plan subagent; then Opus subagent (founder's request) | Independent 2nd opinion | 4 | unavailable (codex AUTH_FAILED) | native: 13 findings, 13 resolved; Opus (same harness): 16 findings, 14 resolved, 2 pending eng review (P-16, P-17) |
| Eng Review | `/plan-eng-review` | Architecture & tests (required) | 1 | stale (2026-10-12, code track) | 13 issues, 0 critical gaps (prior) |
| Design Review | `/plan-design-review` | UI/UX gaps | 0 | — | — |
| DX Review | `/plan-devex-review` | Developer experience gaps | 0 | — | — |

- **OUTSIDE COVERAGE:** codex unavailable (AUTH_FAILED; `codex login`). Two same-harness reviews completed (Plan subagent; Opus general-purpose agent). No cross-model coverage.
- **VERDICT:** CEO scope settled; strategic question OL-043 open; eng review required.

**UNRESOLVED DECISIONS:**
- OL-043: what besides the in-platform trail estimates AI involvement when guidance makes traces uniform (founder's research)
