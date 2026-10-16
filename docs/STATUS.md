# Current Status

**Last updated:** 2026-10-16 (CLEAR meeting delayed; Writing Room kit v0.2 experiment run, see writing-room-kit/RESULTS.md)
**Phase:** 0 done → **concierge viva pilot (pre-Phase 1) not started**; full Phase 1 deferred by D-011
**Code in repo:** `demo/` Room demo (DeepSeek; 12 tests + live API run + real-browser run passed) and `runner/` thin viva runner (FastAPI, 27 passing tests; real-LLM path untested, no API key yet)

## One-line state
The vision is complete and the lecture-mining core was validated in a prior session, but nobody outside the founder has been spoken to. The next work is instructor interviews and a hand-run viva (pilot plan APPROVED 2026-10-12), not the full Phase 1 build. The miner code is still missing from the repo (OL-002).

## What exists
| Area | State | Where |
|---|---|---|
| Product vision / spec / GTM / risks | Complete (v1) | [ultimate-proposal.md](../ultimate-proposal.md) |
| Visual lecture miner (M2) | **[VALIDATED]** in prior session: 159 board states from MIT 18.06 L1, ~0.3 s accuracy on synthetic ground truth | Algorithm documented in [design/lecture-miner.md](../design/lecture-miner.md). **Code missing from repo (OL-002)** |
| Architecture (M1–M11) | Designed at module level | [design/architecture.md](../design/architecture.md) |
| 3-layer data isolation (M7) | Designed | [design/data-isolation.md](../design/data-isolation.md) |
| Code-track MVP (M8) | Spec draft, many open choices | [design/code-track-mvp.md](../design/code-track-mvp.md) |
| Writing track (M9), Proof + dashboard (M10), LMS (M11) | Described in proposal only | proposal §4.4–4.6, §9 |
| Agent handoff docs | Set up | `CLAUDE.md`, `docs/` |

## Module board
| # | Module | Status |
|---|---|---|
| M1 | Ingest | not started (trivial) |
| M2 | Visual miner | **validated prototype; code not in repo** |
| M3 | Transcript (Whisper) | not started |
| M4 | Alignment (state ↔ speech) | not started |
| M5 | Topic structuring (LLM) | not started |
| M6 | QA watcher (VLM spot-checks) | not started |
| M7 | Course KG + isolation + mastery | designed, not built |
| M8 | Code track (variants + viva + no-paste editor) | deferred by D-011; thin viva runner first (pilot) |
| M9 | Writing track | not started |
| M10 | Proof + dashboard + parent layer | not started |
| M11 | LMS integrations | not started (with first pilots) |

## Next action (do this first)
**CLEAR meeting delayed (founder ill; new date not set).** Brief: [ultimate-proposal-v3.md](../ultimate-proposal-v3.md) (process-as-proof + teacher mirror; candidate direction D-023). v2 is superseded for Friday (its Meter-via-API and "proxy closed" claims failed fact-check).
1. **OL-023 before Friday:** check the Expo 2026 call deadline (expo-cfp@cuhk.edu.hk) and whether CLEAR runs course/teaching evaluations; put the miner code + v0.1 HTML on the laptop.
2. Show the `demo/` Room and a **labelled mock** of the teacher mirror (OL-024). Ask for one course pilot (v3 §7).
3. **Kit result to digest first:** [writing-room-kit/RESULTS.md](../writing-room-kit/RESULTS.md): after fixing the harness artifact (v0.3), the coherence receipt does not separate a retyped hybrid from honest work (92 vs 91); the conversation is the gate. Decide OL-027; build the question-gate test (OL-029).
4. After the meeting: confirm or drop D-023 (OL-022). If confirmed, rewrite CLAUDE.md §5 and the interview script for writing/teaching-centre targets.

Still open from before: the eng review's D13 was "interviews first", then T1–T12 before real students (OL-021); OL-013 interviews; OL-017 real-LLM runner check.

## Blockers
- No demand evidence, no known instructor workaround, no named user (OL-013, OL-014). This is the real blocker.
- OL-002: prototype code is not in this repo (now P1, not on the pilot's critical path).
