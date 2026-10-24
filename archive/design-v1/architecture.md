# Architecture

**Status:** designed (module level) · **Implements:** proposal §2, §4, §4.7, §9, §10 · **Open loops:** OL-008 (stack)

## 1. System overview

```
           SCHOOL (tenant)                                   STUDENT
  lectures · notes · assignments · rubrics            work in the Room (code / writing)
                │                                                 │
        ┌───────▼────────┐                                ┌───────▼────────┐
        │ M1 Ingest      │                                │ Room           │
        └───────┬────────┘                                │  Helper ⇄ Coach│
   ┌────────────┼──────────────┐                          │  no-paste editor│
   ▼            ▼              ▼                          └──┬──────────┬──┘
 M2 Visual   M3 Transcript   (docs/rubrics parse)            │ process  │ challenges
 miner       (Whisper)                                       │ events   │ (grounded)
   └────┬───────┘                                            ▼          │
        ▼                                              L3 Mastery model │
   M4 Alignment (state ↔ speech)                       (student-owned)  │
        ▼                                                    │          │
   M5 Topic structuring (LLM) ──► M6 QA watcher (VLM)        │          │
        ▼                                                    │          │
   M7 L1 Course KG (tenant) ◄───── L2 Global concept graph ──┼──────────┘
        │                                                    │
        ▼                                                    ▼
   M8 Code track · M9 Writing track ──────────────► M10 Proof of Understanding
                                                     + School dashboard + parent layer
                                   M11 LMS integrations (Canvas / Classroom / Blackboard)
```

## 2. Modules

| # | Module | Input → Output | Notes |
|---|---|---|---|
| M1 | Ingest | uploads and video URLs → stored media and docs | Server-side downloader. Zero behavior change for schools. |
| M2 | Visual miner | video → timestamped board/slide states (`states.csv` + frames) | **Validated.** See [lecture-miner.md](lecture-miner.md). |
| M3 | Transcript | audio → sentence-timestamped transcript | Whisper. |
| M4 | Alignment | states + transcript → state ↔ speech spans (time overlap) | Standard. |
| M5 | Topic structuring | aligned states and speech → teaching units (concept, explanation, board, time range) | One cheap LLM pass per lecture. |
| M6 | QA watcher | candidate states → accept/reject, title-card flags | VLM spot-checks on candidates only, which keeps cost about zero. |
| M7 | Course KG + isolation + mastery | teaching units → L1 graph, linked to L2 concepts; L3 per student | See [data-isolation.md](data-isolation.md). |
| M8 | Code track | reference solution → reviewed variants; student coding → defense record | **Phase 1.** See [code-track-mvp.md](code-track-mvp.md). |
| M9 | Writing track | sources + drafting → claim cards, verified citations, coverage map | Phase 2. Proposal §4.4. |
| M10 | Proof + dashboard + parent layer | process signals + challenge records → Proof; aggregated L3 → heatmaps | Phase 3. Proposal §4.5–4.6. |
| M11 | LMS integrations | assignments in, submissions and grades out | Comes with the first pilots. |

## 3. Key flows

**Lecture → graph (zero-touch):** M1 → M2 + M3 → M4 → M5 → M6 → M7. Output: teaching units such as "eigenvectors, Lecture 7, 12:40–18:05, board #43", which the Coach cites.

**Code assignment (Phase 1):** the teacher uploads a reference solution. The variant engine generates N variants and the teacher reviews each one. Students receive different variants and work in the no-paste editor. At key lines the Coach asks grounded questions. The answers form the defense record, which produces a comprehension summary, which feeds a Proof (M10, minimal in Phase 1).

**Writing assignment (Phase 2):** sources come in through the Door and become claim cards. The coverage map and conflict prompts follow, then an outline built together with the Coach. Drafting uses in-place citation verification (DOI/Crossref → full text → support judgment), with burst escalation when needed. The End is the manuscript plus the citation report plus the Proof.

## 4. Phases → modules
- **Phase 0 (done):** M2.
- **Phase 1:** M1 (minimal), M3–M5 (enough to ground questions), M7 (minimal L1 and L3), **M8**, minimal Proof/summary.
- **Phase 2:** M9 and the full Proof tiers.
- **Phase 3:** M10 dashboard and parent layer, M11.
- **Phase 4:** School Teaching Brain, cross-school L2 enrichment, accreditation reports.

## 5. Cross-cutting requirements
- **Tenant isolation is auditable.** Encrypt per school. No training on tenant data. Logs prove it.
- **Student data portability.** The L3 and Proof vault can be exported by the student.
- **Human in the loop.** Variants are never released without teacher review. No automated consequences.
- **Cost discipline.** Pixels do the scanning, models do the judging. Use LLM/VLM only where heuristics cannot.
