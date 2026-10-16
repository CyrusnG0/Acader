# TODOS

## Runner (viva pilot)

### Bound total wait for question generation

**What:** Put a total time budget on question generation (across retries) and show a timeout message on the student page.

**Why:** Worst case today is 3 attempts x 60 s = 180 s per question set (360 s in blind mode) behind a spinner with no message (`runner/viva.py` `MAX_RETRIES`, `anthropic_complete` timeout; `runner/static/student.html`).

**Context:** Deferred by /plan-eng-review R12 (`docs/designs/eng-review-runner-demo.md`, answer D11 "A"). The right number should come from measured Anthropic p50/p95 latency, which does not exist yet because the real-LLM path has never been run (OL-017). Start by measuring, then set the budget to roughly 2-3x p95, keep the existing "generation failed" message, and add a timeout-path test. Accepted shortcut: Completeness 7/10, upgrade when OL-017 reports latency.

**Effort:** S
**Priority:** P3
**Depends on:** OL-017 (run the runner with a real Anthropic key and record latency)

## Completed
