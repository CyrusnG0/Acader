# T-009: nursing walkthrough and blind-question protocol

## Pickup and purpose

Ready, no task dependencies for designing the protocol. Claim only T-009 per [pickup rules](README.md), branch `task/T-009-walkthrough`. The university team has supplied a real use case and pain point. This task prepares a test of receipt usefulness; it does not reclassify that supplied context as an unvalidated idea or claim the test has already happened.

## Read first

- design/evaluation.md §§4–7 (the walkthrough is §6); design/receipt.md §§2–4, 7–8.
- design/build-plan.md M1/M2 and pilot gate; PRODUCT.md; OL-026/OL-034/OL-041.
- docs/handoffs/2026-10-24-T-016-receipt-compiler.md and pending proposals OL-047.
- prototype/fixtures/golden/honest-nursing.yaml, thin-honest.yaml, ai-expanded-card.yaml and pasted-rewritten.yaml. Compiled stub questions are not evidence of live question quality.

## Deliverables

- `docs/research/nursing-walkthrough-protocol.md`: objective, participant roles, consent/data minimisation, reconstructed synthetic case, hard/ambiguous case, materials checklist, facilitator script, neutral interview questions, practical-use and misreading criteria, reporting template and stopping conditions.
- `docs/research/blind-question-preregistration.md`: comparable platform-grounded versus essay-only questions, same essay/context constraints, balanced randomisation and hidden condition labels, rating rubric, primary outcome, ties/missing answers, fixed win rule, sample-size rationale, analysis method and a sealed condition-key procedure. Preserve the distinction between teacher usefulness ratings and student understanding; no automated grading of Coach answers.
- `docs/research/nursing-walkthrough-results.template.md`: empty form for actual observations, verbatim quotes with consent, misread lines, unresolved questions and the blind-test result. Clearly label it an unfilled template.
- Dated T-009 handoff with files, checks, EXPECTATIONS A coverage and proposed decisions.

The pilot validity design calls for 50-vs-50 blind question ratings (OL-026). Distinguish that target from an initial walkthrough sample; do not quietly replace the larger design with a convenient small demonstration. Propose any unchosen threshold/sample allocation explicitly. Do not book, contact or message participants; founder owns recruitment and approvals.

## Acceptance and checks

Someone other than the author can run the session without leading the teacher or revealing condition labels. The hard case is included. The script asks what remains unclear, what could be misread and what evidence the teacher would still want. It does not assume the receipt resolves the dispute.

Protocol design can reach review before T-017. Execution waits for actual rendered receipts, suitable question outputs, participants and any required approvals. No real case logs/student identities in Git, no live LLM runs, no invented results or claims of M2 completion. Verify cited fixtures/paths and internal consistency of randomisation, outcome and win rule; run git diff --check. Record tests actually run and explicitly account for EXPECTATIONS A's suite requirement. Return handoff at review; checker records real results later.
