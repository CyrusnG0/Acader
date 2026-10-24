# Current Status

**Last updated:** 2026-10-24 (T-001, T-002, T-003, T-005 merged; CI green; D-035 → D-038 this week)
**Phase:** design finished and reviewed; **building starts with M0**. Work runs as one Opus lead per task, with Sonnet/DeepSeek workers, and one checker conversation (CLAUDE.md §8).
**Code in repo:**
- `writing-room-kit/`: simulated experiments v0.1–v0.5 and the hosted static demo (`web/`), **frozen**; 29 tests pass with `ROOM_LLM=stub` (run 2026-10-23)
- `shared/llm.py`: the DeepSeek client (wrap it, don't change it)
- `prototype/`: scaffold merged (T-001): server packages, `/healthz`, engine CLI stub, Vite + TS web; CI green on GitHub (Python 3.12, Node 22)
- `prototype/server/engine/events/`: hash chain, seal, post-seal whitelist, `verify` + CLI (spike S5: GO); 119 prototype tests pass
- `prototype/server/app/llm.py`: `complete(task, messages, schema)` wrapping `shared/llm.py`, 8 tasks incl. `map_suggest`, stub, five error classes, backend-2 slot, boot ping; Python deps locked in `prototype/requirements.lock` (D-040)
- `prototype/web/schema.json` + `src/schema.ts`: origin mark (6 kinds, closed list) and claim mark `{claim_id, by, suggestion_id?}`; 30 web tests
- Parked code: `archive/code-track/`

## Where we are going (one paragraph)
A writing platform where the process is the evidence. The student writes beside a **live map**: an outline of their own claims, cards and sources, wired both ways to their draft. The Coach asks one pillar question about each new idea (reading, logic, writing or communication), never about where the idea came from. The teacher gets a one-page receipt that shows where to ask, never a verdict. The **mapper** (a small model suggesting links on the map) is a flagged experiment that only turns on if its eval passes. First goal: one real class, after the pilot gate.

## What was decided this week
- **D-035:** the live map is the product; the model maps meaning, never trust.
- **D-036 (design review, 3/10 → 7/10):** [design/workspace.md](../design/workspace.md) (layout, states, access); receipt first screen, one-hue bands, P-15 withdrawal wording.
- **D-037 (eng review v2, clean):** the mapper is safe to build: chained events, pasted text can't enter the student-linked band, consent and flag fixed per record, eval with recall floor and hold-out; M4m after H; pilot tests the student-built outline.
- **D-038:** every new idea gets the same Coach treatment: one pillar question, never blocking.

## Next action (do this first)
**Leads:** T-001 is done. Ready now, in parallel: T-004 (S1) and T-006 (S2) are running as background leads; T-007…T-010 ready. T-001, T-002, T-003, T-005 done. T-004 waits for T-002. Pass [EXPECTATIONS.md](../EXPECTATIONS.md) and write a handoff.
**Founder:** F-001 (schedule option, build-plan §2a), F-002 (named teacher by 10-30), (F-005 approved, D-039; PD-1/PD-2 accepted, D-040).

## Where to read
- Product: [PRODUCT.md](../PRODUCT.md) §5–7
- Design: [design/README.md](../design/README.md) (all reviewed)
- Build plan: [design/build-plan.md](../design/build-plan.md) (≈ 35–36 build days; M4m off the pilot-gate path)
- Review records: [ceo-review-v1](designs/ceo-review-v1.md), [eng-review-v1](designs/eng-review-v1.md), [design-review-v1](designs/design-review-v1.md), [eng-review-v2](designs/eng-review-v2.md)

## Open
- The law 6 wording in D-031 still needs the founder's confirmation.
- DESIGN.md via /design-consultation before the receipt UI in M1 (T-010).
- No mockups yet: the designer needs an OpenAI key (F-004).
- The mapper's model is unnamed; the eval decides.

## P0 loops
- OL-036: no committed pilot class (deadline 10-30).
- OL-037: consent, provider terms, school approval.
- OL-026: ethics approval (pilot-gate item).
- OL-043: if guidance makes every trail look alike, what else estimates AI involvement?
- OL-035: closes after spike S5.
- OL-013 / OL-014: demand evidence and a named champion.

## Blockers
- No committed teacher or class (OL-036). Deadline 10-30.
- School, provider and processor approval; ethics approval if we survey (OL-037, OL-026, CEO-22).
