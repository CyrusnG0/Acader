# The student workspace and the live map

Status: **reviewed (design) 2026-10-24; DESIGN.md pending (/design-consultation, 13A)** · Last updated: 2026-10-24
Implements: D-035 (the live map is the product), laws 1–7 and 10; [reading-aid.md](reading-aid.md), [coach-helper.md](coach-helper.md), [receipt.md](receipt.md). Design review record: [docs/designs/design-review-v1.md](../docs/designs/design-review-v1.md).

## 1. Layout (design review 1A)

The student came to write, so the **editor is the anchor**. The live map stays in view and is wired to the text both ways; that link, not its size, is what makes it the product.

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Writing Room · <assignment>          Readings (3) · Bring in outside work · Submit │  top bar
├──────────────────┬──────────────────────────────────────┬──────────────────┤
│ YOUR MAP (~25%)  │ EDITOR (~50%)                        │ COACH | HELPER   │
│ claim outline    │ title                                │ (~25%)           │
│  ▸ claim 1       │ draft text                           │ one question at  │
│    card · source │                                      │ a time, grounded │
│  ▸ claim 2       │                                      │ in ¶ / claim IDs │
│    card · link   │                                      │                  │
│  ▸ claim 3 …     │                                      │                  │
└──────────────────┴──────────────────────────────────────┴──────────────────┘
 Reader open: the reader replaces the map rail as a split (reader | editor | panel). Never a fourth column.
```

- **Order of attention:** (1) the draft, (2) the student's own claims, (3) the Coach.
- **"Map" in v1 means this outline:** claims in the student's words, each listing its cards, sources and links; declared claims in their own style; unanchored claims shown as "needs a source". The graph view stays deferred (TODOS #7); the outline carries the same data.
- **Two-way highlight:** selecting a claim highlights its paragraphs in the editor; placing the cursor in a paragraph highlights its claims in the map. Links belong to paragraphs, so editing inside one never breaks or stripes a link (D-045).
- **Layout, not cards (10A):** the three columns are divided by 1px hairlines, never boxed panels. The only card shapes in the product are idea cards and the one Coach question.
- **Motion (11A):** one authored motion only: the claim↔paragraph highlight fades in over 150 ms (ease-out) when the student selects; instant under `prefers-reduced-motion`. Map suggestions, Coach questions and status lines appear with no animation, no pulsing badge and no sound.
- **The Door** is a top-bar button ("Bring in outside work"), one click away, never inside the editor.

## 2. Map suggestions (design review 4A, 5A)

The mapper (D-035) proposes meaning links on each 5-minute batch. The student decides.

| State | What the student sees | Record |
|---|---|---|
| Waiting | One quiet line under the map header: "Map updates every few minutes." No spinner, no animation. | — |
| Suggested | A dotted connector on the claim row, the label "suggested by the map, not checked", and two text buttons: **Yes, link it** · **Not this** | `map.suggestion` (chained; artifact_id + output_hash, D31; eng D3) |
| Yes | Becomes "linked by the student, not checked" (band 4), counted on the receipt as "accepted from map suggestions" (eng D12). **Never traced.** | `map.answer` yes + paragraph link `{claim_id, by: student, suggestion_id}` via an editor step (eng D3, D-045) |
| Not this | Gone. Not suggested again for that paragraph. **Never shown on the receipt.** | `map.answer` no (eng D3); rejection keyed by (claim_id, paragraph) (eng D11; exact key settled in M4m, D-045) |
| Stale | The paragraph was deleted or split since the suggestion was made (mapped through later steps from the suggestion's `doc_rev`), or the student already linked it. It is not shown. | — (eng D14, D-045) |
| Conflict | The student's own link always wins; the suggestion is dropped. | — |
| Mapper down | The map simply stops adding suggestions. No error, no banner. | operator alert only |
| Too many open | At most **3 unanswered suggestions** are shown at once; a newer one replaces the oldest, which expires silently. | — (eng D18) |
| At submit | Unanswered suggestions expire silently. | — |

Names (4A): "checked against the source" (L3b) · "linked by the student, not checked" · "suggested by the map, not checked" (student-facing only). The teacher never sees suggestions in the bars or chain; "About this receipt" shows only their count.

## 3. States (design review 6A)

What the student sees. Every string passes the wording filter (receipt.md §5). No spinners; loading shows the last known content or a skeleton.

| Feature | Loading | Empty | Error | Success | Partial |
|---|---|---|---|---|---|
| Map rail | Outline skeleton | "Your map starts with a card. Open a reading, select a passage, then Make a card." **[Open a reading]** | (local; doesn't fail alone) | Claims with their cards, sources and links | Claim with no card or source: "needs a source" |
| Editor | Last saved text | Title field + "Start anywhere. Your map and readings stay beside you." | Offline: "Saving when you're back online" (writing continues; the queue keeps it) | "Saved" | Lease lost: read-only, "This draft is open on another device. **Edit here instead**" (D10); unsent text offered as a file or through the Door (D32) |
| Reader | "Opening p.1…" | "No readings yet. Your teacher hasn't added any." + link to the Door | Scan: "This PDF is a scan. Ask your teacher for a text version." | Page + pins | Parsing: "Still preparing this reading" |
| Card save | Inline "Saving" | — | "Card not saved. Try again." (text kept in the box) | The card appears under its claim on the map | — |
| Coach panel | "Thinking of a question" | "No questions right now. Keep writing." | "AI help unavailable. Writing still works." | One question | "Question not ready, try again" |
| Door | Upload bar | Paste box + "Which tool was this?" field | Over the cap: "Files up to 50 MB and 300 pages." | Declared claims appear on the map in their own style | — |
| Submit | "Saving everything first…" (flush, D10) | — | "Couldn't submit. Your work is saved. Try again." | **Sealed:** "Submitted on [date]. Your receipt preview is ready. Your teacher sees it from [time]." **[See my receipt]** | — |

## 4. The trail in the editor (design review 7A)

- **Off by default.** The editor is plain while drafting: no origin colours, no margin ticks.
- **"Show my trail"** in the editor bar paints the same bands the receipt will use, sentence by sentence. The choice is remembered per student. While it's on, a line under the bar reads: "Your trail so far. Final checks run when you submit." (origin marks are confirmed only at compile, D29, so this view is provisional and says so). The trail service runs the engine's own replay + mark check + L1 on the current draft, never a separate band calculation; a golden parity test keeps it equal to the L1 receipt (eng review v2 D8).
- The map's **"needs a source"** is the only always-on cue, phrased as a task, never a status.

## 5. Widths (design review 14A, amended by 15A)

| Width (CSS px, so browser zoom counts) | Workspace | Receipt and preview |
|---|---|---|
| ≥ 1280 | Three columns (§1) | One 72ch column |
| 900–1279 | Editor full width; **Your map** and **Coach** open as side drawers from the top bar. Drawers push the editor, never cover text being typed. The reader opens as a split with the editor. | One 72ch column |
| < 900 | **One-column writing mode** (15A): editor full width; **Your map**, **Coach** and the reader open as full-screen views with **Back to my draft**. On small devices a dismissible hint reads "Works best on a larger screen." **Writing is never blocked**: a student zoomed to 200–400% gets this mode (WCAG 2.2 1.4.10 Reflow, law 5). | One column, full width |

Tested at 1440, 1024 and 375 px plus 200% and 400% zoom (Playwright + axe, M5).

## 6. Keyboard and screen readers (design review 16A)

- **Landmarks:** top bar = `banner` with `nav`; map = `complementary` "Your map"; editor = `main`; Coach/Helper = `complementary` "Coach". Skip link "Skip to my draft". **F6 / Shift+F6** cycle the regions.
- **Map as a tree:** arrow keys move between claims and their cards; Enter highlights the claim's paragraphs in the editor. On a focused suggestion, **y** = Yes, link it and **n** = Not this (active only while that suggestion has focus, WCAG 2.1.4); the visible buttons do the same.
- **Quiet by default:** new map suggestions and Coach questions are **never announced live**. Their count is in the region name ("Your map, 2 suggestions", "Coach, 1 question"). Only the student's own actions get polite announcements ("Card saved", "Submitted").
- **Targets** 44 px on touch, at least 24 px with a pointer. **Contrast** ≥ 4.5:1 for text and band labels (the pale bands rely on pattern + label, 12A). **Focus ring** 2 px accent, always visible, never removed.
- Dictation and assistive input are `typed` (privacy.md §5); no step requires speech, drag or a timer.
