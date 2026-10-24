# Code Track MVP (Phase 1, M8)

**Status:** draft · **Implements:** proposal §4.3, §10 Phase 1 · **Decision:** D-002
**Open loops:** OL-003 (variant quality), OL-005 (design partner), OL-008 (stack), OL-009 (viva triggers), OL-010 (tiers)

## 1. Acceptance criterion
> One real course assignment completed end-to-end by non-founders.

End-to-end means: course videos are uploaded and turned into a KG. A reference solution produces variants, which the teacher reviews. Students complete their variants in the no-paste editor and answer line-level challenges. Each student gets a defense record and a per-student understanding summary.

## 2. Scope
**In:** minimal ingest, the miner, transcript and topic structuring (enough to ground questions), the variant engine with teacher review, the no-paste editor with keystroke timeline, line-level viva, the defense record, the understanding summary, and a minimal Proof.
**Out:** the writing track, dashboards, parent layer, LMS integrations (manual export is fine), and cross-school L2.

## 3. Variant engine
- Input: one teacher reference solution, plus an optional problem statement, plus the course KG.
- Output: N **isomorphic variants**, each with a different scenario, parameters or constraints but the same core concept, a reference solution, and tests.
- Every variant is released only after **teacher review**, which takes one click to approve, edit or reject.
- Design for deliberate cohesion: multiple functions or classes, because LLMs struggle there (proposal §6, arXiv 2410.09318).
- **Quality probe first (OL-003):** generate 3 variants from one real solution and score difficulty parity. Candidate parity dimensions are concepts exercised, LOC, number of functions or classes, test count and difficulty, and the time a TA takes to solve. **[ASSUMPTION]** Pass bar to be defined.

## 4. Line-level viva (OL-009)
- Pasting is disabled and the student types every line. Keystrokes are recorded as process evidence. This is an *entry condition*, not proof (D-005).
- At **key lines** the Coach stops the student with a question such as "why this approach here?", "what does this function do?" or "what breaks without it?"
- Questions are generated from the **course KG**, so they cite the lecture or board where the concept was taught. This should feel like *their* teacher asking, not a quiz bank.
- Candidate key-line heuristics **[ASSUMPTION]**:
  - lines that implement the assignment's core concept (mapped through the reference solution diff);
  - control-flow decisions such as loop bounds, base cases and invariants;
  - calls to non-trivial library functions;
  - bursts (large correct blocks appearing quickly), which escalate questioning.
- Answer grading: an LLM judge against the reference concept explanation from the KG. The result is Strong / Partial / Needs oral check. This is never a penalty (D-006).
- Coach frequency can be tuned by the student, but there is a minimum floor for graded work.

## 5. Outputs
- **Runnable code** that passes the variant's tests.
- **Defense record:** each challenge with its line, question, the student's answer, the judgment and the KG anchor.
- **Understanding summary per student:** concepts demonstrated, concepts that are shaky, and a recommended oral check if needed.
- **Minimal Proof:** the artifact plus process signals plus comprehension dimensions (the full schema arrives in M10).

## 6. Accessibility
Instructor-approved alternatives to forced typing are required (proposal §8.3). For example, dictation or assistive input with more viva weight.

## 7. Open design questions
- Supported languages for the MVP (Python only?).
- Sandbox for running student code (container or WASM).
- How much KG is needed: a full M2–M5 pipeline, or a hand-seeded KG for the first pilot course?
- Where the defense record is stored (L3, student-owned) and what the teacher sees (derived).
