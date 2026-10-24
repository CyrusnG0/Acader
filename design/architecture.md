# Architecture: The Writing Room v1

Status: **reviewed (CEO + eng) 2026-10-23** · Last updated: 2026-10-23
Implements: [PRODUCT.md](../PRODUCT.md) §5 and §7; D-024, D-029, D-032, D-033, D-034. Decisions are cited as CEO-x ([CEO record](../docs/designs/ceo-review-v1.md)) and Dx ([eng record](../docs/designs/eng-review-v1.md)). Replaces the original M1 to M11 architecture (now in [archive/design-v1/](../archive/design-v1/architecture.md)).
Loops: OL-008 (closed by this doc), OL-031, OL-035.

## 1. The system on one page

```
 Browser (student / teacher)
   editor (TipTap: origin marks + paragraph links, input plugin) · reader (PDF.js) · cards/claims (paste-tracked, D26)
   Coach/Helper panel · Door (text + files, never fetches URLs, CEO-9) · receipt (teacher view, student preview)
      │ steps + marks, batched; client queue in IndexedDB; edit lease (D10)          ▲ receipt JSON
      ▼                                                                              │
 server/app/   auth (roster + scanner-safe magic link, CEO-8, D11) · routes · repo layer (tenant, role, owner, D9)
               staging table → one chained editor.batch per 5 min (D30) · jobs loop (DB rows, D23) · email · operator page (D15)
      │ append: BEGIN IMMEDIATE + unique (log_id, seq)  (CEO-16)
      ▼
 server/engine/   events (hash chain, seal, verify) → replay (prosemirror-py, D6) → provenance (L1; L3b only if S3 passed)
                  → receipt (compile, wording filter, engine stamp D20, stored AI outputs D31)
      ▲                                     ▲
 server/sources/ (parse with caps, blocks)  server/coach/ (policies B, C; leak.py) ── llm complete() ── DeepSeek | backend 2 (OpenAI-compatible) | stub
 SQLite (WAL) on one machine · Litestream or nightly backup (D3)
```

**Main principle.** Provenance is *recorded at the moment it happens* by the UI channel that produced it, then *checked* at compile time: every non-typed mark must match its origin text (D5, D29). The LLM is asked only about specific flagged sentences. See [provenance.md](provenance.md).

## 2. Components

| Component | Responsibility | Spec |
|---|---|---|
| **Editor** | Rich-text writing; an origin mark on every character and links to claims on paragraphs (D-045); input plugin so typed text is always `typed`; emits steps | [event-log.md](event-log.md) §4 |
| **Reader** | PDFs and text sources with block highlights; pins by section kind; view and anchor events | [reading-aid.md](reading-aid.md) |
| **Cards and claim map** | Idea cards (paste-tracked) anchored to blocks; claim nodes; claim links as marks | [provenance.md](provenance.md) §3 |
| **Door** | Declared import of pasted text or files; URLs stored, never fetched | [coach-helper.md](coach-helper.md) §5 |
| **Coach / Helper** | Policy-governed assistant. Helper answers; Coach asks (cases B and C in v1) | [coach-helper.md](coach-helper.md) |
| **app/** | FastAPI routes, auth, repo layer, staging + append, jobs loop, email, operator page | §3, §7 |
| **engine/** | Pure library, no FastAPI import: events, replay, provenance, receipt. CLI: `python -m engine compile LOG` (D2) | [event-log.md](event-log.md), [provenance.md](provenance.md), [receipt.md](receipt.md) |
| **sources/** | Parse uploads into blocks in the jobs loop with caps and a teacher-visible status (D4) | [reading-aid.md](reading-aid.md) §3 |
| **coach/** | Policies, prompts ported from the kit, one leak-check module `leak.py` (D18) | [coach-helper.md](coach-helper.md) |
| **LLM boundary** | `complete(task, messages, schema)` in `server/app/llm.py`, wrapping `shared/llm.py` unchanged (D22) | §5 |

## 3. Data flow for one assignment

1. The teacher uploads the roster, creates an assignment, uploads readings. A job parses each reading into **blocks** (caps 50 MB / 300 pages / 300 s; status ok, scan, failed, processing). Readings become immutable once a student opens them; a re-upload is a new version (D4).
2. The student opens the invite link. The page's button signs them in (D11). They accept consent; `log.open` starts the chain.
3. Reading emits `source.open`, `source.view_span` (blocks opened, no dwell, D16), `aid.pin_opened`. Cards emit `card.create` + `card.anchor`, with pasted characters recorded (D26).
4. Writing: the editor sends batches every ~2 s to the **staging table** (acked, restart-safe). The server appends one merged `editor.batch` per 5-minute window, and at each checkpoint and submit (D30). Only the device holding the edit lease may send (D10).
5. Coach and Helper calls go through policy modules. Every serve is logged.
6. **Submit** (enabled only when the client queue is empty): staging is flushed, `doc.checkpoint` + `submit` are appended, and the hash of the `submit` event is the **seal** emailed to the student (D8). Submit never depends on the LLM (CEO-7).
7. **Compile** (async job): replay → mark check → L1 → receipt v1; L3 jobs → receipt v2 with questions. AI outputs are stored as compile artifacts (D31). A replay mismatch yields an L1 receipt from the client snapshot, labelled (D28).
8. **Release** to the teacher at the latest of the deadline, submit + 24 h, and questions compiled, but no later than the latest of (deadline, submit + 24 h) + 48 h. At that cap the L1 receipt is released as "questions pending" (CEO-21, D7).

## 4. Stack (locked by /plan-eng-review, OL-008 closed)

| Layer | Choice | Why |
|---|---|---|
| Server | **Python 3.12 + FastAPI** | One language; prompts and the DeepSeek client already in Python |
| Front end | **Vite + TypeScript + TipTap (ProseMirror) + PDF.js** | Marks and steps are first-class in ProseMirror |
| Schema | **One `web/schema.json`** loaded by the editor and by prosemirror-py (D6, D33) | Parity between browser and server replay |
| Database | **SQLite (WAL) everywhere** (dev, CI, pilot), one machine; Litestream or nightly backup + restore test. Move to Postgres when >1 class or >1 app machine (TODOS, D3, D35) | Same engine in tests and pilot; writers serialised |
| Jobs | DB job rows (idempotency key, lease), one in-process loop, 4 concurrent LLM calls per backend, round-robin by submission, backoff 1/4/16 min, leases resumed at boot (D23). **Mapper jobs** (D-035) run at the lowest priority, skip batches with < 30 changed words, keep at most one queued job per log (the newest replaces it) and are cancelled at submit (eng v2 D4, D6) | No Redis; restart-safe; receipts never wait behind the mapper |
| PDF parsing | Hosted, in the jobs loop; parser chosen by spike S2 (Docling, GROBID or PyMuPDF) (D4) | Teacher self-serve |
| Embeddings | **None in v1** (D1). L3b gets the student's claim nodes, or the top 5 by BM25 | No extra processor, no pgvector |
| LLM | DeepSeek + one generic OpenAI-compatible backend (base URL, model, key, auth header from config) behind `complete()`; `ROOM_LLM=stub` in tests (CEO-6, D14) | The school picks; consent names it |
| Hosting | One machine in the consented region; no deploys during an assignment window except announced fixes (D34) | Region matters for consent (OL-037) |
| Auth | Teacher-uploaded roster + invite magic link (page + button POST; single use; 30 min; hashed) (CEO-8, D11). Blackboard LTI after the pilot | Roster-only access |

## 5. Interfaces that must not drift

- **Event schema**: versioned (`schema: 1`), defined in [event-log.md](event-log.md) §3. One parser for every consumer.
- **Editor schema**: `web/schema.json`, shared by the editor and the Python replay. Changing it regenerates golden logs in CI (D33).
- **Mark kinds**: origin kinds, the node set and the paragraph `links` attribute are a closed list in [event-log.md](event-log.md) §4. Adding a kind is a schema bump.
- **LLM boundary**: `complete(task, messages, schema) -> dict`. Tasks: `claim_extract`, `claim_compare`, `contradiction`, `coach_question`, `receipt_question`, `limitation_tag`, `leak_check`, `map_suggest` (D-035; output = links only, never prose; each link must name an existing claim_id and one of the changed paragraphs, else it is dropped, like Coach grounding; uses the configured backend, model choice settled by the D7 eval). Each has a pydantic output schema and a stub fixture. Errors: `LLMTimeout`, `LLMRateLimited`, `LLMAuth`, `LLMRefusal`, `LLMSchema` (D13). A startup ping checks each configured backend.
- **`shared/llm.py`**: behaviour unchanged (`chat`, `parse_json`, `NoKey/Upstream/BadOutput`, env vars); only optional keyword params may be added. The kit + web tests (29) run in CI (D22).
- **Receipt JSON**: data first, then rendered; every line cites `event_ids` (and `artifact_ids` for AI-derived lines); carries the `engine` stamp. See [receipt.md](receipt.md) §6.

## 6. Prototype repository layout (D2)

```
prototype/
├── server/
│   ├── app/       FastAPI routes, auth, repo layer, staging + append, jobs loop, llm.py, email, operator page
│   ├── engine/    events/ (chain, seal, verify) · replay/ · provenance/ · receipt/   (no FastAPI import; CLI)
│   ├── sources/   parse, blocks, pins, citation
│   ├── coach/     policies, prompts/ (ported from the kit), leak.py
│   ├── mapper/    map_suggest job, prompts, suggestion store (D-035; own package, eng v2 D2)
│   ├── trail/     provisional bands for "Show my trail": calls engine.provenance (replay + mark check + L1, no L3/AI), no band logic of its own (D-036 7A; eng v2 D2, D8)
│   └── tests/     unit, golden receipts, route enumeration, load (ROOM_LLM=stub)
├── web/           Vite + TS: schema.json, editor/, reader/, map/, coach/, receipt/
├── fixtures/      golden session scripts (YAML), regenerated logs, expected receipts, openly licensed readings
└── spikes/        S1–S5 code and result notes
```

## 7. Non-functional targets (v1, one class)

| Target | Value |
|---|---|
| Editor edit loss | 0 under normal use: client queue + ack; stale queue after a lost lease is never applied, offered as a file or a Door import (D32) |
| Ingest latency | < 300 ms p95 per batch **[ASSUMPTION]** |
| Receipt compile | L1 receipt < 60 s; questions < 15 min under 30 submits in 5 minutes (load test with a 3 s stub, D23) |
| LLM calls per submission | Compile + Coach < 30 **[ASSUMPTION]**; mapper capped at 40, after which suggestions stop (eng v2 D6). Both counted per submission on the operator page |
| Availability | Best effort; submit retries with the same idempotency key until acked (D34) |
| Observability | Structured logs (request_id, log_id; never student text or keys); counters; email alerts on compile failure, LLM auth failure, any leak fail, release cap reached; 3 runbooks (D15) |
| Security | Repo layer on every query; route-enumeration test; text-only rendering + strict CSP; teacher audit rows (D9) |
| Accessibility | WCAG 2.2 AA by design: no drag-only actions, targets ≥ 24 px, no timers, typed alternative to any spoken step |
