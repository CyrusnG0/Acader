# T-015: integrate golden sessions with the receipt compiler

- **Lead:** codex-lead-T015. **Workers:** three Codex subagents (receipt integration; fixtures/recorder; CI and independent review).
- **Branch:** `task/T-015-golden-sessions`.
- **Worktree:** `.claude/worktrees/agent-a32af4671c6a75062`.
- **Base work preserved:** `67b6c82` (original T-015 implementation). Main, including T-016, integrated at `a7ed040`. This handoff supplements the original 2026-10-24 T-015 handoff; the changes below supersede its obsolete pending-mechanics and local-only browser limitations.

## What changed

- `prototype/server/golden/build.py`: the existing ingest/replay/L1 builder now calls the actual receipt service, retains receipt/artifacts/hash/stamp and post-issuance events, supplies the previously missing synthetic mapper artifact, and closes its HTTP client and database. Golden builds require `ROOM_LLM=stub`. The stamp fixes the Git component to `golden-fixtures-v1`, retaining actual lock, editor and prompt hashes.
- `prototype/server/golden/project.py`: includes mechanics words in the L1 projection and a separate compiled question-target projection.
- `prototype/server/golden/__main__.py`: `show` checks both frozen projections and exits unsuccessfully on a mismatch. `actions` remains usable without an LLM configuration.
- `prototype/server/tests/test_golden_sessions.py`: asserts frozen L1 and compiled question targets; directly checks compiled word/claim counts against the independent YAML expectations; verifies issued receipt hashes and artifacts; checks full receipt/chain determinism, stored replay with no model calls, pending mode, and rejection of missing artifacts or changed receipts.
- `prototype/fixtures/golden/`: promotes D-050 mechanics (14 body words, 46 mechanics words); adds the editing-above-linked regression. Twelve synthetic sessions have separately authored compiled target expectations. Expectations were derived from scenario intent and the existing compiler's accepted interfaces, never copied wholesale from generated output.
- `prototype/web/golden/record.mjs`: uses the browser bundled with pinned Playwright by default, records the actual browser version, and closes Vite/browser resources after failures. `CHROMIUM` is an explicit local debugging override.
- `prototype/web/package{,-lock}.json`: exact `playwright-core` 1.56.1 dev dependency.
- `.github/workflows/ci.yml`: a dedicated job installs locked Python dependencies and pinned Chromium, regenerates recordings, rejects drift, and checks receipts against frozen expectations.
- `prototype/fixtures/README.md`: documents the executable compiled expectations and current limits; clarifies held-out sessions must never tune the mapper.
- `docs/TASKS.md`: only T-015 ownership and status changed, while preserving main's merged T-016 status during the merge conflict resolution.

## Tests run

All results below are synthetic engineering checks, not results about students.

- **[VALIDATED]** `cd prototype && ROOM_LLM=stub .venv/bin/python -m pytest -q`: 776 passed, one existing Starlette deprecation warning (before the final assertion-helper regression test was added; the final golden subset was rerun below).
- **[VALIDATED]** `cd prototype && ROOM_LLM=stub .venv/bin/python -m pytest -q server/tests/test_golden_sessions.py`: 138 passed, one existing Starlette deprecation warning.
- **[VALIDATED]** `cd writing-room-kit && ROOM_LLM=stub python3 -m pytest -q v04/tests web/tests`: 29 passed, two existing warnings.
- **[VALIDATED]** `cd prototype/web && npm run typecheck && npm test && npm run build`: typecheck and build passed; 118 web tests passed.
- **[VALIDATED]** Two complete `node golden/record.mjs` runs using bundled Chromium 141.0.7390.37 (revision 1194), Playwright 1.56.1: all twelve recording files byte-identical across runs.
- **[VALIDATED]** Workflow YAML parses; Playwright install CLI checked; `git diff --check` clean.
- Local Python is 3.14; CI specifies 3.12. The Ubuntu CI job itself has not been run in this session.

## Review and EXPECTATIONS sections claimed

- **A:** T-015 scope plus necessary T-016 integration and CI regression coverage. Stub tests pass; no secrets or real student data; `shared/llm.py` unchanged. No user-facing copy or product rules changed. This handoff records the checks. No design files changed.
- **C:** existing input/replay/mark/seal checks retained; actual receipt bytes, hashes, artifacts and stored-output recompilation now tested end to end. Confirmed Helper-only references stay outside the five bands.
- **D:** existing five-band scenarios retained; accepted suggestions never elevate pasted text; editing an earlier paragraph preserves the later paragraph's source chain and link.
- **I-M1:** engine golden coverage only. Rendering and a real person reading the rendered receipts remain outstanding. Agent review does not meet the human-review exit.
- Independent worker review found missing direct assertions for compiled band counts and a browser-version mismatch between local recording and CI. Both were addressed before final validation.

## Not done / open

- T-017 rendering depends on T-010 DESIGN.md. Neither is implemented here.
- The open textbook is selected in D-051 but remains absent from executable sessions. Do not call the full corpus complete.
- Parser-generated block IDs remain deferred; these fixtures retain the original hand-defined, attributed excerpts from the three S2 papers. Original PD-T015-1 still needs founder disposition.
- Mapper labels remain drafts: independent labels, five held-out sessions and the full 15–20-session mapper set remain later evaluation work. These tests do not enable the mapper.
- No live LLM runs or question-quality claims. Leak checking and persistence/release remain later tasks documented by T-016.
- Original T-015 proposals and T-016 proposals are not approved by this integration. The compiler's existing behavior is frozen for regression purposes only; founder changes must update the expectations deliberately.

## Proposed decisions

No new product decisions. Original PD-T015-4's temporary xfail is resolved by the already-approved D-050 and merged T-016 implementation. Original PD-T015-7's deferred CI proposal is superseded in this branch by implementing evaluation.md §2's browser-regeneration requirement now. All other outstanding founder proposals remain with the checker.

## Checker review — 2026-10-25

**Passed for T-015's M1 engineering scope.** An independent subagent reviewed the complete branch diff, and another independently ran all checks. This does not close the M1 rendering/human-review milestone or the mapper gate.

- [x] A1 scope: twelve sessions exceed the ten requested; real editor/ingest and frozen expectations present.
- [x] A2 tests: prototype **777**, goldens **138**, kit **29**, web **118**; typecheck/build passed; all twelve recordings regenerated without diff. Locked applicable package versions match; pip check passed.
- [x] A3 regression checks: forged quote/Coach marks, pasted linked text, mechanics, shifted downstream positions, compiler count forwarding, artifact verification, determinism and pending mode.
- [x] A4 shared client unchanged; A5 no secrets or real student data introduced; A6–A7 no new product claims or banned user-facing copy; source text and code identifiers are distinct from product copy.
- [x] A8–A9: D-050 mechanics synchronized into provenance.md and its design index row; both handoffs retained.
- [x] C1–C5: browser-origin/replay fixtures, mark checks, editor/card/Coach paste scenarios, rounded merge timestamps, seal and post-seal issuance verification.
- [x] C6–C7: same inputs/stored outputs yield identical receipts; receipt tampering/missing artifacts rejected, with existing store/verify tests covering chain edits/deletion/reordering and whitelist rules.
- [x] D: declared/source/Coach/student-linked/untraced scenarios preserve band precedence; paragraph and accepted-suggestion links never elevate pasted text; source links survive an edit above them.
- [ ] I-M1: receipt UI and human reading remain T-017/the milestone exit.

Non-blocking follow-ups are now explicit: OL-046 (full corpus and independent labels) and OL-047 (founder proposals). Local checks used Python 3.14.5/Node 25.9.0; Ubuntu/Python 3.12/Node 22 CI execution remains unobserved here. No proposals were approved by the checker.
