# T-010: approved design system and review preview

- **Lead:** codex-lead-T010. **Workers:** root checker and independent browser QA worker reviewed the draft.
- **Branch/worktree:** `task/T-010-design-system`, `.claude/worktrees/codex-T010-design-system`, based on `c980c5d`.
- **Status:** founder approved the exact candidate with “A — Approve exact candidate”; approved content promoted unchanged to root DESIGN.md. Ready for checker review.
- **Integration:** latest main incorporated at `124496b`; current task links and other task states preserved. Proposal remains at `db6f0ab`; final promotion commit is the commit containing this updated handoff.

## What changed

- `DESIGN.md`: byte-for-byte copy of the founder-approved `docs/designs/T-010-DESIGN.proposed.md`; no token, font, copy or rationale edits.

- `docs/designs/T-010-design-proposal.md`: product-grounded rationale, familiar choices and deliberate departures, verified primary font references, light/dark contrast evidence, verification scope, and exact approval gate.
- `docs/designs/T-010-DESIGN.proposed.md`: complete normative candidate for root DESIGN.md, with the five token groups and usage rationale. It is a proposed artifact, not an authoritative design decision.
- `docs/designs/T-010-preview.html`: static synthetic teacher receipt, workspace and type/colour specimen, theme/view controls, responsive writing panels, print rules and keyboard examples. Current summary/question/counts use the actual `honest-nursing` golden receipt with teacher source registration from the checker correction. The draft and Coach question follow the same synthetic fixture. Fonts load only from the verified Google Fonts families in this preview; product implementation is proposed to self-host them.
- `docs/TASKS.md`: only T-010 ownership and review state; latest main’s ticket links and other task rows retained.

## Checks and evidence

Final-promotion checks, run after founder approval:

- **[VALIDATED]** `bun --no-env-file --config=/dev/null run ~/.claude/skills/gstack/bin/gstack-design-md.ts check DESIGN.md` → `DESIGN_MD_FORMAT: spec`, `DESIGN_MD_MARKER: spec`.
- **[VALIDATED]** `cmp DESIGN.md docs/designs/T-010-DESIGN.proposed.md` → exit 0; byte-identical.
- **[VALIDATED]** `shasum -a 256 DESIGN.md docs/designs/T-010-DESIGN.proposed.md` → both `08a1c28cf47d36610d8e1dc6c069665fd7572b603f1359cc8f51f50e20267d18`.
- **[VALIDATED]** `git diff --check` → exit 0.
- No runtime or preview changes in final promotion, so existing browser evidence below remains applicable; no application tests or browser checks were rerun for copying the approved document. The checker retains the main-line regression evidence.

Prior proposal/preview evidence retained:

- **[VALIDATED]** Official Google Fonts metadata and OFL 1.1 files read on 2026-10-25 for Source Sans 3 and Literata; exact primary URLs are in the proposal and candidate. No licence or availability claim relies on a font aggregator.
- **[VALIDATED]** sRGB/WCAG relative-luminance calculation for text/muted/accent/error against light/dark surface and paper. All proposed text combinations exceed 4.5:1; the light decorative hairline does not, so controls and untraced outlines use the separate high-contrast border role. Full table/method are in the proposal.
- **[VALIDATED]** `node --check /tmp/acader-T010-preview-script.js` passed for the extracted inline script; `git diff --check` passed.
- **[VALIDATED]** `bun --no-env-file --config=/dev/null run ~/.claude/skills/gstack/bin/gstack-design-md.ts check docs/designs/T-010-DESIGN.proposed.md` → `DESIGN_MD_FORMAT: spec`, `DESIGN_MD_MARKER: spec`.
- **[VALIDATED]** Independent local browser QA reported eight wide/narrow light/dark screenshots with no horizontal overflow and fonts loaded. Narrow view controls worked. It found dark-print contrast and hidden skip/focus targets; these were corrected and rechecked. Desktop F6 region cycling and chain-disclosure opening passed.
- **[VALIDATED]** Root visual review found the first-screen bars/disclaimer below the fold. Preview chrome was compacted, the stub caveat moved to the caption, and the full disclaimer moved directly below bars. Final browser measurement at 1440×900: full gloss ends at y=896.11, within the viewport; screenshot `/tmp/acader-T010-first-screen-1440x900.png` is held by the checker.
- No live LLM calls, image generation, production changes or real student data. Prototype/kit/web application code is unchanged by this task; the T-015 checker’s code regression results remain recorded separately.

## EXPECTATIONS coverage

- **A:** requested approved design file exists and matches the exact candidate. No secrets, shared-client changes, runtime dependencies or product-rule changes. Handoff contains actual format/parity/diff checks and prior browser evidence. Application code is unchanged; no claim of a new runtime test run. Checker owns shared tracking, decision recording and updating obsolete DESIGN.md-pending labels in design/README.md/workspace.md/build-plan.md as appropriate.
- **G/H (tokens):** approved system retains D-036 layout, motion, access and band semantics. Preview demonstrates these visual rules, but does not implement student/teacher application behavior, release permissions, persistence or the complete chain service.
- **I-M1:** no completion claim. All golden receipts still need the actual T-017 renderer and a person reading them.

## Skill routing / limitations

Read the installed `~/.claude/skills/design-consultation/SKILL.md` and its `sections/proposal-and-preview.md`. Product/use scene/locked decisions were supplied by the existing session and not re-asked. The parent authorized concrete proposal and HTML preview preparation before a single final approval request. No competitor/account browsing, paid image generation or external provider proposal was run.

The skill-start command reported `CHECK_FAILED gstack-update-check crashed ... update status UNKNOWN`; it eventually emitted interactive-session status but also reported that the session held no workflow lease. Unsupported setup, further external state writes and telemetry were not pursued. No installation or credential detours were taken.

## Approval received and next step

Founder explicitly replied **“A — Approve exact candidate”**. This satisfies the installed design-consultation skill's Phase 6 write gate for the exact candidate. Root DESIGN.md now contains that candidate unchanged. CLAUDE.md and AGENTS.md were not changed, per the founder's task scope.

No new product decisions or alternative design choices were introduced during promotion. The proposed-design artifacts remain historical review inputs; root DESIGN.md is the final file for checker acceptance. The checker records the approval decision and shared status, verifies the final commit and merges. T-010 is `review`, not `done`.

T-017 has not been started. Only checker acceptance/merge may unblock it. M1 still requires the real receipt renderer and a person reading at least ten golden receipts; the visual proposal does not satisfy that production gate.
