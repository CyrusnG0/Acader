# T-029: `artifact_ids` on "More places to ask" items

**Pickup:** ready once T-028 is done (it changes the same engine stamp and fixtures). **Dependencies:** T-027 (done), T-028. Follow [pickup rules](README.md); the board is authoritative for current ownership. Branch: `task/T-029-more-places-artifacts` from checker-accepted main after T-028 merges.

## Read first

AGENTS.md, docs/STATUS.md, docs/TASKS.md, EXPECTATIONS.md, then docs/DECISIONS.md D-053, D-060, D-063; docs/handoffs/2026-10-25-T-027-more-places.md (PD-T027-2); design/receipt.md §6; `engine/receipt/questions.py` (`source_artifact_ids`), `engine/receipt/compile.py` (how a question item builds `artifact_ids`), the receipt verifier and its fixtures.

## Scope and boundaries

Founder accepted 2026-10-25 (D-063, review finding L4): a `more_places` item that comes from a mapper finding must cite the artifact it rests on, the same way a chosen question does, so `verify` can walk it.

Build: add `artifact_ids` to each `more_places` item, filled from the candidate's `source_artifact_ids` (sorted, deduplicated; an empty list when the candidate has none). The field is inside `receipt_hash`. Extend the verifier so a `more_places` item whose `artifact_ids` names a missing or mismatched artifact fails verification, and extend the verifier fixture with a non-chosen map finding. No generated text, no provider call, no new wording; the rendered disclosure does not change.

Engine stamp: this changes receipt bytes again. Unless T-028's handoff says otherwise, bump to the next `l1/` minor (`"receipt/1 l1/3"`) per D-063 and regenerate affected fixtures; keep `RECEIPT_SCHEMA = 1`.

Out of scope: the student preview (T-022, OL-059), question wording for extra places (PD-T027-1 stands).

## Required evidence

A synthetic receipt with a non-chosen map finding lists its artifact id; a candidate with no source artifacts gets `[]`; `receipt_hash` covers the field; `verify` fails when the cited artifact is removed or altered and passes otherwise; byte-identical recompile; integers only, no floats. Each guarded line has a test that fails under mutation. Full prototype tests with ROOM_LLM=stub and the kit's 29; web tests + typecheck if `types.ts` changes.

Model: D (well specified, mechanical).

Return the commit, a dated docs/handoffs note, files changed, EXPECTATIONS A and C lines, and mutation results. Set your own row to `review`. Only the checker merges and marks done.
