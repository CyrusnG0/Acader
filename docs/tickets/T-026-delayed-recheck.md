# T-026: Delayed state and scheduled release re-check

**Pickup:** ready. **Dependencies:** T-021 (done). Follow [pickup rules](README.md); the board is authoritative for current ownership. Branch: `task/T-026-delayed-recheck` from checker-accepted main. Claim only your row before coding. Touches `app/lifecycle.py` like T-025: the coordinator sequences them or the later branch rebases.

## Read first

AGENTS.md, docs/STATUS.md, docs/TASKS.md, EXPECTATIONS.md, docs/OPEN_LOOPS.md, PRODUCT.md, then these spec references (unqualified design filenames are in design/): docs/DECISIONS.md D-061, D-054, D-058; receipt.md §2a, §7; architecture.md §3; docs/handoffs/2026-10-25-T-021-release-withdrawal.md (PD-T021-2, PD-T021-3). Read the existing code and dependency handoffs; these tickets do not override the design specs.

## Scope and boundaries

Engine/jobs side only. Today, when the release job runs at the cap and no receipt exists, `_release_in_tx` writes a `release_no_receipt` operator alert, returns `no_receipt`, and nothing runs again; the teacher keeps seeing `compiling` with a past "Ready by" (D-061).

Build: (1) a `delayed` teacher status, returned by `teacher_view` when the cap has passed and nothing is released; it carries the cap time and nothing else (no receipt contents, summary, bands, question text or receipt id). (2) A scheduled re-check: after a `no_receipt` outcome, enqueue another release attempt for the same log and seal through the existing job queue (idempotent key per attempt), and also attempt release when a receipt is first issued after the cap; whichever comes first releases the latest receipt once, as `cap` kind, with questions pending if they are. (3) The operator alert is written once when the record first becomes delayed, not on every re-check. (4) Re-checks must stop after release and must not run forever: propose the interval and stop rule (suggested default: every 15 minutes, stop after a compile job for the log has permanently failed, with a second operator alert) as a proposed decision; do not invent product wording.

"Ready by" keeps showing the cap time (D-061, accepted as built). The cap never invents a receipt. Release stays out of the chain (D-058 (1)). The teacher-facing wording of the delayed state belongs to T-022; expose a status value and timestamps only. If T-025 has not landed, leave its withdrawal code alone.

## Required evidence

Frozen clock: cap passes with no receipt → `delayed` in the teacher view, one alert; receipt issued later → released once, then status `ready` or `questions pending`; re-check after release is a no-op; duplicate re-check jobs do not double-release; stop rule ends re-checks and alerts; no teacher payload while delayed; cross-log access rejected; app restart reconciles pending re-checks.

Run relevant new tests, full prototype tests with ROOM_LLM=stub, and the kit's 29 regression tests. Record actual environments and results; never claim unobserved CI. No secrets, real student data, live providers or shared/llm.py behavior changes.

Model: O+S.

Return commits, a dated docs/handoffs note, files changed, reproduction commands, EXPECTATIONS A plus the relevant C/H requirements, failures and proposed decisions. Set your own row to review. Only the checker merges, marks done and updates shared tracking. M1 human reading and every pilot gate remain separate; this ticket cannot satisfy them.
