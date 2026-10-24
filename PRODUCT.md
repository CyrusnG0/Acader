# The Writing Room: product definition

Status: **source of truth for product intent** · Last updated: 2026-10-23
Built from: decisions D-024 to D-030 ([docs/DECISIONS.md](docs/DECISIONS.md)), the researcher demo on 2026-10-21, and the founder interview on 2026-10-22.
If any doc disagrees with this file about what we are building, this file wins, unless a later decision in DECISIONS.md overrides it. Engineering detail lives in [design/](design/README.md).

---

## 1. One paragraph

The Writing Room is a writing platform that schools buy and students write their assignments in. While the student reads, plans and writes, the platform records **where each part of the work came from**: a passage in a source, a lecture, an exchange with the Coach, outside AI help the student declared, or nowhere we can see. At submission, the teacher gets a one-page **receipt**. It shows what was traced, what was declared and what has no trace, then lists two or three questions worth asking. **The receipt shows where to ask. It never gives a verdict.** A person has the conversation and makes any decision.

## 2. The problem (what teachers told us)

- "Is this AI?" is a feeling, not a fact. Teachers are stressed by suspecting without evidence, and students are stressed by being suspected.
- Real case (nursing, 2026-10-21): a teacher suspected AI and asked the student for proof. The student handed over a 40-page Copilot log. The teacher then suspected a second outside LLM and asked for more. It took many meetings and settled nothing.
- **What went wrong:** a raw log is too long to read, and it covers only one tool. No log can prove that something *didn't* happen elsewhere.
- **What would have helped:** a short, structured record that shows how the work was built, says plainly what it can't see, and points to the two places worth talking about.

## 3. What we promise, and what we don't

| We promise | We never claim |
|---|---|
| A record of how the work was built inside the platform, with evidence the record wasn't edited after submission | To know where a thought came from |
| Proportions of the work that are traced, declared and untraced, by words and by claims | A "% AI" score, or that untraced means AI |
| Two or three questions anchored to the student's own work and choices | That the questions prove anything without a person asking them |
| Help to read sources, find passages and get citations right | To summarise a paper or write the student's argument |
| That the student owns their process data | That the platform prevents outside AI use |

**Known blind spot, always stated:** text retyped from an outside AI looks the same as text the student typed. Our own simulation showed it (kit v0.3: retyped hybrid 92 vs honest 91). This is why the conversation, not the record, is the real check.

## 4. Who it is for

| Role | Wants | Gets |
|---|---|---|
| **Student** | Do the assignment well without busywork, and not be wrongly suspected | Reading help, source finding, citation mechanics, a Coach that sharpens their ideas, a claim map in their own words, a receipt they can stand behind |
| **Teacher** | Stop guessing; spend any meeting on the right questions | One page per submission, a click-through from any sentence to its origin |
| **School** (buyer) | A defensible AI policy, evidence on every submission, fewer disputes | Assignment setup, policy defaults, aggregate signals only |

First pilot targets (none committed yet, OL-036): nursing/health, a HK university writing course, a CS/FYP write-up course, the researchers' own courses. English only in v1.

## 5. How it works (the core loop)

> v1 is narrower than this full loop: see §7 (one class; Coach B and C; pins by section kind; no polish band or scholarly search).

```
 Sources & lectures ──read with help──▶ Idea cards (student's own words, anchored to a passage)
        ▲                                      │
 Declared outside AI ──Door──▶ Declared claims ┤
                                               ▼
                                   Claim map (the student's mind map) ◀── mapper links meaning, live
                                               │ write                        (never trust; D-035)
                                               ▼
                        Coach asks ◀── Draft (every span carries its origin)
                            │ answered / revised / disagreed / declined
                            ▼
              Receipt: traced · declared · polish only · untraced + where to ask
```

1. **Read.** The teacher uploads readings. The student can add papers from scholarly search or anything through the Door. The **reading aid** shows *places to read* for the student's current claim: support, skeptical, limitation, data, method. It also suggests a **Triad** of confirming, complicating and adjacent sources. It points; it never concludes.
2. **Note.** The student writes the takeaway in their own words as an **idea card**, anchored to the passage it came from.
3. **Map.** Cards and declared claims become **claim nodes** on the student's map. A node without evidence is shown as *unanchored*.
4. **Write.** The student writes in the editor. Every span carries an origin: typed, pasted from outside, quoted from a source, from a Coach answer, or imported through the Door.
5. **Coach.** The Coach asks questions grounded in the sources, the lecture and the student's own trail. **Every new idea gets the same treatment, whatever its origin** (a shower thought or an outside AI's answer): one question from one of four pillars (reading, logic, writing, communication), never about where it came from, never blocking (D-038). It runs in five cases: blank page, arrived with outside AI, untraced text, weak reasoning, and confident mode. Each question ends with a recorded outcome: answered, revised, disagreed (with a reason) or declined.
6. **Submit.** The receipt is a snapshot of the live map and the record. The student sees it before the teacher does.

**The live map is the product (D-035).** While the student writes, a **mapper** runs a small model on each batch of changes and proposes meaning links between the student's sentences and their own claims (this sentence argues claim 2). In v1 it never links to source passages, and a model-proposed link can never make a sentence traced (eng review v2 D19). The map grows bottom-up; nothing is reconstructed at the end. **The model maps meaning, never trust:** provenance bands come only from recorded facts, and a model link shows to the student as "suggested by the map, not checked" and never appears on the teacher's bars or chain. Mapper findings reach the **student** as Coach questions, never as interruptions or timed questions; the teacher sees only the receipt. **In the pilot, the live map is the outline the student builds** (claims, cards, links, the two-way highlight with the draft, and the Coach's "which claim is this making?"). The mapper is a flagged experiment that adds suggestions once its eval passes (eng review v2 D1, D7, D21).

## 6. Product laws (do not break in code, copy or design)

1. **Help students think; never think for them.** The AI never writes the student's prose or invents their argument. It may change structure using the student's own words.
2. **The Helper answers, the Coach asks.** Coach questions are grounded in course material and the student's trail, never in a generic prompt.
3. **Make the right path the easiest one.** Remove mechanical cost (finding, reading, citing). Keep the thinking cost (arguing, choosing, explaining).
4. **Outside is free.** We assume outside AI is always available. The Door imports anything and passes no judgment. Declaring is never penalised.
5. **Typing is not proof.** The trace is evidence of the student's thinking and of *where to ask*. The conversation is the gate. Accessibility alternatives are mandatory.
6. **Never a verdict.** The receipt is a process profile. Untraced is not AI. A human decides any consequence.
7. **Students own their process data.** Schools see the receipt and derived signals only. Course materials never leave their tenant.
8. **Professors are heroes.** Explanations point first to how the student's own instructor taught it.
9. **Scope discipline.** A writing platform for school work. Not a general notes app. The code track is parked.
10. **Wording discipline.** Never "detect", "catch", "cheat", "AI-generated", "forensic" or "suspect". Never promise "no cheating". Promise *evidence on every submission* and *where to ask*. The selling point is thinking, never time saved.

Privacy floor (part of law 7): no keystroke timing, no webcam, no screen capture, no biometrics. **We record what changed in the text, not how you typed it.**

## 7. Prototype v1

Reviewed by /plan-ceo-review on 2026-10-23 (D-032; record in [docs/designs/ceo-review-v1.md](docs/designs/ceo-review-v1.md)).
- **Purpose:** a real student pilot in **one class first**, and a follow-up with the researchers who saw the demo.
- **Build:** solo with Claude, **receipt first** (the questions are what makes us different from Turnitin Clarity and Grammarly Authorship; a blind test checks that). After the eng review (D-034) the plan re-baselined: *engine, receipt and nursing walkthrough ready* about 2026-11-08 (was 11-05); the writing UI follows around 11-14, and 3–5 real people try it before any class does. Students start when the pilot gate passes: school and provider approval, ethics approval if we survey, and a named assignment window. See [design/build-plan.md](design/build-plan.md).
- **In:**
  - Teacher: upload the class roster, create an assignment, upload readings.
  - Student: sign in by invite link; an editor with origin tracking; readings with pins by section kind (limitation, method, data, results); idea cards; the live map as an outline the student builds (D-036); map suggestions from the mapper only behind a flag, if its eval passes (eng v2 D21); the Door (pasted text and files, never fetched links); Helper; Coach cases B and C.
  - The receipt with click-through. The student previews it first (spans and facts, not the questions). It is released to the teacher at the latest of: the deadline, 24 hours after submitting, and when the questions are ready.
  - Consent, export and delete.
- **Rules settled in review:**
  - A submission is always sealed, even when the AI is down. Questions follow later.
  - Reworded text the system hasn't checked counts as untraced, with a note saying so.
  - The AI claim check marks nothing "traced" unless it has passed its test (spike S3).
  - A link the student made themselves shows as "linked by student, not checked", in its own band, unless the check confirms it (D-034).
  - Origin labels are checked against their source; pasting into cards and Coach answers is tracked, so outside text can't become "traced" (D-034).
- **Open (P0, OL-043):** if the platform guides every step, every trail may look the same. What else estimates AI involvement?
- **Deferred (TODOS.md):** student scholarly search, AI-written reading pointers, Coach cases A, D and E, claim-map graph view, the "polish only" band, the teacher policy dial, receipt PDF export, Blackboard LTI (first after the pilot), more classes.
- **Out:** teacher mirror (class view), lecture video mining, voice (except as an accessibility route), browser clipper, other languages, the code track.
- **LLM:** DeepSeek plus a second provider behind the same interface; the school picks one, and consent names it (OL-037).

## 8. What success looks like in the pilot

- One class completes one real assignment in the platform.
- Teachers say the receipt changed what they asked, or saved a meeting.
- Students rate the reading aid and Coach as helpful, not policing.
- Zero leaks in an audit of all Helper and Coach output: no student prose was written by us.
- The nursing walkthrough (OL-034): the teacher says this receipt would have ended the dispute faster.

## 9. Where the rest lives

- How it's built: [design/README.md](design/README.md).
- What's decided: [docs/DECISIONS.md](docs/DECISIONS.md). What's open: [docs/OPEN_LOOPS.md](docs/OPEN_LOOPS.md). Where we are: [docs/STATUS.md](docs/STATUS.md).
- Evidence so far (simulated only): [writing-room-kit/](writing-room-kit/README.md) results v0.3 to v0.5.
- Pitch, verified sources and the static demo: [docs/renewed-direction/](docs/renewed-direction/README.md), `writing-room-kit/web/static/demo.html`.
- Earlier vision (lecture mining, code track, Proof of Understanding): [archive/proposals/](archive/proposals/).
