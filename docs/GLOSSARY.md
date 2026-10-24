# Glossary

Vocabulary for The Writing Room (current direction, D-024). Earlier terms are at the bottom.

## Product

| Term | Meaning |
|---|---|
| **The Writing Room** | The writing platform students write their assignments in. Working product name. |
| **Process as evidence** | Our core idea: how the work was built, recorded in the platform, is the evidence. It is never a verdict about the student. |
| **Helper** | The voice that answers: reading help, finding, citing, formatting. It never writes the student's argument. |
| **Coach** | The voice that asks questions that make the student's idea stronger, grounded in the sources, lecture and the student's own trail. |
| **Mapper** | Background role (not the Helper or Coach) that runs a small model on each batch of changes and proposes sentence-to-claim links on the live map (never links to source passages in v1; eng v2 D19). It maps meaning, never trust: its links show to the student as "suggested by the map, not checked", never raise a band, and appear on the receipt only as a count. Its findings reach the student as Coach questions (D-035). |
| **Live map** | The student's claim map, built bottom-up while they write. The product's main screen; the receipt is its snapshot at submission (D-035). |
| **Paragraph link** | A student's link from a paragraph to one of their claims (D-045). Every sentence in the paragraph shares it, so editing or elaborating never cuts it. Shown as "linked by the student, not checked"; never makes text traced by itself. |
| **Four pillars** | The four skills the Coach's questions train: reading, logic, writing, communication. One pillar question per new idea (D-038). |
| **Coach cases A–E** | When the Coach acts: A blank page, B arrived with outside AI, C untraced text, D weak reasoning, E confident mode. |
| **Coach outcome** | How a question ended: answered, revised, disagreed (with a reason), declined. |
| **Confident mode** | The student turns help off and writes their own claims; the Coach asks a few questions at the end. |
| **Policy module** | Code that governs one Helper capability (P-SRC, P-READ, P-SUM, P-STR, P-ARG, P-WRT, P-CTR, P-CIT). |
| **Policy level** | The teacher's dial per assignment: practice, standard, assessed. |
| **The Door** | The declared channel: the student brings in outside work (chat logs, outlines) and names the tool. Never penalised. |
| **Outside** | Anything not in the platform. Always allowed and never policed. We assume outside AI is present. |
| **Source** | A reading: teacher upload, lecture material, a paper from search, or a Door import. |
| **Block** | A parsed piece of a source with page, position, section and kind (abstract, method, results, table, limitation…). |
| **Reading aid** | Shows places to read for the student's current claim. Points, never concludes. |
| **Pin** | One pointer from the reading aid: support, skeptical, limitation, data, method, lecture. |
| **Triad** | A suggested trio of sources for a claim: confirming, complicating, adjacent. |
| **Idea card** | The student's takeaway in their own words, anchored to the block it came from. |
| **Anchor** | The recorded link from an idea card to a block. |
| **Set aside** | Marking a source as not used, with a reason pill. |
| **Claim node / claim map** | The student's mind map: claims in their own words, linked to cards, declared claims and draft sentences. |
| **Declared claim** | A claim split out of a Door import, in the import's words, labelled as declared. |
| **Unanchored claim** | A claim node with no card or declared claim behind it. |

## Engine

| Term | Meaning |
|---|---|
| **Event log** | The append-only, hash-chained record per student per assignment. The only input to the receipt. |
| **Seal / head hash** | At submit, the log's last hash is printed on the receipt and given to the student, so later edits would show. |
| **Origin mark** | The editor mark on every character saying where it came from: typed, paste_ext, quote, helper, coach, import. |
| **Chain** | Sentence → claim node → idea card → block. Broken at the first missing link. |
| **Recorded vs. inferred link** | Recorded: made by the student or the channel. Inferred: proposed by embeddings and confirmed by the LLM; labelled as such. |
| **L0–L3** | Pipeline layers: capture, deterministic, candidate (embeddings), meaning (LLM on flagged spans only). |
| **Claim compare (L3b)** | Checks each proposition in a sentence against its claim node; "added" propositions are untraced. |
| **AI-expanded card** | A failure case: outside AI expands a student's card with new content that similarity scores miss. |
| **Thin honest student** | A real student who leaves few traces (quiet, anxious, second-language); the receipt must not make them look suspect. |
| **Leak check** | Tests that Helper/Coach output contains nothing the student could paste as their argument (law 1). |
| **Wording filter** | Blocks banned words in teacher-facing text (law 10). |

## Receipt

| Term | Meaning |
|---|---|
| **Receipt** | The one-page process profile per submission. Never a verdict. |
| **Bands** | Traced to a source or lecture, traced to a Coach exchange, declared outside help, polish only, untraced. Shown by words and by claims. |
| **Untraced** | No record in the platform of where it came from. **Not the same as AI.** |
| **Where to ask** | The 2–3 questions on the receipt, anchored to the student's work and choices. |
| **Thinking moments** | Recorded signs of thinking: a claim changed after counter-evidence, a source set aside with a reason, a reasoned disagreement with the Coach. |
| **Reading depth** | Which parts of each source were opened and anchored. |
| **Chain view** | The click-through from a sentence back to its source passage. |
| **Teacher mirror** | Later: a class-level view of what was read and where reasoning was thin. Not in v1. |

## Other

| Term | Meaning |
|---|---|
| **Kit** | `writing-room-kit/`: simulated experiments (v0.1–v0.5) that shaped the design. Not evidence about real students. |
| **Golden session** | A scripted test session with an expected receipt. |
| **Spike (S1–S5)** | A short pre-registered experiment before the build. |
| **AIAS** | AI Assessment Scale; informs the policy levels. |
| **FYP** | Final Year Project. |

## Earlier vocabulary (archived direction)

Lecture mining, board state, ink, ladder, course graph (L1/L2/L3), School Teaching Brain, Proof of Understanding, Space, End/Clear End, variant engine, line-level viva, burst-typing escalation, coverage map, five cross-checks and hero teacher belong to the original vision. See [../archive/proposals/ultimate-proposal.md](../archive/proposals/ultimate-proposal.md). Lecture mining may return as a source input.
