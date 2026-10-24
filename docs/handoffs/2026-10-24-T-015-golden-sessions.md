# T-015: Golden sessions (YAML scripts, Playwright recorder, ingest builder, frozen L1 receipts)

- **Lead:** lead-opus-T015   **Workers used:** Sonnet ×2. One built the Python builder and golden test; the other built the Chromium recorder and the S1 page methods. The lead wrote the spec, the block fixture, all 11 scripts and every expected value, reviewed the code, fixed one test helper and ran the mutation pass.
- **Branch or worktree:** `task/T-015-golden-sessions` (from `origin/main` 823095f)   **Commit(s):** 8ad921a (claim), plus the code-and-handoff commit after it

## What changed
- **`prototype/fixtures/golden/*.yaml`: 11 session scripts.** Each holds the actions, the draft mapper labels (`batches`) and a frozen `expected_receipt`.
  - honest-nursing, declared-outside, pasted-rewritten, ai-expanded-card, thin-honest
  - linked-outside-ai (D13), accepted-suggestion-paste (D12 + D13), forged-marks (D5)
  - coach-paste-moved (D26), elaborating-honest (D-045)
  - reference-list (D-050), whose `pending` block is a strict xfail until T-016
- **`prototype/fixtures/golden/blocks.json`: 9 source blocks** from the three S2 papers (CC BY 4.0, attributed). Block ids look like `nursing.p7.limitation`. See PD-T015-1.
- **`prototype/fixtures/golden/recorded/*.json`: 11 recordings from real Chromium**, 160 KB in total. Each holds the steps, `input_kind` counts and the browser's `doc_hash` per editor action. Two runs gave byte-identical files.
- **`prototype/web/golden/record.mjs` (new): the Playwright recorder.** It drives the real editor on the S1 page. It gets each script's editor actions from `python -m golden actions <id>`, so Python is the only YAML parser.
- **`prototype/spikes/S1/page/main.ts`:** adds `insertMarked`, `blocks`, `accept` and `pasteCount` to the page handle. Existing methods are unchanged, and the S1 Chromium check still passes 23/23 with `s1_browser_steps.json` unchanged.
- **`prototype/server/golden/` (new package):**
  - `script.py`: loads and validates scripts and computes the editor-action hash.
  - `build.py`: the ingest builder. Student events, batches, checkpoints and submit go through the T-012 HTTP API (`create_app` + `TestClient`). `coach.ask`, `helper.serve`, `claim.extracted` and `map.suggestion` go through the same `EventService` with their real actors. The clock is injected (2026-11-02T14:00Z + minute + k s). Then it runs `compile_marks` → `l1_from_compile` and `verify`.
  - `project.py`: the receipt projection.
  - `__main__.py`: `actions` and `show`.
- **`prototype/server/tests/test_golden_sessions.py` (new, 77 tests).** For each session:
  - the frozen receipt;
  - Python replay of every recorded action to the browser's `doc_hash`;
  - the recording is current;
  - two builds give identical chain hashes and L1 bytes;
  - the seal verifies and `editor.batch` timestamps fall on window boundaries;
  - the mapper labels are well formed.

  Plus builder unit tests: stale recording, a forged quote, `mapper_enabled`, clock seconds, code-point offsets, and a missing doc.
- **`prototype/pyproject.toml` and `requirements.lock`:** `pyyaml` added to the `dev` extra. The lock was regenerated with uv; `pyyaml==6.0.3` is the only change and no other pin moved.
- **`prototype/fixtures/README.md`:** the executable format (actions, paths, expected receipt) and the limits.
- **`docs/TASKS.md`:** the T-015 row only.

Not touched: engine/, app/, `web/src`, `schema.json`, `shared/`, `design/`, the kit and CI. CI needs no change: the new test lives in `server/tests`, so the existing python job runs it.

### What runs where
- **CI (python job), no browser:** the whole golden test runs on the committed recordings. It rebuilds every log through the real API, then runs replay, the mark check and L1, and compares each result with the frozen values. A change to `schema.json` or the engine that moves a result fails it. A script whose editor actions changed without a new recording fails with "recording is stale".
- **Locally only (needs Chromium):** `cd prototype/web && npm i --no-save playwright-core@1.56.1 && node golden/record.mjs`. CI does not re-record when editor code changes. That is the S1 PD-S1-7 step at M3.

## Why the frozen numbers are right (checked by hand before the run)
I wrote every expected value from the script's intent, with word counts from `str.split` on each intended sentence (a scratch counter that uses no engine code). Then I ran the pipeline. **10 of 11 matched on the first run.** The 11th differed by one character, explained in PD-T015-2. In the sentence lists, *sN* is the sentence number and the figure in brackets is its word count.

- **thin-honest (21 words):** p1 is typed and student-linked, so s1 (11) and s2 (6) are band 4. p2 is unlinked typed text, so it is untraced (4).
- **honest-nursing (61):**
  - s1 holds a checked 5-word quote and nothing pasted, so it is traced to source (18). s2 is typed elaboration, so band 4 (8).
  - s3 quotes "based in a single institution", so it is traced (16). Only 4 of its words are quoted, because "institution," ends in a typed comma.
  - s4 is the student's own typed Coach answer, so it is traced to the Coach (11). Its link is `by: coach`, so it is not a `student_link` target.
  - p4 is unlinked typed text, so it is untraced (8).
  - Units: c1 = 18 traced + 8 band 4, so traced. c2 = 16 + 11, so traced.
  - Moments:
    - c2 edited after the limitation pin and its anchor;
    - socsci set aside as "off topic";
    - Coach revised.
- **declared-outside (42):**
  - p1 links d1, a declared claim that was never re-anchored. Both sentences are declared: the imported one (13) and the typed one (6).
  - p2 is typed and linked, so band 4 (13).
  - p3 links d2, which card2 re-anchored (D-050 (3)), so it is band 4, not declared (10).
  - Facts: 2 declared claims, 1 re-anchored.
- **pasted-rewritten (41):**
  - s1 is fully pasted in a linked paragraph, so it is untraced with the D13 note (13).
  - s2 was retyped, so it is band 4 (19).
  - s3 keeps 37 of 53 characters pasted (70%), so it is untraced with the note (9).
  - Unit: 22 untraced vs 19, so untraced.
- **ai-expanded-card (32):**
  - The card is 82% pasted (`cards_with_paste` 1). Moved into the draft, s1 is 98 of 119 characters `paste_ext`, so it is untraced with the note (17).
  - s2 (5) and s3 (10) are typed, so band 4.
- **linked-outside-ai (32):** both pasted sentences stay untraced with "pasted; linked by the student, not checked" (14 + 11). The typed paragraph is band 4 (7). 156 pasted characters survive.
- **accepted-suggestion-paste (32):** the accepted link carries `sg1`, so the sub-counts are `inferred_links` 1 and `map_suggestions` 1. The pasted sentences still come out untraced with the note (11 + 10). The hand-linked typed paragraph is band 4 (11).
- **forged-marks (36):**
  - The forged quote (`not_in_block`) covers 44 of 67 characters and counts like a paste, so s1 is untraced with `label_not_confirmed` (12). It gets no D13 note because nothing in it is `paste_ext`.
  - The forged coach mark (`not_in_answer`) is untraced (8).
  - The genuine quote is traced (11, 4 quoted words).
  - The forged coach sentence has no typed characters, so it is not an "unlinked" target. The genuine-quote sentence is 36 of 71 characters typed, so it is.
- **coach-paste-moved (23):** the typed answer part sits inside the typed range, so it is traced to the Coach (10). The pasted part of the answer arrives as `paste_ext`, so it is untraced with the note (13). Facts: `coach_answers_with_paste` 1.
- **elaborating-honest (42):** every sentence, including a phrase typed mid-sentence and two appended sentences, stays band 4 (13 / 14 / 7 / 8). Nothing is untraced. Moment: Coach disagreed, with a written reason.
- **reference-list (60):**
  - Typed and linked, so band 4 (14).
  - Confirmed Helper references with no link come out untraced under L1 as built: 24 + 2 + 1 and 18 + 1. I predicted the splitter's cuts by hand: "M." after a capitalised name doesn't split, "PLoS ONE." does, and nothing splits before lowercase "arXiv".
  - The D-050 "mechanics" expectation (total 14, mechanics 46, untraced 0) is in `pending` as a strict xfail.

## Tests run
- `cd prototype && ROOM_LLM=stub python -m pytest -q` in a **fresh venv**: `pip install --require-hashes -r requirements.lock`, Python 3.14.5 → `602 passed, 1 xfailed, 1 warning in 2.56s` (525 before + 77 new; the xfail is reference-list's D-050 pending).
- `cd prototype/web && npm ci && npm run typecheck && npm test && npm run build` → typecheck ok; `Test Files 3 passed (3)`, `Tests 118 passed (118)`; `✓ built`.
- `cd writing-room-kit && ROOM_LLM=stub python3 -m pytest -q v04/tests web/tests` → `29 passed, 2 warnings in 0.15s`.
- `node ../spikes/S1/browser_check.mjs` → 23/23, fixture unchanged. `node golden/record.mjs` twice → `diff -r` identical.
- **Lead mutation pass** (one change at a time on the golden test file, then restored):

  | Mutation | Golden tests failing |
  |---|---|
  | D13 removed | 6 |
  | unconfirmed marks pass | 1 |
  | min quote words 4 → 6 | 2 |
  | `schema.json`: `paste_ext` dropped from the origin enum | 20 |
  | `schema.json`: paragraph attribute `links` renamed | 23 |
  | claim-unit tie goes to the earlier band | **0** |

  The last mutation survives because no golden session has a tie. T-014's unit test covers it.
- Banned-word grep over the new files: the only hits are JavaScript `catch` statements in the recorder. `blocks.json` contains the CS paper's own word "probabilities", which is source text, not product copy.

## EXPECTATIONS sections claimed
- **A:** all lines. `shared/llm.py`, `design/` and the kit are untouched. No secrets. The student text is invented test text. Only short CC BY excerpts are committed, with attribution.
- **C:**
  - typed text stays `typed` at span edges (Chromium recordings, honest-nursing);
  - forged marks are untraced (D5);
  - pastes are tracked in the editor, in cards and in Coach answers (D26);
  - editor batches carry 5-minute timestamps;
  - the seal verifies;
  - the same log gives byte-identical L1 (the determinism test).
- **D:** exercised end to end on real browser logs: D13 (three sessions), D12 sub-count, D27/D19 (no student or suggestion link is ever traced), D-045 elaboration.
- **I-M1:** partly. The 10 golden L1 receipts (plus reference-list) are frozen and were read by a person (the lead). "Receipts render" needs T-016/T-017.

## Not done / open
- **The 15–20 mapper-eval sessions, the 5 held-out sessions and the second-person review of the labels.** All 11 sessions carry draft `expected_links`; `label_status` is draft.
- **Sessions from evaluation.md §2 that were not in the T-015 list:**
  - **D17, "edit above a linked sentence":** not authored.
  - **The nursing case:** honest-nursing covers it.
- **The open textbook (`sociology_methods`) is not used.** Its page returned a short non-content response to a scripted fetch, so all sessions use the three S2 papers.
- **The `delete` editor action** is implemented but no session uses it yet.
- **Docling is not installed here,** so block references are hand-defined (PD-T015-1).

## Proposed decisions (the checker takes these to the founder; nothing here is decided)
- **PD-T015-1: block references and committed excerpts.**
  - The golden set uses hand-defined block ids over the S2 PDFs, extracted with pypdfium2 and checked by eye.
  - The 9 short block texts are committed in `blocks.json` (CC BY 4.0, attributed), so CI can run the mark check offline. The fixtures README previously said to keep no source text in Git.
  - *Recommend:* accept. Swap in the parser's block ids when the reader task lands; that regenerates every recording.
- **PD-T015-2: unchanged characters keep their origin through a browser text replacement.**
  - In pasted-rewritten, the student replaced a pasted sentence ending in "." with a typed sentence ending in ".". The browser's DOM diff kept the old period, still marked `paste_ext`. So 130 pasted characters survive, not 129, and the retyped sentence carries 1 pasted character.
  - The band is unchanged, and the result can only weaken text, never strengthen it.
  - *Recommend:* accept as "record what changed in the text" (law 7), and say in event-log §4 that a replacement re-marks only the characters it actually changed.
- **PD-T015-3: what "question targets" means in a golden.** As frozen, it is the L1 candidate list (the L3b queue, with reasons). T-016 picks the 2–3 "where to ask" questions from it and should freeze those too. *Recommend:* accept.
- **PD-T015-4: the D-050 mechanics expectation is a strict xfail.** It lives in reference-list `pending`. T-016 must point that check at its compiler output and promote the block. *Recommend:* accept.
- **PD-T015-5: `pyyaml` added as a dev dependency** (lock regenerated per D-040; nothing else moved). *Recommend:* accept.
- **PD-T015-6: payload fields the builder fills that event-log §3 doesn't name:**
  - `helper.serve.helper_serve_id`;
  - `map.suggestion.paragraph_hash` = sha256 of the paragraph node's canonical JSON;
  - `card.anchor.quote_hash` = sha256 of the quote.

  *Recommend:* add them when the event payloads are validated.
- **PD-T015-7: the S1 spike page is the recorder's editor page until the M3 editor exists** (four methods added to its handle). The recorder types with `keyboard.insertText` by default and uses real key events where a script sets `keys: true`. *Recommend:* accept; move the recorder to the M3 page and add Playwright to CI at M3 (PD-S1-7).
