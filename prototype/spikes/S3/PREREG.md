# Spike S3 preregistration: claim comparison and added propositions

Status: **DRAFT preregistration, not approved and not run.** Task T-007. Written 2026-10-25.
Protocol version `s3-prereg-v1` (candidate; see §7).

Spec: [design/evaluation.md](../../../design/evaluation.md) §1 (S3), §7; [design/provenance.md](../../../design/provenance.md)
§§2, 4–6; D-046, D-050; OL-040. The threshold and the independent labeller are **not locked** by
the current docs. This file states concrete proposed values and marks them pending checker and
founder disposition. Nothing here turns L3b on, authorises a live model run, or creates student
data.

## 1. Question

When a claim-comparison call is given one sentence, one of the student's claim nodes and that
node's anchored passages, does its list of propositions correctly mark what is **in the node or
its anchored passages** and what is **added**?

The failure that matters for the product is a **false-traced** result: the sentence contains a
proposition that the student's claim node and anchored passages do not support, but the call
reports no `added` proposition. With L3b on, that result would let an added proposition sit in a
sentence the receipt calls traced to a source. The mirror error, **false-added** (pure polish or
supporting text marked `added`), produces a false untraced result and is reported and gated as
well.

S3 tests a model method, not a student. It uses authored test text over real licensed source
passages. It is never evidence about real students or about how often second-language writers
add propositions.

## 2. Decision this gates

- **Pass:** L3b may be considered for the pilot, subject to the rest of the pilot gate.
- **Fail, incomplete or missing evidence:** **L3b stays off for the pilot.** Only checked recorded
  chains count as traced and unlinked sentences show "unlinked (not checked)" (CEO-14, CEO-24;
  [design/provenance.md](../../../design/provenance.md) §5).
- S3 passing does not by itself enable L3b in production, does not approve a prompt, and does not
  replace the T-023 harness, the leak check, the walkthrough or the human-session gate.

## 3. Definitions

| Term | Meaning in this protocol |
|---|---|
| **Pair** | One `(sentence, candidate claim node, that node's anchored passages)` unit. It is the unit of a model call and of the human label. |
| **Claim node** | One of the student's claim texts, as in [design/provenance.md](../../../design/provenance.md) §3. The pair manifest supplies its text and ID. |
| **Anchored passages** | The blocks reached through the claim node's cards and anchors. Their full text is supplied with the pair; no other source text is supplied. |
| **Proposition** | One assertable statement in the sentence: one subject-predicate relation, one quantity, one comparison, one attribution, one modal or scope qualifier. Compound sentences are split. |
| **`in_node`** | The proposition is stated by the claim node text, or is explicitly supported by one of the supplied anchored passages. A proposition present in an anchored passage is `in_node` even if the node states it more briefly. |
| **`added`** | The proposition is not stated by the node and not explicitly supported by any supplied anchored passage. This includes a new mechanism, cause, comparison, number, attribution, scope change, or a stronger modal than the node or passages support. |
| **`unclear`** | The annotator cannot decide after applying §6. It is not a silent `in_node`. |
| **Human-positive pair** | At least one human-labelled `added` proposition (after adjudication). |
| **Human-negative pair** | Every human-labelled proposition is `in_node`; no `added` remains. |
| **Unresolved pair** | After adjudication the pair is neither human-positive nor human-negative (for example every proposition is `unclear`). It enters neither primary denominator and is counted in the incomplete rule. |
| **Scoreable pair** | The model returned one schema-valid result after the retry rule in §9. A pair with no valid result is an **error**, not a pass and not a human-negative pair. |
| **False-traced** | Human-positive pair where the model result contains zero `added` propositions. |
| **False-added** | Human-negative pair where the model result contains at least one `added` proposition. |
| **Pair family** | The construction group in §5 (`P1`–`P5`, `N1`–`N3`). Family is hidden from the annotator and is not a model input. |
| **Polished** | A change to grammar, spelling, articles, prepositions, word order, voice or a synonymous wording that does not change the proposition. Awkward but interpretable second-language phrasing is polished, not added. |

### 3.1 What "traced" means here

L3b does not assign a band itself. It supplies proposition statuses to L1. Under
[design/provenance.md](../../../design/provenance.md) §6 and D-050 item 7, an `added` proposition
prevents the traced-source and traced-Coach bands for that sentence. A missed `added` proposition
is therefore a **false-traced** risk. S3 measures the proposition labels, not receipt rendering.

## 4. Pair format and the frozen manifest

Every pair has these stable fields. The manifest is a YAML file (not created by this task) named
`prototype/spikes/S3/pairs.yaml`, and its SHA-256 is frozen in §7 before any model output exists.

```yaml
schema_version: 1
protocol_version: s3-prereg-v1
pair_id: s3-eval-P1-001          # s3-<split>-<family>-<serial>
split: evaluation               # development | evaluation
family: P1                      # see §5; hidden from the annotator
source_id: nursing              # id from prototype/fixtures/sources.yaml
source_version: published_2020
sentence_id: s3e-P1-001-s1
sentence_text: "..."
claim_id: s3e-P1-001-c1
claim_text: "..."
anchors:
  - block_id: nursing.p5.outcomes
    text_sha256: "..."          # SHA-256 of the exact passage text supplied
    text: "..."
pair_sha256: "..."              # canonical hash of the fields above
```

Rules:

- Pair text and the private construction record are authored **before** any model output for
  that pair exists. Human labels are added under §6, also before execution.
- Pair text is authored over the pinned sources in [prototype/fixtures/sources.yaml](../../fixtures/sources.yaml)
  and uses the block IDs in [prototype/fixtures/golden/blocks.json](../../fixtures/golden/blocks.json)
  or an S3 passage file that records the same source ID, version and block ID. No new source or
  licence is introduced by S3 (D-051).
- Pair text is **authored simulation**, not student data. It may be based on the golden sessions'
  scenarios, but no participant is invented and no real student text is used.
- `sentence_text` is a single sentence as produced by the v1 sentence splitter
  (`prototype/server/engine/provenance/sentences.py`). A pair whose text would split into two
  sentences is split into two pairs.
- The claim and anchor texts are supplied verbatim. No truncation is allowed. Any pair whose
  input exceeds 12,000 characters is rejected at manifest freeze, not truncated later.
- `pair_sha256` is recomputed by the harness; a mismatch with the manifest aborts the run.
- The manifest records the intended construction of each pair (family, added proposition IDs as
  authored, wrong-node target if any). That record is **not** the human label; it is used only to
  audit that the authored case matches its stratum. The label comes from §6.

## 5. Sampling plan

Target: **48 evaluation pairs** plus **12 development pairs** (60 authored pairs). Forty-eight
evaluation pairs leaves room above the required 40 without using attrition to change the claim.
Development pairs are used only to write and calibrate the prompt and annotation instructions.
They are never included in the metric.

### 5.1 Evaluation strata

| Family | Pairs | Construction | Expected human label |
|---|---:|---|---|
| **P1** Outside-AI expansion | 8 | A short node; an outside-AI paragraph that keeps much of the node's wording and adds a mechanism, cause, comparison or confidence step (the AI-expanded-card case, OL-040). | Human-positive; at least one `added` |
| **P2** Paraphrase with a stronger claim | 6 | A paraphrase that changes scope, strength, quantity, population or causal direction relative to the node and its passages. | Human-positive; at least one `added` |
| **P3** Honest elaboration beyond the node | 6 | The student's own reasoning, written in the student's words, that goes past the node and its passages. This is not an accusation: D-046 says elaboration is questioned forward. It must still be labelled honestly as `added` for the purpose of the method test. | Human-positive; at least one `added` |
| **P4** Mixed support | 4 | Some propositions are in the node or an anchored passage; at least one is not. | Human-positive; at least one `added` |
| **P5** Wrong-node candidate | 8 | A sentence about source A or claim A, paired with a candidate node and anchors on a different topic or a same-topic different proposition. At least one proposition is absent from the supplied candidate material; in most pairs every proposition is absent. | Human-positive; at least one `added` |
| **N1** Non-native polish | 8 | Authored second-language-style grammar, article, preposition, word-order or translation-shaped phrasing that preserves the node's propositions. Fluency is not a label. | Human-negative; no `added` |
| **N2** Native polish/compression | 4 | Synonym substitution, voice change, sentence combining or compression with the same propositions. | Human-negative; no `added` |
| **N3** Verbatim or near-verbatim support | 4 | Text taken from an anchored passage, or a near quote whose propositions are all in that passage. | Human-negative; no `added` |
| **Total** | **48** | | |

- Scores are reported by family. No family may disappear from the scoreable set: at least 5
  scoreable pairs are required in every family with 6 or more pairs, and at least 3 in P4.
- P3 and N1 are deliberately included because the method's two known harms are (a) treating
  outside-AI expansion as in-node and (b) treating honest or second-language polish as added.
- N1 cases must be reviewed by a person with professional experience teaching second-language
  academic writing, or explicitly marked `authored_simulation_only` in the manifest and in the
  result. They are not evidence about real second-language writers. No real writer is asked to
  produce text for S3.
- P5 wrong-node cases record the intended correct node in the private manifest, but the annotator
  and the model see only the supplied candidate node. The annotator must not infer a different
  node from memory.

### 5.2 Development strata

Twelve development pairs cover the same families (two P1, one P2, one P3, one P4, two P5, two N1,
one N2, one N3). They may be shown to the independent labeller as calibration pairs with
author-written labels (§6.2). They never enter the metric. No development pair may be moved into
the evaluation set after model output is seen.

### 5.3 Selection and ordering

- The manifest assigns each evaluation pair a stable ID before labelling.
- Pair order for annotation and for model calls is the SHA-256 order of `pair_id` with the frozen
  seed string `s3-prereg-v1`; this prevents ordering by family.
- No pair is selected or removed because of its model result. The only allowed exclusion after
  freeze is a pair that fails the manifest-hash check (§4), and then the run is incomplete
  under §11, not silently smaller.

## 6. Independent human labels

### 6.1 Who labels

- The label author is an **independent labeller**: not the founder, not the S3 prompt author, not
  the T-023 implementer, and not anyone who has seen model outputs or taken part in prompt
  iteration for S3.
- Required background: graduate-level academic writing or rhetoric, and experience with
  second-language academic writing for the N1 cases.
- The founder has not supplied a named person. The manifest therefore records
  `labeller_id: INDEPENDENT-LABELLER-1` (a role placeholder) and
  `assignment_status: pending-founder`. The protocol can be approved and the harness built
  without pretending that an independent person has labelled anything.
- The labeller signs a short declaration: no conflict of interest, no model output or prompt seen,
  labels made alone, no discussion of evaluation pairs with the prompt author.

### 6.2 Calibration

- The labeller labels four development calibration pairs without seeing their author labels.
- Agreement with the author labels on at least 3 of 4 pairs (at the pair-positive/negative level)
  is required before evaluation annotation starts.
- If calibration fails, the instructions are discussed and the labeller repeats on four different
  development pairs. Calibration attempts and outcomes are reported.
- Calibration labels are not S3 results and do not enter any denominator.

### 6.3 Annotation procedure

- The labeller receives one row set per pair: sentence text, claim text, anchored passage text and
  the stable IDs. The labeller does **not** receive family, split, model output, prompt, arm
  names, expected labels, aggregate expectations or another annotator's labels.
- The labeller lists every proposition and labels each `in_node`, `added` or `unclear`, with an
  `evidence_block_id` when the support is a specific anchored passage and a reason for every
  `unclear`.
- The labeller records a pair-level label: `added_present`, `no_added` or `unclear`. It must agree
  with the proposition rows; a mismatch sends the pair to adjudication.
- No time limit and no interruption are imposed. Accessibility support is available on request;
  the annotation method must not require dragging, timing or speech.
- Labels are made in [labels.template.csv](labels.template.csv). The template has no filled rows;
  no human labels are fabricated by this task.

### 6.4 Audit, agreement and adjudication

- The manifest fixes **12 audit pairs** before any model output exists: at least two from each
  positive family P1–P3 and P5 (eight), at least one from each negative family N1–N3 (three
  total), and the remainder from P4 (one at minimum). The audit list is not chosen from results.
- A second independent annotator, meeting the same independence rule, labels the audit pairs
  without seeing the first annotator's labels or any model output.
- Agreement is reported as Cohen's κ over proposition labels (`in_node` / `added` / `unclear`) on
  the audit pairs. **Proposed:** κ ≥ 0.60 is required. If κ < 0.60, the labels are not stable,
  S3 is incomplete, and L3b stays off.
- Every disagreement on an audit pair is adjudicated by a third independent person who sees both
  label sets and the pair, but never the model output. The adjudicated label is final.
- For non-audit pairs, the first labeller's labels stand.
- If more than 10% of all propositions are `unclear` after adjudication, S3 is incomplete.
- The role for the second annotator and adjudicator is also `pending-founder`; no name is invented.

### 6.5 The annotation template

[labels.template.csv](labels.template.csv) has a header and **no filled rows**. No labels are
fabricated by T-007. One row is one proposition. The pair-level fields repeat on every row for
that pair and must be identical.

| Column | Filled by | Meaning |
|---|---|---|
| `protocol_version` | harness | `s3-prereg-v1` |
| `pair_id` | manifest | Stable pair ID |
| `split` | manifest | `development` or `evaluation`; the annotator sees only evaluation rows, except calibration |
| `family` | manifest | `P1`–`P5` or `N1`–`N3`; **removed from the annotator view** |
| `source_id`, `source_version` | manifest | Source attribution |
| `sentence_id`, `claim_id` | manifest | Stable IDs |
| `anchor_block_ids` | manifest | Semicolon-separated block IDs |
| `pair_sha256` | manifest | Consistency hash of the pair |
| `sentence_text`, `claim_text`, `anchor_text` | manifest | Exact supplied text; `anchor_text` joins blocks with ` || ` |
| `proposition_id` | annotator | Stable within pair, `q1`, `q2`, … |
| `proposition_text` | annotator | One proposition from the sentence |
| `label` | annotator | `in_node`, `added` or `unclear` |
| `evidence_block_id` | annotator | A supplied block ID when the support is a passage; empty otherwise |
| `unclear_reason` | annotator | Required for `unclear`: `ambiguous_scope`, `missing_context`, `disputed_parse` or `pair_error` |
| `pair_label` | annotator | `added_present`, `no_added` or `unclear`; must agree with the proposition rows |
| `annotator_role`, `annotator_id` | annotator | `INDEPENDENT-LABELLER-1`, `AUDIT-ANNOTATOR-1` or `ADJUDICATOR-1` |
| `annotation_date` | annotator | Absolute ISO date |
| `revision` | annotator | Starts at 1; adjudication changes `adjudicated_label`, not the first label |
| `adjudicated_label` | adjudicator | Final label for audit pairs; empty for non-audit rows |
| `adjudicator_id`, `adjudication_date` | adjudicator | Set only when adjudicated |
| `notes` | annotator/adjudicator | Short reason; no model output, no student data |

The harness rejects a file with a blank `label`, a missing `pair_label`, a pair whose rows
disagree on pair-level fields, or a label outside the allowed values.

### 6.6 What the annotator must not do

- Do not reward fluent prose or penalise awkward prose. N1 exists to test exactly this.
- Do not use outside knowledge about the topic. Only the supplied node and passages define
  `in_node`.
- Do not decide whether the student was honest, whether outside AI was used, or what the receipt
  should say. Those are not S3 labels.
- Do not change a label after seeing model output.

## 7. Frozen split and version

Before any model call, the harness writes `prototype/spikes/S3/FROZEN.json` and refuses to run if
any hash differs. It records at least:

```json
{
  "protocol_version": "s3-prereg-v1",
  "frozen_at": "YYYY-MM-DDTHH:MM:SSZ",
  "pairs_sha256": "...",
  "labels_sha256": "...",
  "audit_pairs_sha256": "...",
  "prompt_sha256": "...",
  "prompt_template_path": "prototype/spikes/S3/prompt.v1.txt",
  "prompt_template_sha256": "...",
  "decoding": {"temperature": 0, "top_p": 1, "max_output_tokens": 800, "seed": null},
  "backends": ["deepseek", "openai_compat"],
  "model_ids": {"deepseek": "...", "openai_compat": "..."},
  "schema_sha256": "...",
  "code_commit": "...",
  "independent_labeller": {"id": "INDEPENDENT-LABELLER-1", "assignment_status": "pending-founder"},
  "calibration": {"status": "not-run", "pairs": 4, "agreement": null},
  "audit_kappa": null
}
```

- The development/evaluation split is frozen with the manifest. No pair moves between splits.
- If the prompt, model, decoding, schema, pair text, anchor text, labels, audit list or code
  changes, the version becomes `s3-prereg-v2` (or later) and all hashes are re-frozen. A version
  bump after evaluation output exists is a **new evaluation**, not a revision of the old result.
- One frozen version is executed once per backend. Re-runs after an infrastructure failure are
  allowed only with the identical frozen inputs and are reported as re-runs; results from the
  first valid complete run are the S3 result. No prompt tuning, threshold change or pair removal
  after evaluation output exists.
- The manifest, labels, prompt, FROZEN.json and result report are committed. Raw model responses
  are stored with the run and are not interpreted as student data.

## 8. Model, prompt and call settings

### 8.1 Backends

**Proposed:** both configured backends (`deepseek` and `openai_compat`) run the same frozen
prompt, schema and pairs, and **each must pass §11 independently**. If the second backend is not
available for the evaluation, S3 is incomplete and L3b stays off. This follows the product's
both-backends habit for model-dependent gates; it is not currently written into evaluation.md, so
the checker/founder must dispose of it (PD-T007-3).

### 8.2 Prompt

- New task id `claim_compare` (already in the LLM task enum; the current provisional output schema
  is `{"relation": "same|related|different"}` and is **not** the L3b shape). T-023 replaces the
  provisional schema with the proposition schema below. S3 does not edit code.
- System prompt requirements:
  - Compare one sentence with one claim node and that node's anchored passages.
  - List every proposition in the sentence.
  - Mark each proposition `in_node` only when the node or a supplied anchored passage states or
    explicitly supports it; otherwise `added`.
  - Use no outside knowledge; do not judge the writer, the provenance of the text or whether the
    claim is true.
  - Do not rewrite the student's sentence or add propositions not in it.
  - Return JSON only.
- User payload is JSON with `sentence_id`, `sentence_text`, `claim_id`, `claim_text` and
  `anchors: [{block_id, text}]`. No names, log IDs, arm names, family labels or model outputs.
- Few-shot examples, if any, come only from development pairs and are part of the hashed prompt.
  No evaluation pair appears in the prompt.
- The prompt template is stored at `prototype/spikes/S3/prompt.v1.txt` and hashed. It is not
  written by T-007.

### 8.3 Output schema

```json
{
  "sentence_id": "s3e-P1-001-s1",
  "claim_id": "s3e-P1-001-c1",
  "propositions": [
    {"text": "...", "status": "in_node", "evidence_block": "nursing.p5.outcomes"},
    {"text": "...", "status": "added", "evidence_block": null}
  ]
}
```

- `propositions` has at least one item. `text` is non-empty and is a proposition from the sentence,
  not a summary of the whole pair.
- `status` is exactly `in_node` or `added`.
- `evidence_block` is one of the supplied `block_id` values or `null`; it is required for an
  `in_node` proposition that is supported by a passage rather than by the node text, and may be
  `null` when the node text itself states it.
- Echoed IDs must match the pair. Extra fields are rejected. Any other shape is a schema error.
- The harness validates the response before scoring; a schema error is retried under §9.

### 8.4 Decoding

Temperature 0 (or the backend's documented minimum, with the exact value frozen), `top_p` 1,
`max_output_tokens` 800, no streaming, no tools, no retrieval beyond the supplied pair. If a seed
parameter is supported, freeze one seed; if not, record `seed: null` and run each backend once.

## 9. Retry, error and missing-result treatment

- At most **three attempts** per pair per backend.
- Retry on: transport/timeout, rate limit (with backoff), 5xx, and schema-invalid or empty output.
  Use fixed backoff of 2 s then 8 s with jitter. The prompt is byte-identical on every attempt.
- Do not retry a valid response, and do not alter the prompt, temperature or model between
  attempts.
- Authentication failure aborts the run as incomplete. A provider refusal is recorded as an error;
  it is not converted to `in_node` or `added`.
- A pair with no valid result after three attempts is an **error**. Errors are never imputed,
  never dropped into a human-negative pair and never counted as a pass.
- **Incomplete conditions:** more than 8 of 48 evaluation pairs are errors, or more than 4 pairs
  are unresolved after adjudication, or any family with 6+ pairs has fewer than 5 scoreable
  human-resolved pairs, or P4 has fewer than 3. Incomplete means S3 did not pass; L3b stays off.
- Every error, attempt count, error class and elapsed time is listed in the result report. No
  silent replacement of a failed pair.

## 10. Metrics

All rates are reported with numerator and denominator. Intervals are one-sided 95% Wilson upper
bounds unless stated otherwise. "Rate" here means a share of labelled pairs, not a model score.

Let:

- `H+` = human-positive scoreable pairs; `H-` = human-negative scoreable pairs.
- `FT` = number of `H+` pairs with zero model `added` propositions (false-traced).
- `FA` = number of `H-` pairs with at least one model `added` proposition (false-added).

Primary:

- **False-traced rate** = `FT / |H+|`.
- **False-added rate** = `FA / |H-|`.

Secondary, reported but not gating:

- Per-family false-traced and false-added counts and rates.
- Proposition-level recall of human `added` propositions on the 12 audit pairs. Match a model
  proposition to a human proposition by normalised token-set Jaccard ≥ 0.80; report matches,
  misses and unmatched model propositions. This is descriptive only because proposition
  segmentation can differ.
- The count of pairs where the model returns no `added` and no `in_node` after adjudication.
- The number of `unclear` human propositions and pairs excluded for that reason.

No aggregate is calculated by pooling propositions across pairs; the pair is the sampling unit.

## 11. Pass rule (fixed before execution)

**Primary bar (proposed, pending checker/founder):**

1. `|H+| ≥ 24` and `|H-| ≥ 12`, and at least 40 of the 48 evaluation pairs are both scoreable and
   human-resolved, with every family represented as in §9.
2. False-traced rate ≤ **10%**, and its one-sided 95% Wilson upper bound ≤ **20%**.
3. False-added rate ≤ **15%**, and its one-sided 95% Wilson upper bound ≤ **35%**. This guard
   prevents an "always added" method from passing the primary bar trivially.
4. No family with at least 6 scoreable pairs has a false-traced rate above **25%** (positive
   families) or a false-added rate above **25%** (negative families).
5. Both backends meet 1–4 independently.

**PASS** only when all five hold. Otherwise **FAIL**. Missing evidence, an incomplete run, a
κ below 0.60, more than 10% `unclear` propositions, or a hash mismatch is **FAIL** for the L3b
gate; it is never treated as a pass by default.

These numbers are a proposal. They are not a locked product rule. If the founder sets different
numbers, the version becomes `s3-prereg-v2` before execution and the change is recorded, with its
rationale, before any evaluation output exists.

## 12. Execution and reporting

1. Author the 60 pairs, freeze the manifest, the 12 audit pairs and the 48/12 split.
2. Obtain the independent labeller assignment and the declaration; run calibration.
3. Label evaluation pairs under §6; run the audit and adjudication; compute κ.
4. Write `FROZEN.json` with every hash in §7; confirm the prompt and schema are the frozen ones.
5. Run each backend once with `ROOM_LLM` set to the evaluation backend; no live call is made by
   ordinary tests. Record the command, environment, model ID, start/end time and code commit.
6. Validate every output against §8.3; apply §9; compute §10; apply §11 once.
7. Write `prototype/spikes/S4`-style result note at `prototype/spikes/S3/RESULT.md` with:
   the frozen version and hashes; the verdict; the numerator/denominator and interval of every
   metric; the per-family table; the per-pair table including label and result; all errors and
   retries; the labeller declaration and calibration/audit agreement; the exact limitations; and
   a statement that the result is simulated and not evidence about students.
8. If the verdict is PASS, update the handoff and leave L3b **off** until the founder/checker
   separately authorise the pilot. If FAIL or incomplete, L3b stays off and the result note says
   so in its first line.

No result may be reanalysed with a new threshold. A different threshold or prompt requires a new
version and a new run.

## 13. What this protocol cannot establish

- The pairs are authored simulated text, not real student writing. Results say nothing about real
  students, real second-language writers, or how often added propositions occur.
- The N1 cases are authored second-language-style edits, not a sample of second-language writers.
  They test whether fluency biases the label; they do not measure fairness. The human-session stop
  rule and pilot measures remain separate (evaluation.md §4–§5).
- One topic area (Hong Kong housing) and the four fixed sources would limit generalisation; the
  sampling plan deliberately uses all four sources, but the report must still state the topic and
  source mix.
- The S3 pairs give the model one candidate node. Candidate selection (all nodes, or top 5 by
  BM25, D1) is **not** tested here and belongs to the L3b integration, not to S3.
- S3 does not test receipt wording, question quality, accessibility, latency or cost.
- S3 cannot show that L3b is safe for a student's own honest elaboration. P3 only measures whether
  the method identifies the added proposition; D-046 still governs how it may be used (a pillar
  question, never an accusation).
- No live model call, model key or student record is used in this task.

## 14. Pending human inputs

- Named independent labeller, second annotator and adjudicator (founder).
- Approval of the §11 thresholds (founder/checker).
- Approval of both-backends requirement and model IDs (founder/checker).
- Confirmation that the non-native cases may be authored simulation or that a qualified reviewer
  will be supplied.
- Approval of the prompt and the replacement `claim_compare` output schema before T-023.
