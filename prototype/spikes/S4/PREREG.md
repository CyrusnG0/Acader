# Spike S4 preregistration: do bands match known simulated behaviour?

Status: **DRAFT preregistration, not approved and not run.** Task T-007. Written 2026-10-25.
Protocol version `s4-prereg-v1` (candidate).

Spec: [design/evaluation.md](../../../design/evaluation.md) §1 (S4), §7; [design/provenance.md](../../../design/provenance.md)
§§3, 4, 6–7; D-050; result notes in [writing-room-kit/RESULTS-v0.4.md](../../../writing-room-kit/RESULTS-v0.4.md)
and [writing-room-kit/RESULTS-v0.5.md](../../../writing-room-kit/RESULTS-v0.5.md). The current
docs give S4's expectation in one line ("C1 mostly traced; C4's outside parts untraced or
declared; C11's gaps explainable"). This file makes that line executable and names where the
current v1 band rules force an interpretation. Thresholds and interpretations below are
**proposed** and pending checker/founder disposition.

S4 is a check on band accounting in **known simulated behaviour**. It is never evidence about
real students, and it does not test whether the system can tell where text came from.

## 1. Question

Given the kit's known arms, and a frozen mapping from their available fields into v1 concepts, do
the v1 bands put the words where the construction says they belong?

- The **C1** honest runs: the student read, chose, wrote and cited. Does most of the work end up
  in a checked chain rather than in the untraced band?
- The **C4** partial-outside runs: about half the body paragraphs were written outside and
  retyped, never discussed. Are those paragraphs untraced (or declared), while the student's own
  paragraphs are chain-present?
- The **C11** runs: an honest but thin recorded trail. Are the gaps visible and explainable rather
  than hidden inside a traced band?

## 2. What S4 can and cannot show

S4 can show whether the **band rules, denominators and explanations** behave as intended on a
known construction. It cannot show that the engine can recover that construction from the writing:
the v0.4 runs have no v1 origin marks, paragraph links, claim nodes, cards or Helper text. The S4
mapping therefore **supplies** those objects from a frozen rule (§5). S4 tests the accounting, not
inference. This distinction must appear in the result's first screen.

## 3. Exact available inputs

Only committed files in this repository are used. No URL is fetched; no source is licensed by this
task.

| Input | Path | Fields used |
|---|---|---|
| C1 runs, 6 | `writing-room-kit/v04/runs/C1-1.json` … `C1-6.json` | `id`, `arm`, `essay`, `citations`, `struct`, `drafts`, `turns`, `read_passages`, `unlocked_docs`, `counters`, recorded word total |
| C4 runs, 6 | `writing-room-kit/v04/runs/C4-1.json` … `C4-6.json` | same fields |
| C11 runs, 6 | `writing-room-kit/v04/runs-v05/C11-1.json` … `C11-6.json` | same fields |
| Session mirrors | `writing-room-kit/v04/sessions/C1-*.json`, `C4-*.json`, `writing-room-kit/v04/sessions-v05/C11-*.json` | cross-check only; they mirror the run fields and add no per-paragraph origin |
| Source passages | `writing-room-kit/data/corpus.json` | `id` (`D1`…`D12`), `paras`; block ID `DxPy` = document `Dx`, paragraph `y` (1-based) |
| C1/C4 arm rules | `writing-room-kit/v04/arms/C1.md`, `C4.md` | construction intent |
| Arm definitions | `writing-room-kit/PREREG-v0.4.md` (C1, C4); `PREREG-v0.5.md` §B.1 (C11) | arm rules and the C11 name |
| Known results, context only | `writing-room-kit/RESULTS-v0.4.md`, `RESULTS-v0.5.md` | arm descriptions; not inputs to the mapping or the pass rule |

**Missing input, stated plainly:** there is no record in these files of which C4 paragraphs were
written outside. The arm says the student replaced about half the body paragraphs and retyped
them; the run stores only the final essay and the student's drafts. The construction note in §5.2
is therefore a frozen **evaluation annotation**. It is never fed to the engine.

## 4. Known behaviour of each arm

| Arm | Kit definition | Trait relevant to v1 |
|---|---|---|
| **C1 honest** | Sonnet worker; 15–30 turns; picks with reasons, reads passages, states claims, saves two drafts, writes 500–800 words with at least six citations (PREREG-v0.4). `struct.kind = typed`. | Full student trail and citations. For S4, every paragraph is the student's own and is linked. |
| **C4 partial outside** | Lighter honest process, one draft, then about half the body paragraphs are replaced with an outside writer's paragraphs and **retyped**; never discussed (PREREG-v0.4). `struct.kind = retyped`. | Retyping leaves no v1 origin difference: all text is `typed`. The outside paragraphs are known only through the frozen construction note. |
| **C11 honest, DeepSeek operator** | DeepSeek operator, no essay supplied, the C1 instructions; writes its own drafts and final essay through the tool (PREREG-v0.5 §B.1). `struct.kind = typed`. All six runs record **0 claim statements** and **0 saved drafts**. | The final essay exists, but no claim was stated in the recorded trail. In v1 terms this is a **thin recorded trail**: no claim node, no paragraph link. `evaluation.md` calls it "thin honest"; `PREREG-v0.5` calls it `honest-ds`. S4 uses the run definition and records both names. |

## 5. Mapping into current engine concepts

The mapping is deterministic and frozen before any engine output. Its code path is
`prototype/spikes/S4/adapter.py` (to be built by a later task; this task only freezes the rule).
The adapter may use the real ingest path (`prototype/server/golden/build.py` patterns) but must
not call a live model. `ROOM_LLM=stub`; `L1Config(l3b=False)`.

### 5.1 Document and origins

1. Read `essay`; split on blank lines (`\n\s*\n`); trim; drop empty paragraphs. Paragraph IDs are
   `p1, p2, …` in order.
2. Every character is `typed`. There are no `quote`, `coach`, `helper`, `import` or `paste_ext`
   marks, no editor paste events and no Helper output. Inline citation tokens such as `[D1p1]`
   remain ordinary typed text; they are **not** quotes and are not turned into marks.
3. Sentences are split with the v1 splitter
   (`prototype/server/engine/provenance/sentences.py`). Words are the engine's `\S+` count on
   non-mechanics sentences. These are the denominators.

### 5.2 Claim, card and link construction

| Arm / paragraph | Claim node | Cards and anchors | Paragraph link |
|---|---|---|---|
| C1, every paragraph | `c<paragraph-number>` with text = the paragraph's **first sentence** in the student's words | For each distinct citation token `[DxPy]` in the paragraph, one card whose text is the sentence containing that token, anchored to block `DxPy` from `corpus.json` | `by = student` |
| C4, own paragraph | same as C1 | same as C1 | `by = student` |
| C4, outside paragraph | none | none | none |
| C11, every paragraph | none | none | none |

- "Own" for C4 comes from the frozen construction note. Rule: compute
  `difflib.SequenceMatcher(None, final_paragraph, draft_paragraph).ratio()` against every
  paragraph in every saved draft for that run. A final paragraph is **own** when the maximum
  ratio is **≥ 0.50**, otherwise **outside**. The note records the paragraph index, the best
  matching draft paragraph, the ratio and the resulting class. It is frozen by SHA-256 before any
  engine output. C4 has one draft in every run, so the rule is defined for the available files.
- A C4 run is **conforming** when the note finds at least two outside body paragraphs, matching
  the arm rule. All six runs are used if they conform; a non-conforming run is reported and
  excluded from the pooled pass, and C4 pass requires at least five conforming runs.
- C11 is **conforming** when `counters.claim_statements == 0` and `drafts` is empty. All six
  current runs meet this. A future C11 run that records claims would use the C1 mapping and is not
  part of this frozen S4 set.
- If a cited block ID is absent from `corpus.json`, the pair/run is an adapter error and is
  reported; the adapter does not invent a block. The run is not silently changed.
- The claims are constructed from the student's own first sentences. This is a **simulation
  mapping**, not a record that the student created those claims. No wording is generated by a
  model. If an outside paragraph contains citations, they are ignored for links; the paragraph
  stays unlinked.

### 5.3 Sealed session and L1

1. Post the typed document, the claims, cards, anchors and links through the real event-ingest
   path with a fixed clock. One sealed log per run.
2. Run `compute_l1(doc, runs, events, config=L1Config(l3b=False))`. No L3 call, no live provider,
   no mapper, no Coach or Helper output.
3. The engine stamp records the code commit, lock hash, `web/schema.json` hash and the frozen
   config. Same commit and inputs must give the same receipt bytes (D20, D31).
4. The construction note is joined to the result **after** L1, only for evaluation. It is not in
   any event and cannot change a band.

## 6. Denominators

- **Word denominator:** `bands["total_words"]`, the engine's word count over all non-mechanics
  sentences. It must equal the sum of `bands["by_words"]` across the five bands. The kit's
  recorded word total is reported beside it for reconciliation; the engine's count is the
  denominator. Citation tokens count as words because they are text.
- **Mechanics (D-050):** `bands["mechanics"]` must be **0** for every run. D-050 excludes
  sentences made entirely of confirmed Helper text from the word and claim counts. These runs have
  no Helper output and no confirmed Helper text, so no sentence can qualify. A typed reference
  list, if one were present, would remain ordinary text and is not "mechanics"; S4 notes this
  rather than inventing a Helper mark.
- **Claim-unit denominator:** one unit per paragraph. A linked paragraph is a claim unit keyed by
  its claim ID; an unlinked paragraph is a paragraph unit keyed by its paragraph ID. Every C1 and
  C4-own paragraph is linked to its own claim; C4-outside and C11 paragraphs are unlinked. Thus
  `sum(bands["by_claims"])` equals the number of non-empty paragraphs in the run.
  This is a **paragraph proxy** for the student's claim map, not the map itself; the v0.4 files do
  not record claim nodes. It is labelled as a proxy in every table.
- **Sentences and notes:** report sentence count, per-sentence band, `notes`, `chain_break` and
  the L3b comparison queue (`sentence_id`, `reasons`). No sentence may be missing a band or a
  reason.
- **Quoted words:** `bands["quoted_words"]` must be 0 because §5.1 supplies no quote marks. It is
  reported, not gated separately.

## 7. Expected behaviour and pass rules

Metrics per run and pooled per arm. "Chain-present" means `traced_source + traced_coach +
student_linked`; it never means "traced" on its own. Pooled means summing integer word counts
across the six runs, then dividing; per-run shares are also reported.

### 7.1 C1 honest: mostly chain-present, no untraced wall

Expected mapping: all paragraphs linked; all text typed; no quote marks; L3b off.

- Every sentence is band 4 `student_linked` because a paragraph link exists and nothing confirms
  it; no sentence is `traced_source` or `traced_coach` without a checked quote, Coach mark or L3b.
- `declared = 0`, `untraced = 0`, `mechanics = 0`, `quoted_words = 0`.

**Pass (proposed):**

1. Pooled `chain_present / total_words ≥ 0.80`.
2. Pooled `untraced / total_words ≤ 0.20`.
3. Every run has `declared = 0` and no sentence with `label_not_confirmed` or
   `pasted_linked_not_checked`.
4. `traced_source + traced_coach` is **reported but not gated**; with L3b off and no quote marks,
   the expected value is 0. See PD-T007-4: `evaluation.md`'s "C1 mostly traced" is read here as
   "mostly in a checked chain", not as "mostly `traced_source`".

### 7.2 C4 partial outside: outside paragraphs untraced, own paragraphs chain-present

Expected mapping: outside paragraphs have no claim, no card and no link; own paragraphs are linked
as in C1.

- Every outside paragraph: all its sentences are `untraced`.
- Every own paragraph: all its sentences are `student_linked`.
- `declared = 0`, `mechanics = 0`, `quoted_words = 0`.
- The pooled `untraced` word share should equal the construction note's pooled outside word share.

**Pass (proposed):**

1. Every outside paragraph is 100% `untraced`; no outside paragraph contains a `traced_source`,
   `traced_coach` or `student_linked` sentence.
2. Every own paragraph is 100% `student_linked`.
3. Pooled `untraced` word share is within **±10 percentage points** of the pooled outside word
   share from the construction note.
4. Each run's `untraced` share is within **±15 percentage points** of that run's outside share.
5. At least five C4 runs are conforming; all six are reported.
6. `declared = 0`; `mechanics = 0`.
7. The report states that the engine did **not** infer the outside paragraphs; the note told the
   mapping where they are.

### 7.3 C11 thin recorded trail: gaps explainable

Expected mapping: no claims, no cards, no links.

- Every sentence is `untraced`.
- Every sentence is in the L3b comparison queue with reason `unlinked` (all characters are typed,
  so the 30% typed rule in `provenance.md` §4 is met).
- `declared = 0`, `mechanics = 0`, `quoted_words = 0`, `traced_source = traced_coach = 0`.
- `chain_break = "no_link"` for each sentence.

**Pass (proposed):**

1. Pooled `untraced / total_words ≥ 0.90`.
2. Every run has `untraced ≥ 0.80`.
3. Every untraced sentence appears in the L3b queue with reason `unlinked`.
4. `declared = traced_source = traced_coach = 0`.
5. The report's first screen explains that this is a thin recorded trail, not a rating of the
   student and not a finding about outside AI.

### 7.4 Accounting checks (all runs)

1. `total_words == sum(by_words)`.
2. `mechanics == 0`.
3. `sum(by_claims) == number of non-empty paragraphs`.
4. Every sentence has exactly one band and a non-empty `chain_break` or an existing chain.
5. No sentence has `quoted_words > 0` when no quote mark was supplied.
6. The same commit and inputs produce the same receipt hash on two builds.

A failure of any accounting check is a **FAIL**, even if the arm shares look right.

### 7.5 Verdict

**S4 PASS** only when C1, C4 and C11 pass §7.1–§7.3 and all accounting checks in §7.4 pass.
**Otherwise FAIL.** A FAIL is a finding about the mapping or the band rules; it does not turn L3b
on or off by itself. It must be resolved before the M2 walkthrough. Missing runs, a hash mismatch,
an adapter error or fewer than five conforming runs in an arm makes the arm **incomplete**, which
is reported as not-passed.

These thresholds are proposed, not locked. They are frozen before the S4 run.

## 8. Explanatory review rubric

A person reads the S4 report (not only the aggregate) and answers yes/no for every run:

1. Is every sentence assigned one band, and is its chain or break reason shown?
2. Does every untraced sentence carry an explainable reason (`unlinked`, pasted, unconfirmed, or
   a named break) and, where applicable, appear in the comparison queue?
3. Do the construction-note classes match the bands: outside → untraced, own → chain-present, no
   claims → untraced?
4. Is any traced band present without a checked origin mark or a confirmed link? (Expected: none.)
5. Do the word and claim-unit totals reconcile (§7.4)?
6. Does the report say "simulated", "not evidence about real students" and "untraced is not AI" in
   plain words on its first screen?
7. Are the limitations in §10 present and accurate?

A "no" is recorded against the run and blocks PASS if it affects a §7.1–§7.4 line. Wording or
layout findings that do not affect a gated line are recorded for the walkthrough, not silently
waived.

## 9. Reporting format

The result note is `prototype/spikes/S4/RESULT.md`, written by the later S4 task, with a machine-
readable `prototype/spikes/S4/results.json` beside it. Required content:

- Frozen protocol version, commit, adapter hash, mapping/construction-note hash, engine stamp.
- Verdict on the first line.
- Per-arm table: runs, pooled words, each band's words and share, mechanics, quoted words, claim
  units, chain-present share, untraced share.
- Per-run table with the same fields and pass/fail per §7.
- Per-paragraph table: paragraph ID, construction-note class, band, words, chain/break reason.
- Excluded or non-conforming runs, with reasons; no silent drop.
- Error log (adapter or ingest failures).
- Calibration: none; the reviewer is a person, and the human reading is recorded separately.
- Exact commands and environment, so the result can be reproduced with `ROOM_LLM=stub`.
- Limitations verbatim from §10, plus any new one found.
- A statement that no live model call was made.

No result may be recalculated with a different threshold after the run. A mapping change requires
`s4-prereg-v2` and a new freeze.

## 10. Limitations of the simulation

- **Simulated students, tiny n.** Six runs per arm, one essay question, one fictional Hong Kong
  housing archive, same team. Nothing here is evidence about real students or real classes.
- **v0.4 predates v1 provenance.** There are no origin marks, paragraph links, claim nodes, cards,
  quote marks, Helper outputs or editor paste events in the run files. The adapter authors those
  from §5; S4 tests band accounting, not whether the engine can recover them.
- **C4 outside paragraphs are not recorded.** They are identified by a frozen draft-similarity
  note. The engine sees typed text with no link. S4 must not claim that L1 found the outside
  paragraphs.
- **Retyping is a stated blind spot.** The C4 arm retyped the outside paragraphs. In v1 those
  characters are `typed`, so origin alone cannot separate them; only the absence of a link and
  claim does. The report must say this plainly.
- **No L3b.** Student links stay band 4. `traced_source` is expected to be zero in C1 even though
  `evaluation.md` says "mostly traced". See PD-T007-4.
- **No D-050 mechanics case.** The v0.4 corpus has no Helper text, so `mechanics = 0` by
  construction. S4 verifies the denominator exists and is zero; it does not test reference-list
  mechanics. The T-015 `reference-list` golden does that separately.
- **No quotes.** Citation tokens are typed text, not quote marks. `quoted_words = 0`; S4 does not
  test the quote rule.
- **Claim units are a paragraph proxy.** v0.4 has no claim map. `bands_by_claims` counts linked
  paragraphs as claim units and unlinked paragraphs as paragraph units; it cannot validate the
  student's actual claim structure.
- **C11 name.** `evaluation.md` calls C11 "thin honest"; `PREREG-v0.5` calls it `honest-ds`. S4
  uses the run definition (DeepSeek operator, 0 claim statements) and records both names. Its low
  kit scores are not a rate of honest behaviour.
- **Not the D-051 corpus.** S4 uses the kit's fictional corpus, not the real licensed sources, and
  does not test parsing or source licensing.
- **No fairness, accessibility, latency, cost or question-quality evidence.**

## 11. Pending dispositions

- S4 thresholds and the construction-note rule (checker/founder).
- The "C1 mostly traced" interpretation and whether "traced" in `evaluation.md` means
  chain-present or `traced_source` only (checker/founder).
- The paragraph-proxy claim units (checker/founder).
- The C11 naming reconciliation (checker/founder).
- The added-proposition band wording in `provenance.md` §5 versus §6/D-050 item 7 (checker/founder).
- The adapter implementation and the S4 human read (a later task; not this preregistration).
