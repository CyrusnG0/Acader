# T-007: preregister S3 and S4

## Pickup and purpose

Ready, no task dependencies. Claim only T-007 per [pickup rules](README.md). Branch `task/T-007-preregistration`. This is protocol preparation, not permission to run a live experiment or enable L3b. S3 tests whether claim comparison adds unsupported propositions to traced work; S4 checks explainable bands in known simulated behavior.

## Read first

- design/evaluation.md §§1, 2a, 4, 7; design/provenance.md, especially the L3b gate.
- design/build-plan.md M0/M2; D-050/D-051; OL-040/OL-046.
- prototype/fixtures/README.md, sources.yaml and mapper_seed_labels.yaml. The mapper labels are a separate evaluation, not S3 results.
- writing-room-kit/RESULTS.md and the C1/C4/C11 fixture/run definitions; inspect actual available files before naming an input path.

## Deliverables

- `prototype/spikes/S3/PREREG.md`: question, hypotheses, at least 40-pair sampling plan, positive/negative and added-proposition labels, non-native polish and wrong-node cases, independent annotation instructions, disagreement handling, frozen split/version, model/prompt settings, retry/error/missing-result treatment, false-traced metric and a numerical pass rule fixed before execution.
- `prototype/spikes/S3/labels.template.csv`: empty annotation template with stable pair/source identifiers and fields matching the protocol. Do not fabricate human labels or mark existing draft seeds independent.
- `prototype/spikes/S4/PREREG.md`: exact available C1/C4/C11 inputs, mapping into current engine concepts, expected behaviors, word/claim denominators including D-050 mechanics, explanatory review rubric, pass/fail reporting and explicit limitations of simulation.
- `docs/handoffs/YYYY-MM-DD-T-007-preregistration.md`: review evidence, unresolved founder inputs and proposed decisions.

If a threshold, annotation independence or a v04-to-v1 mapping is not locked by the spec, state a concrete proposed value with rationale and mark it pending checker/founder disposition. Do not invent a locked product rule. Name the independent labeller only when the founder has supplied a real person; otherwise identify the required role and record assignment pending. Draft preparation can finish without pretending independent labels or an approved preregistration exist.

## Acceptance and checks

A new reader can select the pairs, annotate without seeing model predictions, calculate the metric and reproduce the go/no-go result without choosing thresholds after seeing results. S3 failure or missing evidence leaves L3b off. S4 observations are simulated, never evidence about real students. No live calls, prompt tuning, fabricated participants, new source licences or changes to the frozen kit.

Check each cited input path, template consistency, case count plan and denominator definitions. Run git diff --check. This documentation/template task adds no runtime behavior; record regression tests not rerun if none were needed, and explicitly account for EXPECTATIONS A's suite requirement in the handoff for the checker. Claim only A lines actually evidenced. Set review, never done. Founder/independent-person actions remain pending and visible.
