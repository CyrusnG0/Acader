---
# gstack: design-md-format=spec
name: The Writing Room
description: Quiet writing surfaces, clear human questions, and one blue for connections.
colors:
  surface: "#FCFCFA"
  paper: "#FFFFFF"
  text: "#202B35"
  text-muted: "#52616F"
  primary: "#2F4EA2"
  on-primary: "#FFFFFF"
  accent-soft: "#E8EEF9"
  line: "#B7C0C9"
  control-border: "#52616F"
  error: "#973447"
  error-surface: "#FFF0F2"
  dark-surface: "#161D25"
  dark-paper: "#1D2631"
  dark-text: "#ECF0F4"
  dark-text-muted: "#B6C2CF"
  dark-primary: "#A8BEF4"
  dark-on-primary: "#161D25"
  dark-accent-soft: "#28384D"
  dark-line: "#718399"
  dark-control-border: "#B6C2CF"
  dark-error: "#F0A6B3"
  dark-error-surface: "#3E2832"
  band-source: "{colors.primary}"
  band-coach: "color-mix(in srgb, var(--accent) 70%, var(--paper))"
  band-declared: "color-mix(in srgb, var(--accent) 45%, var(--paper))"
  band-student-linked: "color-mix(in srgb, var(--accent) 25%, var(--paper))"
  band-untraced: "{colors.paper}"
typography:
  display:
    fontFamily: "Source Sans 3, sans-serif"
    fontWeight: 600
    fontSize: "clamp(2rem, 3vw, 2.5rem)"
    lineHeight: 1.1
    letterSpacing: "-0.025em"
  heading:
    fontFamily: "Source Sans 3, sans-serif"
    fontWeight: 600
    fontSize: "1.625rem"
    lineHeight: 1.2
  subheading:
    fontFamily: "Source Sans 3, sans-serif"
    fontWeight: 600
    fontSize: "1.25rem"
    lineHeight: 1.3
  body:
    fontFamily: "Source Sans 3, sans-serif"
    fontSize: "1.125rem"
    lineHeight: 1.55
  reading:
    fontFamily: "Literata, Georgia, serif"
    fontSize: "1.125rem"
    fontWeight: 400
    lineHeight: 1.8
  receipt:
    fontFamily: "Literata, Georgia, serif"
    fontSize: "1.0625rem"
    lineHeight: 1.65
  label:
    fontFamily: "Source Sans 3, sans-serif"
    fontSize: "0.9375rem"
    lineHeight: 1.4
    letterSpacing: "0"
  numbers:
    fontFamily: "Source Sans 3, sans-serif"
    fontFeature: "tnum"
rounded:
  control: "4px"
  idea-card: "8px"
  section: "0px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  base: "16px"
  lg: "24px"
  xl: "32px"
  2xl: "48px"
  3xl: "64px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.control}"
    minHeight: "44px"
  button-secondary:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.text}"
    borderColor: "{colors.control-border}"
    rounded: "{rounded.control}"
  button-text:
    backgroundColor: "transparent"
    textColor: "{colors.primary}"
  input:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.text}"
    borderColor: "{colors.control-border}"
    rounded: "{rounded.control}"
    minHeight: "44px"
  idea-card:
    backgroundColor: "{colors.paper}"
    borderColor: "{colors.line}"
    rounded: "{rounded.idea-card}"
  focus:
    outlineColor: "{colors.primary}"
    outlineWidth: "2px"
    outlineOffset: "3px"
  receipt:
    maxWidth: "72ch"
    sectionGap: "{spacing.base}"
    borderColor: "{colors.line}"
  workspace:
    wideBreakpoint: "1280px"
    narrowBreakpoint: "900px"
    columns: "1fr 2fr 1fr"
  highlight:
    backgroundColor: "{colors.accent-soft}"
    duration: "150ms"
    easing: "ease-out"
---

# The Writing Room

## Overview

**Creative North Star:** the student's text feels like work in progress; the receipt feels like a conversation worth having.

This is a school writing platform. Students read, build claims and write; teachers receive process evidence and questions. Read PRODUCT.md and later decisions before applying these visual rules. D-036 already fixes the workspace and receipt composition. This system supplies the type, colour and spacing needed to implement it.

Modes: workspace controls **Operate**; draft and readings **Read**; receipt **Read** with small, clear actions. The product has no marketing-display treatment inside assignments.

## Colors

Restrained neutrals and one blue. Colour identifies interactions and connects paragraphs to claims. It never conveys a judgment about a student.

Follow the device theme initially; offer an explicit light/dark choice. Print always uses the light palette. Dark surfaces keep a visible paper layer and readable secondary text, rather than turning every region black. The neutral backgrounds and two text levels do the hierarchy work.

Map the dark-prefixed tokens to the corresponding base CSS roles when dark mode is active. All evidence-band mixtures use the active accent and paper roles. Evidence fills are supplementary: every band has a text label and number outside its fill. Declared uses dots; student-linked uses diagonal hatching; untraced has no fill and a control-border outline. Preserve those patterns in greyscale print. System-error colour is reserved for genuine operation failures; it never appears in bands, chains or the trail. Success and information use plain text and neutral surfaces.

## Typography

Source Sans 3 gives headings, controls and labels one clear voice. Literata gives the student's draft and longer receipt prose a comfortable reading texture. Use upright, modest headings; avoid italic display treatment and tiny uppercase tracked labels. Use tabular figures for aligned counts, not a new decorative mono face.

Primary font sources and licences were verified on 2026-10-25:

- [Source Sans 3 metadata](https://github.com/google/fonts/blob/main/ofl/sourcesans3/METADATA.pb) and [SIL OFL 1.1](https://github.com/google/fonts/blob/main/ofl/sourcesans3/OFL.txt).
- [Literata metadata](https://github.com/google/fonts/blob/main/ofl/literata/METADATA.pb) and [SIL OFL 1.1](https://github.com/google/fonts/blob/main/ofl/literata/OFL.txt).

Product implementation self-hosts the verified font files and their copyright/licence notices within the school deployment, with `font-display: swap`. Do not load fonts from an external service in the student platform. The proposal preview alone uses the [verified-family Google Fonts stylesheet](https://fonts.googleapis.com/css2?family=Literata:opsz,wght@7..72,400;7..72,600&family=Source+Sans+3:wght@400;600;700&display=swap). System sans and Georgia are fallback roles, not a second aesthetic. The next UI task verifies actual font files, weight coverage and licence packaging before shipping.

## Layout

The receipt is one reading column with a heading and hairline between sections. Questions come before the two evidence bars. Details start collapsed; print expands them. The seal and engine stamp belong at the foot under About this receipt.

The writing workspace has three hairline-separated columns: map, draft, Coach/Helper. The reader replaces the map rail. Medium widths use drawers that push the editor; narrow widths use full-screen map/Coach/reader views with Back to my draft. Writing is never blocked at any zoom. Preserve the breakpoints and state copy in workspace.md.

Use the spacing scale rather than adding custom gaps for individual screenshots. Draft paragraphs get generous vertical space; toolbar groups stay compact. Keep long labels wrapping naturally.

## Elevation & Depth

No shadows or raised dashboard sections. A paper surface, a hairline and whitespace establish regions. Evidence fills carry no elevation.

## Shapes

Controls have the small radius. Only idea cards and the single Coach question use the card radius. Receipt sections and workspace columns stay square, separated by layout rather than boxes. No nested cards.

## Components

Primary buttons use the accent and its matching on-accent text. Secondary actions have a readable outline. Text actions have no enclosing pill. Hover uses accent-soft; keyboard focus keeps the visible focus outline. Pressed states use the accent treatment and a text/ARIA state. Do not use colour alone for selected or disabled state.

Inputs have visible labels and the control-border token. Errors retain entered text and use the exact recovery copy from the state table. Neutral status text handles saving and success; avoid spinners.

Maintain landmark names, skip links and F6 region cycling from workspace.md. New questions and suggestions are never announced live. Keep touch targets at the token minimum and pointer targets at least the product's accessibility floor. Never remove the focus ring.

## Do's and Don'ts

- Do keep the student's writing visually primary and the Coach secondary.
- Do show counts and labels with every evidence band, with the blind-spot explanation beside them.
- Do distinguish system errors from the student's process.
- Do keep the teacher list alphabetical with status only.
- Don't add traffic-light bands, scores, ranking or decorative progress rings.
- Don't turn receipt sections into cards or add a fourth workspace column.
- Don't use tiny tracked labels, glow, gradients or decorative illustrations.
- Don't imply untraced work came from AI; use the exact gloss in receipt.md.

## Motion

Only the student's claim-to-paragraph selection gets the highlight transition. Reduced motion makes it instant. Questions, suggestions, saves and statuses appear without animation, sound or pulsing.

## Decisions Log

| Date | Decision | Rationale |
|---|---|---|
| 2026-10-24 | D-036 workspace/receipt composition retained | The founder already locked layout, band semantics, motion and access rules. |
| 2026-10-25 | T-010 visual system | Prepared from product constraints and the synthetic golden receipt; founder approval is recorded separately by the checker. |
