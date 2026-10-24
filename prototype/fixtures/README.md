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

The sample illustrates the shape only; its illustrative anchors, receipt counts and question labels are not a frozen golden. A real session must use block references generated from the pinned source fixture and independently checked expected receipt values. The initial 15 paragraph-link label seeds are in [mapper_seed_labels.yaml](mapper_seed_labels.yaml); they are draft labels and need a second-person review before they count as frozen gold. The executable session scripts and five held-out cases still need to be authored; holdout labels must come from someone other than the prompt author before use to tune or gate the mapper.

## Labeling rules

- `expected_links` lists all valid links for changed paragraphs in that batch, not only the link the current model is expected to return. The set is keyed by `(paragraph_id, claim_id)`.
- Link labels describe semantic support in the paragraph and the student's claim map, not provenance, writing order, or whether a claim is true.
- A paragraph can have multiple expected links. Do not add a link merely because the paragraph and claim share words.
- A paragraph that elaborates a claim may still link to it (D-045/D-046). Added reasoning is not a provenance downgrade; it can be a question target, never an origin verdict.
- A pasted paragraph can have a correct semantic link. Provenance bands are asserted separately and still follow the rules in `design/provenance.md`; accepting a map suggestion must never change a pasted sentence into a stronger band.
- Holdout labels are locked before mapper prompt/model tuning. Record the independent labeler's identity and date in the session metadata, not in model-visible content.

## Current limitations

This task selects sources, defines the script/label format and supplies 15 draft mapper-label seeds. The complete hand-authored 15–20 executable session set, independent holdout labels, Playwright generator, ingest builder and frozen expected receipts remain before the mapper evaluation can gate `mapper_enabled` (see `design/evaluation.md` §2a and T-015).
