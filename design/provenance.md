# Provenance: chains, bands and the cheap pipeline

Status: **reviewed (CEO + eng) 2026-10-23** · Last updated: 2026-10-25
Implements: D-025 (proportions are about recorded traces, never "% AI"), law 5; D-050 (confirmed Helper mechanics); CEO-3, CEO-13, CEO-14, CEO-17; D1, D5, D17, D20, D26, D27, D29, D31 ([eng record](../docs/designs/eng-review-v1.md)). Answers OL-031 (derivation half) and OL-040.

## 1. The professor's question

> "What can tracking and diffs give us? We can't save every snapshot and give everything to an AI."

- **Origins are recorded, then checked.** The UI channel that put text into the document labels it ([event-log.md](event-log.md) §4); engine/ checks every non-typed label against its source at compile time (§4.1).
- **Meaning is inferred, only where it matters, and only if the method passed its test.** The LLM compares specific flagged sentences with the student's own claims (L3b), and only if spike S3 passed (CEO-14).

Cost scales with flagged sentences, not with keystrokes or snapshots.

## 2. What we can and can't establish

| Recorded and checked (fact) | Inferred (with error, shown as such) | Not knowable |
|---|---|---|
| Which source passages were opened and anchored | Whether a sentence states the same claim as a claim node (L3b, only if S3 passed) | Where untraced text came from |
| The origin mark on every character, and whether it matches its source | Whether two paragraphs contradict (L3c) | Whether in-platform work was driven by an outside AI (relay) |
| Every paste (in the editor, cards and Coach answers), its size, and how much survives | | What the student understands (only the conversation shows that) |
| Every Coach question and its outcome; declared imports | | |

## 3. Data model

```
Source ─< Block {page, kind, bbox, text}
IdeaCard {text (student's words, paste-tracked)} ─ anchor ─> Block
ClaimNode {text (student's words)} ─ supported_by ─> IdeaCard | DeclaredClaim
DeclaredClaim {text (import's words), import_id}
Sentence {range in final doc, origin mix, paragraph links} ─ expresses ─> ClaimNode
Chain(sentence) = Sentence → ClaimNode → IdeaCard → Block      (or broken at the first missing link)
```

- The **claim map** is the student's own mind map: claim nodes in their words, linked to cards and to each other.
- A **link to a claim belongs to the paragraph** (D-045; event-log §4): every sentence in a paragraph shares the paragraph's links, so typing, rewording or adding elaboration never cuts a link. `by = student` means the student linked it; `coach`/`import` means the paragraph was created from a Coach answer or import carrying the claim.

## 4. Pipeline

| Layer | What | Runs | Cost |
|---|---|---|---|
| **L0 capture** | Events, origin marks and paragraph links | Browser → staging → chain | ~0 |
| **L1 deterministic** | Replay steps (prosemirror-py); **mark check** (§4.1); sentence split; origin mix per sentence; chains from paragraph links; reading facts; paste stats; Coach outcomes; set-asides | engine/, plain code | ~0 |
| **L3b claim compare** | Only if S3 passed. For each flagged sentence: list its propositions; mark each `in_node` or `added` against the candidate claim node and that node's anchored passages. Candidates: all of the student's claim nodes, or the top 5 by BM25 when there are more than 5 (D1) | Job, LLM | scales with flags |
| **L3a / L3c / L3e** | Claim extraction from imports; contradiction between paragraph claims; receipt questions | Job, LLM | a few calls |

Every L3 response is stored as a compile artifact (task, prompt hash, body, hash) and cited by the receipt lines it produced (D31). There is **no L2 embedding layer in v1** (D1; TODOS).

**Which sentences are "flagged"** (go to L3b when it is on):
- in a paragraph with no link, and at least 30% of its characters are `typed` or `paste_ext` **[ASSUMPTION: tune on golden sessions; the value is in the receipt's engine stamp, D20]**
- any sentence whose claim node was edited after the sentence last changed
- any sentence in a paragraph with a `by = student` link (CEO-17)
- any sentence with ≥ 50% `paste_ext` characters, even if linked

### 4.1 Mark check (D5, D29)

At compile, before banding, engine/ checks every non-typed run:
- `quote`: each contiguous run must match the text of **its own** `block_id` (whitespace and quote characters normalised) and be at least 4 words, or the whole block.
- `coach`: the run must be inside that q_id's recorded answer, and only the answer's **typed** parts count; parts recorded as pasted into the answer stay `paste_ext` (D26).
- `import`: inside that import's raw text. `helper`: inside that serve's output.

A run that fails is treated as untraced, and the chain view says "this label couldn't be confirmed against its source" (design review 20A). The log keeps the mark as sent.

## 5. Why claim-level comparison, not similarity scores

**The "AI-expanded card" case (OL-040).** The card says "BP drops if the drug is given fast". An outside AI expands it into a paragraph that adds the mechanism. Similarity would call it the student's idea, polished. But the mechanism is the new part, and it's what a nursing teacher wants to ask about.

L3b works per proposition: it lists the propositions, marks each `in_node` or `added`, and the receipt names the added proposition, not the whole sentence.

**Elaboration is not a trace problem (D-046).** Students who think while they write add reasoning their cards don't hold, and often can't say how they got there. An `added` proposition is therefore never an accusation and never changes a link: the sentence stays in its band, and the proposition can only become an idea question in one of the four pillars (receipt §4), never "where did this come from?".

```json
{"sentence_id": "s14", "node_id": "c3",
 "propositions": [{"text": "...", "status": "in_node|added", "evidence_block": "b81|null"}],
 "artifact_id": "a_…"}
```

S3 (≥ 40 pairs, independent labeller, preregistered false-traced bar) must pass before L3b runs at all. **If S3 fails, L3b is off for the pilot:** only checked recorded chains count as traced, and unlinked sentences show "unlinked (not checked)" (CEO-14).

## 6. Bands

Before applying the five bands, sentences made entirely of confirmed Helper text are labelled **mechanics** and excluded from the word and claim counts (D-050). Claim units containing only mechanics sentences are excluded too. The receipt shows their integer word count separately. All other sentences (and claims) get exactly one band. Rules apply in order:

| Order | Band | Rule |
|---|---|---|
| 1 | **Declared outside help** | ≥ 50% of characters carry a checked `import` mark, or the sentence's claim is a `DeclaredClaim` never re-anchored to a source by the student |
| 2 | **Traced to a source or lecture** | A chain ends in a Block, every mark on the way passed the check, the link is not student-only (or L3b confirmed it), and there are no `added` propositions |
| 3 | **Traced to a Coach exchange** | The chain ends in the student's own typed Coach answer (checked `coach` mark, or a card via `coach_answer`) |
| 4 | **Linked by student, not checked** | The sentence's paragraph links to a claim and L3b did not confirm it (L3b off, or not flagged). A paragraph link counts here whatever its `by`; it never makes a sentence traced by itself (D-045). Its own segment, never merged into traced (D27). **A sentence with ≥ 50% `paste_ext` characters never enters this band by any link** (hand-made or accepted from the map); it stays untraced with the note "pasted; linked by the student, not checked" (eng review v2 D13) |
| 5 | **Untraced** | None of the above, including failed marks, pasted parts of cards or Coach answers, and reworded text L3b hasn't confirmed ("reworded after tracing; not checked", CEO-13). Partly untraced sentences report their `added` propositions |

- **A model-proposed link never makes a sentence traced.** The v1 mapper links sentences to the student's claims only, never to source passages (eng review v2 D19).
- There is **no "polish only" band in v1** (CEO-3; TODOS).
- `quote` text counts as traced to its block and is also counted as "quoted".
- Mixed sentences containing `helper` text remain in the ordinary counts; only entirely confirmed Helper sentences qualify for mechanics. The leak check remains required for Helper output.
- **Proportions are shown two ways, by words and by claims**, always together.
- The human-session stop rule (CEO-18) and the "no untraced wall" gate (CEO-24) use the **untraced** share; the student-linked share is reported beside it (D27).

## 7. Facts derived for the receipt (L1 only)

| Fact | Definition |
|---|---|
| Reading depth | Per source: block kinds opened and anchored (abstract / method / results / table / limitation / discussion) |
| Thinking moments | (a) a claim node edited after a limitation pin was opened on its source; (b) `card.set_aside` with a reason; (c) `coach.outcome = disagreed` with a reason; (d) `coach.outcome = revised` |
| Coach record | Questions by case and outcome |
| Paste facts | Number and size of external pastes (editor, cards, Coach answers) and how much survives in the final text |
| Replacement edits | Count of `input_kind: replacement` edits (spellcheck, autocorrect, extensions). A fact, never a band |
| Declared help | Imports by tool name and size; how many declared claims were later anchored |
| Unanchored claims | Claim nodes with no card and no declared claim behind them |

## 8. Signal register (confirmed by /plan-eng-review, OL-038)

| Signal | Decision | Reason |
|---|---|---|
| Origin by channel, checked against source | **Keep** | Recorded, then verified |
| Claim lineage | **Keep** | v0.4 separated partial-outside work (simulated, n=6); never a verdict |
| Paste events | Keep as a fact | v0.4: did not drive separation |
| Typing speed, rhythm, backspaces, dwell | **Drop** | v0.3 retyped hybrid scored like honest work; privacy (D12, D16, D30) |
| Embeddings / cosine as deciders | **Drop** (and no embeddings in v1, D1) | Fail the AI-expanded card |
| AI-style word lists, stylometry | **Drop** | Track the model, not the student; penalise second-language writers (v0.5) |
| Citation correctness as process evidence | **Drop** | Outside AI cites accurately (v0.4); feedback to the student only |
| Set-aside reason vs. relied-on source | Keep, as a question | Only on comparable metadata |
| Construction order (card before paragraph, or after; "source-first ratio") | **Drop** (D-046) | A scripted outside-AI workflow fakes it (open a pin, make a card, then paste); honest writers often find their structure while drafting. Dated thinking moments (§7) stay as facts, never as a ratio |
| Grading a Coach answer ("did it resolve the question?") | **Drop** (D-046) | A verdict on the student (law 6). Outcomes and the answer are shown; the teacher judges |
| Voice as proof | **Drop** | Biometric; accessibility input only |
| "100%" or "impossible to spoof" | **Drop the wording** | Contradicted by §2 |

## 9. Failure modes and how they surface

| Failure | Effect | Guard |
|---|---|---|
| Forged origin mark from devtools | Would be a false "traced" | Mark check (§4.1); golden session with forged quote and coach marks |
| Outside text pasted into a card or Coach answer, then moved | Would be a false "traced" | Paste-tracking in cards and answers (D26); golden session |
| Student self-links outside text | Would be a false "traced" | Own band "linked by student, not checked" (D27); flagged for L3b |
| L3b misses an added proposition | A false "traced" | S3 gate; "checked against the source" label (4A); chain view |
| L3b flags pure polish as added | A false "untraced" | S3 bar; student preview and notes |
| Replay mismatch (schema drift) | Receipt built on a wrong document | Checkpoint replay job alerts early; at submit, L1 receipt from the client snapshot, labelled (D28) |
| Thin honest student | Large untraced share | Framing "untraced ≠ AI"; human-session stop rule (CEO-18); questions about ideas |
| Retyping outside text | A false "typed" | Stated blind spot; questions cover it |
| Writing offline, pasting once | One large `paste_ext` | Declare offer at paste time; never blocked |
