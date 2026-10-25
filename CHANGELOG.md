# Changelog

All notable repo-level changes. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versions start when there is shippable code. Until then, everything goes under `[Unreleased]`.

## [Unreleased]

### Added
- 2026-10-25: tickets T-025 (remove student withdrawal), T-026 (delayed state + release re-check), T-027 ("More places to ask"); T-022 unblocked and rescoped (D-059…D-062).
- 2026-10-25: release cap and transactional withdrawal (`app/lifecycle.py`, `app/withdrawal.py`, `POST /logs/{id}/withdraw`; T-021, D-058); checker accepted.
- 2026-10-25: submit and compile orchestration (`app/compile_jobs.py`: receipt v1 then v2, five-try retry cap with operator alert, startup reconcile; T-020, D-054); checker accepted.
- 2026-10-25: durable receipt and AI-artifact storage (`app/receipt_store.py`, T-018) and bounded durable job queue (`app/jobs/`, T-019); checker accepted.
- 2026-10-25: S3/S4 preregistration (`prototype/spikes/S3/`, `S4/`, T-007) and nursing walkthrough + blind-question preregistration (`docs/research/`, T-009); protocols only, nothing run.
- 2026-10-25: ticket T-024 (drop "Written on N days"); T-020 ticket now carries the five-try retry cap (D-054).
- 2026-10-25: approved DESIGN.md and twelve actual synthetic receipt views with sentence evidence navigation (T-010/T-017); checker accepted, human M1 reading still open.
- 2026-10-25: executable worker tickets T-018…T-023 for storage, jobs, compile orchestration, lifecycle, preview and S3 harness, with separate ownership and dependency gates.
- 2026-10-25: repository-local cold-worker tickets for T-007/T-009/T-010/T-017, claim/review instructions and refreshed pickup status; existing T-010 proposal preserved for resumption.
- 2026-10-25: twelve executable golden sessions with real Chromium recordings, ingest/replay and receipt-compiler regression checks; CI regenerates recordings using pinned Playwright/Chromium (T-015).
- 2026-10-24: receipt compiler (`engine/receipt/`, `app/receipt_service.py`): JSON receipt with integer counts, hash, question text via `complete()`, wording filter, "mechanics" count (T-016, D-050).
- 2026-10-24: golden-set source manifest, D19 session script format and 15 draft mapper-label seeds (`prototype/fixtures/`, T-008).
- 2026-10-24: L1 deterministic provenance (`engine/provenance/`: sentence split, origin mix, chains via paragraph links, bands, receipt facts, thresholds config) (T-014).
- 2026-10-24: compile-time replay with checkpoint hash checks and the provenance mark check (`engine/provenance/`, `engine/replay/rebuild.py`, `app/compile_service.py`) (T-013).
- 2026-10-24: paragraph links and the D-044 node set in the editor schema, replay and fixtures (T-011); the inline `claim` mark is removed.
- 2026-10-24: events layer for M1 (`app/events_service.py`, `routes_events.py`, `engine/events/merge.py`): staging, 5-minute merge, checkpoints, idempotent submit and seal, post-seal 409, verify endpoint, edit lease (T-012).
- 2026-10-24: editor input plugin (`web/src/editor/`) and Python replay (`engine/replay/`) with browser parity (spike S1, T-004; GO). Spikes S2 (`spikes/S2/`, PDF parsers) and S5 result notes.
- 2026-10-24: `prototype/server/app/llm.py`: `complete(task, messages, schema)` boundary with stub, D13 error classes, backend-2 slot and boot ping (T-003).
- 2026-10-24: `prototype/web/schema.json` and `src/schema.ts`: origin and claim marks with closed lists, loaded into ProseMirror (T-002).
- 2026-10-24: `engine/events/`: hash chain, seal, post-seal whitelist, SQLite append store, `verify` and `python -m engine verify` (spike S5, T-005; GO).
- 2026-10-24: `prototype/` scaffold (server packages, FastAPI `/healthz`, engine CLI stub, Vite + TS web, fixtures, spikes) and `.github/workflows/ci.yml` running prototype, kit and web checks (T-001).
- 2026-10-24: `EXPECTATIONS.md` (checklist every task must pass), `docs/TASKS.md` (task board, M0 tasks), `docs/handoffs/` (handoff template); CLAUDE.md §8 lead/worker/checker flow.
- 2026-10-24: `docs/designs/eng-review-v2.md` (eng review of the mapper and workspace, D-037).
- 2026-10-24: `design/workspace.md` (student workspace and live map) and `docs/designs/design-review-v1.md` (design review record, D-036).
- 2026-10-23: `docs/designs/eng-review-v1.md` (eng review record, D-034); TODOS entries for L2 embeddings and the Postgres move.
- 2026-10-23: `docs/designs/ceo-review-v1.md` (CEO review record, D-032); TODOS.md deferrals for v1.

### Changed
- 2026-10-25: founder decisions D-059…D-062: student preview = teacher first screen order; full candidate list behind "More places to ask"; `delayed` state past the cap; student withdrawal of the process record dropped from v1. receipt.md, event-log.md, privacy.md, evaluation.md, EXPECTATIONS H and PRODUCT.md §7 updated.
- 2026-10-25: the receipt summary no longer says "Written on N days" or cites edit batches (T-024, D-055).
- 2026-10-25: design/provenance.md §5 aligned to §6 on `added` propositions (D-056); design/receipt.md summary examples drop the session count (D-055).
- 2026-10-25: golden logs register licensed reading metadata before student actions, so compiled receipts show the correct source count and reading titles (T-015 followup).
- 2026-10-24: links to claims move from an inline mark to the paragraph (D-045); construction order and answer grading dropped as signals (D-046); spike decisions D-041…D-044 folded into design/ (event-log, provenance, receipt, workspace, reading-aid, coach-helper). M1 tasks T-011…T-017 on the board.
- 2026-10-24: Python deps for `prototype/` locked with hashes in `requirements.lock` (uv); `requirements.txt` removed; CI installs the lock (D-040, T-003).
- 2026-10-24: D-038: Coach cases B and C run as one "new idea" case with one pillar question (reading, logic, writing, communication); coach-helper.md §3, event-log.md, PRODUCT.md §5, GLOSSARY.
- 2026-10-24: /plan-eng-review v2 (D-037): mapper events, band rules, payload/consent, budget, eval and M4m written into design/; PRODUCT.md §5/§7 say the pilot tests the student-built outline; OL-044 closed.
- 2026-10-24: /plan-design-review (D-036): receipt first screen, submissions list, band colours, chain wording, student preview and P-15 wording set; wording filter now covers every surface; /design-consultation gate added to the build plan.
- 2026-10-24: D-035: the live map is the product; a mapper links meaning as the student writes, never trust. PRODUCT.md §5 updated; OL-044 opened to fold it into design/.
- 2026-10-23: /plan-eng-review (D-034): stack locked (OL-008); every CEO and eng decision folded into design/ (override boxes removed); build plan re-baselined (~28 build days; engine + receipt + walkthrough ~11-08); kit frozen.
- 2026-10-23: second outside review (Opus, D-033): build-plan re-planned bottom-up (11-05 = engine + receipt + walkthrough ready), stricter pilot gate, OL-043 opened.
- 2026-10-23: `design/build-plan.md` rewritten (receipt-first, one class, 10-30 checkpoint, hardened pilot gate); PRODUCT.md §7 updated; CEO-review override notes on seven design docs.

### Added
- 2026-10-23: `PRODUCT.md` (product source of truth); `design/` v1 set: architecture, event-log, provenance, receipt, reading-aid, coach-helper, privacy, evaluation, build-plan; `prototype/` scaffold README; `shared/llm.py`.
- 2026-10-22: `docs/designs/writing-platform-v1.md` (product design for The Writing Room v1) and `docs/designs/provenance-engine.md` (engineering design: event model, chains, receipt, signal register, spikes). Decisions D-024 to D-030; loops OL-035 to OL-042.

### Changed
- 2026-10-23: repo restructured (D-031). Moved to `archive/`: earlier proposals, design v1 docs, `demo/`, `runner/`, viva pilot docs. Moved to `docs/research/`: reports, research notes, market research, the Gemini brainstorm (was `response.md`). `demo/llm.py` → `shared/llm.py` (kit, web app and Dockerfile updated; 29 tests pass). CLAUDE.md, README.md, GLOSSARY.md rewritten; kit README gets an English index.
- 2026-10-22: direction locked to The Writing Room, process as evidence (D-024); product laws 5 and 9 amended (D-028); code track and viva pilot parked (D-030). `CLAUDE.md`, `STATUS.md` and `design/README.md` updated.

### Added
- 2026-10-21: Hosted static demo (`writing-room-kit/web/static/demo.html` plain click-through, `index_demo.html`, `vision.html`), `docs/renewed-direction/` (renewed proposal v2, verified sources, pitch scripts, plans).
- 2026-10-21: repo tidy: renewed-direction docs moved into `docs/renewed-direction/`, `feature-experiment-report.md` into `writing-room-kit/`, stray `writing-room-kit 2/` into `archive/`, caches removed.
- 2026-10-16: `writing-room-kit/` v0.2 experiment: tooling, pre-registration (PREREG.md), 36 simulated runs, RESULTS.md; v0.3 repair (PREREG-v0.3.md) after a harness artifact was found. Not evidence about real students.

### Changed
- 2026-10-12: proposal sections 6, 7, 14 corrected from market research (viva = commodity; pricing as hypotheses; Clarity = pilots). D-017, D-018.
- 2026-10-12: current focus switched from the full Phase 1 code track to a concierge viva pilot (D-011); `STATUS.md`, `CLAUDE.md` section 5 and `design/README.md` updated to match.

### Added
- 2026-10-14: `ultimate-proposal-v3.md` (CLEAR brief: process-as-proof + teacher mirror; replaces v2 for Friday), candidate decision D-023, loops OL-022 to OL-026.
- 2026-10-14: `reports/AI era understanding assessment tools.md` and its research notes (competitors, policy, evidence, gaps).
- 2026-10-12: `docs/designs/eng-review-runner-demo.md` (eng review, 13 decided findings), `TODOS.md`. D-022.
- 2026-10-12: `docs/designs/market-research-ceo-review.md`, `docs/interview-script.md`, `docs/outreach-data-note.md`; demo sample-text button and sticky banner. D-019 to D-021.
- 2026-10-12: `demo/`, the Acader Room demo (spaces, sources, typing-only sandbox, Helper, Coach, coverage map, citation check, Proof) on DeepSeek. D-016.
- 2026-10-12: `runner/`, the thin viva runner (FastAPI, guardrails, consent, blind-test mode, 27 tests). D-015.
- 2026-10-12: `docs/designs/concierge-viva-pilot.md` (APPROVED pilot plan); decisions D-011 to D-014; open loops OL-013 to OL-016; gstack skill-routing rules in `CLAUDE.md`.
- 2026-10-11: Repo initialized for cold-start agent handoff:
  - `CLAUDE.md` (agent orientation, product rules, session protocol), `README.md`, `.gitignore`.
  - `docs/`: `STATUS.md`, `UPDATE_LOG.md`, `OPEN_LOOPS.md`, `DECISIONS.md`, `GLOSSARY.md`.
  - `design/`: `README.md`, `architecture.md`, `lecture-miner.md`, `data-isolation.md`, `code-track-mvp.md`.
- 2026-10-11: `ultimate-proposal.md`, the product source of truth (vision, validated miner, philosophy, product spec, market evidence, GTM, risks, module plan, roadmap, sources).
