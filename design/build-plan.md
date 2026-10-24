# Build plan: prototype v1

Status: **reviewed by /plan-ceo-review and /plan-eng-review 2026-10-23; re-baselined after the eng review (D25)** · Last updated: 2026-10-23
Implements: D-029, D-032, D-033, D-034 (CEO-1 to CEO-24 in [ceo-review-v1.md](../docs/designs/ceo-review-v1.md); D1 to D35 in [eng-review-v1.md](../docs/designs/eng-review-v1.md)).
**Engine + receipt + nursing walkthrough ready: about 2026-11-08** (was 11-05; the eng review added about 8 build days, see §2). The writing UI follows around 11-14, human sessions around 11-17. Hosting is timed to the class's assignment window. Students start only when the pilot gate (§4) is green. §2a lists proposed ways to pull the milestone back toward 11-05; **none are applied**.

## 1. Shape of v1 (CEO-1: receipt-first thin slice, one class)

Receipt and chain view first, on golden sessions; then the writing flow that feeds it. The questions (claim lineage + where to ask) are what makes us different from Turnitin Clarity and Grammarly Authorship. The blind test (CEO-19) checks that bet early.

**In v1:**
- event log: one append at a time per log, staging + one chained batch per 5 min, seal = submit event, verify
- replay with prosemirror-py on a shared `web/schema.json`; checkpoint replay checks with a labelled fallback
- provenance L1 with the mark check; L3b only if the stronger S3 passes; no embeddings
- bands: traced to source, traced to Coach, declared, linked by student (not checked), untraced
- receipt + chain view + questions; engine stamp; stored AI outputs
- student preview: spans + facts, no question text
- release at the latest of deadline, submit + 24 h, questions compiled, capped at +48 h
- editor with origin marks and paragraph links (D-045), input plugin, client queue, edit lease
- teacher readings with hosted parsing (caps, status, immutability); pins by section kind
- idea cards + anchors (paste-tracked); claim list with paragraph links
- the Door (text and files only); Coach cases B and C (paste-tracked answers)
- leak check (one module; adversarial set on both backends); wording filter
- roster + scanner-safe magic link; consent; export/delete
- two LLM backends (DeepSeek + a generic OpenAI-compatible slot)
- monitoring: logs, counters, alerts, runbooks

**Deferred to [TODOS.md](../TODOS.md):** student scholarly search, LLM-directed pins, Coach cases A, D, E, claim map graph view, polish band, policy dial, receipt PDF, Blackboard LTI, further classes, L2 embeddings, Postgres.

**Still open (P0):** OL-043. If guidance makes every student's trail look alike, what else estimates AI involvement? Research before the pilot design is final.

## 2. Milestones (bottom-up, re-baselined after the eng review) [estimated]

Build days are days with Claude; founder time for outreach, approvals and the walkthrough runs alongside at about a quarter of each day. "+" lists what the eng review added.

| # | Dates | Build days | Deliverable | Done when |
|---|---|---|---|---|
| **R** | 10-23 | 0.5 | /plan-ceo-review + /plan-eng-review; stack locked (OL-008) | Done 2026-10-23 |
| **M0** | 10-24 → 10-28 | 4.75 (was 3.25) | Scaffold + CI (incl. the kit's 29 tests, D22). `web/schema.json`. LLM wrapper `complete()` with stub, error classes, boot ping, backend-2 slot. **S1** first (+ widened cases, Python replay parity: D6, D17, D21, D33), then S5 and S2 (+ a scan). Preregister **S3** (≥ 40 pairs) and S4. Design the walkthrough + blind test. Outreach and the processor-approval request | S1 go/no-go written |
| **M1** | 10-29 → 11-03 | 6.25 (was 3.75) | + Golden YAML scripts, Playwright generator and ingest builder (D19). `engine/events`: append, staging + 5-min merge, seal whitelist, verify (D8, D30). Replay + mark check (D5, D29). L1 provenance with paragraph links (D-045) and the student-linked band (D17, D27). Receipt compiler + UI + chain view + wording filter + engine stamp (D20) | 10 golden receipts render (§ evaluation 2); a person has read them |
| **✓ 10-30** | checkpoint | — | Named teacher + assignment window? (CEO-11) | Branch on the window start (CEO-23) |
| **M2** | 11-04 → 11-07 | 3.5 (was 2.75) | **Run S3.** L3b if it passes. L3a/c/e with stored outputs (D31). Preview without question text. Bounded job queue (D23), checkpoint replay jobs + fallback (D28), release rule + cap (D7). **Nursing walkthrough with the blind test and the hard case** | Walkthrough + blind-test result in UPDATE_LOG |
| **~11-08** | milestone | — | **Engine + receipt + walkthrough ready** | — |
| **M3** | 11-08 → 11-12 | 4.75 (was 3) | Editor with marks, input plugin, client queue, edit lease, stale-queue handling (D10, D32); reader, paste-tracked cards, anchors, section-kind pins, "quote this"; hosted parsing with caps and status (D4) | Real UI flow; regenerated goldens match |
| **M4** | 11-13 → 11-14 | 2 | Claim list + claim-mark UI; the Door; Coach B and C with paste-tracked answers (D26); **adversarial leak set on both backends** | Zero leaks on golden + adversarial sets |
| **M4m** | ~11-18 → 11-21 [estimated], after H (eng v2 D16) | ~4 (eng v2 D1) | Mapper (D-035): `server/mapper/` job + `map_suggest` task, `map.suggestion`/`map.answer` events (D3), cancel at submit (D4), minimum payload + consent line (D5), lowest priority + caps (D6), suggestions UI (workspace.md §2); `server/trail/` for "Show my trail"; labelled mapper eval (D7). **Behind `mapper_enabled`; not required by the pilot gate** | Eval bar met → flag on; else off |
| **M4b** | 11-15 → 11-16 | 2 (was 1) | Export/delete incl. stored outputs; security set (D9); release-window + load tests (30 submits / 5 min); submit retry (D34) | Tests green |
| **H** | ~11-17 | 1 | **Human sessions (CEO-18):** 3–5 real people, ~500 words each; preregistered stop rule; **`mapper_enabled` off** so the stop rule measures the core flow (eng v2 D16) | Honest median untraced ≤ 40%, or stop and fix the flow |
| **M5** | timed to the window | 3.25 (was 2.75) | Roster + magic link + email; consent; one machine in the consented region; SQLite backups + restore test (D3); monitoring + runbooks (D15); deploy-freeze rule; Playwright + axe; smoke test | Pilot gate green |

**Design gate (design review 13A):** run /design-consultation to produce `DESIGN.md` (typefaces for draft/receipt text and UI, type scale, spacing, radius, focus ring, dark mode from the use scene) **before the receipt UI in M1 and before M3**. Until then the interim system is the demo.html tokens plus the rules in [workspace.md](workspace.md) and [receipt.md](receipt.md) (layout, band colours, motion, states).

**Workspace design (D-036)** adds to M3/M4: the state table, trail toggle, widths incl. zoom mode, keyboard/screen-reader model and receipt layout (design-review-v1.md T2–T11) **[estimated: ~3–4 build days on top of the M3/M4 figures]**. With M4m (~4), the total rises to **≈ 35–36 build days**; M4m sits off the pilot-gate path (eng review v2, 2026-10-24). The line below is the D-034 baseline.

**Total ≈ 28 build days** (was ~20) [estimated: per-item estimates from the eng review's decision records, converted to build days; D1 and D3 save about 0.75].

### 2a. Proposed ways to pull the milestone back (not applied; founder decides)

1. **Re-sequence (≈ −1.75 days → ~11-06).** Move work the walkthrough doesn't need from M1–M2 to M4b: the 5-minute merge (D30), stored AI outputs (D31), the parallel queue and leases (D23; run sequentially until then), the replay fallback receipt (D28) and the release cap (D7). All of it stays before the pilot gate.
2. **Accept ~11-08** and tell the researchers and the nursing teacher now.
3. **Walkthrough on M1 receipts** (~11-04) with hand-checked questions instead of L3e output. This weakens the blind test, which needs the generated questions.

## 3. Cut lines (in order, if behind)

1. Section-kind pins → reader without pins.
2. Coach case C live nudges → C questions only at submit.
3. Sentence-link UI → recorded links from cards and Coach answers only. **Not allowed while L3b is off** (CEO-24).
4. Second backend live run → recorded fixtures only; live run before the gate.

**Never cut:**
- consent, the event log + verify + seal rule, origin marks and the mark check
- the leak check (incl. the adversarial set), the wording filter
- the "untraced is not AI" line, the student-linked band and labels
- export/delete, the seal-on-submit path (CEO-7), the release rule and cap
- the S3 gate, human sessions
- the route-enumeration test (D9)

## 4. Pilot gate (before any real student)

- [ ] Named teacher, class and **assignment window** agreed (CEO-12, OL-036)
- [ ] **The Writing Room approved by the university as a data processor**: DPA or PIA, IT security review, a signing entity (CEO-22)
- [ ] School approval for the chosen LLM provider; terms quoted in `docs/research/`; second backend available in HK (CEO-6, D14, OL-037)
- [ ] Hosting region and email provider named; backups in the same region
- [ ] Research-ethics approval if any survey or publication is planned (CEO-12, OL-026)
- [ ] Consent text finalised with the teacher (OL-016, CEO-20)
- [ ] An alternative submission route offered by the school
- [ ] Spikes: S1 (widened, with Python parity) and S5 passed; **S3 passed its bar, or L3b is off** (CEO-14, CEO-24)
- [ ] With L3b off: honest golden and human sessions don't come out as an untraced wall
- [ ] **Human sessions passed their stop rule** (CEO-18)
- [ ] Leak audit: zero leaks on golden **and adversarial** sets, both backends
- [ ] Wording filter test passes; a person has read all golden receipts
- [ ] Roster sign-in only; magic-link tests; route enumeration passes; CSP on; teacher audit on (D9, D11)
- [ ] LLM-down-at-submit test; release rule + cap test; 30-submits load test; replay fallback test
- [ ] Export and delete work end to end (incl. stored AI outputs)
- [ ] Backups and a restore test
- [ ] Monitoring: alerts fire in a drill; runbooks written (D15)
- [ ] Deploy freeze for the window agreed (D34)
- [ ] OL-043 answered well enough to finalise the pilot design

## 5. How each session should work (for agents)

- Pick the next unchecked task from the current milestone. Read its design doc section first. The design docs now include every CEO and eng decision; where a doc and this plan disagree, **this plan, then [eng-review-v1.md](../docs/designs/eng-review-v1.md), then [ceo-review-v1.md](../docs/designs/ceo-review-v1.md) win**.
- Write tests first where a doc gives a rule (bands, chain, seal, mark check, filter, policy routing).
- Use `ROOM_LLM=stub` in tests. Live LLM calls only in golden-session release runs.
- Don't change `shared/llm.py` behaviour; wrap it (D22).
- At the end, follow the session protocol in [CLAUDE.md](../CLAUDE.md) §6.
