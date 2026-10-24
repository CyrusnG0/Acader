# Design review v1: the live-map workspace and the receipt

/plan-design-review, 2026-10-24, branch `main` at `b4f4bc7` (uncommitted docs). Reviewer: Claude (Opus 5.5) with one independent Opus subagent as the outside voice (Codex skipped: auth). Decisions locked as **D-036**.

**Scope (chosen by the founder):** the student workspace with the live map as its centre (D-035), the teacher receipt as its snapshot, the student preview, and P-15. All 7 passes.

## System audit

- **UI scope:** the student workspace (reader, editor, cards, live map, Coach/Helper panel, Door) and the teacher surfaces (submissions list, receipt, chain view), plus the student preview.
- **DESIGN.md:** none. The only tokens are in `writing-room-kit/web/static/demo.html`. That is now a build-plan gate (13A).
- **Prior design reviews:** none.
- **Conflict found:** D-035 says "the live map is the product", while PRODUCT.md §7 and TODOS #7 ship a claim list. Settled by 1A.
- **Mockups:** the gstack designer is installed, but generation failed with "No OpenAI API key found" (`~/.gstack/openai.json` has no usable key). Text-only review. Run `$D setup` and regenerate before M3.

## Step 0

Initial rating **3/10**. The receipt was fairly well specified (about 7/10 on its own). The workspace, now the product, had only a component list. Focus: all 7 passes (D1).

## Outside voice (D2: Opus subagent; Codex skipped)

There were 12 findings, three of them critical: the workspace had no layout; three link names looked almost the same; the demo's ok/warn/bad tokens invited a verdict colouring. All 12 were raised in the passes below and decided, except where noted.

```
LITMUS                      Opus subagent                     Codex
1 Product clear 1st screen  NOT SPEC'D → layout set (1A)       unavailable
2 One visual anchor         NOT SPEC'D → editor (1A)           unavailable
3 Scannable by headings     YES receipt / NOT SPEC'D workspace unavailable
4 One job per section       NO → receipt details folded (2A)   unavailable
5 Cards necessary           objects yes, layout no (10A)       unavailable
6 Motion helps hierarchy    NOT SPEC'D → one motion (11A)      unavailable
7 Premium without shadows   flat tokens; locked (10A)          unavailable
Hard rejections (pre-emptive): receipt as stacked .box cards; workspace as a panel grid → both rejected by 10A
```

## Decisions (one question each, all answered)

| # | Pass | Issue | Decision | Written into |
|---|---|---|---|---|
| 1A | 1 IA | Workspace layout; what "map" means in v1 | Editor centre (~50%), live map as a left outline with a two-way claim↔sentence highlight, Coach/Helper on the right, the reader replaces the map rail, the Door in the top bar. v1 map = outline. | workspace.md §1 |
| 2A | 1 IA | Receipt first screen | Header (no hash), summary, Where to ask, bars + blind-spot line. Items 5–9 go under "How it was built (details)". Seal and verify go to "About this receipt". | receipt.md §2, §3 |
| 3A | 1 IA | Teacher submissions list | Alphabetical; name, submitted, status only. No band columns, no sort or filter by band. "Mark as discussed". | receipt.md §2a |
| 4A | 2 States | Three similar link names | "checked against the source" (L3b) · "linked by the student, not checked" · "suggested by the map, not checked" (student only). Map suggestions never reach the bars or the chain; only a count appears. | receipt.md §3, §6; workspace.md §2; provenance.md; PRODUCT.md §5; GLOSSARY |
| 5A | 2 States | Mapper suggestion behaviour | The student confirms ("Yes, link it" → student-linked, never traced) or rejects ("Not this" → logged, never on the receipt). The student's own link wins. A quiet pending line. Silent when the mapper is down. Suggestions expire at submit. | workspace.md §2 |
| 6A | 2 States | Workspace and submit states | Full state table: empty map → "Make a card", offline, lease lost, card failure, Door cap, the sealed screen with release time, "Still compiling. Ready by [time]". | workspace.md §3; receipt.md §7 |
| 7A | 3 Journey | Live trail in the editor | Off by default. A "Show my trail" toggle (remembered; labelled provisional). "needs a source" on the map is the only cue that is always on. | workspace.md §4 |
| 8A | 3 Journey | Student preview | The same order as the teacher. "Nothing here is a grade." "Be ready to explain your thinking" per span, with note and link actions. A release-time footer. | receipt.md §7 |
| 9A | 3 Journey | P-15 withdrawal between submit and release | Allowed. Plain confirm text for the student. Teacher sees status `record removed` and a neutral notice with no seal, bars or questions. Edits after submit are never part of the submission. | receipt.md §7; privacy.md §5; event-log.md |
| 10A | 4 Slop | Cards versus layout | The receipt is one 72ch column with hairline-ruled sections, print-first. The workspace is three hairline-split columns. Card shapes are used only for idea cards and the Coach question. | receipt.md §6; workspace.md §1 |
| 11A | 4 Slop | Motion | Only the student-triggered highlight fades in (150 ms ease-out; instant under reduced-motion). Nothing the system adds animates, pulses or makes a sound. | workspace.md §1; coach-helper.md §3 |
| 12A | 5 System | Band colours | One hue at falling strength plus patterns and labels. Untraced is an outline only. ok/warn/bad are banned from bands, the chain and the trail. | receipt.md §2 |
| 13A | 5 System | No DESIGN.md; system-ui type | Run /design-consultation before the receipt UI (M1) and M3. Interim: demo tokens plus the rules in this review. | build-plan.md |
| 14A | 6 Resp/a11y | Narrow widths | ≥1280: three columns. 900–1279: drawers. Receipt is one 72ch column everywhere. | workspace.md §5 |
| 15A | 6 Resp/a11y | 14A blocked zoomed-in writers (WCAG 1.4.10) | Below 900px: a one-column writing mode with full-screen map, Coach and reader views. Writing is never blocked. | workspace.md §5 |
| 16A | 6 Resp/a11y | Keyboard and screen reader | Landmarks, F6 region cycle, skip link. The map is a tree with focused y/n. Suggestions and questions are never announced live; counts appear in region names. 44/24 px targets, 4.5:1 contrast, a 2 px focus ring. | workspace.md §6 |
| 17A | 7 Decisions | Mapper questions and the Coach budget | One budget. Mapper findings are Coach candidates after cases B and C. Unasked findings may feed the receipt's questions. | coach-helper.md §3 |
| 18A | 7 Decisions | Coach case C copy | Map-shaped invitations ("¶4 isn't connected to your map yet. Which claim is it making?"). Never "untraced" or "flag" in Coach copy. | coach-helper.md §3 |
| 19A | 7 Decisions | Wording filter scope | Every rendered string on every surface. "flag/flags/flagged" banned everywhere. "Untraced" shown to students only with its gloss. | receipt.md §5 |
| 20A | 7 Decisions | Chain view wording | Plain, rounded break labels ("about half reworded since", "this label couldn't be confirmed against its source"). Exact figures stay in the JSON and export only. | receipt.md §3; provenance.md; eng test plan |

## Journey storyboard (after the decisions)

```
STEP | USER DOES                         | USER FEELS                 | PLAN SPECIFIES
1    | Student opens invite, consents    | wary                       | privacy notice (D11)
2    | First workspace, empty map        | knows where to start       | 6A "Make a card"
3    | Reads, makes first card           | relief                     | reading-aid §5
4    | Writes; map grows; suggestions    | guided, not watched        | 1A, 5A, 7A, 11A
5    | Coach question appears            | curious, not accused       | 17A budget, 18A copy
6    | Submits, sealed                   | knows what happens next    | 6A sealed screen
7    | Student preview                   | prepared                   | 8A
8    | Teacher: list → receipt           | gets the gist in seconds   | 3A, 2A
9    | Teacher asks 2 questions          | fair                       | receipt §4
10   | Teacher marks discussed           | done                       | 3A
11   | Student withdraws (P-15)          | in control; teacher clear  | 9A
```

## NOT in scope

- **Visual mockups:** blocked by the missing OpenAI key. Regenerate once `$D setup` is done, before M3.
- **Typefaces, type scale, spacing, dark mode:** deferred to /design-consultation by the founder's choice (13A). This is a build-plan gate.
- **Claim map graph view:** stays deferred (TODOS #7). The outline carries the same data (1A).
- **Teacher-side assignment setup screens** (roster, readings upload): covered by the eng test plan's states (parse status). Not reviewed for layout here.
- **Folding the mapper into the engine docs** (provenance layer, evaluation golden set, architecture job): OL-044. This review settled the screen side only.

## What already exists

- **demo.html tokens:** the paper background, one accent, ink and muted text, hairline lines, a dark-mode set, no shadows. These are the interim palette. `.box` cards are not reused (10A).
- **receipt.md §2 order** and the blind-spot line next to the bars, kept and tightened (2A).
- **WCAG 2.2 AA, no drag-only actions, no timers** (architecture.md). Extended by 15A and 16A.
- **Coach budget and outcomes** (coach-helper.md §3). Extended by 17A.
- **Error copy already specified:** "AI help unavailable", "Question not ready", the scan message, "edit here instead". These are reused in the 6A table.

## TODOS.md updates

None proposed. Every approved fix is in the plan docs or the build-plan gate. Remaining design debt is either already a TODO (graph view, #7) or a gate (DESIGN.md, 13A).

## Implementation Tasks

Synthesized from this review's findings. Each task derives from a specific finding above.

- [ ] **T1 (P1, human: ~1 day / CC: ~30 min)**: design system. Run /design-consultation and write DESIGN.md before the receipt UI.
  - Surfaced by: Pass 5, 13A
  - Files: DESIGN.md, design/build-plan.md
  - Verify: DESIGN.md exists and the receipt and workspace CSS use only its tokens
- [ ] **T2 (P1, human: ~2 days / CC: ~1 h)**: workspace shell. Build the 3-column / drawer / one-column layout with the two-way highlight.
  - Surfaced by: Passes 1 and 6, 1A, 10A, 11A, 14A, 15A
  - Files: prototype/web/map/, prototype/web/editor/
  - Verify: Playwright at 1440, 1024 and 375 px and at 200% and 400% zoom; axe clean
- [ ] **T3 (P1, human: ~1 day / CC: ~30 min)**: map suggestions. Build the suggestion row, Yes/Not this, the `map.suggestion_rejected` event, the student-wins rule and expiry at submit.
  - Surfaced by: Pass 2, 4A, 5A
  - Files: prototype/web/map/, prototype/server/engine/
  - Verify: a golden session with an accepted suggestion → band 4, never traced; a rejected one is absent from the receipt
- [ ] **T4 (P1, human: ~1 day / CC: ~30 min)**: states. Implement every string in the workspace.md §3 table and the receipt's "Still compiling. Ready by [time]".
  - Surfaced by: Pass 2, 6A
  - Files: prototype/web/*
  - Verify: one Playwright test per row (empty, offline, lease lost, card failure, Door cap, sealed)
- [ ] **T5 (P1, human: ~1 day / CC: ~30 min)**: receipt layout. Build the 4-part first screen, the details disclosure, the seal in About, the one-hue band scale with patterns, and print CSS.
  - Surfaced by: Passes 1, 4 and 5; 2A, 10A, 12A
  - Files: prototype/web/receipt/
  - Verify: golden receipts render; greyscale print shows the bands as distinct
- [ ] **T6 (P1, human: ~4 h / CC: ~15 min)**: submissions list. Alphabetical, status only, "Mark as discussed".
  - Surfaced by: Pass 1, 3A
  - Files: prototype/web/receipt/, prototype/server/
  - Verify: test asserts there is no band field in the list API
- [ ] **T7 (P1, human: ~4 h / CC: ~15 min)**: student preview and P-15. Build the preview layout and the withdrawal confirm with the teacher notice.
  - Surfaced by: Pass 3, 8A, 9A
  - Files: prototype/web/receipt/, prototype/server/
  - Verify: a golden withdrawal session shows `record removed` and none of the seal, bars or questions
- [ ] **T8 (P1, human: ~4 h / CC: ~15 min)**: wording filter. Run it on every rendered string, ban flag/flags/flagged, require the gloss with "untraced", and use the chain labels and case C copy.
  - Surfaced by: Pass 7, 18A, 19A, 20A
  - Files: prototype/server/receipt/wording.py, prototype/server/coach/
  - Verify: a unit test over all UI string tables and golden outputs
- [ ] **T9 (P2, human: ~4 h / CC: ~15 min)**: the trail toggle. "Show my trail", remembered, with the provisional line.
  - Surfaced by: Pass 3, 7A
  - Files: prototype/web/editor/
  - Verify: off by default; on paints the 12A scale
- [ ] **T10 (P1, human: ~4 h / CC: ~15 min)**: keyboard and screen readers. Landmarks, F6, the map tree, focused y/n, quiet counts.
  - Surfaced by: Pass 6, 16A
  - Files: prototype/web/*
  - Verify: an axe check plus a manual VoiceOver pass; no live-region announcement on a new suggestion
- [ ] **T11 (P2, human: ~2 h / CC: ~10 min)**: Coach budget. Mapper findings join the Coach queue under one cap.
  - Surfaced by: Pass 7, 17A
  - Files: prototype/server/coach/
  - Verify: a stub test shows no more than 1 question per 10 min and 6 per assignment with mapper findings present

## Design Review Completion Summary

```
  +====================================================================+
  |         DESIGN PLAN REVIEW — COMPLETION SUMMARY                    |
  +====================================================================+
  | System Audit         | no DESIGN.md; UI scope = workspace + receipt |
  | Step 0               | 3/10; all 7 passes                          |
  | Pass 1  (Info Arch)  | 3/10 → 9/10 after fixes                     |
  | Pass 2  (States)     | 3/10 → 8/10 after fixes                     |
  | Pass 3  (Journey)    | 4/10 → 9/10 after fixes                     |
  | Pass 4  (AI Slop)    | 5/10 → 8/10 after fixes                     |
  | Pass 5  (Design Sys) | 3/10 → 7/10 after fixes                     |
  | Pass 6  (Responsive) | 4/10 → 9/10 after fixes                     |
  | Pass 7  (Decisions)  | 4 resolved, 0 deferred                      |
  +--------------------------------------------------------------------+
  | NOT in scope         | written (5 items)                           |
  | What already exists  | written                                     |
  | TODOS.md updates     | 0 items proposed                            |
  | Approved Mockups     | 0 generated (no OpenAI key), 0 approved     |
  | Decisions made       | 20 added to plan                            |
  | Decisions deferred   | 0                                           |
  | Overall design score | 3/10 → 7/10                                 |
  +====================================================================+
```

Why the remaining scores are below 10:
- **Pass 5 is at 7:** there is no DESIGN.md until /design-consultation (the founder's choice, 13A).
- **Passes 2 and 4 are at 8:** nothing has been seen as pixels yet (no mockups), and the typeface is open.
- **Passes 1, 3 and 6 are at 9:** they need checking against real screens.

### Unresolved Decisions

None. Every finding got its own question and an answer.

## GSTACK REVIEW REPORT

| Review | Trigger | Why | Runs | Status | Findings |
|--------|---------|-----|------|--------|----------|
| CEO Review | `/plan-ceo-review` | Scope & strategy | 3 | clean (2026-10-22) | mode: SCOPE_REDUCTION, 0 critical gaps |
| Outside Review | Opus subagent (Codex skipped or auth failed) | Independent 2nd opinion | 5 | unavailable (Codex); native Opus completed | design phase: 12 findings, all raised and decided |
| Eng Review | `/plan-eng-review` | Architecture & tests (required) | 2 | issues_open (2026-10-23, 0 unresolved) | 19 issues, 0 critical gaps |
| Design Review | `/plan-design-review` | UI/UX gaps | 1 | issues_open | score: 3/10 → 7/10, 20 decisions |
| DX Review | `/plan-devex-review` | Developer experience gaps | 0 | — | — |

- **OUTSIDE COVERAGE:** design phase. Codex was skipped (auth failed earlier; the founder prefers Opus). The native Opus subagent completed with 12 findings. There is no completed external-provider review in this phase.
- **VERDICT:** CEO CLEAR. Eng review was logged `issues_open` with 0 unresolved, and its decisions are applied in design/ (D-034). The design review is not yet clean (7/10, held back by DESIGN.md and the missing mockups). Eng review required: re-run /plan-eng-review on the D-035 mapper and the workspace.md additions before M1.

NO UNRESOLVED DECISIONS
