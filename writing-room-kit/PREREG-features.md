# Pre-registration — verifying the kit-2 features (F1, F7, F8, F9) and the "construction direction" idea

Written 2026-10-16 **before any relay run**. Source claims: [feature-experiment-report.md](feature-experiment-report.md) and `archive/writing-room-kit-v0.2-copy/experiments/` (moved there on 2026-10-21).
Founder's idea: honest writers build start to finish; outside-written work is built end to start (the finished text exists first and the process is reverse-engineered from it). There must be some observable difference.

## Why the kit-2 numbers can't be taken as evidence
The harness generates both sides with code. The executor is hard-coded to ask only canonical wh-questions (F7), never miss and cite everything (F8), and run all queries before any writing (F9), so those means are 0.00 / 1.00 by construction. The hybrid is a fixed generic paragraph (12.3 continuity) while our measured retyped hybrid scored 75 (v0.3). This test removes the experimenter-written executor.

## Test
New arms driven through the real Room (v04), no hand-written behaviour:
- **C6 relay-naive (n = 6):** a DeepSeek "operator" holds the finished outside essay (written by `outside.py v4`) and drives the Room alone: says, picks, reads, saves drafts, finishes. Told only to make a process that fits the essay, in a plain way.
- **C7 relay-careful (n = 6):** same, but told to make the log look like a human's: mixed message forms (fragments, hedges), dead ends, re-asks, returning to earlier sources, drafts saved between research steps, and **not** to follow the essay's order.
- Compared with the existing C1 (honest, Sonnet), C2, C4, C5 runs (30 existing runs, unchanged).
Submitted essay = the outside essay unchanged; struct = retyped (the paste signal is off, as in v04).

## Features (computed from run logs by `v04/features.py`; no LLM)
| ID | Definition | Honest-direction |
|---|---|---|
| F7 | share of student `say` messages that are NOT a canonical wh-question (regex `^(what\|why\|how\|does\|is\|are\|can\|which)\b` and ends `?`) | high |
| F8 | waste = ½·(share of picked docs never cited) + ½·(share of read passages never cited) | high |
| F1 | returns = reads of a doc already read earlier and not immediately before + consecutive source requests (re-asks) | high |
| F9 | alternations between query events (say/pick/read/confident) and write events (draft saves, then the final essay) on the turn timeline | high |
| F11 (new, from the shower thought) | Spearman correlation between a claim's position in the essay and the turn of its earliest ancestor in the Room (claims with ancestors, ≥ 4) | honest LOW: honest students learn in discovery order and arrange later; a process reverse-engineered from a finished essay follows essay order |
| F12 (new) | mean share of each student message's word-trigrams (messages ≥ 6 words) that appear verbatim in the final essay | honest LOW: honest students ask and hedge; a relay narrates the essay |

## Endpoints (AUC, honest C1 vs the arm, in the stated honest-direction; bar 0.80, as in the kit-2 report)
1. Does each kit-2 feature (F1, F7, F8, F9) hold against **C6 naive**? (Prediction: F7 and F9 hold only if the operator really behaves like the stereotype; I expect partial.)
2. Does each hold against **C7 careful**? **Prediction: F7, F8 and F9 fall below 0.80** (a prompted operator can fake variety; the kit-2 report itself concedes this).
3. **F11 and F12 against C6 and C7.** Prediction: F11 separates naive (≥ 0.80), is weaker against careful; F12 separates both better than F7/F8/F9. Either may fail.
4. **Report check:** the coherence report on C6/C7 (the dedicated narrator from the v04 "agreed limit"). Prediction: composite_nostruct AUC C1 vs C6 and vs C7 < 0.70 (a relay that reads the Room's questions and answers from the essay is the attack we said no typed trail closes).
5. Also report, for context, every feature against C4 and C5.

## Exclusions / limits
Simulated, n = 6 per arm, one vendor again (DeepSeek plays assistant, outside AI, relay operator and judge). Honest students' draft timing in C1 was partly prescribed by their instructions (two drafts), so F9 on C1 is not independent of the instructions; reported as such. A relay run that fails to finalise is excluded and counted.

## Amendment 1 (written after C6/C7 ran, before C8 ran)
C6/C7 results showed the relay operators mostly requested, picked and read sources and rarely restated the essay's claims; the coherence report separated them from honest work (AUC 1.00), against prediction 4 (< 0.70). That tests a weak attacker, not the dedicated narrator the v04 "agreed limit" is about. **C8 relay-narrator (n = 6)** is added: the operator must, for every source the essay cites, request it, pick it with a reason, read every cited passage, then restate in its own words (paraphrasing, never pasting) the claim the essay builds on it, answer any opposing claim, and save growing drafts. **Prediction:** composite_nostruct AUC C1 vs C8 falls below 0.80 (narrating is what the report rewards), and F11/F12 may separate it because it follows essay order. Exploratory feature **F13** (not pre-registered, reported as post-hoc): evidence-after-claim share = over claims that have an ancestor, the share of (claim, cited passage in the same paragraph) pairs whose passage was never read or was first read after the claim's ancestor turn; honest-direction: low (learn, then say), the reverse being "top-down" (end-to-start) building.

## Amendment 2 (written after C8 ran, before C9 ran)
C8 results: the coherence report still separated the dedicated narrator (composite_nostruct AUC 1.00; prediction < 0.80 was wrong). Exploratory F13 (evidence-after-claim) separated every relay arm (AUC 1.00) and the read-after share was ~0.5 for relay arms against 0.10 for honest. Caveat noted before testing further: the honest arm's instructions prescribe "read, then say what you think", so honest-low F13 is partly prescribed.
**C9 relay-blind (n = 6):** the operator knows F13's idea: it must pretend to discover the essay. Start with a broad open request, never state a claim from the essay before the passage supporting it has been read, state each claim only after reading, in its own words, save growing drafts. **Prediction:** F13 AUC C1 vs C9 falls below 0.80; the coherence report AUC stays ≥ 0.80 but is lower than for C6/C7. This is the arms-race check: if a prompted operator erases the direction signal, F13 is a tax on attackers (extra turns, acting ignorant), not a gate.

## Amendment 3 (written 2026-10-17 after C9 ran, before C10 ran)
Concern raised after the results: F13's honest-low value may be prescribed by C1's instruction ("read the passages … say what you think about them"). Many real students are taught to state a thesis first. If a thesis-first honest student looks top-down, F13 would point at honest students and must not be used even as a question generator without care.
**C10 honest, thesis-first (n = 6, Sonnet workers, same common prompt and Room as C1):** before asking for any source the student states where they stand from their own intuition (with `confident`) and the main reasons they expect to hold, then tests that position against the sources, keeping, refining or changing it. Everything else as C1 (shortlists with reasons, reads, answers the opposing view, structure once, two drafts, own essay, ≥ 6 citations to passages read). Struct typed. The prompt does not mention order of reading and claiming beyond this, nor any feature.
**Endpoints (AUC, bar 0.80):**
1. F13, C10 (as honest) vs each relay arm C6–C9, honest direction low. If any falls below 0.80, F13 does not hold for thesis-first honest students.
2. F13, C1 vs C10 (how much of C1's low value is the instruction). Descriptive.
3. Coherence report composite_nostruct, C10 vs each relay arm (does the report still hold for thesis-first honest work?).
**Prediction (mine, before running):** C10's F13 mean rises well above C1's 0.10 (to ≥ 0.30), and F13 falls below 0.80 against at least C8 and C9; the coherence report stays ≥ 0.80 against all relay arms, because the thesis gets restated after reading and the claim lineage still finds ancestors.
