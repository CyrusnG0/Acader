# T-009: nursing walkthrough and blind-question protocol

- **Lead:** worker-T-009   **Workers used:** none
- **Branch or worktree:** `task/T-009-walkthrough`, worktree `/Users/micmic/Documents/GitHub/Acader-wt-T-009-walkthrough`   **Commit(s):** 12bfda8 (documents), plus the commit containing this handoff and the T-009 board row

## What changed

- `docs/research/nursing-walkthrough-protocol.md`: the runnable walkthrough. Objective; roles and separation; consent, approvals and data minimisation; the synthetic Case A (honest nursing) and the required hard pair B1/B2 (`ai-expanded-card` + `thin-honest`); materials checklist; facilitator script and neutral questions; practical-use and misreading criteria with severity; reporting and storage; stopping conditions; after-session key handling.
- `docs/research/blind-question-preregistration.md`: the 50-vs-50 pilot design and the four-pair walkthrough rehearsal. Comparable platform-grounded vs essay-only questions; same essay/context constraints; one pair per essay; balanced seeded randomisation; hidden labels and sealed key; rating rubric; primary outcome; ties and missing answers; fixed one-sided win rule; sample-size rationale with exact binomial figures; analysis method; blinding and leak checks; execution gates; deviations table.
- `docs/research/nursing-walkthrough-results.template.md`: an explicitly **unfilled** form for observations, practical-use codes P1–P6, misread lines with severity, neutral-question answers, the hard-case outcome, the descriptive four-pair rehearsal (no win rule), verbatim quotes with separate consent, unresolved questions, stopping conditions, deviations and sign-off.
- `docs/TASKS.md`: only the T-009 row (`Owner worker-T-009`; `in progress` then `review`).

No engine, UI, schema, fixture, design doc, `shared/llm.py`, dependency file or shared tracking file was changed. OL-047 stays open; the protocol says to use the rendered wording as-is and not to change copy silently.

## What the documents establish, and what they refuse to claim

- The walkthrough and the pilot blind test are kept separate. The walkthrough uses four descriptive pairs and has no win rule; the pilot's target is 50 platform-grounded vs 50 essay-only ratings, one pair per essay. Neither is reported as a result because no session has been run.
- The hard case is a pair with an untraced band from two different histories (`ai-expanded-card` and `thin-honest`). The specified correct outcome is lingering doubt plus a question, not certainty, and the script does not assume the receipt would have ended the dispute.
- The rating measures a teacher's judgment that a question is worth asking. It does not measure student understanding, authorship, honesty or learning, and no model or person grades a Coach answer.
- Stub-compiled questions are not evidence of live question quality. The walkthrough blind portion requires an approved live release run; otherwise it is a labelled dry run with no blind result.
- No real student logs, identities or essays are used or stored in Git; the cases are synthetic reconstructions. Recruitment, consent and approvals remain with the founder.
- Cited fixtures and paths were checked to exist: `honest-nursing`, `thin-honest`, `ai-expanded-card`, `pasted-rewritten`, `declared-outside`, `elaborating-honest`, `reference-list` under `prototype/fixtures/golden/`; `design/evaluation.md`, `design/receipt.md`, `design/build-plan.md`, `PRODUCT.md`, `docs/OPEN_LOOPS.md`, and the T-016 handoff.

## Tests run (exact commands and real results)

- Environment: Python 3.14.5. Created the venv and installed the hash-locked set:
  - `cd prototype && python3 -m venv .venv && .venv/bin/python -m pip install --require-hashes -r requirements.lock`
  - Result: exit 0; installed the locked packages (`pytest 9.1.1`, `prosemirror 0.6.1`, etc.).
- `cd prototype && ROOM_LLM=stub .venv/bin/python -m pytest -q`
  - Result: **840 passed, 1 warning in 9.40s**, exit 0.
- `cd writing-room-kit && ROOM_LLM=stub python3 -m pytest -q v04/tests web/tests`
  - Result: **29 passed, 2 warnings in 0.16s**, exit 0.
- `git diff --check`
  - Result: exit 0, no whitespace errors.
- Banned-word scan over the three new documents, using the same stem list as `engine/receipt/wording.py`:
  - Result: **no matches**.
- Path/fixture existence check for every cited file: all present.
- No live LLM call was made.

## EXPECTATIONS.md sections claimed

- **A (all lines).**
  - The task asked for three protocol/template documents and a handoff; no unrequested implementation was added.
  - The prototype suite (840) and the kit's 29 both pass under `ROOM_LLM=stub`.
  - New-behaviour test line: **not applicable** — docs only, no engine or UI behaviour changed, so there is no behaviour to test. The best available checks are the full suites (unchanged), `git diff --check`, the banned-word scan and the path check.
  - `shared/llm.py` untouched; no secrets; no real student data; no banned wording in the new docs; no promise of prevention or completeness; no design doc changed; this handoff lists files, commands and results.
- **B (the product laws, as they apply to a protocol):** no verdict or score; untraced is not outside work; the conversation is the gate; no timing, keystroke, webcam or screen data; consent and data minimisation; no automated grading of Coach answers; recruitment and approvals left to the founder.
- **I / M2:** **not claimed.** No walkthrough or blind-test result exists; the template is unfilled. The ticket's execution gate (rendered receipts, live question artifacts, participant, approvals) remains open.

## Acceptance evidence for the T-009 ticket

- A person other than the author can run the session: roles, script, materials, key handover and after-session steps are written for a separate facilitator; the author is expressly not required and should not facilitate if another trained person is available.
- The hard case is included: Case B1/B2, with the fixture histories and the expected lingering doubt.
- The script asks what remains unclear, what could be misread and what evidence the teacher would still want (prompts 3, 4 and 7; the results template repeats them).
- It does not assume the receipt resolves the dispute: the original-case question explicitly accepts "nothing would have changed", and the hard case's correct outcome is doubt plus a question.
- Internal consistency checked by reading: sample (50 pairs, minimum 45, one pair per essay), randomisation (25/25 first position, seeded, sealed key), primary outcome (paired Yes rate, exact one-sided McNemar), missing/ties rules and the win rule all use the same `M`, `N`, `b`, `c` definitions and the same thresholds.
- No live LLM runs, no real case logs or student identities, no invented results, no M2 completion claim.

## Not done / open

- No session was run and no participant was contacted. The results template is empty by design.
- The essay-only prompt, the allocation script and the analysis script do not exist yet. The preregistration specifies what they must do and makes them execution gates; building them is outside T-009.
- The walkthrough needs actual rendered receipts and non-stub question artifacts. T-017 rendering exists, but the M1 human reading gate and live question quality are separate and still open.
- `AGENTS.md` is **not present in this worktree** (the founder's copy is untracked in the parent checkout, which this worker must not touch). I used `CLAUDE.md`, the ticket index, the ticket and the cited design docs instead. No founder file was modified.
- The T-009 acceptance says the checker records real results later; none are recorded here.

## Proposed decisions (the checker takes these to the founder; nothing here is decided)

- **PD-T009-1: what "50-vs-50" means.** I read it as 50 platform-grounded questions and 50 essay-only questions — 50 essays with one pair each — not 50 essays per arm. *Recommend:* accept. If the founder intended 50 essays per arm (100 pairs), the sample must be fixed larger before the pilot; the win rule and the one-pair-per-essay analysis do not change.
- **PD-T009-2: the fixed win-rule thresholds.** Platform-grounded wins only if `M ≥ 45` complete pairs, `N ≥ 15` discordant pairs, one-sided exact McNemar p < 0.05, a paired Yes-rate difference of at least +10 percentage points, at most 5 missing pairs, the compliance guard, and no condition leak. Essay-only wins on the mirror. *Recommend:* accept; these are the thresholds the ticket says to propose explicitly.
- **PD-T009-3: the walkthrough's blind portion is four descriptive pairs.** It is a procedure rehearsal, not a smaller version of the pilot result, and is never pooled with the pilot. *Recommend:* accept.
- **PD-T009-4: misreading severity.** Any reading that turns a band or the seal into an authorship conclusion, a score, a measure of honesty or a replacement for the conversation is a **blocking** receipt defect to fix before the pilot; other misreads are material or minor. *Recommend:* accept.
- **PD-T009-5: the hard case is a pair, not one receipt.** `ai-expanded-card` (outside expansion inside the student's card, untraced band, L3b off) and `thin-honest` (quiet honest writer, unlinked closing line) both show an untraced band for different histories. The correct outcome is lingering doubt plus a question. *Recommend:* accept.
- **PD-T009-6: blind ratings hide the receipt and use a different essay set.** The teacher sees the plain essay and two questions only; the qualitative receipt cases and the four blind essays are disjoint to reduce priming. *Recommend:* accept.
- **PD-T009-7: under-target samples are inconclusive.** Fewer than 45 complete pairs in the pilot means no win or loss claim; the 50-pair target is not replaced by a smaller demonstration. *Recommend:* accept.
- **PD-T009-8: teacher usefulness, not student understanding.** The test measures only whether a teacher would ask the question. No student study, no automated grading of Coach answers and no claim about understanding are made here; a future understanding study needs its own preregistration and consent. *Recommend:* accept.
- **PD-T009-9: OL-047 remains open.** The walkthrough uses the receipt exactly as rendered, including any wording awaiting the founder's disposition ("Written on N days" included); no silent copy change. *Recommend:* accept and keep OL-047 open.
- **PD-T009-10: plain text for blind essays.** Blind essays are the plain final document text from replay, with no origin marks, actions, expected bands, fixture metadata or receipt. *Recommend:* accept; it prevents the origin marks from revealing the trail.

## Checker review (2026-10-25): passed, merged to `main` (fb89767)

- Independent read-only review by an Opus reviewer (fresh locked venvs, Python 3.14.5, `ROOM_LLM=stub`; no CI result claimed). Merged main: prototype suite **898 passed** (reported by the checker after all four merges); kit 29 per the handoffs.
- Cases synthetic and said so to the teacher; sealed key held apart from the facilitator; win rule fixed in advance; nothing grades Coach answers; results template empty. The banned-word scan hits only negated sentences ("never a …").
- EXPECTATIONS A ticked; B as applied to a protocol ticked; I/M2 not claimed (no session run).
- Founder decisions (**D-057**): PD-1 (50 pairs), PD-2 (win rule) and PD-9 (OL-047 stays open) accepted. PD-3…8 and 10 remain open (OL-050). Execution still needs the essay-only prompt, allocation and analysis scripts, live question artifacts, a teacher and approvals.
