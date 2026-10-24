# CLAUDE.md: agent orientation for Acader

> Read this file first. It says what we are building, where everything lives, the rules you must not break, and how to leave the repo for the next agent.

## 1. What this project is (30 seconds)

**The Writing Room** (repo name "Acader"; product name not final, OL-001) is a **writing platform that schools buy and students write their assignments in. The process is the evidence.**

- While a student reads, plans and writes, the platform records **where each part of the work came from**: a source passage, a lecture, a Coach exchange, declared outside-AI help, or nowhere we can see.
- At submission, the teacher gets a one-page **receipt**: what was traced, declared and untraced, plus 2–3 questions worth asking. **It shows where to ask, never a verdict.**
- A **Helper** answers (reading, finding, citing). A **Coach** asks questions that make the student's idea stronger. Neither writes the student's work.
- We **assume outside AI is always available** and don't try to block it. Untraced is not AI.

Source of truth for product intent: **[PRODUCT.md](PRODUCT.md)**. If any doc disagrees with it, PRODUCT.md wins unless a later entry in [docs/DECISIONS.md](docs/DECISIONS.md) overrides it. Current direction: D-024 to D-030 (locked 2026-10-22).

## 2. Cold-start reading order

1. This file (§8 says which role you are: lead, worker or checker).
2. [docs/STATUS.md](docs/STATUS.md): where things stand and the single next action.
3. [docs/TASKS.md](docs/TASKS.md): the task board. Leads pick their task here.
4. [EXPECTATIONS.md](EXPECTATIONS.md): the checklist every finished task must pass.
5. [docs/OPEN_LOOPS.md](docs/OPEN_LOOPS.md): open questions, blockers and TODOs.
6. [PRODUCT.md](PRODUCT.md): what we build and why.
7. [design/README.md](design/README.md): how it's built (architecture, workspace, event log, provenance, receipt, reading aid, Coach/Helper, privacy, evaluation, build plan).
8. [docs/UPDATE_LOG.md](docs/UPDATE_LOG.md): what each past session did (newest first).
9. [docs/DECISIONS.md](docs/DECISIONS.md) and [docs/GLOSSARY.md](docs/GLOSSARY.md) when needed.

## 3. Repo layout

```
Acader/
├── CLAUDE.md, README.md, PRODUCT.md, EXPECTATIONS.md (task checklist), CHANGELOG.md, TODOS.md
├── design/               ← v1 engineering designs (read design/README.md)
├── prototype/            ← v1 code (server/, web/, fixtures/, spikes/); empty until the build starts
├── shared/llm.py         ← the one DeepSeek client (used by the kit and the prototype)
├── docs/
│   ├── STATUS.md, TASKS.md (task board), UPDATE_LOG.md, OPEN_LOOPS.md, DECISIONS.md, GLOSSARY.md
│   ├── handoffs/         ← one note per finished task, read by the checker
│   ├── designs/          ← review inputs and history (writing-platform-v1, provenance-engine, process-evidence-room)
│   ├── renewed-direction/← pitch scripts, verified sources, the renewed proposal
│   ├── research/         ← market research, deep-research reports and notes, brainstorm records
│   └── interview-script.md, outreach-data-note.md
├── writing-room-kit/     ← simulated experiments v0.1–v0.5 (v04/ engine) + hosted static demo (web/)
└── archive/              ← superseded material (earlier proposals, design v1, code track, stray copies)
```

## 4. Non-negotiable rules (product law; do not violate in code, copy or design)

1. **Help students think; never think for them.** Never write the student's prose or invent their argument. AI may change *structure* using *the student's own words*.
2. **Helper answers, Coach asks.** Coach questions are grounded in course material and the student's own trail (they cite block or claim IDs), never in a generic prompt.
3. **Make the right path the easiest one.** Remove mechanical cost (finding, reading, citing). Keep the thinking cost (arguing, choosing, explaining).
4. **Outside is free.** Assume outside AI is present. The Door imports anything and passes no judgment. Declaring is never penalised.
5. **Typing is not proof.** The trace is evidence of the student's thinking (writing traced back to its claim map and sources) and of *where to ask*. The conversation is the gate. Accessibility alternatives are mandatory.
6. **Never a verdict.** The receipt is a process profile with no score. Untraced is not AI. A human decides any consequence.
7. **Students own their process data.** Schools see the receipt and derived signals only. Course materials never leave their tenant. **Record what changed in the text, not how you typed it**: no keystroke timing, webcam, screen capture or biometrics.
8. **Professors are heroes.** Explanations and grounding point first to the student's own instructor's material.
9. **Scope discipline.** A writing platform for school work. Not a general notes app. The code track is parked (D-030).
10. **Wording discipline.** Never "detect", "catch", "cheat", "AI-generated", "forensic", "suspect" or "suspicious". Never promise "no cheating" or "100%". Promise *evidence on every submission* and *where to ask*. The selling point is thinking, never time saved.

## 5. Current focus

**Prototype v1** for one real class first, then more (D-029). **Design is finished; building starts now.**
1. Reviews: all done (CEO D-032/D-033, eng D-034, design D-036, eng v2 D-037). Latest direction: the live map is the product (D-035); in the pilot it is the outline the student builds, and the mapper is a flagged experiment (D-037); every new idea gets one pillar question, whatever its origin (D-038).
2. **M0 now**: scaffold, schema, LLM boundary, spikes S1/S2/S5, preregistration, golden-set sources, DESIGN.md. See [docs/TASKS.md](docs/TASKS.md).
3. Then M1–M5 and M4m ([design/build-plan.md](design/build-plan.md)); ≈ 35–36 build days.

Don't claim more than the engine can establish ([design/provenance.md](design/provenance.md) §2). No real student touches the system before the pilot gate in build-plan.md §4.

## 6. Session protocol (how to leave the repo for the next agent)

> In the multi-agent flow (§8), **leads and workers write only their own code, docs and handoff**; the **checker** does the shared-file steps below.

At the **start** of a session:
- Read STATUS.md and OPEN_LOOPS.md. Do not redo work marked done, or reopen items marked decided, without a reason.

At the **end** of every session that changes anything:
1. **docs/STATUS.md**: overwrite the snapshot (phase, what works, what is in progress, the *single* next action, last-updated date).
2. **docs/UPDATE_LOG.md**: add a new entry **at the top** with the date, a summary, files touched, and loops opened or closed.
3. **CHANGELOG.md**: add lines under `[Unreleased]` for repo-level changes.
4. **docs/OPEN_LOOPS.md**: add new loops with the next free `OL-xxx` ID; move resolved ones to *Closed* with the resolution and date. Never reuse IDs.
5. **docs/DECISIONS.md**: record any decision the user locked in (`D-xxx`, with context and consequences).
6. If a design changed, update the doc in `design/` and its row in [design/README.md](design/README.md).

Conventions:
- Dates are absolute ISO (`2026-10-23`), never "yesterday".
- Mark tested claims **[VALIDATED]** and guesses **[ASSUMPTION]**. Kit results are simulated: never present them as evidence about real students.
- Numbers and quotes in pitches and demos come only from `docs/renewed-direction/sources-verified.md` or validated results.
- Change PRODUCT.md only when a decision changes product intent, and cite the D-xxx.

## 7. Tech notes

- **Stack (locked by /plan-eng-review, D-034):** Python 3.12 + FastAPI; Vite + TypeScript + TipTap (ProseMirror) + PDF.js with one `web/schema.json` (server replay via prosemirror-py); SQLite (WAL) everywhere; DB job queue; PDF parser chosen by spike S2; DeepSeek + an OpenAI-compatible backend via `shared/llm.py` (wrap it, don't change it).
- **Tests:** set `ROOM_LLM=stub` for deterministic LLM output. Kit and web tests: `cd writing-room-kit && ROOM_LLM=stub python3 -m pytest -q v04/tests web/tests`.
- **Secrets:** `DEEPSEEK_API_KEY` in the repo-root `.env` (gitignored) or the host's secret store. Never commit it.
- **Hosted demo:** `writing-room-kit/web/` (FastAPI, Fly.io; build from the repo root, see its Dockerfile). `/demo` is the static click-through.
- Large media and run dumps must not be committed (see `.gitignore`).

## 8. How we work: lead, worker, checker

Several conversations run at once. Each has one role:

| Role | Who | Does | Never does |
|---|---|---|---|
| **Lead** | One Opus conversation per task, started by the founder | Claims one task in [docs/TASKS.md](docs/TASKS.md) (Owner + `in progress`); reads the docs it cites; plans; hands well-specified pieces to workers; reviews their output; runs the tests; writes a handoff in [docs/handoffs/](docs/handoffs/README.md); sets the task to `review` | Edit STATUS, UPDATE_LOG, CHANGELOG, DECISIONS or other tasks; decide product questions (it writes them as *proposed decisions* in the handoff) |
| **Worker** | Subagents launched by a lead: Sonnet, or DeepSeek where TASKS.md marks **D** | One narrow, fully specified piece (a module, its tests, fixtures) | Choose wording, prompts, product behaviour or band rules; touch files outside its piece; see `.env` |
| **Checker** | The founder's long-running review conversation | Reads each handoff; runs the tests; ticks [EXPECTATIONS.md](EXPECTATIONS.md) line by line; marks `done` or sends back the failing lines; merges; does the §6 protocol (STATUS, UPDATE_LOG, CHANGELOG, OPEN_LOOPS, DECISIONS); takes proposed decisions to the founder; adds the next wave of tasks | Build features itself |

Rules for every role:
- **Work on a branch per task** (`task/T-0xx-short-name`) or a worktree, never directly on `main`; the checker merges.
- The docs in `design/` are the spec. If something is unclear or wrong, stop and write it as a proposed decision in the handoff; don't improvise.
- `ROOM_LLM=stub` for tests; no live LLM calls except golden release runs.
- DeepSeek workers only if F-005 in TASKS.md is approved; they never receive `.env` or anything outside the repo.

## Skill routing

When the user's request matches an available skill, invoke it via the Skill tool. When in doubt, invoke the skill.

Key routing rules:
- Product ideas/brainstorming → invoke /office-hours
- Strategy/scope → invoke /plan-ceo-review
- Architecture → invoke /plan-eng-review
- Design system/plan review → invoke /design-consultation or /plan-design-review
- Full review pipeline → invoke /autoplan
- Bugs/errors → invoke /investigate
- QA/testing site behavior → invoke /qa or /qa-only
- Code review/diff check → invoke /review
- Visual polish → invoke /design-review
- Ship/deploy/PR → invoke /ship or /land-and-deploy
- Save progress → invoke /context-save
- Resume context → invoke /context-restore
- Author a backlog-ready spec/issue → invoke /spec
