# Handoffs

When a lead finishes a task, it writes one file here: `YYYY-MM-DD-T-0xx-short-name.md`. The checker reads it, runs the checks and either marks the task `done` in [../TASKS.md](../TASKS.md) or sends it back with the failing lines.

Leads never edit STATUS.md, TASKS.md statuses (except setting their own task to `in progress` / `review`), UPDATE_LOG.md, CHANGELOG.md or DECISIONS.md. The checker does that, so parallel conversations never collide on shared files.

## Cold-start pickup

Before starting, use [the ticket index](../tickets/README.md) and the live [task board](../TASKS.md). A handoff describes completed work; an execution ticket describes work still to do. Return branch/worktree, commit, ticket acceptance evidence, exact EXPECTATIONS lines covered, tests actually run and any pending human/founder gate. Codex is the planner/checker for the current wave.

## Template

```markdown
# T-0xx: <task name>

- **Lead:** <conversation tag>   **Workers used:** <Sonnet / DeepSeek / none>
- **Branch or worktree:** <name>   **Commit(s):** <sha>

## What changed
- <file>: <one line>

## Tests run (paste the command and the last lines of output)
- `ROOM_LLM=stub ...` → <N passed>

## EXPECTATIONS sections claimed
- A, C (lines 1–4), ...

## Not done / open
- <anything skipped, and why>

## Proposed decisions (the checker takes these to the founder; nothing here is decided)
- <none, or the question and the recommended answer>
```
