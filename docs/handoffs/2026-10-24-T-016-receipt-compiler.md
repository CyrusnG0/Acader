# T-016: Receipt compiler (JSON)

- **Lead:** lead-opus-T016   **Workers used:** Sonnet ×2 (A: D-050 mechanics; B: compiler, one round of three review fixes). The lead wrote the specs, the prompt (`receipt_question.v1.txt`), all user-facing wording (`engine/receipt/copy.py`), reviewed the code and ran its own mutation pass.
- **Branch or worktree:** `task/T-016-receipt-compiler` (from `origin/main` 823095f)   **Commit(s):** 029a5f2 (claim), 8c3296f (D-050 mechanics), plus the compiler-and-handoff commit after it

## What changed
- `engine/provenance/bands.py` (+ `__init__` export), **D-050:** a sentence whose every character is confirmed `helper` text gets band `mechanics` (checked before the five bands). It is left out of `by_words`, `total_words`, the claim units and the L3b queue. A claim unit with only mechanics sentences is dropped. `bands["mechanics"]` is the integer word count. **No existing L1 test changed:** none used helper text. 7 new tests.
- `engine/receipt/wording.py`: the wording filter. It has 13 case-insensitive stem patterns: detect, catch/caught, cheat (which covers "no cheating"), ghost, forensic, AI-generated, suspicio-, suspect, flag, violat-, integrity score, probabilit-, and "100%". `WordingFilter.apply(s, fallback)` swaps in the fallback and counts each swap. The filter is deliberately conservative: "flagship" counts as a hit.
- `engine/receipt/questions.py`:
  - **Candidates** follow receipt.md §4 rules 1, 5, 6 and 7, at most 3 in total and at most one per paragraph.
    - "Carries the argument" means the claim sits in the first or last body paragraph, or other claims have it as `parent_claim_id`.
    - Rules 2–4 need L3b, L3c or source metadata. Their `why` codes are reserved and not built.
  - **Grounding** items are labelled g1… and passed to the model. The model must cite labels, and the receipt keeps only the claim and block ids it cited. A candidate with no grounding is skipped and counted (law 2).
  - **Prompt** is built from the versioned file. The model is never told why a span was chosen.
  - **Validation:** checks the output shape, pillar, cites, question form, length (5–30 words) and wording. It also rejects three kinds of question: about where the idea came from, about construction order, and about the trace (D-046).
  - **Asking:** at most 2 attempts, with a retry note. Every response is stored as an artifact `{artifact_id, task, prompt_hash, body, hash}` and cited, including rejected attempts.
    - A stored artifact with the same prompt hash is reused, so a recompile needs no LLM.
    - If the LLM is unavailable, it is not called again for the remaining candidates.
- `engine/receipt/summary.py`: builds the one-sentence summary from facts only, using `copy.py` wording. It cites the seal, source.add, editor.batch, paste, import and Coach events.
- `engine/receipt/compile.py`: `compile_receipt(...) -> ReceiptResult(receipt, artifacts, receipt_hash)` and `issued_payload()`.
  - **Keys:** follow receipt.md §6, plus `questions_pending`, `built_from` and `replay_note`.
  - **Status:** `replay_mismatch` > `questions_pending` > `complete`.
  - **Pending questions** keep their span, `why` and artifacts, with `q: null`.
  - **`receipt_id`** = `r_` + sha256(log/seal/version)[:16].
  - **Final sweep:** the wording filter runs over every non-identifier string.
  - **`engine` stamp** = the stamp passed in + L1 flags and thresholds + `wording_filter {version, replaced, skipped_no_grounding}`.
  - **`receipt_hash`** = sha256(canonical_json(receipt)). It is not inside the receipt; it goes in `receipt.issued`, which is what `verify` checks.
  - **`declared.by_tool`** is a list, so no student text becomes a dict key.
  - **Replacement edits** carry `reported_by: "browser"` and `lower_bound: true`.
- `engine/receipt/copy.py` (lead), `engine/receipt/prompts/receipt_question.v1.txt` (lead).
- `app/receipt_service.py`:
  - `llm_ask` wraps `complete(Task.receipt_question, …)`. `LLMSchema` maps to `OutputRejected`; any other `LLMError` maps to `LLMUnavailable`.
  - `build_stamp` fills:
    - the git sha (argument, else `ROOM_GIT_SHA`, else `git rev-parse`);
    - `lock_hash` = sha256 of `requirements.lock`;
    - `editor_pair`, read from `web/package.json` and the installed prosemirror (`tiptap-pm 3.32.0 / prosemirror-py 0.6.1`);
    - `models` (`stub` under stub);
    - `prompt_hashes`.
  - `issue_receipt` runs compile_marks → L1 → receipt, then appends `receipt.issued`.
- `app/llm.py`: only `ReceiptQuestionOut`, which is now `{question, pillar, cites}`, and its stub fixture. The provisional shape was owned by this task (T-003 PD-1).
- Tests: `test_receipt_wording.py`, `test_receipt_questions.py`, `test_receipt_compile.py` (103 new), plus 7 in `test_l1_bands.py`.
- `docs/TASKS.md`: the T-016 row only.

Not touched: `prototype/web/`, `schema.json`, `engine/events/`, `engine/replay/`, `shared/`, `design/`, the kit, dependency files (checked with `git diff origin/main`).

## Tests run
- `cd prototype && ROOM_LLM=stub .venv/bin/python -m pytest -q` (venv: Python 3.14, `pip install --require-hashes -r requirements.lock`) → `639 passed, 1 warning in 0.90s` (525 before)
- `cd writing-room-kit && ROOM_LLM=stub python3 -m pytest -q v04/tests web/tests` → `29 passed, 2 warnings in 0.11s`
- Covered:
  - every banned pattern;
  - every validation reason;
  - candidate order, the cap of 3 and one per paragraph;
  - the law-2 skip;
  - an answered map finding, and a finding on a "Not this" paragraph;
  - end to end through `issue_receipt`, then `verify` with the receipt and artifacts: ok. Tampering fails, and so does a missing artifact;
  - a map-finding question with its mapper artifact, which verifies only when that artifact is given;
  - determinism: compiling twice; recompiling from stored artifacts with `ask=None`; the events reversed; and **two fresh processes** (`PYTHONHASHSEED` 1 and 2). All give identical bytes;
  - pending: LLM down (no further calls), invalid output twice, invalid then valid, `ask=None`;
  - replay mismatch → `browser_copy` and the note;
  - a no-floats walk;
  - a walk of every string and key for banned words, plus the tool name, source title and reason_tag fallbacks;
  - the Coach section holds counts and outcomes only, and the answer text never appears;
  - mechanics in the summary;
  - the stamp.
- **Mutation pass:** each change applied alone, then restored. All 18 changes were caught.
  - **Worker A:**

    | Mutation | Result |
    |---|---|
    | mechanics check removed | 4 fail |
    | mechanics words left in by_words | 3 fail |
    | unconfirmed helper counted as mechanics | 1 fail |
  - **Worker B:**

    | Mutation | Result |
    |---|---|
    | one-per-paragraph rule dropped | 1 fail |
    | cites outside the labels accepted | 4 fail |
    | `about_the_trace` check removed | 3 fail |
    | an exception raised instead of pending | 3 fail |
    | the sweep skips the summary | 1 fail |
    | timestamp in `receipt_id` | 3 fail |
    | a float in the bands | 20 fail |
  - **Lead:**

    | Mutation | Result |
    |---|---|
    | `asks_origin` removed | 4 fail |
    | `construction_order` removed | 2 fail |
    | the law-2 no-grounding skip removed | 1 fail |
    | rule 6 ignores "carries the argument" | 1 fail |
    | a "Not this" answer ignored (D15) | 1 fail |

## EXPECTATIONS sections claimed
- **A:** all lines. No design doc changed, `shared/llm.py` untouched, no secrets. The banned-word walk runs on compiled receipts.
- **B:**
  - Question text comes only from the model, about the student's idea. It never writes prose for the student.
  - Every question cites a claim or block id.
  - Nothing reads as a verdict: no score; Coach outcomes are counts only (D-046).
  - No timing is used apart from distinct days in the summary; see PD-T016-5.
- **C:** "Same log + same engine stamp + stored AI outputs → a byte-identical receipt", across processes too.
- **H (data lines):** the JSON carries what the first screen needs: summary, Where to ask, both bars, mechanics, `replay_note`, and the pending spans for the student preview. The rendering lines are T-017.

## Not done / open
- Rules 2–4 (L3b added propositions, L3c contradictions, inconsistent standards) need later layers. Their `why` codes and WHY_TEXT are ready.
- Questions do not run through the leak check (`coach/leak.py` isn't built yet).
- Receipts and artifacts are not persisted; `issue_receipt` returns them. Storing them, the release timing, the `engine compile` CLI and the 48 h cap are later tasks.
- provenance.md §6 still needs its "mechanics" line (D-050 says it is added when T-016 lands). That is a design-doc edit for the checker.

## Proposed decisions (the checker takes these to the founder; nothing here is decided)
- **PD-T016-1: `mechanics` is a word count.** `bands.mechanics` counts words, not sentences, so it reads next to `total_words`. *Recommend:* accept.
- **PD-T016-2: per-question pending.** A question that fails twice, or isn't asked because the LLM is down, keeps its span and `why` with `q: null`. Any null makes the status `questions_pending`, and the other questions still show. A replay mismatch outranks pending as the status; `questions_pending` stays a separate boolean. *Recommend:* accept, and add it to receipt.md §6.
- **PD-T016-3: grounding for an unlinked paragraph.** The model gets the student's claims and anchored blocks (up to 6) and must cite at least one. If the student has none, there is no question (law 2). *Recommend:* accept.
- **PD-T016-4: no catch-all rule.** Rule 1 covers only claims that carry the argument (first or last paragraph, or with dependent claims), so a pasted middle paragraph gets no question at L1. *Option:* add rule 8, "the largest other untraced unit". *Recommend:* decide after the golden receipts.
- **PD-T016-5: "Written on N days".** The summary counts distinct dates of `editor.batch` (5-minute-rounded server time) in place of "sessions", which the log does not define. *Recommend:* accept, or drop the clause if it reads as a timing signal.
- **PD-T016-6: receipt keys beyond §6.** The receipt adds `questions_pending`, `built_from`, `replay_note`, `why_text`, `paragraph_id`, `quoted_words`, `engine.wording_filter`, and makes `declared.by_tool` a list. *Recommend:* add them to receipt.md §6.
- **PD-T016-7: rejected attempts are cited too.** A question cites every LLM attempt for it, rejected ones included, so the record is complete. *Recommend:* accept.
- **PD-T016-8: map-finding spans** are positions at the finding's doc_rev, which may have shifted by the final document. Today they are matched by `span.from` against the final paragraphs. *Recommend:* `map.finding` carries `paragraph` + `paragraph_hash`, as `map.suggestion` does (mapper task). Low urgency: the mapper is off.
- **PD-T016-9: the git sha in the stamp** changes on every commit, so golden receipts regenerate per commit. *Recommend:* accept (that is D20), and pin `ROOM_GIT_SHA` in golden runs.
