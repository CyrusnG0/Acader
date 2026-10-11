# CLAUDE.md — Agent orientation for Acader

> Read this file first. It tells you what this project is, where everything lives,
> the rules you must not break, and how to leave the repo for the next agent.

## 1. What this project is (30 seconds)

**Acader** (working repo name; product name not decided, see [docs/OPEN_LOOPS.md](docs/OPEN_LOOPS.md) OL-001) is
**understanding infrastructure for schools in the AI era**:

- Schools upload what they already post to Classroom/Blackboard (lecture videos, notes, assignments, rubrics).
- We **mine lectures** into a **teaching knowledge graph** that reflects how *their* instructors teach.
- Students do graded work (code first, then writing) inside **the Room**. A **Helper** removes mechanical friction and a **Coach** asks viva-style questions grounded in the course graph.
- Each finished piece of work earns a **Proof of Understanding**: portable, owned by the student, backed by evidence.

The full vision, market evidence, risks and roadmap are in **[ultimate-proposal.md](ultimate-proposal.md)**, the single source of truth for product intent. If this file or any doc disagrees with the proposal about *product intent*, the proposal wins unless a later entry in [docs/DECISIONS.md](docs/DECISIONS.md) overrides it.

## 2. Cold-start reading order

1. This file.
2. [docs/STATUS.md](docs/STATUS.md): where things stand right now and the next action.
3. [docs/OPEN_LOOPS.md](docs/OPEN_LOOPS.md): unresolved questions, blockers, TODOs.
4. [ultimate-proposal.md](ultimate-proposal.md): §1 vision, §3 philosophy, §9 module plan, §10 roadmap, §14 one-pager.
5. [design/README.md](design/README.md): technical designs (architecture, miner, data isolation, code-track MVP).
6. [docs/UPDATE_LOG.md](docs/UPDATE_LOG.md): what happened in each past session (newest first).
7. [docs/DECISIONS.md](docs/DECISIONS.md) and [docs/GLOSSARY.md](docs/GLOSSARY.md) when needed.

## 3. Repo layout

```
Acader/
├── CLAUDE.md               ← you are here (agent orientation + rules)
├── README.md               ← human-facing short intro
├── ultimate-proposal.md    ← product source of truth (vision → roadmap → sources)
├── CHANGELOG.md            ← user-visible / repo-level changes (Keep a Changelog style)
├── docs/
│   ├── STATUS.md           ← current state snapshot + next action (overwrite each session)
│   ├── UPDATE_LOG.md       ← append-only session journal (newest on top)
│   ├── OPEN_LOOPS.md       ← open questions, blockers, TODOs with IDs (OL-xxx)
│   ├── DECISIONS.md        ← locked decisions log (D-xxx), ADR-lite
│   └── GLOSSARY.md         ← project vocabulary (Room, Door, Proof, L1/L2/L3 …)
└── design/
    ├── README.md           ← design index + status of each design doc
    ├── architecture.md     ← system overview, modules M1–M11, data flow
    ├── lecture-miner.md    ← M2 visual miner algorithm + calibration lessons [VALIDATED]
    ├── data-isolation.md   ← 3-layer model (L1/L2/L3), ownership, cross-checks
    └── code-track-mvp.md   ← Phase 1 spec draft (variant engine + line-level viva)
```

There is **no application code yet**. The validated prototype (`lecture_miner.py` etc.) lived in an earlier session and **is not in this repo** (see OL-002).

## 4. Non-negotiable rules (product law; do not violate in code, copy, or design)

These come from proposal §3, §8 and §11. Breaking one means building a different product.

1. **Help students think; never think for them.** Never automate argument formation or write the student's content. AI may change *structure* (cluster, order, rename, find gaps) and must use *the student's own words*.
2. **Helper answers, Coach asks.** The Coach's questions must be grounded in the course graph, not in a generic system prompt.
3. **Make the right path the easiest one.** Remove mechanical cost (finding, citing, verifying sources). Keep the thinking cost (arguing, defending, explaining).
4. **Outside is free.** Never police or compete with research tools (Gemini Notebook, Elicit …). The Door imports anything and passes no judgment.
5. **Typing is not proof.** It is only the entry condition for process evidence. The viva/challenge is the real gate. Accessibility alternatives are mandatory.
6. **Never a cheat report.** Outputs are comprehension tiers: *Strong / Partial / Oral-verified*. Low confidence leads to a *recommended* oral check, and a human decides any consequence (EU AI Act posture).
7. **Students own their process data.** Schools see derived signals only. Tenant course materials **never** enter the global graph.
8. **Professors are heroes.** Explanations point first to how *their own* instructor taught the concept.
9. **Scope discipline.** The workspace exists for graded work only (code track and writing track). It is not a general notes app.
10. **Wording discipline.** Never use surveillance vocabulary ("detect", "catch", "cheater"). Never promise "no cheating". Promise *evidence on every submission* and *visibility into who is behind and where*. The selling point is thinking, never time saved.

## 5. Current focus

**Phase 1: CS viva-coach MVP (module M8, with M7 underneath it).** Acceptance criterion: *one real course assignment completed end-to-end by non-founders.* See [design/code-track-mvp.md](design/code-track-mvp.md) and [docs/STATUS.md](docs/STATUS.md) for the immediate next step.

## 6. Session protocol (how to leave the repo for the next agent)

At the **start** of a session:
- Read STATUS.md and OPEN_LOOPS.md. Do not redo work marked done or reopen items marked decided without a reason.

At the **end** of every session that changes anything:
1. **docs/STATUS.md**: overwrite the snapshot (phase, what works, what is in progress, the *single* next action, last-updated date).
2. **docs/UPDATE_LOG.md**: add a new entry **at the top** with the date, a summary, files touched, and loops opened or closed.
3. **CHANGELOG.md**: add lines under `[Unreleased]` for repo-level changes (new modules, docs, behavior).
4. **docs/OPEN_LOOPS.md**: add new loops with the next free `OL-xxx` ID, and move resolved ones to the *Closed* section with the resolution and date. Never reuse IDs.
5. **docs/DECISIONS.md**: record any decision the user locked in (`D-xxx`, with context and consequences).
6. If a design changed, update the doc in `design/` and its status row in [design/README.md](design/README.md).

Conventions:
- Dates are absolute ISO (`2026-10-11`), never "yesterday".
- Mark claims that were tested **[VALIDATED]**. Mark guesses **[ASSUMPTION]**.
- Keep the proposal unchanged except to fix factual errors. Record evolution in DECISIONS.md instead.

## 7. Tech notes (for when code starts)

- Prototype stack: Python 3, ffmpeg, OpenCV and numpy, with no ML in the visual miner. Command: `python3 lecture_miner.py VIDEO.mp4 --outdir out [--fps 1] [--max-seconds 600]`.
- Planned additions: Whisper (transcripts), a cheap LLM pass (topic structuring), a VLM (QA spot-checks), Crossref/DOI + Semantic Scholar or Scite (citation verification), and Canvas, Google Classroom and Blackboard (LMS).
- No language or framework is decided for the app (web Room, dashboard). See OL-008.
- Large media (videos, `*_out/` frame dumps) must not be committed. See `.gitignore`.

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
