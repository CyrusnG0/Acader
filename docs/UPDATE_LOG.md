# Update Log

Append-only session journal. **Newest entry on top.** One entry per working session.
Template:

```
## YYYY-MM-DD — <short title>
**Summary:** what was done and why (2–5 lines)
**Files touched:** …
**Loops:** opened OL-xxx … / closed OL-xxx …
**Decisions:** D-xxx … (if any)
**Next:** the single most important next step
```

---

## 2026-10-16 — Writing Room kit executed (v0.2 experiment)
**Summary:** CLEAR meeting delayed (founder ill). Read and ran `writing-room-kit/` (founder's AI-brainstormed test module). Review found the v0.1 test was circular (prompts set paste/burst counts; the outsourced arm was guaranteed to lose; retrievals self-declared). Built tooling (`librarian.js`, `finalize.js`, `validate.js`, `outside.py`, `engine.js`, `export-corpus.js`, score upgrades with `--by-arm`, AUC, no-structure composite), pre-registered the analysis, generated 36 runs over 6 arms (24 Sonnet workers, 12 mechanical, DeepSeek as the outside writer), scored. v0.2 result: primary AUC 0.83 but driven by a harness artifact (outside essays capped at 6 citations). Fixed and re-run as v0.3 (PREREG-v0.3.md): retyped hybrid scores 92 vs honest 91, primary AUC 0.33, so the receipt does not separate them. Supports law 5 (the conversation is the gate).
**Files touched:** `writing-room-kit/` (PLAN.md, PREREG.md, RESULTS.md, scripts/*, claude-prompts/ rewritten, v0.1 prompts archived to `_v0.1-superseded/`, runs/, work/); `docs/OPEN_LOOPS.md`; `docs/STATUS.md`; `CHANGELOG.md`.
**Loops:** opened OL-027 to OL-030; closed OL-028.
**Decisions:** none (OL-027 proposes one).
**Next:** decide OL-027 after the rescheduled CLEAR meeting; fix the kit artifact (OL-028) before showing numbers to anyone.

## 2026-10-14 — Proposal v2 fact-check → v3 (process-as-proof + teacher mirror)
**Summary:** Fact-checked ultimate-proposal-v2.md for the CLEAR meeting (2026-10-16). Verified: Davalos & Zhang and DraftTrace papers exist; NYU $15/36 includes grading but validity is not established; UNESCO quote is a guest article. Broke: Clarity already shows instructors AI chat activity ("Layer 4 empty" is false); no evidence the Meter can read ChatGPT Edu via API, and CUHK seems to use its own chatbots + Copilot; a typed unsupervised Room can be proxied live. Founder clarified the real backbone (staged, course-grounded, AI does legwork and asks; gaps become conversations) and the teacher mirror. Wrote v3. Earlier this session: research report on AI-era understanding assessment tools.
**Files touched:** `ultimate-proposal-v3.md` (new), `docs/{DECISIONS,OPEN_LOOPS,STATUS,UPDATE_LOG}.md`, `CHANGELOG.md`; earlier: `reports/AI era understanding assessment tools.md`, `research_notes/AI era understanding assessment tools/` (new).
**Loops:** opened OL-022 to OL-026. **Decisions:** D-023 (candidate).
**Not done:** eng-review D13 ("interviews first") still not written into the eng-review doc; T1–T12 not implemented; teacher mirror not built (mock only).
**Next:** prepare Friday: verify OL-023, mock the teacher mirror in the demo, rehearse v3 §0.

## 2026-10-12 (eng review) — /plan-eng-review of runner/ and demo/
**Summary:** Reviewed both services against the approved pilot plan. Proved by probe: provider errors become raw 500 (runner), the 30-day deletion resets whenever an answer is saved, delimiter tags can be closed from inside student text (both), instructor token is written to the access log, and a Helper reply lands in the wrong room when you switch rooms mid-request (demo). 13 decisions, all answered; TODOS.md created with one item.
**Files touched:** `docs/designs/eng-review-runner-demo.md` (new), `TODOS.md` (new), `docs/{DECISIONS,OPEN_LOOPS,STATUS,UPDATE_LOG}.md`, `CHANGELOG.md`. No product code changed.
**Loops:** opened OL-021. **Decisions:** D-022.
**Not done:** tasks T1 to T12 (not implemented); outside-voice review unavailable (Codex binary missing; no native fallback tool).
**Next:** implement T1 to T4 before hosting students; interviews can proceed now.

## 2026-10-12 (market research) — /plan-ceo-review, HOLD SCOPE
**Summary:** 15 searches on competitors, price, instructor behavior and HK/APAC. Found: code viva is not empty (NYU Viva public, ~$0.42/student; OralExam.AI, ExamSim, EXAMAI, Socratic Mind), Turnitin Clarity is in campus pilots only, "Prova" unverifiable, no WTP or HK procurement evidence. Five findings approved: positioning rewrite (D-017), pricing hypotheses (D-018), interview mix 3 HK + 2 remote (D-019), free-alternative test (D-020), data-handling note and demo sample mode (D-021).
**Files touched:** `ultimate-proposal.md` (sections 6, 7, 14), `docs/designs/market-research-ceo-review.md` (new), `docs/interview-script.md` (new), `docs/outreach-data-note.md` (new), `docs/designs/concierge-viva-pilot.md`, `docs/{DECISIONS,OPEN_LOOPS,STATUS}.md`, `demo/static/{index.html,app.js}`.
**Loops:** opened OL-019, OL-020. **Decisions:** D-017 to D-021.
**Not done:** outside-voice review unavailable (Codex binary missing; no native fallback tool). HK/Singapore procurement data not found.
**Next:** run the five interviews.

## 2026-10-12 (later still) — Built the Room demo on DeepSeek (founder call, D-016)
**Summary:** `demo/`: two seeded Spaces with fictional sources, typing-only sandbox (paste blocked, bulk-input escalation, assisted-input alternative), Helper (lecture-first, refuses to write for the student), Coach (grounded, anchor validated, tunable frequency), coverage map, in-room citation check, deterministic Proof (Standard / Oral-verified recommended / Returned with reasons). DeepSeek key read from the gitignored `.env`, never printed.
**Verified:** 12 unit tests (fake LLM); all endpoints run live against DeepSeek; full flow in headless Chromium (spaces, typing, blocked paste, burst-triggered Coach, grading, Helper, coverage, citation check catching an unsupported claim and a nonexistent [S9], Proof, reload persistence) with zero console errors.
**Not done:** live DOI verification, lecture mining feeding rooms, code track in the Room, accounts, dashboard, LMS (OL-018).
**Files touched:** `demo/**`, `docs/{DECISIONS,OPEN_LOOPS,STATUS,UPDATE_LOG}.md`, `CHANGELOG.md`.
**Next:** use the demo yourself, then outreach (OL-013).

## 2026-10-12 (later) — Built the thin viva runner (founder call, D-015)
**Summary:** Founder chose to build before outreach. Built `runner/`: FastAPI + plain HTML; guardrails (line-citation validation, bounded retries, distinct visible errors, injection-safe prompt framing), consent gate, 30-day purge, student export/delete, blind-test mode with hidden arm mapping and tally. 27 tests pass; live HTTP smoke test passed in stub mode.
**Not verified:** real Anthropic calls (no API key), browser rendering of the pages.
**Files touched:** `runner/**`, `.gitignore`, `docs/{STATUS,OPEN_LOOPS,DECISIONS,UPDATE_LOG}.md`, `CHANGELOG.md`.
**Loops:** opened OL-017.  **Decisions:** D-015.
**Next:** run with a real key, then send the five emails the same day.

## 2026-10-12 — /office-hours + /plan-ceo-review (HOLD SCOPE): pilot-first replan
**Summary:** Ran an office-hours diagnostic: Q1 demand, Q2 status quo and Q3 specific human all came back with no evidence. A landscape search showed the "EMPTY market" claim for code viva is overstated. A second opinion (Claude subagent; Codex binary was broken) challenged premise 3. Approved Approach A (concierge pilot + thin viva runner) and a design doc. CEO review in HOLD SCOPE added four approved remedies: blind-test design, generator guardrails, consent-first policy, doc updates.
**Files touched:** `docs/designs/concierge-viva-pilot.md` (new, APPROVED), `CLAUDE.md` (section 5 + gstack routing rules, committed in 4251931), `docs/STATUS.md`, `docs/OPEN_LOOPS.md`, `docs/DECISIONS.md`, `design/README.md`, `CHANGELOG.md`.
**Loops:** opened OL-013 to OL-016; demoted OL-002 (P1) and OL-003 (P2).
**Decisions:** D-011 to D-014; D-002 superseded in part.
**Next:** email five CS instructors (OL-013). Do not build before two answers are on paper.
**Not done:** the adversarial spec-review loop on the design doc was skipped; no outside-voice plan review ran (Codex binary missing, no native-fallback tools). gstack was upgraded 1.87.0.0 to 1.91.85.0.

## 2026-10-11 — Repo initialized for agent handoff
**Summary:** Created the documentation skeleton so an agent with no context can continue the work. All content comes from `ultimate-proposal.md`. Made no product decisions beyond what the proposal already locks (recorded as D-001…D-010). Found that the prototype miner code mentioned in the proposal is not in the repo, logged as OL-002.
**Files touched:** `CLAUDE.md`, `README.md`, `.gitignore`, `CHANGELOG.md`, `docs/{STATUS,UPDATE_LOG,OPEN_LOOPS,DECISIONS,GLOSSARY}.md`, `design/{README,architecture,lecture-miner,data-isolation,code-track-mvp}.md`.
**Loops:** opened OL-001 to OL-012.
**Decisions:** D-001 to D-010 (backfilled from the proposal).
**Next:** recover the prototype code (OL-002), then run the variant-engine quality probe (OL-003).

## 2026-10-11 — (prior session, backfilled) Product/market working session
**Summary:** Full product and market working session that produced `ultimate-proposal.md`. Prototyped the visual lecture miner on MIT 18.06 Lecture 1 (159 board states, ~1 min CPU, no ML) and validated it against a synthetic chalkboard ground truth (~0.3 s accuracy). Ran live market research (sources in proposal §13).
**Files produced (outside this repo):** `lecture_miner.py`, `make_sheet.py`, `gen_synth.py`, `strang_out/states.csv`, demo contact sheets.
**Next:** Phase 1 CS viva-coach MVP.
