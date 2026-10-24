# Writing Room kit: execution plan v0.5, "working as designed, not luck"

Status: PLANNED 2026-10-17 · Owner: Cyrus · Planner: Opus · Executor: Sonnet (this session, after the model switch)
Builds on: [PLAN-v0.4.md](PLAN-v0.4.md), [RESULTS-v0.4.md](RESULTS-v0.4.md), [PREREG-features.md](PREREG-features.md) (amendments 1–3), [FEATURE-VERIFICATION.md](FEATURE-VERIFICATION.md).

---

## 0. Why this round exists (read first)

So far 66 simulated runs (C1–C10) show the coherence report separating honest work from every outside-AI arm, at AUC 1.00 against the relay arms. The exploratory F13 ("claim before evidence") does the same, and it held for thesis-first honest students (C10). A sharp researcher or investor will reply in one of five ways:

| # | The objection | What would show it's right |
|---|---|---|
| O1 | "AUC 1.00 at n = 6 is luck." | A permutation test fails to reject label exchangeability |
| O2 | "Your judge just likes on-topic essays; the link between trail and essay is irrelevant." | Pairing an essay with *someone else's* trail barely lowers its score |
| O3 | "You're separating model styles: honest = Sonnet, outside = DeepSeek." | The essays alone separate the arms, and a model swap kills the trail result |
| O4 | "The attacker didn't know your rules and couldn't iterate." | A white-box attacker who loops on the Coach's feedback passes cheaply |
| O5 | "One judge model, one vendor." | A different judge disagrees |

**This round answers O1–O5, each with a control that could have failed.** It also builds the founder's idea as a pre-registered feature: honest thinking grows in many small steps, each derived from something earlier. It also closes the loop-relay attack with a **timing rule**: an explanation given after a claim reached the draft is an *explanation*, not a *derivation*.

**The claim we are trying to earn (product language, law 10):**
> Every idea in the submission has a derivation the student built in the Room. Where one is missing we ask how they got there, and a person hears the answer. Every path through the system leads either to visible thinking or to an open question, and no path is both cheap and silent.

That breaks into three testable parts:
1. **Fairness:** honest students rarely get a gap they can't explain.
2. **Economics:** outside work either leaves gaps, or the attacker must build a derivation that costs about as much as the work.
3. **Gate:** asked live, the questions separate the two. This is out of scope here; it's the real-student pilot, and P6 only writes its protocol.

## 1. Standing constraints (unchanged from v0.4, verbatim where quoted)

- **Security:** "Never print, log or copy the DeepSeek key. Get it only through `demo/llm.py` (`llm.chat`). Never open `.env`." The only route is `v04/llmx.py`.
- **No commits.** Cyrus commits.
- **Product laws** in CLAUDE.md §4. **Banned words** in any human-readable file: the surveillance list in CLAUDE.md law 10 plus the word for watching someone (m-o-n-i-t-o-r). Before every hand-back, run the same banned-word grep used in v0.4.
- **Read-only:**
  - runs/, runs-v0.2/, PREREG.md, PREREG-v0.3.md, PREREG-v0.4.md, RESULTS.md, RESULTS-v0.4.md, the v0.2/v0.3 scripts
  - **all existing files in `v04/runs/` and `v04/reports/`** (v0.4 numbers must stay reproducible)
  - v0.5 writes go to new paths only (below)
- Keep `llm.chat` calls **serial within a process**. Separate processes may run in parallel; max 3 at a time.
- **Claude workers** (subagents) are students, outside writers or judges. Each gets only its own prompt file. Each must not read plans, preregs, results, other runs or v04 source. Say so in each prompt, as in v0.4.
- If a step's assumption fails (an API option is unsupported, a model refuses), **record it in the prereg amendments and continue with the stated fallback**; don't improvise silently.
- Session protocol (STATUS, UPDATE_LOG, CHANGELOG, OPEN_LOOPS next free **OL-031**, DECISIONS only if locked) happens only in P7, after Cyrus says go.

## 2. New paths

```
writing-room-kit/
  PREREG-v0.5.md                 ← P2, written before any P3 run or any F14 test-split number
  RESULTS-v0.5.md                ← P5
  PILOT-PROTOCOL.md              ← P6 (design only)
  v04/controls.py                ← P0: permutation, trail swap, essay-only, judge agreement
  v04/lineage2.py                ← P1: report v2 = v0.4 report + timing rule; writes v04/reports-v05/
  v04/derive.py                  ← P1: F14 derivation graph; writes v04/reports-v05/<id>.derive.json
  v04/effort.py                  ← P1: effort accounting per run
  v04/coach.py                   ← P1: the check→questions loop used by the C13/C14 attackers
  v04/judge_packets/             ← P0: stripped runs for Claude judges + their JSON answers
  v04/reports-v05/               ← all v0.5 reports (+ _controls.json, _scores.json, _curve.json)
  v04/runs-v05/                  ← new runs C11–C14 (room.py ROOM_SESSIONS_DIR as before; finalize writes here via an env var, below)
```
The `finalize.py` change: honour `ROOM_RUNS_DIR` (default `v04/runs`), and add `ARM_STRUCT` entries `C11: typed`, `C12: retyped`, `C13: retyped`, `C14: retyped`. No other v0.4 code changes except the additions in P1, each with a test.

---

## P0 — Controls on the existing 66 runs (no new students; ~1–2 h, ~400 LLM calls)

These come first because if O2 or O3 holds, the v0.4 results are suspect, and we must know before building more.

**P0 is exploratory-confirmatory:** write `PREREG-v0.5.md` §A (the P0 endpoints and predictions below, copied as-is) **before** running `controls.py`. That takes 10 minutes and is not optional.

### P0.1 Permutation test (O1), no LLM
- For each v0.4 headline comparison, run 10,000 label shuffles within the two pooled arms and report the exact or approximate p of the observed AUC. Comparisons: C1 vs C4, C5, C6, C7, C8, C9 on composite_nostruct; C1 vs C6–C9 and C10 vs C6–C9 on F13.
- Also report the **smallest AUC that reaches p < 0.05** at 6 vs 6 (for context: at 6 vs 6, AUC 1.00 has exact one-sided p = 1/924 ≈ 0.001).
- **Prediction:** p < 0.01 for every AUC ≥ 0.95. The test is trivial, but it must be in the table.

### P0.2 Trail swap (O2): the most important control
Build **hybrid runs** in memory only (never written to `v04/runs/`):
- The writing side comes from essay owner *i*: `essay`, `citations`, `drafts`, `struct`.
- The thinking side comes from trail owner *j*: `turns`, `src_requests`, `picks`, `unlocked_docs`, `read_passages`, `counters`, `question_kinds`.
- *j* is a fixed derangement within the same arm (seed 5): j = the next run in sorted order, wrapping around.

Pools:
- **S1 honest swap:** C1 essays × other C1 trails (6), and C10 × other C10 (6).
- **S2 relay with an honest trail ("stolen trail"):** each C8 essay with C1 trail *k* (6). This is the attacker who copies a classmate's whole Room trail.
- **S3 honest essay with a relay trail:** C1 essays with C8 trails (6). This is the mirror check.

Run `lineage.report()` on each hybrid; v0.4 judge, `--force`, writing to `v04/reports-v05/swap/`.

**Endpoints:**
- E-A1: AUC(matched honest C1 + C10 vs S1) on composite_nostruct and on the claim component. Pass ≥ 0.80.
- E-A2: mean drop in claim lineage, matched minus S1, with its bootstrap CI.
- E-A3: S2's composite compared with C8's own. Does a stolen honest trail rescue an outside essay?

**Prediction (planner, Opus):**
- E-A1 ≥ 0.80 for C1, and weaker for C10. The six C10 students wrote near-identical opening positions, so a swapped C10 trail may look like a fit.
- S2 stays low (claim lineage < 40), because the classmate's statements don't contain this essay's specific claims.

**If E-A1 < 0.70:** the report is measuring topic, not derivation. **Stop, write it up, tell Cyrus. Do not run P3.**

### P0.3 Essay-only baseline (O3, part 1)
Two kinds of baseline, both reported as AUC of C1 vs each arm:
- **Stylometry, no LLM:**
  - mean sentence length
  - type–token ratio over the first 400 words
  - citations per 100 words
  - share of sentences containing a number
  - mean paragraph length
- **Blind LLM read, one call per essay:**
  - The prompt gives the essay only (no trail, no arm) and asks for json `{"process": 0-100}`, where 0 means "produced in one pass by a writing tool" and 100 means "developed step by step by a student who researched it".
  - The wording must not contain the banned words.

**Prediction:** the essays alone DO separate C1 from the relay arms (AUC ≥ 0.80 on at least one stylometric feature), because honest essays are Sonnet's and outside essays are DeepSeek's. That is the confound P3's model swap exists to break, and finding it is expected. Report it plainly.

### P0.4 Judge swap (O5)
- **J1, the same vendor's other model:**
  - Re-run the claim-lineage and ancestor calls only on all 66 runs with `DEEPSEEK_MODEL=deepseek-reasoner`, set in the process environment. Do not edit `demo/llm.py`; it already reads the env var. Write the results to `v04/reports-v05/judge-r1/`.
  - **Smoke test first:** one `claims` call. If the model rejects json mode or temperature, retry without json mode. `llm.parse_json` tolerates fences. If it still fails, record the failure and skip J1.
- **J2, a different vendor (Claude):**
  - `controls.py packets` writes `v04/judge_packets/<n>.json` for **24 runs**: 4 each from C1, C10, C4, C6, C8, C9, picked by seed 7.
  - Each packet holds `strip(run)` (no arm, no id), the essay's claims as already extracted in the v0.4 report (so the claim list is identical), and the student statements formatted exactly as `fmt_statements`. The packets are renamed `P01..P24` and the key goes to `v04/judge_packets/_key.json`.
  - Spawn **3 Sonnet judge workers**, 8 packets each. Each gets only the v0.4 ancestor system prompt (copy it verbatim from `lineage.claim_lineage`) and writes `P<n>.answer.json`.
  - `controls.py import` scores claim lineage from the answers.
- **Endpoints:**
  - E-A5: per-run Spearman between the v0.4 judge and each of J1 and J2 on claim lineage.
  - E-A6: AUC of C1 + C10 vs C6 + C8 + C9 under each judge.
- **Prediction:** Spearman ≥ 0.6 and the AUC direction is unchanged (≥ 0.80) under both judges.

### Gate A (Cyrus)
Hand Cyrus a one-screen summary: P0.1–P0.4 numbers against their predictions, and whether the stop rule fired. **Wait for "go" before P1.**

---

## P1 — Tooling (~3 h; all stub-tested, `ROOM_LLM=stub`)

### P1.1 Timing rule: `lineage2.py` (report v2)
The loop-relay attacker gets the Coach's questions after drafting, has an outside AI write "explanations", and types them into the Room. Under v0.4 those count as ancestors. They must not.
- For each essay claim, find its **birth turn**: the turn of the first saved snapshot (draft or `check`, below) with a paragraph whose `difflib` ratio to the claim's essay paragraph is ≥ 0.5 and which contains the claim's key content. Use the cheap test first: ≥ 50% of the claim's content words (5+ letters) appear in that paragraph. If no snapshot qualifies, the birth turn is the final submission turn.
- A claim's ancestor counts as a **derivation** only if `ancestor_turn < birth_turn`. If the only ancestor is at or after the birth turn, the claim is **explained after**. That isn't a gap and isn't a derivation; it's a separate list the report hands to the person ("explained after it was written: worth hearing live").
- The report v2 keeps every v0.4 field and adds:
  - `claims[].birth`, `claims[].kind` ∈ {derived, explained_after, none}
  - `components.claim_v2` (the share derived)
  - `composite_v2` (claim_v2 in place of claim)
  - `explained_after` (a list of questions)
- Every report must say which report version it is.
- **Re-score all 66 v0.4 runs** with lineage2 into `v04/reports-v05/`. The ancestor judge calls can be reused from `v04/reports/<id>.json` (same claims, same ancestors), so only birth turns are new and **no LLM is needed** for old runs.
- **Endpoint E-B1 (fairness):** honest C1 + C10 mean composite_v2 drop vs v0.4 is ≤ 10 points.
  - **Prediction:** about 5. Honest students talk *before* they draft, but they also comment on drafts afterwards, so a few claims will move to explained_after.
  - **If honest drops more than 15, the timing rule is unfair as specified:** report it, propose a variant, and don't silently tune it.

### P1.2 F14 derivation graph: `derive.py` (the founder's "many small ideas")
- **Input:** the student statements in order, from `say` and `confident` turns and pick reasons, plus the passage texts read before each statement.
- **The LLM call** (`tag="derive"`, chunks of 12 statements) lists each statement's **idea units**: new propositions not already said by the student earlier. For each unit it gives a parent:
  - `{"type":"student","turn":t}`, building on the student's own earlier unit
  - `{"type":"passage","pid":...}`, which must be read before this turn; code verifies this, and a parent read later becomes `none`
  - `{"type":"assistant","turn":t}`, a point the assistant raised that the student now restates
  - `{"type":"none"}`, a leap
- **Metrics per run, all defined now:**
  - `F14a step size`: mean new units per statement that has ≥ 1 unit. Honest direction: low.
  - `F14b parentage`: share of units with a non-`none` parent. Honest direction: high.
  - `F14c grounded chains`: share of *essay claims* (from the v2 report) whose derived ancestor unit has a parent chain reaching a passage within ≤ 3 hops. Honest direction: high.
  - `F14d refinement`: one LLM call comparing the student's first stated position with the essay's thesis, `{"relation":"same"|"sharpened"|"changed"}`. This is descriptive only, never in a score. Thesis-first honest students should be sharpened or changed.
- **Leaps are not marks.** Each `none` unit becomes a question: "At turn t you said X. How did you get there?" That is the founder's "it's OK if it's big, we just ask how it was derived."
- **Dev/test split, to stop F14 being tuned to the answer:**
  - Runs `-1` and `-2` of every arm are the **dev set**. The executor may look at dev numbers and fix bugs.
  - Runs `-3` to `-6` are the **test set**. **Freeze `derive.py` and record its sha256 in PREREG-v0.5 §B before computing anything on the test set.**
  - Test-set numbers are the only ones reported as results.

### P1.3 `effort.py`: the cost axis
Per run:
- student turns
- characters typed by the student
- reads
- distinct passages
- rounds of `check`
- **outside-AI calls**: relay operator calls plus outside-writer calls, counted from `_calls.jsonl` tags tied to the run. Add a `run` field to llmx log lines via the env var `ROOM_RUN_ID`, set by relay.py and coach.py. That is metadata only, never prompt text.

Honest runs have 0 outside calls by construction. For them, report turns and characters as the effort the attacker must match.

### P1.4 `coach.py` and `room.py check`: the feedback loop
- `room.py check ID ESSAYFILE` saves a snapshot (kind `check`, struct per arm). It runs lineage2 on a provisional run and posts **up to 5 Coach turns**, policy `COACH-CHECK`. They are the report's own mismatch and explained-after questions, phrased as questions, and never say which component scored low.
- `room.py answer ID "text"` is a student turn of kind `answer`, routed to `student_statements`. It counts as a statement for lineage, but the timing rule applies to it.
- A test proves that an `answer` given after a claim's birth gives that claim `explained_after`, not `derived`.

### P1.5 relay.py: new styles (no change to the existing four)
- `--style honest-ds` (arm **C11**): the operator gets **no essay**. It gets only the essay question and the honest C1 instruction text, and must build the work itself. It writes drafts and the final essay through new actions `{"action":"write","text":...}`, which writes the next draft file, and `{"action":"submit","text":...}`, the final essay. This is the **model swap for the honest side**: a DeepSeek honest student.
- `--essay-file PATH` (any style): use this essay instead of calling `outside.py`, for **C12**, where the outside writer is Claude.
- `--style loop` (arm **C13**, the white-box adaptive attacker). The operator's system prompt includes a plain summary of how the report works:
  - Claims need an earlier ancestor stated in the Room *before* they appear in a draft.
  - Claims built on evidence that was never read get questions.
  - Big jumps get questions.
  - Explanations given after a claim is written don't count as derivation.

  It starts with the outside essay. After its first `draft` it may call `{"action":"check"}` up to **3 rounds**. The check questions go back to the operator, which may:
  - (a) ask the **outside writer** (outside.py, a new `revise` mode: essay plus questions in, revised essay out) to revise the essay
  - (b) narrate new statements in the Room before the next draft

  Cap: 80 actions. This is the founder's direction (a), "paste back the Coach feedback and keep redoing the passage".
- `--style stubborn` (arm **C14**): the essay never changes. After the first draft, `check` runs; for each question the operator gets the outside writer to produce an answer and types it with `answer`. Then it submits unchanged. This is the founder's direction (b), "insist on the final paragraph".

### P1.6 Tests (add to `v04/tests/test_v04.py`, all stub)
1. The timing rule: derived vs explained_after vs none.
2. The birth turn is found from the first matching snapshot.
3. An `answer` after birth gives explained_after.
4. `derive.py` turns a passage parent read after the statement into `none`.
5. The trail-swap builder never writes to `v04/runs/`, and the hybrid keeps writing fields from *i* and thinking fields from *j*.
6. The relay `honest-ds` operator prompt contains no essay text.
7. Effort counts outside calls only for the matching `ROOM_RUN_ID`.
8. `finalize` honours `ROOM_RUNS_DIR`.

**Done when** the old 13 tests and the 8 new ones pass. Then do one stub dry run of each new relay style end to end.

### P1.7 Live smoke (2 runs, ~150 LLM calls)
- `DRY-C13` and `DRY-C14`, into `v04/dryrun/_runs/`.
- Check by eye:
  - The check questions read as questions, with no score leakage.
  - The loop actually revises.
  - Birth turns look right on 5 claims, which you check by hand.

Fix anything you find, and record it in PREREG-v0.5 §C (pre-run amendments).

---

## P2 — Pre-register v0.5 (~30 min) → Gate B

Write `PREREG-v0.5.md` with:
- **§A**: the P0 endpoints and predictions, already written before P0.
- **§B**: the P3 arms, the F14 definition plus the frozen `derive.py` sha256, the endpoints below with predictions, the exclusions, and n.
- **§C**: amendments.

**Arms (n = 6 each, 24 runs):**

| Arm | Who | Essay | Purpose |
|---|---|---|---|
| C11 honest-ds | DeepSeek operator, no essay, honest instructions | its own | Model swap: honest side not Sonnet |
| C12 relay-claude | DeepSeek operator, `careful` style | written by a **Claude** worker given only the `outside.py v4` prompt text (corpus with ids, 500–800 words, inline [DxPy]) | Model swap: outside side not DeepSeek |
| C13 loop | DeepSeek operator, white-box, up to 3 check rounds plus outside revisions | outside.py v4 | Founder's direction (a), adaptive attacker |
| C14 stubborn | DeepSeek operator, answers questions through the outside writer | outside.py v4, never changed | Founder's direction (b) |

**Endpoints (AUC; bar 0.80; bootstrap CI 2000; one-sided permutation p):**
- **E-C1 model swap:** composite_v2 of C11 vs C12.
  - Prediction ≥ 0.80. If it fails, the v0.4 separation was largely writer-model style: say so in the first line of RESULTS-v0.5.
- **E-C2 model-swap essay-only:** the P0.3 baselines on C11 vs C12.
  - Prediction: they separate less than on C1 vs relay, which shows the trail carries signal the essay doesn't.
- **E-C3 loop:** composite_v2 of honest (C1 + C10 + C11) vs C13 after its final round.
  - Prediction ≥ 0.80, because revisions arrive as large rewrites with explained_after ancestors.
  - Also report the **per-round trajectory** of C13: composite_v2, open questions, effort.
- **E-C4 stubborn:** C14 open-question count. Prediction: every C14 run ends with ≥ 3 questions in `explained_after` plus `none`, and composite_v2 < 60.
- **E-C5 F14 (test set only):** honest (C1, C10, C11) vs outside (C6–C9, C12–C14) on F14a, F14b, F14c.
  - Prediction ≥ 0.80 on F14b or F14c.
  - F14a step size may fail: careful relays chop claims small. That would be fine, because chopping alone isn't derivation.
- **E-C6 fairness:** share of honest runs (C1, C10, C11) with ≥ 1 open question of kind `none`, and the median number of open questions per honest run.
  - This isn't pass/fail. It's the number the pilot must beat with real students.
- **E-C7 cost of passing:** for each arm, effort (student characters typed and outside calls) against composite_v2, with C13 per round.
  - **Pass** is a *shape*: no outside arm reaches the honest composite_v2 median with less student effort than the honest median.
  - Prediction: holds. If C13 crosses below the honest effort line, that is the headline weakness, and we report it.

**Exclusions:**
- Runs that fail `finalize`.
- C11 runs with an essay under 400 words.
- Any run whose `law1` audit has more than 2 violations; report these, don't drop silently.

### Gate B (Cyrus)
Cyrus reads PREREG-v0.5 §B. **Wait for "go".**

---

## P3 — Runs (~2–3 h wall; up to 3 relay processes in parallel)

1. **C12 essays first:** spawn 6 Sonnet "outside writer" workers. Each gets only `v04/arms/_outside_writer_claude.md`, which holds the exact `outside.py v4` prompt text and corpus. Each writes `v04/sessions/C12-n-outside.txt`. Then `relay.py C12-n --style careful --essay-file ...`.
2. **C11:** `relay.py C11-n --style honest-ds`.
3. **C13:** `relay.py C13-n --style loop`.
4. **C14:** `relay.py C14-n --style stubborn`.
5. Every run must set `ROOM_RUNS_DIR=v04/runs-v05`, `ROOM_SESSIONS_DIR=v04/sessions-v05` and `ROOM_RUN_ID=<id>`.
6. Then run `audit.py`, `lineage2.py`, `derive.py` (test-set ids for results; dev ids allowed for the debug log) and `effort.py` on all new runs. Do the same for the old C1–C10 runs where they're needed for E-C5 to E-C7. For old runs, derive.py needs LLM calls: about 66 × 3.

Budget: about 24 runs × 60–90 actions ≈ 2,000 operator calls, plus the Room's own calls, plus judges. That's roughly 5–6k DeepSeek calls. Check that `_calls.jsonl` grows steadily, and stop if a run loops (the same action 5 times).

## P4 — Mechanism trace (~1 h): "why it separates", per run

The not-luck argument needs to show *which behaviour* drove each separation, as was done for C10.

For every outside run whose composite_v2 is below the honest minimum, and for every honest run with ≥ 2 open questions, `controls.py trace ID` prints:
- each component's contribution against the honest mean
- the top 3 claims driving it, each with kind (none / explained_after / derived), birth turn, ancestor turn and the cited-passage first-read turn
- F14 leaps

**Ablation table:** recompute the headline AUCs (C1 + C10 + C11 vs all outside arms) with each component removed in turn (claim_v2, source, cite, change). This shows which components carry the result, and whether anything carries it alone.

## P5 — Results (~1.5 h)

Write `RESULTS-v0.5.md` in the house style:
- the outcome first, one line per objection O1–O5: answered, partly answered, or not
- the tables
- the predictions against outcomes, wrong ones included, as in v0.4
- the cost-of-passing figure, as an inline SVG or a table
- the mechanism traces for 3 example runs
- limits:
  - all simulated
  - n = 6
  - one API vendor plus Claude workers
  - F14 defined by the planner (test-split protected)
  - P0.4 J2 on 24 runs only
- a **"For investors / for CLEAR"** box of ≤ 6 sentences, written to the claim in §0, not to "we tell them apart"

Then regenerate the review page:
- Extend `scratchpad/build_review.py` with a v0.5 section, or write a new one.
- Republish to the same artifact URL: https://claude.ai/artifact/U7SJrpGKa16MUdp3dt7B65. Read it first with `Artifact action:"read"` and build on what comes back.

## P6 — Real-student pilot protocol (design only, ~1 h) → `PILOT-PROTOCOL.md`

This is the step simulation can't replace. The doc must cover:
- **Conditions:** 6–10 students per condition.
  - Honest.
  - "Use any outside AI however you like, then submit through the Room": consented and paid, research framing, no grades at stake.
  - Optional: thesis-first honest.
- **Measures:**
  - E-C6 fairness (open questions per honest student)
  - E-C5 / E-A1 replicated on real trails
  - **the live gate:** a TA asks each student the report's top 3 questions for 5 minutes, and blind raters score the answers
  - time on task
  - student perception, including whether it felt like surveillance
- **Ethics and law:**
  - consent
  - law 7 (students own the trail; the school sees derived signals only)
  - an accessibility route (voice, extra time)
  - English-as-a-second-language and anxious-student subgroups for fairness
  - no consequence attached to any output (law 6)
- **Success criteria**, set before recruiting, mirroring §0's three parts.
- A list of what Cyrus needs to supply: an instructor, a course and an ethics contact.

## P7 — Bookkeeping (only after Cyrus reads RESULTS-v0.5 and says go)
STATUS, UPDATE_LOG, CHANGELOG, OPEN_LOOPS (next free OL-031, covering the hand audit, PREREG-v0.4 design note 1, and the pilot), DECISIONS only for what Cyrus locks, and the design/README row. No commits.

---

## Order and gates

```
P0 controls (prereg §A first) ──Gate A──► P1 tooling + tests + smoke ──► P2 prereg §B (derive.py frozen) ──Gate B──► P3 runs ──► P4 trace ──► P5 results + review page ──► P6 pilot protocol ──(Cyrus go)──► P7 docs
```
Stop rules:
- P0.2 E-A1 < 0.70 → stop after P0 and report.
- P1.1 honest drop > 15 → report and propose a variant before P2.
- Any law-1 audit with > 2 violations in a run → pause and report.

## What "working as designed, not luck" will mean if this all passes

| Objection | Answered by |
|---|---|
| O1 luck | P0.1 permutation p-values, plus a second set of arms (C11–C14) |
| O2 topic, not link | P0.2 trail swap: someone else's trail doesn't fit |
| O3 model style | P0.3 shows the essay-only confound exists, then E-C1 shows the trail result survives the swap |
| O4 adaptive attacker | E-C3 / E-C4 / E-C7: the loop and stubborn paths either stay open or cost as much as the work |
| O5 one judge | P0.4: a second DeepSeek model and a Claude judge agree |
| "Why does it work?" | P4: traced to named behaviours (claims born before evidence, explanations after the fact, leaps), with the ablation table |

If any row fails, that failure is the result and goes in the first line. We've been wrong in public three times already (v0.3, and the C6–C9 and C10 predictions), and that track record is part of what makes the passes credible.
