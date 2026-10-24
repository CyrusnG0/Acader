# The receipt

Status: **reviewed (CEO + eng 2026-10-23, design 2026-10-24)** · Last updated: 2026-10-24
Implements: D-025, laws 5, 6 and 10; CEO-3, CEO-5, CEO-7, CEO-17, CEO-20, CEO-21; D7, D20, D27, D28, D31 ([CEO record](../docs/designs/ceo-review-v1.md), [eng record](../docs/designs/eng-review-v1.md)). Answers OL-032 (proportions) and OL-041 (stop it reading as a score). Validated against the nursing case in OL-034.

## 1. Job of the receipt

Replace "40 pages of log and five meetings" with **one page and one short conversation**. A teacher should be able to read it in under 3 minutes and know:
- what happened in the platform
- what the student said came from outside
- what has no trace
- the 2 or 3 questions worth asking

**It is a process profile, never a verdict.** It has no overall score, no colour that means "bad", and no ranking against classmates.

## 2. Layout (top to bottom)

The questions come before the numbers, and the blind spot sits next to the bar, so the bar isn't read as a score (OL-041).

**First screen (design review 2A):** items 1–4 only. Items 5–9 sit behind one disclosure, "How it was built (details)", closed by default and expanded in print. Item 10 and the seal live in "About this receipt" at the foot.

1. **Header:** student, assignment, submitted date, words, number of sources used. No hash here: the seal hash and `verify` move to "About this receipt" (2A), so the first impression isn't a certificate.
2. **Summary in one sentence**, generated from facts only. Example: "Built over 6 sessions from 4 sources; most claims trace to passages the student anchored; one paragraph was pasted from outside and partly rewritten; two Coach questions were declined."
3. **Where to ask (2–3 questions).** Each shows the span it is about and why it was chosen ("this paragraph has no trace in the platform"). Each links to the chain. During an AI outage this section reads "questions pending" (CEO-7).
4. **How the work was built: the bar.** Five bands by words, and the same five by claims, in two thin bars:
   - Traced to a source or lecture
   - Traced to a Coach exchange
   - Declared outside help
   - Linked by student, not checked (D27), with the sub-count "of which N accepted from map suggestions" (eng review v2 D12)
   - Untraced

   **Band colours (design review 12A):** one hue (the accent blue) at falling strength, never good/bad colours. Traced to source = solid; traced to Coach = 70%; declared = 45% + dot pattern; linked by the student = 25% + diagonal hatch; untraced = paper with a hairline outline, no fill. Every band carries its text label (never colour alone) and survives greyscale print. `--ok`, `--warn` and `--bad` are banned from the bars, the chain view and the editor trail; `--bad` is for system errors only. The same scale paints "Show my trail" in the workspace.
   Directly under the bars, always: *"Untraced is not AI. It means this platform has no record of where it came from. Retyping, writing offline and outside help all look the same here."*
   There is no "polish only" band in v1 (CEO-3). Reworded text that hasn't been checked is untraced, with the note "reworded after tracing; not checked" (CEO-13).
5. **Thinking moments:** claims changed after meeting counter-evidence; sources set aside with reasons; disagreements with the Coach and the reasons given.
6. **Coach record:** questions by case, with outcomes (answered / revised / disagreed / declined). "Declined" is a fact, not a mark.
7. **Reading depth:** per source, which parts were opened and anchored. A small grid, not a score.
8. **Declared help:** tools named by the student, size of imports, how many declared claims the student later anchored.
9. **Other facts:** pastes (editor, cards, Coach answers) and replacement edits (spellcheck, autocorrect, extensions), as counts.
10. **What this record can't see:** retyped text, work done offline, outside help not declared, the student's understanding.

## 2a. The teacher's submissions list (design review 3A)

One row per student, **alphabetical by name only**: name · submitted date · status (`still compiling` with its release time · `ready` · `questions pending` · `discussed` · `record removed`, 9A). **No band columns, no sort or filter by band, no class averages.** Law 6 holds at the list level: nothing here ranks students by how traced their work is. "Mark as discussed" sits at the foot of each receipt and sets the status; it is the teacher's finish line, not a verdict. It is stored teacher-side (`receipt_status`: receipt_id, teacher_id, discussed_at, plus an audit row), never in the student's log, and is not shown to the student (eng review v2 D9).

## 3. Click-through: the chain view

Clicking any sentence opens its chain, left to right:

`source passage (highlighted block) → idea card (student's words, date) → claim node → drafts of this sentence (diff) → final sentence`

- Each step shows its event ID and date + hour.
- A broken chain shows where it breaks, in plain rounded words (design review 20A): "no card links here", "came in by paste on 2 Nov (140 words); about half reworded since" (rounded to none / some / about half / most / all), "pasted into a Coach answer", "this label couldn't be confirmed against its source". Exact figures stay in the JSON and the export.
- Link names (design review 4A) say who linked and whether it was checked: L3b-confirmed links read **"checked against the source"**; student-only links read **"linked by the student, not checked"**, or "linked by the student from a map suggestion" when the link carries `suggestion_id` (eng review v2 D12; reopens 4A for accepted suggestions only). Mapper suggestions (D-035) **never appear in the bars or the chain**; "About this receipt" shows only their count ("12 links suggested by the map, not checked; none of them counts as traced").
- "About this receipt" shows the seal ("Record sealed at submission. Check: `verify 3f9a…`" and "Notes added after submission are dated, not sealed.", D-041), what this record can't see (§2 item 10), the engine stamp (D20) and, if it applies, "built from the browser's copy (replay mismatch)" (D28).

## 4. How the questions are chosen

Candidates, in priority order:
1. Untraced claims that carry the argument (in the introduction or conclusion, or other claims depend on them).
2. Added propositions inside otherwise traced sentences (L3b, only if S3 passed).
3. Contradictions between paragraphs (L3c).
4. Inconsistent standards: a set-aside reason that also applies to a relied-on source, only on comparable metadata.
5. Declared claims never anchored to a source.
6. Student-linked claims that carry the argument.
7. An unanswered mapper finding (`map.finding`: an unconnected paragraph or a claim without a source), cited by its event_id and artifact_id. Never about a sentence the student answered "Not this" (eng review v2 D15).

At most 3, at most one per paragraph. Generated with L3e under these rules:
- About **the idea and the student's choices**, never about the trace ("How does renal clearance connect to your dosage point?", never "Did you write this?").
- **One of the four pillars** (reading, logic, writing, communication; coach-helper §3), looking forward: test the idea against a reading, a boundary condition, a qualifier or a sceptical reader. Never "how did you think of this?" Elaboration is taken at face value (D-046).
- Never built from construction order (which came first, card or paragraph), and never from a judgment of whether a Coach answer was good enough (D-046).
- Must cite grounding: the span plus a block or claim ID. No grounding → rejected (law 2).
- Answerable in about 30 seconds by someone who did the work.
- Passes the wording filter (§5) and the leak check.
- The generating AI output is stored and cited (D31).

## 5. Wording filter (law 10)

**Every rendered string on every surface** passes a filter before rendering: the receipt, the student preview, workspace UI strings, Coach and Helper output, and emails (design review 19A).
- **Banned everywhere:** detect, detected, catch, caught, cheat, cheating, ghost, forensic, AI-generated, suspicious, suspect, flag, flags, flagged, violation, integrity score, probability. Internal docs say "mapper finding", not "flag".
- **"Untraced" shown to a student** must have its gloss in the same view ("no record here of where it came from"); the Coach never uses it (18A).
- **Preferred:** traced, untraced, declared, where to ask, no record, the student chose.

A unit-tested list, plus a person reading every golden receipt before the pilot.

## 6. Data format

Compiled to JSON first, then rendered as HTML with a print stylesheet. **The receipt is a document, not a dashboard (design review 10A):** one reading column (max 72ch), sections separated by a heading and a hairline rule, no boxed sections, print-first. Server PDF export is deferred (CEO-5).

```json
{
  "receipt_id": "r_…", "log_id": "…", "seal_hash": "3f9a…", "seal_seq": 412, "version": 2, "schema": 1,
  "status": "complete | questions_pending | replay_mismatch",
  "summary": {"text": "...", "event_ids": [...]},
  "questions": [{"q": "...", "span": {"from": 812, "to": 1004}, "why": "untraced_claim",
                 "grounding": ["b81", "c3"], "event_ids": [...], "artifact_ids": ["a_…"]}],
  "bands": {"total_words": 1500,
            "by_words": {"traced_source": 870, "traced_coach": 120, "declared": 150, "student_linked": 90, "untraced": 270},
            "by_claims": {"traced_source": 7, "traced_coach": 1, "declared": 1, "student_linked": 1, "untraced": 2}},
  "moments": [...], "coach": {...}, "reading": {...}, "declared": {...}, "facts": {...},
  "inferred_links": 5, "map_suggestions": 12, "blind_spots": ["retyped", "offline", "undeclared_outside", "understanding"],
  "engine": {"version": "...", "git_sha": "...", "lock_hash": "...", "editor_pair": "tiptap-pm 3.32.0 / prosemirror-py 0.6.1", "flags": {"l3b": false}, "thresholds": {...},
             "models": {"receipt_question": "deepseek/deepseek-chat"}, "prompt_hashes": {...}}
}
```

**No floats anywhere in the receipt JSON** (D-041): shares are integer word counts and the renderer rounds, so `receipt_hash = sha256(canonical_json(receipt))` is well defined. An id in `event_ids` is the event's `seq`.

Every element carries `event_ids`; AI-derived elements also carry `artifact_ids`. `verify` checks both. Same log + same engine stamp + stored outputs → a byte-identical receipt (D20, D31).

## 7. Release and the student view

- **Student preview, before release:** bands, facts, and which spans may be asked about, **not the question text** (CEO-20). The student can add a short note to any span ("drafted on paper in class") and a link they forgot. Both are new events marked "added after submit"; links never change the bands (CEO-17).
- **Preview layout (design review 8A):** same order as the teacher's first screen, so there is no hidden version.
  ```
  Here's what your teacher will see.                      Nothing here is a grade.
  Summary sentence (same as the teacher's)
  Bars by words / by claims + "Untraced is not AI. …"
  Parts your teacher may ask about
    ¶3 "Rapid boluses harm after the first hour…"
       Your teacher may ask about this part. Be ready to explain your thinking.
       [Add a note]  [Link a card or source]
  How it was built (details) ▸
  Your teacher sees this from [time]. Until then you can add notes and links.
  ```
- **Release to the teacher:** at the latest of the deadline, submit + 24 h, and questions compiled, but **no later than the latest of (deadline, submit + 24 h) + 48 h**. At that cap the receipt is released with "questions pending", the operator is alerted, and questions arrive later marked "added after release" (CEO-21, D7). Until release the teacher sees "Still compiling. Ready by [time]" (6A), never a bare status.
- Notes added after release are marked "added after release".
- **Withdrawal between submit and release (P-15, design review 9A).** Allowed (law 7).
  - Student confirm: "Remove your process record? Your teacher will see that the record was removed, not why. Your submitted work stays submitted. Removing it is your right and isn't treated as a mark. This can't be undone." **[Keep my record]** **[Remove it]**
  - Teacher list status: `record removed`. Teacher view, in place of the receipt: "The student chose to remove their process record before release. The submitted work is unchanged. Talk with the student about it as you would for any work written outside this platform." No seal, bars or questions.
  - **Jobs (eng review v2 D10):** `record.withdrawn` cancels queued compile, L3, question and release jobs for that log in the same transaction; a running job checks the withdrawn flag before it writes and stops; a compiled but unreleased receipt is deleted with its stored outputs. A teacher-side tombstone (log_id, withdrawn_at) drives `record removed`.
  - Edits after submitting are never part of the submission; the editor says so: "Edits after submitting aren't part of this submission."

## 8. Worked example: the nursing case (for OL-034)

Fictional reconstruction for the walkthrough. Not real data.
- Assignment: a care-plan rationale, 1,200 words, 3 readings.
- Summary: "Built over 4 sessions from 3 readings. 9 of 12 claims trace to passages the student anchored. One paragraph (¶4, 180 words) was pasted from outside on 3 Nov and about half rewritten. Copilot was declared for the outline."
- Where to ask: (1) ¶4's mechanism for hypotension after rapid infusion, added beyond the student's card; (2) why the student chose the second reading over the guideline for the monitoring interval.
- The teacher asks both in 5 minutes. The 40-page log is never needed; the declared Copilot outline appears in "Declared help", and its raw text stays with the student unless they share it.

The test (OL-034, CEO-19): does the real teacher agree this would have ended the dispute faster, and do our questions beat essay-only questions in the blind test? The hard case (some untraced text and lingering doubt) is shown too.
