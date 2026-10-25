# Worker pickup tickets

Start with [AGENTS.md](../../AGENTS.md), [STATUS](../STATUS.md), [TASKS](../TASKS.md), [EXPECTATIONS](../../EXPECTATIONS.md) and [OPEN_LOOPS](../OPEN_LOOPS.md). Then read the ticket and the design sections it cites. Design docs remain authoritative; these tickets specify execution and review evidence.

## Claim one task

1. Choose **any unowned ready task** with every dependency done. Recommended critical-path pickup: T-010; T-007 and T-009 can run independently. An empty owner on a blocked task is not permission to start it. Founder tasks are not agent work.
2. Refresh the board and check active branches/worktrees before claiming. Set only your task's Owner to your conversation tag and Status to `in progress`; communicate the claim to the coordinator. Claims on separate branches are not a distributed lock: the coordinator must reconcile them before duplicate work starts.
3. Use `task/T-0xx-short-name` or its worktree. Never build on main. For T-010, resume the existing branch/worktree rather than discarding its proposal. Preserve the founder's untracked AGENTS.md and all other work.
4. Deliver the ticket's files and tests. Use ROOM_LLM=stub; no live model calls, secrets, real student data or unapproved product choices. If a design is ambiguous, document a proposed decision; progress on independent pieces.
5. Commit your work, write the dated handoff in docs/handoffs, and set only your task to `review`. Return branch/worktree, commit, handoff and check results to Codex for review. Never mark yourself done or merge.

The checker owns STATUS, UPDATE_LOG, CHANGELOG, OPEN_LOOPS and DECISIONS and accepts/returns the work. Do not edit another task's row. A task's human or founder gate cannot be fulfilled by a model.

## Tickets

| Ticket | Pickup | Output |
|---|---|---|
| [T-007](T-007-preregistration.md) | ready, independent | S3/S4 preregistration and labelling package |
| [T-009](T-009-walkthrough.md) | ready, independent | nursing walkthrough and blind-question protocol |
| [T-010](T-010-design-system.md) | ready to resume existing work | final design-system handoff |
| [T-017](T-017-receipt-ui.md) | blocked by checker-accepted T-010 | real golden receipt renderer and chain view |

Do not expand the later milestone waves into implementation tasks before the checker adds their dependencies and acceptance criteria.
