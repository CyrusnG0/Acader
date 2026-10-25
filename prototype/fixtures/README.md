# Golden fixtures

The golden set is a deterministic engineering/evaluation set, not evidence about student behavior. Source metadata and the current licence checks live in [sources.yaml](sources.yaml). Source PDFs are fetched into an ignored cache; they are not committed. Keep only the source identifiers, versioned links, attribution, labels and test scripts in Git.

## Source and reuse rules

- Use readings listed in `sources.yaml`; each source has a stable ID and a pinned version or edition.
- Prefer CC BY 4.0 material for this set. Attribute it in the source manifest and on any rendered source page.
- For the selected textbook, use only original text whose page attribution is CC BY 4.0. Exclude images and any material marked with a different licence unless separately cleared.
- Do not use OpenStax text in this corpus without permission: its current books generally use CC BY-NC-SA, and its pages state that the content may not be used in generative-AI offerings without prior written permission.
- Download the exact version named in the manifest. Do not silently follow a `latest` URL. A source or licence change requires reviewing affected labels.

## Session script format (D19)

Each YAML file describes one authored session. The script is high-level input for the later Playwright editor driver and ingest builder; it is not a hand-written event log. `expected_links` is the human-authored gold set of **paragraph → claim** pairs for each five-minute batch (D-045). An unlisted pair is not expected for that batch. Empty `expected_links` means no paragraph in that batch should link to a claim.

```yaml
schema_version: 1
session_id: nursing-methods-01
split: tuning # tuning | holdout
scenario: "An honest writer connects a clinical finding to a bounded claim."
source_ids: [nursing, sociology_methods]

claims:
  - claim_id: c1
    text: "The observed association is limited to the studied ICU and period."
    anchors:
      - source_id: nursing
        block_ref: "<stable block reference from the pinned source fixture>"

actions:
  - minute: 0
    action: open_source
    source_id: nursing
  - minute: 1
    action: create_card
    card_id: card1
    text: "The study compares outcomes before and after a CNS became head nurse."
    anchor: {source_id: nursing, block_ref: "<stable block reference>"}
  - minute: 2
    action: create_claim
    claim_id: c1
  - minute: 3
    action: type_paragraph
    paragraph_id: p1
    text: "In this ICU, lower mortality followed the CNS appointment, but the before-and-after design limits what can be inferred."

batches:
  - batch_id: b0
    window_start_minute: 0
    changed_paragraph_ids: [p1]
    expected_links:
      - {paragraph_id: p1, claim_id: c1}

expected_receipt:
  bands_by_words: {} # frozen integer counts are filled by a complete golden session
  moments: []
  question_targets: []
```

The sample illustrates the shape only; its illustrative anchors, receipt counts and question labels are not a frozen golden. A real session must use block references generated from the pinned source fixture and independently checked expected receipt values. The initial 15 paragraph-link label seeds are in [mapper_seed_labels.yaml](mapper_seed_labels.yaml); they are draft labels and need a second-person review before they count as frozen gold. The executable session scripts and five held-out cases still need to be authored; holdout labels must come from someone other than the prompt author before use to gate the mapper. Held-out sessions must never be used for tuning.

## Labeling rules

- `expected_links` lists all valid links for changed paragraphs in that batch, not only the link the current model is expected to return. The set is keyed by `(paragraph_id, claim_id)`.
- Link labels describe semantic support in the paragraph and the student's claim map, not provenance, writing order, or whether a claim is true.
- A paragraph can have multiple expected links. Do not add a link merely because the paragraph and claim share words.
- A paragraph that elaborates a claim may still link to it (D-045/D-046). Added reasoning is not a provenance downgrade; it can be a question target, never an origin verdict.
- A pasted paragraph can have a correct semantic link. Provenance bands are asserted separately and still follow the rules in `design/provenance.md`; accepting a map suggestion must never change a pasted sentence into a stronger band.
- Holdout labels are locked before mapper prompt/model tuning. Record the independent labeler's identity and date in the session metadata, not in model-visible content.

## Executable golden sessions (T-015)

The sessions live in [golden/](golden/), one `<session_id>.yaml` each. The pipeline has three parts:

1. **Recorder** (`prototype/web/golden/record.mjs`, Playwright, needs Chromium, runs locally and in CI). It drives the real editor page (the S1 page, `prototype/spikes/S1/page/`) through every *editor* action of a script and writes `golden/recorded/<session_id>.json`: the ProseMirror steps, `input_kind` counts and `doc_hash` the browser produced for each editor action. These recordings are committed.
2. **Ingest builder** (`prototype/server/golden/`). It walks the script in order with an injected clock and posts everything through the real ingest path: student events, batches, checkpoints and submit through the T-012 HTTP API (`create_app` + `TestClient`); server-side events (`coach.ask`, `helper.serve`, `claim.extracted`, `map.suggestion`) through the same `EventService` the API uses, with their real actors. The script’s `source_ids` first register the teacher library through `source.add`, using exact titles and URLs from the local manifest (no URL is fetched). The result is one sealed log per session.
3. **Golden test** (`prototype/server/tests/test_golden_sessions.py`, runs in CI's python job). It rebuilds every log from the YAML plus its recording, runs the real pipeline (replay, mark check, L1, receipt compiler), projects the result and compares it with the frozen `expected_receipt` and `expected_compiled_receipt` in the YAML. It also checks that each recording replays in Python to the browser's `doc_hash` and that two builds give the same chain hashes.

Regenerate after a change to the editor, `web/schema.json` or a script's editor actions: from `prototype/web`, `npm ci && npx playwright-core install chromium && node golden/record.mjs` (all sessions) or `node golden/record.mjs <session_id>`. The test fails with "recording is stale" when a script's editor actions no longer match its recording.

### Script fields

```yaml
schema_version: 1
session_id: thin-honest          # = the file name
split: tuning                    # tuning | holdout
label_status: draft_needs_second_person_review
scenario: "One line on what the session shows."
source_ids: [nursing]
claims:                          # the student's claim texts (mapper labels and claim events use them)
  - {claim_id: c1, text: "..."}
helper_outputs: {h1: "Helper text, verbatim"}         # optional: helper_serve_id -> output (the Helper store)
imports: {imp1: {tool_name: ChatGPT, text: "..."}}   # optional: import_id -> Door raw text
actions: [...]                   # below; `minute` is an int >= 0 and never decreases
batches: [...]                   # optional mapper labels (format above)
expected_receipt: {...}          # frozen; see "Expected receipt"
expected_compiled_receipt: {...} # frozen selected question targets and mechanics from the receipt compiler
```

Block references are the ids in [golden/blocks.json](golden/blocks.json). A quote's text must be an exact substring of its block.

### Actions

Every action has `minute`. The builder's clock for an action is `2026-11-02T14:00:00Z + minute minutes + k seconds`, where `k` counts earlier actions with the same minute. Nothing reads the wall clock.

**Editor actions** (run in Chromium by the recorder; the builder posts one batch with the recorded steps, then the listed events). Paragraph ids are `p1, p2, …` in document order (L1 uses the same names). The document starts with one empty paragraph, `p1`. Naming the next unused id creates that paragraph at the end of the document (Enter at the end of the last paragraph; for `p1`, its empty paragraph).

| action | fields | in the browser | events the builder adds |
|---|---|---|---|
| `type_paragraph` | paragraph_id (new), text, keys? | new paragraph, then type | — |
| `type` | paragraph_id, text, after?, keys? | cursor at the paragraph's end, or right after the first occurrence of `after`; type | — |
| `insert` | paragraph_id, after?, runs: [{text, kind, ref}] | `insertMarked` each run in order (kind: quote, helper, coach, import, paste_ext) | `editor.insert_quote` per quote run, `editor.insert_helper` per helper run |
| `paste` | paragraph_id, text, after? | external paste of `text/plain` with the real clipboard | `editor.paste` (kind external, the recorded paste_id) |
| `replace` | paragraph_id, find, text, keys? | select the first occurrence of `find` in the paragraph, type `text` | — |
| `delete` | paragraph_id, find | select it, Backspace | — |
| `link` | paragraph_id, claim_id, by | `linkParagraph` | — |
| `accept_suggestion` | paragraph_id, claim_id, suggestion_id | `acceptSuggestion` | — |

Typing uses `keyboard.insertText` (one browser input event per action); `keys: true` uses `keyboard.type` (one key event per character).

**Other actions** (builder only):

| action | fields | event (actor; path) |
|---|---|---|
| `open_source` | source_id | `source.open` (student; HTTP) |
| `view_blocks` | source_id, block_ids | `source.view_span` (student; HTTP) |
| `open_pin` | source_id, block_id, pin_kind | `aid.pin_opened` (student; HTTP) |
| `create_card` | card_id, text or parts: [{text, kind: typed\|paste_ext}], via?, via_ref?, anchor?: {source_id, block_ref, quote?} | `card.create`, then `card.anchor` if `anchor` (student; HTTP) |
| `anchor_card` | card_id, source_id, block_ref, quote? | `card.anchor` (student; HTTP) |
| `create_claim` / `edit_claim` | claim_id, text?, card_ids?, parent_claim_id? | `claim.create` / `claim.edit`; text defaults to the `claims` entry (student; HTTP) |
| `set_aside` | source_id, reason_tag, note? | `card.set_aside` (student; HTTP) |
| `declare_import` | import_id | `import.declared` (student; HTTP) |
| `extract_claim` | claim_id, import_id, text | `claim.extracted` (system; service) |
| `coach_ask` | q_id, case, pillar, grounding_ids, question, trigger_ref?, target_span? | `coach.ask` (coach; service) |
| `coach_outcome` | q_id, outcome, parts: [{text, kind: typed\|paste_ext}] | `coach.outcome` with `answer_text` and code-point `origin_runs` (student; HTTP) |
| `helper_serve` | serve_id, request_kind | `helper.serve` (helper; service) |
| `map_suggestion` | suggestion_id, paragraph_id, claim_id | `map.suggestion` (system; service) |
| `map_answer` | suggestion_id, answer (`"yes"`/`"no"`, quoted) | `map.answer` (student; HTTP) |
| `checkpoint` | — | `POST /checkpoint` with the browser's document and hash |
| `submit` | — | `POST /submit`; must be the last action |

The mark check reads its origins from the session: block text from `blocks.json`, Coach answers from the latest `coach.outcome` per `q_id`, imports and Helper outputs from `imports` and `helper_outputs`.

### Expected receipt

`expected_receipt` is the frozen L1 result, written by hand from the script's intent and then checked against the pipeline (never copied from it). All counts are integers.

```yaml
expected_receipt:
  status: complete                # complete | replay_mismatch
  total_words: 0
  mechanics_words: 0              # confirmed Helper-only text, outside the five bands
  bands_by_words: {declared: 0, traced_source: 0, traced_coach: 0, student_linked: 0, untraced: 0}
  bands_by_claims: {declared: 0, traced_source: 0, traced_coach: 0, student_linked: 0, untraced: 0}
  quoted_words: 0
  inferred_links: 0               # links accepted from map suggestions (D12 sub-count)
  map_suggestions: 0
  sentences: {p1: ["student_linked 14", "untraced 9"]}   # per paragraph: "<band> <words>" per sentence
  claim_units: {c1: student_linked, p3: untraced}        # claim units (a linked claim, or an unlinked paragraph)
  notes: {label_not_confirmed: 0, pasted_linked_not_checked: 0}   # sentences carrying each note
  unconfirmed_marks: []           # ["<kind> <ref> <reason>"] for each mark run that failed its check
  moments: []                     # thinking moments without seq/ts, e.g. {kind: set_aside, source_id: x, reason_tag: y}
  question_targets: []            # L1 candidates (the L3b queue): "<sentence_id> <paragraph_id> <reason,reason>"
  facts: {editor_pastes: 0, paste_surviving_chars: 0, cards_with_paste: 0, coach_answers_with_paste: 0,
          declared_claims: 0, declared_claims_anchored: 0}
```

The L1 `question_targets` list is the L3b comparison queue, not the receipt compiler's selected questions. The compiler applies receipt.md §4, grounding checks, and its cap independently. Its stable selections are frozen separately:

```yaml
expected_compiled_receipt:
  status: complete
  questions_pending: false
  mechanics: 0
  question_targets:
    - {paragraph_id: p1, why: student_linked_claim, grounding: [c1]}
```

These expectations are authored from the scenario before checking actual output. Tests also check complete receipt bytes and hashes across builds, stored-artifact recompilation without another model call, pending questions, and chain verification with the issued receipt and its artifacts. The golden stamp fixes its Git identifier; the real lock hash and editor pair are retained. Stub question text is for engineering only and is not evidence of question quality. Mapper labels (`batches`) remain draft and need independent review.

## Current limitations

- The golden set has 12 M1 sessions (T-015), including editing above a linked paragraph and the D-050 reference-list case. The 15–20 session mapper set, the five held-out sessions with independent labels, and the second-person review of every label remain before the mapper evaluation can gate `mapper_enabled` (see `design/evaluation.md` §2a).
- Block references are hand-defined over the S2 corpus because the Docling parser is not installed in this environment; see the note in `golden/blocks.json`.
- The Chromium recorder runs locally and in CI. CI regenerates every recording, checks for differences from the committed files, and reruns the golden tests. Expected receipt assertions are never regenerated.
- The selected open textbook has not yet been used in an executable session; this remains a corpus-completeness gap under D-051.
- Receipt rendering and a human reading the rendered receipts remain T-017 and the M1 exit review.
