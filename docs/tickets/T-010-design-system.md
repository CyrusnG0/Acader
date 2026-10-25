# T-010: resume and finalize the design system

**Current status (2026-10-25): checker-accepted done. Do not claim again.** The brief below is retained as the implementation contract/history; superseded pickup and approval gates are resolved by D-052 and the [checker review](../handoffs/2026-10-25-T-010-T-017-checker.md). T-017 does not complete the separate M1 human reading gate.


Ready for a new owner to resume. The prior codex-lead-T010 ownership has been released for pickup; the proposal work is preserved, not rejected or restarted.

## Starting point

Existing branch `task/T-010-design-system`, worktree `.claude/worktrees/codex-T010-design-system`, proposal commit `db6f0ab`. Inspect its status and integrate latest main before editing. Claim T-010 per the pickup rules. Read its existing handoff `docs/handoffs/2026-10-25-T-010-design-proposal.md` on that branch, the candidate, rationale and interactive preview.

Read AGENTS/STATUS/TASKS/EXPECTATIONS, design-review-v1.md 13A, design/workspace.md and design/receipt.md. Installed design-consultation skill was already applied; reuse its evidence rather than restarting preferences or generating a new design.

## Work

The prior continuation authorizes preparing the final handoff around the exact presented candidate. Promote `docs/designs/T-010-DESIGN.proposed.md` to root DESIGN.md unchanged: Source Sans 3 UI, Literata prose, existing light/dark tokens, focus/spacing/motion and patterned single-blue evidence bands. Any revision to those choices is a new proposal, not implicit approval. Do not edit CLAUDE.md or AGENTS.md or record a founder decision yourself. The checker verifies the approval trail before recording a locked decision.

Run `bun --no-env-file --config=/dev/null run ~/.claude/skills/gstack/bin/gstack-design-md.ts check DESIGN.md`; require DESIGN_MD_FORMAT: spec. Compare the final file with the candidate and run git diff --check. Existing preview checks cover light/dark, 1440/375 widths, keyboard/focus, contrast and print; rerun affected checks if anything changes and retain evidence. These checks do not establish production UI acceptance.

Update the existing dated handoff with final commit/files/checks, actual EXPECTATIONS A and G/H token coverage, and any remaining gate. Do not mark workspace functionality or M1 passed. Set T-010 review and return it to Codex. Only after checker acceptance/merge may T-017 start. No runtime changes, live calls, font substitution, external font requests in production or shared tracking edits by this lead.
