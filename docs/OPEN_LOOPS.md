# Open Loops

Unresolved questions, blockers and TODOs. IDs are permanent and never reused.
Priority: **P0** blocks progress · **P1** needed for Phase 1 · **P2** later phases.
When resolving a loop, move it to **Closed** with the date and the resolution. If it produced a decision, add it to [DECISIONS.md](DECISIONS.md).

## Open

| ID | Pri | Type | Loop | Context / next step | Source |
|---|---|---|---|---|---|
| OL-027 | **P0** | decision | **Decide whether "gate the input" (clear-meeting-master-brief.md) becomes a decision, in light of writing-room-kit/RESULTS.md** | Kit result (v0.2 + v0.3 repair): the coherence receipt separates no-engagement but NOT retyped-hybrid work (composite 92 vs 91; AUC 0.33). Supports "the conversation is the gate". Log a D-xxx once the CLEAR meeting (delayed; founder ill) has happened. |
| OL-029 | P1 | research | **Test the real gate: claim-anchored questions from each run's essay, answered by a responder who sees only the trail** | The experiment CLEAR would care about; kit v0.2 only tested the receipt. |
| OL-030 | P2 | build | **Add hinge documents + question budget to the kit engine** | Master brief §5–§7. Note the tension with law 3 (assessed tasks only; practice unlimited). |
| OL-022 | **P0** | decision | **Confirm or drop D-023 (process-as-proof + teacher mirror) after CLEAR, 2026-10-16** | If confirmed: rewrite CLAUDE.md §5, interview script, design index; decide what happens to the code-first viva pilot (D-011). | D-023 |
| OL-023 | **P0** | verify | **Before Friday: Expo 2026 call deadline, and whether CLEAR runs CUHK's course and teaching evaluations** | 2024 call closed Oct 28; email expo-cfp@cuhk.edu.hk. The CTE link is an [ASSUMPTION] in v3 §4. Also bring the miner code + v0.1 HTML on the laptop (OL-002). | v3 review |
| OL-024 | P1 | design | **Teacher mirror: signals, privacy floor, ownership** | Mock for Friday (labelled). Then define signals, k≥5 group floor, teacher-owned sharing, and how misconceptions link to mined lecture timestamps. | D-023 |
| OL-025 | P1 | design | **Stage boundary rule and AIAS dial** | Turn v3 §2 table into a spec: which requests are retrieval/mechanics vs claim/synthesis, per AIAS level; how fact errors are raised openly. | D-023 |
| OL-026 | P1 | research | **Pilot ethics + validity design** | Ask CLEAR about ethics approval if results go to the Expo; design the platform-vs-5-min-TA-oral agreement check and the 50-vs-50 blind question rating. | v3 §7 |
| OL-017 | **P0** | verify | **Runner's real-LLM path is untested** | No API key was available when built. Set the key, run on a real assignment, check question quality, JSON compliance and the retry path; test the pages in a real browser. | D-015 |
| OL-018 | P1 | tech | **Demo gaps vs proposal** | Not in demo: live DOI/Crossref citation verification, lecture mining feeding the rooms, code track in the Room, school dashboard, LMS, accounts/multi-user. Decide which (if any) matter after the first instructor conversations. | D-016 |
| OL-019 | P1 | privacy | **Confirm Anthropic API data terms + HK PDPO** | Replace the [ASSUMPTION] line in docs/outreach-data-note.md with a quoted term; check PDPO and each university's data-transfer rules. | D-021 |
| OL-020 | P1 | research | **Verify or remove "Prova" and "Professr"** | Not found in 2026-10 research; proposal section 6 marks them unverified. | market-research review T3 |
| OL-021 | P1 | build | **Implement eng-review tasks T1 to T12** | See docs/designs/eng-review-runner-demo.md (Implementation Tasks, 3 parallel lanes). Gate: do not host the runner for real students before T1 (provider errors), T2 (retention), T3 (limits), T4 (tokens). Demo may be shown by screen share meanwhile. | D-022 |
| OL-013 | **P0** | research | **Instructors' real workaround is unknown** | Target mix (D-019): 3 Hong Kong university CS/engineering instructors or FYP supervisors + 2 remote instructors (US/UK/AU) for comparison. Script: docs/interview-script.md. Email 5 reachable CS lecturers/FYP supervisors: "What did you do last semester when you suspected a student's code was AI-written?" Record answers verbatim. Build nothing until 2 answers are on paper. | D-011 |
| OL-014 | **P0** | business | **No named user or champion** | Book one instructor to run a real assignment through a hand-run viva. Also learn who feels the pain vs who pays (TA, lecturer, FYP supervisor, dept head). | office-hours Q3 |
| OL-015 | P1 | experiment | **Graph vs pasted-notes blind test** | Design in docs/designs/concierge-viva-pilot.md. Needs instructor lecture notes and a hand-structured stand-in. Pass bar 6 of 10. | D-012 |
| OL-016 | P1 | design | **Consent note + retention text for pilot students** | Write plain-language note (LLM provider, what is stored, who sees it, opt-out, 30-day delete, export); get instructor sign-off. | D-014 |
| OL-002 | P1 | blocker (demoted by D-011) | **Prototype code is not in the repo** | `lecture_miner.py`, `make_sheet.py`, `gen_synth.py`, `strang_out/states.csv` and the contact sheets were built in the prior session. Ask the user for them and commit them under `miner/`. If they are lost, rebuild from [design/lecture-miner.md](../design/lecture-miner.md). | init audit |
| OL-003 | P2 | experiment (demoted by D-011) | **Variant-engine quality bar** | Generate 3 isomorphic variants from one real reference solution and grade difficulty parity. Define a parity rubric (concept coverage, LOC, number of functions, test difficulty). This is the riskiest Phase 1 assumption. | proposal §12.2 |
| OL-005 | P1 | business | **First design partner**: FYP department (university) or a hero teacher (secondary)? Phase 1 also needs a CS course with lecture videos and an assignment. | Phase 1 acceptance needs a real assignment completed by non-founders. | proposal §12.4 |
| OL-008 | P1 | tech | **App stack for the full product not chosen** (pilot runner uses Python/FastAPI + plain HTML + Claude API, D-015) (Room editor, backend, KG store, LLM provider, hosting) | Needs a decision before Phase 1 implementation. Editor must support blocking paste and keystroke timelines (e.g. Monaco/CodeMirror). KG store options: Postgres + pgvector or a graph DB. | init audit |
| OL-009 | P1 | design | **Line-level viva trigger policy**: which lines are "key lines", how often to stop the student, and how answers are graded | Draft heuristics in [design/code-track-mvp.md](../design/code-track-mvp.md) §4. Needs a prototype. | proposal §4.3 |
| OL-010 | P1 | design | **Comprehension tier thresholds** (Strong / Partial / Oral-verified) and the evidence schema behind them | Must stay formative and human-decided. | proposal §3.10, §4.5 |
| OL-004 | P2 | tech | **Citation backend first**: Scite Smart Citations, or Crossref + Semantic Scholar directly | Phase 2 (writing track). | proposal §12.3 |
| OL-001 | P2 | brand | **Product name + domain** (repo is "Acader", which is a working name only) | Brand voice is locked (proposal §11). Only the name is open. | proposal §12.1 |
| OL-006 | P2 | business | **Pricing calibration**: per-student/year band per segment, plus FYP cohort pricing | | proposal §12.5 |
| OL-007 | P2 | legal | **EU AI Act classification review** before the first EU pilot | Education is a high-risk category. Keep features formative with a human in the loop. | proposal §12.6 |
| OL-011 | P2 | tech | **Miner production gaps**: semantic-clustering pass over the fine-grained state "ladders", sub-8 s board re-appearances being missed, title cards needing VLM QA | See [design/lecture-miner.md](../design/lecture-miner.md) §5. | proposal §8.8 |
| OL-012 | P2 | metrics | **Outcome measurement design** from day one: pre/post concept tests, viva pass rates, in-cohort student NPS | Follows the Harvard-RCT marketing playbook. | proposal §7, §10 |

## Closed

| ID | Closed | Resolution |
|---|---|---|
| OL-028 | 2026-10-16 | Kit harness artifact fixed (citation cap 6 to 12) and A3/A4 re-run (PREREG-v0.3.md). Result: retyped hybrid scores 92 vs honest 91; primary AUC 0.33. Receipt does not separate them. See writing-room-kit/RESULTS.md. |
| (none yet) | | |
