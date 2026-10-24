# Changelog

All notable repo-level changes. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versions start when there is shippable code. Until then, everything goes under `[Unreleased]`.

## [Unreleased]

### Added
- 2026-10-24: `EXPECTATIONS.md` (checklist every task must pass), `docs/TASKS.md` (task board, M0 tasks), `docs/handoffs/` (handoff template); CLAUDE.md §8 lead/worker/checker flow.
- 2026-10-24: `docs/designs/eng-review-v2.md` (eng review of the mapper and workspace, D-037).
- 2026-10-24: `design/workspace.md` (student workspace and live map) and `docs/designs/design-review-v1.md` (design review record, D-036).
- 2026-10-23: `docs/designs/eng-review-v1.md` (eng review record, D-034); TODOS entries for L2 embeddings and the Postgres move.
- 2026-10-23: `docs/designs/ceo-review-v1.md` (CEO review record, D-032); TODOS.md deferrals for v1.

### Changed
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
