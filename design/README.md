# Design

How The Writing Room v1 is built. Product intent is in [../PRODUCT.md](../PRODUCT.md); decisions are in [../docs/DECISIONS.md](../docs/DECISIONS.md).
Status values: **validated** (tested) · **reviewed** (passed gstack review) · **draft** (written, open choices) · **stub**.

## Read in this order

| # | Doc | Covers | Status | Updated |
|---|---|---|---|---|
| 1 | [architecture.md](architecture.md) | Components, data flow, recommended stack, prototype layout, non-functional targets | reviewed (CEO + eng; eng v2 2026-10-24); D-041–D-046 | 2026-10-24 |
| 2 | [event-log.md](event-log.md) | Event envelope and types, origin marks, batching, hash chain, sealing, who reads what | reviewed (CEO + eng; eng v2 2026-10-24); D-041–D-046 | 2026-10-24 |
| 3 | [provenance.md](provenance.md) | Chains, the claim map model, pipeline layers L0–L3, claim-level comparison, bands, signal register | reviewed (CEO + eng; eng v2 2026-10-24); D-041–D-046; D-050 mechanics | 2026-10-25 |
| 4 | [receipt.md](receipt.md) | Receipt layout, submissions list, chain view, question selection, wording filter, JSON format, student preview, P-15, nursing example | reviewed (CEO + eng + design; eng v2); D-041–D-046 | 2026-10-24 |
| 4a | [workspace.md](workspace.md) | The student workspace and the live map: layout, map suggestions, states, trail toggle, widths, keyboard and screen readers | reviewed (design + eng v2); DESIGN.md approved D-052; D-041–D-046 | 2026-10-25 |
| 5 | [reading-aid.md](reading-aid.md) | Source origins, parsing into blocks, reading pins, reader actions, citation help | reviewed (CEO + eng; eng v2 2026-10-24); D-041–D-046 | 2026-10-24 |
| 6 | [coach-helper.md](coach-helper.md) | Helper vs Coach, policy modules, cases A–E, grounding, the Door, leak check, prompt hygiene | reviewed (CEO + eng; eng v2 2026-10-24); D-041–D-046 | 2026-10-24 |
| 7 | [privacy.md](privacy.md) | Data inventory, provider question, consent text, student rights, pilot security | reviewed (CEO + eng); provider terms + school approval before real students | 2026-10-23 |
| 8 | [evaluation.md](evaluation.md) | Spikes S1–S5, automated tests, golden receipts, pilot measures, nursing walkthrough | reviewed (CEO + eng; eng v2 2026-10-24) | 2026-10-24 |
| 9 | [build-plan.md](build-plan.md) | Milestones (re-baselined: engine + receipt + walkthrough ~11-08), cut lines, pilot gate | reviewed (CEO + eng; eng v2 2026-10-24) | 2026-10-25 |

Review records: [../docs/designs/ceo-review-v1.md](../docs/designs/ceo-review-v1.md) (CEO-1 to CEO-24) [../docs/designs/eng-review-v1.md](../docs/designs/eng-review-v1.md) (D1 to D35) [../docs/designs/design-review-v1.md](../docs/designs/design-review-v1.md) (1A to 20A, D-036) and [../docs/designs/eng-review-v2.md](../docs/designs/eng-review-v2.md) (D1 to D21, D-037). Every decision in them is now written into the docs above; there are no override boxes.

Presentation tokens: [DESIGN.md](../DESIGN.md), approved unchanged by the founder (D-052).

## Inputs these docs were built from

These are kept for history and review trails. Where they disagree with this folder, this folder wins.
- [../docs/designs/writing-platform-v1.md](../docs/designs/writing-platform-v1.md): product design draft (2026-10-22), now distilled into PRODUCT.md and receipt.md.
- [../docs/designs/provenance-engine.md](../docs/designs/provenance-engine.md): engineering draft (2026-10-22), now split into event-log.md, provenance.md, reading-aid.md and evaluation.md.
- [../docs/designs/process-evidence-room.md](../docs/designs/process-evidence-room.md): policy modules and claim lineage (2026-10-16), now in coach-helper.md.
- Earlier architecture, lecture miner, code track and data isolation: [../archive/design-v1/](../archive/design-v1/).

Rule: every design doc starts with a status line, names the decisions it implements, and lists its open loops by `OL-xxx`.
