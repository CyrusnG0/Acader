# T-007: preregister S3 and S4

- **Worker:** worker-T-007   **Workers used:** none (DeepSeek worker executed the ticket directly)
- **Branch or worktree:** `task/T-007-preregistration`, worktree
  `/Users/micmic/Documents/GitHub/Acader-wt-T-007-preregistration`
- **Commit(s):** `ecade9c` (deliverables; this handoff is a follow-up commit on the same branch)
- **Status set:** T-007 `review`; no other task row changed.

## What changed

- `prototype/spikes/S3/PREREG.md`: draft `s3-prereg-v1`. Question, decision it gates,
  definitions, pair format, 48 evaluation pairs plus 12 development pairs across eight families,
  independent-labeller rules, calibration, audit and adjudication, frozen split/version, prompt
  and output schema, both-backend proposal, retry/error/missing-result rules, pair-level metrics,
  a fixed pass rule, execution/reporting and limitations.
- `prototype/spikes/S3/labels.template.csv`: header-only annotation template (27 columns, zero
  data rows). No human labels or participants are invented. The template excludes model output
  and hides `family` from the annotator view.
- `prototype/spikes/S4/PREREG.md`: draft `s4-prereg-v1`. Exact C1/C4/C11 input paths, arm
  definitions, a deterministic mapping into v1 concepts, word/claim denominators including
  D-050 mechanics, expected bands, proposed pass rules, review rubric, reporting format and
  simulation limitations.
- `docs/TASKS.md`: only T-007's Owner set to `worker-T-007` and Status set to `review`.

No design doc, shared tracking file (STATUS, UPDATE_LOG, CHANGELOG, OPEN_LOOPS, DECISIONS), source
licence, frozen kit file, `shared/llm.py` or runtime code changed.

## Acceptance evidence

- **A new reader can select the pairs:** S3 §4–§5 give the stable fields, the 48/12 split and the
  eight-family counts. The family counts were checked: 48 evaluation pairs, 32 positive and 16
  negative; the 12 development pairs are separate and never scored.
- **Annotate without seeing model output:** S3 §6 and the template. The labeller receives only
  sentence, claim, anchored-passage text and IDs; `family`, split (except calibration), model
  output, prompt and expected labels are withheld. The second annotator and adjudicator roles are
  independent and pending.
- **Calculate the metric and reproduce the go/no-go:** S3 §10 defines false-traced and false-added
  at pair level with integer numerators and denominators; §11 fixes the proposed pass rule before
  execution; §12 fixes the hashes, one-run rule and reporting fields. A threshold or prompt change
  requires a new version before any output exists.
- **Template consistency:** the CSV header parses as 27 unique columns and has zero data rows.
  Every CSV column is documented in S3 §6.5; the check reported no missing columns.
- **Input paths and counts were checked against the actual files:** six C1 run files, six C4 run
  files, six C11 run files and their six session mirrors each; `writing-room-kit/data/corpus.json`
  resolves all 327 citation block IDs used by the 18 runs (0 unresolved). C4 has one saved draft
  per run; the frozen draft-similarity rule classifies 3–4 paragraphs as outside in each of the
  six runs, so every run meets the arm rule's "at least two body paragraphs". All six C11 runs
  record 0 claim statements and 0 drafts, matching the frozen thin-trail mapping.
- **Denominators:** S3 uses the pair as the sampling unit and does not pool propositions across
  pairs. S4 uses `bands["total_words"]`, requires `mechanics == 0` by construction, and labels the
  paragraph-based claim units as a proxy because v0.4 has no claim map.
- **S3 failure or missing evidence leaves L3b off:** S3 §2 and §11 say so; incomplete, a low audit
  agreement, too many unresolved pairs or a hash mismatch is not a pass.
- **S4 remains simulated:** S4 §2 and §10 state that it tests band accounting, not inference, and
  that nothing in it is evidence about real students.
- **No live calls, prompt tuning, fabricated participants, new source licences or frozen-kit
  changes:** no provider call was made; `ROOM_LLM=stub` was used for both suites; the protocol
  names the future inputs but does not fetch or add a source.

## Tests run (exact commands and last lines)

Environment: `.venv` created with `/Users/micmic/miniconda3/bin/python3.13` (Python 3.13.13);
`pip install --require-hashes -r prototype/requirements.lock` succeeded (all hashes matched).
System Python 3.14.5 was not used for the tests.

- `cd /Users/micmic/Documents/GitHub/Acader-wt-T-007-preregistration/prototype && ROOM_LLM=stub ../.venv/bin/python -m pytest -q`
  → **840 passed, 1 warning in 9.14s** (warning: Starlette TestClient deprecation notice).
- `cd /Users/micmic/Documents/GitHub/Acader-wt-T-007-preregistration/writing-room-kit && ROOM_LLM=stub ../.venv/bin/python -m pytest -q v04/tests web/tests`
  → **29 passed, 1 warning in 0.24s** (same deprecation notice).
- Protocol consistency check (one-off Python): 27 CSV columns, 0 rows, no column missing from the
  S3 column table; 48 evaluation pairs (32 positive / 16 negative); run/session counts 6 each;
  327 citations checked, 0 unresolved; C11 all 0 claim statements / 0 drafts; C4 outside counts
  4, 3, 4, 3, 3, 3. All assertions passed.
- `git diff --check` → exit 0, no whitespace errors.

Web TypeScript/vitest tests and typecheck were **not rerun**: this task changed no web code. The
ticket's documentation-only scope needs no new runtime test; the existing suites above are the A
regression evidence.

## EXPECTATIONS sections claimed

- **A** (all nine lines):
  - Task scope: only T-007's deliverables and its own TASKS row.
  - Tests: both required suites ran with `ROOM_LLM=stub` and passed.
  - New-behaviour test: not applicable; this task adds documentation and a template, no runtime
    behaviour. The protocols define future tests (T-023 and the S4 adapter), not built here.
  - `shared/llm.py` unchanged.
  - No secrets; no `.env` read or written; no real student data.
  - No banned wording in the new files: a case-insensitive search for every term banned by
    EXPECTATIONS A and the ticket returned no matches in `prototype/spikes/S3/` and
    `prototype/spikes/S4/`.
  - No absolute promise about conduct or accuracy; the protocols promise evidence and a gate,
    never a verdict.
  - No design doc changed.
  - This handoff exists with files, tests and claimed sections.
- **B, C, D, E, F, G, H, I:** not claimed. The protocols reference the existing band, provenance
  and gate rules but implement no runtime behaviour and decide no product rule. Their proposals
  are explicitly pending (§Proposed decisions below).

## Not done / open

- The S3 pairs, prompt, `FROZEN.json`, labels, live run and `RESULT.md` do not exist. No model
  call was made. T-023 remains blocked until the checker/founder approve the frozen protocol and
  threshold (its own ticket says T-007 `done` alone does not unlock it).
- The S4 adapter, construction note, `results.json` and `RESULT.md` do not exist. S4 was
  preregistered only; its observations are future simulated evidence.
- The independent labeller, second annotator and adjudicator are **not named**. The founder must
  supply real people; the protocol records roles and `assignment_status: pending-founder`.
- The non-native cases need a qualified reviewer or an explicit `authored_simulation_only` mark.
- The S3 prompt and the replacement `claim_compare` output schema need approval before T-023.
- AGENTS.md is not present in this worktree (the ticket index says it is the founder's untracked
  file in the parent checkout). I read it read-only from the parent; I did not modify the parent
  checkout, any `.env`, or anything outside this worktree.
- I did not run a live S3 or S4 evaluation, did not tune a prompt, did not author pairs or labels,
  and did not touch main.

## Proposed decisions (the checker takes these to the founder; nothing here is decided)

- **PD-T007-1: S3 sampling and pass rule.** Adopt 48 evaluation pairs (32 positive / 16 negative)
  plus 12 development pairs, and the §11 bar: false-traced ≤10% with one-sided 95% upper ≤20%;
  false-added ≤15% with upper ≤35%; no family ≥6 pairs above 25% error; at least 40 pairs
  scoreable and human-resolved. *Recommend:* approve the shape and let the founder set the exact
  numbers before T-023 freezes them. The alternative is a stricter/looser single bar with no
  false-added guard, which an "always added" method could pass.
- **PD-T007-2: independent labelling and adjudication.** Use one independent labeller for all
  evaluation pairs, a 12-pair blind audit by a second independent annotator, Cohen's κ ≥ 0.60,
  and a third independent adjudicator for audit disagreements. *Recommend:* approve; name the
  people before execution.
- **PD-T007-3: both backends.** Require `deepseek` and `openai_compat` to pass the S3 bar
  independently; if the second backend is unavailable, S3 is incomplete and L3b stays off.
  *Recommend:* approve; this matches the both-backends habit elsewhere but is not in
  evaluation.md's S3 row.
- **PD-T007-4: replace the provisional `claim_compare` output.** The current `ClaimCompareOut`
  returns `{"relation": "same|related|different"}`, which cannot express propositions. T-023
  should replace it with the S3 §8.3 schema (`propositions[{text,status,evidence_block}]`) while
  keeping the task id. *Recommend:* accept; this is a schema extension, not an engine-band change.
- **PD-T007-5: what "C1 mostly traced" means in S4.** With L3b off and no quote marks, C1's
  student links are band 4 (`student_linked`), not `traced_source`. S4 reads the evaluation line
  as "mostly in a checked chain" (traced_source + traced_coach + student_linked ≥80%) and reports
  `traced_source` separately. *Recommend:* accept; otherwise S4 cannot pass without L3b, and the
  evaluation wording needs correction. This is the clearest spec tension found.
- **PD-T007-6: C4 outside paragraphs in S4.** Treat them as known only through a frozen
  draft-similarity note (≥0.50 to any saved draft = own; else outside). The engine never sees the
  note and the report must say the engine did not infer the outside paragraphs. *Recommend:*
  accept; there is no per-paragraph origin record in the v0.4 files.
- **PD-T007-7: C11 naming.** `evaluation.md` calls C11 "thin honest"; `PREREG-v0.5` defines it as
  `honest-ds` (DeepSeek honest operator). S4 uses the run definition (0 claim statements, 0
  drafts) and records both names. *Recommend:* accept and add a one-line alias in the design doc;
  do not rename the arm or treat its low kit score as a rate.
- **PD-T007-8: claim-unit proxy in S4.** Because v0.4 has no claim nodes, S4 counts linked
  paragraphs as claim units and unlinked paragraphs as paragraph units. This validates the
  denominator, not the student's real claim map. *Recommend:* accept and keep the "proxy" label
  in every table.
- **PD-T007-9: added propositions and bands.** `provenance.md` §5 says an `added` proposition
  "never changes a link: the sentence stays in its band", while §6 band 2 and D-050 item 7 make
  `added` block the traced-source and traced-Coach bands. The built engine follows §6/D-050.
  *Recommend:* keep the engine behaviour and correct §5's wording to "never changes the paragraph
  link; it can only become a pillar question". S3 is written against the §6/D-050 behaviour.

## Checker review (2026-10-25): passed, merged to `main` (8dd8db4)

- Independent read-only review by an Opus reviewer (fresh locked venvs, Python 3.14.5, `ROOM_LLM=stub`; no CI result claimed). Merged main: prototype suite **898 passed** (reported by the checker after all four merges); kit 29 per the handoffs. Docs-only branch; the reviewer did not rerun suites for it.
- Thresholds fixed before any data; labeller roles `pending-founder`; CSV header only; S4 labelled simulated; L3b stays off on any failure. Nit: S3/PREREG.md uses one judgement word for the experiment's PASS/FAIL, never about a student; "result" would be cleaner at the next version.
- EXPECTATIONS A ticked.
- Founder decisions (**D-056**): PD-1, -2, -3 accepted (bar, independent labelling with κ ≥ 0.60, both backends). **PD-5 rejected:** band 4 is not traced for C1; S4 needs s4-prereg-v2 (OL-051). PD-9: provenance.md §5 aligned to §6 (checker edit). The §6 "mechanics" line (D-050) was already present. PD-4, -6, -7, -8 and the S3 prompt remain open (OL-050); named labeller, second annotator and adjudicator still owed (OL-051). T-023 stays blocked on PD-4 and the prompt.
