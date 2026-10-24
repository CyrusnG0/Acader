# Spike S5: is the log tamper-evident?

Date: 2026-10-24 · Task: T-005 · Spec: [design/event-log.md](../../../design/event-log.md) §3, §6; [design/evaluation.md](../../../design/evaluation.md) §1 (S5)

**Result: GO.** The chain, the seal and the whitelist work as designed. `verify` fails on every tampering case the spike set out to test and passes on clean logs. Four small spec gaps need a decision before M1 (below).

## What was built (`prototype/server/engine/events/`, no FastAPI import)

- `canonical.py`: canonical JSON (UTF-8, sorted keys, no whitespace) that **refuses floats** anywhere, and sha256.
- `chain.py`: genesis `prev_hash = sha256("writing-room/" + log_id)`; `hash = sha256(prev_hash || canonical_json(envelope without hash))`; the post-seal whitelist (`receipt.issued`, `note.add`, `link.add`, `record.withdrawn`, `resubmit.open`); `build_event` refuses a non-whitelisted type on a sealed log (`SealedError`, the 409).
- `store.py`: SQLite append under `BEGIN IMMEDIATE`, primary key `(log_id, seq)`, `client_seq` dedupe on retry. No staging or 5-minute merge (that is M1).
- `verify.py`: `verify(events, seal, receipt=None, artifacts=None)` checks the chain (genesis, gap-free seq from 0, links, recomputed hashes, one `log_id`), that the seal is the hash of a `submit`, the post-seal whitelist (with a resubmission window from `resubmit.open` to the next `submit`), and, when given, stored AI outputs and receipt citations.
- CLI: `python -m engine verify LOG.jsonl SEAL [--receipt R.json] [--artifacts A.json]` (exit 0 ok, 1 with the problems on stderr). The endpoint is left to M1.

## What the tests show (`server/tests/test_events_s5.py`, 48 tests)

`verify` **fails** on: an edit to any of the 6 pre-seal events; a one-character change made directly in SQLite; an edit followed by recomputing every hash (internally consistent, but the seal no longer matches); deleting any pre-seal event; deleting a post-seal event that has a later event; swapping two events (with or without renumbering `seq`); any of 6 non-whitelisted types appended after the seal with a valid hash; a seal that names a non-`submit` event or no event; an empty log; an event from another log; a changed receipt; a receipt citing an event after the seal or a missing one; a changed or missing stored output; a receipt that contains a float.

`verify` **passes** on: the clean log; each whitelisted post-seal type; a full record with receipt, student note and stored output; a resubmitted log against both its first and second seal.

Mutation check: removing the whitelist check makes 6 tests fail; removing the hash recompute makes 8 fail.

## What was learned

1. **The seal protects everything up to `submit`, and nothing after it.** The post-seal events (notes, links, `receipt.issued`) are chained, so an edit or deletion in the middle shows. **Dropping events from the tail after the seal does not show** without an anchor for the head. A dropped `receipt.issued` shows only when the receipt is checked against it. This matches §6 ("the record up to the seal"), but the copy must never suggest the student's later notes are sealed.
2. **An edit plus a full rehash is internally consistent.** Only the seal held outside the system (emailed to the student, printed on the receipt) shows it. The emailed seal is load-bearing, not a nice-to-have.
3. **The receipt cannot be hashed as currently drafted.** receipt.md §6 has float band shares (`"untraced": 0.18`), and canonical JSON forbids floats. Without a fix, `receipt_hash` is not defined.
4. **"Event id" is not defined.** Receipt lines carry `event_ids`, but events have only `seq` and `hash`. The spike uses `seq` (unique per log, gap-free).
5. **`prev_hash || canonical_json` is ambiguous** (hex text or raw 32 bytes). The spike uses the hex text as UTF-8.
6. **Floats in payloads have to be refused at append**, not just at verify, or a valid-looking event can never be verified. The store now refuses them.
7. `verify` cannot tell whether a `resubmit.open` was allowed by the teacher; it only checks that the type is on the whitelist. Permission belongs to the append path.

## Proposed changes to the design (for the checker; nothing here is decided)

- **PD-S5-1:** event-log.md §3: "`prev_hash` is concatenated as its lowercase hex text (UTF-8)."
- **PD-S5-2:** receipt.md §6: an event id in `event_ids` is the event's `seq`.
- **PD-S5-3:** receipt.md §6: no floats in the receipt JSON. Store band shares as integer word counts (or per-mille); the renderer rounds. `receipt_hash = sha256(canonical_json(receipt))`.
- **PD-S5-4:** event-log.md §6 and receipt copy: say plainly that the seal covers the record up to submission; notes and links added afterwards are chained and dated but not sealed.
- Spike convention, for M1 to confirm: a stored AI output is `{"body", "hash": sha256(body)}`, and events that cite it carry `artifact_id` + `output_hash`.
