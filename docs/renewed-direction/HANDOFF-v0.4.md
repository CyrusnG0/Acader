# The Writing Room — Handoff Brief v0.4 (for repo agents)

**Date:** 2026-10-18 · **For:** any coding agent adopting this repo · **Owner:** Cyrus Ng (CS, CUHK)
**Contract:** read this file top to bottom before touching code. Every design decision below was either experimentally tested (lab-verified in this repo) or is a standing owner decision. Do not reverse either category silently.

---

## 1. What this project is

"The Writing Room" is an assessment prototype for the AI era. Thesis: **don't police the output; gate the input and price the outsourcing.** Students research a sealed corpus through a scripted librarian that returns passages, never conclusions. Every essay citation must mechanically point to a passage the student personally retrieved. A process receipt is computed from the session log and prints the interview questions a teacher should ask. A second task family (black-box matrix probing, `matrix-lab-v0.2.html`) proves the receipt format generalizes beyond essays.

Key files:
- `writing-room/writing-room-v0.3.html` — platform (single self-contained HTML; `<script id="core">` block is the scoring engine's source of truth)
- `matrix-lab-v0.2.html` — second task family
- `scripts/score.js` — CLI engine extracted from core (routes by `task` field: `*matrix*` → matrix scoring, else writing-room)
- `scripts/test.js` — 18 assertions, all must stay green (`node scripts/test.js`)
- `scripts/compare.js` / `scripts/similarity.js` — batch report / collusion screening
- `sessions/*.json` — hand-made persona sessions (unit tests of the engine, NOT evidence of real-world validity)
- `claude-prompts/00–07` — simulation, red-team, and classroom-pilot protocols
- `experiments/` — harness.js, f9.js, f11.js, f17.js, f18.js, results JSONs, REPORT.md (the experiment ledger)

## 2. Standing owner decisions (do not violate)

1. **No time pressure, no time tracking.** The platform is low-stakes and not time-sensitive. Never use minutes/seconds as a signal, never add timers (except user-visible countdown mechanics explicitly approved later, e.g. the curveball addendum window if the owner opts in).
2. **Add, don't delete.** Evolve the score by adding signal layers; demote signals to "shown, not scored" rather than removing them. The one agreed deletion (citation spread) is already done and recorded in REPORT.md.
3. **All professor-facing material in English.** Kit README may stay bilingual; product UI is English.
4. **Everything is mock and offline.** Corpus and librarian are scripted. Label it on-page. No server, no LLM calls in the prototype.
5. **Byproduct principle (design law):** any signal may only measure something an honest student produces naturally as a byproduct of doing the task. Signals that require extra performative work from honest students are taxes — reject them.
6. **Flags route interviews; scores never verdict.** The receipt says "PROCESS PROFILE — NOT A VERDICT". Hidden-layer signals stay hidden from the published rubric and rotate.
7. **Report results either way.** Every experiment's outcome — flattering or not — goes into `experiments/REPORT.md`. Never tune thresholds after seeing results (bar is pre-registered at accuracy ≥ 0.80 on 10×16 sim sessions).

## 3. Evidence ledger (what we may claim, and at what level)

| Level | What we can say |
|---|---|
| Mechanical (verified in repo) | Engine 18/18; citations verified against own retrievals; receipts reproducible offline |
| Sim-vs-sim (160 sessions/hypothesis, pre-registered) | 14 hypotheses tested over four rounds; 8 kept, 6 removed/killed (incl. one inverted signal). Accuracy 0.83–0.99 for kept signals |
| Design-complete, not built | Seed variants, curveball gate, claim-first unlocking, triad retrieval, graveyard, closed-book mode |
| Unproven | Real-student separation, Blind Turing Test pilot, construct validity with real populations |

Never claim: "we detect AI writing", "students can't cheat", any accuracy number as if it came from real students. The worst-case executor attack (AI pre-writes essay + full process script; student executes) scores **85** on our receipt vs honest **86** — say this openly; it's the theorem: any log-only verifier can be maximized by a live relay with full rubric knowledge. The product sells: honest work as cheapest path, fake-impact-requires-learning, verification compressed from 20-minute oral to 3-minute targeted interview.

## 4. Experiment results summary (details + raw data in experiments/)

| ID | Signal | honest vs executor (mean) | acc | Status |
|---|---|---|---|---|
| F1 | aliveness (return arcs + re-asks) | 1.26 vs 0.00 | 0.84 | KEEP — flag layer (in v0.3) |
| F2 | hook-variant verbatim (seeded corpus match) | 0.92 vs 0.86 | 0.78 | DESIGN REQUIREMENT, not scored (sim artifact: mutation too weak) |
| F3 | trajectory (DEEP ramp) | 51.7 vs 50.0 | 0.70 | DEMOTED to informational bar |
| F4 | citation spread | 51.5 vs 53.5 | 0.42 | REMOVED — inverted (rewarded scripts) |
| F6 | continuity | 74.3 vs 88.2 (vs executor) | 0.17 | KEEP AS WEIGHT — recategorized: the HYBRID kill-signal (12.3 hybrid, 62-pt gap) |
| F7 | form diversity (non-canonical question forms) | 0.65 vs 0.00 | 0.99 | KEEP — hidden flag layer |
| F8 | waste rate (misses + uncited retrievals) | 0.24 vs 0.00 | 0.89 | KEEP — hidden flag layer |
| F9 | phase separation (interleave asking/writing) | 8.06 vs 1.00 | 0.96 | KEEP — flag layer (needs burst timestamps in log) |
| F10 | citation birth timing | 0.82 vs 1.01 | 0.23 | REMOVED — conflates honest draft-then-cite style |
| H3 | warm-up (bad first question) | — | 0.59 | REMOVED — mechanism didn't express |
| H5 | vocabulary adoption slope | — | 0.20 | REMOVED — metric too crude |
| H7 | perfect record (zero misses = inhuman) | 0.66 vs 0.00 | 0.83 | KEEP — hidden flag layer |
| H11 | attention obsession (topic Gini) | 0.28 vs 0.00 | 0.95 | KEEP — hidden flag layer |
| H14 | re-citation | — | 0.22 | REMOVED — sim artifact |
| H15 | confirmation-bias index (opened complicating / served) | 0.48 vs 0.00 | 0.91 | KEEP — hidden layer (requires Triad mechanic) |
| H17 | note register (scratchpad fragment ratio) | 0.61 vs 0.07 | 0.96 | KEEP — hidden flag layer |
| H16 | zero-pivot flag | 0.52 vs 0.00 | 0.76 | REMOVED as standalone — fold into Graveyard data, interview-route only |
| F17 | class-level guide fingerprints (pairwise off-corpus 3-grams) | 0.251 vs 0.052 | 0.75 | KEEP as class-level SCREEN in similarity.js only (16% honest FP; interview resolves leads) |

Flag layer today: F1, F7, F8, F9, H7, H11 (+H15, H17 once their mechanics exist). Weight layer today: traceability .30, continuity .25, non-orphan .10, structure .15 (+trajectory .10 and spread .10 to be demoted per §5).

## 5. v0.4 work plan — build these, in this order

Owner rulings for v0.4: **replace the coherence framing (rename + reframe, keep the weighted score); add the Triad mechanic; no time pressure anywhere.**

### 5.1 Rename & reframe (do first, trivial)
- In both HTML files and score.js output, rebrand "coherence profile" → **"Research Telemetry"** with subtitle "process profile — an X-ray of trade-offs, not a verdict". Keep all existing weights and the numeric composite (owner: add, don't delete — the number stays, the story changes).
- Demote **trajectory** and **spread** from weighted components to "shown, not scored" informational bars on the receipt (weights redistributed: traceability .35, continuity .30, non-orphan .15, structure .20 — verify all 18 tests still pass, adjust thresholds in test.js ONLY if a test's intent is preserved; document any change in REPORT.md).

### 5.2 Log additions (schema v0.4 — additive fields only)
```
s.burstTs      : number[]  // editor sitting timestamps (sequence positions, NOT wall-clock) — enables F9
s.queryForms   : string[]  // parallel to queries: "wh"|"casual"|"frag"|"uniform" — enables F7 (auto-derived if absent)
s.servedTriads : [{ts, confirming:pid, complicating:pid, adjacent:pid, opened:[pids], tensionNote?:string}] — enables H15 + Graveyard
s.bets         : [{ts, claim, staked:"core"|"support"|"hedge", revisedTo?:string, atEvent?:pid}] — enables Citation Staking + hypothesis-pivot log
s.curveball?   : {docId, addendum, citedPassages:[pids]} — enables the submit-gate stress-test
```
Backwards compatible: engine must score v0.1–v0.3 sessions unchanged (missing fields = signal silently inert, no penalty, no flag).

### 5.3 New flag computations (flag layer only — never weighted, never shown in published rubric)
- F9 interleave: merge query ts and burstTs as sequence events, count alternations; flag when events ≥ 8 and alternations ≤ 2 ("BATCH-SHAPED: research and writing never interleaved — ask when you researched vs wrote").
- F7 uniform-form: flag when ≥ 6 queries and canonical-form ratio = 1.0.
- F8 zero-waste: flag when ≥ 6 retrievals and zero misses and every retrieval cited.
- H7 already covered by F8's miss clause; H11: Gini of retrievals-per-topic ≥ 0.55 → "EVEN-ATTENTION" flag.
- H15 zero-friction: flag when servedTriads ≥ 2 and every complicating source unopened ("COUNTER-SOURCES IGNORED — interview asks how the thesis survives Lee-type critique").
- H17 polish mismatch: scratchpad exists, > 90% of sentences > 80 chars, and ≤ 1 fragment → "POLISHED-NOTES" flag.

### 5.4 Platform features (in priority order)
1. **Triad librarian responses** (mock): when a DEEP query returns a passage, the librarian also serves 2 side-along options — one complicating (pick from a contradicting document: D6↔D11 tension, D4 self-contradiction, D10 strike-from-public-vs-D1), one adjacent. Student may open or ignore; log to `servedTriads`. This is the fresh-bit generator AND the H15 data source. Zero server calls: precompute the triad table from CORPUS by hand in the build script.
2. **Graveyard section on receipt**: passages retrieved, never cited, plus complicating sources served and ignored — each with a generated interview question ("You pulled D5's margins concession and never used it — why?").
3. **Claim-first unlocking (mock)**: first DEEP query requires a one-sentence bet before the passage unlocks; stored in `bets`; receipt shows "hypothesis at start vs claim at end" delta. No scoring; interview route only.
4. **Curveball gate (optional toggle, default OFF for pilot)**: after submit, unlock D13 (new contradcting doc — write it: a January 2026 judicial-review ruling on band schemes, citing D9's compensation risk), ask for a 150-word addendum: does the thesis survive? Store as `s.curveball`. Receipt appends "stress-test" section. **No countdown timer shown** (owner decision §2.1) — the constraint is the new document, not the clock.
5. **Closed-book mode (optional toggle)**: hides archive+log for the final 300-word core-argument reconstruction; log the fact it was used (voluntary), never the content.
6. **similarity.js upgrade**: add class-level screen mode using F17 (off-corpus 3-gram pairwise ranking); output "leads" ranked, never verdicts.

### 5.5 Pilot protocol (write `claude-prompts/08-blind-turing.md`)
15 students (or Claude sims as dry-run) × 3 arms: A honest / B reverse-engineered (essay first, then fake process) / C live relay (external LLM decides every move). Instructors blinded; judge each case twice: (1) receipts alone, (2) receipts + 3 generated interview questions (or the 90-second async voice check if built). Report both accuracies either way. This protocol merges our A5 RELAY red-team with Gemini's Blind Turing Test proposal and replaces all hand-waved detection-rate claims.

## 6. Regression invariants (all must hold after every change)

1. `node scripts/test.js` — all existing assertions pass.
2. Honest-minimal ≥ executor on composite (the anti-tax invariant).
3. Jumpy-honest ≥ executor on composite (anti-tax for non-linear thinkers).
4. Honest sessions raise NO hidden-layer flags; executor raises LOW-ALIVENESS (already in v0.3).
5. v0.1–v0.3 session files score identically before/after engine changes (additive-only guarantee).
6. Hybrid continuity gap vs honest ≥ 50 pts in sim.
7. No signal may use wall-clock time (grep the engine for Date.now in scoring paths — burstTs are sequence ranks, exported as ranks).

## 7. Out of scope / rejected ideas (do not resurrect without new evidence)

Time-pattern tracking (owner ban) · honeypot documents (punishes honest citation of weak sources) · hidden scoring published as detection guarantees (theorem forbids) · "kill the coherence score" (overreach — continuity is the hybrid killer) · F10 citation-birth timing (conflates honest drafting styles) · performative-pivot demands (H16 failed: ~half of honest students never pivot).

## 8. Definition of done for v0.4

All §6 invariants green · new flags firing on constructed attack sessions (add `wr-batch` and `wr-zero-friction` personas mirroring harness.js generators) · REPORT.md addendum 5 records what was built, what fired, what didn't · both HTML files still render (screenshot check) · kit zip rebuilt.
