# Eng review v2: the live map (D-035) and the workspace (D-036)

/plan-eng-review, 2026-10-24. **Target (fixed): the branch diff on `main`** (uncommitted v1 docs at `b4f4bc7`). The 2026-10-23 eng review (D-034, `docs/designs/eng-review-v1.md`) already reviewed and approved everything in this diff except the D-035 and D-036 additions. Those approvals are reused unchanged. This review covers the new parts only:
- D-035: the mapper. PRODUCT.md §5, DECISIONS D-035, GLOSSARY.
- D-036: design/workspace.md (new), plus the design-review edits to receipt.md, coach-helper.md, provenance.md, privacy.md, event-log.md and build-plan.md.

Design doc used as context: docs/designs/design-review-v1.md.

## Scope Challenge

### A. Assessment

- **What already exists:**
  - the jobs loop (D23)
  - `complete()` with a closed task enum (architecture.md:74)
  - claim marks with `by: student` (event-log.md:91-94)
  - the 5-minute merged `editor.batch` (event-log.md:108)
  - L1 provenance in engine/ (architecture.md:38)
  - stored AI outputs (D31)
  - the seal whitelist (event-log.md:118)

  The mapper can reuse all of these. Nothing new is needed besides one task, two event types and one job kind.
- **Complexity:** the diff touches more than 8 doc files. It proposes two new services:
  - the mapper job (server/coach or engine)
  - a provisional-trail endpoint ("Show my trail", 7A)

  The complexity gate trips.
- **TODOS cross-reference:** TODOS #7 (graph view) stays deferred (1A). Nothing in TODOS blocks the mapper.

### Reality rows

- REALITY: premise-table finding unverified=2. Two premises have no receipt: "a small model" is never named or costed in the plan (PRODUCT.md:67), and nothing measures mapper precision. Also, `claim.link` (workspace.md §2) does not exist in the event types (event-log.md:59). Receipt: design/workspace.md:38.
- REALITY: already-done pass. No origin remote commits since b4f4bc7, and the mapper is not built anywhere (prototype/ is empty). Receipt: design/architecture.md:81.
- REALITY: surface-check finding. The `complete()` task enum has no mapper task (architecture.md:74). The `claim.link` event is not in the event table (event-log.md:59). Receipt: design/architecture.md:74.
- REALITY: binding-decisions pass. D-034 (SQLite, DB job queue, no embeddings, D31 stored outputs) and D-035/D-036 are honoured. No overruled default is reintroduced. Receipt: docs/DECISIONS.md:201.
- REALITY: numbers finding. "< 30 LLM calls per submission" (architecture.md:100) is [estimated] and was set before the mapper existed. One mapper call per 5-minute batch over a 2-hour session is about 24 calls, which nearly uses up that budget alone. Receipt: design/architecture.md:100.
- REALITY: deferred-asks pass. There is no linked issue. OL-044 remains the tracker. Receipt: docs/OPEN_LOOPS.md:11.
- REALITY: pr-count pass. There is no .gstack/ship-policy.json, so the default is one PR per wave. This review changes docs only. Receipt: design/build-plan.md:38.

### B. Scope record (post-answer)

feature answers: D1 = A (new milestone M4m after M4: mapper job, map-suggestions UI, eval on the golden set; behind flag `mapper_enabled`; pilot gate does not require it); structure: A = Original arrangement (D2): new package `server/mapper/` (job runner, prompts, store; ~4 files, 1 new service) + `server/trail/` service for provisional bands (~2 files, 1 new service); accepted scope: D-035 mapper and D-036 workspace as designed, sequenced as M4m behind a flag, in the original two-service arrangement; pending remedies: C1–C6 (events, privacy/consent, call budget, post-seal race, eval, build plan) plus the trail-vs-engine band risk raised by D2's con.

### C. Findings

1. [P1] (9/10) design/workspace.md:38 — `claim.link by: student, via: map` names a nonexistent event; mapper suggestions have no event type (event-log.md:59, 80, 91-94). Reviewer: Claude. → R1
2. [P1] (8/10) design/privacy.md:12, 28 — mapper sends draft text to the provider every 5 min; consent does not name it; minimum payload undefined. → R2
3. [P2] (8/10) design/architecture.md:62, 100 — ~24 mapper calls per 2 h session vs the < 30 budget; competes with compile jobs at the deadline burst. → R3
4. [P1] (9/10) design/event-log.md:118 — a mapper result can arrive after the seal. → R4
5. [P1] (8/10) design/evaluation.md:19 — no mapper eval, yet D1 gates the flag on it. → R5
6. [P2] (9/10) design/build-plan.md:44-46 — M4m and D-036 work uncosted. Carried by D1 + D-036 approvals; no question (mechanics of approved scope).

## Decision ledger

### R1: How map suggestions and their answers are recorded
Finding: 1, P1, 9/10, design/workspace.md:38, Claude
Plan baseline: workspace.md §2 (5A, D-036): `map.suggestion` (compile artifact, D31), Yes → `claim.link` by: student, via: map; Not this → `map.suggestion_rejected`; 17A: unasked findings may feed receipt questions.
Runtime evidence: none (prototype/ empty). Event table (event-log.md:46-76) has no map.* or claim.link type; claim links are `claim` marks `{claim_id, by}` in editor steps (event-log.md:80).
Comparison grid:
| Choice | Current | A | B |
|---|---|---|---|
| R1 suggestion record | `map.suggestion` named, no schema | chained event `map.suggestion {suggestion_id, span, claim_id, artifact_id, output_hash}` | server table only, not in the chain |
| R1 answer record | `claim.link` / `map.suggestion_rejected` (undefined) | chained event `map.answer {suggestion_id, answer: yes\|no}`; Yes also applies claim mark `{claim_id, by: student}` via a normal editor step | Yes applies claim mark only; No stored in server table |
| 17A findings → receipt questions | allowed | kept (findings cited by event + artifact id, verify covers them) | dropped (unsealed data can't feed the receipt) |
| R4 post-seal race | pending | pending | pending |
| claim.by values | student, coach, import | unchanged (no schema bump) | unchanged |
Question D3:
D3 — How are map suggestions and the student's answers recorded? <gstack-qid:plan-eng-review-mapper-events>
Project/branch/task: main, eng review of D-035/D-036; mapper approved as flagged M4m (D1), own package (D2).
ELI10: The design says a suggestion and the student's Yes or No get recorded, but names events that don't exist. In our system, anything the receipt relies on must sit in the sealed log so it can be checked later. A student's link is already recorded as a mark inside their edits. The question is whether suggestions and answers go into the sealed log too, or into a side table.
Stakes if we pick wrong: either receipt questions cite mapper findings nobody can verify, or we bloat the sealed log for data the teacher never sees.
Recommendation: A, because 17A lets mapper findings feed the receipt's questions, and D31 requires anything AI-derived on the receipt to be stored and checkable.
Completeness: A=9/10, B=6/10
Pros / cons:
A) Two chained events: `map.suggestion` (suggestion_id, span, claim_id, artifact_id, output_hash) and `map.answer` (suggestion_id, yes|no). Yes also applies the normal claim mark by: student through an editor step. No new claim.by value, no schema bump (recommended) (human: ~1 day / CC: ~20 min)
  ✅ verify() covers suggestions, so receipt questions built from them stay citable and byte-identical on rebuild (D31).
  ✅ A confirmed link is just a student link, so bands stay exactly as 4A/5A say: never traced.
  ❌ Adds up to ~24 small events per session to the chain. Rejections are in the student's log (never on the receipt).
B) Keep suggestions and No answers in a server table outside the chain; Yes applies only the claim mark
  ✅ Smaller sealed log and no new event types.
  ❌ Mapper findings can't feed receipt questions verifiably, so 17A's 'may feed' has to be dropped.
Net: a checkable record that keeps 17A, versus a lighter log that gives it up.
Header: D3 Events
Options:
A) Chained events (recommended)
`map.suggestion` + `map.answer` in the chain; Yes also applies claim mark by: student via an editor step; no claim.by change; 17A kept. (human ~1 day / CC ~20 min)
B) Side table only
Suggestions and No answers in a server table; Yes = claim mark only; 17A's 'findings feed receipt questions' dropped.

State: approved
Actual answer: A) Chained events (recommended), D3, 2026-10-24
Accepted scope: Add chained events `map.suggestion {suggestion_id, span, claim_id, artifact_id, output_hash}` and `map.answer {suggestion_id, answer: yes|no}` to event-log.md; a Yes also applies the claim mark {claim_id, by: student} through a normal editor step; claim.by unchanged (no schema bump); 17A kept; workspace.md §2 record column corrected.
History: none

### R4: A mapper result that arrives after the seal
Finding: 4, P1, 9/10, design/event-log.md:118, Claude
Plan baseline: post-seal whitelist = receipt.issued, note.add, link.add, record.withdrawn, resubmit.open (event-log.md:118); 5A: unanswered suggestions expire silently at submit; D3 (approved): `map.suggestion` is a chained event.
Runtime evidence: none (not built). The whitelist rejects any other post-seal append with 409 (event-log.md:118).
Comparison grid:
| Choice | Current | A | B |
|---|---|---|---|
| R4 late mapper result | unspecified | at submit, queued mapper jobs for that log are cancelled; a result finishing after the seal is discarded (never appended), counted on the operator page | add `map.suggestion` to the post-seal whitelist, marked post-seal, ignored by compile |
| Post-seal whitelist | 5 types | unchanged | +1 type |
| R1 events | approved D3 | unchanged | unchanged |
| R2, R3, R5 | pending | pending | pending |
Question D4:
D4 — What happens to a map suggestion that finishes after the student submits? <gstack-qid:plan-eng-review-mapper-post-seal>
Project/branch/task: main, eng review of D-035/D-036; suggestions are sealed-log events (D3).
ELI10: The mapper works on 5-minute batches in the background. If a student submits while the last batch is still being processed, the result arrives after the record is sealed. The sealed record only accepts a short list of later additions (notes, links, the receipt). Either we throw the late result away, or we widen that list.
Stakes if we pick wrong: either submit races produce 409 errors and alerts, or model output gets attached to a sealed record after the fact.
Recommendation: A, because 5A already says suggestions expire at submit, so a late one has no use, and the seal's whitelist stays as tight as D8 made it.
Completeness: A=9/10, B=6/10
Pros / cons:
A) Cancel queued mapper jobs for the log at submit; discard any result that finishes after the seal (never appended), and count it on the operator page (recommended) (human: ~2 h / CC: ~10 min)
  ✅ The sealed record stays exactly what the student submitted; the whitelist doesn't grow.
  ✅ Matches 5A: suggestions expire at submit, so nothing is lost.
  ❌ Mapper work for the final batch is wasted when it races the submit.
B) Whitelist `map.suggestion` after the seal, marked post-seal and ignored by compile
  ✅ Every mapper result is kept, even late ones.
  ❌ Puts model output after the seal for no user benefit, and widens a whitelist D8 kept minimal.
Net: a tight seal with a little wasted work, versus keeping useless late results.
Header: D4 Late result
Options:
A) Cancel and discard (recommended)
Cancel queued mapper jobs at submit; drop results finishing after the seal; operator counter. Whitelist unchanged. (human ~2 h / CC ~10 min)
B) Whitelist after seal
Allow post-seal `map.suggestion`, marked post-seal, ignored by compile.

State: approved
Actual answer: A) Cancel and discard (recommended), D4, 2026-10-24
Accepted scope: At submit, cancel queued mapper jobs for that log; a mapper result finishing after the seal is discarded, never appended, and counted on the operator page. Post-seal whitelist unchanged. Written into event-log.md §6.
History: none

### R2: What the mapper sends to the LLM, and what consent says
Finding: 2, P1, 8/10, design/privacy.md:12, 28, 57, Claude
Plan baseline: privacy principle 4 "Minimum to the LLM. Each call gets only the blocks, cards and spans it needs" (privacy.md:12); consent AI line "Parts of your writing and readings are sent to [provider, location] to generate questions" (privacy.md:57); D-035: mapper runs a small model on each 5-minute batch.
Runtime evidence: none (not built). Consent text is a draft (OL-016).
Comparison grid:
| Choice | Current | A | B |
|---|---|---|---|
| R2 mapper payload | undefined | only the paragraphs changed in this batch + the student's claim texts (ids + words) + titles of anchored blocks; no names, no full draft, no log | undefined (implementer decides) |
| R2 consent AI line | "to generate questions" | adds: "While you write, changed paragraphs are also sent every few minutes to suggest links on your map. Suggestions never change what counts as traced; they can shape the questions your teacher may ask." | unchanged |
| Flag off (D1) | — | nothing sent while writing | — |
| R3, R5 | pending | pending | pending |
Question D5:
D5 — What does the mapper send to the AI provider, and does consent say so? <gstack-qid:plan-eng-review-mapper-privacy>
Project/branch/task: main, eng review of D-035/D-036; mapper flagged M4m (D1), chained events (D3).
ELI10: Until now, student writing went to the AI provider mainly at submit, to make questions. The mapper sends writing every few minutes while the student is still drafting. The consent text doesn't mention that, and nothing limits what the mapper sends. A school's approval and the student's consent cover only what the text says.
Stakes if we pick wrong: the pilot sends draft text the student never agreed to share, which can end the pilot with the school and breaks law 7.
Recommendation: A, because consent has to name every purpose, and the mapper needs only the changed paragraphs and the claim list, not the whole draft.
Completeness: A=9/10, B=3/10
Pros / cons:
A) Minimum payload: only paragraphs changed in this batch + the student's claim texts + titles of anchored blocks; no names, full draft or log. Consent adds one line: 'While you write, changed paragraphs are also sent every few minutes to suggest links on your map. Suggestions never change what counts as traced; they can shape the questions your teacher may ask.' Flag off = nothing sent while writing (recommended) (human: ~2 h / CC: ~10 min)
  ✅ The school's approval and the student's consent cover exactly what is sent.
  ✅ Smaller prompts are cheaper and leak less if the provider is ever breached.
  ❌ The mapper sees less context, so some links across distant paragraphs will be missed.
B) Leave the payload to the implementer and the consent text as is
  ✅ No change now; the implementer can send whatever gives the best links.
  ❌ Sends draft text under a consent line that only mentions 'to generate questions' at submit.
Net: a defined, consented minimum versus an unbounded payload the student never agreed to.
Header: D5 Privacy
Options:
A) Minimum + consent line (recommended)
Changed paragraphs + claim texts + anchored block titles only; consent names live map suggestions; flag off = nothing sent. (human ~2 h / CC ~10 min)
B) Leave as is
Payload undefined; consent text unchanged.

State: approved
Actual answer: A) Minimum + consent line (recommended), D5, 2026-10-24
Accepted scope: Mapper payload = only paragraphs changed in this batch + the student's claim texts (ids + words) + titles of anchored blocks; no names, full draft or log. Consent adds: 'While you write, changed paragraphs are also sent every few minutes to suggest links on your map. Suggestions never change what counts as traced; they can shape the questions your teacher may ask.' Flag off = nothing sent while writing. Written into privacy.md §1 and §4.
History: none

### R3: Mapper call budget and queue priority
Finding: 3, P2, 8/10, design/architecture.md:62, 99-100, Claude
Plan baseline: jobs loop, 4 concurrent LLM calls per backend, round-robin by submission (architecture.md:62); "LLM calls per submission < 30 [ASSUMPTION]" (architecture.md:100); "L1 receipt < 60 s; questions < 15 min under 30 submits in 5 minutes" (architecture.md:99); D-035: one mapper run per 5-minute batch.
Runtime evidence: none (not built). Estimate: 2 h session = 24 batches = up to 24 mapper calls [estimated].
Comparison grid:
| Choice | Current | A | B |
|---|---|---|---|
| R3 mapper priority | none (same queue) | lowest; compile and Coach jobs always go first | same as other jobs |
| R3 skip rule | none | skip a batch with < 30 changed words; at most one queued mapper job per log (newer batch replaces the queued one) | none |
| R3 budget | < 30 per submission (all calls) | compile/Coach budget unchanged (< 30); separate mapper cap 40 per submission, then the map stops suggesting; both counted on the operator page | one shared < 30 |
| R2, R4 | approved D5, D4 | unchanged | unchanged |
| R5, R6 | pending | pending | pending |
Question D6:
D6 — How do mapper calls share the AI budget and queue with the receipt? <gstack-qid:plan-eng-review-mapper-budget-queue>
Project/branch/task: main, eng review of D-035/D-036; mapper flagged M4m (D1), events (D3), payload (D5).
ELI10: The mapper could call the AI every 5 minutes for every student. In a 2-hour session that's about 24 calls, close to the whole per-submission budget we set before the mapper existed. At the deadline, 30 students submitting means receipts need the same 4 AI slots per provider that live mappers are using. If they share a queue equally, receipts get slower right when teachers are waiting for them.
Stakes if we pick wrong: receipts miss their 60-second target at the deadline, or the AI bill doubles without anyone noticing.
Recommendation: A, because the receipt is the pilot's proof and must never wait behind a suggestion; small edits don't need a new suggestion.
Completeness: A=9/10, B=4/10
Pros / cons:
A) Mapper jobs at lowest priority; skip batches with < 30 changed words; at most one queued mapper job per log (newest batch replaces it); separate mapper cap of 40 calls per submission (then suggestions stop); the < 30 budget for compile and Coach stays; both counters on the operator page (recommended) (human: ~4 h / CC: ~15 min)
  ✅ Receipts and Coach questions are never delayed by the mapper, even at the deadline burst.
  ✅ Costs are bounded and visible per submission.
  ❌ During a busy deadline, students still writing may get no suggestions until the queue clears.
B) Same queue and budget as everything else
  ✅ Simplest; nothing new to build.
  ❌ Mapper calls compete with receipts at the deadline and can eat the whole per-submission budget.
Net: guaranteed receipt latency and bounded cost, versus simplicity.
Header: D6 Budget
Options:
A) Lowest priority + caps (recommended)
Lowest priority; skip <30 changed words; one queued job per log; mapper cap 40/submission; compile/Coach <30 unchanged; operator counters. (human ~4 h / CC ~15 min)
B) Shared queue
Same queue, priority and budget as all other jobs.

State: approved
Actual answer: A) Lowest priority + caps (recommended), D6, 2026-10-24
Accepted scope: Mapper jobs run at lowest priority (compile and Coach first); skip batches with < 30 changed words; at most one queued mapper job per log (newest replaces it); separate mapper cap 40 calls per submission, then suggestions stop; compile/Coach budget < 30 unchanged; both counted on the operator page. Written into architecture.md §4 (Jobs) and §7.
History: none

### R5: The mapper eval that gates `mapper_enabled`
Finding: 5, P1, 8/10, design/evaluation.md:19, Claude
Plan baseline: D1 (approved): flag on for the pilot "if its eval passes"; D-035 golden set: real sources + an open textbook, 15–20 hand-scripted sessions + a generator to ~100, labelled simulated; evaluation.md §2 golden sessions (YAML: actions + expected bands, moments, question targets).
Runtime evidence: none. evaluation.md has no mapper eval and no link labels.
Comparison grid:
| Choice | Current | A | B |
|---|---|---|---|
| R5 labels | none | each of the 15–20 hand sessions labels, per batch, the correct sentence→claim links (YAML field `expected_links`) | none |
| R5 pass bar | none | precision ≥ 0.80 of shown suggestions; ≤ 1 suggestion per 5-min batch on average; on both backends; plus 3 human sessions (H) where the student rejects < 1 in 3 | judged by feel in the human sessions (H) |
| R5 regression | none | runs in CI as a stub-replayed eval and live on prompt or model change [→EVAL] | none |
| D1 flag rule | on if eval passes | flag on only when A's bar passes | flag on by founder judgment |
| R6 | pending | pending | pending |
Question D7:
D7 — What eval decides whether the mapper is switched on for the pilot? <gstack-qid:plan-eng-review-mapper-eval>
Project/branch/task: main, eng review of D-035/D-036; mapper flagged M4m, on only if its eval passes (D1).
ELI10: D1 says the mapper goes live only if its eval passes, but no eval exists. A mapper that suggests wrong links makes students click 'Not this' over and over and stop trusting the map. We need labelled answers (which sentence really argues which claim) and a pass mark, measured before any student sees it.
Stakes if we pick wrong: either a noisy mapper reaches the first class, or a good one stays off because nobody can say it passed.
Recommendation: A, because the golden sessions D-035 already plans are the natural place to label links, and a number is the only fair way to flip a flag.
Completeness: A=9/10, B=4/10
Pros / cons:
A) Label correct sentence-to-claim links per batch in the 15–20 hand golden sessions (`expected_links`). Pass = precision >= 0.80 of shown suggestions, <= 1 suggestion per 5-minute batch on average, on both backends, plus 3 human sessions where students reject fewer than 1 in 3. Runs in CI (stub replay) and live on any prompt or model change (recommended) (human: ~2 days / CC: ~1 h)
  ✅ A clear, repeatable bar for flipping the flag, measured before students see anything.
  ✅ Becomes the regression eval for every later prompt or model change.
  ❌ Hand-labelling links in 15–20 sessions takes real time and judgment.
B) Judge it by feel during the human sessions (H)
  ✅ No labelling work; fast.
  ❌ No number to defend the decision, and no regression check when prompts change.
Net: a measured gate and a lasting regression eval, versus a gut call.
Header: D7 Eval
Options:
A) Labelled golden eval (recommended)
`expected_links` in hand sessions; precision >= 0.80, <= 1 per batch, both backends, + 3 human sessions rejecting < 1 in 3; CI + live on change. (human ~2 days / CC ~1 h)
B) Judge by feel
Decide in the human sessions without labels or a pass bar.

State: approved
Actual answer: A) Labelled golden eval (recommended), D7, 2026-10-24
Accepted scope: Hand golden sessions (15–20) label correct sentence→claim links per batch (YAML `expected_links`). Pass bar: precision >= 0.80 of shown suggestions; <= 1 suggestion per 5-min batch on average; both backends; plus 3 human sessions (H) where students reject < 1 in 3. Runs in CI (stub replay) and live on any prompt/model change. mapper_enabled turns on only when the bar passes. Written into evaluation.md.
History: none

### C. Dispositions and result

- 1 (R1): accepted, D3 = A.
- 2 (R2): accepted, D5 = A.
- 3 (R3): accepted, D6 = A.
- 4 (R4): accepted, D4 = A.
- 5 (R5): accepted, D7 = A.
- 6: applied as mechanics of D1 + D-036 (M4m row; workspace work costed at ~3–4 days [estimated]; total ≈ 35–36 build days). Also added the `map_suggest` task and the mapper/ and trail/ packages to architecture.md (required by D2, D3). Model choice stays with the D7 eval; "small model" remains an unverified premise.
- Scope Challenge result: scope accepted as-is (sequenced into M4m behind a flag; D2 kept the original arrangement).

## Section 1: Architecture

Findings:
- A1 [P1] (8/10) design/architecture.md:89-90 (trail/ added per D2) — no rule that trail/ uses engine.provenance's band function; a second calculation can drift from the receipt. → R7
- A2 [P2] (8/10) design/receipt.md §2a — "Mark as discussed" (3A) has no storage; the student's sealed log can't take it (event-log.md:120). → R8
- A3 [P1] (8/10) design/receipt.md §7 (9A) — withdrawal between submit and release must stop queued compile/release jobs. → R9
- Carried without a question: GET /trail and the map endpoints join the route-enumeration test (D9); mapper provider failure = map stops, operator alert (5A, D15).

### R7: How the trail service computes bands
Finding: A1, P1, 8/10, design/architecture.md:89-90, Claude
Plan baseline: D2 = A, `server/trail/` is its own service; 7A: "Show my trail" paints the same bands the receipt will use, labelled provisional; engine/ is a pure library (architecture.md:38).
Runtime evidence: none (not built).
Comparison grid:
| Choice | Current | A | B |
|---|---|---|---|
| R7 band computation | unspecified | trail/ imports engine.provenance and runs replay + mark check + L1 on the current staged doc (no L3, no LLM); no band logic in trail/ | trail/ computes its own approximate bands (e.g. from marks only, skipping the mark check) |
| R7 parity test | none | one test: for every golden session, trail at the submit doc_rev == the L1 receipt's bands (receipt v1, before any L3b) | none |
| D2 package layout | trail/ own package | unchanged | unchanged |
| R8, R9 | pending | pending | pending |
Question D8:
D8 — How does the 'Show my trail' service work out the bands? <gstack-qid:plan-eng-review-trail-bands>
Project/branch/task: main, eng review of D-035/D-036; trail/ is its own package (D2).
ELI10: 'Show my trail' promises the student the same colouring the receipt will use. If the trail service has its own way of working out bands, it will slowly disagree with the receipt, and a student who saw 'traced' while writing sees 'untraced' after submitting. The safest design: the trail service has no band logic, it just calls the engine.
Stakes if we pick wrong: students are told one thing while writing and another on the receipt, which feels like a trap.
Recommendation: A, because one band function means the trail and the receipt can't disagree, and a parity test on every golden session proves it.
Completeness: A=9/10, B=4/10
Pros / cons:
A) trail/ calls engine.provenance (replay + mark check + L1) on the current staged document, with no L3 and no AI calls, and holds no band logic itself. One parity test: for every golden session, the trail at the submitted revision equals the L1 receipt's bands (before any L3b) (recommended) (human: ~4 h / CC: ~15 min)
  ✅ The trail and the receipt use one band function, so they can't drift.
  ✅ The parity test catches any future change that breaks the promise.
  ❌ Replay plus mark check on every toggle costs more server time than a quick approximation.
B) trail/ computes its own approximate bands from the marks alone
  ✅ Faster responses, no replay on each request.
  ❌ Skips the mark check, so forged or failed marks show as traced in the trail but not on the receipt.
Net: one source of truth with a little server cost, versus a fast approximation that can mislead.
Header: D8 Trail
Options:
A) Call the engine (recommended)
trail/ runs engine.provenance (replay + mark check + L1, no L3/AI) on the staged doc; no band logic in trail/; golden parity test vs the L1 receipt. (human ~4 h / CC ~15 min)
B) Own approximation
trail/ computes bands from marks alone, without the mark check.

State: approved
Actual answer: A) Call the engine (recommended), D8, 2026-10-24
Accepted scope: trail/ calls engine.provenance (replay + mark check + L1, no L3, no AI) on the current staged doc and holds no band logic; parity test: for every golden session, trail at the submit doc_rev == the L1 receipt's bands (before any L3b). Written into workspace.md §4 and architecture.md §6.
History: none

### R8: Where "Mark as discussed" is stored
Finding: A2, P2, 8/10, design/receipt.md §2a, Claude
Plan baseline: 3A: status column incl. `discussed`; "Mark as discussed" at the foot of each receipt sets it. D9: teacher opens/exports are logged in an audit table, not in the student's log (event-log.md:132). Post-seal whitelist (event-log.md:120) has no teacher status event.
Runtime evidence: none (not built).
Comparison grid:
| Choice | Current | A | B |
|---|---|---|---|
| R8 storage | unspecified | teacher-side table `receipt_status (receipt_id, teacher_id, discussed_at)` + an audit row; never in the student's log | new post-seal event `teacher.discussed` in the student's chain |
| R8 student visibility | unspecified | not shown to the student | visible in the student's export |
| Post-seal whitelist | 5 types | unchanged | +1 type |
| R9 | pending | pending | pending |
Question D9:
D9 — Where is the teacher's 'Mark as discussed' stored? <gstack-qid:plan-eng-review-discussed-storage>
Project/branch/task: main, eng review of D-035/D-036; 3A added a 'discussed' status to the teacher's list.
ELI10: When the teacher has talked with the student, they tick 'discussed'. That tick is the teacher's note, not part of the student's writing record. Our rule (D9) keeps teacher actions in the teacher's own audit table, and the sealed student record accepts only a short list of later additions.
Stakes if we pick wrong: teacher actions leak into the student's sealed record, or the status has no home and gets improvised.
Recommendation: A, because the tick is teacher data, and D9 already puts teacher actions in the audit table, outside the student's chain.
Completeness: A=9/10, B=6/10
Pros / cons:
A) Teacher-side table receipt_status (receipt_id, teacher_id, discussed_at) plus an audit row; never in the student's log; not shown to the student (recommended) (human: ~1 h / CC: ~5 min)
  ✅ Keeps the student's sealed record exactly what the student did, and the whitelist stays at five types.
  ✅ Fits D9's pattern of teacher actions in the audit table.
  ❌ The student can't see that their teacher marked the conversation as done.
B) New post-seal event teacher.discussed in the student's chain, visible in their export
  ✅ The student's export shows when the conversation was marked done.
  ❌ Puts a teacher action in the student's record and widens the seal's whitelist.
Net: clean separation of teacher and student data, versus student visibility of the tick.
Header: D9 Discussed
Options:
A) Teacher table (recommended)
receipt_status (receipt_id, teacher_id, discussed_at) + audit row; not in the student's log; not shown to the student. (human ~1 h / CC ~5 min)
B) Event in student chain
Post-seal teacher.discussed event, whitelisted, visible in the student's export.

State: approved
Actual answer: A) Teacher table (recommended), D9, 2026-10-24
Accepted scope: Teacher-side table receipt_status (receipt_id, teacher_id, discussed_at) plus an audit row; never in the student's log; not shown to the student; post-seal whitelist unchanged. Written into receipt.md §2a.
History: none

### R9: Jobs in flight when a student withdraws before release
Finding: A3, P1, 8/10, design/receipt.md §7 (9A), Claude
Plan baseline: 9A: withdrawal between submit and release is allowed; teacher list shows `record removed` and a neutral notice, no seal, bars or questions. privacy.md §5 Delete: after submission → `record.withdrawn`. Release rule and +48 h cap (architecture.md:52).
Runtime evidence: none (not built). Compile, L3 and release run as DB jobs (D23).
Comparison grid:
| Choice | Current | A | B |
|---|---|---|---|
| R9 queued jobs | unspecified | `record.withdrawn` cancels queued compile, L3, question and release jobs for that log in the same transaction; a job already running checks the withdrawn flag before writing and stops | jobs run to completion; the release step checks the flag |
| R9 unreleased receipt | unspecified | any compiled-but-unreleased receipt is never released and is deleted with the log's stored outputs | compiled receipt kept, hidden from the teacher |
| R9 tombstone | unspecified | teacher-side row (log_id, withdrawn_at) drives the `record removed` status | same |
| Release after withdraw | possible | impossible (integration test with a frozen clock) | prevented only at release |
Question D10:
D10 — What happens to receipt jobs already in the queue when a student withdraws? <gstack-qid:plan-eng-review-withdraw-jobs>
Project/branch/task: main, eng review of D-035/D-036; 9A allows withdrawal between submit and release.
ELI10: After submitting, the system starts building the receipt and the questions in the background, then releases it to the teacher later. If the student withdraws in between, those jobs are still queued. If nothing stops them, a receipt the student removed could still be built, and in the worst case released.
Stakes if we pick wrong: a withdrawn record reaches the teacher anyway, which breaks the student's right to remove it (law 7) and the 9A promise.
Recommendation: A, because cancelling in the same step as the withdrawal, plus a check inside running jobs, makes a release after withdrawal impossible, not just unlikely.
Completeness: A=9/10, B=6/10
Pros / cons:
A) record.withdrawn cancels queued compile, L3, question and release jobs for that log in the same transaction; a running job checks the withdrawn flag before writing and stops; any compiled-but-unreleased receipt is deleted with the stored outputs; a teacher-side tombstone (log_id, withdrawn_at) shows 'record removed'. Integration test with a frozen clock (recommended) (human: ~4 h / CC: ~15 min)
  ✅ A release after withdrawal can't happen, and a test proves it.
  ✅ Nothing the student removed is left behind on the server.
  ❌ Every long job needs a withdrawn-flag check before it writes.
B) Let jobs finish; the release step checks the flag and hides the receipt
  ✅ Less code: one check at release.
  ❌ A built receipt and its AI outputs stay on the server after the student removed the record.
Net: guaranteed removal everywhere, versus one check at the last step.
Header: D10 Withdraw
Options:
A) Cancel + delete (recommended)
Cancel queued jobs in the same transaction; running jobs check the flag; unreleased receipt deleted; teacher tombstone; frozen-clock test. (human ~4 h / CC ~15 min)
B) Check at release
Jobs finish; release checks the flag and hides the receipt.

State: approved
Actual answer: A) Cancel + delete (recommended), D10, 2026-10-24
Accepted scope: record.withdrawn cancels queued compile, L3, question and release jobs for the log in the same transaction; running jobs check the withdrawn flag before writing and stop; any compiled-but-unreleased receipt is deleted with its stored outputs; teacher-side tombstone (log_id, withdrawn_at) drives 'record removed'; integration test with a frozen clock. Written into receipt.md §7 and evaluation.md §3.
History: none

### Section 1 dispositions
A1 → D8 A (accepted); A2 → D9 A (accepted); A3 → D10 A (accepted).

## Section 2: Code quality

Findings:
- Q1 [P2] (8/10) design/workspace.md:41 — "Never suggested again for that sentence": sentences have no stable id across edits (event-log.md §4 has only origin and claim marks). → R10
- Carried (no question; proof of approved contracts): `map_suggest` output validated like Coach grounding (coach-helper.md §4): existing claim_id + span inside the changed paragraphs, else dropped; output is ids only, label is a fixed template; errors follow D13 classes (LLMSchema → drop, LLMAuth → operator alert).

### R10: How "Not this" stops the same suggestion coming back
Finding: Q1, P2, 8/10, design/workspace.md:41, Claude
Plan baseline: 5A: "Not this → gone; never suggested again for that sentence"; D3: `map.answer {suggestion_id, no}`; mark kinds are a closed list, adding one is a schema bump (architecture.md:73).
Runtime evidence: none (not built).
Comparison grid:
| Choice | Current | A | B |
|---|---|---|---|
| R10 rejection key | "that sentence" (undefined) | (claim_id, sha256 of the normalised sentence text) from `map.answer no`; a materially edited sentence may be suggested again | a hidden sentence-anchor mark in web/schema.json that survives edits; key = (claim_id, anchor_id) |
| Schema | unchanged | unchanged | bump (new mark kind; golden logs regenerate, D33) |
| Copy (5A) | "never again for that sentence" | "not suggested again for that sentence unless you rewrite it" | unchanged |
Question D11:
D11 — How does 'Not this' stop the same suggestion coming back? <gstack-qid:plan-eng-review-reject-key>
Project/branch/task: main, eng review of D-035/D-036; suggestions and answers are chained events (D3).
ELI10: When a student says 'Not this', the design promises that suggestion never comes back for that sentence. But sentences have no permanent ID: they change as the student edits. We either remember the rejection by the sentence's exact words (an edited sentence counts as new), or add an invisible tag to every sentence that follows it through edits.
Stakes if we pick wrong: students see the same rejected suggestion again and feel ignored, or we change the editor schema for a small feature.
Recommendation: A, because remembering by the claim plus the sentence's words is simple and needs no schema change, and a rewritten sentence is a fair reason to look again.
Completeness: A=8/10, B=9/10
Pros / cons:
A) Key rejections by (claim_id, hash of the normalised sentence text); a materially rewritten sentence may get suggested again; the 5A copy becomes 'not suggested again for that sentence unless you rewrite it' (recommended) (human: ~1 h / CC: ~5 min)
  ✅ No editor schema change, so no golden-log regeneration and no S1 replay risk.
  ✅ Honest copy: the student knows a rewrite resets it.
  ❌ Small edits that change the words (a typo fix) can bring a rejected suggestion back.
B) Add a hidden sentence-anchor mark to web/schema.json that survives edits; key by (claim_id, anchor_id)
  ✅ The promise holds exactly, even across heavy edits.
  ❌ A schema bump: regenerates golden logs (D33) and adds a mark kind the replay must handle.
Net: simple and honest with an occasional repeat, versus exact at the cost of a schema change.
Header: D11 Reject key
Options:
A) Claim + text hash (recommended)
Key (claim_id, normalised sentence hash); rewrite may re-suggest; copy says 'unless you rewrite it'. (human ~1 h / CC ~5 min)
B) Sentence anchor mark
New hidden mark kind in web/schema.json; key (claim_id, anchor_id); schema bump.

State: approved
Actual answer: A) Claim + text hash (recommended), D11, 2026-10-24
Accepted scope: Rejections keyed by (claim_id, sha256 of the normalised sentence text) from map.answer no; a materially rewritten sentence may be suggested again; workspace.md §2 'Not this' row reads 'not suggested again for that sentence unless you rewrite it'; no schema change.
History: none

### Section 2 dispositions
Q1 → D11 A (accepted). Carried items applied as proof of approved contracts.

## Section 3: Tests

Framework: pytest (`ROOM_LLM=stub`), Playwright + axe (CLAUDE.md §7; evaluation.md §3). All paths below are proposals (prototype/ empty); every test is required proof of an approved decision, so no new test-policy question was needed.

```
CODE PATHS (proposed)                                   USER FLOWS
[+] server/mapper/ job (D2)                             [+] Student writes with the map on
  ├── batch < 30 changed words → skip      [GAP] D6       ├── [GAP] [→E2E] suggestion appears, Yes → band 4 (never traced)
  ├── one queued per log, newest wins      [GAP] D6       ├── [GAP] [→E2E] Not this → gone; same sentence not re-suggested; rewrite may re-suggest (D11)
  ├── cap 40 reached → stop                [GAP] D6       └── [GAP]        mapper down → map stops, no banner (5A)
  ├── payload = changed ¶ + claims + titles [GAP] D5
  ├── output validation (claim_id + span)  [GAP]        [+] Submit race
  ├── LLM errors (D13 classes)             [GAP]          └── [GAP] [→E2E] submit while mapper job runs → result discarded, seal intact (D4)
  ├── submit → cancel queued; late → drop  [GAP] D4
  └── flag off → nothing sent              [GAP] D5     [+] Show my trail
[+] events map.suggestion / map.answer (D3)               └── [GAP] [→E2E] toggle on → provisional line + bands
  ├── chained, verify() covers them        [GAP]
  └── yes → claim mark by: student          [GAP]       [+] Withdraw before release
[+] server/trail/ (D8)                                    └── [GAP] [→E2E] withdraw → teacher sees 'record removed', never a receipt
  └── == L1 receipt bands (golden parity)  [GAP]
[+] withdraw (D10): cancel jobs, running job stops, unreleased receipt deleted  [GAP]
[+] receipt_status table (D9): not in student log, audit row  [GAP]
[+] Coach queue: mapper findings share 1/10 min, 6/assignment (17A)  [GAP]

LLM integration: [GAP] [→EVAL] map_suggest prompt/model: labelled golden eval, precision >= 0.80, <= 1/batch, both backends (D7)

COVERAGE: 0/22 paths tested (0%; nothing built) | GAPS: 22 (6 E2E, 1 eval)
```

Proposed tests (all required by the cited answers):
- `server/tests/test_mapper.py` (unit): skip <30 words; coalesce one queued job per log; cap 40 stops suggestions; payload contains only changed paragraphs + claim texts + block titles and no names; invalid claim_id/span dropped; LLMSchema → drop, LLMAuth → operator alert; flag off → zero outbound calls (fake transport).
- `server/tests/test_events.py` (extend existing table): `map.suggestion` and `map.answer` round-trip through append + verify; a post-seal mapper result is never appended; whitelist unchanged (extends S5 rows).
- `server/tests/test_trail.py` (golden parity): for every golden session, trail bands at the submit doc_rev == L1 receipt bands.
- Integration (extend evaluation.md §3 row): withdraw between submit and release with a frozen clock → no release, jobs cancelled, unreleased receipt and stored outputs deleted; running job checks the flag.
- `server/tests/test_teacher_status.py`: Mark as discussed writes receipt_status + audit row and no event in the student log.
- `server/tests/test_coach_queue.py`: with mapper findings present, unprompted questions ≤ 1 per 10 min and ≤ 6 per assignment; case B/C outrank mapper findings.
- Playwright: suggestion Yes/No flows (incl. D11 rewrite), submit race, trail toggle, withdraw, plus the D-036 workspace states and widths (design-review-v1.md T2–T10).
- [→EVAL] mapper eval per D7.

Tests made obsolete: none.

### Section 3 dispositions
No new choices; all tests carried as required proof of D3–D11 and D-036.

## Section 4: Performance

No issues found requiring a decision. Scale: one class (~30 students). Mapper: ≤ ~30 chained appends per 5 min through BEGIN IMMEDIATE [estimated]; LLM load bounded by D6. Trail: replay from the nearest checkpoint (≤ 5 min of steps) + mark check + L1, no LLM; ~0.5 req/s worst case [estimated]; implementation note: cache by (log_id, doc_rev).

## Outside Voice (native Plan subagent; Codex skipped at founder request)

Completed in ~91 s, before the 5-min timer (timer stopped). 10 findings (1 Critical, 3 High, 5 Medium, 1 Low). Recommendation: fix 1–3 before M4m.
- 10 (Low, validation): factual correction, already in architecture.md:74 (claim_id + span checked, else dropped); "small model" stays an unverified premise settled by D7. No question.
- 1 → R11 (sub-count) + R12 (paste exclusion); 2 → R13; 3 → R14; 4 → R15; 5 → R16 (reopens D7); 6 → R17; 7 → R18; 8 → R19; 9 → R20.

### R11: Can the receipt tell accepted map suggestions from the student's own links?
Finding: OV-1, Critical, 8/10, design/event-log.md:78, 95; design/receipt.md:54, outside voice (Plan subagent)
Plan baseline: D3: Yes applies claim mark {claim_id, by: student}; band 4 'linked by the student, not checked'; receipt About shows only the count of suggestions.
Runtime evidence: none (not built). claim.by values: student, coach, import (event-log.md:93-96).
Comparison grid:
| Choice | Current | A | B | C | D |
|---|---|---|---|---|---|
| R11 mark origin | by: student, indistinguishable | claim mark gains attr `suggestion_id` (by stays student); receipt shows under band 4 "of which N accepted from map suggestions"; chain view says "linked by the student from a map suggestion" | unchanged | investigate (bounded: decide after S1 schema parity check) | deferred |
| Schema | — | attr on existing mark: schema bump (D33 golden regen) | none | none | none |
| R12 paste exclusion | pending | pending | pending | pending | pending |
Question D12:
D12 — Should the receipt show which student links came from accepted map suggestions? <gstack-qid:plan-eng-review-ov-map-accepted-count>
Project/branch/task: main, eng review of D-035/D-036; outside voice finding 1 (Critical).
ELI10: When a student clicks 'Yes, link it', the link is recorded exactly like one they made by hand. So the teacher's receipt can't tell 'the student linked this' from 'the model proposed this and the student clicked yes'. The model's choice then hides inside the student's own band. Note: A partly reopens design 4A ('the teacher never sees suggestions in bars or chain'): accepted ones would show as a sub-count and in the chain wording; rejected and unanswered ones stay invisible.
Stakes if we pick wrong: the model quietly shapes a band the teacher reads as the student's own work, which breaks D-035's 'never trust'.
Recommendation: A, because the record should say where every link came from, and one attribute on the existing mark does it.
Note: options differ in kind, not coverage — no completeness score.
Pros / cons:
A) Apply: the claim mark carries `suggestion_id` when it came from a Yes (by stays student); the receipt shows 'of which N accepted from map suggestions' under band 4, and the chain view says 'linked by the student from a map suggestion' (recommended) (human: ~3 h / CC: ~15 min; schema bump regenerates goldens)
  ✅ The teacher sees exactly how many student links the model proposed. Nothing is hidden.
  ✅ No new band and no change to traced; one attribute and one sub-count.
  ❌ A schema bump: golden logs regenerate (D33) and S1's parity check must cover the new attribute.
B) Keep: accepted suggestions stay identical to hand-made links
  ✅ No schema change and nothing new to explain to teachers.
  ❌ The receipt can't separate the model's proposals from the student's own links.
C) Investigate before choosing: check after S1 whether attributes on marks are cheap to replay, then decide
  ✅ Avoids committing to a schema change before the editor spike.
  ❌ Leaves the record ambiguous until then; no change is approved now.
D) Defer this proposed change only
  ✅ Keeps the review moving; revisit at M4m.
  ❌ The row stays unresolved and the issue may be forgotten.
Net: a faithful record at the cost of a schema bump, versus a simpler but ambiguous one.
Header: D12 Sub-count
Options:
A) Apply (recommended)
Claim mark carries suggestion_id; receipt sub-count 'of which N accepted from map suggestions'; chain view wording; schema bump. (human ~3 h / CC ~15 min)
B) Keep current
Accepted suggestions identical to hand-made links.
C) Investigate first
Decide after S1 checks mark-attribute replay cost; nothing approved now.
D) Defer this only
Leave this row unresolved; revisit at M4m.

State: approved
Actual answer: A) Apply (recommended), D12, 2026-10-24
Accepted scope: Claim mark gains attr suggestion_id when it came from a map Yes (by stays student; schema bump, goldens regenerate D33, S1 parity covers it); receipt shows under band 4 'of which N accepted from map suggestions'; chain view says 'linked by the student from a map suggestion'. Partly reopens 4A for accepted suggestions only. Written into event-log.md §4, receipt.md §2-3, workspace.md §2.
History: none

### R12: Can mostly-pasted sentences enter band 4 through a link?
Finding: OV-1, Critical, 8/10, design/provenance.md:87 (band 4 rule), outside voice (Plan subagent)
Plan baseline: band 4 rule "The sentence's claim link is by: student and L3b did not confirm it" (provenance.md, §6 order 4), with no paste condition; D27/CEO-17: a student self-linking outside text gets its own band, "flagged for L3b" (provenance.md:129). D12 (approved): accepted suggestions carry suggestion_id and a sub-count.
Runtime evidence: none (not built).
Comparison grid:
| Choice | Current | A | B | C | D |
|---|---|---|---|---|---|
| R12 band 4 for paste_ext | allowed (any linked sentence) | a sentence with ≥ 50% `paste_ext` characters cannot enter band 4 by any link (hand-made or accepted); it stays untraced with the note "pasted; linked by the student, not checked" | unchanged | investigate on golden/S3 data before choosing | deferred |
| Applies to hand-made links too | — | yes (changes D27 behaviour) | — | — | — |
| D12 sub-count | approved | unchanged | unchanged | unchanged | unchanged |
Question D13:
D13 — Can a mostly pasted sentence move into 'linked by the student' just because it was linked? <gstack-qid:plan-eng-review-ov-paste-band4>
Project/branch/task: main, eng review of D-035/D-036; outside voice finding 1 (Critical), part 2.
ELI10: Today, any sentence the student links to a claim lands in 'linked by the student, not checked', even if most of it was pasted from outside. With the mapper, a pasted AI paragraph can get a suggested link and one click moves it out of 'untraced'. The proposal: if half or more of a sentence was pasted from outside, a link alone can't move it; it stays untraced with a note saying the student linked it. This also changes hand-made links (D27), not just map ones.
Stakes if we pick wrong: a click turns pasted outside text into a friendlier band on the teacher's receipt, or honest students who paste their own notes lose credit for linking them.
Recommendation: A, because a link says what a sentence argues, not where its words came from, and pasted words should stay visible as pasted.
Note: options differ in kind, not coverage — no completeness score.
Pros / cons:
A) Apply: a sentence with >= 50% paste_ext characters cannot enter band 4 by any link (hand-made or accepted); it stays untraced with the note 'pasted; linked by the student, not checked'. Golden session 'student links an outside-AI paragraph' updated (recommended) (human: ~2 h / CC: ~10 min)
  ✅ No click can move pasted outside words out of untraced. The 'never trust' line holds for hand and map links alike.
  ✅ The note still credits the student's link, so the teacher sees both facts.
  ❌ A student who pasted their own notes from another app and linked them stays untraced (the stated blind spot; they can declare via the Door).
B) Keep: any linked sentence enters band 4
  ✅ No change to D27's band rules or the goldens.
  ❌ One click moves pasted outside text into a friendlier band, and the mapper makes that easy.
C) Investigate before choosing: measure on goldens and S3 pairs how often linked sentences are mostly pasted
  ✅ Decision based on data rather than a rule of thumb.
  ❌ Leaves the loophole open until measured; nothing approved now.
D) Defer this proposed change only
  ✅ Moves on; revisit at M4m.
  ❌ The loophole stays in the plan unresolved.
Net: pasted words always stay visible as pasted, versus keeping links as the student's free choice.
Header: D13 Paste
Options:
A) Apply (recommended)
>= 50% paste_ext sentences can't enter band 4 by any link; untraced with note 'pasted; linked by the student, not checked'; golden updated. (human ~2 h / CC ~10 min)
B) Keep current
Any linked sentence enters band 4.
C) Investigate first
Measure on goldens and S3 pairs before choosing; nothing approved now.
D) Defer this only
Leave this row unresolved; revisit at M4m.

State: approved
Actual answer: A) Apply (recommended), D13, 2026-10-24
Accepted scope: A sentence with >= 50% paste_ext characters cannot enter band 4 by any link (hand-made or accepted); it stays untraced with the note 'pasted; linked by the student, not checked'; changes D27 behaviour; golden 'student links an outside-AI paragraph' expected receipt updated. Written into provenance.md §6 and evaluation.md §2.
History: none

### R13: Anchoring a suggestion to text that has moved on
Finding: OV-2, High, 8/10, design/event-log.md:77; design/workspace.md:36-44, outside voice (Plan subagent)
Plan baseline: D3: `map.suggestion {suggestion_id, span, claim_id, artifact_id, output_hash}`; D6: lowest priority, so results arrive minutes later; D11: rejections keyed by (claim_id, normalised sentence hash). No stale state in workspace.md §2.
Runtime evidence: none (not built). ProseMirror steps carry position maps (event-log.md §4, web/schema.json).
Comparison grid:
| Choice | Current | A | B | C | D |
|---|---|---|---|---|---|
| R13 suggestion anchor | span only | `map.suggestion` adds `doc_rev` and `sentence_hash`; the client maps the span through later steps; if the sentence's hash no longer matches, the suggestion is Stale and is not shown (no event) | unchanged | investigate in S1 (position mapping cost) | deferred |
| Stale state in workspace.md §2 | none | new row: "Stale: the sentence changed since the suggestion; it is not shown" | none | none | none |
| D11 key | (claim_id, sentence hash) | aligned (same sentence_hash) | unchanged | unchanged | unchanged |
Question D14:
D14 — What happens when a suggestion arrives for a sentence the student has already changed? <gstack-qid:plan-eng-review-ov-suggestion-anchor>
Project/branch/task: main, eng review of D-035/D-036; outside voice finding 2 (High).
ELI10: The mapper looks at a 5-minute batch and answers minutes later (it runs last, D6). By then the student may have rewritten or moved the sentence. The suggestion only stores a position, so it could land on the wrong words. The fix: remember which version of the draft and which sentence it was about; if that sentence has changed, quietly don't show it.
Stakes if we pick wrong: suggestions attach to the wrong sentence, and a student who clicks Yes links text the model never read.
Recommendation: A, because a suggestion is only meaningful for the exact words it was computed on, and dropping stale ones keeps the map honest.
Note: options differ in kind, not coverage — no completeness score.
Pros / cons:
A) Apply: `map.suggestion` adds doc_rev and sentence_hash; the client maps the span through later steps; if the sentence's hash no longer matches, it is Stale and not shown (no event); new Stale row in workspace.md §2; D11 uses the same sentence_hash (recommended) (human: ~3 h / CC: ~15 min)
  ✅ A Yes always links the exact words the model read.
  ✅ Rejections and suggestions share one sentence key, so D11 works as written.
  ❌ Students who edit quickly will see fewer suggestions, since many go stale.
B) Keep: position-only spans
  ✅ Nothing new to build.
  ❌ Late suggestions can attach to the wrong words.
C) Investigate in S1: measure the cost of mapping positions through steps first
  ✅ Grounds the choice in the editor spike.
  ❌ Leaves misplaced suggestions possible until then; nothing approved now.
D) Defer this proposed change only
  ✅ Moves on; revisit at M4m.
  ❌ The row stays unresolved.
Net: exact anchoring with fewer shown suggestions, versus more suggestions that may land on the wrong words.
Header: D14 Anchor
Options:
A) Apply (recommended)
Add doc_rev + sentence_hash; client maps span forward; changed sentence = Stale, not shown; new Stale row; D11 shares the hash. (human ~3 h / CC ~15 min)
B) Keep current
Position-only spans.
C) Investigate first
Measure position-mapping cost in S1; nothing approved now.
D) Defer this only
Leave this row unresolved; revisit at M4m.

State: approved
Actual answer: A) Apply (recommended), D14, 2026-10-24
Accepted scope: map.suggestion adds doc_rev and sentence_hash; client maps the span through later steps; if the sentence hash no longer matches it is Stale and not shown (no event); new Stale row in workspace.md §2; D11 uses the same sentence_hash. Written into event-log.md §3 and workspace.md §2.
History: none

### R14: What a "mapper finding" is, and how it may reach a question
Finding: OV-3, High, 8/10, design/coach-helper.md:47; design/receipt.md §4; outside voice (Plan subagent)
Plan baseline: D-035: "flags feed the 2–3 where-to-ask questions"; 17A: mapper findings are Coach candidates after cases B/C, and unasked findings may feed the receipt's questions; receipt §4 lists six candidate types, none from the mapper; D3 defines only link suggestions.
Runtime evidence: none (not built).
Comparison grid:
| Choice | Current | A | B | C | D |
|---|---|---|---|---|---|
| R14 finding definition | undefined | `map_suggest` output may include findings of two kinds only: `unconnected_paragraph` (¶ with no claim link) and `claim_without_source`; each appended as chained `map.finding {finding_id, kind, span, claim_id?, artifact_id, output_hash}` | undefined | investigate during M4m prompt work | deferred |
| Inputs excluded | none | a sentence with a `map.answer no` is never the subject of a finding or a question from one | — | — | — |
| receipt §4 | 6 candidate types | adds 7: an unanswered `map.finding`, cited by its event_id + artifact_id; same grounding and wording rules | unchanged | unchanged | unchanged |
| D4 post-seal | approved | applies to map.finding too | — | — | — |
Question D15:
D15 — What exactly is a 'mapper finding' that can become a Coach or teacher question? <gstack-qid:plan-eng-review-ov-mapper-findings>
Project/branch/task: main, eng review of D-035/D-036; outside voice finding 3 (High).
ELI10: D-035 and 17A say the mapper's 'findings' can turn into Coach questions for the student and 'where to ask' questions for the teacher. But the only thing the mapper is defined to produce is a link suggestion. Nothing says what a finding is, how it's recorded, or that a suggestion the student rejected can't come back as a teacher question.
Stakes if we pick wrong: teacher questions cite model output nobody can check, or a rejected suggestion resurfaces as a question about the student.
Recommendation: A, because two narrow, structural finding kinds are enough for the questions we want, and recording them in the sealed log keeps every receipt question citable (D31).
Note: options differ in kind, not coverage — no completeness score.
Pros / cons:
A) Apply: findings are only `unconnected_paragraph` and `claim_without_source`, appended as chained `map.finding` (finding_id, kind, span, claim_id?, artifact_id, output_hash); sentences with a 'Not this' answer are never their subject; receipt §4 adds candidate 7 (an unanswered map.finding, cited by event + artifact id, same grounding/wording rules); D4's post-seal discard covers findings (recommended) (human: ~3 h / CC: ~15 min)
  ✅ Every question built from the mapper cites a sealed record, so receipts stay checkable and byte-identical.
  ✅ A 'Not this' can never come back as a question about the student.
  ❌ Narrow kinds miss subtler findings (e.g. a claim that contradicts a source) until a later version.
B) Keep: leave 'findings' undefined
  ✅ No new event type now.
  ❌ Implementers invent the finding format and may feed uncited model output into teacher questions.
C) Investigate during M4m prompt work, then decide the kinds
  ✅ Kinds chosen from what the model can actually do well.
  ❌ The receipt path stays undefined until then; nothing approved now.
D) Defer this proposed change only
  ✅ Moves on.
  ❌ The row stays unresolved.
Net: two checkable finding kinds now, versus open-ended findings that may not be citable.
Header: D15 Findings
Options:
A) Apply (recommended)
Two kinds (unconnected_paragraph, claim_without_source) as chained map.finding; never about 'Not this' sentences; receipt §4 candidate 7; D4 covers it. (human ~3 h / CC ~15 min)
B) Keep current
Findings stay undefined.
C) Investigate first
Choose kinds during M4m prompt work; nothing approved now.
D) Defer this only
Leave this row unresolved.

State: approved
Actual answer: A) Apply (recommended), D15, 2026-10-24
Accepted scope: Mapper findings are only unconnected_paragraph and claim_without_source, appended as chained map.finding {finding_id, kind, span, claim_id?, artifact_id, output_hash}; sentences with a map.answer no are never their subject; receipt §4 adds candidate 7 (an unanswered map.finding, cited by event_id + artifact_id, same grounding/wording rules); D4 discard covers findings. Written into event-log.md §3, §6, receipt.md §4, coach-helper.md §3.
History: none

### R15: Keeping the human-session stop rule clean of the mapper
Finding: OV-4, High, 8/10, design/build-plan.md (M4m, H rows); design/evaluation.md §2a, outside voice (Plan subagent)
Plan baseline: H (~11-17): 3–5 real people, preregistered stop rule "honest median untraced ≤ 40%, or stop and fix the flow" (build-plan.md H row); D1: M4m after M4, undated; D7: needs 3 human sessions, and H is the only planned one.
Runtime evidence: none.
Comparison grid:
| Choice | Current | A | B | C | D |
|---|---|---|---|---|---|
| R15 H flag state | unspecified | H runs with `mapper_enabled` off; the stop rule is measured without the mapper | unchanged (may run with mapper on) | investigate | deferred |
| D7 human sessions | from H | 3 separate mapper sessions after M4m, flag on, results kept apart from H | from H | — | — |
| M4m dates | undated | after H: ~11-18 → 11-21 [estimated] | undated | — | — |
Question D16:
D16 — Should the human sessions (H) run with the mapper switched off? <gstack-qid:plan-eng-review-ov-h-sessions>
Project/branch/task: main, eng review of D-035/D-036; outside voice finding 4 (High).
ELI10: Before the pilot, 3–5 real people write in the platform (H) and we check a stop rule: honest writers' untraced share must be 40% or less. The mapper's eval (D7) also needs 3 human sessions, and H is the only one planned. If the mapper is on during H, accepted suggestions move text out of untraced, so the stop rule partly measures the mapper, not the writing flow.
Stakes if we pick wrong: the pilot gate passes because of the mapper, not because the core flow works, or the mapper eval gets no clean human data.
Recommendation: A, because each test should measure one thing: H tests the core flow, and separate sessions test the mapper.
Note: options differ in kind, not coverage — no completeness score.
Pros / cons:
A) Apply: H runs with mapper_enabled off; D7's 3 human sessions are separate, after M4m, with the flag on, results kept apart; M4m dated after H at about 11-18 to 11-21 [estimated] (recommended) (human: 3 more sessions to recruit / CC: ~10 min to replan)
  ✅ The stop rule measures the core writing flow alone, as preregistered.
  ✅ The mapper eval gets its own human data.
  ❌ Three more human sessions to recruit and run.
B) Keep: H may run with the mapper on
  ✅ No extra sessions.
  ❌ The stop rule mixes two effects and can pass for the wrong reason.
C) Investigate before choosing
  ✅ Time to check recruiting capacity.
  ❌ Leaves the gate measurement ambiguous; nothing approved now.
D) Defer this proposed change only
  ✅ Moves on.
  ❌ The row stays unresolved.
Net: two clean measurements with more recruiting, versus one mixed one.
Header: D16 H sessions
Options:
A) Apply (recommended)
H with mapper off; 3 separate mapper sessions after M4m; M4m ~11-18 to 11-21 [estimated].
B) Keep current
H may run with the mapper on.
C) Investigate first
Check recruiting capacity first; nothing approved now.
D) Defer this only
Leave this row unresolved.

State: approved
Actual answer: A) Apply (recommended), D16, 2026-10-24
Accepted scope: H runs with mapper_enabled off (stop rule measured without the mapper); D7's 3 human sessions are separate, after M4m, flag on, results kept apart; M4m dated ~11-18 to 11-21 [estimated], after H. Written into build-plan.md M4m and H rows and evaluation.md §2a.
History: none

### R16: Tightening the mapper eval bar (reopens D7)
Finding: OV-5, Medium, 7/10, design/evaluation.md §2a, outside voice (Plan subagent)
Plan baseline: D7 (approved): expected_links labels in 15–20 hand sessions; precision ≥ 0.80; ≤ 1 suggestion per batch; both backends; + 3 human sessions where students reject < 1 in 3 (D16: separate from H). Reopened for new evidence: no recall floor (a silent mapper passes); "reject < 1 in 3" rewards accepting (the D13 path); same author writes labels and prompt.
Runtime evidence: none.
Comparison grid:
| Choice | Current | A | B | C | D |
|---|---|---|---|---|---|
| R16 recall floor | none | ≥ 0.50 of labelled links get suggested | none | investigate | deferred |
| R16 human-session measure | students reject < 1 in 3 | a second person labels each shown suggestion correct/incorrect; precision ≥ 0.80 on those too (reject rate reported, not gated) | reject < 1 in 3 | — | — |
| R16 hold-out | none | ≥ 5 golden sessions labelled by someone other than the prompt author and never used while tuning | none | — | — |
| Other D7 values (precision ≥ 0.80, ≤ 1/batch, both backends, CI + live) | approved | unchanged | unchanged | unchanged | unchanged |
Question D17:
D17 — Tighten the mapper eval so a timid or flattering mapper can't pass? <gstack-qid:plan-eng-review-ov-eval-bar>
Project/branch/task: main, eng review of D-035/D-036; outside voice finding 5 (Medium); reopens D7 with new evidence.
ELI10: D7's bar checks that suggestions are mostly right and not too frequent. But a mapper that almost never suggests anything passes easily. 'Students reject fewer than 1 in 3' rewards students clicking Yes, not the suggestion being right. And the same person writing the prompt and the answer key will overfit.
Stakes if we pick wrong: the flag turns on for a mapper that is useless or quietly wrong, and nobody can tell from the numbers.
Recommendation: A, because a recall floor, correctness labels instead of accept rates, and held-out sessions are the standard fixes for exactly these three gaps.
Note: options differ in kind, not coverage — no completeness score.
Pros / cons:
A) Apply: add a recall floor (>= 0.50 of labelled links suggested); in the human sessions a second person labels each shown suggestion correct or not, precision >= 0.80 there too (reject rate reported, not gated); >= 5 golden sessions labelled by someone other than the prompt author and never used in tuning. Other D7 values unchanged (recommended) (human: ~1 day more labelling / CC: ~20 min)
  ✅ A mapper must be useful, right and not overfit to pass.
  ✅ Accepting stops being the measure, so the eval can't reward the D13 risk.
  ❌ Needs a second labeller and about a day more of labelling.
B) Keep D7 as approved
  ✅ Less labelling work.
  ❌ A silent or flattering mapper can pass the bar.
C) Investigate before choosing
  ✅ Time to find a second labeller first.
  ❌ The bar stays gameable; nothing approved now.
D) Defer this proposed change only
  ✅ Moves on.
  ❌ The row stays unresolved.
Net: a bar that can't be gamed, at the cost of a second labeller, versus the simpler D7 bar.
Header: D17 Eval bar
Options:
A) Apply (recommended)
Recall >= 0.50; second-person correctness labels in human sessions (precision >= 0.80); >= 5 held-out sessions by another labeller; rest of D7 unchanged. (human ~1 day / CC ~20 min)
B) Keep D7
Keep the bar as approved in D7.
C) Investigate first
Find a second labeller first; nothing approved now.
D) Defer this only
Leave this row unresolved.

State: approved
Actual answer: A) Apply (recommended), D17, 2026-10-24
Accepted scope: Add recall floor >= 0.50 of labelled links suggested; in the separate human sessions a second person labels each shown suggestion correct/incorrect, precision >= 0.80 there too (reject rate reported, not gated); >= 5 golden sessions labelled by someone other than the prompt author and never used in tuning. Other D7 values unchanged. Written into evaluation.md §2a.
History: D7 approved the original bar (R5, A). Reopened 2026-10-24 on outside-voice evidence (no recall floor; accept-rate measure; same-author labels).

### R17: A visible limit on open map suggestions
Finding: OV-6, Medium, 7/10, design/coach-helper.md:47 vs design/workspace.md:39, outside voice (Plan subagent)
Plan baseline: 17A: one budget for Coach questions (incl. mapper findings), 1 per 10 min, 6 per assignment; 5A/11A/16A: suggestions appear in the map rail without motion, sound or live announcement; D6: mapper cap 40 calls per submission; D7/D17: ≤ 1 suggestion per batch on average.
Runtime evidence: none.
Comparison grid:
| Choice | Current | A | B | C | D |
|---|---|---|---|---|---|
| R17 open suggestions | unbounded (only call caps) | at most 3 unanswered suggestions shown at once; a newer one replaces the oldest, which expires silently (no event) | unbounded; rely on no-motion rules and ≤ 1/batch | investigate in the D16 mapper sessions | deferred |
| Coach budget (17A) | questions only | unchanged | unchanged | unchanged | unchanged |
Question D18:
D18 — Should the map show at most a few open suggestions at a time? <gstack-qid:plan-eng-review-ov-suggestion-cap>
Project/branch/task: main, eng review of D-035/D-036; outside voice finding 6 (Medium).
ELI10: Coach questions have a strict budget (1 per 10 minutes, 6 per assignment), but map suggestions don't. They're quiet (no motion, sound or announcement), yet over a long session dozens could pile up in the map rail, which turns the student's own map into a to-do list written by the model.
Stakes if we pick wrong: the map fills with model suggestions and stops feeling like the student's own, or a useful suggestion gets pushed out too soon.
Recommendation: A, because a small visible limit keeps the map the student's, and the no-motion rules already keep each suggestion quiet.
Note: options differ in kind, not coverage — no completeness score.
Pros / cons:
A) Apply: at most 3 unanswered suggestions are shown at once; a newer one replaces the oldest, which expires silently (no event). Coach budget unchanged (recommended) (human: ~1 h / CC: ~5 min)
  ✅ The map never becomes a backlog of model suggestions.
  ✅ Simple, visible rule; no change to the Coach budget.
  ❌ A useful older suggestion can disappear before the student looks at it.
B) Keep: no limit beyond the call caps and the no-motion rules
  ✅ Every suggestion stays available until submit.
  ❌ Long sessions can pile up dozens of open suggestions in the rail.
C) Investigate in the D16 mapper sessions
  ✅ Set the limit from real behaviour.
  ❌ No limit until then; nothing approved now.
D) Defer this proposed change only
  ✅ Moves on.
  ❌ The row stays unresolved.
Net: a calm, student-owned map with occasional lost suggestions, versus keeping every suggestion.
Header: D18 Open cap
Options:
A) Apply (recommended)
At most 3 unanswered suggestions shown; newest replaces oldest, which expires silently. Coach budget unchanged. (human ~1 h / CC ~5 min)
B) Keep current
No limit beyond call caps and no-motion rules.
C) Investigate first
Set the limit from the D16 mapper sessions; nothing approved now.
D) Defer this only
Leave this row unresolved.

State: approved
Actual answer: A) Apply (recommended), D18, 2026-10-24
Accepted scope: At most 3 unanswered suggestions shown at once; a newer one replaces the oldest, which expires silently (no event); Coach budget unchanged. Written into workspace.md §2.
History: none

### R18: Passage links ("this paraphrases passage P") in v1
Finding: OV-7, Medium, 8/10, docs/DECISIONS.md D-035 vs design/event-log.md (map.suggestion carries only claim_id), outside voice (Plan subagent)
Plan baseline: D-035 text: "It proposes meaning links: this sentence argues claim N; this paraphrases passage P." PRODUCT.md §5 example "this paraphrases p.41". D3/D14: map.suggestion carries claim_id only. Band 2 (traced) = a chain ending in a Block (provenance.md §6).
Runtime evidence: none.
Comparison grid:
| Choice | Current | A | B | C | D |
|---|---|---|---|---|---|
| R18 passage links | promised in D-035 text, no schema | v1 mapper proposes sentence→claim links only; passage (block) links are out of v1; PRODUCT.md §5 example reworded; GLOSSARY says the same | unchanged (ambiguous) | investigate after M4m | deferred |
| Future rule | none | stated now: a model-proposed passage link can never make a sentence traced (band 2 needs a student-made chain) | none | — | — |
Question D19:
D19 — Does the v1 mapper suggest links to source passages, or only to the student's claims? <gstack-qid:plan-eng-review-ov-passage-links>
Project/branch/task: main, eng review of D-035/D-036; outside voice finding 7 (Medium).
ELI10: D-035's examples include 'this paraphrases p.41', a link from a sentence straight to a source passage. Nothing in the design records that kind of link. Worse, a sentence linked to a passage counts as 'traced to a source', the strongest band. An implementer 'completing' D-035 could let a model link make text traced.
Stakes if we pick wrong: a model-proposed passage link makes a sentence 'traced', the exact thing D-035 forbids.
Recommendation: A, because v1 only needs links to the student's own claims, and saying now that model passage links can never make text traced closes the door before anyone builds it.
Note: options differ in kind, not coverage — no completeness score.
Pros / cons:
A) Apply: the v1 mapper proposes sentence-to-claim links only; passage links are out of v1; reword the PRODUCT.md §5 example and the glossary; state now that a model-proposed passage link can never make a sentence traced (recommended) (human: ~30 min / CC: ~5 min)
  ✅ No path from a model guess to the 'traced' band, now or later.
  ✅ The docs stop promising something v1 doesn't build.
  ❌ Students don't get 'this sounds like p.41' hints, which could help them cite.
B) Keep the D-035 wording as is
  ✅ Leaves room for passage hints later without a doc change.
  ❌ Ambiguous scope; an implementer may build passage links that count as traced.
C) Investigate after M4m
  ✅ Decide with real mapper data.
  ❌ The ambiguity stays in the docs; nothing approved now.
D) Defer this proposed change only
  ✅ Moves on.
  ❌ The row stays unresolved.
Net: a narrow, safe v1 mapper, versus keeping a promise the design can't yet keep safely.
Header: D19 Passages
Options:
A) Apply (recommended)
Sentence-to-claim links only in v1; reword PRODUCT.md §5 + glossary; model passage links can never make text traced. (human ~30 min / CC ~5 min)
B) Keep current
Leave D-035's passage example as is.
C) Investigate first
Decide after M4m data; nothing approved now.
D) Defer this only
Leave this row unresolved.

State: approved
Actual answer: A) Apply (recommended), D19, 2026-10-24
Accepted scope: v1 mapper proposes sentence-to-claim links only; passage links out of v1; PRODUCT.md §5 example and GLOSSARY reworded; stated rule: a model-proposed passage link can never make a sentence traced. Written into PRODUCT.md §5, GLOSSARY, provenance.md §6.
History: none

### R19: Tying consent to the mapper flag
Finding: OV-8, Medium, 8/10, design/privacy.md:57; design/event-log.md (`log.open` carries consent_version), outside voice (Plan subagent)
Plan baseline: D5: consent adds the live-map line; flag off = nothing sent while writing; D1/D7/D17: the flag may turn on mid-pilot once the eval passes; `log.open {assignment_id, consent_version}`.
Runtime evidence: none.
Comparison grid:
| Choice | Current | A | B | C | D |
|---|---|---|---|---|---|
| R19 consent text | one text incl. the mapper line | two versions: with the mapper line (flag on) and without (flag off); the student sees the one matching the flag at consent | one text, always incl. the line | investigate with the school (OL-016) | deferred |
| R19 flag per log | global, can flip mid-log | flag value fixed per log at `log.open` (recorded with consent_version); turning it on mid-pilot affects only logs opened afterwards | global | — | — |
Question D20:
D20 — Should the mapper flag be fixed per student record at consent time? <gstack-qid:plan-eng-review-ov-consent-flag>
Project/branch/task: main, eng review of D-035/D-036; outside voice finding 8 (Medium).
ELI10: The consent text now says changed paragraphs are sent every few minutes for map suggestions. But the mapper can be off, and it might be switched on in the middle of the pilot once its eval passes. Then students who agreed to one thing get another, and students told 'we send your paragraphs' when the mapper is off are told something untrue.
Stakes if we pick wrong: draft text goes to the provider (possibly DeepSeek, China-based) under a consent the student never saw, which can end the pilot with the school.
Recommendation: A, because consent must match exactly what happens for that student, and fixing the flag when the record opens makes that automatic.
Note: options differ in kind, not coverage — no completeness score.
Pros / cons:
A) Apply: two consent versions (with and without the mapper line), shown to match the flag; the flag value is fixed per student record at log.open and stored with consent_version; switching it on mid-pilot affects only records opened afterwards (recommended) (human: ~2 h / CC: ~10 min)
  ✅ Every student's consent matches exactly what is sent for their record.
  ✅ Flipping the flag mid-pilot is safe by construction.
  ❌ Students already writing when the flag turns on won't get suggestions on that assignment.
B) Keep one consent text with the line, and a global flag
  ✅ Simpler: one text, one switch.
  ❌ Consent can promise sending that doesn't happen, or the flag can start sending mid-record.
C) Investigate with the school's consent process first (OL-016)
  ✅ Aligns with the school's wording rules.
  ❌ The mismatch stays possible until then; nothing approved now.
D) Defer this proposed change only
  ✅ Moves on.
  ❌ The row stays unresolved.
Net: consent that always matches each record, versus one simpler text that can drift.
Header: D20 Consent
Options:
A) Apply (recommended)
Two consent versions matched to the flag; flag fixed per record at log.open with consent_version; mid-pilot switch affects new records only. (human ~2 h / CC ~10 min)
B) Keep current
One consent text with the line; global flag.
C) Investigate first
Settle with the school's consent process (OL-016); nothing approved now.
D) Defer this only
Leave this row unresolved.

State: approved
Actual answer: A) Apply (recommended), D20, 2026-10-24
Accepted scope: Two consent versions (with and without the mapper line), shown to match the flag; the flag value is fixed per log at log.open and stored with consent_version; switching it on mid-pilot affects only logs opened afterwards. Written into privacy.md §4 and event-log.md (log.open payload).
History: none

### R20: What the pilot claims to test: the student's own live outline, or the mapper
Finding: OV-9, Medium, 7/10, docs/DECISIONS.md D-035 vs D1 (M4m off the gate), outside voice (Plan subagent)
Plan baseline: D-035: "The live map is the product… A mapper builds it"; D1: mapper behind a flag, not required by the pilot gate; 1A: the v1 map is an outline the student builds (claims, cards, links, two-way highlight); 18A: case C asks "Which claim is it making?" at save points.
Runtime evidence: none.
Comparison grid:
| Choice | Current | A | B | C | D |
|---|---|---|---|---|---|
| R20 pilot framing | "live map is the product, built by a mapper" | PRODUCT.md §5/§7 say: the pilot tests the live outline the student builds (claims, cards, links, two-way highlight, case C); the mapper is a flagged experiment that adds suggestions when its eval passes | unchanged | investigate after H | deferred |
| D-035 law ("model maps meaning, never trust") | locked | unchanged | unchanged | unchanged | unchanged |
Question D21:
D21 — Should the docs say the pilot tests the student's own live outline, with the mapper as an add-on experiment? <gstack-qid:plan-eng-review-ov-pilot-framing>
Project/branch/task: main, eng review of D-035/D-036; outside voice finding 9 (Medium, strategy).
ELI10: D-035 says 'the live map is the product, and a mapper builds it'. D1 then put the mapper behind a switch that may stay off for the first class. So the pilot could run without the thing D-035 calls the product. But the outline the student builds themselves (claims, cards, links, the highlight between map and text, and the Coach's 'which claim is this making?') is already a live map with no model at all.
Stakes if we pick wrong: we tell the school and ourselves the pilot tests something it doesn't, and read the results wrongly.
Recommendation: A, because it matches what will actually run, keeps D-035's 'never trust' rule untouched, and makes the mapper a measured add-on rather than an untested promise.
Note: options differ in kind, not coverage — no completeness score.
Pros / cons:
A) Apply: PRODUCT.md §5/§7 state that the pilot tests the live outline the student builds (claims, cards, links, two-way highlight, case C), and the mapper is a flagged experiment that adds suggestions once its eval passes; D-035's 'model maps meaning, never trust' unchanged (recommended) (human: ~30 min / CC: ~5 min)
  ✅ The pilot's claims match exactly what runs, so results are read correctly.
  ✅ The product still works, and is still a live map, if the mapper never passes its eval.
  ❌ Softens the D-035 story ('a model builds your map') for demos and pitches.
B) Keep D-035's framing as is
  ✅ Keeps the stronger 'live, model-built map' story.
  ❌ The pilot may test something other than what the docs call the product.
C) Investigate after H: decide the framing once the core-flow results are in
  ✅ Frame from evidence.
  ❌ Docs stay inconsistent until then; nothing approved now.
D) Defer this proposed change only
  ✅ Moves on.
  ❌ The row stays unresolved.
Net: an honest pilot claim with a softer story, versus a stronger story the pilot may not test.
Header: D21 Framing
Options:
A) Apply (recommended)
PRODUCT.md: pilot tests the student-built live outline; mapper is a flagged experiment; D-035's 'never trust' unchanged. (human ~30 min / CC ~5 min)
B) Keep current
Keep D-035's 'mapper builds the map' framing.
C) Investigate first
Decide framing after H results; nothing approved now.
D) Defer this only
Leave this row unresolved.

State: approved
Actual answer: A) Apply (recommended), D21, 2026-10-24
Accepted scope: PRODUCT.md §5/§7 state that the pilot tests the live outline the student builds (claims, cards, links, two-way highlight, case C); the mapper is a flagged experiment that adds suggestions once its eval passes; D-035's 'model maps meaning, never trust' unchanged.
History: none

Approval readiness: PASS. Checked R1 (D3), R2 (D5), R3 (D6), R4 (D4), R5 (D7), R7 (D8), R8 (D9), R9 (D10), R10 (D11), R11 (D12), R12 (D13), R13 (D14), R14 (D15), R15 (D16), R16 (D17, reopens D7), R17 (D18), R18 (D19), R19 (D20), R20 (D21); scope D1 = A, D2 = A. All answered 2026-10-24 by the founder.

## TODOS.md updates

None proposed. Richer mapper finding kinds and passage hints were ruled out of v1 by D15/D19 and stay with the D7/D17 eval loop; nothing else was deferred.

## NOT in scope

- Choosing the mapper's model ("small model"): left to the D7/D17 eval on both configured backends; unverified premise.
- Passage (block) links from the mapper: out of v1 (D19).
- Finding kinds beyond unconnected_paragraph and claim_without_source (D15).
- Re-reviewing anything the D-034 eng review approved (reused unchanged).
- Visual design system (DESIGN.md): /design-consultation gate (design 13A).

## What already exists

Jobs loop with leases (D23), `complete()` with error classes (D13), claim marks by: student (D17, D27), 5-min merged editor.batch (D30), engine/ as a pure library with L1 (D2), stored AI outputs (D31), the seal whitelist (D8), the audit table for teacher actions (D9), golden YAML sessions (D19). The mapper, trail, findings and withdrawal rules all build on these.

## Failure modes (new paths)

| Path | Realistic failure | Covered by |
|---|---|---|
| Mapper call | provider down or auth fails | map stops silently, operator alert (5A, D13); test_mapper |
| Mapper result | arrives after submit | discarded, counter (D4); events test |
| Suggestion | sentence edited before it arrives | Stale, not shown (D14) |
| Accepted suggestion on pasted text | moves untraced → band 4 | blocked ≥ 50% paste_ext (D13); golden session |
| Mapper finding | rejected sentence resurfaces as a teacher question | excluded (D15) |
| Flag flip mid-pilot | sends under the wrong consent | flag fixed per record (D20) |
| Withdraw before release | queued release still runs | cancelled in the same transaction, frozen-clock test (D10) |
| Trail | disagrees with the receipt | engine-only + parity test (D8) |

No path is left with no test, no error handling and a silent failure.

## Completion summary

- Step 0 Scope Challenge: scope accepted as-is (D1 A: M4m flagged, off the gate; D2 A: original two-service arrangement).
- Architecture: 3 issues (D8, D9, D10), all accepted.
- Code quality: 1 issue (D11), accepted; 2 items carried.
- Tests: diagram produced, 22 gaps (all proposed paths), 6 E2E, 1 eval; test plan written.
- Performance: 0 issues.
- Scope findings: 5 (D3–D7) + 1 mechanical (C6).
- Outside voice: native Plan subagent (Codex skipped at founder request), 10 findings; 9 resolved via D12–D21, 1 factual (already fixed).
- NOT in scope: written. What already exists: written. TODOS: 0 proposed. Failure modes: 0 critical gaps.
- Unverified premises: 2 ("small model" unnamed; mapper precision unmeasured until D7/D17).
- Lake Score: 19/19 recommendations chose the complete option.

## GSTACK REVIEW REPORT

| Review | Trigger | Why | Runs | Status | Findings |
|--------|---------|-----|------|--------|----------|
| CEO Review | `/plan-ceo-review` | Scope & strategy | 3 | clean (2026-10-22) | mode: SCOPE_REDUCTION, 0 critical gaps |
| Outside Review | native Plan subagent (Codex skipped at founder request) | Independent 2nd opinion | 6 | unavailable (Codex); native completed | 10 findings, 9 resolved (D12–D21), 1 factual |
| Eng Review | `/plan-eng-review` | Architecture & tests (required) | 3 | clean | 19 issues, 0 critical gaps |
| Design Review | `/plan-design-review` | UI/UX gaps | 1 | issues_open (2026-10-24) | score: 3/10 → 7/10, 20 decisions |
| DX Review | `/plan-devex-review` | Developer experience gaps | 0 | — | — |

- **OUTSIDE COVERAGE:** plan-review phase. Codex was skipped because the founder asked for an Opus/Claude voice. The native Plan subagent completed with 10 findings: 1 Critical, 3 High, 5 Medium, 1 Low. There is no completed external-provider review.
- **VERDICT:** CEO and Eng are cleared, ready to implement under the D-034 and D-037 plans. The design review stays at 7/10 until DESIGN.md (/design-consultation) and real mockups exist.

NO UNRESOLVED DECISIONS
