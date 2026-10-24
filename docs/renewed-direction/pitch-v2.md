# Pitch script v2 (matches demo.html)

Open `writing-room-kit/web/static/demo.html` (or `/demo` on the app). Click **Next** as you talk.
Lines in *italics* are stage directions. Everything said here matches what is on the screen.

> Before you use it: **check the Po-Shen Loh line** (section I) against a real source and quote his exact words, or say it as your own idea. It is not verified yet.

---

## I. The hook (Start screen)

"Thank you for your time. I'd love your feedback as researchers.

Soon every student will have an AI that can write a polished 1,000-word essay. The essay will look great. But ask the student one real question about the trade-offs behind it, and many will freeze.

The way I'd put it: using AI to write your homework is like driving a car one mile to get exercise. *(Po-Shen Loh has made a similar point; check his exact words first.)* So the skill students need now is not only writing homework. It is judging it: their own, and the AI's.

Most tools today either try to guess who used AI, or give up. We do neither. We built a place where a student's thinking is easy to do and easy to see."

## II. The idea in one line (still on Start)

"We borrowed one idea from software teams: version control. Like git.

Every change shows up in a **git status** box. Every save is a **snapshot with a reason**, in the student's own words. The **Coach** asks questions. The **Helper** does the boring parts, like sorting notes or finding a quote. Neither of them writes the essay.

The questions train four skills: **reading, logic, writing and communication**."

---

## III. Student 1: from one idea to an essay (10 steps)

*Click Next to Student 1, step 1.*

1. **One rough idea.** "This student has read nothing yet. They type one line: 'Remote work is good. No commute.' Look at git status, top right: 1 change, not saved yet."
2. **Brainstorm.** "The Coach asks three short questions: good for who, good how, says who. The student types rough bullets. The Helper puts them into groups. It does not add a single word. One bullet is a doubt: new people learn by watching others. Remember that one."
3. **Read.** "The student links their claim to a real sentence in Bloom and colleagues. Then they read the method note: one company, call-centre volunteers. So they make their claim smaller to match. That is reading: what a study shows, and what it does not."
4. **First save.** "They save. git status is clean, and the history shows snapshot 101a with their reason. The teacher will be able to read these reasons later."
5. **Push back.** "The Coach points to the second paper, Gibbs and colleagues: skilled IT staff, hours up roughly 30%, output flat, less coaching. The student does not ignore it. They change their view: the gain depends on the kind of work. That idea is theirs, and the history shows exactly when it appeared."
6. **Judge your own words.** "Look at the purple. The student wrote 'remote work navigates a complex balance between flexibility and growth'. It sounds smart and says nothing. The Coach asks: who gains, and who pays? The student rewrites it. The Coach also flagged the word 'quietly', and the student pressed **Disagree**: 'Quietly is my point: the cost does not show up in output numbers.' The word stays, and the reason goes to the teacher. The Coach can be wrong, and that becomes a good moment for the teacher to see."
7. **The other side.** "The Coach asks what a new hire would say. They save a commute. The student adds that view and answers it with the third paper. That is communication: writing for someone who disagrees."
8. **Pasting has a cost.** "Now the student is tired and pastes a chatbot paragraph. That is allowed, and we never block it. But look at git status: 'replaced, 100%', and 'unlinked': the source link is gone. The blue tip says editing 4 flagged words would keep the link."
9. **Undo and edit.** "They undo and change those 4 words. Link kept. Fewer words to change, and the thinking stays in the Room. We did that with design, not a rule."
10. **What the teacher sees.** "One page. Facts, not a score: 5 snapshots, all sources linked, one paste undone, one disagreement with a reason. Which skill each step trained. Where the main idea came from. And three questions about this student's own choices. A student who built this answers each in about 30 seconds."

---

## IV. Student 2: pastes a whole AI essay (5 steps)

*Click the Student 2 pill.*

"This student pastes a full AI essay. git status shows it: 3 paragraphs in one go, 0 source links. We don't accuse anyone. We ask the same question we ask everyone: which passage supports this?

They patch Paragraph 2 to answer. Now Paragraph 2 says staff got less coaching, while Paragraphs 1 and 3 still say everything is great. The yellow box says the paragraphs now disagree. It does not say what to write.

To fix Paragraph 1, they must read what Bloom actually studied. To fix Paragraph 3, they need the third paper. One patch led to the next. By the end they have rewritten the whole essay, and read the sources to do it.

We're honest about the limit: a very determined person could do all this with an AI too. That is why every essay comes with three questions."

---

## V. Student 3: hands everything to an AI agent (5 steps)

*Click the Student 3 pill.*

"This is the hardest case. A strong AI agent writes the essay and fakes a neat, step-by-step history. It also sets aside the paper that disagrees, with a smart-sounding reason: 'One company only. Cannot generalise.'

*(Step 4.)* Here the teacher's page runs a simple reasoning check: same standard? The student set Gibbs aside for being one company. But their main source, Bloom, is also one company, and much smaller: 249 people against more than 10,000. The same filter was used on one paper and not the other.

This is not a verdict. It becomes a question. *(Step 5: press 'Read question 1 aloud'.)* The teacher or a TA asks it in person. A student who did the thinking answers in about 30 seconds. The teacher decides what happens next. The system never does."

---

## VI. What people usually ask

1. **Teacher workload.** "The teacher reads one page and asks three questions. Turning a teacher's own reading list into source cards is the next thing we build. It is not built yet."
2. **The AI makes mistakes.** "Yes. That is why there is a Disagree button. The student's reason goes to the teacher, and a good disagreement is a sign of thinking."
3. **Privacy and access.** "No webcam and no keystroke logging. We record only snapshots and the reasons the student writes. No drag-and-drop and no timers. We are designing to WCAG 2.2 AA. It has not been audited yet."

## VII. The ask

"We'd like a small pilot: one writing assignment, or about 30 volunteer students, this semester. Together we could answer three questions:

1. When a pasted draft starts to disagree with itself, how many students go back and read the sources?
2. Do the Coach's questions make the final essays better?
3. How long does a teacher really need per student with the one-page summary?

Which of these would you most like to test?"

---

### Things this script no longer says (and why)

| Old line | Why it's gone |
|---|---|
| Bloom +13.5%, 1,000 workers; Gibbs JPE 2024 Table 3, −42% juniors; Pentland 3.2x | Not in the real papers. We use the real figures from `sources-verified.md`. |
| "Caught", "detected", "liability", "X-Ray", "cheater" | Our rule: no police words. We give evidence and questions, not accusations. |
| 90-second countdown | It clashed with "no stressful timers". The answer has no clock. |
| "Git history proves 100%", "collapses in 30 seconds" | Overclaims. A strong AI can fake the history, so the person asking questions is the real check. |
| "Turnitin Clarity tracks webcams" | Not checked, and probably wrong. Don't name rivals unless you've verified the claim. |
| "PDF to sources in 2 minutes", "fully WCAG compliant" | Not built or audited yet. Said as plans instead. |
