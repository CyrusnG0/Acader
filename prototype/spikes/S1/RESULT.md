# Spike S1: do origin and claim marks survive real editing, and does Python replay match?

Date: 2026-10-24 · Task: T-004 · Spec: [design/evaluation.md](../../../design/evaluation.md) §1 (S1); [design/event-log.md](../../../design/event-log.md) §4–§5; D6, D17, D21, D26, D33

**Result: GO.** Marks were correct in every case we ran. Typed text was always `typed`, including inside and at both edges of marked spans. External paste and drop were always `paste_ext`. Internal copy/paste, moves and undo/redo kept their marks. prosemirror-py, loading the same `web/schema.json`, replayed every recorded log (28 jsdom cases + 14 real-Chromium cases) to the same document, marks and `doc_hash` as the browser. We found one real problem, the `markSet` step (point 2 under "What was learned"); the step recorder now handles it. The editor can be built on this design. Seven design points need a decision first (below).

## What was built

**Browser (`prototype/web/src/editor/`)**
- `marks.ts`: TipTap mark extensions generated from `schema.json` (closed lists enforced, required attrs kept required). A vitest test checks that TipTap's schema has the same nodes, marks, `inclusive`, `excludes` and attrs as the JSON.
- `origin.ts`: the input plugin.
  - `handleTextInput` inserts keystrokes already marked `typed`, as one step.
  - `appendTransaction` re-marks every other text insertion as `typed` with no claim mark. That covers IME, replacements, DOM edits by extensions, select-all + type, and anything not explicitly marked.
  - `beforeinput` sets `input_kind`, which is kept as counts in plugin state and never stored on a mark.
  - `transformPasted` stamps `paste_ext` with a fresh `paste_id` on every paste and every drop from outside. It strips all marks first, including forged ones in pasted HTML.
  - Copy and cut write `application/x-writing-room-slice` with the slice and `log_id`. A paste carrying that type and the same `log_id` restores the marks. Another log, or malformed data, gives `paste_ext`.
  - Paste, drop, cut, undo/redo and explicitly marked transactions are left alone. `insertMarked()` is the explicit path for quote, helper, coach and import text.
- `record.ts`: records `{start, steps}` from every doc-changing transaction, including appended ones. `replaySteps()` is the JS replay.
- `canonical.ts`: canonical JSON and `doc_hash`, byte-compatible with `engine/events/canonical.py`.
- `editor.ts`: the TipTap editor with Document/Paragraph/Text, the two marks, the plugin, the recorder and history (Mod-z / Shift-Mod-z / Mod-y). Input rules and paste rules are off.
- `s1.test.ts` (vitest + jsdom, 33 tests): 28 recorded cases plus the schema-parity, closed-list, canonical-JSON and flattening tests. Each case checks the marks, replays in JS in both schemas (TipTap's and the one built from the JSON), and checks that every character has exactly one origin. It then compares the whole run with `prototype/fixtures/replay/s1_steps.json`. The test fails if that fixture drifts. Regenerate it with `UPDATE_S1_FIXTURES=1`.

**Server (`prototype/server/engine/replay/`, no FastAPI)**
- `replay.py`: `load_schema()` builds a prosemirror-py Schema from `web/schema.json` and turns each `enum` into a validate check, as `schema.ts` does. `replay_steps(start, steps)` and `doc_hash(doc)` are built on it.
- `server/tests/test_replay_s1.py` (81 tests): replays both fixtures and asserts the same doc JSON and the same `doc_hash`. It also checks that a changed step, a dropped step, an `ai` kind, a `model` claim author and an unknown step type each make the replay fail or differ.

**Real browser (`prototype/spikes/S1/browser_check.mjs` + `page/`)**: this pass is not part of CI. It drives the real editor in headless Chromium (Chrome for Testing, Playwright) and covers:
- real keystrokes inside and at the edges of quote and claim spans;
- IME composition via CDP (`Input.imeSetComposition` + `insertText`);
- an extension-style DOM edit inside a quote span;
- select-all + type, Enter inside a span, and Backspace across an edge;
- internal copy/paste and cut/paste through the real clipboard;
- an external HTML paste with a forged origin span;
- drag inside the document and a drop from outside;
- undo/redo from the keyboard.

Result: **14/14 pass**. The recorded steps are in `fixtures/replay/s1_browser_steps.json`, and pytest replays them in Python with the same result. To run it, go to `prototype/web` and run `npm i --no-save playwright-core@1.56.1 && node ../spikes/S1/browser_check.mjs`.

## What was learned

1. **The typed rule has to act after the fact, not only on keystrokes.** ProseMirror sees IME text, autocorrect and extension edits as DOM mutations, then diffs them into steps. A keystroke-only handler would miss them. The `appendTransaction` sweep covers every path. `handleTextInput` is only an optimisation: without it, each keystroke at the end of a typed run cost two steps, because with `inclusive: false` the cursor does not inherit `typed`.
2. **`markSet` breaks the shared log (fixed in the recorder).** prosemirror-transform 1.12 inverts "add an origin that replaced another origin" into a `markSet` step. Redo can then nest one `markSet` inside another. Nested `markSet` JSON does not load back in JS (`MarkSetStep.fromJSON` refuses it), and prosemirror-py has no `markSet` at all. The recorder now flattens it into its `addMark`/`removeMark` children. Those children apply in order and never move positions, so the replay result is identical. The undo case depends on this exact inversion: in older transform versions, undoing typing inside a quote would leave text with no origin. That last point comes from reading the source; we did not test it.
3. **Positions match across runtimes, astral characters included.** prosemirror-py counts UTF-16 units like JS. The emoji case replays identically.
4. **prosemirror-py ignores our `x-` keys and `enum` lists.** Its loader adds the enum checks, so a mark outside the closed list fails in Python as it does in the browser. This answers T-002's open question.
5. **What the input kinds can and cannot tell.**
   - `insertReplacementText` (spellcheck menu, autocorrect) is reported as `replacement`.
   - Composition is reported as `ime`.
   - **Dictation has no distinct input type** in Chromium. It arrives as `insertText` or composition, so the `dictation` count will stay near 0.
   - **Extensions that edit the page directly do not fire `beforeinput`.** They count as `keyboard`, not `replacement`.
   - In every one of these cases the text is still `typed`. Only the counts are less precise.
6. **Log volume.** In real Chromium a keystroke is one `replace` step of about 150 bytes of JSON. A 1,500-word essay is about 9,000 characters. Allowing for revisions, that is roughly 1.5–2.5 MB of raw steps per log, under the 5 MB in event-log.md §5. **[ASSUMPTION: extrapolated from measured step sizes, not from a real session.]**
7. **Limits of this spike.**
   - No real spellcheck menu and no real Grammarly in headless Chromium. The replacement path was driven by `beforeinput` + insert in jsdom, and the extension path by a direct DOM edit in Chromium.
   - OS-level drag does not start from Playwright's mouse in headless mode. Drag cases used real `DragEvent`s with a real `DataTransfer` at real coordinates, which run ProseMirror's own dragstart/drop and `posAtCoords`.
   - Only Chromium was tested; Safari and Firefox were not.
   - The node set is still `doc/paragraph/text`.
   - A short manual pass in desktop Chrome with Grammarly installed, and in Safari, is still worth doing before M3.

## Proposed design changes (for the checker; nothing here is decided)

- **PD-S1-1: node set (from T-002 PD-1).** Add `heading` (attr `level` 1–3), `bullet_list`, `ordered_list`, `list_item`, `blockquote`, `hard_break`, and two formatting marks, `em` and `strong`. Italics are needed for titles in APA and MLA references. Formatting marks are independent of `origin`: toggling them is a mark step, not text input, so the typed rule leaves them alone. Leave out tables, images, code, links and footnotes in v1. Decide this before golden logs exist, because every node added later changes `schema.json` and regenerates the goldens (D33).
- **PD-S1-2: typed text never carries a claim mark.** Text typed inside a linked span loses the claim for the typed characters, even when `by: student`, and a claim comes only from an explicit link action. This matches the edge behaviour T-002 shipped and never invents a link. The alternative is to keep `by: student` claims on student typing inside the student's own link. Recommended: keep as built. Banding is per sentence (provenance.md §6), so a small gap does not change the sentence's link.
- **PD-S1-3: event-log.md §5.** "The step log holds only step types both replays know (`replace`, `replaceAround`, `addMark`, `removeMark`, `addNodeMark`, `removeNodeMark`, `attr`, `docAttr`). The editor flattens `markSet` before sending. Replay rejects any other type."
- **PD-S1-4: event-log.md §5.** "`doc_hash = sha256(canonical_json(doc.toJSON()))`, with the same canonical JSON as the chain (§3)."
- **PD-S1-5: pin the editor and replay libraries as a pair.** prosemirror-transform 1.12.x (via @tiptap/pm 3.32.0, exact) with prosemirror-py 0.6.1 (in `requirements.lock`). Upgrading either side requires the S1 parity fixtures to pass again, plus the Chromium pass. Record the pair in the engine stamp alongside the lock hash.
- **PD-S1-6: event-log.md §4 `input_kind`.** Say that `dictation` cannot be told apart in browsers, and that extension edits that bypass `beforeinput` count as `keyboard`. The replacement count on the receipt is therefore a lower bound. Recommended wording for the facts table: "Replacement edits (spellcheck, autocorrect) reported by the browser."
- **PD-S1-7: CI for the browser pass at M3.** Add Playwright plus a pinned Chromium to CI once the real editor exists, so `browser_check.mjs` regenerates and checks the Chromium fixture on every change. Until then, pytest replays the committed Chromium fixture.

## Files

`prototype/web/src/editor/{marks,origin,record,canonical,editor}.ts`, `s1.test.ts`; `prototype/server/engine/replay/{__init__,replay}.py`; `prototype/server/tests/test_replay_s1.py`; `prototype/fixtures/replay/{s1_steps,s1_browser_steps}.json`; `prototype/spikes/S1/{browser_check.mjs,page/}`.
