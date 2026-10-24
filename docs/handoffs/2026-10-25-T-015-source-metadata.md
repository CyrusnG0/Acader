# T-015 followup: register golden source metadata

- **Worker:** checker_review (narrow implementation followup delegated by the lead).
- **Branch/worktree:** `task/T-015-source-metadata`, `.claude/worktrees/codex-T015-source-metadata`.
- **Base:** `c980c5d`. No commit made by this worker.

## What changed

The golden scripts named readings and used their blocks and anchors, but never registered `source.add`. The actual receipt consequently said "with no sources" and showed null reading titles. This fixes fixture setup rather than receipt behavior.

- `prototype/server/golden/script.py`: safe-load the existing local `sources.yaml` manifest, resolve each script's `source_ids` in declared order, reject unknown/duplicate/malformed IDs and invalid manifest entries. Omitting `source_ids` remains valid for unit scripts.
- `prototype/server/golden/build.py`: before student actions, append one teacher `source.add` event per script source via the existing `EventService`. Payload uses the manifest's exact ID, title and `content_url`, with `origin: teacher`. URLs are metadata only; nothing is fetched.
- `prototype/server/tests/test_golden_sessions.py`: all twelve sessions assert source-registration count/order/actor/payload, populated reading titles, correct source-count wording and source-event citations in the compiled summary. Five invalid-ID cases exercise both validation and build entry points. A unit script without source IDs still builds.

No compiler, copy, frozen band/question expectations, recorder, dependency or shared tracking files changed.

## Checks

- **[VALIDATED]** From this worktree's `prototype/`, `ROOM_LLM=stub /Users/micmic/Documents/GitHub/Acader/.claude/worktrees/agent-a32af4671c6a75062/prototype/.venv/bin/python -m pytest -q` → **795 passed**, one existing Starlette warning. The reused environment supplies dependencies; pytest's local `pythonpath` loads this worktree's implementation.
- **[VALIDATED]** From this worktree's `writing-room-kit/`, `ROOM_LLM=stub python3 -m pytest -q v04/tests web/tests` → **29 passed**, two existing warnings.
- **[VALIDATED]** Existing 138 golden tests passed after the code fix before the 18 new source-registration regressions were added, with all frozen expectations unchanged.
- **[VALIDATED]** Built honest-nursing under `ROOM_LLM=stub PYTHONPATH=server:..`, explicitly asserted `golden.build.__file__` points into `codex-T015-source-metadata`, and saved the real compiled receipt to `/tmp/acader-T015-honest-nursing-receipt.json` for the design lead.
- Honest-nursing summary now begins: "Written on 1 day with 2 sources." Both reading titles match the local manifest.
- `git diff --check` passed.

## EXPECTATIONS and limits

A and C: fixture scope only, deterministic existing events, same stored-output replay and verification checks retained; stub-only and no network calls or secrets. No product laws, provenance rules or question-selection rules changed. Independent checker review and merge remain with the lead. Timing-summary wording is existing T-016 behavior and remains subject to its pending founder proposal.

## Checker review — 2026-10-25

Passed. Reviewed the entire three-file code diff and independently reran the **156 golden tests**, all passing. Existing expectations stay frozen, with correct library metadata now flowing through the actual service. The worker's full prototype run passed **795 tests**, and kit **29** passed. No new product decision; T-015 remains done.
