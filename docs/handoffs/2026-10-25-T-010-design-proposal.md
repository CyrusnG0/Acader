# T-010: proposed design system and review preview

- **Lead:** codex-lead-T010. **Workers:** root checker and independent browser QA worker reviewed the draft.
- **Branch/worktree:** `task/T-010-design-system`, `.claude/worktrees/codex-T010-design-system`, based on `c980c5d`.
- **Status:** proposal prepared; founder approval and final DESIGN.md remain outstanding. No commits by this lead.

## What changed

- `docs/designs/T-010-design-proposal.md`: product-grounded rationale, familiar choices and deliberate departures, verified primary font references, light/dark contrast evidence, verification scope, and exact approval gate.
- `docs/designs/T-010-DESIGN.proposed.md`: complete normative candidate for root DESIGN.md, with the five token groups and usage rationale. It is a proposed artifact, not an authoritative design decision.
- `docs/designs/T-010-preview.html`: static synthetic teacher receipt, workspace and type/colour specimen, theme/view controls, responsive writing panels, print rules and keyboard examples. Current summary/question/counts use the actual `honest-nursing` golden receipt with teacher source registration from the checker correction. The draft and Coach question follow the same synthetic fixture. Fonts load only from the verified Google Fonts families in this preview; product implementation is proposed to self-host them.
- `docs/TASKS.md`: only T-010 owner and in-progress state.

## Checks and evidence

- **[VALIDATED]** Official Google Fonts metadata and OFL 1.1 files read on 2026-10-25 for Source Sans 3 and Literata; exact primary URLs are in the proposal and candidate. No licence or availability claim relies on a font aggregator.
- **[VALIDATED]** sRGB/WCAG relative-luminance calculation for text/muted/accent/error against light/dark surface and paper. All proposed text combinations exceed 4.5:1; the light decorative hairline does not, so controls and untraced outlines use the separate high-contrast border role. Full table/method are in the proposal.
- **[VALIDATED]** `node --check /tmp/acader-T010-preview-script.js` passed for the extracted inline script; `git diff --check` passed.
- **[VALIDATED]** `bun --no-env-file --config=/dev/null run ~/.claude/skills/gstack/bin/gstack-design-md.ts check docs/designs/T-010-DESIGN.proposed.md` → `DESIGN_MD_FORMAT: spec`, `DESIGN_MD_MARKER: spec`.
- **[VALIDATED]** Independent local browser QA reported eight wide/narrow light/dark screenshots with no horizontal overflow and fonts loaded. Narrow view controls worked. It found dark-print contrast and hidden skip/focus targets; these were corrected and rechecked. Desktop F6 region cycling and chain-disclosure opening passed.
- **[VALIDATED]** Root visual review found the first-screen bars/disclaimer below the fold. Preview chrome was compacted, the stub caveat moved to the caption, and the full disclaimer moved directly below bars. Final browser measurement at 1440×900: full gloss ends at y=896.11, within the viewport; screenshot `/tmp/acader-T010-first-screen-1440x900.png` is held by the checker.
- No live LLM calls, image generation, production changes or real student data. Prototype/kit/web application code is unchanged by this task; the T-015 checker’s code regression results remain recorded separately.

## EXPECTATIONS coverage

- **A (partial):** authorized proposal scope only; no secrets, shared-client changes, runtime dependencies or product rules. Handoff and static/browser checks exist. This task is not done because approved root DESIGN.md is absent.
- **G/H (proposed tokens):** candidate retains D-036 layout, motion, access and band semantics. Preview demonstrates these visual rules, but does not implement student/teacher application behavior, release permissions, persistence or the complete chain service.
- **I-M1:** no completion claim. All golden receipts still need the actual T-017 renderer and a person reading them.

## Skill routing / limitations

Read the installed `~/.claude/skills/design-consultation/SKILL.md` and its `sections/proposal-and-preview.md`. Product/use scene/locked decisions were supplied by the existing session and not re-asked. The parent authorized concrete proposal and HTML preview preparation before a single final approval request. No competitor/account browsing, paid image generation or external provider proposal was run.

The skill-start command reported `CHECK_FAILED gstack-update-check crashed ... update status UNKNOWN`; it eventually emitted interactive-session status but also reported that the session held no workflow lease. Unsupported setup, further external state writes and telemetry were not pursued. No installation or credential detours were taken.

## Proposed decision and next step

Approve or revise the exact proposed DESIGN.md plus its matching preview. No final root DESIGN.md or CLAUDE.md/AGENTS.md edit has been made. The installed skill's Phase 6 says: **“Wait. Only A permits the writes below; B/C leave project files untouched.”** The exact candidate is ready so founder approval can be the final gate. The task remains in progress until that approval and final-file promotion/checker review.

After approval, promote the candidate to root DESIGN.md, record the founder decision through the checker, and unlock T-017. Do not treat agent selection of the typefaces as founder approval.
