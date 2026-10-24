# Can the process tell?
### A feasibility test of process-coherence receipts for AI-era writing tasks
*Cyrus Ng · CS, CUHK — [date]*

**Question.** When a task's evidence is gated behind understanding — students must ASK for what they need, and every citation must come from what they asked for — does the *process* distinguish honest work from outsourced (AI-written) work, even when the final essay looks equally polished?

**Setup.** Writing Room v0.2: sealed archive (12 fictional documents on HK subdivided-housing rent control), scripted librarian that answers with passages only, retrieval budget, citations anchored to personally-retrieved passages, in-platform editor. Mechanical receipt: traceability, continuity, non-orphan rate, structure, trajectory, citation spread. No timers, no surveillance, one attempt, untimed.

**Arms.** Same essay question. A: written outside the platform (AI use unrestricted, pasted in). B: written inside, honest process. C (hybrid): real retrievals, outsourced writing. Plus red-team attacks A1-A4 (fabricated process, retyped AI text, bought queries, citation padding).

**Results (model-simulated sessions, n={{N}}).**
{{TABLE: per-arm composite distributions + component means}}

**Findings.**
1. {{FINDING 1: honest vs pasted separation}}
2. {{FINDING 2: hybrid — what the score caught}}
3. {{FINDING 3: red-team — where the receipt breaks, and what fabrication costs}}

**What this is NOT.** Not a detector, not an accusation tool, not AI-proof. The design goal is structural: make outsourcing *harder, riskier, and more effortful* than genuine engagement (Winstone et al. 2026), and make understanding the key to the evidence rather than policing the output.

**Ask.** One course, one task, one week. A classroom pilot answers what simulation cannot: do real students' receipts show something the essay alone cannot?

*Engine, corpus and protocol: writing-room-kit (offline, browser-side, no data leaves the student's machine).*
