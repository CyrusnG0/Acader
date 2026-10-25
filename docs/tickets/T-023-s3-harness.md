# T-023: Executable preregistered S3 evaluation harness

**Pickup:** blocked. **Dependencies:** T-007 plus founder-approved frozen S3 protocol and threshold. Follow [pickup rules](README.md); the board is authoritative for current ownership. Branch: `task/T-023-s3-harness` from checker-accepted main. Claim only your row before coding.

## Read first

AGENTS.md, docs/STATUS.md, docs/TASKS.md, EXPECTATIONS.md, docs/OPEN_LOOPS.md, PRODUCT.md, then these spec references (unqualified design filenames are in design/): evaluation.md §1 S3; provenance.md §§4–5; accepted T-007 preregistration. Read the existing code and dependency handoffs; these tickets do not override the design specs.

## Scope and boundaries

Own prototype/spikes/S3/ and its tests/documentation. T-007 may finish with a draft and threshold still pending: its done status alone does not unlock this task. Implement only after the protocol, numerical threshold and input contract are frozen with the required founder approval. Do not label the corpus yourself or choose thresholds after observing results.

Validate at least 40 independently labelled pairs, preregistered splits/metrics and provenance of labels. Support deterministic stub execution and stored-output replay, missing/error reporting and a reproducible report. A report must distinguish simulated stub output from actual model evidence. No live calls in ordinary tests. Missing labels or protocol leaves the actual run blocked, not replaced with invented evidence.

This ticket builds the harness only. A later founder-authorized live evaluation with independent labels and the frozen protocol is needed before any L3b execution; failure or missing evidence leaves L3b off. Do not change engine bands or enable flags.

## Required evidence

Input validation for counts/labels/splits; exact protocol metrics on known small fixtures; missing/error accounting; deterministic replay; no network in stub mode; report clearly marks simulated results and cannot claim S3 passed from a stub run.

Run relevant new tests, full prototype tests with ROOM_LLM=stub, and the kit's 29 regression tests. For UI changes also run web tests, typecheck/build and focused browser checks. Record actual environments and results; never claim unobserved CI. No secrets, real student data, live providers or shared/llm.py behavior changes.

Return commits, a dated docs/handoffs note, files changed, reproduction commands, EXPECTATIONS A plus the relevant C/H requirements, failures and proposed decisions. Set your own row to review. Only the checker merges, marks done and updates shared tracking. M1 human reading and every pilot gate remain separate; this ticket cannot satisfy them.
