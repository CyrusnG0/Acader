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

## 2026-10-24 — T-006 (spike S2, PDF parser) checked and merged
**Summary:** Spike S2 compared Docling, GROBID (CRF image) and PyMuPDF on three CC BY readings plus a synthetic scan. Docling (OCR off) is the only one passing the S2 bar on all three; GROBID fails on tables and the scan; PyMuPDF is AGPL-3.0. Checker re-ran prototype 119 / kit 29 (spike adds no product code); no PDFs committed; Docling numbers not reproduced by the checker (2.6 GB install).
**Files touched:** prototype/spikes/S2/ (RESULT.md, run_s2.py, blocks.py, fetch.py, scancheck.py, corpus.json, gold.json), docs/handoffs/2026-10-24-T-006-spike-s2.md, docs/TASKS.md, docs/OPEN_LOOPS.md, docs/STATUS.md
**Loops:** opened OL-045 (limitation remarks outside Discussion are missed)
**Decisions:** none. Proposed: Docling as the v1 parser; text-layer scan check first; no PyMuPDF in product code (AGPL); ≥ 8 GB RAM and one parse at a time; GROBID for reference metadata later.
**Next:** founder decides the S2 proposals; T-004 lands.

---

## 2026-10-24 — T-003 (LLM boundary + lock file) checked and merged
**Summary:** Checker installed `prototype/requirements.lock` with `--require-hashes` into a fresh venv: prototype 119, kit 29 passed; `shared/` unchanged; task list matches architecture.md §5. `requirements.txt` replaced by the uv lock (D-040); CI installs it.
**Files touched:** prototype/server/app/llm.py, prototype/server/app/main.py, prototype/server/tests/test_llm.py, prototype/requirements.lock (new), prototype/requirements.txt (removed), prototype/pyproject.toml, prototype/README.md, .github/workflows/ci.yml, docs/handoffs/2026-10-24-T-003-llm-boundary.md, docs/TASKS.md, docs/STATUS.md, CHANGELOG.md
**Loops:** none
**Decisions:** none. Proposed: per-task output schemas are provisional and owned by each feature task; HTTP code mapping (5xx/408/network → Timeout, 402 → Auth, other 4xx → Refusal); deepseek backend takes [system, user] only; uv as the lock tool.
**Next:** check the CI run on 3.12; T-004 adds prosemirror-py to the lock.

---

## 2026-10-24 — T-002 (schema.json) checked and merged
**Summary:** Checker re-ran T-002: prototype 21, kit 29, web 30 passed; typecheck and build clean; after merge, prototype 69 passed. Schema matches event-log.md §4 (six origin kinds, claim.by student/coach/import, optional suggestion_id, inclusive false). T-004 unblocked. Also fixed a checker mistake: agent worktrees under `.claude/worktrees/` had been committed as gitlinks; untracked and ignored (733c45d).
**Files touched:** prototype/web/schema.json, prototype/web/src/schema.ts, schema tests, prototype/web/package.json (+prosemirror-model 1.25.4), tsconfig.json, docs/handoffs/2026-10-24-T-002-schema.md, docs/TASKS.md, docs/STATUS.md, CHANGELOG.md, .gitignore
**Loops:** none
**Decisions:** none. Proposed: node set (doc/paragraph/text only for now; full set decided in T-004 before golden logs), one claim per span.
**Next:** T-004 (spike S1) lead launched; founder decides PD-S5-1…4 and the T-002 proposals.

---

## 2026-10-24 — T-005 (spike S5) checked and merged; CI green
**Summary:** First GitHub CI run green (prototype 13, kit 29, web). Leads now run as background Opus agents launched by the checker, one worktree each (T-002, T-003, T-005, T-006). T-005 re-run by the checker: 61 + 29 passed, whitelist matches event-log.md §6. Spike S5 is GO. EXPECTATIONS C clarified: the seal covers the record up to submission; dropping the newest post-seal events doesn't show.
**Files touched:** prototype/server/engine/events/, prototype/server/engine/__main__.py, prototype/server/tests/test_events_s5.py, prototype/spikes/S5/RESULT.md, docs/handoffs/2026-10-24-T-005-spike-s5.md, docs/TASKS.md, EXPECTATIONS.md, docs/STATUS.md, CHANGELOG.md
**Loops:** OL-035 can close once PD-S5-1…4 are decided
**Decisions:** none yet. Proposed: PD-S5-1 (prev_hash as hex text), PD-S5-2 (event id = seq), PD-S5-3 (no floats in the receipt JSON; integer word counts), PD-S5-4 (say the seal covers the record up to submission).
**Next:** founder decides PD-S5-1…4; checker reviews T-002, T-003, T-006 as they land.

---

## 2026-10-24 — T-001 checked and merged (prototype scaffold + CI)
**Summary:** Checker re-ran T-001 from a clean checkout: prototype 13 passed, kit 29 passed, web typecheck/test/build clean. Section A ticked; I-M0 scaffold ticked, "CI green" open until the first GitHub Actions run. Merged to main; T-002, T-003, T-005, T-006 unblocked.
**Files touched:** prototype/ (scaffold), .github/workflows/ci.yml, .gitignore, docs/TASKS.md, docs/handoffs/2026-10-24-T-001-scaffold.md, docs/STATUS.md, CHANGELOG.md
**Loops:** none
**Decisions:** D-039 (DeepSeek workers may read the repo, F-005), D-040 (Python lock file in T-003 with its hash in the engine stamp; Node 22.12+).
**Next:** check the first CI run; leads take T-002/T-003/T-005/T-006 (plus T-007…T-010).

---

## 2026-10-24 — Multi-agent flow set up for the build
**Summary:** The repo is ready for parallel work: one Opus lead per task (in separate conversations) with Sonnet/DeepSeek workers, and this conversation as the checker. Added EXPECTATIONS.md (plain-language checklist, sections A–I), docs/TASKS.md (M0 tasks T-001…T-010 plus founder tasks F-001…F-005), docs/handoffs/ (template). CLAUDE.md gained §8 (roles, branch per task, only the checker edits shared docs); STATUS.md rewritten as a clean snapshot.
**Files touched:** EXPECTATIONS.md (new), docs/TASKS.md (new), docs/handoffs/README.md (new), CLAUDE.md, README.md, docs/STATUS.md, CHANGELOG.md
**Loops:** none
**Decisions:** none (workflow, set by the founder)
**Next:** leads start T-001; founder answers F-001, F-002, F-005.

---

## 2026-10-24 — One Coach treatment for every new idea (D-038)
**Summary:** Founder proposal adopted: shower thoughts and outside-AI thoughts get the same Coach treatment. Cases B and C (and mapper findings) become triggers for one "new idea" case; one question from one of four pillars, never about origin, never blocking; record unchanged.
**Files touched:** design/coach-helper.md, design/event-log.md, PRODUCT.md, docs/GLOSSARY.md, docs/DECISIONS.md, docs/STATUS.md, CHANGELOG.md
**Loops:** none
**Decisions:** D-038
**Next:** pick a schedule option (build-plan §2a), then M0.

---

## 2026-10-24 — Eng review v2: the mapper and the workspace (D-037)
**Summary:** /plan-eng-review on the branch diff, scoped to D-035/D-036 (D-034 approvals reused). 21 decisions, one question each. Native Plan subagent outside voice (Codex skipped at founder request) found a Critical hole (one click could move pasted text out of untraced), fixed by D12/D13. Mapper becomes a flagged experiment in M4m after H; chained suggestion/finding/answer events; trail uses engine L1; consent and flag fixed per record; eval with recall floor and hold-out; withdrawal cancels jobs; pilot tests the student-built outline. Eng review: clean.
**Files touched:** design/event-log.md, provenance.md, architecture.md, privacy.md, evaluation.md, build-plan.md, receipt.md, coach-helper.md, workspace.md, design/README.md, PRODUCT.md §5/§7, docs/GLOSSARY.md, docs/DECISIONS.md, docs/OPEN_LOOPS.md, docs/STATUS.md, CHANGELOG.md, docs/designs/eng-review-v2.md (new); test plan + tasks JSONL in ~/.gstack.
**Loops:** closed OL-044.
**Decisions:** D-037.
**Next:** pick a schedule option (build-plan §2a), then M0 (scaffold + S1); /design-consultation before the receipt UI in M1.

---

## 2026-10-24 — Design review of the live-map workspace and receipt (D-036)
**Summary:** /plan-design-review, all 7 passes, re-centred on the live map (D-035). Opus subagent as outside voice (Codex skipped); mockups blocked (designer has no OpenAI key). 20 decisions, one question each: editor-anchored layout with the map as a two-way outline; map suggestions named "suggested by the map, not checked", confirmed by the student, never on the teacher's bars; receipt first screen, alphabetical submissions list, one-hue bands, plain chain labels; state table; trail toggle; student preview; P-15 withdrawal wording; widths incl. zoom (WCAG reflow); keyboard/screen-reader model; one Coach budget; case C copy; wording filter on every surface. Score 3/10 → 7/10.
**Files touched:** design/workspace.md (new), design/receipt.md, design/coach-helper.md, design/provenance.md, design/privacy.md, design/event-log.md, design/build-plan.md, design/README.md, PRODUCT.md §5, docs/GLOSSARY.md, docs/OPEN_LOOPS.md, docs/DECISIONS.md, docs/designs/design-review-v1.md (new), docs/STATUS.md, CHANGELOG.md; eng test plan in ~/.gstack (chain label).
**Loops:** P-15 (CEO pending item) closed by 9A; OL-044 narrowed to the engine side.
**Decisions:** D-036.
**Next:** pick a schedule option (build-plan §2a), then M0; run /design-consultation before the receipt UI in M1.

---

## 2026-10-24 — The live map direction (D-035)
**Summary:** Before continuing /plan-design-review, the founder proposed building the map bottom-up with a small model on each change. Agreed: the live map is the product and the receipt is its snapshot; a mapper proposes meaning links; the model maps meaning, never trust (bands only from recorded facts; model links show as "linked by model, not checked"); flags reach the student as Coach questions, never the teacher; golden set of real sources + an open textbook.
**Files touched:** docs/DECISIONS.md, PRODUCT.md §5, docs/OPEN_LOOPS.md, docs/STATUS.md, docs/UPDATE_LOG.md, CHANGELOG.md
**Loops:** opened OL-044
**Decisions:** D-035
**Next:** continue /plan-design-review with the map as the main student screen.

## 2026-10-23 — /plan-eng-review of the whole v1 plan set (D-034)
**Summary:** Ran /plan-eng-review on PRODUCT.md, design/ and the CEO record. 35 decisions (D1–D35), all as recommended except D4 (hosted parsing).
- **Stack locked:** SQLite everywhere, DB job queue, prosemirror-py replay, no embeddings, generic second LLM backend.
- **Receipt hardened:** marks are checked against their source; pasting into cards and Coach answers is tracked; student links get their own band.
- **Seal defined;** AI outputs are stored; batches are merged per 5 minutes for privacy.
- **Outside voice** (Opus Plan agent, not cross-model): 12 findings, 10 accepted, 1 covered, 1 rejected.
- **Docs:** all CEO and eng decisions folded into design/; the override boxes are removed.
- **Schedule** re-baselined at ~28 build days: engine + receipt + walkthrough about 11-08. Options to pull it back are in build-plan §2a, not applied.
- Kit tests: 29 passed with `ROOM_LLM=stub` (live run).

**Files touched:** docs/designs/eng-review-v1.md (new); design/architecture.md, event-log.md, provenance.md, receipt.md, reading-aid.md, coach-helper.md, privacy.md, evaluation.md, build-plan.md, README.md; PRODUCT.md §7; CLAUDE.md §5, §7; TODOS.md; prototype/README.md; writing-room-kit/README.md; docs/DECISIONS.md (D-034); docs/OPEN_LOOPS.md; docs/STATUS.md; CHANGELOG.md.
**Loops:** closed OL-008, OL-031, OL-038. OL-035 stays open until S5. OL-043, OL-036, OL-037, OL-026 still open.

## 2026-10-23 — Second outside review (Opus) folded in
**Summary:** The founder asked for an Opus reviewer instead of Codex. It read the full plan and found 16 issues. Eight decisions followed (CEO-17 to CEO-24, D-033):
- Student-made links are labelled "not checked".
- Human sessions come before the pilot.
- A blind test of process vs essay-only questions, plus the hard nursing case.
- No question text in the student preview.
- Release at the latest of: deadline, submit + 24 h, questions compiled.
- Platform-as-processor approval joins the gate.
- Bottom-up re-plan: about 20 build days, so 11-05 = engine + receipt + walkthrough ready.
- Stronger S3, an adversarial leak set, and no link-UI cut while the check is off.

The founder raised a new P0 (OL-043): if guidance makes trails uniform, what else estimates AI involvement? Doc contradictions fixed.
**Files touched:** `design/build-plan.md` (rewritten), `PRODUCT.md` §5/§7, override boxes in provenance/receipt/evaluation/coach-helper/privacy, `design/receipt.md` (PDF line), `docs/designs/ceo-review-v1.md`, `docs/DECISIONS.md` (D-033), `docs/OPEN_LOOPS.md` (OL-043), `docs/STATUS.md`, `CHANGELOG.md`.
**Loops:** opened OL-043.
**Decisions:** D-033.
**Next:** /plan-eng-review; deep research on OL-043.

## 2026-10-23 — /plan-ceo-review of v1 (SCOPE REDUCTION)
**Summary:**
- Ran the CEO review on PRODUCT.md and design/build-plan.md. gstack was upgraded to 1.91.176.0 first.
- Landscape: Clarity and Authorship already track characters; our difference is claim lineage plus questions.
- Decisions: 16, all answered.
  - Build: receipt-first thin slice for one class; 9 items deferred to TODOS.md.
  - Rules: a second LLM backend; seal on submit; roster + magic link (LTI next); the Door never fetches URLs; release at the deadline; a 10-30 teacher checkpoint; ethics approval + an assignment window in the gate; reworded text counts as untraced; S3 gates L3b; the walkthrough moves mid-build; one append per log.
- Codex outside voice failed (AUTH_FAILED). The native fallback found 13 issues, all handled, including the fact that the plan files had not yet been updated (now done).
**Files touched:** `docs/designs/ceo-review-v1.md` (new), `design/build-plan.md` (rewritten), `PRODUCT.md` §7, override boxes in `design/{architecture,provenance,receipt,coach-helper,reading-aid,privacy,evaluation}.md`, `TODOS.md`, `docs/DECISIONS.md` (D-032), `docs/OPEN_LOOPS.md`, `docs/STATUS.md`, `CHANGELOG.md`.
**Loops:** OL-036 now has a 2026-10-30 deadline; OL-026 raised to P0 (pilot gate).
**Decisions:** D-032.
**Next:** /plan-eng-review on design/architecture, event-log, provenance; start teacher outreach and approval requests (T13).

## 2026-10-23 — Repo restructured for the prototype; v1 spec and design set written
**Summary:** On the founder's request, turned the repo into the prototype repo:
- Wrote `PRODUCT.md` as the product source of truth.
- Wrote nine design docs in `design/`: architecture with the recommended stack, event log (envelope, origin marks, hash chain, sealing), provenance (chains, L0–L3, claim compare, bands), receipt (layout, chain view, question selection, wording filter, JSON, nursing example), reading aid, Coach/Helper/Door with the leak check, privacy with draft consent text, evaluation (spikes, golden receipts, pilot measures), and a build plan to 2026-11-05 with cut lines and a pilot gate.
- Archived the old vision, design v1 and code-track code.
- Moved the LLM client to `shared/llm.py`; the kit and web tests still pass (29).
- Rewrote CLAUDE.md, README.md and GLOSSARY.md.
**Files touched:** `PRODUCT.md`, `design/*` (new set), `prototype/README.md`, `shared/llm.py`, `CLAUDE.md`, `README.md`, `docs/GLOSSARY.md`, `docs/DECISIONS.md` (D-031), `docs/OPEN_LOOPS.md`, `docs/STATUS.md`, `CHANGELOG.md`, `archive/README.md`, `writing-room-kit/README.md`, `writing-room-kit/v04/llmx.py`, `writing-room-kit/scripts/outside.py`, `writing-room-kit/web/{app.py,Dockerfile}`, superseded notes on `docs/designs/*`; many moves (see CHANGELOG).
**Loops:** closed OL-004, OL-010, OL-018; parked OL-021; updated OL-025, OL-031, OL-033, OL-035, OL-037, OL-039, OL-041.
**Decisions:** D-031 (repo structure; law 6 wording aligned with D-025, to be confirmed by the founder).
**Next:** /plan-ceo-review on PRODUCT.md + design/build-plan.md.
**Verification sweep (same day):** 152 live markdown files link-checked (1 broken link left in a historical plan, `docs/renewed-direction/PLAN-static-demo.md`); OL-031 and OL-038 repointed from the superseded drafts to `design/`; no banned wording in PRODUCT.md or `design/`; 29 kit/web tests pass with `ROOM_LLM=stub`.

## 2026-10-22 — Founder interview; direction locked; v1 designs drafted for gstack
**Summary:** Reviewed `response.md`, a Gemini brainstorm after the 2026-10-21 meeting, against the kit results. Kept: provenance by channel, cheap pipeline, reading pins, declared channel. Dropped: typing velocity, cosine thresholds, "token fog", "100% / bulletproof" wording. Interviewed the founder in four rounds on direction, receipt, outside AI, users, purpose, timeline, sources, LLM, scale, facts and laws. Locked the direction (The Writing Room, process as evidence) and wrote the v1 product and engineering designs, ready for /plan-ceo-review, /plan-eng-review and /plan-design-review.
**Files touched:** new `docs/designs/writing-platform-v1.md`, `docs/designs/provenance-engine.md`; updated `CLAUDE.md` (§1 direction, §3 repo note, laws 5 and 9, §5 focus), `docs/DECISIONS.md` (D-024 to D-030; D-002, D-011 and D-023 marked), `docs/OPEN_LOOPS.md`, `docs/STATUS.md`, `design/README.md`, `CHANGELOG.md`.
**Loops:** opened OL-035 to OL-042; closed OL-022, OL-027, OL-032; updated OL-013, OL-023, OL-031, OL-033; parked OL-003, OL-009, OL-015, OL-017.
**Decisions:** D-024 direction; D-025 receipt and proportions; D-026 outside AI and Coach cases; D-027 reading aid; D-028 laws 5 and 9; D-029 prototype v1 plan; D-030 code track parked.
**Next:** /plan-ceo-review on writing-platform-v1.md.

## 2026-10-21 — Demo shown; feedback recorded; repo tidied
**Summary:** Built and iterated the static demo (22 screens, Presenter mode, guided tour, later reduced to a plain click-through for `/demo`), `vision.html`, `index_demo.html` cleanup, verified sources and pitch-v2. The demo was shown to professors and researchers: they liked it and said it could be a startup, but want technical depth. Key feedback: teachers are stressed because "is it AI?" is subjective with no proof (nursing case: 40-page Copilot log, then a demand for more); a log that shows AI proportion, which parts were AI-aided, and a readable receipt would be the product; the citation idea needs more thought (not summarising, but nobody wants to read 40 pages); one said "Grammarly but more academic and whole-process", then asked what tracking and diff add, since we can't send every snapshot to an AI. Tidied the repo.
**Files touched:** moved to `docs/renewed-direction/` (renewed_proposal*, outsider, sources-verified, pitch, pitch-v2, PLAN-renewed-v2, PLAN-static-demo, HANDOFF-v0.4) with a README; `feature-experiment-report.md` to `writing-room-kit/` (two links fixed); `writing-room-kit 2/` to `archive/writing-room-kit-v0.2-copy/` with a README (two references fixed); removed `__pycache__` and `.pytest_cache`; updated STATUS, OPEN_LOOPS, CHANGELOG. Nothing committed.
**Loops:** opened OL-031 to OL-034.
**Decisions:** none locked.
**Next:** write the tracking-and-diff spec (OL-031) and prototype on kit sessions.

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
