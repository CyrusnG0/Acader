# Evaluation: spikes, tests and pilot measures

Status: **reviewed (CEO + eng) 2026-10-23** · Last updated: 2026-10-25 (D-061, D-062)
Implements: the "[VALIDATED] only when tested" convention; CEO-6, CEO-7, CEO-14, CEO-15, CEO-18, CEO-19, CEO-21, CEO-24; D5, D6, D8, D9, D10, D19, D20, D21, D22, D23, D26, D28, D32, D33 ([eng record](../docs/designs/eng-review-v1.md)). Answers how OL-034, OL-035, OL-038 and OL-040 close.
Test plan for /qa: `~/.gstack/projects/CyrusnG0-Acader/micmic-main-eng-review-test-plan-20261023-164120.md`.

## 1. Spikes (before the main build)

Each spike gets a short preregistration (pass condition written before running), a result note in `prototype/spikes/`, and a line in UPDATE_LOG.

| # | Question | Method | Pass condition | Blocks |
|---|---|---|---|---|
| **S1** | Do origin and claim marks survive real editing, and does Python replay match? | TipTap page built on `web/schema.json`. Cases: type; type **inside and at both edges** of marked spans; IME composition; spellcheck/autocorrect replacement; Grammarly-style extension edit (Chrome); paste external; copy/paste internal; drag-drop inside and from outside; select-all + type; move; undo/redo; reload from steps. Same cases for claim marks. Replay every case with prosemirror-py (D6, D17, D21) | Marks correct in every case (typed text always `typed`; replacements `input_kind: replacement`); external paste always `paste_ext`; JS and Python replay give the same doc and marks | Editor |
| **S2** | Can we parse real readings into usable blocks? | Docling vs GROBID vs PyMuPDF on 3 real readings (nursing paper with tables, social-science working paper, CS paper) and one scan, under the 300 s cap | Block kinds and tables usable on ≥ 2 of 3; limitation passages found; the scan reports "scan" | Reading aid |
| **S3** | Does claim-level comparison catch added propositions without false "traced"? | **≥ 40 pairs**, including non-native polish and wrong-node cases, labelled by someone other than the founder | Preregistered false-traced bar met. **Fail → L3b off for the pilot** (CEO-14, CEO-24) | L3b |
| **S4** | Do bands match known behaviour? | Replay of kit v04 runs (C1 honest, C4 partial outside, C11 thin honest). Simulated evidence only | C1 mostly traced; C4's outside parts untraced or declared; C11's gaps explainable | Receipt |
| **S5** | Is the log tamper-evident? | Append, seal, then edit one event / delete one / reorder two / append a non-whitelisted event after the seal (D8) | `verify` fails on each; receipt citations and stored-output hashes resolve | Event log |

## 2. Golden sessions (the executable spec, D19, D33)

- Each golden session is a **YAML script** (actions + expected bands, moments, question targets and mapper labels). The current format and licensed source manifest are in [prototype/fixtures/README.md](../prototype/fixtures/README.md) and [prototype/fixtures/sources.yaml](../prototype/fixtures/sources.yaml).
- Logs are produced by **Playwright driving the real editor page** (the S1 page, then the M3 editor) for editor steps, plus a Python builder that posts card, anchor, Coach and Door events **through the real ingest path**.
- Logs are **regenerated in CI** whenever `web/schema.json` or editor code changes. The **expected receipts are frozen** and are the assertion.
- Sessions: honest · declared outside · pasted then partly rewritten · AI-expanded card · thin honest · **student links an outside-AI paragraph to their own card** (CEO-17; expected: untraced with the note "pasted; linked by the student, not checked", eng v2 D13) · **student accepts a map suggestion on a pasted paragraph** (same expectation, plus the D12 sub-count) · **forged quote and coach marks** (D5) · **AI prose pasted into a Coach answer, then moved** (D26) · **edit above a linked sentence** (D17) · the nursing case (CEO-15).
- Same log + same engine stamp + stored outputs → **byte-identical receipt** (D20, D31).
- Run with `ROOM_LLM=stub` fixtures in CI; live once per release on **both backends** (CEO-6).

## 2a. Mapper eval (gates `mapper_enabled`, eng review v2 D7)

- The 15–20 hand-scripted golden sessions (D-035: licensed real sources + an open textbook; simulated, never evidence about students) label, per 5-minute batch, the correct paragraph→claim links (YAML `expected_links`, D-045). A label is a `(paragraph_id, claim_id)` pair; links are not provenance judgments.
- **Pass bar:** precision ≥ 0.80 of suggestions shown; **recall ≥ 0.50** of labelled links; ≤ 1 suggestion per batch on average; on **both backends**; plus 3 human sessions **separate from H** (after M4m, flag on, results kept apart; eng v2 D16) where **a second person labels each shown suggestion correct or not and precision ≥ 0.80** (the students' reject rate is reported, not gated) (eng v2 D17).
- **Hold-out:** ≥ 5 golden sessions labelled by someone other than the prompt author and never used while tuning (eng v2 D17).
- Runs in CI as a stub replay, and live on any change to the mapper prompt or model. `mapper_enabled` turns on for the pilot only when the bar passes (D1).

## 3. Automated tests (prototype)

| Level | What |
|---|---|
| Unit | Hash chain + verify + seal whitelist; append concurrency (two batches at once → one chain, CEO-16); ts rounding + 5-min merge + session split (D12, D30); mark check incl. quote rules (D5, D29); band table, one row per rule (incl. student-linked, D27); claim-mark majority; sentence split; wording filter; leak-check shape rules; policy routing per classifier label; `complete()` error classes with a fake transport (D13) |
| Integration | Submit while the LLM is down → sealed, L1 receipt "questions pending", retry job (CEO-7); release rule incl. the +48 h cap, frozen clock (CEO-21, D7); preview has no question text (CEO-20); no student withdrawal route exists and `record.withdrawn` is refused after the seal (D-062); cap passed with no receipt → `delayed` state, operator alert, re-check releases once compiled (frozen clock, D-061); replay mismatch → labelled fallback receipt (D28); magic link GET doesn't consume, reuse/expiry rejected (D11); uninvited email → no session; Door makes zero outbound calls (CEO-9); parse caps and status (D4) |
| Security | Route enumeration: foreign IDs → 404 on every route; CSP header present; teacher audit rows written (D9) |
| Load | 30 submits in 5 minutes with a 3 s stub: every L1 receipt < 60 s, every question set < 15 min, no rate-limit errors (D23) |
| Regression | `ROOM_LLM=stub pytest writing-room-kit/v04/tests writing-room-kit/web/tests` (29 tests) on every change (D22) |
| Leak audit | Golden outputs + ~30 adversarial prompts, both backends, through `coach/leak.py`; any leak fails the release (CEO-24) |
| End to end (Playwright) | Student: invite → consent → read → card → anchor → write → paste → Coach → submit → preview. Teacher: roster → assignment → upload → status → release → receipt → chain. Two tabs (second read-only, takeover); offline then reconnect; stale queue after takeover offered as file/Door (D10, D32); submit retry across a restart (D34) |
| Accessibility | axe-core on every page; keyboard-only run of the student flow |

## 4. Human sessions and the blind test

- **Human sessions (CEO-18):** 3–5 real people, ~500 words each from one real reading, before any class. Preregistered stop rule: if the honest median **untraced** share is over 40%, fix the flow before any class sees it. The student-linked share is reported beside it (D27).
- **Blind question test (CEO-19):** in the nursing walkthrough (and the pilot), our questions are mixed with essay-only questions, unlabelled and randomised, with a preregistered win rule. The hard case is shown too.

## 5. Pilot measures (real students)

Preregister with the pilot teacher before the class starts (OL-026 for ethics).

| Question | Measure | Source |
|---|---|---|
| Does the receipt help teachers? | "Did the receipt change what you asked, or save a meeting?" + time per receipt | Teacher interview |
| Is it fair to quiet and second-language students? | Untraced share by self-reported writing habits; teacher's view of their questions | Survey + receipts (aggregate, consented) |
| Do students experience it as help? | 5-item survey: reading aid, Coach, Door, consent clarity, feeling watched | Student survey |
| Law 1 held? | Leaks in the transcript audit | Audit |
| Does the conversation settle things? | For every receipt a teacher acted on: was 5 minutes enough? | Teacher log |
| Cost | LLM calls and spend per submission | Operator counters (D15) |

**What would make us change course:** teachers ignore the receipt; students describe it as surveillance; untraced share is driven by language background rather than process.

## 6. The nursing walkthrough (OL-034, CEO-15, CEO-19)

After the engine runs on golden sessions, walk the teacher from the 2026-10-21 case through a reconstructed receipt ([receipt.md](receipt.md) §8), including the blind question test and the hard case. Ask: would this have ended the dispute faster? What would you still have asked for? Which line would you have misread? Record the answers in UPDATE_LOG and adjust the receipt.

## 7. What counts as evidence

- Kit results (v0.3–v0.5) are **simulated**. They guide design and are never quoted as evidence about real students.
- Product claims in pitches come only from validated spikes, the pilot measures above, or `docs/renewed-direction/sources-verified.md`.
