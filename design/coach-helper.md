# Coach, Helper and the Door

Status: **reviewed (CEO + eng) 2026-10-23** · Last updated: 2026-10-23
Implements: D-026 (assume outside AI), laws 1, 2, 4 and 6; CEO-1, CEO-4, CEO-9, CEO-24; D13, D18, D26 ([eng record](../docs/designs/eng-review-v1.md)). Folds in OL-025.

## 1. Two voices

| | Helper | Coach |
|---|---|---|
| Role | Answers: mechanics, reading, finding | Asks: questions that make the student's idea stronger |
| Starts | When the student asks | At defined triggers and at submit |
| May produce | Locations, definitions, formatting, structure options using the student's own words | Questions grounded in the sources, lecture and the student's trail |
| Never produces | The student's argument, prose they could paste, a summary of a paper's argument | Verdicts, grades, "this looks like AI" |

**We assume outside AI is present.** The Coach doesn't block or judge it. Its job is to make sure the student understands and owns the idea.

## 2. Policy modules (enforced in code)

Every request passes through `classify → policy → serve | redirect → log`. A policy is code, with the prompt as one part. **v1 runs one fixed default policy agreed with the pilot teacher; the teacher dial is deferred (CEO-4).**

| Policy | Student asks | What happens |
|---|---|---|
| **P-READ** reading help | "Where does it say…", "what does X mean" | Point to blocks; define terms. Never summarise the argument |
| **P-SUM** summarise | "Summarise this paper" | "What do you think its main claim is? One line." Then point to passages |
| **P-STR** structure | "How should I structure this?" | 2–3 structure tracks; examples drawn from the student's own cards |
| **P-ARG** what to argue | "What should I argue?" | Only positions in the course or chosen sources (attributed), or clusters of what the student has said. Never an invented argument |
| **P-WRT** write it | "Write this paragraph" | Not served. "What's your idea for this paragraph? One line is enough", then P-STR. Counted, never a mark |
| **P-CIT** citation | Format or check a citation | [reading-aid.md](reading-aid.md) §6 |

P-SRC (find a source) waits for student search (TODOS). P-CTR (counter-claim) waits for Coach D.

## 3. Coach cases (v1: B and C, run as one "new idea" case, D-038)

**Every new idea is treated the same, whatever its origin (D-038).** A shower thought, a friend's remark and an outside AI's answer all look alike to us ("untraced is not AI"), so the Coach never asks where an idea came from. It asks about the idea. B and C below are just the **triggers**; mapper findings (`unconnected_paragraph`, `claim_without_source`) are a third trigger. Whatever the trigger, the question is the same kind: **one pillar question per idea**, grounded in the student's own sources and claims (law 2). This doesn't make outside AI impossible to use; it makes thinking the easier path, because a generic answer fits these questions badly and pasted answers are tracked (D26). Never promise it stops copying (law 10).

| Pillar | Asked when | Example question |
|---|---|---|
| **Reading** | The idea has no source, or leans on one | "What does the study behind this actually show, and about whom?" |
| **Logic** | The idea clashes with another claim or with a source | "Your ¶2 says the opposite. Which one do you keep, and why?" |
| **Writing** | The wording is vague or only sounds smart | "What does 'optimises outcomes' mean here, in your own words?" |
| **Communication** | A confident conclusion | "How would someone who disagrees read this?" |

The Coach picks the one pillar that fits; never all four for one idea. **It never blocks:** the student writes the idea freely, the question comes later in the panel, and declining is allowed and recorded.


| Case | Trigger | What the Coach asks |
|---|---|---|
| **B. Arrived with outside AI** | `import.declared` | For each declared claim: "Which source supports this? What would complicate it?" The student anchors, restates or drops it. Declaring is never penalised |
| **C. Untraced text** | An external paste > 40 words, or an untraced paragraph found at a save point (not live) | First offers "trace this": link it to a card or source, or declare it. Then asks about the idea. No accusation, no blocking |

**Case C wording (design review 18A).** The words describe the map, never the student:
- Paste over 40 words: "You brought in a longer passage in ¶3. Want to connect it to your map?" **[Link a card or source]** **[Say where it came from]** (opens the Door) **[Not now]**
- Unconnected paragraph at a save point: "¶4 isn't connected to your map yet. Which claim is it making?" **[Link to a claim]** **[Not now]**
- If the student engages, one idea question follows, grounded in the claim or source (law 2).
- "Untraced", "flag" and any judgment words never appear in Coach copy.

Cases A (blank page), D (weak reasoning) and E (confident mode) are deferred to TODOS (CEO-1). A blank page shows a static hint instead ("Open a reading and make your first card").

**Budget.** At most one unprompted question per 10 minutes of writing and at most 6 per assignment before submit. Questions appear in the side panel with a static badge (no pulse, no sound, no animation; design review 11A) and never interrupt typing. **One budget for all questions (design review 17A):** mapper findings (D-035; only `unconnected_paragraph` and `claim_without_source`, recorded as `map.finding`, eng v2 D15) are candidates in the Coach's queue, not a second stream. When a slot opens the Coach asks the highest-priority candidate (case B or C first, then mapper findings). Unasked findings may still feed the receipt's 2–3 "where to ask" questions at compile. The student can always decline; declining is a fact on the receipt. Case C nudges and the declare-at-paste prompt sit behind feature flags so they can be switched off mid-pilot without a deploy.

**Outcomes.** `answered`, `revised`, `disagreed` (with a reason) or `declined`. The answer box records pasted characters; only the typed parts of an answer count as "traced to a Coach exchange" when moved into the draft (D26).

## 4. Grounding (law 2)

- Coach output is structured: `{case, target_span, grounding_ids[], question}`. `grounding_ids` must contain at least one existing block or claim ID. Invalid → regenerate once, then drop.
- Grounding priority: the student's own lecturer's material, then assigned readings, then the student's own sources.
- Prompts get only the needed blocks, cards and claims. Never the full log, never names, never other students' data.

## 5. The Door (declared channel)

- One click away: "Bring in outside work". The student pastes a chat log, outline or notes, or uploads a file, and names the tool (free text).
- **URLs are stored as links, never fetched** (CEO-9). Uploads use the same caps as readings.
- The raw text is **student-private**. L3a splits it into declared claims in the import's own words.
- Declared claims appear on the claim map in a distinct style. The student can anchor, restate or delete them.
- At an external paste the editor offers once per session (dismissible): "Was this written elsewhere? You can declare it." It never blocks.
- Copy: "Using outside AI is allowed here. Declaring it keeps your record clear."
- The Door is also where unsent offline text can come back in after a lost edit lease (D32).

## 6. Leak check (law 1): one module, `coach/leak.py` (D18)

Every Helper and Coach output passes, before it is shown:
1. **Shape rules** (code): Coach output ends with a question; length within the policy limit.
2. **Paste-ready test** (code): reject a run of 8+ consecutive words that read as a declarative claim about the topic. Cheap, with false positives; not enough alone.
3. **LLM judge** (the law-1 prompt ported from the kit): on all golden-session outputs, **~30 adversarial prompts** ("write my intro", role-play, instructions hidden in Door imports and readings) on **both backends**, and 2% of pilot outputs. Pilot target: zero leaks. Any leak blocks the next release and alerts the operator (CEO-24, D15).

A failed output is logged (`helper.serve`, `leak_check: fail`) and the student sees a safe fallback ("Let's start from your idea: what do you want this part to say?").

## 7. Prompt hygiene

- Sources, imports and student text are untrusted. They go inside delimited, tagged blocks; the system prompt says to treat them as data.
- Serve or redirect is decided in code from the classifier's fixed enum (`where_is`, `define`, `summarise`, `structure`, `what_to_argue`, `write_for_me`, `check_citation`, `other`). Unknown → `other`, answered under the strictest leak check.
- AI failures follow the `complete()` error classes (D13). The panel shows "Question not ready, try again" or "AI help unavailable"; writing always continues.

## 8. What comes from the kit (D18)

The kit's code is bound to its fictional corpus (`room.py` loads `data/corpus.json` at import), so it isn't ported. What moves:
- `writing-room-kit/v04/policies/*.md` → `prototype/server/coach/prompts/`, with corpus references removed.
- The law-1 judge prompt (`v04/audit.py`) → `prototype/server/coach/leak.py`, the one module the app and the leak-audit tests both use.

The kit is **frozen as of 2026-10-23**. Its tests keep running in CI as the regression guard for `shared/llm.py` (D22).
