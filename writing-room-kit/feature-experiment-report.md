# Feature Experiment Report — can each signal tell honest from executor?

**Date:** 2026-10-16 · **Harness:** `experiments/harness.js` · **Raw data:** `experiments/results.json`

## Method

- **Task:** for each candidate signal, measure whether it separates **honest sessions** from **executor sessions** (outsider AI pre-writes essay + full process script; student executes).
- **Volume:** 10 rounds × 8 honest + 8 executor = **160 sessions per feature**. Hybrid check: 24 additional sims.
- **Conservative by construction:** the same generator wrote both sides. A signal that cannot separate these will not survive real students. Conversely, sim separation is *necessary but not sufficient* evidence.
- **Pre-registered rule:** a feature stays in the authenticity role only at **accuracy ≥ 0.80**. Thresholds are simple midpoints — no tuning.
- **Known sim limits:** honest sims are template-generated (topic walks with jump/return/re-ask/miss probabilities; essays copied verbatim from a per-round *mutated corpus*). Executor sims are the stereotype: depth-first topics, uniform question forms, zero waste, all retrievals cited.

## Decision matrix

| Feature | honest (mean) | executor (mean) | accuracy | Verdict |
|---|---|---|---|---|
| **F7 form diversity** — queries not all canonical wh-questions | 0.65 | 0.00 | **0.99** | ✅ **STAY** (flag, hidden layer) |
| **F8 waste rate** — misses + uncited retrievals | 0.24 | 0.00 | **0.89** | ✅ **STAY** (flag) |
| **F1 aliveness** — return arcs + re-asks | 1.26 | 0.00 | **0.84** | ✅ **STAY** (already in v0.3) |
| **F2 hook-variant verbatim** — citations must match the variant corpus the student actually received | 0.92 | 0.86 | 0.78 | ⚠️ **WEAK IN SIM — keep as design requirement, not a scored signal** |
| **F3 trajectory** (DEEP ramp) | 51.7 | 50.0 | 0.70 | 🔻 **REMOVE from authenticity role** — keep as effort signal (lazy detection) |
| **F4 citation spread** | 51.5 | 53.5 | 0.42 | 🔻 **REMOVE — inverted**: the executor's evenly spaced citations *score higher* than a human's |
| **F6 continuity** | 74.3 | 88.2 | 0.17 | 🔻 for executor — **but recategorize: it is the HYBRID kill-signal** (below) |

## Findings that matter

1. **F7 form diversity is the strongest new signal (0.99).** Real students ask in fragments, hedges and half-sentences; scripts ask in uniform grammar. Caveat: a rubric-aware attacker can fake it, so it belongs in the **hidden 20% layer** (never published), and it passes the byproduct principle — honest question-asking naturally varies, nobody has to *work* to vary.
2. **F8 waste rate (0.89).** Humans miss, wander, retrieve more than they use; scripts are perfectly efficient. Same caveat and same home: hidden layer, flag-only.
3. **F1 aliveness confirmed (0.84)** — the v0.3 bet was right.
4. **F2's 0.78 is a sim artifact, not a refutation.** The mutation only perturbed numbers, so 5-gram windows still matched most content. The design theorem stands: in production the variant *is* the corpus — a script built on a published base cites passages whose numbers don't exist in the student's variant, and the hook-verbatim check is mechanical. But it fails the pre-registered bar here, so it stays a **variant-design requirement**, to be re-tested with a harsher mutation (and with real Claude runs) before it earns a weight.
5. **F4 spread must go.** This is the experiment's most valuable surprise: our own v0.2 signal *rewards* the script's even citation rhythm and *punishes* the human cluster-where-it-matters pattern. A signal that inverts is worse than a weak one.
6. **F6 continuity changes jobs.** Against executors it's useless (the same AI writes both script and essay — of course they're coherent, acc 0.17). Against **hybrids** (honest research, AI-written essay) it separates by **62 points** (12.3 vs 74.3). Keep the weight; change its story: *the essay must continue the mind that asked the questions.*
7. **F3 trajectory is dead as an authenticity signal** (executor scripts ramp DEEP just fine, 0.70). Demote to an informational bar: it still helps separate lazy from honest.

## Recommended composite v0.4 (pending your review)

- **Weighted score (unchanged philosophy):** traceability .30 · continuity .25 *(now framed as the hybrid signal)* · non-orphan .10 · structure .15 · *(spread and trajectory demoted to informational bars — shown, not weighted)*
- **Flag layer (shown, not scored):** LOW-ALIVENESS (shipped in v0.3) + UNIFORM-FORM (F7) + ZERO-WASTE (F8)
- **Hidden layer (never published, rotating):** F7, F8, F1 — all pass the byproduct principle
- **Variant design requirement:** hook-verbatim verification against the per-student corpus (F2), re-test with harsher mutation

## What was NOT tested (and why)

- **Curiosity-engagement as a signal** — would punish honest students who ignore the librarian's small talk; violates the byproduct principle. The curiosity mechanic stays as an entropy source + interview primer, not a signal.
- **Time-pattern signals** — banned by design decision (low-pressure platform).
- **Real-model runs** — these are sim-vs-sim mechanics tests; your Claude experiment remains the actual evidence step.

## Addendum — F9/F10: the construction-direction hypothesis (shower-thought round)

**Hypothesis (user):** honest writers build start→finish; outsiders build end→start (the finished text exists first, the process is reverse-engineered from it). Same protocol: 10 rounds × 16 sessions, pre-registered 0.80 bar.

| Feature | honest | executor | accuracy | Verdict |
|---|---|---|---|---|
| **F9 phase separation** — do queries and writing interleave on the timeline? | 8.06 alternations | 1.00 | **0.96** | ✅ **STAY** (flag layer) |
| **F10 citation birth** — hooks inserted into a finished, chunk-arrived text | 0.82 | 1.01 | 0.23 | ❌ **REMOVE** |

1. **The direction of construction IS visible in the log — as phasing, not as citation timing.** Executors run a batch job (all questions, then all typing: 1 alternation). Honest writers oscillate between archive and editor (~8 alternations). This is the strongest single signal found so far (0.96), and it's mechanical: queries are already timestamped; the editor needs only a burst-timestamp array.
2. **F10's failure is itself informative:** honest *draft-then-cite* writers insert all citations into finished text exactly like transcribers do — citation timing conflates a very common honest style with cheating. Removed. (The `atLen` instrumentation stays cheap enough to record, shown as informational only.)
3. **F9's honest caveat:** some honest students genuinely batch (research an hour, write in one sitting). The sim assumed oscillation, so 0.96 is optimistic about honest spread. Therefore F9 joins F7/F8 as a **flag, not a weight** — low interleave routes the *interview question* ("walk me through when you researched vs wrote"), never a score penalty.
4. **Against a careful executor** who fakes interleaving during retyping, F9 stops detecting and starts taxing — consistent with the pricing doctrine (every hidden check converts a lazy relay into an expensive live one).
