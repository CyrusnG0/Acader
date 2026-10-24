# THE WRITING ROOM: Source-Confrontation Workbench
**Master Product Proposal & Clickable Vision Mockup Spec, v2**

Status 2026-10-19. This replaces the draft in `renewed_proposal.md` (left untouched). All source facts come from [sources-verified.md](sources-verified.md). If a number is not in that file, it must not be on screen.

---

## 1. Core thesis

In the AI era, policing keystrokes and scoring prose is a dead end. **The Writing Room** is a workbench where a student meets real literature, including papers that disagree with their hunch, and ends up with a piece of work plus **3 questions about their own choices**.

- **For honest students:** it removes busywork (finding sources, formatting and checking citations, surfacing a disagreeing paper) and turns their rough notes into their outline. Nothing is required that an honest student wouldn't do anyway.
- **For a pasted draft:** the room never blocks or accuses. It pairs the draft with questions anchored to specific passages in real papers. If the student patches the draft paragraph by paragraph, the paragraphs start to disagree with each other. That is **what faking looks like when it gets expensive**: the student has to work through the problem anyway.
- **We do not claim to win inside the screen.** A strong outside AI can answer our questions and write a draft that hangs together. So the room does two things:
  1. **Faking costs about as much as thinking**, because the questions are about this student's own sources and choices.
  2. **Every submission comes with 3 questions.** A student who did the thinking answers them in 30 seconds, out loud. The spoken answer, heard by a person, is the real check.
- **Strict boundary:** the room never writes the student's prose and never grades. A human reads the receipt and decides what, if anything, follows.

> Wording note: the receipt is a **process profile, not a verdict**. It shows evidence on every submission and where the reasoning is thin. It never labels a student.

---

## 2. Accessibility (WCAG 2.2 AA)

- **No drag-and-drop (2.5.7).** Linking a passage, anchoring a claim and marking a flaw are all single-click buttons.
- **Target size (2.5.8).** All controls at least 32×32 px, with visible focus rings.
- **Colour independence.** Every status colour comes with an icon and a text label.
- **No timers.** There is no countdown anywhere. The oral is one spoken answer with no visible clock, and a typed alternative is always available.

---

## 3. Layout and demo switcher

Sticky header:
1. Brand: **The Writing Room**, with the badge "Process profile, not a verdict".
2. Assignment pill: `SOC-304: Remote Work and Junior Staff (Prof. Vance)` *(fictional course)*.
3. Three tabs: **1. Writing Room**, **2. Reviewing Room**, **3. Understanding Receipt**.
4. Scenario switcher (presenter tool):
   - **A. Honest iterative thinker.** Rough notes, balanced sources, tensions worked out.
   - **B. Pasted draft, patched.** A polished AI essay pasted in, then patched to answer our question. The paragraphs now disagree.
   - **C. Full offload.** An outside AI filled in every box. The form looks perfect; the receipt's same-standard check and the 3 questions still apply.

---

## 4. Real sources used (all verified)

| ID | Source | Role | Key facts shown (from the paper) |
|---|---|---|---|
| S1 | Bloom, Liang, Roberts & Ying, *Does Working from Home Work?* NBER WP 18871 (2013) | Confirming | One company (CTrip, a 16,000-employee travel agency); call-centre volunteers randomly assigned for 9 months; **+13% performance**, about 9 points from more minutes worked and about 4 from more calls per minute; promotion rate conditional on performance fell |
| S2 | Gibbs, Mengel & Siemroth, *Work from Home & Productivity*, IZA DP 14336 (May 2021) | Complicating | One company ("a large Asian IT services company"); **10,000+** professionals; total hours **+~30%**, **+18% after hours**; output not significantly changed, so productivity **−~20%**; less coaching and 1:1 time; greater-tenure staff increased output slightly |
| S3 | Emanuel, Harrington & Pallais, *The Power of Proximity to Coworkers*, NBER WP 31880 (June 2026 revision) | Adjacent (juniors and feedback) | Software engineers at a Fortune 500 firm; sitting near teammates raises coding feedback **18.3%**; gains concentrated among **less-tenured and younger** employees; experienced engineers write less code when sitting near teammates |
| S4 | Yang et al., *The effects of remote work on collaboration among information workers*, Nature Human Behaviour (2021) | Mechanism | 61,182 Microsoft employees; remote work made the collaboration network **more static and siloed**; **less synchronous, more asynchronous** communication |

**Demo caveat shown on screen:** "Sources are real; the course, student and essays are fictional. Quotes are from the abstracts. Open the paper to check them." Where the mockup shows a source card, it shows only the abstract-level quotes in `sources-verified.md`.

---

## 5. View 1: The Writing Room

**Left column: sources.**
- *Step 1 (optional claim-first):* the student writes a hunch. Hardcoded: "Remote work boosts productivity because people skip commuting and have fewer distractions."
- *The Triad:* three cards, each with a clickable quote (Bloom as Confirming, Gibbs as Complicating, Emanuel as Adjacent).
- *Citation help:* clicking a quote inserts a formatted citation **and checks it against the paper**. This replaces hand-formatting.
- *Graveyard:* a **Set aside** button on each card. One click on a reason pill (`Different setting`, `Out of scope`, `Method concern`, `Will address in text`). A note is optional.

**Middle column: your outline (optional).** Three inquiry cards. Answers double as the student's outline and are tracked against the essay.
1. **Scope.** "Bloom measures call-centre staff who volunteered. Your question is about junior staff. How are you narrowing 'productivity'?"
2. **Tension.** "Bloom reports +13%. Gibbs reports roughly flat output with ~30% more hours, so about −20% per hour. How does your thesis handle both?" Stance pills: `Limit the claim`, `Argue tools replace coaching`, `Move to a hybrid model`.
3. **Boundary.** "Emanuel et al. find the feedback gain from sitting near teammates is concentrated among less-tenured engineers. If a team uses AI pair-programming instead, does that gain still matter? Commit to a boundary."

**Right column: essay canvas.**
- Three paragraphs with badges such as `[Cites S1]` and `[Linked to Inquiry 1]`.
- **Scenario A:** paragraph 1 splits routine output from learning on the job; paragraph 2 uses Gibbs' hours-versus-output result; paragraph 3 uses Emanuel's finding on less-tenured staff. Student's own phrase: "seniority tax" (their term, not a paper's).
- **Scenario B:** paragraph 1 says remote work raises everyone's output by 13%; paragraph 2 (patched after the Gibbs question) says remote work cuts productivity about 20%; paragraph 3 says remote transitions have no trade-offs. A neutral note appears: **"Paragraph 2 and Paragraph 3 now say different things."** There is no instruction on how to fix it.
- Button **Simulate pasted draft and patch** runs the animation. Caption: **"Faking gets expensive: patching one paragraph moves the others."**
- Toggle **Polished by an outside AI** on Scenario A: the final sentences are smoothed, and the receipt still shows the idea started in the student's notes.

---

## 6. View 2: The Reviewing Room

Header: "Review this AI-written draft. Find 3 problems by linking the sentence to the passage that shows it."

Left: the draft, with 3 clickable sentences. Right: evidence rows. After linking, the student picks a tag. Each flaw misstates a real finding.

1. *"Bloom et al. conclusively show that working from home raises output by 13% for all kinds of employees."* → link to S1's setting (call-centre volunteers at one company, 9 months). Tag: **Too broad a population.**
2. *"Gibbs et al. found that staff worked fewer hours at home but output rose, so productivity improved."* → link to S2's abstract (total hours up ~30%; output not significantly changed; productivity down ~20%). Tag: **Finding reversed.**
3. *"Yang et al. show that firm-wide remote work made Microsoft's collaboration network more connected across teams."* → link to S4's abstract ("more static and siloed, with fewer bridges"). Tag: **Mechanism reversed.**

A counter shows **Flaws found: n of 3**, which feeds the receipt.

---

## 7. View 3: Understanding Receipt

One page for the instructor. **No AI-probability score. No verdict.**

**Switcher** for Scenarios A, B and C.

**Block 1: Process profile (three cards).**
- *Sources met:* e.g. "3 of 3 sources opened" (A) versus "Gibbs first opened after the question" (B).
- *Do the paragraphs agree?* "Yes, 3 revisions in step" (A) versus "Paragraphs 2 and 3 now say different things" (B).
- *Set-aside sources:* what was put aside and the reason pill chosen.

**Block 2: Same standard? (a reasoning check, shown for Scenario C.)**
> "In Set aside, the student put away **Gibbs et al. (IZA 2021)** with the note *'One company only, can't generalize.'* In paragraph 1 the student relied on **Bloom et al. (2013)**, which is also a single-company study (CTrip). The same limit was applied to one source and not the other."

This is true to both papers (S1 and S2 are both single-company). No sample-size claim is made.

**Block 3: Seed-to-prose diff.**
- Left: the student's rough note: "Remote work is a seniority tax: seniors get quiet focus, juniors lose the feedback."
- Right: the final sentence: "Ultimately, remote work works as an unequal tax: it protects experienced staff's focused output while thinning the feedback that less-tenured staff learn from."
- Badge: **"The core idea started in the student's own notes. Polishing the prose doesn't change where it came from."**
- The student's claim stays labelled as the student's. Neither source says "seniority tax". It is the student's reading of S2 (tenure) and S3.

**Block 4: Defend-it questions.** Generated from the student's own choices.
1. *"You set Gibbs aside for being a single-company study, but paragraph 1 rests on Bloom, also a single company. Why did you trust one and not the other?"*
2. *"Gibbs reports about 30% more hours and flat output. Your paragraph 2 says tools can replace coaching. What would that look like for the less-tenured staff in Emanuel's data?"*
3. *"If this firm's goal were training new hires rather than this quarter's output, which paragraph would you cut first, and why?"*

**Button: Request a spoken answer.** Opens a quiet panel with no timer or countdown. The browser reads Question 1 aloud (`speechSynthesis`), and the student can answer out loud with a person listening, or type instead.

**Last beat of the demo:** "This mockup shows the vision. **This part already runs for real:** [live room link]" (the working room in `writing-room-kit/web/`).

---

## 8. Pitch (clean version)

**Cold open (30 seconds)**
> "Schools are stuck between two bad options: software that watches every keystroke, or AI-text checkers that don't work. We chose a third way. We don't police AI use. We make sure every submission comes with evidence of understanding. A workbench that helps students find and confront real sources, and 3 questions a person can ask out loud in a minute."

**Act 1: honest student.** The student places a hunch. The room brings three real papers, one of which disagrees. Clicking a quote cites it correctly and checks it against the paper. "Less busywork. The room never writes a sentence."

**Act 2: a pasted draft.** "A strong AI can write a clean essay in ten seconds, and it can answer our questions too. We don't pretend otherwise. So we don't try to win inside the screen. Faking costs about as much as thinking, because the questions are about *this* student's own sources and choices. Watch: patch paragraph 2 to answer the Gibbs question, and paragraph 3 no longer agrees. And the questions go to a person."

**Act 3: Reviewing Room.** "Instead of a 500-word review that can be pasted in, the student finds three problems in an AI draft and links each to the passage that shows it. Every flaw here is a real misreading of a real paper."

**Act 4: Receipt, then the oral.** The three profile cards, the same-standard check, the seed-to-prose diff, the 3 questions, and the spoken-answer panel with no clock.

**Closing line**
> "Welcome to the AI era. If a student runs our questions through an AI, rewrites their premises three times to resolve the conflict, and then uses AI to smooth the grammar, they now know their thesis, they know why the counter-evidence matters, and they can defend it out loud. That is the outcome we want. And the person asking the 3 questions finds out in a minute."

---

## 9. Q&A answers

**Q1. "What if the student copies your questions into Claude and answers them?"**
> "Then they have done the thinking, or the spoken answer shows they haven't. Our edge is not a lock on the screen. It is that the questions are about their own choices, and a person hears the answer."

**Q2. "What if next year's model fills in the whole form and essay in one click?"**
> "Inside the screen, a stronger model will always beat static software rules. That is why the gate is not a digital lock. The more an outside AI decides for the student, the more specific choices it makes on their behalf, and those choices become the 3 questions. A student who did none of the work can't say why they set a source aside."

**Q3. "Does it meet accessibility standards (WCAG 2.2 AA)?"**
> "By design: no timers anywhere, no webcam, and every spatial action is a single-click button, following WCAG 2.2 AA criteria 2.5.7 and 2.5.8. The oral can be spoken or typed."

**Q4. "Are those the real papers?"**
> "Yes. The four sources are real and every quote is taken from the abstract. The course, the student and the essays are fictional. Open any card and compare."

---

## 10. Honest limits, to say out loud if asked

- "Less busywork" is `[ASSUMPTION — to be measured in pilot]`. We have not yet measured time saved.
- The mockup uses fixed data. The live room is separate and already runs real model calls; the real citation lookup (DOI to source text) is built next.
- Whether the spoken answer improves a teacher's judgement is exactly what the 15-student blind test measures (see `PLAN-renewed-v2.md`, Step 5).

---

## 11. Presenter notes only (not for screen or public copy)

- "Welcome to the AI era" is the closer; pause before it.
- Keep it plain. If a researcher says "so it can be beaten," agree and go to the spoken answer.
- Wording to avoid on stage: the old draft's words for pasted drafts, for what the receipt does, and the names it gave the questions and the receipt (see the swap table in `PLAN-renewed-v2.md` §2a).
