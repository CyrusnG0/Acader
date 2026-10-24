# Provenance engine: tracking, chains and the receipt (engineering design)

> **Superseded 2026-10-23** as the working spec: split into [design/event-log.md](../../design/event-log.md), [provenance.md](../../design/provenance.md), [reading-aid.md](../../design/reading-aid.md) and [evaluation.md](../../design/evaluation.md). Kept as the review input.

Status: **DRAFT, ready for /plan-eng-review** · Owner: Cyrus · Last updated: 2026-10-22
Product side: [writing-platform-v1.md](writing-platform-v1.md). Decisions: D-024 to D-030. Loops: OL-031 (this doc answers it in draft), OL-035, OL-037 to OL-040, OL-008 (stack).
Evidence base: [writing-room-kit/RESULTS.md](../../writing-room-kit/RESULTS.md) (v0.3), [RESULTS-v0.4.md](../../writing-room-kit/RESULTS-v0.4.md), [RESULTS-v0.5.md](../../writing-room-kit/RESULTS-v0.5.md), [FEATURE-VERIFICATION.md](../../writing-room-kit/FEATURE-VERIFICATION.md). All simulated; none of it is evidence about real students.

---

## 1. The professor's question, answered in one paragraph

"What can tracking and diffs give us? We can't save every snapshot and send it to an AI."

**Most provenance is recorded at the moment it happens, not guessed from diffs afterwards.** The UI has separate channels:
- a card anchored to a source span
- a Coach answer
- a declared import
- a paste
- typing in the editor

Each event is stored with its origin. Diffs are only needed for what happens *inside* the editor (edits, pastes, moves). Cheap local code handles most of it. An LLM is called only where a judgement about meaning is needed: claim extraction, the claim-level comparison on flagged spans, and Coach questions. Cost scales with flagged spans, not with keystrokes.

## 2. What the engine can and cannot establish

| Can establish (recorded) | Can establish (inferred, with error) | Cannot establish |
|---|---|---|
| Which sources and pages were opened, and for how long | Whether a sentence expresses the same claim as an idea card | Where untraced text came from (retyped outside AI = typed by hand) |
| Which spans were anchored to which cards | Whether a revision changed the claim or only the wording | Whether in-platform work was driven by an outside AI (relay; process-evidence-room §5) |
| Every Coach question and the student's answer or decline | Whether ¶1 and ¶3 contradict each other | What the student understands. Only the conversation shows that (law 5) |
| Declared imports and what they contained | Which parts of a source a claim relies on | |
| Paste events, their size and target | | |
| The edit history of every span | | |

**"Bulletproof" means two specific things** (OL-035):
1. **The record is tamper-evident.** Events are append-only and hash-chained. The receipt cites event IDs, and a school can check that the log wasn't edited after submission.
2. **Every number on the receipt traces to recorded events.** Nothing on the receipt is a model's opinion presented as fact.

It does **not** mean we can prove where a thought came from.

## 3. Event model (layer 0, captured)

An append-only log per student per assignment. Each event:

```
{ id, prev_hash, hash, ts, actor: student|helper|coach|system,
  type, payload, doc_rev }
```

| Event type | Payload (key fields) | Captured where |
|---|---|---|
| `source.add` | source_id, origin: teacher|lecture|search|door, DOI/URL | library |
| `source.open` / `source.view_span` | source_id, page, block_id, block_kind (abstract/method/results/table/limitation…), dwell_ms | PDF viewer |
| `aid.pin_shown` / `aid.pin_opened` | source_id, pin_kind (support/skeptical/limitation/data/method), block_id | reading aid |
| `card.create` / `card.edit` | card_id, text, via: typed|voice|coach_answer|import | idea cards |
| `card.anchor` | card_id, source_id, block_id, quote_hash | PDF viewer |
| `card.set_aside` | source_id, reason_tag, note | library |
| `import.declared` | import_id, raw_text (stored by the student; school sees derived only), tool_name | the Door |
| `claim.extracted` | claim_id, from: import|card, text | LLM worker |
| `editor.step` | ProseMirror step (insert/delete/replace/move), span origin marks, input_kind: typed|paste|drop|ime|dictation | editor |
| `editor.paste` | size_chars, target_range, clipboard_kind (plain/html), from_inside_platform: bool | editor |
| `coach.ask` | q_id, case (A–E), target_span, grounding: [block_ids, claim_ids] | Coach |
| `coach.outcome` | q_id, outcome: answered|revised|disagreed|declined, answer_text | Coach |
| `helper.serve` | request_kind, policy_id, served: bool, leak_check: pass|fail | Helper |
| `submit` | doc_rev, receipt_id | — |

**Storage:**
- No full snapshots. Store editor steps (compact, replayable); a full snapshot is materialised only at checkpoints (each save, each submit).
- Raw keystroke timing is **not** stored. Only step-level `input_kind` and coarse timestamps. This is the privacy floor (OL-037).

## 4. Data model (derived)

```
Source ─< Block (page, kind, bbox, text)
Card (student words) ─ anchors ─> Block
Card ─> ClaimNode (the mind map)  <─ Import claims (declared)
ClaimNode ─ expressed_by ─> Span (range in the final doc)
Span.origin_marks: [typed | paste_internal | paste_external | import:<id> | helper:<id> | coach_answer:<q>]
Span.chain: Span → ClaimNode → Card → Block   (or broken: untraced)
```

**Origin marks** are ProseMirror marks carried on text:
- They survive moves and internal copy.
- An external paste gets `paste_external`.
- Retyping over a span keeps `typed`. **This is the known blind spot.**

## 5. Pipeline layers

| Layer | What | Where it runs | Cost |
|---|---|---|---|
| L0 capture | Events above; origin marks in the editor | Browser → server append | ~0 |
| L1 deterministic | Chain assembly, band counts, reading depth by block kind, set-aside vs. accepted metadata, paste stats, Coach outcome counts | Server, plain code | ~0 |
| L2 cheap models | Sentence segmentation; embedding retrieval to propose a span → claim node link (candidate only) | Server; small embedding model | low |
| L3 LLM, flagged only | (a) extract claims from imports and drafts; (b) **claim-level comparison** on changed or untraced spans: "does this sentence add a claim, a mechanism or a number not present in its linked node?"; (c) contradiction between paragraph claims; (d) Coach questions; (e) receipt questions | DeepSeek (pilot) | scales with flags |

**Why L3(b) and not a cosine threshold.** This is the "AI-expanded card" failure (OL-040). A student's card says "bp drops if med given fast". An outside AI turns it into a paragraph about the mechanism. Paragraph-level cosine similarity stays high, so a similarity rule would label it "student idea + polish". But the mechanism, which is the part the nursing teacher cares about, is new. So:
- compare at the **claim / proposition** level: list the propositions in the sentence, then check each against the node and its anchored spans
- any **added proposition** is shown as untraced, even inside a "polished" paragraph

Embeddings only propose candidate links; they never decide a band.

## 6. Receipt compilation

1. Assemble chains for every span in the final doc (L1).
2. Assign each span to a band using recorded facts first:
   - an import mark → declared
   - a coach_answer mark → Coach
   - an anchored chain → traced to source/lecture
   - otherwise → untraced, unless L3(b) finds it is the same claim as a traced node with only wording changed (→ polish only)
3. Proportions are computed over **words and over claims**, and both are shown. A short untraced sentence can carry the main claim.
4. Pick 2–3 "where to ask" spans: untraced spans carrying a claim, contradictions, a set-aside reason applied inconsistently. Generate the questions grounded in the trail (L3(e)), then run the law-1 leak check and the law-10 wording filter on them.
5. Every line cites event IDs. The receipt is reproducible from the log.

## 7. Guardrails (Helper and Coach)

- **Policies live in code, not only in prompts.** Each tool call goes through a policy module (process-evidence-room §3), and `helper.serve` is logged with its policy.
- **Structured output.** Coach output is JSON: `{target_span, grounding_ids[], question}`. A question with no grounding IDs is rejected (law 2).
- **Leak check (law 1).** Reject Helper/Coach output that contains a claim-bearing sentence the student could paste. The ">8 consecutive words" rule from response.md is a cheap first filter, not enough on its own. Audit sample transcripts as in kit v0.4 (limit 2%).
- **Wording filter (law 10)** on everything teacher-facing.
- **Prompt-injection hygiene:** sources, imports and student text are untrusted. Use delimited, tagged inputs (D-022 R3).

## 8. Signal register: what we keep and what we drop

These include the claims from the 2026-10-21 Gemini brainstorm ([response.md](../research/gemini-brainstorm-2026-10-21.md)). /plan-eng-review should confirm each row (OL-038).

| Signal / claim | Status | Evidence | Use in v1 |
|---|---|---|---|
| Provenance by channel (anchor, import, Coach, paste) | **Keep** | Recorded, not inferred | Core of the bands |
| Claim lineage (a claim with no ancestor is untraced) | **Keep** | v0.4: separated partial-outside work on claim/source lineage (C1 vs C4 AUC 1.00, n=6, simulated). v0.5: a stolen honest trail adds +15; a white-box loop attacker reached median 52 vs 86 | Bands + where to ask; never a verdict |
| Paste events | Keep as a fact | v0.4: the paste signal did **not** drive separation | Show as a fact; it feeds the questions |
| Typing velocity / "no backspaces" | **Drop** | v0.3: a retyped hybrid scored 92 vs 91 for honest work | Not captured |
| Cosine thresholds (>0.92 polish, <0.65 new idea) | **Drop as a decider** | Invented numbers; fails the AI-expanded-card case | Candidate links only (L2) |
| "Token fog" regex / AI-style words | **Drop** | Stylometry tracks the model's style (v0.5 O3, the direction flipped on model swap); penalises ESL writers | Not used |
| Citation correctness as a process signal | **Drop as a signal** | v0.4: outside AI cites accurately (87 vs 97) | Feedback to the student only |
| NLI entailment, claim vs. cited span | Keep as feedback | NLI is weak on tables and numbers **[ASSUMPTION]**; use the LLM with the span | Coach case D |
| Set-aside reason vs. accepted sources ("double standard") | Keep, **as a question** | Only when the reason tag and the metadata are comparable (same field, extracted reliably) | Where to ask, rarely |
| Reading depth by block kind | Keep as a fact | Recorded | Receipt §3 |
| Voice seed as "unforgeable proof" | **Drop the claim** | It's biometric data (PDPO), and a student can read AI text aloud | Voice only as an accessibility input |
| "Accounts for 100% of the text" / "impossible to spoof" | **Drop the wording** | Contradicted by the blind spot in §2 | Never in copy |
| Trail-anchored questions | Keep | process-evidence-room §5; answerable by a long-context AI unless asked live | The receipt hands them to the teacher for a live conversation |

## 9. Reading aid pipeline

1. **Parse.** Docling or GROBID gives blocks with page, bbox, section and kind (abstract / method / results / table / figure / limitation / discussion). Tables become structured. **Spike S2.**
2. **Index.** Embed the blocks (pgvector or equivalent) with metadata.
3. **Pins.** For the current card or claim, retrieve per pin kind using the kind filter plus the query:
   - support / skeptical: same topic, compared for direction by the LLM; the output is a block ID and a one-line *pointer* ("Table 3 splits by tenure"), never a conclusion
   - limitation / method / data: filtered by block kind
4. **Leak check** on pointers (no claim-bearing prose about the paper's argument).
5. **Search** for student-found papers through OpenAlex / Crossref / Semantic Scholar. Only open-access PDFs are parsed; others are linked with metadata only. **[ASSUMPTION]** about licensing; check before the pilot.

## 10. Stack (open, decide in /plan-eng-review; OL-008)

| Option | For | Against |
|---|---|---|
| Extend `writing-room-kit/web` (FastAPI) + TipTap/ProseMirror + PDF.js; Postgres + pgvector | Reuses the v04 scoring and Coach code; Python for PDF parsing; fastest in 2 weeks | Plain-HTML front end needs a real build setup for TipTap |
| Next.js + Supabase (auth, Postgres, pgvector) + a Python worker for parsing | Auth, hosting and the DB come ready; cleaner for multi-class | Rewrite; two languages |

Fixed whichever option is chosen: ProseMirror-family editor (marks + steps), PDF.js viewer with bbox highlights, an append-only hash-chained event table, and DeepSeek behind a provider interface (pluggable, D-029).

## 11. Spikes before the build (days 1–3)

| # | Spike | Pass condition |
|---|---|---|
| S1 | ProseMirror origin marks survive move, internal copy/paste, undo/redo, collaborative-free autosave | Marks intact in all cases; external paste reliably gets `paste_external` |
| S2 | Docling vs. GROBID on 3 real readings (a 40-page nursing paper with tables, a social-science WP, a CS paper) | Block kinds and tables usable on ≥ 2 of 3 |
| S3 | L3(b) claim-level comparison on the AI-expanded-card case: 10 hand-made pairs (pure polish vs. polish + added mechanism) | Added propositions flagged in ≥ 8 of 10; pure polish not flagged in ≥ 8 of 10 |
| S4 | Offline replay: run the band assignment on the existing v04 runs (C1 honest vs. C4 partial outside vs. C11 thin honest) | Bands match the known arms; C11's receipt shows explainable gaps, not an untraced wall |
| S5 | Hash-chained log: append and verify; receipt cites resolve | Verification script passes; tampering is detected |

S3 and S4 must be preregistered in the kit's style before running (PREREG).

## 12. Privacy and consent (OL-037, with OL-016 and OL-019)

- The student owns the log. The school sees the receipt and derived signals only (law 7). Declared import raw text is visible to the student only, unless they share it.
- No raw keystroke timing, no webcam, no screen capture, no biometrics.
- **DeepSeek:** text sent includes student drafts and source passages. Consent must name the provider and its location. Check each university's rules before the first real student.
- Retention: created-based, with export and delete (D-022 R2). The pilot gate is D-022 T1–T4 or their equivalents.

## 13. Test plan (outline)

- Unit: chain assembly, band rules, hash verification, policy modules.
- Golden receipts: 5 scripted sessions (honest, declared outside, pasted, AI-expanded card, thin honest) with expected bands and questions.
- Leak audit: law-1 check over all Helper/Coach output from the golden sessions and a sample of pilot transcripts.
- Playwright: student flow (read → card → anchor → write → Coach → submit) and teacher flow (receipt → click a chain).
