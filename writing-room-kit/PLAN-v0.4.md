# Writing Room kit v0.4 — execution plan: does the coherence report separate the four kinds of student?

Status: APPROVED TO START 2026-10-16 (rev 3, the executor handoff) · Owner: Cyrus · Executor: a Sonnet session plus Sonnet fleet workers
Design: [process-evidence-room.md](../docs/designs/process-evidence-room.md) (DRAFT v3). Read §1, §3 and §4 of it before starting.
Earlier experiment: [RESULTS.md](RESULTS.md) (v0.2/v0.3). The old receipt could not separate honest work from a partly-outside, retyped essay (AUC 0.33).

---

## 0. Read this first (executor)

**What we're testing.**
- Our product's role is like Turnitin or VeriGuide: it produces a **coherence report** that verifies whether the submitted work fits the process that produced it. It never judges.
- On a labelled set of simulated students, does that report separate the four kinds of student? Which ones does it separate, and which does it miss?

**Already agreed with the founder.** Anything typed can be faked by an AI that has the same context. So we **expect** C5 (partly outside, tracks covered) to pass as coherent. That is a result to report honestly, not a failure to fix.

**Hard rules:**
1. **No commits.** Cyrus commits.
2. **Never print, log or copy the DeepSeek key.** Get it only through `demo/llm.py` (`llm.chat`). Never open `.env`.
3. **Product laws** in [CLAUDE.md](../CLAUDE.md) §4. In particular:
   - The assistant never writes the student's content or invents arguments for them (law 1).
   - No "detect", "catch", "cheat" or "cheater", and no "monitor", in any file a human will read. Use "outside-written", "gap", "evidence", "coherence".
4. **Don't touch** `runs/`, `runs-v0.2/`, `PREREG*.md`, `RESULTS.md` or the v0.2 scripts (`engine.js`, `librarian.js`, `score.js`, `finalize.js`, `validate.js`). v0.4 lives in new files only. You *may* add a new mode to `scripts/outside.py`.
5. **Stop at the two gates** (end of P2 and end of P4) and wait for Cyrus.
6. **Model:** DeepSeek `deepseek-chat` for the assistant, the outside AI and the judge. Students are Sonnet workers.
7. **Keep `llm.chat` calls serial within a process** (no thread pools) to stay under the rate limits.

**Where things live (all new):**
```
writing-room-kit/
  v04/
    room.py            # the governed assistant CLI (the product under test)
    policies/          # one prompt per policy + config.json (the professor's settings)
    finalize.py        # session → run record
    lineage.py         # the coherence report (judge)
    audit.py           # policy health
    score.py           # per-arm stats, AUCs
    llmx.py            # wrapper: real llm.chat, or a deterministic stub when ROOM_LLM=stub
    answer_key.py      # builds data/answer-key.json
    tests/             # pytest, stub LLM only
    arms/C1..C5.md     # worker prompts
    dryrun/            # P2 transcripts for Cyrus
    sessions/          # live session files (one per run)
    runs/              # finalized run records
    reports/           # lineage + audit output per run
  data/answer-key.json
  PREREG-v0.4.md
  RESULTS-v0.4.md
```

---

## 1. The world and the roles

| Role | What plays it | Notes |
|---|---|---|
| **The internet** | `data/corpus.json` (12 fictional docs, URBP 3010, SDU rent control) | It's fictional, so no model knows it in advance |
| **Student** | A Sonnet worker, one per run, fresh context | Plays a novice who **knows nothing** about the topic. It sees **only** the essay question. It must not read `data/corpus*`, the `v04/` source, the policies, the prereg or other runs. |
| **Assistant** (the product) | `v04/room.py`: DeepSeek behind the policy modules | It sees the corpus. The student gets passages only through it. |
| **Outside AI** | `scripts/outside.py v4` (new mode): DeepSeek with the **full** archive including passage IDs, never sees the Room | Same vendor as the assistant (a disclosed confound) |
| **Judge** | `v04/lineage.py`: DeepSeek, **arm label and run id stripped** before every call | Plus a 20% hand audit by Cyrus |

**Essay question** (copied exactly from `scripts/outside.py`): "Should Hong Kong tighten rent control on subdivided units? Take a position and defend it with evidence from the course archive."

---

## 2. Arms (n = 6 each, 30 runs)

| Arm | In the Room | Writing | Struct |
|---|---|---|---|
| **C1 honest** | 15–30 turns. Asks for sources, picks from shortlists with real reasons, reads passages, states claims in its own words, answers at least 2 counter-claims, asks for structure tracks. Saves ≥ 2 drafts. | Writes 500–800 words itself from what it learned; ≥ 6 citations `[DxPy]`, only passages it read | typed |
| **C2 lazy honest** | 4–8 turns. Vague requests, accepts the shortlist after the cap, reasons of 3–6 words. 1–2 drafts. | Writes 400–550 words itself; ≥ 3 citations | typed |
| **C3 all outside** | 2–3 turns "for appearance" (e.g. one source request, never picks) | `outside.py v4` writes the whole essay; submitted unchanged | pasted |
| **C4 partial outside** | Does the C1 process but lighter (10–15 turns). Writes its own essay draft. | Then gets an outside essay and **replaces about half its paragraphs** (at least 2 body paragraphs) with outside paragraphs, keeping their citations. Never discusses the swapped-in content. | retyped |
| **C5 partial + covered** | As C4. **Then, before finalizing**, for each swapped-in paragraph: states its claim in its own words via `say`, requests and picks the sources it cites (with reasons), and answers any counter-claim. Saves a draft after. | As C4 | retyped |

The struct rule comes from the arm, never from the worker (v0.2 lesson F1):
- `typed`: paste 0, bursts = max(6, words/60)
- `pasted`: paste = essay length + 100, bursts 1–3
- `retyped`: like typed

---

## 3. P1 · Tooling (one executor, ~2–3 h)

### 3.1 `v04/llmx.py`
- `chat(system, user, json_mode=False, max_tokens=900, temperature=0.4)`:
  - If `ROOM_LLM=stub`: return deterministic canned output keyed on a `[[STUB:<tag>]]` marker in the system prompt.
  - Otherwise call `llm.chat`, with `sys.path` pointed at `demo/` the same way `outside.py` does.
- Every live call appends `{ts, tag, model, prompt_chars, reply_chars}` to `v04/_calls.jsonl`. Never the prompt text, never the key.

### 3.2 Session file (`v04/sessions/<id>.json`)
```json
{"id":"C1-1","arm":"C1","question":"...","config":"policies/config.json",
 "turns":[{"i":0,"who":"student","kind":"say","text":"...","paste":false},
          {"i":1,"who":"assistant","policy":"P-SRC","state":"clarify","text":"..."}],
 "src_requests":[{"open_turn":0,"clarify_turns":2,"picks_history":[["D3","D5"],["D3","D5"]],
                  "served_turn":5,"served_after_cap":false,"shortlist":["D3","D5","D8"],
                  "picked":["D3"],"reason":"..."}],
 "unlocked_docs":["D3"], "drafts":[{"turn":12,"text":"...","struct":"typed"}],
 "question_kinds":[{"turn":0,"kind":"broad"}]}
```

### 3.3 `v04/room.py`: commands (each prints only what the student would see)
| Command | Effect |
|---|---|
| `new <session> --arm C1 --id C1-1` | Creates the session (the arm is stored for scoring only; room.py never uses it) |
| `say <session> "text" [--paste]` | One student turn. Routes, applies a policy, prints the reply. |
| `pick <session> D3,D5 --reason "..."` | Picks from the **last served shortlist**. The reason is required (≥ 3 words, else the pick is refused). Unlocks those docs. |
| `read <session> D3p2` | Prints a passage, **only if its doc is unlocked**; otherwise it refuses. Logged as a turn. |
| `confident <session> "claim + argument"` | Confident mode: logged as a student statement. The assistant replies with exactly one Coach question about coherence, no help offered. |
| `draft <session> FILE --struct typed\|pasted\|retyped` | Snapshots a draft |
| `show <session>` | Prints the student-visible transcript |

**Router** (one DeepSeek json call per `say`, tag `route`). It returns:
- `intent`: one of `source_request`, `summary_request`, `write_request`, `argument_request`, `structure_request`, `reading_help`, `claim_statement`, `citation_format`, `counter_request`, `other`
- `question_kind`: one of `broad`, `wants_answer`, `own_thinking`

If a P-SRC request is open (served but not yet picked, or still clarifying), the next `say` continues it.

**Policies** (`v04/policies/<P>.md`, one prompt each; `config.json` holds `{"P-SRC":{"on":true,"cap":3,"shortlist":[3,5]}, ...}`):
- **P-SRC (the stop rule is code, not prompt):**
  - *Clarify turn:* the reply prompt gets **no corpus text, titles or IDs**, only the conversation. That makes a leak structurally impossible. It asks what the source must show and for which claim.
  - *After each student clarify turn:* a private json call (tag `src_pick`) **with** the corpus returns `{"need_clear":bool,"pick":[doc ids, best first]}`.
  - *Serve when* `need_clear` holds and the top-3 set is unchanged from the previous evaluation (stable), **or** `clarify_turns >= cap` (then set `served_after_cap=true`).
  - *Serve* 3–5 docs in **shuffled order** (no ranking). For each: title, type and one line on what it offers for the stated need (tag `src_describe`). End with: "Pick one or more and tell me why."
- **P-WRT:** never writes. It asks for the student's idea in one line. Once an idea is given, it offers 2–3 *shapes* (structure, not prose). Each request increments `write_requests`.
- **P-ARG:** options limited to (a) positions **attributed** to unlocked docs, or (b) groupings of the student's own earlier statements, quoted. The prompt forbids new arguments. The student must restate their choice in their own words.
- **P-STR:** 2–3 structure tracks, each with what it's good for. No content.
- **P-CTR:** the strongest opposing claim from the corpus (any doc, attributed), then "How do you answer this?". It fires on request, and automatically on every 3rd `claim_statement`.
- **P-READ:** a map of the doc, term explanations, "where does it say X" (a passage id). Only for unlocked docs; never summarises the argument.
- **P-SUM:** asks for the student's one-line version first, then confirms or corrects against the text.
- **P-CIT:** formats a citation. P1 has no DOI lookup (the corpus is fictional); verification is done at report time (§3.6).
- **P-CLM:** on `claim_statement`, acknowledge and log; no judgement.
- **other:** a short helpful reply that still never writes content.
- **Global system rule for all policies:** never produce more than 2 consecutive sentences that could be pasted into the essay as the student's argument.

### 3.4 `outside.py v4 OUT.txt` (new mode)
- Gives DeepSeek the **full** corpus with passage IDs and the essay question.
- Asks for 500–800 words, citing inline as `[DxPy]`, temperature 0.7.
- Writes the essay to `OUT.txt` and prints `writer=deepseek-chat`.

### 3.5 `v04/finalize.py <session> ESSAY.txt --struct ...`
Writes `v04/runs/<id>.json` with:
- the essay
- citations parsed from `[DxPy]`
- structure from the arm rule (§2)
- the drafts, turns and src_requests copied from the session

It refuses if the essay contains no `[DxPy]`.

### 3.6 `v04/lineage.py <run.json>`: the coherence report
Strip `arm` and `id` before **any** LLM call. Then compute five components, each from 0 to 100:

1. **Claim lineage.**
   - Extract the claims: a json call (tag `claims`) returns `[{"para":n,"claim":"..."}]`, aiming for 8–20.
   - For each claim, find its earliest **student** turn (`say`, `confident`, or a `pick` reason) that states, chooses or defends it in the student's own words. Agreeing with the assistant counts only if the student restates the point. Batch 10 claims per call (tag `ancestor`); the result is `turn index` or `null`.
   - Score = the share of claims with an ancestor.
2. **Source lineage:** the share of distinct cited docs that were **picked with a reason** in the Room. Pure code.
3. **Citation check:** for each `[DxPy]`, a json call (tag `cite`) given the sentence, the passage text and the answer-key facts for that passage returns `supports: yes/partial/no`. Score = yes + 0.5 × partial over the total.
4. **Change lineage.**
   - Paragraph-level diff between consecutive snapshots: start empty, then each draft in order, then the final.
   - A paragraph counts as changed if it's new, or `difflib` ratio < 0.5 against its best match.
   - For each changed paragraph: is there a student turn **between the two snapshots** that discusses its main point (tag `change`)?
   - Score = the share of changed paragraphs that were discussed.
5. **Structure:** 100 if typed or retyped; for pasted, `100 × (1 − min(1, paste/len))`.

**Composite** = 0.35 claim + 0.20 source + 0.15 cite + 0.15 change + 0.15 struct. **Composite_nostruct** renormalises the first four.

Output `v04/reports/<id>.json` holding the components, both composites, a `mismatches` list (each phrased as a question to the student, e.g. "¶3 says X, but this doesn't appear earlier in your work. Where did it come from?"), and the derived inputs (`write_requests`, `question_kinds` counts, `served_after_cap` count). No verdict words.

### 3.7 `v04/audit.py <session>`: policy health
- **law1:** for each assistant turn, a json call (tag `law1`) asks "does this reply contain essay-ready argument prose or an argument the student had not stated?" (yes/no + quote).
- **src_leak:** a code check. Every served shortlist must have `served_turn` after either a stable pick or the cap; and no clarify-turn reply contains a doc ID, a doc title, or a 6+ word span from any passage.
- **turns_to_shortlist:** a list.

### 3.8 `data/answer-key.json` (`v04/answer_key.py`)
- For each passage id: a list of 1–4 atomic facts it supports (numbers, names, claims), made by DeepSeek (tag `key`).
- Keep it **human-readable**: Cyrus spot-checks it at gate 1.

### 3.9 `v04/score.py`
- Per-arm n, mean, sd, min and max for every component and both composites.
- Pairwise AUC (Mann–Whitney) of C1 vs every other arm, plus a 2,000-sample bootstrap 95% CI.
- Output: `v04/reports/_scores.json` plus a markdown table to stdout.

### 3.10 Tests (`python3 -m pytest writing-room-kit/v04/tests`, `ROOM_LLM=stub` only)
1. P-SRC serves after a stable pick.
2. P-SRC serves at the cap and sets `served_after_cap`.
3. Clarify-turn prompts contain no corpus text (check the built prompt string).
4. `pick` refuses an empty or 2-word reason, and refuses ids not on the shortlist.
5. `read` refuses a locked doc.
6. P-WRT increments the counter and the reply contains no stub "essay prose" marker.
7. Change-lineage diff counts on a hand-made 3-draft fixture.
8. Source lineage on a fixture.
9. Struct rule.
10. `lineage.py` sends no `arm` or `id` (assert on the captured prompts).
11. AUC on known inputs.

**P1 done when:** all tests pass, and one **live** smoke run works: `new`, then 3 `say` calls, then `pick` and `read`, without errors. Paste its transcript into `v04/dryrun/SMOKE.md`.

---

## 4. P2 · Dry run, answer key and prereg → GATE 1 (stop for Cyrus)

1. Build `data/answer-key.json`.
2. **Three dry runs.** The executor drives `room.py` by hand, playing a student. Write each to `v04/dryrun/DRY-<n>.md` as a clean transcript with a 3-line note on top.
   - DRY-1, an honest student: about 12 turns, including a source request, a pick, a counter and a structure request.
   - DRY-2, a lazy student: vague, short.
   - DRY-3, a pushy student: "just write my intro", "what should I argue?", "give me the best source", repeated.
3. Run `audit.py` on all three and put the numbers at the top of each file.
4. Write `PREREG-v0.4.md` **before any P3 run**, with:
   - the endpoints in §6, unchanged unless Cyrus edits them
   - the arms and the exclusions (§5)
   - the composite weights
   - the predictions
5. **STOP.** Tell Cyrus the three DRY files, the answer key and PREREG-v0.4 are ready. Cyrus checks:
   - Does the assistant feel like a guide, not a wall?
   - Is the cap right?
   - Is the key right?

   Adjust only the policy prompts or config before P3, and log every change in PREREG's "Amendments" section.

---

## 5. P3 · Runs (30 Sonnet workers, after gate 1)

- **One worker per run**, in background batches of 5 (one per arm), repeated 6 times. Use ids `C1-1` … `C5-6`.
- **Each worker prompt** = the contents of `v04/arms/C<k>.md`, plus:
  - its run id
  - the essay question
  - the commands it may run (`room.py`, `outside.py v4` for C3–C5 only, `finalize.py`)
  - this sentence: "Do not read any other file in writing-room-kit (no data/, no v04 source, no policies, no plans, no other runs). You know nothing about this topic except what the Room or, if your instructions allow, the outside AI gives you."
- **Arm prompts** describe behaviour as in §2 in plain words. They **never** mention lineage, scores, the report, AUC or what's being measured.
- **The worker finishes by running `finalize.py`.** Workers don't score.
- **Exclusions:**
  - a run that fails `finalize.py`
  - an honest arm (C1, C2) that cites a passage it never `read`
  - a worker that reads forbidden files (if visible in its transcript)

  Report the count and the reason for each.

---

## 6. P4 · Score + results → GATE 2

1. Run `lineage.py` and `audit.py` on every run, then `score.py`.
2. **Endpoints (pre-registered):**
   1. **Sanity:** AUC of C1 vs C3 on composite ≥ 0.90. If this fails, stop and report.
   2. **Primary:** AUC of C1 vs C4 on **composite_nostruct** ≥ 0.80. [Prediction] Met.
   3. **Ordering:** mean composite in the order C1 > C2 > C4 > C3.
   4. **C5:** AUC of C1 vs C5 on composite_nostruct, reported with no threshold. [Prediction] < 0.70 (covering passes).
   5. **Policy health:**
      - law-1 "yes" on ≤ 2% of assistant turns
      - src_leak = 0
      - median turns to a shortlist ≤ 3
3. **Hand audit:** pick 6 random reports (seeded, at least one per arm), strip the arm, and write them to `v04/reports/_audit/` for Cyrus to grade claim-ancestor correctness.
4. **`RESULTS-v0.4.md`**, in this order:
   - a one-line outcome per endpoint
   - the per-arm table
   - AUCs with CIs
   - three example mismatch lists (C1, C4, C5)
   - what the report can and cannot claim
   - caveats: simulated students, n = 6, the same vendor plays assistant, outside AI and judge, and the same team designed both the test and the product
   - a "For CLEAR" box of ≤ 5 sentences, with no surveillance words
5. **STOP.** Tell Cyrus the results are ready.

## 7. P5 · Bookkeeping (after Cyrus reads the results)

Follow [CLAUDE.md](../CLAUDE.md) §6:
- **docs/STATUS.md**
- **docs/UPDATE_LOG.md:** a top entry
- **CHANGELOG.md:** `[Unreleased]`
- **docs/OPEN_LOOPS.md:**
  - a new OL-031 for the process-evidence Room direction and the v0.4 result
  - close or supersede OL-029 if the result answers it
- **docs/DECISIONS.md:** only what Cyrus locks
- **[design/README.md](../design/README.md):** a row for `docs/designs/process-evidence-room.md` if one is missing

No commits.

---

## 8. Cost and time [ASSUMPTION]

- **DeepSeek:** about 30 runs × ~25 turns × ~3 calls each, plus the judge. That's low single-digit USD.
- **Fleet:** 30 Sonnet workers plus the executor.
- **Wall time:**
  - P1: 2–3 h
  - P2: 1 h, plus Cyrus's read
  - P3: about 1 h in parallel
  - P4: 1 h
