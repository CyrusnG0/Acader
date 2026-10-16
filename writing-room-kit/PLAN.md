# Writing Room kit — execution plan (v0.2 experiment)

Status: PLANNED 2026-10-16 · Owner: Cyrus · Executors: Sonnet fleet workers
Goal: turn the kit's "can the process tell?" test from **separation by construction** into a test whose answer we don't already know, then run it.

---

## 0. Review findings (why the plan isn't just "run 04-batch-protocol.md")

Baseline verified 2026-10-16: `node scripts/test.js` gives 10/10 PASS (README says 11). The examples score honest 87, hybrid 69, lazy 37 and pasted 5. The HTML engine is identical to `scripts/score.js`.

| # | Problem | Effect | Fix (phase) |
|---|---|---|---|
| F1 | Persona prompts **dictate** `pasteChars` and `editBursts` (cheater: "essay length + 120, bursts 1"; hybrid: "+80, 2–4"). | Structure (20% of the score) separates the arms *because we told it to*. It's circular. | Workers never self-report structure; it's set by the arm's behaviour rule and reported **with and without** struct (P1, P2). |
| F2 | The cheater arm has no retrievals, so trace = 0 and orphan = 0 by definition. | The 5-point score is guaranteed. It's a strawman, not a finding. | Keep it as a sanity floor; add realistic adversaries (P2). |
| F3 | **Missing arm: the laundered hybrid.** Retrieves inside, has an outside AI write, then *retypes* (no paste) and clicks citations. This is the attacker CLEAR will ask about. | Without it, the claim "the process tells" is untested. | New arm A4 (P2). |
| F4 | **Missing arm: the outside-AI question coach.** ChatGPT suggests which questions to ask, the student asks them inside, and the outside AI writes. | It tests the master brief's "outside AI can't ask for you" claim (§4), which I flagged as an overclaim. | New arm A5 (P2). |
| F5 | Retrievals are **self-declared** by the persona ("plausibly returned"). The engine never checks that a query actually yields that passage. | Sessions can be impossible. In the real platform the engine decides retrievals. | `librarian.js` CLI: the worker asks, the engine returns. Retrievals come only from the engine (P1). |
| F6 | The hybrid prompt tells the writer "should NOT echo the specific analytical path your queries took". | That instructs the very outcome continuity measures (circular again). | Remove it. The outside writer gets only the passages and the question (P2). |
| F7 | One model (Claude) plays honest *and* outside writer. Honest vs hybrid then differ only in style instructions. | Same-model confound. | The outside writer in A3/A4/A5 is a **different model** (DeepSeek via `demo/llm.py` key) where available; record the writer model per run (P3). |
| F8 | The honest-run adherence check ("no fact from unretrieved passages") is manual. | It's slow and gets skipped. | `validate.js` automates it: numbers and named entities in the essay found only in unretrieved passages (P1). |
| F9 | No pre-registered numeric threshold. | Results can be read any way. | `PREREG.md` is written and committed **before** any run (P2). |
| F10 | Small issues: `editBurssts` typo (01), "11 項 PASS" (actually 10), "theAssociation" (D9p3), CLI column misalignment (padEnd 26 is too short), `02-cheater-student.md` naming (law 10: no "cheater"), hinge/budget from the master brief not in the engine. | Cosmetic, except the naming if shown to CLEAR. | P1 cleanup. Rename to `02-outsourced-student.md`. Hinge/budget are out of scope for v0.2 (OL). |

**My prediction (pre-registered in P2, so we can be wrong in public):** A4 (laundered hybrid) will score within about 10 points of honest. Continuity is vocabulary overlap with retrieved passages, and an outside writer *fed those passages* reuses their vocabulary. If that happens, it's a **useful** result: it shows the receipt alone is not the gate, which supports law 5 (the conversation is the gate) and the master brief's §10 honesty. CLEAR should hear it from us first.

---

## Phase 1 — Tooling (sequential, 1 worker, ~1–2 h)

All in `writing-room-kit/scripts/`, plain Node, no dependencies. Load the engine by the same `eval`-strip trick `test.js` uses. **Do not fork the engine.**

1. **`librarian.js`** — `node scripts/librarian.js <draft.json> "question"`
   - Runs `classify()`. If the result is CONCLUSION, prints the refusal and records the query with `mark` and no retrieval.
   - Otherwise runs `retrieve()`. On a miss it records MISS; on a hit it prints `pid` and text, appends to `queries` (with `ts` = index) and appends `pid` to `retrievals`.
   - Creates the draft if it's missing, using `task`, `version` and `session_id` from flags `--id`.
   - This is the **only** way a run gets retrievals.
2. **`finalize.js`** — `node scripts/finalize.js <draft.json> --essay essay.txt --notes notes.txt --arm A4 --writer deepseek-chat --struct typed|pasted|retyped`
   - Parses `[DxPy]` markers in the essay into `hooks` (`pos` = char index), so hooks can't drift from the text.
   - Sets structure from the **arm rule**, never from the worker:
     - `typed`: paste 0, bursts = max(6, round(words/60))
     - `pasted`: paste = essay length + 100, bursts 1 to 3
     - `retyped`: paste 0, bursts like typed
   - Writes `runs/<arm>-<n>.json`.
3. **`validate.js`** — `node scripts/validate.js runs/*.json`, exits non-zero on hard errors. Checks:
   - (a) schema
   - (b) **replay**: every retrieval must be reproducible by `retrieve()` from some query in the session
   - (c) every inline `[DxPy]` is in `hooks` and the reverse
   - (d) **leak check**: digits and capitalised tokens in the essay that occur in some unretrieved passage and in no retrieved passage, printed as warnings; for arm A1, any leak marks the run `invalid_adherence`
4. **`score.js` upgrades** (keep the existing CLI output compatible):
   - Widen columns.
   - Add `--json` (machine output) and `--by-arm` (groups by the filename prefix `A1-…`).
   - Report per-arm n, mean, sd, min and max for composite, **composite_nostruct** (re-weighted: trace .4375, cont .375, orphan .1875) and each component.
   - Report pairwise AUC (Mann–Whitney) for A1 vs every other arm.
   - **Do not change the v1 weights.**
5. **`test.js`**
   - Add tests for `librarian.js` (CONCLUSION is refused; MISS is recorded), `finalize.js` hook parsing, and `validate.js` replay rejecting a forged retrieval.
   - Fix the README test count.
6. **Cleanup:** fix every F10 item. Keep the corpus in the HTML as the source of truth; regenerate `data/corpus.json` and `data/corpus-for-sims.md` from it with a tiny `scripts/export-corpus.js`, so the "theAssociation" fix lands in all three.

**Done when:** `node scripts/test.js` is all PASS, and a forged session (retrieval not reachable) fails `validate.js`.

## Phase 2 — Arms and pre-registration (1 worker, ~45 min; Cyrus reviews before P3)

Rewrite `claude-prompts/` to one file per arm. No prompt mentions scoring, continuity or structure.

| Arm | Who works where | Queries | Writing | Struct rule |
|---|---|---|---|---|
| **A1 honest** | inside | worker asks via `librarian.js`, 8–12, own words | worker writes from engine-returned passages only | typed |
| **A2 lazy-honest** | inside | 3–5 | worker writes, cites ≤ 2 | typed |
| **A3 hybrid-pasted** | inside, then outside | as A1 | **outside model** gets the question plus the retrieved passage texts, writes 500–800 words; the worker inserts `[DxPy]` at 6 claims | pasted |
| **A4 hybrid-laundered** | inside, then outside, retyped | as A1 | as A3 | retyped |
| **A5 outside-coached** | outside suggests questions | outside model gets the essay question **only** (no corpus) and is asked "what should I ask a librarian with the course archive?"; the worker asks those verbatim via `librarian.js` | as A3 | retyped |
| **A6 outsourced-floor** | outside only | none | outside model, no corpus | pasted |

A6 is the old "cheater" arm, kept only as a sanity floor (F2).

**`PREREG.md`** (commit before any run):
- **Primary:** AUC(A1 vs A4) on `composite_nostruct`. Success means ≥ 0.80. My prediction is < 0.70.
- **Secondary:**
  - AUC(A1 vs A5)
  - A1 vs A3 with struct (expected high; it's trivially true and shouldn't be cited as evidence)
  - A2 flags explain its low score (≥ 1 flag in every A2 run)
- **Exclusions:** A1 runs flagged `invalid_adherence`; any run failing `validate.js`. Report the excluded count.
- **n:** 6 per arm (36 runs). That's tiny; we call it a mechanism feasibility check, never a detector.

## Phase 3 — Generate runs (fleet, parallel)

- **One worker per run** (fresh context gives independence). That's 36 workers in batches of 6 to 9, e.g. one batch = one run per arm, repeated 6 times.
- Each worker reads **only** its arm prompt, `data/corpus-for-sims.md` (A1–A4 only; A5 and A6 must not read it) and the CLI usage. It must not read `score.js`, `PLAN.md`, `PREREG.md` or other runs. Say so explicitly in the worker prompt.
- **Outside model:**
  - DeepSeek through a small `scripts/outside.py`. Reuse `demo/llm.py`'s client and key; no new key handling. Temperature 0.7. Prompt logged into the run's `notes` field as `outside_prompt_sha` plus the model name.
  - **Fallback** if there is no key: a *separate* Claude worker acts as the outside writer, given only the outside prompt. Record `writer: claude-separate`. The confound is noted in results.
- Output goes to `writing-room-kit/runs/`. **Workers do not score.**

## Phase 4 — Score and write up (1 worker, ~1 h)

1. Run `node scripts/validate.js runs/*.json`, then `node scripts/score.js --by-arm runs/*.json` and `--json > runs/_scores.json`.
2. Write **`RESULTS.md`**:
   - prereg outcome first (pass or fail, in one line)
   - the per-arm table
   - AUCs
   - three example flag lists
   - what the receipt can and can't tell, and what that implies (the conversation / the Room is the gate)
   - caveats: simulated students, n = 6, mechanical librarian, writer-model confound status
3. Write a **"For CLEAR" box** of at most 5 sentences. No "detect", "catch" or "cheat"; say "outsourced", "gap", "evidence".

## Phase 5 — Repo bookkeeping (1 worker, per CLAUDE.md §6)

- `docs/STATUS.md`, `docs/UPDATE_LOG.md` (top entry), `CHANGELOG.md` `[Unreleased]`.
- New OLs (next free IDs after OL-026):
  - kit results, and whether "gate the input" becomes a decision
  - hinge and budget in the engine
  - a real-LLM librarian
  - a classroom pilot with real students
- **No commits** unless Cyrus asks.

---

## Dependency graph

```
P1 tooling ──► P2 arms + PREREG ──(Cyrus reviews prereg)──► P3 fleet runs (36, parallel) ──► P4 score + RESULTS ──► P5 docs
```

P1 and the P2 prompt drafting can overlap. **P3 must not start before PREREG.md exists.**

## Open decisions for Cyrus (defaults used if silent)

1. Outside writer = DeepSeek (default) or Claude-separate.
2. n = 6 per arm (default) or 10 (more cost, still tiny).
3. Add hinge and budget to the engine now (default: no, v0.3).
