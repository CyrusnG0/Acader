# Synthetic receipt review gallery (T-017)

This is a local development gallery of twelve actual golden receipts. It has no school accounts or production student preview/release routes. All names and assignments are explicitly synthetic. The existing compiler supplies summary, questions, word/claim bands, mechanics, sources and hashes; the browser does not recompute provenance.

Install the repo's locked Python dependencies in `prototype/.venv` and run `npm ci` in `prototype/web` once. Then, from `prototype/web`:

```sh
npm run review:receipts
```

That single command exports the real stub-only golden data into ignored `public/review/golden-receipts.json` and starts Vite. If the interpreter lives elsewhere, set `GOLDEN_PYTHON=/absolute/path/to/python`. No `.env`, API key, LLM connection, reading URL fetch or external font request is needed. Use only synthetic fixture data. The teacher question text in this gallery is not a student preview.

Open the printed local URL. The default is the nursing golden. Expand Sample submissions to select every session; the list is alphabetical by synthetic name with status only. Direct links use `?session=honest-nursing`, `?session=forged-marks`, etc. The session IDs are the YAML filenames under `prototype/fixtures/golden/`.

Click a displayed question span or a sentence under How it was built → Final text to open its own evidence. The dialog shows actual IDs, event sequence/date/hour, source/card/claim/Coach/import/Helper steps and supported position-mapped draft spans. Escape or Back returns keyboard focus to the exact opener. Card anchors alone remain unchecked. Failed origin marks retain their gap. Typed and pasted portions of Coach answers are not mixed into a stronger claim.

## Export and checks

From `prototype` (with the locked environment active):

```sh
ROOM_LLM=stub PYTHONPATH=server:.. python -m golden export web/public/review/golden-receipts.json
ROOM_LLM=stub python -m pytest -q
```

From `prototype/web`:

```sh
npm run typecheck
npm test
npm run build
npm run review:receipts -- --host 127.0.0.1 --port 5199
```

With the server running, a second terminal in `prototype/web`:

```sh
node review/check.mjs
```

The browser check uses pinned Playwright Chromium (`npx --no-install playwright-core install chromium` once if not already installed). Override `RECEIPT_REVIEW_URL` to match a different port; use a loopback URL. The check asserts every session's actual compiled data, six meaningful evidence paths, null/pending/replay/zero and escaping states, focus restoration, full first-screen gloss, narrow header readability, light/dark/reflow and print. Derived states are test-only clones, never exported as frozen goldens. Screenshots, print PDF and JSON report default to `/tmp/acader-T017-review`; set `RECEIPT_ARTIFACTS` to choose another directory. The browser does not count as the required human reading of ten receipts.

Do not regenerate editor recordings for this UI-only change. Existing golden projection tests run unchanged. All Python checks use `ROOM_LLM=stub`; live release runs belong to their separate release process.

## Evidence boundary and limitations

- `receipt` and `receipt_hash` remain the exact compiler outputs. `view_context` separately contains synthetic header metadata, final sentence/paragraph spans and display evidence. Prose in the context passes the existing wording filter; blocked text is explicitly omitted, not silently changed into a claim.
- A source/claim/card path is a recorded association, not proof that every linked sentence is supported. Only already-confirmed marks are labelled confirmed. Accepted suggestions remain student links and pasted sentences remain in their existing bands.
- Draft correspondence uses ProseMirror step maps, not paragraph order. A span whose boundaries cannot be mapped safely has an explicit unavailable-history note. Missing sentence IDs in historical snapshots, replaced/deleted boundaries and replay-mismatch copies are not guessed. Complete lineage through those cases would need an explicitly designed stable identity/mapping contract, outside this renderer.
- Event references are real sequence IDs. Dates display only date/hour; no input timing is introduced. Diff snippets are from actual mapped spans; the display does not invent an original draft or a percentage of rewriting.
- OL-047 remains open for the other T-015/T-016 proposals. D-055 removed the “Written on N days” clause; the renderer shows the compiled summary unchanged.
- `Mark as discussed`, production student preview, withdrawal, release windows, persistence and jobs remain later implementation work. No inert control is presented as if it works.
- The human M1 reading gate is recorded separately in the task handoff. Do not treat an automated screenshot or an AI review as completion of that gate.

## Fonts

Only same-origin font assets are requested. `public/fonts/manifest.json` records the official Google source URLs, licence URLs and SHA256 values. Source Sans 3 and Literata are distributed with their full OFL notices in that directory. The renderer uses the approved T-010 family choices, light/dark tokens, focus ring, spacing and patterned single-blue bands. No external CDN is needed at runtime.
