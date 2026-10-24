# The Writing Room v1: product design for the first real prototype

> **Superseded 2026-10-23** as the working spec: product intent is now in [PRODUCT.md](../../PRODUCT.md), the receipt in [design/receipt.md](../../design/receipt.md). Kept as the review input and the record of the founder interview.

Status: **DRAFT, ready for gstack review** (/plan-ceo-review, then /plan-design-review) · Owner: Cyrus · Last updated: 2026-10-22
Source: founder interview 2026-10-22 (four rounds, answers quoted as **[founder]**), the researcher demo meeting 2026-10-21, kit results v0.3 to v0.5, [process-evidence-room.md](process-evidence-room.md) (policy modules, claim lineage), [renewed_proposal_v2.md](../renewed-direction/renewed_proposal_v2.md) (Writing Room, Triad, receipt).
Decisions: D-024 to D-030 in [DECISIONS.md](../DECISIONS.md). Engineering companion: [provenance-engine.md](provenance-engine.md).
Loops: OL-031 to OL-034, OL-035 to OL-042.

---

## 1. Vision and direction (locked 2026-10-22, D-024)

**The Writing Room is a writing platform that schools buy and students write in. The process is the evidence.**

- Schools buy it. Students use it as the place they write school work (essays, reports, care plans, literature reviews, FYP write-ups).
- Every word in the final piece has a traceable origin: a source span, a lecture moment, a Coach exchange, a declared outside-AI import, or nothing. **[founder]** "Every single word is tracked and has a source."
- The teacher gets a short **receipt**: the AI-use proportion and the insights from the process, presented as evidence. **The receipt shows where to ask, never a verdict** (D-025).
- **We assume outside AI is always available** (Claude, Copilot, ChatGPT). We design for that and don't pretend to block it. **[founder]** So the Coach is there to **help, not judge**: it asks questions that make the student's idea stronger, so that they understand the work and use their own brain.
- Tracing is two things at once (amended law 5, D-028): **evidence of the student's thinking** (the writing can be traced back to its mind map of claims and sources) and **the grounds for a conversation** when the teacher wants one. **[founder]** "It's essentially from writing back to mind map. When asking and meeting is needed, we provide evidence and ground support."

**Why now (from the 2026-10-21 meeting).** Teachers struggle because "is this AI?" is subjective and has no proof. Real case: a nursing teacher suspected AI; the student handed over a 40-page Copilot log; the teacher suspected a second outside LLM and asked for more; it took many meetings. A researcher put it as "Grammarly, but more academic and the whole process". A second professor (a friend of the founder) is looking for ways to get AI out of the way of writing. **[ASSUMPTION]** These are informal conversations, not committed pilots.

**What we are not.**
- Not a detector. We never say "this is AI".
- Not a summariser. We help students read; we don't read for them.
- Not a general notes app.
- Not a keystroke-surveillance tool. Process data belongs to the student (law 7).

## 2. Users and buyer

| Role | What they want | What they get |
|---|---|---|
| **Student** (writer) | Get the assignment done well without busywork; not be wrongly accused | Reading help, source finding, citation mechanics, a Coach that strengthens ideas, their own mind map, and a receipt they can stand behind |
| **Teacher** (reader of receipts) | Stop guessing; know where to ask; spend the meeting on the right 2 questions | A 1-page receipt per submission, plus the class view (teacher mirror, later) |
| **School** (buyer) | A defensible AI policy, evidence on every submission, fewer disputes | Course/assignment setup, policy defaults, aggregate signals only |

**First pilot targets [founder]** (several classes, English):
- nursing / health (the 40-page-log case; ESL-heavy clinical writing)
- a HK university writing course (CLEAR / English or writing centre)
- a CS / FYP write-up course
- the researchers met on 2026-10-21 (their own courses)

Named classes are **not yet committed** (OL-036).

## 3. Product laws for this direction

The 10 laws in [CLAUDE.md](../../CLAUDE.md) §4 still apply. Amended by D-028:
- **Law 5 (amended):** typing is not proof. Process tracing is evidence of the student's thinking (writing → mind map) and of *where to ask*. When a conversation is needed, the trace supplies the grounds. The conversation is still the gate. Accessibility alternatives are mandatory.
- **Law 9 (amended):** the platform is a writing platform for school work (assigned writing, graded or practice). Writing first; code track parked (D-030). Still not a general notes app.

Wording guard: internally we say "assume outside AI is present". **Never "suspect the student"** in any UI, copy or pitch (law 10). The receipt never uses "detected", "caught", "ghost", "forensic" or "AI-generated".

## 4. The core loop: writing back to the mind map

```
 Sources & lectures ──read with help──▶ Idea cards (student's words)
        ▲                                     │ anchor to span / lecture moment
        │                                     ▼
 Declared outside AI ──import──▶ Unanchored claims ──anchor or defend──▶ Claim map (mind map)
                                                                            │ write
                                                                            ▼
                                     Coach asks ◀──── Draft (every span carries its origin)
                                         │ student answers / revises / declines
                                         ▼
                              Receipt: traced · declared · untraced + where to ask
```

The **claim map** is the student's mind map. Each node is a claim in the student's words, with links to its evidence (source span, lecture moment) and to the draft sentences that express it. The draft and the map stay in sync: a sentence with no node is "untraced"; a node with no evidence is "unanchored".

## 5. Sources and the reading aid (D-027)

**Where sources come from [founder]:**
1. Teacher-uploaded PDFs and readings (the course pack)
2. Lecture material: slides, notes, transcripts (law 8; the M2 miner is a future input)
3. Papers the student finds through scholarly search (Crossref / OpenAlex / Semantic Scholar)
4. Outside sources the student pastes in through the Door (any URL or text)

**The reading aid: we help them read; we never summarise.** **[founder]** "When we have LLMs, no one is going to insist on reading 40 pages by hand. Instead of letting students use an LLM blindly, we let them use it in our platform, like Google Scholar, and help them read, but still aid their thinking." The researchers agreed.

For a source and the student's current claim, the aid shows **places to read**, not conclusions:

| Pin | Points to |
|---|---|
| Support | Passages that go in the claim's direction |
| Skeptical | Passages that complicate or contradict it |
| Limitation | Sample, setting, method limits ("one company, volunteers") |
| Data | The tables and figures carrying the numbers |
| Method | How it was measured |
| (more) | Definitions, the authors' own caveats, related lecture moment |

- It also offers **Triad recommendations** across sources (confirming / complicating / adjacent), as in the demo.
- It explains terms and answers "where does it say X?" by pointing to the page.
- **The student writes the takeaway in their own words**, which becomes an idea card anchored to that span.
- It does **not** produce "this paper argues…" or "the key finding is…" prose. (P-READ and P-SUM in [process-evidence-room.md](process-evidence-room.md).)

**Citation help:** formatting is instant (mechanics, law 3). Verification checks that the source exists (DOI) and that the cited span is about what the sentence says. A failed check gives the student an open note. Note: v0.4 showed a correct citation is **not** process evidence (outside AI cites accurately), so verification is feedback for the student, not a provenance signal.

## 6. Coach and Helper cases (D-026)

The **Helper** answers (mechanics, reading, finding). The **Coach** asks (grounded in the sources, the lecture and the student's own trail). Neither writes the student's prose or invents their argument (law 1).

| Case | Situation | Helper does | Coach asks |
|---|---|---|---|
| **A. Blank page** | No idea yet | Finds sources, shows Triad and reading pins, explains terms | "What's your hunch? One line is enough." Then "What in this source makes you think that?" Never supplies the idea. |
| **B. Arrived with outside AI** | Student brings a log, outline or ideas from Claude/Copilot through the **declared channel** | Splits the import into unanchored claims (in the import's words, labelled as declared) | For each claim: "Which source supports this? What would complicate it?" The student anchors it, restates it in their own words, or drops it. Declaring is never penalised. |
| **C. Untraced text appears** | A paste or a block with no ancestor appears in the draft | Offers "trace this": link it to a card or source, or mark it as declared outside help | Asks neutrally about the idea: "This paragraph brings in renal clearance. How does it connect to your dosage point in ¶2?" No accusation, no blocking. |
| **D. Weak reasoning in own work** | Contradiction between paragraphs, scope creep, cherry-picking, an unanswered counter-source | Points to the passages involved | "¶1 says all staff gain; Gibbs Table 3 says juniors drop. Which do you mean?" The student fixes it in their own words or explains why not. |
| **E. Confident mode** | Student wants no help and writes their own claims | Stays quiet except mechanics | Asks a few questions at the end that check the work fits what they said |

Each Coach question records the outcome: **answered**, **revised**, **disagreed with reasons**, or **declined**. **[founder]** Declining ("refused to answer") is a fact on the receipt, not a penalty.

## 7. The receipt (D-025)

**Promise:** "Here is what we saw happen in the platform, what the student told us came from outside, what has no trace, and the questions worth asking." It is a process profile, not a verdict. A human decides any consequence (law 6).

**The proportion bar.** The only proportions we show are about **traces we recorded**, never "% AI":

| Band | Meaning | How we know |
|---|---|---|
| **Traced to a source or lecture** | The claim or sentence links to a span the student opened and anchored, and it's in their words | Recorded links + edit history |
| **Traced to a Coach exchange** | It came out of the student's own answer to a Coach question | Recorded dialogue |
| **Declared outside help** | It came in through the declared channel (anchored afterwards, or not) | The student declared it |
| **Polish only** | The wording changed (by the student, our Helper, or declared outside polish) but the claim node is unchanged | Claim-level comparison, not a similarity score alone (see the eng doc §5) |
| **Untraced** | No ancestor in the platform. **We can't see where it came from.** | Absence of a record |

Printed under the bar: "Untraced is not AI. It means this platform has no record of where it came from. Retyping, writing offline and outside help all look the same here."

**Then the receipt shows:**
1. **Where to ask:** 2 or 3 questions anchored to untraced or weakly anchored spans and to the student's own choices ("On 3 Nov you set aside Gibbs as 'different setting'; ¶2 relies on a single-company study too. What's the difference?").
2. **Coach record:** how many questions were asked and the outcome of each (answered / revised / disagreed / declined).
3. **Reading depth:** which parts of the sources were opened and anchored (abstract only vs. method / data / limitations). Shown as facts, not a score.
4. **Thinking moments:** claims the student changed after meeting evidence, ideas set aside with reasons, and disagreements with the Coach backed by reasons.
5. **Blind spots, stated:** what the platform can't see.

**Click-through:** from any sentence to its chain (source span → idea card → claim node → drafts → final). This is the "40 pages replaced by one page" answer for the nursing case (OL-034).

## 8. Teacher mirror (later than v1)

Class-level view from D-023: which source passages the class used and skipped, shared reasoning gaps, linked to lecture moments. Teacher-owned, no rankings, minimum group size ~5 (OL-024). **Not in v1**; v1 records the data it needs.

## 9. Prototype v1 scope (D-029)

**Purpose [founder]:** a real student pilot and a researcher follow-up. **Timeline:** solo + Claude, 2 weeks (target 2026-11-05). **Language:** English. **Scale:** several classes. **LLM:** DeepSeek. **Stack:** decided in /plan-eng-review.

**In v1:**
- Teacher: create an assignment, upload readings, set the policy level.
- Student: editor with origin tracking; source library with the reading aid; idea cards → claim map; declared outside-AI channel; Helper; Coach cases A–E.
- The receipt (§7) with click-through chains.
- Consent screen, export and delete for students.

**Not in v1:** teacher mirror; LMS integration; lecture video mining (lecture *notes/slides* as text sources are in); voice input except as an accessibility route; browser clipper; discipline "cartridges"; a provenance file-format standard; personal knowledge graph across courses.

## 10. Tensions to clear in gstack review

These are flagged on purpose for /plan-ceo-review and /plan-eng-review:
1. **2 weeks vs. a real student pilot in several classes.** Hosting, consent, accounts, retention and the D-022 hardening gate (T1–T4) all apply. A thinner cut (one class first) may be needed. (OL-039)
2. **DeepSeek for real HK students.** Student text goes to a China-based provider; needs disclosure, school approval and a PDPO check. Some universities may refuse. (OL-037)
3. **"Every word has a source" vs. what we can prove.** The *record* can be made tamper-evident; the *origin of a thought* can't. Retyped outside text looks typed. The receipt has to say so plainly. (OL-035)
4. **Proportions as evidence.** Even "traced %" will be read as a score by some teachers. The design needs to stop that reading. (OL-032, closed by D-025, but its UX is open)
5. **Thin honest students** (quiet, anxious, ESL) score low on traces. v0.5: an honest DeepSeek-driven student scored 49 vs ~90. The receipt must not make them look suspect. (OL-040)
6. **No committed pilot class yet.** The 2-week build is useful only if a class is ready to use it. (OL-036)

## 11. Pilot success criteria [ASSUMPTION, to set in review]

- At least one class completes one real assignment in the platform.
- Teachers say the receipt changed what they asked or saved a meeting (interview after grading).
- Students rate the reading aid and Coach as helpful, not policing (short survey).
- Zero law-1 leaks (the Helper/Coach wrote no student prose) in an audit of all transcripts.
- The nursing-case walkthrough (OL-034): the teacher says the receipt would have ended the dispute faster.
