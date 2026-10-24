# Event log and origin capture

Status: **reviewed (CEO + eng) 2026-10-23** · Last updated: 2026-10-23
Implements: D-025 (tamper-evident record, every receipt line cites events), the privacy floor in [PRODUCT.md](../PRODUCT.md) §6, CEO-16, D5, D8, D10, D12, D16, D17, D21, D26, D28, D30, D31, D32 ([eng record](../docs/designs/eng-review-v1.md)). Answers OL-031 (capture half) and OL-035 (what "provable" means).

## 1. What this record is for

The event log is the input to the receipt. If something isn't in the log (or in a stored AI output the log points to), the receipt can't say it.
It must be:
1. **Complete for what it covers:** every action in the platform that can change where the work came from is an event.
2. **Tamper-evident:** after submission, nobody (student, school or us) can change it without it showing.
3. **Small and private:** edit operations, not snapshots; **no typing rhythm** (§5).

"Provable" in our copy means exactly two things (OL-035):
- **(a)** the record up to the seal wasn't edited after submission, and anyone holding the seal hash can check that;
- **(b)** every number and line on the receipt traces to events in the log, or, for AI-derived lines, to a stored AI output that is labelled as such (D31).

It never means we can prove where a thought came from.

## 2. Scope of one log

One log per (student, assignment). It opens when the student accepts consent for that assignment. It is **sealed** by the `submit` event (§6). A resubmission (only if the teacher allows it) continues the same chain after a `resubmit.open` event and seals again; each seal gets its own receipt.

## 3. Event envelope (schema 1)

```json
{
  "schema": 1,
  "log_id": "uuid",
  "seq": 418,
  "client_seq": 1203,
  "ts": "2026-11-02T14:00:00Z",
  "actor": "student | helper | coach | system | teacher",
  "type": "editor.batch",
  "payload": { },
  "doc_rev": 77,
  "prev_hash": "hex",
  "hash": "hex"
}
```

- `seq` is assigned by the server, gap-free per log. Appends are one at a time per log: `BEGIN IMMEDIATE`, read head, insert, with a unique `(log_id, seq)` (CEO-16). `client_seq` lets the server drop duplicates on retry.
- `ts` is server time. For `editor.batch` it is **rounded down to 5 minutes**. Other events keep seconds (D12). Client timing is never stored.
- `hash = sha256(prev_hash || canonical_json(envelope without hash))`. Canonical JSON: UTF-8 (no ASCII escaping), sorted keys, no whitespace, no floats in payloads. The genesis event uses `prev_hash = sha256("writing-room/" + log_id)`.

### Event types

| Type | Actor | Payload | Emitted by |
|---|---|---|---|
| `log.open` | system | assignment_id, consent_version, mapper_enabled (fixed for this record, eng v2 D20) | consent accept |
| `source.add` | student/teacher | source_id, origin: `teacher \| door`, url (stored, never fetched), title | library |
| `source.open` | student | source_id | reader |
| `source.view_span` | student | source_id, block_ids[] (opened only; no dwell, D16) | reader |
| `aid.pins_shown` | system | source_id, pins[{kind, block_id}] | reading aid |
| `aid.pin_opened` | student | source_id, block_id, pin_kind | reader |
| `card.create` / `card.edit` / `card.delete` | student | card_id, text, origin_runs[{from, to, kind: typed \| paste_ext}] (D26), via: `typed \| coach_answer \| import` | cards |
| `card.anchor` | student | card_id, source_id, block_id, quote (≤ 300 chars), quote_hash | reader |
| `card.set_aside` | student | source_id, reason_tag, note | library |
| `claim.create` / `claim.edit` | student | claim_id, text, card_ids[], parent_claim_id | claim map |
| `import.declared` | student | import_id, tool_name, raw_text_ref (student-private), size_chars | Door |
| `claim.extracted` | system | claim_id, from: `import`, text, artifact_id | L3a job |
| `editor.batch` | student | steps[] (ProseMirror JSON, merged per 5-min window), input_kind counts | staging flush (D30) |
| `editor.paste` | student | paste_id, size_chars, kind: `external \| internal`, internal_origin, target_from, target_to | editor |
| `editor.insert_quote` | student | block_id, quote_hash, citation_id | reader → editor |
| `editor.insert_helper` | student | helper_serve_id, text_hash | Helper panel (mechanics only) |
| `cite.format` / `cite.verify` | system | citation_id, doi, result: `ok \| not_found \| span_mismatch` | citation help |
| `helper.serve` | helper | request_kind, policy_id, served: bool, leak_check: `pass \| fail`, output_hash | Helper |
| `coach.ask` | coach | q_id, case: `B \| C` (trigger), trigger_ref (import, paste or `map.finding` id), pillar: `reading \| logic \| writing \| communication` (D-038), target_span, grounding_ids[], question | Coach |
| `coach.outcome` | student | q_id, outcome: `answered \| revised \| disagreed \| declined`, answer_text, origin_runs[] (D26) | Coach |
| `doc.checkpoint` | system | doc_rev, doc_hash, snapshot_ref | each save point (≤ 1 per 5 min) and submit |
| `submit` | student | doc_rev, doc_hash, idempotency_key | submit (the seal) |
| `resubmit.open` | teacher | reason | teacher, if allowed |
| `receipt.issued` | system | receipt_id, receipt_hash, seal_seq, version | compiler |
| `note.add` | student | span, text, after_release: bool | student receipt view |
| `link.add` | student | sentence span, claim_id (never changes bands, CEO-17) | student receipt view |
| `record.withdrawn` | student | reason (optional) | delete after submit |
| `map.suggestion` | system (mapper) | suggestion_id, doc_rev, span, sentence_hash, claim_id, artifact_id, output_hash (D-035; eng review v2 D3, D14) | mapper job |
| `map.finding` | system (mapper) | finding_id, kind: `unconnected_paragraph \| claim_without_source`, span, claim_id (optional), artifact_id, output_hash. Never about a sentence with a `map.answer` no (eng review v2 D15) | mapper job |
| `map.answer` | student | suggestion_id, answer: `yes \| no`. A yes also applies the claim mark `{claim_id, by: student}` through a normal editor step | live map |

## 4. Marks in the editor

Every character carries exactly one `origin` mark `{kind, ref}`. Linked text also carries a `claim` mark `{claim_id, by}` (D17). Both are defined in `web/schema.json`, which the Python replay also loads (D33).

| `origin.kind` | `ref` | When it is applied |
|---|---|---|
| `typed` | — | Text the student types, including IME, dictation and autocorrect. `input_kind` (keyboard, ime, dictation, replacement) is kept as counts for accessibility and facts only |
| `paste_ext` | paste_id | Pasted text whose clipboard has no platform marker, and pasted parts of cards or Coach answers moved into the draft (D26) |
| `quote` | block_id | "Quote this passage" from the reader |
| `helper` | helper_serve_id | Helper output (mechanics only: references, formatting) |
| `coach` | q_id | The student's own typed answer to a Coach question, moved into the draft |
| `import` | import_id | Text from a declared import |

| `claim.by` | Meaning |
|---|---|
| `student` | The student linked this text to a claim. Shown as "linked by student, not checked" unless L3b confirms it (CEO-17, D27). When the link came from a map suggestion (a `map.answer` yes) the mark also carries `suggestion_id` (schema bump; eng v2 D12) |
| `coach` / `import` | The text arrived from a Coach answer or import that carries the claim |

**Rules:**
- **Typed text is always `typed`.** Marks are `inclusive: false`, and an input plugin sets `origin=typed` on every text input, including typing inside or at the edge of a marked span (D21).
- **Replacements** (spellcheck, autocorrect, browser extensions such as Grammarly) are `typed` with `input_kind: replacement`. That count is a fact on the receipt, never a band.
- **Internal copy and paste keeps marks.** On copy the editor writes `application/x-writing-room-slice` with the marks and the log_id. A paste with that type and a matching log_id restores the marks (`internal`); anything else is `paste_ext`.
- **Moves, drag-and-drop inside the document, and undo/redo** keep marks. Drag-and-drop from outside is `paste_ext`.
- **Retyping is invisible.** Text typed by hand from another screen is `typed`. This is the stated blind spot (receipt §4).
- **Marks are claims, checked later.** The browser can be tampered with, so at compile time engine/ checks every non-typed mark against its origin (provenance §4.1). The log keeps the mark as sent.
- Spike **S1** must pass before the editor is built on this ([evaluation.md](evaluation.md) §1).

## 5. Batching, staging and storage

- The editor sends a batch every ~2 s of activity, on blur, and before submit. The server **acks it into a staging table** (outside the chain, restart-safe).
- The server appends **one merged `editor.batch` per 5-minute window**, and at every checkpoint and submit (D30). The chain therefore holds no per-burst activity, only what changed in each 5-minute period.
- Full document snapshots are stored only at `doc.checkpoint` (at most one per 5 minutes of activity, and at submit). Any `doc_rev` can be rebuilt by replaying steps from the nearest checkpoint.
- A background job **replays steps at every checkpoint** with prosemirror-py and compares the result with the client's `doc_hash`. A mismatch alerts the operator; the student is unaffected (D6, D28).
- Rough volume: a 1,500-word essay is a few thousand steps, well under 5 MB per log **[ASSUMPTION; measure in S1]**.
- **Single writer.** Only the device holding the edit lease may send (heartbeat 30 s, expiry 90 s); other tabs are read-only with "edit here instead" (D10). A device that lost its lease while offline never applies its queued edits. The student sees that text with "Save as a file" or "Bring it in through the Door" (D32).

## 6. Sealing and verification

- **Submit** is enabled only when the client queue is empty. One submit per `doc_rev` (idempotency key); a 0-word submit is blocked. Submit retries with the same key until acked (D10, D34).
- At submit the server flushes staging, writes `doc.checkpoint` and `submit`. **The hash of the `submit` event is the seal.** It is emailed to the student and printed on the receipt (D8).
- After a seal, only these may append: `receipt.issued`, `note.add`, `link.add`, `record.withdrawn`, `resubmit.open`. An editor batch after submit gets 409 unless a resubmission is open. **Mapper jobs** (D-035) for a log are cancelled at submit; a mapper result (suggestion or finding) that finishes after the seal is discarded, never appended, and counted on the operator page (eng review v2 D4).
- `verify(log, seal)` recomputes every hash from genesis to the seal, checks the post-seal events against the whitelist, checks that each receipt line's `event_ids` exist at or before its `seal_seq` (or are marked post-seal notes), and checks stored AI output hashes and `receipt_hash`. A CLI and an endpoint expose it. Spike **S5** tests tampering, including an edit after the seal.
- The chain is evidence against after-the-fact editing. It is not evidence about what happened outside the platform.

## 7. Who can read what

| Data | Student | Teacher | School admin | Us (operators) |
|---|---|---|---|---|
| Full event log + stored AI outputs | yes (export) | no | no | only for support, with the student's permission, logged |
| `import.declared` raw text | yes | no, unless the student shares it | no | no |
| Coach Q&A text | yes | question + outcome on the receipt; full text only if shared | no | as above |
| Receipt | preview before release (spans + facts, no question text, CEO-20) | at release (CEO-21, D7) | aggregate counts only | as above |
| Seal hash | yes | yes | yes | yes |

Teacher opens and exports are logged in an audit table, not in the student's log (D9). Details and retention: [privacy.md](privacy.md).

## 8. Settled questions

- Dwell time: not stored (D16).
- Deleting a log: before submit, deleted with no receipt; after submit, `record.withdrawn` and the receipt reads "record withdrawn by the student". Wording: [receipt.md](receipt.md) §7 (P-15, design review 9A).
- Anchoring: the emailed seal hash only in v1; no public transparency log.
