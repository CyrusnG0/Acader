# Data Isolation & Ownership (M7)

**Status:** designed, not built · **Implements:** proposal §3.7, §4.7, §8.4 · **Decision:** D-007

## 1. Ownership table (this is the sales-meeting table)
| Data | Owner | School sees | Enters global graph |
|---|---|---|---|
| Course materials (recordings, assignments, rubrics) | School | own school only | **never** |
| Student process data (keystrokes, coach dialogues) | **Student** | derived signals only | anonymized stats, opt-out available |
| Proof of Understanding | both | yes | no |
| Concept graph + openly licensed content | Platform | all | yes |

## 2. Three layers
- **L1: Tenant course graph.** One per school, encrypted per tenant. Built from mined materials (M2–M5). Holds teaching units and links to L2 concepts.
- **L2: Global concept graph.** Concepts, prerequisite edges, and openly licensed canonical explanations (seed corpus: MIT OCW, CC BY-NC-SA). It never contains tenant content.
- **L3: Student mastery model.** Owned by the student and portable. Contains the raw process data. Schools receive derived signals only.

## 3. Five cross-checks
| Check | Layers | What it does |
|---|---|---|
| Course alignment | L1 | Does the work or question match what this course taught? |
| Citation authenticity | L2 | Does the source exist, and does it support the claim? |
| Concept consistency | L2×L3 | A claim that relies on an unmastered prerequisite triggers the Coach *before* the teacher sees a problem. |
| Code-challenge grounding | L1×L2 | Viva questions are anchored to taught concepts. |
| Process consistency | L3 | A process-evidence mismatch produces a *recommended* oral check. |

## 4. Engineering requirements
- Isolation and no-training promises must be **auditable** (procurement question #1): per-tenant keys, access logs, and a documented data path.
- The student vault can be exported (Proof and process data).
- Guardian-visible layer for secondary schools, explicitly marked. Adult autonomy at university level.
- **[ASSUMPTION]** Storage tech is undecided (OL-008).
