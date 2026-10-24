# T-010 design proposal

**Status:** proposed, awaiting founder feedback and final approval. **Date:** 2026-10-25. **Lead:** codex-lead-T010. This is a review input, not a new product decision or the final DESIGN.md.

## Review the concrete result

- [Interactive HTML preview](T-010-preview.html): teacher receipt, student workspace, type comparison and palette; light/dark switch, narrow layouts and print styling.
- [Exact proposed DESIGN.md](T-010-DESIGN.proposed.md): the complete normative token file and rationale to promote to repository-root DESIGN.md after approval. It is not yet authoritative.

The proposed first impression is **a place for the student's work and a useful human conversation**. The university team has already supplied a real use case. This proposal addresses technical presentation of that product; it does not revisit demand validation.

The sample is synthetic. Receipt summary, question and band counts come from `honest-nursing`, compiled with `ROOM_LLM=stub`. The source-registration correction supplied by the checker gives its real summary two sources; no receipt text was invented to improve its appearance. The question is a deterministic placeholder, not evidence of question quality. The 61-word sample is deliberately small enough to inspect every count. T-017 must still render all golden receipts, and a real person must read them before the M1 exit.

## Product constraints retained

D-036 and design/workspace.md/design/receipt.md already define the composition: editor as anchor; map/editor/Coach at wide widths; reader replacing map; drawers then one-column writing; receipt as one 72ch column; questions before two bars; disclaimer beside the bars; detail disclosure; print patterns; visible focus and generous targets. Those remain fixed.

No new verdict, score, teacher ranking, traffic-light evidence colour, tracking signal, student-writing service or new Coach policy is proposed. No changes to CLAUDE.md or AGENTS.md are part of this approval.

## Proposed direction

**Aesthetic:** quiet and practical, with clear type and spacious reading text. **Decoration:** minimal. **Layout:** the already-approved ruled document and workspace columns, without shadows or extra cards. **Palette:** near-white paper, blue-grey ink, one restrained blue; dark mode uses layered slate surfaces rather than black/glow. **Typography:** upright Source Sans 3 headings and controls, Literata reading text. **Spacing:** a four-pixel rhythm with generous paragraph and section gaps. **Motion:** the already-locked student-triggered 150ms highlight only.

These choices reinforce the same hierarchy: writing first, claims beside it, a question when useful. Receipt counts remain supporting facts below Where to ask. Light and dark keep that hierarchy identical.

### Familiar choices

- Readable form labels and text buttons; a teacher can scan the receipt without learning a new visual language.
- One primary action and plain recovery states; the student can keep writing when AI help is unavailable.
- A normal document column and browser print; the receipt travels into a conversation without becoming an analytics dashboard.

### Deliberate departures to review

1. **Literata for the student's draft and receipt prose, with upright sans headings.** It makes student writing visibly different from surrounding controls and gives the receipt the same reading texture. The benefit is continuity between writing and discussion. The cost is two font families and slightly more vertical space; Source Sans 3 everywhere is the concrete alternative shown in the type specimen.
2. **Generous ordinary-case labels instead of small tracked metadata.** Source names, evidence explanations and control text remain readable rather than becoming tiny dashboard decoration. The benefit is accessibility and a calmer hierarchy; the cost is fewer facts on a crowded screen. Compact preview chrome and the existing details disclosure preserve the first-screen requirements.

These are proposals, not approved departures from the locked product layout. More dramatic display fonts, accent changes and animation were rejected because they would compete with the student's words.

## Fonts: checked primary sources

Verified on 2026-10-25 against Google's official font repository:

| Family | Adopted roles | Verified weights/axes | Source and licence |
|---|---|---|---|
| Source Sans 3 | Display, headings, UI, labels, aligned figures | Variable weight 200–900; proposal uses 400, 600, 700 | [Metadata](https://github.com/google/fonts/blob/main/ofl/sourcesans3/METADATA.pb), [SIL OFL 1.1](https://github.com/google/fonts/blob/main/ofl/sourcesans3/OFL.txt) |
| Literata | Student prose and longer receipt prose | Variable weight 200–900 and optical size 7–72; proposal uses 400 and 600 | [Metadata](https://github.com/google/fonts/blob/main/ofl/literata/METADATA.pb), [SIL OFL 1.1](https://github.com/google/fonts/blob/main/ofl/literata/OFL.txt) |

The preview stylesheet requests only these verified families and weights via [Google Fonts CSS](https://fonts.googleapis.com/css2?family=Literata:opsz,wght@7..72,400;7..72,600&family=Source+Sans+3:wght@400;600;700&display=swap). It needs network access for fonts; if blocked it renders fallbacks. The proposed student platform self-hosts the font files and OFL notices, with swap loading, so class materials and student browsing are not sent to a font service. No font assets or new runtime dependencies were added here.

The skill's font-role shortlist was narrowed by the product: Source Sans 3, Literata and Source Serif 4 were considered for reading; Source Sans 3, Literata and a plain system sans were considered for headings/labels. Only the first two verified families are adopted. Source Serif 4 and a primary system-font aesthetic were not adopted or loaded. There is no need for a decorative mono face; tabular Source Sans figures suffice.

Competitive research and account/browser access were not needed for these locked compositions. No competitor observations are claimed. Outside design-provider proposals were not run; the proposal uses design knowledge and the product specs. Independent local review checks layout, contrast, keyboard and print, not a second provider's taste.

## Contrast evidence

Calculated from the proposed sRGB hex values using WCAG relative luminance: each channel is linearised at 0.04045, then `L=0.2126R+0.7152G+0.0722B`; contrast is `(Llighter+0.05)/(Ldarker+0.05)`.

| Pair | Light | Dark | Use |
|---|---:|---:|---|
| Main text / outer surface | 14.02:1 | 14.83:1 | Reading and headings |
| Muted text / outer surface | 6.20:1 | 9.39:1 | Metadata and labels |
| Accent / outer surface | 7.48:1 | 9.17:1 | Links and focus |
| Main text / paper | 14.40:1 | 13.35:1 | Draft and controls |
| Muted text / paper | 6.37:1 | 8.45:1 | Labels, control outlines, untraced outlines |
| Accent / paper | 7.69:1 | 8.25:1 | Links and focused controls |
| Error text / paper | 7.25:1 | 7.87:1 | System failures only |
| Decorative hairline / paper | 1.84:1 | 3.94:1 | Noninteractive section dividers only |

The light hairline is intentionally not used to identify controls or untraced bands: those use the higher-contrast control-border/muted colour. Band labels/numbers sit outside the coloured fills; patterns plus text identify bands when pale fills have low contrast or print loses colour. The accent button uses white text in light mode and dark surface text in dark mode. Muted colours are never reduced again with opacity.

## Preview verification and scope

The HTML is a static, synthetic visual specimen, not application functionality. Its local view/theme/highlight controls are enough to review the system; assignment actions do not submit work. The renderer, release logic, student preview permissions and chain service remain T-017/later tasks. Printing forces light tokens and expands details; screen details begin closed.

Independent browser review covers wide/narrow light and dark surfaces, overflow, keyboard focus, the current-view skip link, mobile return to draft, and print. Screenshots and exact results are recorded in the task handoff after review. Contrast calculations are validated static evidence, not a substitute for the later axe and real UI flow checks.

## Exact final approval gate

The installed skill requires: **“Wait. Only A permits the writes below; B/C leave project files untouched.”** This is in [proposal-and-preview.md, Phase 6](/Users/micmic/.claude/skills/gstack/design-consultation/sections/proposal-and-preview.md). The proposed DESIGN.md and preview are complete review artifacts; the final root DESIGN.md is deliberately absent pending founder approval of these exact values. Approval should promote `T-010-DESIGN.proposed.md` to `DESIGN.md`; revisions require updating the preview and affected checks before asking again.

Requested choice: **approve this type/colour/spacing system**, or identify which part to revise. No final design or product decision has been recorded.
