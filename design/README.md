# Design

Technical design documents. Product intent lives in [../ultimate-proposal.md](../ultimate-proposal.md). These docs turn it into buildable designs.
Status values: **validated** (prototyped and tested) · **designed** (agreed design, not built) · **draft** (proposal, open choices) · **stub**.

| Doc | Covers | Status | Last updated |
|---|---|---|---|
| [architecture.md](architecture.md) | System overview, modules M1–M11, data flow, phases | designed | 2026-10-11 |
| [lecture-miner.md](lecture-miner.md) | M2 visual board/slide miner algorithm and calibration lessons | **validated** (code not in repo, OL-002) | 2026-10-11 |
| [data-isolation.md](data-isolation.md) | L1/L2/L3 layers, ownership table, five cross-checks | designed | 2026-10-11 |
| [code-track-mvp.md](code-track-mvp.md) | Phase 1: variant engine, no-paste editor, line-level viva, defense record | draft | 2026-10-11 |

Pilot plan (current focus): [../docs/designs/concierge-viva-pilot.md](../docs/designs/concierge-viva-pilot.md), APPROVED 2026-10-12. It takes priority over the Phase 1 draft above.

Not yet written (add these when the work starts): `writing-track.md` (M9), `proof-of-understanding.md` (M10 Proof schema), `dashboard.md` (M10), `lms-integrations.md` (M11).

Rule: every design doc starts with a status line, links back to the proposal sections it implements, and lists its open loops by `OL-xxx`.
