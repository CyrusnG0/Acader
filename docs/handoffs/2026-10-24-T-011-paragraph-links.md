# T-011: Paragraph links + D-044 node set

- **Lead:** lead-opus-T011   **Workers used:** Sonnet ×2 (schema, editor, replay and jsdom fixture; Chromium pass). The lead wrote the spec and reviewed the output.
- **Branch or worktree:** `task/T-011-paragraph-links` (from `main` 4d2701d)   **Commit(s):** 23982cd (schema, editor, replay, jsdom fixture), fac6eec (Chromium pass), plus the handoff commit

## What changed
- `prototype/web/schema.json`: `schema_version` 2.
  - The `claim` mark is removed. Marks are `origin`, `em` and `strong`.
  - Nodes follow D-044: doc, paragraph, heading (level 1–3), blockquote, bullet_list, ordered_list, list_item, text and hard_break.
  - `paragraph.links` defaults to `[]`, with item rules: `claim_id` and `by` are required; `suggestion_id` is optional and allowed only when `by` is `student`; unknown keys are refused.
  - Saved shape: `{claim_id, by}` or `{claim_id, by, suggestion_id}`. When there is no suggestion the key is left out; it is never `null`.
- `prototype/web/src/schema.ts` and `prototype/server/engine/replay/replay.py`: both apply the same new checks (`array`/`object` types, `items`, `optional`, `only_when`). `LINK_BY` replaces `CLAIM_BY`.
- **Step-type allowlist in both replays (D-044):** the allowed types are `replace`, `replaceAround`, `addMark`, `removeMark`, `addNodeMark`, `removeNodeMark`, `attr` and `docAttr`.
  - Any other type raises `ReplayError` before the step is loaded.
  - The list is exported as `ALLOWED_STEP_TYPES` from `record.ts` and from `engine.replay`.
- `prototype/web/src/editor/nodes.ts` (new): TipTap nodes are generated from `schema.json`, the same way `marks.ts` builds marks.
  - On `links`: `keepOnSplit: false`, and `parseHTML` always returns `[]`, so HTML never brings links in.
- `prototype/web/src/editor/links.ts` (new): the link commands and the structural rule.
  - **Commands:** `linkParagraph`, `unlinkParagraph` (removes every link with that claim_id) and `acceptSuggestion` (a `by: student` link with its `suggestion_id`).
    - Each one makes one undoable `attr` step, marked with the `wr-links` meta.
    - They refuse a duplicate, an empty `claim_id`, a `by` outside the list, and a `suggestion_id` without `by: student`.
  - **`linksPlugin`:** an appended transaction for the structural rules:
    - **J1:** the tail of a joined paragraph brings its links.
    - **J2:** the first paragraph of a multi-paragraph internal paste brings its links.
    - **J3:** Enter at the start of a linked paragraph leaves the new empty paragraph above it unlinked.
    - Joins union the links, deduplicated by claim_id + by + suggestion_id: the surviving paragraph's links come first, then the new ones in source order.
    - History transactions are skipped, so undo and redo restore links exactly.
- `prototype/web/src/editor/origin.ts`:
  - The claim stripping is removed, and `insertMarked` no longer takes a claim.
  - `handleTextInput` keeps `strong` and `em` and replaces the origin with `typed`.
  - `stampSlice` sets `links: []` on every pasted node from outside.
  - An internal paste carries its clipboard slice as meta (`wr-paste-slice`) for J2; see "Not done / open" 1.
- `prototype/web/src/editor/marks.ts`: em renders `<em>` (and parses `<i>`); strong renders `<strong>` (and parses `<b>`).
- `prototype/web/src/editor/editor.ts` and `formatting.ts` (new):
  - The generated nodes are used and `linksPlugin` is wired in.
  - Keys: Enter (`splitListItem` in lists), Shift-Enter (hard break), Tab and Shift-Tab (sink and lift a list item), Mod-b, Mod-i.
  - Helpers: `setHeading`, `setParagraph`, `toggleBulletList`, `toggleOrderedList` and `toggleBlockquote`.
  - Input and paste rules stay off.
- `prototype/web/src/editor/record.ts`: the allowlist is added in `replaySteps`. `markSet` flattening is kept.
- Tests:
  - `web/src/schema.test.ts` and `web/src/editor/s1.test.ts`: 55 recorded cases.
  - `server/tests/test_replay_s1.py` and `server/tests/test_schema_json.py`.
- Fixtures:
  - `prototype/fixtures/replay/s1_steps.json`: regenerated, 55 cases (replace 147, addMark 63, attr 19, replaceAround 17, removeMark 2).
  - `s1_browser_steps.json`: regenerated in real Chromium, 23 cases.
- `prototype/spikes/S1/browser_check.mjs` and `page/main.ts`: moved to the new schema. The claim cases are replaced by linked-paragraph cases, and new real-keyboard cases cover split, Enter at the end, Backspace join, copy and paste of linked paragraphs, undo and redo of a link, bold typing, Enter in a list, and Shift-Enter.
- `docs/TASKS.md`: T-011 row only (Owner `lead-opus-T011`, `review`).

**prosemirror-py 0.6.1 check:** it has `AttrStep` (`attr`) and `ReplaceAroundStep`, and both replay to the same JSON as JS. Link changes therefore use `tr.setNodeAttribute`, which makes an `attr` step. Wrapping in or lifting out of lists and blockquotes uses `replaceAround`. No workaround was needed.

## Tests run
- `cd prototype && ROOM_LLM=stub .venv/bin/python -m pytest -q` → `388 passed, 1 warning`.
  - The venv is Python 3.14.5, installed with `pip install --require-hashes -r requirements.lock`.
  - Every jsdom and Chromium case replays in Python to the same doc JSON and `doc_hash`.
- `cd prototype/web && npm ci && npm run typecheck && npm test && npm run build` → typecheck clean; `Test Files 3 passed (3)`, `Tests 118 passed (118)`; `✓ built`.
- `cd writing-room-kit && ROOM_LLM=stub python3 -m pytest -q v04/tests web/tests` → `29 passed`.
- `cd prototype/web && npm i --no-save playwright-core@1.56.1 && node ../spikes/S1/browser_check.mjs` (local Chrome for Testing):
  - `23/23 passed`.
  - A second run wrote a byte-identical fixture (`cmp`).
  - `npm ci` was run afterwards; `package.json` and the lock are unchanged.
- Mutation checks (each restored afterwards):

  | Change | Result |
  |---|---|
  | J1 off | 6 editor tests fail, plus the fixture comparison |
  | `stampSlice` keeps links | the direct `stampSlice` test fails |
  | `keepOnSplit: true` | 3 tests fail (Enter at the end, both list cases) |
  | Python allowlist removed | 3 allowlist tests fail |

- Banned-word grep over `web/src`, `engine/replay`, `spikes/S1` and `schema.json`: no hits. No user-facing strings were added.

## EXPECTATIONS sections claimed
- **A:** all lines. No design doc was changed, no dependency was added, and `shared/llm.py` and the kit are untouched.
- **C, line 1 (typed text is always `typed`):** re-tested on the new schema, including inside linked paragraphs, with bold or italic active, in headings, and in real Chromium.
- **C, line 3 (pastes):** editor part only. External paste is `paste_ext` and never brings links.
- **D, last line (D-045):** the record side only.
  - Typing, IME, replacements, adding sentences, and deleting all the text inside a paragraph never change its links.
  - Split, join, Enter, paste, undo and redo follow the rules above.
  - "A paragraph link alone never makes a sentence traced" is banding, which comes in T-013 and later; nothing here bands.

## Not done / open
1. **J2 has to read the clipboard slice.**
   - The problem: ProseMirror's fitter rebuilds the first open paragraph of a pasted slice with default attrs, so the recorded step shows `links: []` there.
   - The fix: the internal paste puts the original slice on the transaction as meta, and J2 reads the links from it.
   - The limit: a drag inside the document carries no such meta, so dragging part of a paragraph into an empty paragraph does not bring its links. Dragging whole paragraphs, or into a non-empty paragraph, follows the rules.
2. **Some deletes drop links, because the whole paragraph is deleted** ("a paragraph deleted whole takes its links"):
   - **Backspace onto an empty paragraph:** ProseMirror deletes the empty paragraph rather than joining. If that empty paragraph had links, they are dropped.
   - **Select-all (Mod-a) on a one-paragraph document, then typing:** this replaces the paragraph node itself, so its links go. Selecting only the paragraph's text and typing keeps them, which is tested.
3. **Changing a linked paragraph into a heading drops its links,** because headings have no `links` attr. Undo restores them. Wrapping in a list or blockquote keeps them.
4. **Pasting outside text strips `em` and `strong` too** (`stampSlice` strips every mark, as in S1). Italic titles pasted from outside come in plain.
5. Small choices:
   - `acceptSuggestion` allows `c1/student/s1` next to a plain `c1/student`, because the dedupe key includes `suggestion_id`.
   - An empty-string `suggestion_id` is accepted.
   - `@tiptap/extension-paragraph` is no longer imported but stays in `package.json`, so the lock does not change.
6. **CI still does not run the Chromium pass** (PD-S1-7, M3). pytest replays the committed Chromium fixture.

## Proposed decisions (the checker takes these to the founder; nothing here is decided)
- **PD-T011-1: an inline fragment pasted inside another paragraph.** This is my reading of "internal paste keeps links".
  - **As built:**
    - Pasted whole paragraphs keep their links.
    - When a multi-paragraph paste joins its first or last paragraph with the paragraph at the cursor, those joins union the links.
    - A part of one paragraph pasted into an empty paragraph brings that paragraph's links.
    - An inline fragment pasted inside a non-empty paragraph changes nothing: the fragment takes the target's links, as typed text does.
  - **Alternative:** a fragment also unions its source paragraph's links into the target.
  - **Recommended:** as built. Moving a phrase shouldn't silently add a link (D-045: links change only by explicit action or by structure).
- **PD-T011-2: a paragraph deleted whole takes its links** (open item 2: Backspace onto an empty linked paragraph; select-all plus typing).
  - **Recommended:** accept it. Undo restores the links, and it follows from "a deleted paragraph's links go".
  - **Alternative:** have the editor keep the first paragraph's links when select-all replaces the whole document.
- **PD-T011-3: headings carry no links.** Converting a linked paragraph to a heading drops its links (undo restores).
  - **Recommended:** keep. Event-log §4 puts links on paragraphs, and a heading is not part of an argument.
  - **Alternative:** give `heading` a `links` attr too, which is a schema bump.
- **PD-T011-4: external paste keeps `em` and `strong`?** Today every mark is stripped.
  - **Recommended:** keep formatting marks on external paste, because references need italics. It changes nothing about origin, which is still `paste_ext`. This would be a small follow-up.
- **PD-T011-5: event-log.md §4 wording.** Add one line to the link rules: "Internal paste keeps the links of whole pasted paragraphs; external paste never adds links." Also add the step-type allowlist (as listed above) to §5 if the checker wants it explicit.
