# Worker pickup tickets

Start with [AGENTS.md](../../AGENTS.md), [STATUS](../STATUS.md), [TASKS](../TASKS.md), [EXPECTATIONS](../../EXPECTATIONS.md) and [OPEN_LOOPS](../OPEN_LOOPS.md). Then read the ticket and the design sections it cites. Design docs remain authoritative; these tickets specify execution and review evidence.

## Claim one task

1. Choose **any unowned ready task** with every dependency done. Recommended pickup: T-025, then T-026; T-027 can run in parallel. An empty owner on a blocked task is not permission to start it. Founder tasks are not agent work.
2. Refresh the board and check active branches/worktrees before claiming. Set only your task's Owner to your conversation tag and Status to `in progress`; communicate the claim to the coordinator. Claims on separate branches are not a distributed lock: the coordinator must reconcile them before duplicate work starts.
3. Use `task/T-0xx-short-name` or its worktree. Never build on main. T-010 and T-017 are checker-accepted; do not reopen their implementation. Preserve the founder's untracked AGENTS.md and all other work.
4. Deliver the ticket's files and tests. Use ROOM_LLM=stub; no live model calls, secrets, real student data or unapproved product choices. If a design is ambiguous, document a proposed decision; progress on independent pieces.
5. Commit your work, write the dated handoff in docs/handoffs, and set only your task to `review`. Return branch/worktree, commit, handoff and check results to Codex for review. Never mark yourself done or merge.

The checker owns STATUS, UPDATE_LOG, CHANGELOG, OPEN_LOOPS and DECISIONS and accepts/returns the work. Do not edit another task's row. A task's human or founder gate cannot be fulfilled by a model.

## Tickets

| Ticket | Pickup | Output |
|---|---|---|
| [T-007](T-007-preregistration.md) | done | S3/S4 preregistration and labelling package |
| [T-009](T-009-walkthrough.md) | done | nursing walkthrough and blind-question protocol |
| [T-010](T-010-design-system.md) | done | approved DESIGN.md |
| [T-017](T-017-receipt-ui.md) | done; human M1 gate open | real golden receipt renderer and chain view |

Do not expand the later milestone waves into implementation tasks before the checker adds their dependencies and acceptance criteria.

- [T-018: Durable receipts and AI artifacts](T-018-receipt-storage.md) — done.
- [T-019: Bounded durable job queue](T-019-job-queue.md) — done.
- [T-020: Submit and compile orchestration](T-020-compile-jobs.md) — done (includes the D-054 retry cap).
- [T-021: Release cap and transactional withdrawal](T-021-release-withdrawal.md) — done (withdrawal reversed by D-062).
- [T-022: Student preview and teacher lifecycle views](T-022-receipt-preview.md) — ready (D-059, D-061, D-062).
- [T-023: Executable preregistered S3 evaluation harness](T-023-s3-harness.md) — blocked.
- [T-024: Drop "Written on N days"](T-024-drop-written-days.md) — done (D-055).
- [T-025: Remove student withdrawal](T-025-remove-withdrawal.md) — ready (D-062).
- [T-026: Delayed state and scheduled release re-check](T-026-delayed-recheck.md) — ready (D-061).
- [T-027: "More places to ask"](T-027-more-places.md) — ready (D-060).

T-025, T-026 and T-022 all touch `app/lifecycle.py`: run them in that order or rebase the later branch. T-027 may run in parallel; coordinate with T-022 on the teacher receipt view. Blocked tickets are not empty work slots.
