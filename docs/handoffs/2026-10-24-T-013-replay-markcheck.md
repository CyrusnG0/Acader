# T-013: Replay + mark check at compile

- **Lead:** lead-opus-T013   **Workers used:** Sonnet ×1 (fully specified; the lead wrote the spec, reviewed the code and ran its own mutation pass)
- **Branch or worktree:** `task/T-013-replay-markcheck` (from `origin/main` 591a082)   **Commit(s):** 4984730 (claim), 80c9f0c (code and tests), plus the commit with this handoff

## What changed
- `prototype/server/engine/replay/rebuild.py` (new, pure):
  - `EMPTY_DOC` is the rev-0 document, the editor's empty doc (`doc > paragraph{links: []}`).
  - `step_segments` / `steps_between`: read the `editor.batch` events as `(start_rev, end_rev, steps)`, with `start_rev = doc_rev − len(steps)`. A missing or non-contiguous batch raises `ReplayError("steps_gap …")`.
  - `rebuild_at(events, doc_rev, load_snapshot)`: rebuilds from the nearest checkpoint snapshot at or below `doc_rev` (or from `EMPTY_DOC`), then the chained steps.
  - `check_replay(events, load_snapshot, seal_seq=None) -> ReplayReport`: checks every checkpoint up to the seal (the latest `submit` by default). Each one gets one of these results:
    - `ok`
    - `hash_mismatch`: the replayed hash differs from the hash the client sent.
    - `snapshot_mismatch`: the stored browser snapshot doesn't hash to what the client sent.
    - `replay_error`
    - `steps_gap`
    - `snapshot_missing`

    Each segment starts from the previous checkpoint's own snapshot, so one bad segment never hides later ones. When every check passes, the result is status `ok` with `built_from: replay` and the replayed final doc. Otherwise it is status `replay_mismatch` with `built_from: browser_copy` and the stored snapshot of the final (submit) checkpoint. It only raises when even that snapshot is missing.
- `prototype/server/engine/provenance/sources.py` (new):
  - `ProvenanceSources` protocol: `block_text(block_id)`, `coach_answer(q_id) -> CoachAnswer(text, typed_ranges)`, `import_text(import_id)`, `helper_output(serve_id)`.
  - `InMemorySources` for tests.
  - `coach_answer_from_runs(text, origin_runs)` builds a `CoachAnswer` from a `coach.outcome` payload. Typed runs are merged and clamped. Anything not covered by a typed run counts as pasted (fail closed).
- `prototype/server/engine/provenance/markcheck.py` (new):
  - `normalise` maps curly, prime and guillemet quotes to `'` and `"`, collapses all Unicode whitespace to one space, and strips the ends.
  - `origin_runs` returns the maximal runs with the same origin `(kind, ref)` inside one textblock. `em` and `strong` don't split a run. A `hard_break` carrying the same origin continues the run as whitespace. Runs never cross textblocks.
  - `check_marks(doc, sources) -> [RunCheck]` returns one result per `quote`, `coach`, `import` or `helper` run. `typed` and `paste_ext` runs are never checked. Each result is `{from, to, kind, ref, confirmed, reason}`, with integers only.
  - Reasons are checked in this order:
    - `missing_ref`, then `origin_not_found`.
    - quote: `not_in_block` (its own block only), then `ok` if the run is the whole block, then `too_short` (< 4 words), then `ok`.
    - coach: `ok` only if the run is inside one typed range of the answer. Otherwise `pasted_in_answer` if it is in the answer but touches a pasted part (D26), else `not_in_answer`.
    - import: `not_in_import`. helper: `not_in_output`.
- `prototype/server/engine/provenance/compile.py` (new):
  - `compile_marks(...) -> CompileResult` runs the replay first, then the mark check on its document (on a mismatch that is the browser's copy).
  - `status` is `complete` or `replay_mismatch` (receipt.md §3, D28).
  - `to_json()` includes the `unconfirmed` count and passes `canonical_json` (no floats).
  - `operator_alerts(result, log_id)` returns one alert per failing checkpoint. An alert holds hashes, seq, doc_rev and reason only, never document text.
- `prototype/server/app/compile_service.py` (new):
  - `compile_log(service, log_id, sources, seal_seq=None)` loads the events and the stored snapshots from `EventService` and runs the compile.
  - It writes alerts with `INSERT OR IGNORE` into a new `operator_alerts` table (unique per log, kind and seq), so a second compile adds nothing.
  - It never appends to the chain, so the student is unaffected.
  - `list_alerts` reads the table back.
- `engine/replay/__init__.py` and `engine/provenance/__init__.py`: exports only.
- Tests: `server/tests/test_markcheck.py` (24 tests) and `server/tests/test_replay_compile.py` (11 tests, driven through the real `EventService` with an injectable clock). The step logs are built with prosemirror-py `Transform`.
- `docs/TASKS.md`: T-013 row only.

Not touched: `prototype/web/`, `schema.json`, `engine/events/`, `app/events_service.py`, `engine/replay/replay.py`, `shared/`, `design/`, the kit, dependency files.

## Tests run
- `cd prototype && ROOM_LLM=stub .venv/bin/python -m pytest -q` (venv: Python 3.14, `pip install --require-hashes -r requirements.lock`) → `453 passed, 1 warning in 0.47s` (418 before + 35 new)
- `cd writing-room-kit && ROOM_LLM=stub python3 -m pytest -q v04/tests web/tests` → `29 passed, 2 warnings in 0.15s`
- Required cases, each with its own test:
  - a forged quote, including text from a different block (`not_in_block`)
  - 3 words → `too_short`, 4 words → `ok`
  - a whole 2-word block → `ok`, also with different whitespace and quotes
  - a coach run on the pasted part, or spanning typed and pasted → `pasted_in_answer`
  - a coach typed part not at offset 0, and a coach run moved to another paragraph by replayed steps → `ok`
  - a gap in a coach answer's runs counts as pasted
  - an import and a helper run, each passing and failing
  - a checkpoint hash mismatch: status `replay_mismatch`, `browser_copy`, one alert row (still one after a second compile), and the chain unchanged with `verify` still ok
  - replay across 3+ checkpoints, plus `rebuild_at` between and before checkpoints
  - a run split by bold is one run; the same block quoted twice around typed text gives two runs
  - normalisation: curly quotes both ways, NBSP, double spaces, a hard break
  - also: `snapshot_mismatch`, `replay_error` with later checkpoints still checked, `steps_gap`, runs on the browser copy after a mismatch, the end-to-end `compile_log`, seal selection after a resubmission, and byte-identical `canonical_json` across two runs
- Mutation checks: each change was applied alone, the two new test files were run, and the code was restored. The worker ran a–f and the lead ran g–l.

  | Mutation | Result |
  |---|---|
  | a. drop the 4-word minimum | 2 fail |
  | b. quote matched against any block | 1 fail |
  | c. coach: whole answer instead of typed parts | 2 fail |
  | d. no quote-character mapping | 3 fail |
  | e. skip the replayed-hash comparison | 1 fail |
  | f. split runs on any mark difference (bold) | 1 fail |
  | g. no whole-block exception | 2 fail |
  | h. no whitespace normalisation | 4 fail |
  | i. no snapshot-hash check | 1 fail |
  | j. on mismatch use the replayed doc, not the browser copy | 1 fail |
  | k. drop the `pasted_in_answer` reason | 2 fail |
  | l. checkpoints after a failed one go unchecked | 2 fail |
- Banned-word grep over the new files: no hits. The only strings are snake_case reason codes; no user-facing copy was added.

## EXPECTATIONS sections claimed
- **A:** all lines. No design doc changed, `shared/llm.py` untouched, no secrets, no dependency added.
- **C, line 2:** "Every non-typed mark is checked against its origin text at compile; a failed check is untraced". This task covers the check and the `unconfirmed` result. Turning `unconfirmed` into the untraced band and the chain-view note is T-014.
- **C:** the replay-mismatch path (D28) on the record side: `replay_mismatch` status, `browser_copy`, operator alert. The receipt label is T-014 and the receipt work.

## Not done / open
- **No jobs loop yet.** event-log §5 wants the replay check as a background job at every checkpoint. The function exists (`check_replay`, or `compile_log` before the seal compiles the unsealed head), but nothing runs it on a timer. The operator page that reads `operator_alerts` is also not built.
- **Real sources.** The stores behind `ProvenanceSources` (reader blocks, `coach.outcome` answers, Door raw text, Helper outputs) come with their feature tasks. Only the in-memory version exists.
- **Paragraph links are not checked** (D-045, banding is T-014). `paste_ext` and unmarked text produce no `RunCheck`.
- **Unsealed head:** final rev = the last batch end. Its client hash is used only if a checkpoint sits exactly there.

## Proposed decisions (the checker takes these to the founder; nothing here is decided)
- **PD-T013-1: the rev-0 document.** As built, replay starts at rev 0 from the editor's empty doc (`doc > paragraph{links: []}`); nothing in the chain records it.
  - *Recommend:* accept, and add one line to event-log.md §5. Alternative: `log.open` carries the empty doc's hash.
- **PD-T013-2: offsets in `coach.outcome.origin_runs`.** `CoachAnswer.typed_ranges` uses Python string indices (code points). The browser's natural unit is UTF-16. Any emoji or other astral character in an answer would shift the ranges.
  - *Recommend:* the client sends code-point offsets, or the store converts UTF-16 to code points when it builds `CoachAnswer`. Write this in event-log.md §3 with the Coach task.
- **PD-T013-3: quotes are matched as substrings, not on word boundaries.** A quote run that starts or ends mid-word still passes if it is ≥ 4 words and inside its block.
  - *Recommend:* keep (fewer false fails on PDF hyphenation). Alternative: require word boundaries.
- **PD-T013-4: normalisation applies to all four kinds,** not only quotes. Otherwise an NBSP from the editor could fail a genuine Helper or import run.
  - *Recommend:* accept. Ligatures (ﬁ), soft hyphens and dashes are not normalised. Revisit with the S2 parser output if real quotes fail.
- **PD-T013-5: coach runs must lie inside one typed range.** Two typed parts joined across a deleted pasted part don't count.
  - *Recommend:* accept, since it fails closed. The min-length rule stays quote-only, as provenance §4.1 says.
- **PD-T013-6: reason codes** (`not_in_block`, `too_short`, `pasted_in_answer`, `not_in_answer`, `not_in_import`, `not_in_output`, `missing_ref`, `origin_not_found`).
  - *Recommend:* keep them as internal codes. The chain view shows one sentence for all of them: "this label couldn't be confirmed against its source".
- **PD-T013-7: `snapshot_mismatch` counts as a replay mismatch.** The browser's stored copy disagreeing with the hash it sent is also D28.
  - *Recommend:* accept.
- **PD-T013-8: `operator_alerts` table.** One SQLite table (`log_id, kind, doc_rev, seq, detail, created_at`), unique per log, kind and seq, holding hashes only.
  - *Recommend:* accept as the minimal operator record until the operator page (D15) exists.
