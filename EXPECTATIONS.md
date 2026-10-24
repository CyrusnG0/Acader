# EXPECTATIONS.md: the checklist every finished task is checked against

This is the spec in plain words. When a task says "done", the checker goes through every section the task touched and ticks each line. **One unticked line in a touched section means the task is not done.** Section A applies to every task.

Where a line cites a code like `D13`, `9A` or `D-035`, the full reasoning is in [docs/DECISIONS.md](docs/DECISIONS.md) or the review records in [docs/designs/](docs/designs/). If this file and a design doc disagree, the design doc wins and this file gets fixed.

---

## A. Every task, every time

- [ ] It does what the task in [docs/TASKS.md](docs/TASKS.md) asked, and nothing it didn't ask for.
- [ ] Tests pass with `ROOM_LLM=stub`: the prototype tests, plus the kit's 29 (`cd writing-room-kit && ROOM_LLM=stub python3 -m pytest -q v04/tests web/tests`).
- [ ] New behaviour has a test that would fail if the behaviour broke.
- [ ] `shared/llm.py` behaves exactly as before (wrapped, never changed; D22).
- [ ] No secrets in any file (`DEEPSEEK_API_KEY` stays in `.env`); no real student data anywhere.
- [ ] No banned words in any user-facing string: detect, catch, cheat, ghost, forensic, AI-generated, suspicious, suspect, flag/flagged, violation, integrity score, probability (receipt.md §5).
- [ ] No promise of "no cheating" or "100%"; the selling point is thinking, never time saved.
- [ ] If a design changed: the doc in `design/` is updated, and so is its row in [design/README.md](design/README.md).
- [ ] A handoff note exists in [docs/handoffs/](docs/handoffs/README.md) that lists the files changed, the tests run with their results, and the sections of this file it claims.

## B. The 10 product laws (CLAUDE.md §4): nothing breaks them

- [ ] The AI never writes the student's prose or invents their argument.
- [ ] The Helper answers and the Coach asks; every Coach question cites a block or claim ID.
- [ ] Mechanical cost (finding, reading, citing) goes down; thinking cost stays.
- [ ] Outside AI is never blocked; declaring is never penalised.
- [ ] No step needs typing speed, speech, dragging or a timer; accessible alternatives exist.
- [ ] Nothing reads as a verdict or score; "untraced" always comes with "untraced is not AI".
- [ ] No keystroke timing, typing rhythm, reading dwell, webcam, screen capture or biometrics.
- [ ] Course material stays in its tenant; nothing trains a model.

## C. The record (event-log.md, provenance.md)

- [ ] Typed text is always `typed`, including at the edges of marked spans (D21).
- [ ] Every non-typed mark is checked against its origin text at compile; a failed check is untraced (D5, D29).
- [ ] Pastes are tracked in the editor, in cards and in Coach answers (D26).
- [ ] Editor changes enter the chain once per 5 minutes; timestamps rounded down to 5 minutes (D12, D30).
- [ ] The seal is the hash of the `submit` event; after it, only the whitelisted events may append (D8).
- [ ] Same log + same engine stamp + stored AI outputs → a byte-identical receipt (D20, D31).
- [ ] `verify` fails on any edit, deletion, reordering or non-whitelisted post-seal event (S5). The seal covers the record up to submission: later notes are chained, so a gap in the middle shows, but dropping the newest ones does not (S5 result, PD-S5-4).

## D. Bands (provenance.md §6)

- [ ] Bands are applied in order: declared, traced to source, traced to Coach, linked by the student, untraced.
- [ ] A link the student made (or accepted) is never "traced" unless L3b confirms it (D27).
- [ ] A sentence that is ≥ 50% pasted never enters "linked by the student" by any link (D13).
- [ ] A model-proposed link never makes a sentence traced; the mapper never links to source passages (D19).
- [ ] Links accepted from map suggestions carry `suggestion_id` and show as a sub-count on the receipt (D12).
- [ ] Links belong to paragraphs: typing or adding sentences in a linked paragraph never removes a link; a paragraph link alone never makes a sentence traced (D-045).

## E. Coach and Helper (coach-helper.md)

- [ ] Every new idea gets the same treatment, whatever its origin; the Coach never asks where an idea came from (D-038).
- [ ] Construction order (card before or after the paragraph) is never a signal, trigger or ratio; Coach answers are recorded as outcomes, never graded (D-046).
- [ ] One pillar question per idea (reading, logic, writing or communication), grounded in the student's own sources or claims.
- [ ] Never blocks writing, never interrupts, never timed; declining is allowed and recorded.
- [ ] Budget: at most 1 unprompted question per 10 minutes and 6 per assignment, mapper findings included (17A).
- [ ] Every Helper and Coach output passes `coach/leak.py`; a failure shows the safe fallback and is logged.

## F. The mapper (only when `mapper_enabled` is on; D-035, D-037)

- [ ] Flag off → nothing is sent while the student writes.
- [ ] The flag is fixed per record at `log.open`, and the consent version matches it (D20).
- [ ] The payload is only the changed paragraphs + claim texts + anchored block titles; no names, no full draft (D5).
- [ ] Lowest priority; batches with < 30 changed words are skipped; one queued job per log; cap of 40 calls per submission (D6).
- [ ] Jobs are cancelled at submit; a late result is discarded, never appended (D4).
- [ ] Suggestions and findings are chained events; a stale suggestion is not shown; at most 3 open suggestions (D3, D14, D18).
- [ ] "Not this" is never shown on the receipt and never becomes the subject of a question (D11, D15).
- [ ] Before the flag goes on for real students: precision ≥ 0.80, recall ≥ 0.50, ≤ 1 suggestion per batch, both backends, ≥ 5 held-out sessions, 3 separate human sessions labelled by a second person (D7, D17).

## G. The student's screen (workspace.md)

- [ ] The editor is the anchor; the live map is the left outline; Coach and Helper are on the right; the reader replaces the map rail (1A).
- [ ] Every string in the workspace.md §3 state table appears exactly as written.
- [ ] "Show my trail" is off by default; it uses the engine's own bands and matches the L1 receipt (7A, D8).
- [ ] Only the claim↔paragraph highlight moves (150 ms); nothing the system adds animates, pulses or makes a sound (11A).
- [ ] Writing is never blocked at any width or zoom level; below 900 px it switches to a one-column mode (15A).
- [ ] Landmarks, F6 region cycling and a skip link exist; new suggestions and questions are never announced live (16A).
- [ ] Targets are 44 px on touch and at least 24 px with a pointer; contrast ≥ 4.5:1; the focus ring is always visible.

## H. The teacher's receipt (receipt.md)

- [ ] The first screen shows header (no hash), summary, Where to ask, and the bars with the "untraced is not AI" line (2A).
- [ ] Bands use one hue at falling strength plus patterns and labels; never green/amber/red (12A).
- [ ] The submissions list is alphabetical with status only; no band columns, sorting or filters (3A).
- [ ] The student preview matches the teacher's order and says "Nothing here is a grade." (8A)
- [ ] Withdrawal before release: plain notices on both sides, queued jobs cancelled, never released (9A, D10).
- [ ] The chain view uses plain rounded wording; exact figures only in the JSON and export (20A).

## I. Milestone exits (build-plan.md)

- [ ] **M0:** scaffold + CI green (incl. the kit's 29 tests); `web/schema.json`; `complete()` with stub, error classes and boot ping; S1 go/no-go written.
- [ ] **M1:** 10 golden receipts render; a person has read them.
- [ ] **M2:** walkthrough and blind-test result in UPDATE_LOG.
- [ ] **M3:** the real UI flow works; regenerated goldens match.
- [ ] **M4:** zero leaks on the golden and adversarial sets, both backends.
- [ ] **M4b:** export/delete, security, load and retry tests green.
- [ ] **H:** honest median untraced ≤ 40% with the mapper **off**, or stop and fix the flow.
- [ ] **M4m:** the mapper eval in section F passes, or the flag stays off.
- [ ] **M5 / pilot gate:** every box in [build-plan.md §4](design/build-plan.md) ticked. No real student before this.
