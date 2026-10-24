# Eng review: The Writing Room prototype v1

**Skill:** /plan-eng-review (gstack 1.91.181.0) · **Date:** 2026-10-23 · **Branch:** main (uncommitted; no branch diff)
**Target (fixed):** the whole v1 plan set, as the founder asked at the scope gate ("review the whole repo … all the plan and our vision"):
PRODUCT.md, design/ (README, architecture, event-log, provenance, receipt, reading-aid, coach-helper, privacy, evaluation, build-plan), and the CEO review record docs/designs/ceo-review-v1.md (decisions CEO-1 to CEO-24, pending P-6 to P-17).
**Report file:** this file. It sits next to ceo-review-v1.md, per the repo's session protocol (CLAUDE.md §6), instead of gstack's state folder.

## Original plan snapshot

The plan is about 86 KB across 12 files, so instead of copying it here, this table records the sha256 prefix of each file at the start of the review. Any later edit by this review is listed under "Accepted changes" below.

| File | sha256 (first 16) |
|---|---|
| PRODUCT.md | 5d603813632b36c8 |
| design/README.md | 61c23bdd06327fcf |
| design/architecture.md | 5ca785bc985289ba |
| design/build-plan.md | fe070d21ec267243 |
| design/coach-helper.md | b379d47302f126ce |
| design/evaluation.md | 6c3da1a1d82258af |
| design/event-log.md | 7f4b5e20794cbee0 |
| design/privacy.md | ff03237ecff8df38 |
| design/provenance.md | 657eaa0aed48a62b |
| design/reading-aid.md | eb409569fc8c2d61 |
| design/receipt.md | ceff71ae2312a7d0 |
| docs/designs/ceo-review-v1.md | 8cfc3f8758864c60 |

## Binding decisions carried in (not re-argued)

CEO-1 to CEO-24 (D-032, D-033) are binding: receipt-first thin slice for one class; seal on submit; roster + magic link; the Door doesn't fetch; S3 gates L3b; reworded = untraced; student links labelled; human sessions; blind test; preview without question text; release = later of three; processor approval; bottom-up schedule; rigour upgrades. This review reopens an approved choice only for a concrete new risk, and says so.

## Step 0: Scope Challenge

### A. Assessment
- **What already exists:** `shared/llm.py` (DeepSeek `chat()`, error classes `NoKey/Upstream/BadOutput`, `parse_json`); kit `v04/llmx.py` (stub mode `ROOM_LLM=stub`, call-metadata log), `v04/audit.py` (law-1 judge prompt), `v04/policies/*.md` (policy prompts), `v04/room.py` (governed assistant). **Correction to P-13:** `room.py:20-22` and `audit.py:13-16` load the fictional `data/corpus.json` at import, so they can't be ported as code. What ports is the prompts (`policies/*.md`, the law-1 judge text) and the test ideas.
- **Complexity:** the plan proposes 6 server packages, a web app with 5 areas, a worker, an LLM boundary with 2 backends, an email sender, and auth. That's well over 8 files and more than 2 new services, so the gate tripped.
- **Search check** (WebSearch; Aside not installed):
  - A Python port of prosemirror-model/transform exists ([PyPI `prosemirror`](https://pypi.org/project/prosemirror)).
  - DeepSeek's public API appears to have no embeddings endpoint ([Tabby docs](https://tabby.tabbyml.com/docs/references/models-http-api/deepseek/); [unverified], the official docs weren't in the results).
  - ProseMirror marks are inclusive by default, and typed text takes the marks at the cursor ([forum](https://discuss.prosemirror.net/t/rationale-for-inclusiveright-inclusive-change/701)).
- **TODOS cross-reference:** TODOS.md "Writing Room v1: deferred" holds the CEO deferrals. Nothing there blocks this plan. L2 joins it (D1).
- **Distribution:** hosted web app only (Fly.io or a host in the consented region). The Docker image builds from the repo root, like the kit's web app. No packages to publish.

### B. Scope record (post-answer)
feature answers: D1 "Defer L2 (recommended)", 2026-10-23; structure: B "Smaller arrangement (recommended)", D2 answer 2026-10-23; accepted scope:
- L2 embeddings deferred to TODOS (trigger: more than 30 claim nodes per essay). L3b gets all of the student's claim nodes, or the top 5 by BM25 word overlap.
- Server = `app/` (routes, auth, jobs loop), `engine/` (events + provenance + receipt; no FastAPI import; CLI `python -m engine compile LOG`), `sources/`, `coach/`.
- Jobs are DB rows worked by one in-process loop. There is no separate worker service.
- Every other CEO-approved feature is unchanged.

pending remedies: SC2, P-7, A1, A2, A3, A4, A5, A6, P-6, P-8, P-9, P-10, P-11, P-12, P-13, P-14, P-16, P-17, Q1, Q2, T1

### C. Findings
1. [P2] (confidence: 8/10) provenance.md:53, architecture.md:75. L2 needs an embedding provider not in consent, plus pgvector or a model, for a step that only feeds L3b. Reviewer: Claude (main). → D1, deferred.
2. [P2] (confidence: 7/10) architecture.md:72 "SQLite in development, Postgres in the pilot". Two engines mean the CEO-16 append transaction, job locking and tests behave differently in dev and in the pilot. Reviewer: Claude (main). → SC2.
3. [P2] (confidence: 7/10) reading-aid.md:47 "Docling → GROBID → PyMuPDF" plus P-7. Docling pulls in torch and models (GBs) and can take minutes per paper. That's heavy for a hosted image serving one class with 3–6 readings. Reviewer: Claude (main). → P-7.
4. [P2] (confidence: 9/10) coach-helper.md:92 "ports them into prototype/server/coach/". The kit code is tied to the fictional corpus (room.py:20-22), so a port means rewriting, not copying. Reviewer: Claude (main). → P-13 (Section 2).

## Decision ledger

### SC2: one database engine
Finding: C.2, P2, 7/10, architecture.md:72, Claude (main)
Plan baseline: SQLite in development, Postgres + pgvector in the pilot (architecture.md:72; OL-008 open). pgvector is no longer needed (D1).
Runtime evidence: no server code exists. CEO-16 requires "head read + insert in one transaction, retry on conflict" (architecture.md:10). SQLite serialises writers (BEGIN IMMEDIATE). Postgres needs row locks or a unique-constraint retry. Unverified until built.
Comparison grid:
| Choice | Current | A | B | C |
|---|---|---|---|---|
| SC2 engine (dev / pilot) | SQLite / Postgres | SQLite / SQLite (WAL, one machine, Litestream or nightly backup; upgrade when >1 class or >1 machine) | Postgres / Postgres (local Docker) | SQLite / Postgres (as is) |
| CEO-16 append rule | approved | kept (BEGIN IMMEDIATE + unique (log_id, seq)) | kept (unique + retry) | kept, two implementations |
| Backups + restore test (pilot gate) | approved | kept (file-level) | kept (pg_dump) | kept |
| L2 / pgvector | deferred (D1) | unchanged | unchanged | unchanged |
Question D3:
D3 — One database engine for dev and pilot?
Project/branch/task: main, eng review of the v1 plan set.
ELI10: The plan uses SQLite on your laptop and Postgres when hosted. That means the code that keeps the event log in order (one write at a time, CEO-16) and the job queue would behave differently in the two places, and tests on the laptop wouldn't prove the pilot works. One class of ~30 students is tiny: SQLite in WAL mode on one machine handles it easily and makes backups a file copy. Postgres everywhere is the other clean option, at the cost of running it locally and paying for a managed instance.
Stakes if we pick wrong: Two engines let a concurrency or locking bug pass tests and show up only with real students.
Recommendation: A because one class on one machine is well inside SQLite's range and it's the fewest moving parts for a solo build.
Completeness: A=9/10, B=9/10, C=6/10
Pros / cons:
A) SQLite everywhere (recommended)
  ✅ Same engine in tests and pilot; writers are serialised by design
  ✅ Backup is a file copy (Litestream or nightly), restore test is trivial
  ❌ One machine only; upgrade to Postgres for more classes or a second machine
B) Postgres everywhere
  ✅ Ready for several classes and several app machines
  ✅ Managed backups and point-in-time restore from the host
  ❌ Local Docker for dev; a managed DB is another processor to name
C) Keep SQLite dev / Postgres pilot
  ✅ Matches the current architecture.md text
  ✅ Fast local setup with Postgres features in the pilot
  ❌ Two code paths for locking; tests don't prove pilot behaviour
Net: simplest single engine now versus scale headroom you don't need for one class.
Header: DB engine
Options:
A) SQLite everywhere (recommended)
SQLite (WAL) in dev, CI and the pilot, on one machine. Append = BEGIN IMMEDIATE + unique (log_id, seq). Backups by Litestream or a nightly copy plus a restore test. Upgrade trigger: more than one class or more than one app machine. human: ~0.5 day saved / CC: ~20 min saved.
B) Postgres everywhere
Postgres in dev (Docker), CI and the pilot. Append = unique (log_id, seq) + retry on conflict. Managed backups. Name the DB host in consent.
C) Keep SQLite dev / Postgres pilot
As architecture.md says now: two engines, with CEO-16 tested on both.

State: approved
Actual answer: A) "SQLite everywhere (recommended)", D3 answer 2026-10-23
Accepted scope: SQLite (WAL) in dev, CI and pilot on one machine; append = BEGIN IMMEDIATE + unique (log_id, seq); Litestream or nightly backup + restore test; upgrade to Postgres when >1 class or >1 app machine. architecture.md §4 updated.
History: none

### P-7: readings: limits, status and where parsing runs
Finding: C.3, P2, 7/10, reading-aid.md:47; P-7 from ceo-review-v1.md:697, Claude (main)
Plan baseline: P-7 pending: upload limits + parse status (scan / failed / ok) shown to the teacher; parser in a worker with size/page/time caps; readings immutable after first open. Parser chosen by S2.
Runtime evidence: no parser code. Docling depends on torch and model downloads [unverified size; GBs is typical]. S2 has not run.
Comparison grid:
| Choice | Current | A | B |
|---|---|---|---|
| Caps (size, pages, time) | pending | 50 MB, 300 pages, 300 s per parse | same |
| Status shown to the teacher | pending | ok / scan (no text layer) / failed / processing | same |
| Readings immutable after first student open; re-upload = new version | pending | yes | yes |
| Where parsing runs | hosted worker (any parser) | hosted jobs loop; parser chosen by S2, installed in the image | operator CLI on the founder's machine (`python -m sources parse`), uploads blocks; hosted image has no parser |
| Teacher sees blocks | immediately after parse | minutes | within the working day ("being prepared") |
Question D4:
D4 — Readings: limits, status, and where the PDF parser runs?
Project/branch/task: main, eng review of the v1 plan set.
ELI10: Teachers upload readings. Some are scans with no text, some are huge, and the best parser (Docling) is a heavy AI library that can take minutes per paper. Both options add the same safety rules: size and page limits, a status the teacher can see ('this PDF is a scan'), and readings that can't change under students once they're opened. The question is where parsing runs. Either the hosted server does it (teacher self-serve, but the heavy parser goes into the hosted image), or for the one pilot class you run it on your own machine and upload the blocks (hosted app stays small, teacher waits a few hours).
Stakes if we pick wrong: A heavy parser in the hosted image means slow deploys and a bigger server bill. An operator step means the teacher waits for you.
Recommendation: B because one class has 3–6 readings, S2 can pick the best parser without image cost, and the teacher sets readings days before students start.
Note: options differ in kind, not coverage — no completeness score.
Pros / cons:
A) Hosted parse with caps
  ✅ Teacher self-serve: upload and see blocks within minutes
  ✅ No founder step per reading; scales to more classes
  ❌ Heavy parser in the hosted image if S2 picks Docling (slow deploys)
B) Operator-run parse for the pilot (recommended)
  ✅ Hosted image stays small; S2 can choose any parser freely
  ✅ Founder sees every reading's blocks before students do
  ❌ Teacher waits hours; move to hosted parse before more classes
Net: teacher self-serve now versus a lighter server and hand-checked blocks for one class.
Header: Parsing
Options:
A) Hosted parse with caps
Caps 50 MB / 300 pages / 300 s; status ok, scan, failed, processing; readings immutable after first open (re-upload = new version). The parser chosen by S2 runs in the hosted jobs loop. human: ~1 day / CC: ~40 min.
B) Operator-run parse (recommended)
Same caps, status and immutability. Teacher uploads; status shows "being prepared". Founder runs `python -m sources parse` locally with the S2 parser and uploads blocks. Hosted image has no parser. Move to hosted before a second class. human: ~0.5 day / CC: ~25 min.

State: approved
Actual answer: A) "Hosted parse with caps" (not the recommendation), D4 answer 2026-10-23
Accepted scope: caps 50 MB / 300 pages / 300 s; teacher-visible status ok / scan / failed / processing; readings immutable after first student open (re-upload = new version); parser chosen by S2 runs in the hosted jobs loop (image size accepted). Tests: scanned PDF → scan status; oversized file → rejected with limit; re-upload after open → new version, old anchors intact.
History: none

### Scope Challenge result
Scope reduced per recommendation (D1: L2 deferred). Structure: smaller arrangement (D2). Stack items settled: SQLite everywhere (D3), hosted parse with caps (D4).

## Section 1: Architecture review

```
 Browser ── editor (TipTap, origin marks, claim-link marks) ── reader (PDF.js) ── cards/claims ── Coach ── Door
    │ steps + marks (batched, client queue)                      ▲ receipt JSON
    ▼                                                            │
 app/  auth (roster + magic link) · routes · tenancy · jobs loop (DB rows) · email
    │ append (BEGIN IMMEDIATE, unique log_id+seq)                │
    ▼                                                            │
 engine/  events (hash chain, verify) → replay steps → provenance (L1, L3b if S3) → receipt (compile, wording filter)
    │                                     ▲
 sources/ (parse with caps, blocks) ──────┘        coach/ (policies, leak check) ── llm complete() ── DeepSeek | 2nd backend | stub
 SQLite (WAL) on one machine, backups
```

Findings (most severe first):
- **A1** [P1] (confidence: 8/10) event-log.md:83 "`quote` | block_id | Text inserted by 'quote this passage'", together with provenance.md:96 "`quote` text counts as traced to its block". **Origin marks are claimed by the browser.** A student with devtools can put a `quote` or `coach` mark on any text and get "traced" with no check. CEO-17 covers links, not marks.
- **A2** [P1] (confidence: 8/10) provenance.md:52 "Rebuild final doc" and event-log.md:99 "rebuilt by replaying steps". **The server is Python and the steps are ProseMirror (JavaScript).** Nothing says how the server replays them. Without replay, the final document isn't proven to come from the logged steps.
- **A3** [P1] (confidence: 9/10) receipt.md:11 "Release = the latest of the deadline, submit + 24 h, and questions compiled" contradicts receipt.md:9 "Receipts can show 'questions pending' during an LLM outage". **With no cap, a long LLM outage means the teacher never gets the receipt.** This reopens CEO-21 for a concrete risk.
- **A4** [P2] (confidence: 8/10) event-log.md:23 "A resubmission continues the same chain and seals again" and :105 "returns the head hash". **"Sealed" isn't defined.** Notes, links, receipt.issued and withdrawal all append after submit, so it's unclear which hash the student holds and what it proves.
- **P-9** [P1] (confidence: 7/10) ceo-review-v1.md:699: authorization per route (IDOR), text-only rendering + CSP, teacher audit events.
- **P-10** [P1] (confidence: 8/10) ceo-review-v1.md:700: submit guards and the two-tab lease.
- **P-11** [P1] (confidence: 8/10) ceo-review-v1.md:701: email scanners consume one-time links on GET.
- **A5** [P2] (confidence: 6/10) event-log.md:44 "`ts` is server receive time, rounded to the second" plus :98 "one `editor.batch` per ~2 s of activity". Together these make a per-2-second activity timeline, close to the "how you typed" that law 7 rules out.
- **P-6** [P2] (confidence: 8/10) shared/llm.py:62 `raise BadOutput("empty model output")`: empty, refusal and schema errors share one class, and NoKey is found only at call time.
- **P-17** [P2] (confidence: 6/10) ceo-review-v1.md:898: the second backend may not be offered in HK; an OpenAI-compatible base URL covers Azure and others.
- **P-8** [P2] (confidence: 7/10) ceo-review-v1.md:698: no logs, counters or runbooks beyond the CEO-7 alert.
- **A6** [P3] (confidence: 8/10) event-log.md:54 `dwell_bucket` is collected, but no receipt fact uses it (provenance.md:104 uses "opened and anchored" only).

### A1: validate non-typed origin marks
Finding: A1, P1, 8/10, event-log.md:83 + provenance.md:96, Claude (main)
Plan baseline: marks are recorded as sent by the editor; no server check (event-log.md §4).
Runtime evidence: no code. The browser is untrusted by construction.
Comparison grid:
| Choice | Current | A | B | C |
|---|---|---|---|---|
| Where marks are checked | nowhere | engine at compile: marked text (whitespace-normalised) must be inside its origin text (block for quote, coach answer for coach, import raw for import, helper output for helper) | app at ingest, per batch (needs live replay) | nowhere (as is) |
| Mark that fails | counts as claimed | counted untraced, chain view says "origin mark didn't match its source"; claimed mark kept in the log | batch rejected 400 | counts as claimed |
| Test | none | golden session with a forged quote mark and a forged coach mark | same | none |
Question D5:
D5 — Check origin marks against their source before they count as traced?
Project/branch/task: main, eng review of the v1 plan set.
ELI10: Every character carries a label saying where it came from: typed, quoted from a reading, from a Coach answer, and so on. The browser applies those labels, and a student who knows devtools can relabel pasted AI text as "quoted from reading 2", which the receipt then shows as traced. The fix: when the receipt is built, check that each "quote" really matches the reading's text, each "coach" really matches the student's recorded answer, and so on. If a label doesn't match, the text counts as untraced and the chain view says so.
Stakes if we pick wrong: Without the check, the strongest band on the receipt ("traced to a source") can be forged with two minutes of devtools.
Recommendation: A because a check when the receipt is built is pure code in engine/, needs no live replay, and closes the forgery.
Completeness: A=9/10, B=9/10, C=3/10
Pros / cons:
A) Check at compile in engine/ (recommended)
  ✅ Forged quote/coach/import/helper marks count as untraced, never traced
  ✅ Pure function over final doc + origin texts; easy table tests
  ❌ The forged mark stays in the log; only the receipt ignores it
B) Check at ingest per batch
  ✅ Rejects forged marks the moment they arrive
  ✅ The log itself never holds an unchecked mark
  ❌ Needs live step replay on every batch; more code on the hot path
C) Trust the browser (as is)
  ✅ No work now
  ✅ Honest students see no difference
  ❌ "Traced to source" can be forged; breaks the receipt's core claim
Net: a cheap check at receipt time closes the forgery path without slowing writing.
Header: Mark check
Options:
A) Check at compile (recommended)
engine/ checks each quote/coach/import/helper mark's text against its origin text (whitespace-normalised). Mismatch → untraced, with chain note "origin mark didn't match its source"; the log keeps the claimed mark. Golden session with forged quote + coach marks. human: ~4h / CC: ~15 min.
B) Check at ingest
app/ replays each batch and rejects (400) any batch whose marks don't match their origin. Needs live replay on the hot path. human: ~1 day / CC: ~40 min.
C) Trust the browser
No check (as is).

State: approved
Actual answer: A) "Check at compile (recommended)", D5 answer 2026-10-23
Accepted scope: engine/ checks quote/coach/import/helper marks against origin text (whitespace-normalised); mismatch → untraced + chain note "origin mark didn't match its source"; claimed mark kept in log; golden session with forged quote + coach marks.
History: none

### A2: how the server replays editor steps
Finding: A2, P1, 8/10, provenance.md:52 + event-log.md:99, Claude (main)
Plan baseline: "Rebuild final doc" on the server (Python); no mechanism named.
Runtime evidence: PyPI `prosemirror` (prosemirror-py) ports prosemirror-model and prosemirror-transform; its exact `Step.apply` API isn't verified. Node v25.9.0 is installed locally.
Comparison grid:
| Choice | Current | A | B | C |
|---|---|---|---|---|
| Replay engine | unnamed | prosemirror-py in engine/; schema mirrored in Python | Node script (prosemirror-transform + the web app's schema file) called by engine/ | none: client sends the full doc with marks at checkpoint/submit |
| Proof that final doc = logged steps | none | replay result must equal the client's doc_hash at each checkpoint; mismatch → compile error + alert | same | none (tests only) |
| S1 adds | — | JS-vs-Python replay parity on the S1 cases | replay in Node on the S1 cases | — |
| Runtime deps | — | Python only | Node in the server image | none |
Question D6:
D6 — How does the Python server rebuild the document from editor steps?
Project/branch/task: main, eng review of the v1 plan set.
ELI10: The editor sends small edit steps, not the whole document. To build the receipt, the server has to replay those steps to get the final text and its labels. The steps are in ProseMirror's format, which is JavaScript, and our server is Python. Options: use the Python port of ProseMirror (stays all-Python, but the editor's schema has to be copied into Python and the two checked to agree), run a tiny Node script that uses the real ProseMirror code, or skip replay and trust the document the browser sends.
Stakes if we pick wrong: Skip replay and the final document isn't tied to the logged steps, so "every receipt line traces to the log" stops being true.
Recommendation: A because it keeps engine/ pure Python (D2) and the CLI simple, and S1 can prove parity before anything depends on it.
Completeness: A=9/10, B=9/10, C=4/10
Pros / cons:
A) Python port (prosemirror-py) (recommended)
  ✅ engine/ stays pure Python; CLI runs on golden logs with no Node
  ✅ The checkpoint doc_hash check ties the final doc to the steps
  ❌ Schema kept in two languages; S1 parity test must guard drift
B) Node replayer script
  ✅ Uses the exact ProseMirror code the editor uses; no parity risk
  ✅ The checkpoint doc_hash check ties the final doc to the steps
  ❌ Node in the server image; subprocess per compile; two runtimes
C) Trust the browser's document
  ✅ No replay code at all
  ✅ Fastest to build
  ❌ The final doc isn't proven to come from the logged steps
Net: one language with a parity test versus the canonical code with a second runtime.
Header: Replay
Options:
A) Python port (recommended)
engine/ uses prosemirror-py with a minimal schema mirrored from web/ (one schema JSON both sides load where possible). Replay must equal the client's doc_hash at each checkpoint, else compile error + alert. S1 adds a JS-vs-Python parity check. human: ~1 day / CC: ~45 min.
B) Node replayer
engine/ calls `node replay.mjs` (prosemirror-transform + the web app's schema module). Same doc_hash check. Node goes into the server image. human: ~0.5 day / CC: ~30 min.
C) Trust the browser's document
Client sends the full doc with marks at checkpoint and submit; steps are stored but not replayed.

State: approved
Actual answer: A) "Python port (recommended)", D6 answer 2026-10-23
Accepted scope: engine/ replays steps with prosemirror-py and a minimal schema mirrored from web/; replay must equal client doc_hash at each checkpoint, else compile error + alert; S1 adds JS-vs-Python parity check (failure reopens this choice).
History: none

### A3: cap on the release wait (reopens CEO-21)
Finding: A3, P1, 9/10, receipt.md:11 vs receipt.md:9, Claude (main)
Plan baseline: CEO-21 (O5 answer "Later of three"): release = latest of deadline, submit + 24 h, questions compiled; teacher sees "still compiling" until then.
Runtime evidence: none. Reason for reopening: concrete new risk. CEO-7 lets questions stay pending through an outage, so under CEO-21 the teacher waits with no bound.
Comparison grid:
| Choice | Current | A | B |
|---|---|---|---|
| Release time | latest of (deadline, submit+24h, questions compiled) | same, but no later than latest of (deadline, submit+24h) + 48 h | as is (no cap) |
| At the cap with questions pending | n/a (waits) | L1 receipt released, labelled "questions pending"; questions appear later marked "added after release"; operator alert | n/a |
| Student preview rule (CEO-20) | approved | unchanged | unchanged |
| Test | 30 submits in 5 min (CEO-21) | + frozen-clock test: LLM down past the cap → L1 released | unchanged |
Question D7:
D7 — Cap how long the teacher waits for a receipt when the AI is down?
Project/branch/task: main, eng review of the v1 plan set.
ELI10: You chose: the teacher sees the receipt at the latest of the deadline, 24 hours after submitting, and when the questions are ready. But if the AI provider is down for days, the questions are never ready, so the teacher never sees anything, even though the sealed record and the facts are fine. A cap fixes that: after 48 more hours, release the receipt without questions, labelled 'questions pending', and add them later marked 'added after release'.
Stakes if we pick wrong: An outage during grading week leaves a whole class of receipts invisible to the teacher.
Recommendation: A because it keeps CEO-21 in normal cases and matches CEO-7's 'questions pending' promise.
Completeness: A=9/10, B=6/10
Pros / cons:
A) Add a 48 h cap (recommended)
  ✅ Teacher always gets the record within 48 h of the normal release
  ✅ Matches CEO-7: L1 receipt with 'questions pending' actually reaches the teacher
  ❌ Questions arriving later are marked, which the teacher may notice
B) Keep CEO-21 as is
  ✅ The teacher never sees a receipt without questions
  ✅ No extra state or test
  ❌ An outage can withhold every receipt indefinitely
Net: a bounded wait versus a receipt that is always complete but maybe never arrives.
Header: Release cap
Options:
A) Add a 48 h cap (recommended)
Release = latest of (deadline, submit + 24 h, questions compiled), but no later than latest of (deadline, submit + 24 h) + 48 h. At the cap, release L1 "questions pending", alert the operator, add questions later marked "added after release". Frozen-clock test. human: ~2h / CC: ~10 min.
B) Keep CEO-21 as is
No cap; the teacher sees "still compiling" until questions compile.

State: approved
Actual answer: A) "Add a 48 h cap (recommended)", D7 answer 2026-10-23
Accepted scope: release no later than latest of (deadline, submit + 24 h) + 48 h; at the cap L1 receipt released as "questions pending", operator alert, questions added later marked "added after release"; frozen-clock test. CEO-21 otherwise unchanged.
History: CEO-21 approved 2026-10-23 (O5). Reopened 2026-10-23 for the outage risk above.

### A4: what "sealed" means
Finding: A4, P2, 8/10, event-log.md:23 + :105, Claude (main)
Plan baseline: submit seals; head hash emailed; resubmission continues the chain.
Runtime evidence: none.
Comparison grid:
| Choice | Current | A | B |
|---|---|---|---|
| Hash the student holds | "head hash" (undefined point) | hash of the `submit` event (the seal) | as is |
| What verify proves | chain from genesis | prefix up to the seal is unchanged; receipt lines cite events at or before the seal, except marked post-seal notes | as is |
| Events allowed after a seal | any | whitelist: receipt.issued, note.add, link.add, record.withdrawn, resubmit.open | any |
| Editor batch after submit | undefined | 409 unless resubmit.open; each new seal → new receipt citing its seal seq | undefined |
Question D8:
D8 — Define exactly what the submit seal covers?
Project/branch/task: main, eng review of the v1 plan set.
ELI10: At submit we email the student a fingerprint (hash) of their record. But things still get added after submit: the receipt itself, notes the student adds, a withdrawal. So we need to say precisely which fingerprint the student holds (the one at the moment of submitting), what checking it proves (nothing before that moment changed), and which kinds of events are allowed after it. Editing after submit is refused unless the teacher opens a resubmission, which gets its own seal and receipt.
Stakes if we pick wrong: Left vague, the promise 'nobody can change it after submission' can't be checked, and resubmissions mix two records.
Recommendation: A because it makes the one cryptographic promise (OL-035 a) testable in S5.
Completeness: A=9/10, B=5/10
Pros / cons:
A) Seal = the submit event (recommended)
  ✅ The student's hash proves exactly the pre-submit record is unchanged
  ✅ Post-seal events limited to a whitelist; S5 tests each
  ❌ Small schema and verify additions (an hour or two)
B) Leave as written
  ✅ No extra rules to implement
  ✅ Fewer event types to document
  ❌ 'Sealed' is untestable; resubmission semantics stay undefined
Net: a precise, testable promise for a couple of hours of work.
Header: Seal rule
Options:
A) Seal = submit event (recommended)
Student holds the hash of the `submit` event. verify proves the prefix to it. After a seal only receipt.issued, note.add, link.add, record.withdrawn, resubmit.open may append; editor batches get 409 unless resubmit.open; each receipt cites its seal seq. S5 adds a "post-seal edit" tamper case. human: ~3h / CC: ~15 min.
B) Leave as written
No definition beyond event-log.md §6.

State: approved
Actual answer: A) "Seal = submit event (recommended)", D8 answer 2026-10-23
Accepted scope: student holds hash of the submit event; verify proves prefix; post-seal whitelist receipt.issued, note.add, link.add, record.withdrawn, resubmit.open; editor batch after submit → 409 unless resubmit.open; each receipt cites its seal seq; S5 adds post-seal tamper case.
History: none

### P-9: security tests and receipt rendering
Finding: P-9, P1, 7/10, ceo-review-v1.md:699 + privacy.md:67 "Per-tenant row filtering enforced in one data-access layer", Claude (main)
Plan baseline: P-9 pending (authz per route, text-only rendering + CSP, teacher audit events).
Runtime evidence: no code. The kit's web app has rate limits (privacy.md:68), not authz.
Comparison grid:
| Choice | Current | A | B |
|---|---|---|---|
| Data access | "one layer" (privacy.md:67) | every query goes through a repo layer that requires (tenant, role, owner) | same |
| Route test | none | enumerate every route; another student's or class's ID → 404 | same |
| Receipt rendering | unspecified | student text rendered as text only; strict CSP (default-src 'self', no inline script) | not specified |
| Teacher audit | none | teacher opens/exports logged in an audit table (not the student's log) | none |
Question D9:
D9 — Lock down who can see what, with a test for every route?
Project/branch/task: main, eng review of the v1 plan set.
ELI10: Receipts and logs hold students' writing. The usual leak is simple: change the number in a URL and you see someone else's receipt. The fix is one gate every database read passes through (which school, which role, whose data), plus a test that walks every route and tries someone else's ID. Students' text on the receipt is shown as plain text with a strict browser policy, so a student can't plant a script that runs in the teacher's browser. Teacher opens and exports get logged.
Stakes if we pick wrong: One missed route exposes another student's writing; one unescaped field lets a student run code in the teacher's session.
Recommendation: A because these are the standard protections for student data and cheap to test now.
Completeness: A=10/10, B=7/10
Pros / cons:
A) Full set (recommended)
  ✅ Route-enumeration test catches any route that skips the tenant gate
  ✅ CSP + text-only rendering stops stored script in receipts
  ❌ About half a day more than authz alone
B) Authz + route test only
  ✅ Covers the most likely leak (guessing IDs)
  ✅ Less work before M5
  ❌ No CSP or audit trail; teacher access to receipts unrecorded
Net: half a day for complete student-data protection versus the most likely hole only.
Header: Security
Options:
A) Full set (recommended)
Repo layer requires (tenant, role, owner); route-enumeration test (foreign ID → 404); text-only rendering + strict CSP on all pages; teacher open/export audit rows. human: ~1 day / CC: ~40 min.
B) Authz + route test only
Repo layer + route-enumeration test; no CSP, no teacher audit. human: ~0.5 day / CC: ~25 min.

State: approved
Actual answer: A) "Full set (recommended)", D9 answer 2026-10-23
Accepted scope: repo layer requires (tenant, role, owner); route-enumeration test (foreign ID → 404); text-only rendering + strict CSP on all pages; teacher open/export audit rows.
History: none

### P-10: submit guards and two tabs
Finding: P-10, P1, 8/10, ceo-review-v1.md:700 + event-log.md:101 "single-writer: one student, one document", Claude (main)
Plan baseline: P-10 pending.
Runtime evidence: no code.
Comparison grid:
| Choice | Current | A | B |
|---|---|---|---|
| Flush before submit | none | Submit enabled only after the client queue is empty and acked | same |
| Double submit | "idempotent" | one submit per doc_rev (idempotency key) | same |
| Empty submit | none | 0 words blocked with a message | same |
| Resubmission | undefined | teacher setting per assignment, default off (with D8) | same |
| Two tabs / devices | not designed | edit lease per log (heartbeat 30 s, expiry 90 s); second tab read-only with "edit here instead" | no lease: second tab gets 409 on rev conflict and reloads, losing unsent edits in that tab |
Question D10:
D10 — Submit guards and what happens with two open tabs?
Project/branch/task: main, eng review of the v1 plan set.
ELI10: Four small guards keep a submission honest: don't allow Submit until every edit has reached the server, accept one submit per version, block empty submissions, and let the teacher decide whether resubmitting is allowed. The bigger question is two tabs (say a laptop and a library PC). Either only one can edit at a time and the other shows read-only with an 'edit here instead' button, or both can type and one gets a conflict and reloads, losing its unsent words.
Stakes if we pick wrong: Without a lease, a student working on two devices can lose writing or fork their document.
Recommendation: A because losing a student's words is the worst user-facing failure we can have.
Completeness: A=10/10, B=7/10
Pros / cons:
A) Guards + edit lease (recommended)
  ✅ No lost words: only one place edits; the other is read-only
  ✅ Submit seals exactly what the student sees
  ❌ Lease logic + a Playwright two-tab test (~half a day)
B) Guards, no lease
  ✅ Simpler server; conflicts handled by reload
  ✅ Same submit guards
  ❌ The losing tab's unsent edits are dropped
Net: half a day to make 'lost my work' impossible versus rare but real data loss.
Header: Submit/tabs
Options:
A) Guards + edit lease (recommended)
Flush-then-enable Submit; one submit per doc_rev; 0-word block; resubmission setting (default off); edit lease per log (30 s heartbeat, 90 s expiry), second tab read-only with takeover. Playwright: two tabs + offline submit. human: ~1 day / CC: ~45 min.
B) Guards, no lease
Same four guards; second tab gets 409 and reloads (unsent edits there are lost). human: ~0.5 day / CC: ~20 min.

State: approved
Actual answer: A) "Guards + edit lease (recommended)", D10 answer 2026-10-23
Accepted scope: flush-then-enable Submit; one submit per doc_rev; 0-word block; resubmission setting default off; edit lease per log (30 s heartbeat, 90 s expiry), second tab read-only with takeover; Playwright two-tab + offline submit tests.
History: none

### P-11: scanner-safe magic link
Finding: P-11, P1, 8/10, ceo-review-v1.md:701; architecture.md:6 "the link opens a page whose button signs in", Claude (main)
Plan baseline: CEO-8 approved roster + magic link; the scanner-safe detail is pending P-11 (named in the override box, not decided).
Runtime evidence: none. University mail gateways commonly pre-fetch links (Safe Links style scanners) [Layer 1 knowledge].
Comparison grid:
| Choice | Current | A | B |
|---|---|---|---|
| What GET does | consumes token (implied) | shows a page; a button POSTs the token | GET consumes (as is) |
| Token | one-time | single use, 30 min expiry, bound to the roster email, stored hashed | one-time |
| Test | none | GET never consumes; reused/expired token rejected | reused/expired rejected |
Question D11:
D11 — Make the sign-in link safe from email scanners?
Project/branch/task: main, eng review of the v1 plan set.
ELI10: Students sign in with a one-time link in an email. University mail systems often 'click' every link to scan it for malware before the student sees the email. If opening the link uses up the token, the scanner uses it and the student's real click fails. The fix: the link opens a page with a 'Sign in' button, and only the button press uses the token.
Stakes if we pick wrong: Students at a school with link scanning can't sign in on day one.
Recommendation: A because it costs an hour and removes a known day-one failure.
Completeness: A=10/10, B=5/10
Pros / cons:
A) Page + button POST (recommended)
  ✅ Scanners can't burn the token; real students always get in
  ✅ Token single-use, 30 min, hashed at rest
  ❌ One extra click for the student
B) Link signs in directly
  ✅ One click fewer
  ✅ Slightly less code
  ❌ Breaks wherever mail scanners pre-open links
Net: one extra click versus a sign-in failure you can't fix mid-pilot.
Header: Magic link
Options:
A) Page + button POST (recommended)
GET shows a page; the button POSTs the token. Single use, 30 min expiry, bound to the roster email, stored hashed. Tests: GET doesn't consume; reused/expired rejected. human: ~2h / CC: ~10 min.
B) Link signs in directly
GET consumes the token (as implied now).

State: approved
Actual answer: A) "Page + button POST (recommended)", D11 answer 2026-10-23
Accepted scope: GET shows a page, button POSTs the token; single use, 30 min expiry, bound to roster email, stored hashed; tests: GET doesn't consume, reused/expired rejected.
History: none

### A5: coarser timestamps on editor batches
Finding: A5, P2, 6/10, event-log.md:44 + :98, Claude (main)
Plan baseline: every event ts = server receive time to the second; batches every ~2 s of activity.
Runtime evidence: none. The receipt uses only sessions and dates (receipt.md:31, :53 "date + hour only").
Comparison grid:
| Choice | Current | A | B | C |
|---|---|---|---|---|
| editor.batch ts stored | to the second | rounded down to 5 min | rounded to 1 min | to the second (as is) |
| Other events (submit, receipt, coach) | to the second | unchanged | unchanged | unchanged |
| Sessions on the receipt | derived | gap ≥ 30 min between batches = new session | same | same |
Question D12:
D12 — Store editor activity times more coarsely?
Project/branch/task: main, eng review of the v1 plan set.
ELI10: We promise 'we record what changed in the text, not how you typed it'. But the editor sends a small batch every ~2 seconds while the student types, each stamped to the second. Line those up and you get a fairly detailed picture of when and how fast someone typed. The receipt only needs sessions and dates. Rounding batch times to 5 minutes keeps everything the receipt needs and drops the typing rhythm.
Stakes if we pick wrong: Second-level batch times could be read as a typing timeline, which contradicts our privacy promise and consent text.
Recommendation: A because the receipt needs only sessions and dates, and the privacy floor is part of law 7.
Completeness: A=9/10, B=8/10, C=5/10
Pros / cons:
A) Round to 5 minutes (recommended)
  ✅ No typing rhythm in the log; matches 'not how you typed'
  ✅ Sessions (30-min gaps) still derivable for the receipt
  ❌ Support debugging loses fine-grained timing
B) Round to 1 minute
  ✅ More detail for debugging
  ✅ Still hides per-burst rhythm mostly
  ❌ A minute-level activity trace is still fairly revealing
C) Keep seconds
  ✅ Simplest, no rounding rule
  ✅ Best for debugging
  ❌ A ~2-second activity timeline sits in the record
Net: a small debugging loss in exchange for keeping the privacy promise literally true.
Header: Timestamps
Options:
A) Round to 5 minutes (recommended)
editor.batch ts rounded down to 5 min before hashing; other events keep seconds; a 30-min gap starts a new session. Unit test on rounding + session split. human: ~1h / CC: ~5 min.
B) Round to 1 minute
Same rule at 1-minute granularity.
C) Keep seconds
As event-log.md says now.

State: approved
Actual answer: A) "Round to 5 minutes (recommended)", D12 answer 2026-10-23
Accepted scope: editor.batch ts rounded down to 5 min before hashing; other events keep seconds; 30-min gap = new session; unit test.
History: none

### P-6: AI failure classes and a boot check
Finding: P-6, P2, 8/10, shared/llm.py:62 `raise BadOutput("empty model output")` and :38 `raise NoKey(...)` at call time, Claude (main)
Plan baseline: P-6 pending (distinct handling for refusal, empty output, auth failure; boot health check).
Runtime evidence: shared/llm.py has NoKey, Upstream, BadOutput. Empty output and malformed JSON both raise BadOutput (:60, :62, :82). 401/403 surface as Upstream("HTTP 401") with no retry (:65). No schema validation.
Comparison grid:
| Choice | Current | A | B |
|---|---|---|---|
| Error classes from `complete()` | 3 (NoKey, Upstream, BadOutput) | Timeout, RateLimited, Auth (401/403/NoKey), Refusal (empty or refusal text), Schema (fails the task's pydantic schema) | the 3 existing |
| Rescue per class | mixed | timeout/429 → retry ×2 then other backend; schema/refusal → regenerate once then drop; auth → mark backend down + alert | all → "AI help unavailable" |
| Boot check | none | ping each configured backend at start; AI shown unavailable if auth fails | none |
| Tests | none | one unit test per class with a fake transport | one generic test |
Question D13:
D13 — Handle each kind of AI failure differently, and check keys at startup?
Project/branch/task: main, eng review of the v1 plan set.
ELI10: AI calls fail in different ways. A timeout is worth retrying. An empty answer or bad JSON is worth asking again once. A wrong API key will never fix itself, so we should know at startup, not when the first student submits. Today our client lumps empty answers and bad JSON together and only finds a missing key when a call is made. The fix gives each failure its own type and its own response, plus a startup check that pings each AI backend.
Stakes if we pick wrong: A bad key or a provider change goes unnoticed until students are mid-assignment, and retries are wasted on failures that can't recover.
Recommendation: A because it turns silent, confusing failures into specific, tested behaviour before students arrive.
Completeness: A=9/10, B=5/10
Pros / cons:
A) Five classes + boot check (recommended)
  ✅ Auth failures caught at deploy, not by a student at submit
  ✅ Retries only where they can help; each path unit-tested
  ❌ A few hours to wrap shared/llm.py and add fake-transport tests
B) Keep the three classes
  ✅ No change to shared/llm.py behaviour
  ✅ Less code
  ❌ Bad keys and refusals look the same as malformed JSON
Net: a few hours for failures you can see and act on before the class does.
Header: AI errors
Options:
A) Five classes + boot check (recommended)
`complete()` maps to Timeout, RateLimited, Auth, Refusal, Schema (pydantic per task); per-class rescue as in the CEO registry; startup ping per backend; one fake-transport test per class. shared/llm.py stays the DeepSeek transport. human: ~0.5 day / CC: ~25 min.
B) Keep the three classes
Map NoKey/Upstream/BadOutput to "AI help unavailable".

State: approved
Actual answer: A) "Five classes + boot check (recommended)", D13 answer 2026-10-23
Accepted scope: complete() raises Timeout, RateLimited, Auth, Refusal, Schema (pydantic per task); per-class rescue per CEO registry; startup ping per backend; fake-transport unit test per class; shared/llm.py stays the DeepSeek transport.
History: none

### P-17: shape of the second AI backend
Finding: P-17, P2, 6/10, ceo-review-v1.md:898; shared/llm.py:11 `BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", ...)`, Claude (main)
Plan baseline: CEO-6 approved a second backend behind `complete()`; its shape is pending P-17 (OpenAI-compatible endpoint with configurable base URL).
Runtime evidence: shared/llm.py already speaks the OpenAI chat-completions format with a configurable base URL, so one parameterised transport can serve both backends. Azure OpenAI uses an `api-key` header and deployment paths [unverified for the current Azure v1 endpoint].
Comparison grid:
| Choice | Current | A | B |
|---|---|---|---|
| Backend 2 | unnamed | generic OpenAI-compatible transport (base URL, model, key, auth header name configurable), reusing shared/llm.py's request code | a named vendor SDK chosen now |
| Golden fixtures | both backends (CEO-6) | unchanged | unchanged |
| Provider confirmation | OL-037 | founder confirms which backend the school allows, in HK, before M5 | vendor fixed now |
Question D14:
D14 — Make the second AI backend a generic 'OpenAI-compatible' slot?
Project/branch/task: main, eng review of the v1 plan set.
ELI10: You agreed to have a second AI provider ready in case the school won't accept DeepSeek. We don't know yet which one the school will allow, and some (OpenAI direct, Anthropic) may not be offered in Hong Kong. Most providers, including a school's own Azure account, accept the same request format DeepSeek uses. So instead of picking a vendor now, build one generic slot where you set the address, model and key, and the school's choice drops in.
Stakes if we pick wrong: Picking a vendor now may mean rebuilding when the school names a different one.
Recommendation: A because our DeepSeek client already uses that format, so the slot is mostly configuration.
Completeness: A=9/10, B=7/10
Pros / cons:
A) Generic OpenAI-compatible slot (recommended)
  ✅ Fits DeepSeek, Azure OpenAI in the school's tenant, and others
  ✅ Reuses shared/llm.py's request code; mostly config
  ❌ Vendor-specific features (e.g. strict JSON schema mode) not used
B) Named vendor SDK now
  ✅ Can use that vendor's strongest features
  ✅ Fewer config knobs
  ❌ Wasted if the school picks a different provider
Net: stay flexible until the school decides, at almost no cost.
Header: Backend 2
Options:
A) Generic slot (recommended)
One OpenAI-compatible transport with base URL, model, key and auth-header name from config; backend 2 = whatever the school approves; fixtures for both. Founder confirms the HK-available provider before M5. human: ~2h / CC: ~10 min.
B) Named vendor SDK
Pick and integrate one vendor's SDK now.

State: approved
Actual answer: A) "Generic slot (recommended)", D14 answer 2026-10-23
Accepted scope: one OpenAI-compatible transport (base URL, model, key, auth-header name from config) reusing shared/llm.py request code; backend 2 = school-approved provider; fixtures for both; founder confirms HK-available provider before M5.
History: none

### P-8: logs, counters, alerts and runbooks
Finding: P-8, P2, 7/10, ceo-review-v1.md:698, Claude (main)
Plan baseline: CEO-7 approved an operator alert on L3 failure; the rest is pending P-8.
Runtime evidence: none for the prototype. The kit logs call metadata to `_calls.jsonl` (llmx.py:41-47), never prompt text.
Comparison grid:
| Choice | Current | A | B |
|---|---|---|---|
| Logs | none | structured JSON with request_id, log_id; never student text or keys | same |
| Counters | none | batch rejects, compile failures, questions_pending receipts, release-cap hits, leak-check fails, LLM errors by backend and class, spend per submission; shown on an operator page | none |
| Alerts (email) | CEO-7 compile alert | compile failure, LLM auth failure, any leak-check fail, release cap reached | CEO-7 only |
| Runbooks | none | 3 short docs: "AI down", "my work is missing", "teacher can't see a receipt" | none |
Question D15:
D15 — What monitoring do you need to run one class alone?
Project/branch/task: main, eng review of the v1 plan set.
ELI10: You'll be the only person running this. When something breaks at 11 pm before a deadline, you need to know quickly and know what to do. That means logs that never contain student text, a handful of counters on one operator page (failed compiles, leak-check failures, AI errors, cost per submission), email alerts on the four things that need you now, and three one-page runbooks.
Stakes if we pick wrong: Without counters and alerts you'll learn about a broken compile or a leak from the teacher.
Recommendation: A because a solo operator needs the system to tell them, and the counters also feed the pilot's cost measure.
Completeness: A=9/10, B=5/10
Pros / cons:
A) Logs + counters + alerts + runbooks (recommended)
  ✅ You hear about failures before the teacher does
  ✅ Spend per submission is measured, as evaluation.md §3 needs
  ❌ About half a day; an operator page to maintain
B) Logs + the CEO-7 alert only
  ✅ Least work
  ✅ Covers the most likely failure (AI down at submit)
  ❌ Leak-check fails and auth errors stay silent
Net: half a day for running the pilot without flying blind.
Header: Monitoring
Options:
A) Full set (recommended)
Structured logs (request_id, log_id; no student text); counters on an operator page; email alerts on compile failure, LLM auth failure, any leak fail, release cap reached; 3 runbooks in docs/. Smoke test reads counters. human: ~1 day / CC: ~30 min.
B) Logs + CEO-7 alert only
Structured logs and the compile-failure alert.

State: approved
Actual answer: A) "Full set (recommended)", D15 answer 2026-10-23
Accepted scope: structured logs (request_id, log_id; no student text); counters on an operator page; email alerts on compile failure, LLM auth failure, any leak fail, release cap reached; 3 runbooks; smoke test reads counters.
History: none

### A6: drop reading dwell time
Finding: A6, P3, 8/10, event-log.md:54 `dwell_bucket: <10s | 10–60s | >60s` vs provenance.md:104 "block kinds opened and anchored", Claude (main)
Plan baseline: event-log.md §8 open question; default "coarse buckets, review in /plan-eng-review".
Runtime evidence: no receipt fact, band or question reads dwell.
Comparison grid:
| Choice | Current | A | B |
|---|---|---|---|
| source.view_span payload | source_id, block_ids, dwell_bucket | source_id, block_ids (opened only) | as is |
| Receipt reading depth | opened + anchored | unchanged | unchanged |
| Consent text | "which parts of your readings you open" | unchanged | unchanged |
Question D16:
D16 — Stop recording how long students spend on each passage?
Project/branch/task: main, eng review of the v1 plan set.
ELI10: The reader logs which passages a student opens, and also roughly how long they stayed (under 10 s, 10–60 s, over a minute). Nothing on the receipt uses the time: reading depth is 'which parts were opened and anchored'. Collecting data we don't use is a privacy cost with no benefit, and it invites misreading ('only skimmed').
Stakes if we pick wrong: Keeping it adds timing data the consent doesn't need, and it could later be misread as a measure of effort.
Recommendation: A because no feature uses it and law 7 says collect the minimum.
Completeness: A=9/10, B=7/10
Pros / cons:
A) Drop dwell (recommended)
  ✅ Less timing data; consent stays simple
  ✅ One less field to explain to teachers
  ❌ Can't study reading time later without a schema bump
B) Keep coarse buckets
  ✅ Data available if a later feature wants it
  ✅ No change to event-log.md
  ❌ Unused timing data, open to being read as effort
Net: drop an unused privacy cost; add it back with a version bump if a feature needs it.
Header: Dwell time
Options:
A) Drop dwell (recommended)
source.view_span = source_id + block_ids only. event-log.md §3 and §8 updated. human: ~10 min / CC: ~2 min.
B) Keep coarse buckets
As event-log.md says now.

State: approved
Actual answer: A) "Drop dwell (recommended)", D16 answer 2026-10-23
Accepted scope: source.view_span = source_id + block_ids only; event-log.md §3 and §8 updated.
History: none

Section 1 dispositions: A1 accepted (D5), A2 accepted (D6), A3 accepted, reopening CEO-21 (D7), A4 accepted (D8), P-9 accepted (D9), P-10 accepted (D10), P-11 accepted (D11), A5 accepted (D12), P-6 accepted (D13), P-17 accepted (D14), P-8 accepted (D15), A6 accepted (D16).

## Section 2: Code quality review

Findings (most severe first):
- **Q1** [P1] (confidence: 8/10) provenance.md:45 "A sentence→claim link is *recorded* when the student links it explicitly in the editor". **The plan never says how a link survives later edits.** Sentences are re-split from the final document at compile time, so a link stored as "sentence 14" points at the wrong text after the student edits above it.
- **P-13** [P2] (confidence: 9/10) room.py:20-22 `CORPUS = json.load(open(V04.parent / "data" / "corpus.json"))` and audit.py:13 `for t in room.PASSAGES.values()`. The kit's coach and audit code is bound to the fictional corpus at import. What can be reused is the prompts (`policies/*.md`, the law-1 judge text at audit.py:50-52), not the modules.
- **P-16** [P2] (confidence: 7/10) ceo-review-v1.md:897 "Hand-written golden logs are toys". Golden logs are the executable spec for bands and receipts. If they're hand-written, they won't contain real ProseMirror steps, so replay (D6) and the mark check (D5) go untested.
- **Q2** [P2] (confidence: 7/10) provenance.md:57 "at least 30% … **[ASSUMPTION: tune on golden sessions]**", plus CEO-14's L3b on/off flag. A receipt doesn't record which thresholds, flags, models or prompts produced it, so it can't be reproduced or explained later.
- Shared code: `shared/llm.py` is the one transport for the kit and the prototype (D14 reuses it). No other extraction qualifies: there aren't two authored callers with the same contract.
- Diagrams: architecture.md §1 and §6 are stale after D1–D3 (L2 box, worker queue, Postgres, the six packages). They get fixed under P-14.

### Q1: claim links travel with the text
Finding: Q1, P1, 8/10, provenance.md:45, Claude (main)
Plan baseline: recorded sentence→claim link, storage unspecified; CEO-17 labels student links.
Runtime evidence: none.
Comparison grid:
| Choice | Current | A | B |
|---|---|---|---|
| How a link is stored | unspecified | a second ProseMirror mark `claim{claim_id, by: student \| coach \| import}` on the text range; moves with edits like origin marks | a DB row (sentence index or char offsets at link time) |
| After the student edits nearby | undefined | link stays on its words | link drifts or breaks |
| Sentence's claim at compile | — | claim mark covering most of the sentence's characters; ties → both claims listed | row lookup |
| CEO-17 labels and the post-submit rule | approved | unchanged | unchanged |
| Tests | none | S1 cases repeated for claim marks; golden "edit above a linked sentence" | none |
Question D17:
D17 — Store claim links as marks on the words, so they survive editing?
Project/branch/task: main, eng review of the v1 plan set.
ELI10: A student can say 'this sentence makes claim 3'. If we store that as 'sentence number 14', then adding a sentence above it makes the link point at the wrong text. The editor already labels every character with where it came from; claim links can work the same way, as a second label on the words themselves, so they move with the text when the student edits. At receipt time each sentence takes the claim label on most of its words.
Stakes if we pick wrong: Links silently attach to the wrong sentences, so the chain view shows a student's claim next to text that doesn't make it.
Recommendation: A because it reuses the origin-mark machinery S1 already tests, and links can't drift.
Completeness: A=9/10, B=4/10
Pros / cons:
A) Claim links as marks (recommended)
  ✅ Links follow the words through edits, moves, undo and copy-paste
  ✅ Same S1 tests and the same D5 compile check apply
  ❌ A second mark type in the schema (Python mirror too, D6)
B) DB rows by position
  ✅ Simple to store and query
  ✅ No editor schema change
  ❌ Any edit above the sentence breaks or misplaces the link
Net: reuse the mark machinery and get links that can't drift.
Header: Claim links
Options:
A) Claim links as marks (recommended)
`claim{claim_id, by}` mark on text ranges, carried like origin marks; at compile a sentence's claim = the claim mark on most of its characters (ties list both); S1 cases repeated for claim marks; golden "edit above a linked sentence". human: ~0.5 day / CC: ~25 min.
B) DB rows by position
Store links as sentence index or offsets at link time.

State: approved
Actual answer: A) "Claim links as marks (recommended)", D17 answer 2026-10-23
Accepted scope: claim{claim_id, by} mark on text ranges carried like origin marks; sentence's claim = mark on most of its characters (ties list both); S1 cases repeated for claim marks; golden "edit above a linked sentence".
History: none

### P-13: what to port from the kit
Finding: P-13, P2, 9/10, room.py:20-22 + audit.py:13, Claude (main)
Plan baseline: CEO pending P-13: "port kit coach/audit once; kit frozen". coach-helper.md:92 "ports them into prototype/server/coach/".
Runtime evidence: room.py and audit.py import the fictional corpus at module load; the policies/*.md prompts and the law-1 judge prompt are plain text.
Comparison grid:
| Choice | Current | A | B |
|---|---|---|---|
| What moves | "port the modules" | prompts only: policies/*.md (corpus references removed) → coach/prompts/; law-1 judge text → coach/leak.py | copy room.py, audit.py, coach.py and adapt |
| Leak-check code | kit audit.py | one module coach/leak.py, used by the app at serve time and by the leak-audit tests | adapted copy |
| Kit | live | frozen: README note "frozen 2026-10-23"; its 29 tests keep running | live, two copies drift |
Question D18:
D18 — Port the kit's prompts, not its code?
Project/branch/task: main, eng review of the v1 plan set.
ELI10: The kit is our earlier experiment. Its assistant and audit code load a made-up reading list (the HK rent-control corpus) the moment they start, so they can't just be copied into the real product. What is worth keeping is the wording: the policy prompts and the 'did the AI write the student's argument?' judge prompt. The plan: move those prompts over, write the coach and leak-check code fresh against the real data, make one leak-check module that both the product and its tests use, and freeze the kit so the experiments stay reproducible.
Stakes if we pick wrong: Adapting kit code drags fictional-corpus assumptions into the product, and two leak checks drift apart, which is risky for law 1.
Recommendation: A because the prompts are the proven part; the code is tied to the old corpus.
Completeness: A=9/10, B=6/10
Pros / cons:
A) Port prompts, write code fresh (recommended)
  ✅ One leak-check module for the app and the tests (law 1)
  ✅ No fictional-corpus assumptions in the product
  ❌ Coach code written fresh (~half a day more than copying)
B) Copy and adapt the kit modules
  ✅ Starts from code that ran in v0.4
  ✅ Faster first commit
  ❌ Corpus coupling and two drifting leak checks
Net: keep the proven prompts and drop the coupled code.
Header: Kit port
Options:
A) Port prompts, fresh code (recommended)
policies/*.md (corpus refs removed) → server/coach/prompts/; law-1 judge prompt → server/coach/leak.py, imported by the app and the leak-audit tests; kit marked frozen 2026-10-23, its tests still run. human: ~0.5 day / CC: ~25 min.
B) Copy and adapt kit modules
Copy room.py/audit.py/coach.py into server/coach/ and adapt.

State: approved
Actual answer: A) "Port prompts, fresh code (recommended)", D18 answer 2026-10-23
Accepted scope: policies/*.md (corpus refs removed) → server/coach/prompts/; law-1 judge → server/coach/leak.py used by app + leak-audit tests; kit frozen 2026-10-23, its tests still run.
History: none

### P-16: how golden logs are made
Finding: P-16, P2, 7/10, ceo-review-v1.md:897, Claude (main)
Plan baseline: P-16 pending: "generate by scripting the S1 page or converting kit v04 runs". Build plan M1: "Golden logs generated by scripting the S1 page, or converted from kit v04 runs (P-16), frozen after S1".
Runtime evidence: kit v04 runs are turn transcripts (room.py add_turn), not editor steps.
Comparison grid:
| Choice | Current | A | B | C |
|---|---|---|---|---|
| Editor steps | — | real ProseMirror steps from Playwright driving the S1 page (later the M3 editor) | synthesised from kit transcripts | hand-written JSON |
| Non-editor events (cards, anchors, Coach, Door) | — | a Python session builder posting through the real ingest API | converted | hand-written |
| Spec format | — | one YAML script per golden session (actions + expected bands/moments/question targets) | kit run files | JSON |
| Kit v04 runs | — | used only for S4 replay (simulated, labelled) | main source | not used |
Question D19:
D19 — Make golden sessions by driving the real editor?
Project/branch/task: main, eng review of the v1 plan set.
ELI10: Golden sessions are scripted fake students whose expected receipts define 'correct' for the engine. If we write their logs by hand or convert old kit transcripts, they won't contain the real edit steps the editor produces, so the replay (D6) and the mark check (D5) never get tested on realistic data. Better: a short script per session (open reading, make card, type, paste, answer Coach) that drives the real editor page in a headless browser and sends the other events through the real API.
Stakes if we pick wrong: The engine passes golden tests on data no real editor would produce, and breaks on the first real student.
Recommendation: A because golden logs must exercise the same steps and ingest path students will.
Completeness: A=9/10, B=6/10, C=4/10
Pros / cons:
A) Drive the real editor (recommended)
  ✅ Real ProseMirror steps and marks; replay and mark check really tested
  ✅ Scripts are readable specs; regenerate when the editor changes
  ❌ Needs the S1 page working first (M0), so M1 starts after S1
B) Convert kit v04 runs
  ✅ Reuses existing simulated sessions
  ✅ Available before any editor exists
  ❌ Steps are synthesised; editor behaviour untested
C) Hand-write logs
  ✅ Fastest to start
  ✅ Full control of edge cases
  ❌ Toys: no realistic steps, easy to make internally consistent but wrong
Net: realistic logs that test the real path versus logs available a day earlier.
Header: Golden logs
Options:
A) Drive the real editor (recommended)
YAML script per session → Playwright drives the S1 page (later the M3 editor) for steps + a Python builder posts cards/anchors/Coach/Door events through ingest; outputs frozen; kit v04 runs only for S4. human: ~1 day / CC: ~45 min.
B) Convert kit v04 runs
Synthesise event logs from kit transcripts.
C) Hand-write logs
Write golden JSON logs by hand.

State: approved
Actual answer: A) "Drive the real editor (recommended)", D19 answer 2026-10-23
Accepted scope: YAML script per golden session; Playwright drives S1 page (later M3 editor) for steps; Python builder posts cards/anchors/Coach/Door via ingest; outputs frozen; kit v04 runs only for S4.
History: none

### Q2: receipts record how they were made
Finding: Q2, P2, 7/10, provenance.md:57 + CEO-14 flag, Claude (main)
Plan baseline: CEO S5-F4 "record the value used in the receipt JSON" (pending, not decided); receipt.md §6 has no such field.
Runtime evidence: none.
Comparison grid:
| Choice | Current | A | B |
|---|---|---|---|
| receipt.json field | none | `engine: {version, git_sha, flags {l3b}, thresholds {...}, models {task: backend/model}, prompt_hashes {task: sha256}}` | none |
| Reproducibility test | none | same log + same engine block + stub fixtures → byte-identical receipt (golden) | none |
| Teacher-facing | — | not shown; available in the chain view's "about this receipt" | — |
Question D20:
D20 — Stamp each receipt with the settings that produced it?
Project/branch/task: main, eng review of the v1 plan set.
ELI10: A receipt depends on settings we'll tune during the pilot: thresholds like 'at least 30% typed', whether the AI claim check is on, which AI model and which prompt version. If a teacher asks 'why does this say untraced?' a month later, we need to know which settings made it. The fix: each receipt carries a small block naming its engine version, flags, thresholds, models and prompt fingerprints, plus a test that rebuilding with the same block gives the identical receipt.
Stakes if we pick wrong: You can't explain or reproduce an old receipt after tuning, which is exactly when a dispute will ask.
Recommendation: A because it costs an hour and makes every receipt explainable later.
Completeness: A=9/10, B=5/10
Pros / cons:
A) Stamp receipts (recommended)
  ✅ Any receipt can be rebuilt and explained after tuning
  ✅ The golden test catches accidental changes to output
  ❌ A few fields and one test to maintain
B) No stamp
  ✅ Simpler receipt JSON
  ✅ Nothing extra to test
  ❌ Old receipts can't be explained once settings change
Net: an hour now to answer 'why does this say that?' later.
Header: Engine stamp
Options:
A) Stamp receipts (recommended)
receipt.json gets `engine {version, git_sha, flags, thresholds, models, prompt_hashes}`; golden test: same log + same stamp + stub → byte-identical receipt; shown under "about this receipt". human: ~2h / CC: ~10 min.
B) No stamp
receipt.json as in receipt.md §6.

State: approved
Actual answer: A) "Stamp receipts (recommended)", D20 answer 2026-10-23
Accepted scope: receipt.json engine {version, git_sha, flags, thresholds, models, prompt_hashes}; golden test same log + stamp + stub → byte-identical receipt; shown under "about this receipt".
History: none

Section 2 dispositions: Q1 accepted (D17), P-13 accepted (D18), P-16 accepted (D19), Q2 accepted (D20).

## Section 3: Test review

Framework: the server uses **pytest** (the repo already runs it: `cd writing-room-kit && ROOM_LLM=stub python3 -m pytest -q v04/tests web/tests` gave **29 passed** on 2026-10-23, a live run). The web app gets **Vitest** (unit) and **Playwright** (E2E plus golden generation, D19). Accessibility uses axe-core. No prototype code exists, so every path below is a proposal. Nothing here is "observed".

```
CODE PATHS (proposed)                                          USER FLOWS (proposed)
[+] engine/events                                              [+] Student writes and submits
  ├── append (BEGIN IMMEDIATE, unique log_id+seq)  [GAP] CEO-16  ├── [GAP][→E2E] invite → link page → POST → consent → editor (D11)
  ├── hash/canonical JSON + verify                 [GAP] S5      ├── [GAP][→E2E] type, paste, quote, card, Coach answer → marks right (S1)
  ├── seal rule + post-seal whitelist               [GAP] D8      ├── [GAP][→E2E] offline, then reconnect: queue replays, no dupes
  └── ts rounding + session split                   [GAP] D12     ├── [GAP][→E2E] two tabs: second read-only, takeover (D10)
[+] engine/replay (prosemirror-py)                              ├── [GAP][→E2E] submit disabled until flushed; 0 words blocked (D10)
  ├── steps → doc == client doc_hash               [GAP] D6      └── [GAP]       submit while AI down → sealed, "questions pending"
  └── mismatch → compile error + alert             [GAP] D6     [+] Teacher
[+] engine/provenance                                            ├── [GAP][→E2E] roster upload → assignment → readings → parse status (D4)
  ├── mark check (forged quote/coach/import/helper) [GAP] D5      ├── [GAP]       before release: "still compiling"; after: receipt (CEO-21)
  ├── claim marks → sentence claim (majority, ties) [GAP] D17     ├── [GAP]       at cap with AI down: L1 receipt "questions pending" (D7)
  ├── bands table (one row per rule)                [GAP]         └── [GAP][→E2E] click a sentence → chain view
  ├── student link labels / post-submit links       [GAP] CEO-17 [+] Error states
  ├── reworded unchecked → untraced + note          [GAP] CEO-13  ├── [GAP] scanned PDF → "this PDF is a scan" (D4)
  └── L3b flag off → "unlinked (not checked)"       [GAP] CEO-14  ├── [GAP] oversized upload → limit message (D4)
[+] engine/receipt                                               └── [GAP] guessed receipt ID → 404 (D9)
  ├── compile L1 → v1; L3 → v2                      [GAP] CEO-7
  ├── release = later of three, capped at +48 h     [GAP] D7      LLM integration:
  ├── student preview has no question text          [GAP] CEO-20   [GAP][→EVAL] golden sessions on both backends (CEO-6)
  ├── wording filter                                [GAP]          [GAP][→EVAL] leak audit: golden + ~30 adversarial prompts (CEO-24)
  └── engine stamp, byte-identical rebuild          [GAP] D20      [GAP][→EVAL] S3 claim compare ≥ 40 pairs (CEO-24)
[+] app/llm complete()                                             [GAP][→EVAL] blind question test (CEO-19, human-judged)
  ├── Timeout/RateLimited/Auth/Refusal/Schema        [GAP] D13
  ├── backend 2 via config                          [GAP] D14
  └── boot ping                                     [GAP] D13
[+] app/auth, tenancy, jobs                                     
  ├── magic link: GET doesn't consume; reuse/expiry  [GAP] D11
  ├── route enumeration: foreign ID → 404            [GAP] D9
  ├── CSP header + text-only rendering              [GAP] D9
  └── jobs: lease, retry, resume on boot            [GAP] P-12
[+] sources/parse (caps, status, immutability)      [GAP] D4
[+] coach/ (B, C), leak.py, Door no-fetch           [GAP] D18, CEO-9
[+] shared/llm.py (existing)                         [★★ TESTED] via kit tests (29 passed), stub path only

COVERAGE: 0/48 proposed paths tested (all new; no code yet) | existing: shared/llm.py stub path only
QUALITY: n/a for new code | GAPS: 48 (12 E2E, 4 eval)
Legend: ★★★ behavior + edge + error | ★★ happy path | ★ smoke | [→E2E] integration | [→EVAL] LLM eval
```

Each gap above belongs to an approved decision (CEO-x or D-x), and its test is required proof of that decision. No separate approval is needed. Two new choices come up:
- **T1** [P1] (confidence: 8/10) evaluation.md:24, S1 method "type, paste external, copy/paste internal, move, undo/redo, reload from steps". This list misses the cases most likely to break origin marks:
  - Typing inside or at the end of a marked span. ProseMirror gives typed text the marks at the cursor by default, so typed words would inherit `quote` or `paste_ext`.
  - IME composition.
  - Spellcheck/autocorrect replacement.
  - Drag-and-drop.
  - Select-all then type.
  - Edits made by browser extensions such as Grammarly, which rewrite text inside the editor: an outside-AI channel that would look `typed`.
- **R1** [P1] (confidence: 9/10) regression rule. D13/D14 build on `shared/llm.py`, which the kit and the hosted demo already use (llmx.py:54-56 `import llm` / `llm.chat(...)`). A change there can break the frozen kit (D18) and the demo.

### T1: S1 spike cases
Finding: T1, P1, 8/10, evaluation.md:24, Claude (main)
Plan baseline: S1 cases as in evaluation.md §1; D6 adds replay parity; D17 adds claim marks.
Runtime evidence: ProseMirror `ResolvedPos.marks()` returns the marks typed text would get at a position; marks are inclusive by default ([forum](https://discuss.prosemirror.net/t/rationale-for-inclusiveright-inclusive-change/701)). No editor code yet.
Comparison grid:
| Choice | Current | A | B |
|---|---|---|---|
| Typing inside / at the edges of a marked span | not tested | must yield `typed` (origin set by an input plugin, marks `inclusive: false`) | not tested |
| IME, autocorrect, drag-drop, select-all-replace | not tested | tested; autocorrect/extension replacement recorded with `input_kind: replacement` | not tested |
| Extension edits (Grammarly-style) | not tested | tested in Chrome with the extension on; recorded `input_kind: replacement`, shown as a fact, never a band | not tested |
| D6 parity, D17 claim marks | approved | included | included |
Question D21:
D21 — Widen the editor spike (S1) to the cases most likely to break the labels?
Project/branch/task: main, eng review of the v1 plan set.
ELI10: Spike S1 checks that the 'where did this come from' labels survive real editing before we build on them. Its test list misses the risky cases. By default the editor gives new typing the label of the text around it, so typing inside a quoted passage would be labelled 'quote'. Other gaps: Chinese/Japanese input methods, autocorrect, drag-and-drop, and browser extensions like Grammarly that rewrite text inside the page, which is an outside-AI path that would otherwise look like typing. Adding these to S1 costs a few hours and catches the bugs before golden sessions are generated from this editor.
Stakes if we pick wrong: Labels are wrong in normal use (typing inside a quote, autocorrect), and every receipt built on them is wrong.
Recommendation: A because S1 is the gate for the whole editor, and these are everyday student actions.
Completeness: A=10/10, B=6/10
Pros / cons:
A) Wider S1 (recommended)
  ✅ Catches label inheritance, IME, autocorrect and extension rewrites early
  ✅ Extension rewrites recorded as a fact ('replacement'), not hidden as typing
  ❌ A few more hours in M0 before S1 can pass
B) S1 as written (+ D6, D17)
  ✅ S1 finishes sooner
  ✅ Still covers paste, copy, move, undo and replay
  ❌ Everyday cases untested; bugs surface in golden sessions or real use
Net: a few hours in M0 to make sure the core labels are right in normal use.
Header: S1 cases
Options:
A) Wider S1 (recommended)
Adds: typing inside and at both edges of marked spans → typed (input plugin, `inclusive: false`); IME composition; autocorrect/spellcheck replacement; drag-drop inside (keep marks) and from outside (paste_ext); select-all + type; Grammarly-style extension edits in Chrome → `input_kind: replacement` (a fact, never a band). Plus D6 parity and D17 claim marks. human: ~0.5 day / CC: ~30 min.
B) S1 as written
evaluation.md §1 S1 cases plus the D6 and D17 additions.

State: approved
Actual answer: A) "Wider S1 (recommended)", D21 answer 2026-10-23
Accepted scope: S1 adds typing inside/at edges of marked spans → typed (input plugin, inclusive: false); IME; autocorrect/spellcheck replacement; drag-drop inside (keep marks) and from outside (paste_ext); select-all + type; Grammarly-style extension edits → input_kind replacement (fact, never a band); plus D6 parity and D17 claim marks.
History: none

### R1: regression contract for shared/llm.py
Finding: R1, P1, 9/10, writing-room-kit/v04/llmx.py:54-56 `import llm` / `out = llm.chat(system, user, ...)`, Claude (main)
Plan baseline: D13 ("shared/llm.py stays the DeepSeek transport"), D14 ("reusing shared/llm.py request code"), D18 ("kit frozen, its tests still run").
Runtime evidence: 29 kit + web tests pass with ROOM_LLM=stub (live run, 2026-10-23). Stub mode lives in llmx.py:12-13, not in shared/llm.py.
Comparison grid:
| Choice | Current | A | B |
|---|---|---|---|
| shared/llm.py `chat()`, `parse_json()`, error classes, env vars | used by kit + demo | unchanged; prototype wraps it in server/app/llm.py; only optional keyword params may be added | refactored into a transport class; kit callers updated |
| Kit + web tests | 29 pass, not in CI | run in CI on every change, must stay green | same |
| Intentional behaviour changes | — | none | transport API changes, kit edited (breaks "frozen") |
Question D22:
D22 — How do we protect the kit and demo when the AI client grows?
Project/branch/task: main, eng review of the v1 plan set.
ELI10: The prototype's new AI layer builds on shared/llm.py, the same file the frozen kit and the hosted demo use. If we change it carelessly, the old experiments or the demo break. The safe contract: leave its functions exactly as they behave today, put the new error types and second backend in a wrapper inside the prototype, allow only new optional settings, and run the kit's 29 tests in CI so any break shows up immediately.
Stakes if we pick wrong: A refactor breaks the hosted demo or makes the kit's published results irreproducible.
Recommendation: A because the kit is frozen (D18) and the demo is live; wrapping costs nothing extra.
Completeness: A=10/10, B=8/10
Pros / cons:
A) Wrap, don't change (recommended)
  ✅ Kit and demo keep working; results stay reproducible
  ✅ 29 existing tests in CI guard the contract
  ❌ Two layers (transport + wrapper) to read
B) Refactor and update callers
  ✅ One cleaner client class
  ✅ Kit tests still run to catch breaks
  ❌ Edits the frozen kit; demo redeploy needed
Net: zero-risk wrapping versus a tidier client that touches frozen code.
Header: LLM contract
Options:
A) Wrap, don't change (recommended)
shared/llm.py behaviour unchanged (chat, parse_json, NoKey/Upstream/BadOutput, env vars); optional keyword params only; prototype wrapper server/app/llm.py adds classes, backend 2, stub; CI runs `ROOM_LLM=stub pytest writing-room-kit/v04/tests writing-room-kit/web/tests` (29 tests) on every change. human: ~1h / CC: ~5 min.
B) Refactor and update callers
Turn shared/llm.py into a transport class; update kit llmx.py and web app; kit tests must pass.

State: approved
Actual answer: A) "Wrap, don't change (recommended)", D22 answer 2026-10-23
Accepted scope: shared/llm.py behaviour unchanged (chat, parse_json, NoKey/Upstream/BadOutput, env vars); optional keyword params only; wrapper server/app/llm.py adds classes, backend 2, stub; CI runs the kit + web tests (29) with ROOM_LLM=stub on every change.
History: none

## Section 4: Performance review

- **P-12** [P2] (confidence: 7/10) architecture.md:114 "target < 30 calls" per submission. 30 submissions near the deadline is about 900 LLM calls in a burst [estimated: 30 × 30]. Sequential, at about 3 s a call [estimated], that's around 45 minutes. There are no queue bounds, no fairness and no indexes.
- Replay at compile: bounded by checkpoints at most every 5 minutes of activity (event-log.md:99). No finding.
- Memory: one log is under 5 MB [ASSUMPTION, measure in S1] (event-log.md:100). No finding.
- N+1: chain assembly must load a log's events once, by `(log_id, seq)`. This is covered by the index in P-12.
- Parse: capped at 300 s and async (D4). No finding.

### P-12: bounded job queue and indexes
Finding: P-12, P2, 7/10, architecture.md:114 + :73, Claude (main)
Plan baseline: P-12 pending: bounded parallel L3 queue per assignment; indexes. D2: jobs are DB rows worked by one in-process loop. D3: SQLite.
Runtime evidence: none.
Comparison grid:
| Choice | Current | A | B |
|---|---|---|---|
| Job row | — | id, kind, idempotency key (unique), state, attempts, run_after, lease_until | same |
| LLM concurrency | unbounded | global semaphore 4 per backend; round-robin across submissions, earliest submit first | one job at a time |
| Retries | CEO-7 "retry with backoff" | backoff 1, 4, 16 min, then wait for the D7 cap | same |
| Restart | — | expired leases picked up again at boot | same |
| Indexes | none | events (log_id, seq) unique; receipts (log_id); blocks (source_id); roster (class_id, email) unique; jobs (state, run_after) | same |
| Load test | CEO-21: 30 submits in 5 min | stub LLM at 3 s latency: every L1 receipt < 60 s, every question set < 15 min | L1 < 60 s only |
Question D23:
D23 — How should receipt jobs run when the whole class submits at once?
Project/branch/task: main, eng review of the v1 plan set.
ELI10: At the deadline maybe 30 students submit within minutes, and each receipt needs up to ~30 AI calls. One at a time, the last student's questions arrive after about 45 minutes; all at once, we hit the provider's rate limits. The plan: a small queue in the database that runs 4 AI calls at a time per provider, takes students in submit order, survives a server restart, and is load-tested with a fake AI that takes 3 seconds per call.
Stakes if we pick wrong: Unbounded calls trip rate limits right at the deadline; sequential calls leave receipts waiting long after release.
Recommendation: A because it bounds both latency and rate-limit risk, and the load test proves it before the pilot.
Completeness: A=9/10, B=6/10
Pros / cons:
A) Bounded parallel queue (recommended)
  ✅ 4 calls at a time per provider: fast but under rate limits
  ✅ Survives restarts; load-tested at 30 submits in 5 minutes
  ❌ Lease and fairness logic (~half a day)
B) One job at a time
  ✅ Simplest possible loop
  ✅ Never hits rate limits
  ❌ Questions for the last submitter arrive ~45 min later
Net: half a day for timely questions at the busiest moment of the pilot.
Header: Job queue
Options:
A) Bounded parallel queue (recommended)
Job rows with idempotency key and lease; 4 concurrent calls per backend, round-robin by submission (earliest first); backoff 1/4/16 min then the D7 cap; leases resumed at boot; the listed indexes; load test with a 3 s stub: L1 < 60 s, questions < 15 min. human: ~1 day / CC: ~40 min.
B) One job at a time
Sequential loop; same indexes; load test asserts L1 < 60 s only.

State: approved
Actual answer: A) "Bounded parallel queue (recommended)", D23 answer 2026-10-23
Accepted scope: job rows with idempotency key + lease; 4 concurrent calls per backend, round-robin by submission (earliest first); backoff 1/4/16 min then D7 cap; leases resumed at boot; indexes events(log_id,seq) unique, receipts(log_id), blocks(source_id), roster(class_id,email) unique, jobs(state,run_after); load test 3 s stub: L1 < 60 s, questions < 15 min.
History: none

### P-14: fold the override boxes into the design docs
Finding: P-14, P2, 9/10, architecture.md:5-10 "These override the text below until /plan-eng-review folds them in", Claude (main)
Plan baseline: P-14 pending (CEO outside voice #3).
Runtime evidence: 7 design docs carry "Changed by /plan-ceo-review" boxes; architecture.md §1, §4 and §6 are stale after D1–D3.
Comparison grid:
| Choice | Current | A | B |
|---|---|---|---|
| CEO boxes | at the top of 7 docs | folded into the body text; boxes removed | kept |
| This review's decisions (D1–D23) | only in this record | written into the docs they change | added as a second box per doc |
| Doc status | "draft, for /plan-eng-review" | "reviewed (CEO + eng) 2026-10-23" in design/README | unchanged |
| When | — | at the end of this review | during M0 |
Question D24:
D24 — Fold every review decision into the design docs now?
Project/branch/task: main, eng review of the v1 plan set.
ELI10: Right now seven design docs have a box at the top saying 'this overrides the text below'. Anyone building from them (you or an agent) has to read the box and mentally patch the body, and this review adds 23 more decisions. Folding means rewriting the affected sections so the body itself is correct, removing the boxes, and marking the docs reviewed. Then M0 starts from docs that say exactly what to build.
Stakes if we pick wrong: Agents build from stale body text and miss a box: Postgres instead of SQLite, a polish band, URL fetching.
Recommendation: A because M0 starts tomorrow and builders should read one true version.
Completeness: A=10/10, B=6/10
Pros / cons:
A) Fold now (recommended)
  ✅ Each doc reads correctly top to bottom; no mental patching
  ✅ design/README statuses become 'reviewed'
  ❌ Large doc edit at the end of this session (~30 min of agent time)
B) Add boxes, fold during M0
  ✅ This session ends sooner
  ✅ Decisions still recorded here
  ❌ Two layers of boxes; easy for a builder to miss one
Net: one clean doc set before building versus a quicker end to this session.
Header: Fold docs
Options:
A) Fold now (recommended)
Rewrite the affected sections of architecture, event-log, provenance, receipt, reading-aid, coach-helper, privacy, evaluation and build-plan with CEO-1..24 and D1..D23; remove the boxes; design/README statuses "reviewed (CEO + eng) 2026-10-23"; prototype/README layout updated. human: ~3h / CC: ~30 min.
B) Add boxes, fold during M0
Add an "eng review" box to each affected doc; fold at the start of M0.

State: approved
Actual answer: A) "Fold now (recommended)", D24 answer 2026-10-23
Accepted scope: fold CEO-1..24 and D1..D23 into architecture, event-log, provenance, receipt, reading-aid, coach-helper, privacy, evaluation, build-plan; remove override boxes; design/README statuses "reviewed (CEO + eng) 2026-10-23"; prototype/README layout updated.
History: none

Section 3 dispositions: T1 accepted (D21), R1 accepted (D22). Test Plan Artifact: ~/.gstack/projects/CyrusnG0-Acader/micmic-main-eng-review-test-plan-20261023-164120.md.
Section 4 dispositions: P-12 accepted (D23). P-14 accepted (D24).

## Outside Voice (native fallback: Opus Plan subagent)

Codex was skipped at the founder's standing request ("not codex, just use another opus"). A native Plan subagent (inherited model: Opus 5.5) ran read-only, with the decisions passed inline and the files read directly, and completed inside the 5-minute timer. It runs in the same harness family, so this is **not cross-model coverage**.

| # | Sev | Finding | Disposition |
|---|---|---|---|
| 1 | Critical | Schedule not re-estimated after D1–D24 | V1 |
| 2 | High | Agents build the superseded design until D24 lands | Covered by D24 (fold this session) + precedence line in build-plan §5. No question |
| 3 | High | Replay mismatch found only after the seal | V4 |
| 4 | High | Coach answers / cards launder pasted text into "traced" | V2 |
| 5 | High | "Linked by student, not checked" has no band | V3 |
| 6 | Medium | Quote check too weak for short phrases | V5 |
| 7 | Medium | 5-min rounding still leaves an activity curve | V6 |
| 8 | Medium | LLM-derived lines aren't reproducible from the log | V7 |
| 9 | Medium | Offline queue vs lost lease | V8 |
| 10 | Medium | Goldens tied to the spike editor's schema | V9 |
| 11 | Low | Hosted parser is a processor | **Rejected (factual):** the parser runs in our own server process; no third party receives text. No change |
| 12 | Low | Deploy downtime on SQLite | V10 |

### V1: re-baseline the schedule after this review
Finding: OV-1, Critical, 8/10, build-plan.md:47-59, outside voice
Plan baseline: CEO-23 bottom-up (~20 build days; 11-05 = engine + receipt + walkthrough).
Runtime evidence: the D-records add roughly 9–10 human-days of named work, minus ~1.5 saved (D1, D3) [estimated from the D-record effort labels]. Some of it (D9–D11, D13, D15, D23) was already pending P-work in M4b/M5 and may already be in the 20 days [unknown].
Comparison grid:
| Choice | Current | A | B | C | D |
|---|---|---|---|---|---|
| build-plan §2 | ~20 days, pre-review | re-estimated bottom-up with D1–D24 while folding (D24); each milestone's added items listed; if 11-05 slips, the new date is stated and cuts proposed to you, not applied | unchanged | 1-hour estimate first, then choose | defer to the 10-30 checkpoint |
Question D25:
D25 — Re-estimate the schedule now that the review added work?
Project/branch/task: main, eng review of the v1 plan set.
ELI10: The outside reviewer is right that we added work (replay in Python, the edit lease, the job queue, security tests, monitoring) without touching the calendar. Some of it was already pending in the old plan, but nobody has added it up. Option A: while folding the docs, re-count each milestone bottom-up, show what moved, and if 11-05 slips, say the new date and propose cuts for you to approve. Nothing gets cut without your say.
Stakes if we pick wrong: You promise 11-05 to the researchers and the nursing teacher on a plan that is already 3–5 days over.
Recommendation: A because a re-count costs minutes and the 10-30 checkpoint needs an honest date.
Note: options differ in kind, not coverage — no completeness score.
Pros / cons:
A) Apply: re-baseline now
  ✅ Honest 11-05 meaning before outreach promises anything
  ✅ Cuts proposed to you, not applied silently
  ❌ May show 11-05 slipping, which is uncomfortable but true
B) Keep current plan
  ✅ No change to dates already shared
  ✅ Less doc churn today
  ❌ Plan known to be under-counted
C) Investigate first
  ✅ A quick estimate before committing to a rewrite
  ✅ Same information as A, less editing
  ❌ Another round trip for the same answer
D) Defer to 10-30
  ✅ Decide with the teacher answer in hand
  ✅ No work now
  ❌ A week of building against a wrong plan
Net: count now or find out late.
Header: Schedule
Options:
A) Apply: re-baseline now (recommended)
While folding (D24), re-estimate M0–M5 bottom-up including D1–D24; list added items per milestone; if 11-05 slips, state the new date and propose cuts for approval (none applied).
B) Keep current plan
build-plan §2 unchanged.
C) Investigate first
Produce a 1-page estimate only; decide afterwards.
D) Defer to 10-30
Revisit at the checkpoint.

State: approved
Actual answer: A) "Apply: re-baseline now (recommended)", D25 answer 2026-10-23
Accepted scope: while folding (D24), re-estimate M0–M5 bottom-up incl. D1–D28; list added items per milestone; if 11-05 slips, state the new date and propose cuts for founder approval (none applied).
History: none

### V2: origin tracking inside Coach answers and cards
Finding: OV-4, High, 8/10, event-log.md:57 `via: typed | coach_answer | import`, :70 `answer_text`; provenance.md:92 band 3, outside voice
Plan baseline: only the editor records origin; card/Coach text is trusted as the student's own; D5 checks that coach-marked text matches the recorded answer (it would pass).
Runtime evidence: none.
Comparison grid:
| Choice | Current | A | B | C | D |
|---|---|---|---|---|---|
| Card editor + Coach answer box | plain text | small origin-tracking inputs: pasted characters recorded as paste_ext in card.create / coach.outcome | as is | investigate | defer |
| Text moved from them into the draft | `coach` mark → band "Traced to Coach" | pasted parts carry `paste_ext` (via coach/card) → untraced, note "pasted into a Coach answer" / "pasted into a card" | traced | — | — |
| Golden session | none | "AI prose pasted into a Coach answer, then moved to the draft" | none | — | — |
Question D26:
D26 — Track pasting inside Coach answers and idea cards too?
Project/branch/task: main, eng review of the v1 plan set.
ELI10: Only the main editor records where each character came from. A student can paste AI text into the Coach answer box (or an idea card), then move it into the essay with one click, and the receipt calls it 'traced to a Coach exchange' or 'traced to a source'. That's a back door into the strongest bands. The fix: those small text boxes record pasted characters too, and pasted parts stay 'pasted' wherever they move, shown as untraced with a plain note.
Stakes if we pick wrong: Any student who figures this out gets 'traced' for outside text, and the receipt's main promise breaks.
Recommendation: A because it closes the easiest laundering path with the same marks we already built.
Note: options differ in kind, not coverage — no completeness score.
Pros / cons:
A) Apply: track paste in cards and answers
  ✅ Pasted text stays untraced wherever it goes
  ✅ Reuses origin marks; one golden session proves it
  ❌ Cards and answers need small editors instead of plain textareas (~half a day)
B) Keep current
  ✅ Simpler card and answer boxes
  ✅ No extra golden session
  ❌ Easy back door into "traced"
C) Investigate first
  ✅ Check how often students would paste into cards
  ✅ Might find a cheaper guard
  ❌ The hole exists regardless of frequency
D) Defer
  ✅ Ship sooner
  ✅ Could add before the pilot gate
  ❌ Goldens and receipts built meanwhile assume the hole
Net: half a day to close the easiest way around the receipt.
Header: Card paste
Options:
A) Apply: track paste (recommended)
Card editor and Coach answer box record pasted characters (paste_ext) in card.create / coach.outcome; moved text keeps paste_ext (via card/coach) → untraced with note; golden "AI prose via Coach answer". human: ~0.5 day / CC: ~25 min.
B) Keep current
Cards and answers trusted as the student's words.
C) Investigate first
Look for a cheaper guard before deciding.
D) Defer
Revisit before the pilot gate.

State: approved
Actual answer: A) "Apply: track paste (recommended)", D26 answer 2026-10-23
Accepted scope: card editor + Coach answer box record pasted characters (paste_ext) in card.create / coach.outcome; moved text keeps paste_ext (via card/coach) → untraced with note; golden "AI prose via Coach answer".
History: none

### V3: a band for student-made links
Finding: OV-5, High, 8/10, provenance.md:86-94 (no row) vs CEO-17; build-plan.md:58, :89, outside voice
Plan baseline: CEO-17 label only; band unspecified.
Runtime evidence: none.
Comparison grid:
| Choice | Current | A | B | C | D |
|---|---|---|---|---|---|
| Band for student-linked, unconfirmed sentences | unspecified | own band "Linked by student, not checked", its own segment in both bars, never merged into traced | counted as traced (with label) | investigate | defer |
| H stop rule metric (CEO-18) | "untraced" | untraced share, with student-linked reported next to it | untraced | — | — |
| Untraced-wall gate (CEO-24) | "untraced wall" | untraced share only; student-linked shown | same | — | — |
Question D27:
D27 — Give 'linked by student, not checked' its own band in the numbers?
Project/branch/task: main, eng review of the v1 plan set.
ELI10: You decided student-made links show as 'linked by student, not checked'. But the bars still need to know where those words go. Count them as traced and self-linking becomes a laundering trick; count them as untraced and an honest student who linked carefully looks like an untraced wall when the AI check is off. A separate band, shown on its own in both bars, says exactly what is true: the student says this is where it came from, and we didn't check.
Stakes if we pick wrong: Either self-links pass as traced, or honest careful students look like they have no trace.
Recommendation: A because it is the literal truth and keeps the stop rule and the gate measurable.
Note: options differ in kind, not coverage — no completeness score.
Pros / cons:
A) Apply: separate band
  ✅ Honest about what we know: student-asserted, unchecked
  ✅ Stop rule and wall gate measured on untraced, not muddied
  ❌ A sixth segment for the teacher to read
B) Count as traced
  ✅ Fewer bands; looks cleaner
  ✅ Careful honest students look traced
  ❌ Self-linking launders outside text
C) Investigate first
  ✅ Ask the nursing teacher how she'd read it
  ✅ Data from the walkthrough
  ❌ Engine and goldens need an answer in M1
D) Defer
  ✅ No change now
  ✅ Decide after S3
  ❌ M1 receipts built on an undefined rule
Net: an honest extra segment versus a cleaner bar that can be gamed.
Header: Link band
Options:
A) Apply: separate band (recommended)
Band "Linked by student, not checked" in both bars, never merged into traced; becomes traced only if L3b confirms; stop rule and untraced-wall gate use untraced share and report this band beside it. human: ~2h / CC: ~10 min.
B) Count as traced
Student-linked words count as traced with the label in the chain view.
C) Investigate first
Show both versions in the nursing walkthrough, then decide.
D) Defer
Leave unspecified for now.

State: approved
Actual answer: A) "Apply: separate band (recommended)", D27 answer 2026-10-23
Accepted scope: band "Linked by student, not checked" in both bars, never merged into traced; traced only if L3b confirms; stop rule + untraced-wall gate use untraced share and report this band beside it.
History: none

### V4: catch replay mismatches before the seal
Finding: OV-3, High, 7/10, D6 accepted scope ("replay must equal client doc_hash at each checkpoint, else compile error + alert"), outside voice
Plan baseline: D6 (replay at compile; mismatch → compile error + alert); CEO-7 (submit always seals; L1 receipt).
Runtime evidence: none.
Comparison grid:
| Choice | Current | A | B | C | D |
|---|---|---|---|---|---|
| When replay runs | at compile (after seal) | background job at every doc.checkpoint too | at compile only | investigate | defer |
| Mismatch before submit | — | operator alert; student unaffected | — | — | — |
| Mismatch at submit | compile error, no receipt | L1 receipt from the client snapshot, labelled "built from the browser's copy (replay mismatch)" + alert | no receipt | — | — |
Question D28:
D28 — Check the replay at every save point, with a fallback receipt?
Project/branch/task: main, eng review of the v1 plan set.
ELI10: D6 rebuilds the document in Python and compares it with what the browser has. If they disagree (a schema slip, an odd character), we'd only find out after the student submits, and then there's no receipt, which breaks 'submit always gets a receipt'. Option A: run the same check in the background at every save point, so you hear about it days earlier, and if it still fails at submit, build the basic receipt from the browser's copy with a clear label.
Stakes if we pick wrong: A replay bug silently blocks receipts for a whole class at the deadline.
Recommendation: A because it moves a fatal surprise to an early alert and keeps CEO-7's promise.
Note: options differ in kind, not coverage — no completeness score.
Pros / cons:
A) Apply: check early + fallback
  ✅ Replay bugs show up days before submit, as an alert
  ✅ Every submission still gets a receipt (CEO-7)
  ❌ Background jobs at each checkpoint; one more receipt label
B) Keep D6 as is
  ✅ Fewer jobs
  ✅ Simpler receipt states
  ❌ First sign of a mismatch is a missing receipt
C) Investigate first
  ✅ S1 parity may show mismatches never happen
  ✅ Less work if so
  ❌ S1 can't cover every real student document
D) Defer
  ✅ Revisit after S1
  ✅ No work now
  ❌ Risk stays unowned until then
Net: cheap early warning plus a safe fallback versus a rare but total failure.
Header: Replay check
Options:
A) Apply: early check + fallback (recommended)
Replay check as a job at every doc.checkpoint (mismatch → operator alert); at submit a mismatch yields an L1 receipt from the client snapshot labelled "built from the browser's copy (replay mismatch)" + alert. human: ~3h / CC: ~15 min.
B) Keep D6 as is
Replay at compile only; mismatch → compile error + alert.
C) Investigate first
Decide after S1 parity results.
D) Defer
Revisit later.

State: approved
Actual answer: A) "Apply: early check + fallback (recommended)", D28 answer 2026-10-23
Accepted scope: replay check job at every doc.checkpoint (mismatch → operator alert); at submit a mismatch yields an L1 receipt from the client snapshot labelled "built from the browser's copy (replay mismatch)" + alert.
History: none

### V5: stricter quote-mark check
Finding: OV-6, Medium, 7/10, D5 accepted scope ("marked text … inside its origin text"), outside voice
Plan baseline: D5 (substring of the origin text, whitespace-normalised).
Runtime evidence: none.
Comparison grid:
| Choice | Current | A | B | C | D |
|---|---|---|---|---|---|
| Quote run rule | substring anywhere in origin | each contiguous quote-marked run must match its own block_id's text (normalise whitespace and quote characters) and be ≥ 4 words or the whole block; otherwise untraced | D5 as is | investigate | defer |
| coach/import/helper runs | substring of origin | unchanged (each run inside its own referenced origin) | unchanged | — | — |
Question D29:
D29 — Make the quote check match the exact passage, with a minimum length?
Project/branch/task: main, eng review of the v1 plan set.
ELI10: D5 checks that text labelled 'quote' appears in the reading. But short or common phrases ('the results show that') appear in almost any reading, so a forged label on them would pass. Tighter rule: each quoted stretch must match the specific passage its label points to, and be at least four words long (or the whole passage).
Stakes if we pick wrong: Forged quote labels on short common phrases still count as traced.
Recommendation: A because it closes the gap in D5 with a few lines of code.
Note: options differ in kind, not coverage — no completeness score.
Pros / cons:
A) Apply: exact block + minimum length
  ✅ Forged short quotes fail the check
  ✅ Few lines in the same D5 function; table tests
  ❌ A genuine 1–3 word quote counts as untraced (rare, explained in chain view)
B) Keep D5 as is
  ✅ No change
  ✅ Short real quotes stay traced
  ❌ Common-phrase forgeries pass
C) Investigate first
  ✅ Measure quote lengths in human sessions
  ✅ Tune the minimum on data
  ❌ Goldens need a rule in M1
D) Defer
  ✅ No work now
  ✅ Revisit before the gate
  ❌ Weak check stays meanwhile
Net: a few lines to make the mark check mean what it says.
Header: Quote check
Options:
A) Apply: exact block + min length (recommended)
Each contiguous quote run must match its own block_id's text (whitespace + quote-char normalised) and be ≥ 4 words or the whole block; else untraced with chain note. human: ~1h / CC: ~5 min.
B) Keep D5 as is
Substring of the origin text.
C) Investigate first
Tune after human sessions.
D) Defer
Revisit before the pilot gate.

State: approved
Actual answer: A) "Apply: exact block + min length (recommended)", D29 answer 2026-10-23
Accepted scope: each contiguous quote run must match its own block_id's text (whitespace + quote-char normalised) and be ≥ 4 words or the whole block; else untraced with chain note.
History: none

### V6: no typing rhythm in the chain at all
Finding: OV-7, Medium, 6/10, D12 accepted scope; event-log.md:43 `seq` gap-free, :98 batches every ~2 s, outside voice
Plan baseline: D12 (batch ts rounded down to 5 min).
Runtime evidence: none. With D12, the number of batches per 5-minute bucket still shows how active the typing was.
Comparison grid:
| Choice | Current | A | B | C | D |
|---|---|---|---|---|---|
| What enters the hash chain | one editor.batch per ~2 s | client batches go to an unchained staging table (survives restarts, acked to the client); the server appends one merged editor.batch per 5-min window, and at checkpoint and submit | as D12, plus consent says "how much text changed in each 5-minute period" | investigate | defer |
| Client data safety | queue + ack | unchanged (ack on staging write) | unchanged | — | — |
| Seal | D8 | submit first flushes staging into the chain | unchanged | — | — |
Question D30:
D30 — Merge editor batches into one per 5 minutes before they enter the record?
Project/branch/task: main, eng review of the v1 plan set.
ELI10: Even with 5-minute timestamps (D12), the record still holds one entry per ~2 seconds of typing, so counting entries per 5 minutes shows how hard someone was typing. Option A: the server parks incoming edits in a holding table (safe across restarts) and writes one combined entry per 5 minutes into the sealed record. Option B: keep the entries and say plainly in the consent text that we keep how much text changed in each 5-minute period.
Stakes if we pick wrong: 'We record what changed, not how you typed' stays slightly untrue in a way a careful student or ethics board could point out.
Recommendation: A because it makes the privacy promise literally true for a few hours of work.
Note: options differ in kind, not coverage — no completeness score.
Pros / cons:
A) Apply: merge per 5 minutes
  ✅ The record holds no typing rhythm at all
  ✅ Client safety unchanged: edits are acked on arrival
  ❌ A staging table and a flush rule (~3h); seal must flush first
B) Disclose in consent instead
  ✅ No engineering change
  ✅ Honest about what is kept
  ❌ Consent gets a line that invites 'so you track my typing?'
C) Investigate first
  ✅ Ask the ethics office which they prefer
  ✅ May not matter to them
  ❌ Event schema should settle in M0
D) Defer
  ✅ No work now
  ✅ Change before the gate
  ❌ Golden logs built with the old shape
Net: a few hours to make the privacy line exactly true.
Header: Batch merge
Options:
A) Apply: merge per 5 min (recommended)
Client batches → unchained staging table (acked, restart-safe); server appends one merged editor.batch per 5-min window and at checkpoint/submit; submit flushes staging before the seal. Test: 10 min of typing → ≤ 3 chained editor.batch events. human: ~3h / CC: ~15 min.
B) Disclose in consent
Keep D12; consent says per-5-minute change volume is kept.
C) Investigate first
Ask the ethics office.
D) Defer
Revisit before the gate.

State: approved
Actual answer: A) "Apply: merge per 5 min (recommended)", D30 answer 2026-10-23
Accepted scope: client batches → unchained staging table (acked, restart-safe); server appends one merged editor.batch per 5-min window and at checkpoint/submit; submit flushes staging before seal; test: 10 min typing → ≤ 3 chained editor.batch events.
History: none

### V7: keep the AI outputs that shaped a receipt
Finding: OV-8, Medium, 8/10, event-log.md:17 "(b) every number and line on the receipt traces to events in the log"; D20 stub-only rebuild, outside voice
Plan baseline: OL-035 (b); D20 engine stamp.
Runtime evidence: none. L3 outputs (claim compare, questions) aren't events.
Comparison grid:
| Choice | Current | A | B | C | D |
|---|---|---|---|---|---|
| L3 outputs | discarded | stored as compile artifacts (task, prompt hash, response body, response hash), same access rules as the log; receipt.json lines cite artifact ids as well as event ids | discarded; D20 stub rebuild only | investigate | defer |
| Rebuild | stubs only | live receipts rebuildable by reusing stored outputs; verify checks artifact hashes | stubs only | — | — |
| "Provable" (b) wording | every line traces to events | every line traces to events, or to a stored AI output labelled as such | unchanged (overclaims) | — | — |
Question D31:
D31 — Store the AI outputs behind each receipt so it can be rebuilt and checked?
Project/branch/task: main, eng review of the v1 plan set.
ELI10: We promise 'every line on the receipt traces to the record'. That's true for facts, but the questions and any AI-checked bands come from AI answers that are thrown away after use. Rerun the AI and you might get a different answer, so an old receipt can't be checked. Option A: keep each AI answer (with a fingerprint) alongside the record, and have receipt lines point to it. Then any receipt can be rebuilt exactly and our 'provable' wording stays true.
Stakes if we pick wrong: Our 'every line traces to the record' claim is false for the most important lines, the questions.
Recommendation: A because it keeps the provability promise honest at the cost of a small table.
Note: options differ in kind, not coverage — no completeness score.
Pros / cons:
A) Apply: store AI outputs
  ✅ Any live receipt can be rebuilt and verified exactly
  ✅ Wording of 'provable' (b) stays true
  ❌ Stores AI outputs about student text: same retention and export as the log
B) Keep as is
  ✅ Less data stored
  ✅ No new table
  ❌ The provability claim overreaches for AI-derived lines
C) Investigate first
  ✅ Check retention rules with the school
  ✅ Might shape what's kept
  ❌ Receipt schema should settle in M1
D) Defer
  ✅ No work now
  ✅ Add before the gate
  ❌ Early receipts can't be rebuilt
Net: a small table versus an overclaim on the most-read lines.
Header: AI outputs
Options:
A) Apply: store AI outputs (recommended)
Each L3 call stored as a compile artifact (task, prompt hash, response body, hash) under log access rules and included in export/delete; receipt lines cite artifact ids; rebuild reuses them; verify checks hashes; event-log §1 (b) reworded. human: ~3h / CC: ~15 min.
B) Keep as is
Discard L3 outputs; D20 stub rebuild only.
C) Investigate first
Check with the school's retention rules.
D) Defer
Revisit before the gate.

State: approved
Actual answer: A) "Apply: store AI outputs (recommended)", D31 answer 2026-10-23
Accepted scope: each L3 call stored as compile artifact (task, prompt hash, response body, hash) under log access rules, in export/delete; receipt lines cite artifact ids; rebuild reuses them; verify checks hashes; event-log §1 (b) reworded.
History: none

### V8: offline edits after losing the edit lease
Finding: OV-9, Medium, 7/10, event-log.md:101 "the client rebases"; D10 lease, outside voice
Plan baseline: D10 (lease 30 s heartbeat / 90 s expiry; second tab read-only with takeover).
Runtime evidence: none.
Comparison grid:
| Choice | Current | A | B | C | D |
|---|---|---|---|---|---|
| Device reconnects after another took over | "client rebases" (undefined) | stale queue never applied; the student sees the unsent text with "Save as a file" or "Bring it in through the Door" (declared) | client rebases its queue onto the new head | investigate | defer |
| Test | none | E2E: offline tab A, takeover in tab B, A reconnects | E2E for rebase | — | — |
Question D32:
D32 — What happens to offline edits when another device took over?
Project/branch/task: main, eng review of the v1 plan set.
ELI10: With the edit lease (D10), only one device edits. But a laptop can go offline, keep typing (edits wait on the device), lose its lease, and meanwhile the student continues on a library PC. When the laptop reconnects, its waiting edits no longer fit the document. Option A: never merge them automatically; show the student the unsent text and let them save it as a file or bring it in through the Door. Nothing is lost and the record stays clean.
Stakes if we pick wrong: Automatic merging can scramble the document or mislabel where text came from.
Recommendation: A because it never loses words and never guesses a merge.
Note: options differ in kind, not coverage — no completeness score.
Pros / cons:
A) Apply: no merge, offer save or Door
  ✅ No lost words, no scrambled document
  ✅ Brought-in text is declared, so the record stays honest
  ❌ The student copies a few lines back by hand
B) Automatic rebase
  ✅ Seamless when the edits don't overlap
  ✅ No extra step for the student
  ❌ Overlapping edits can scramble text and marks
C) Investigate first
  ✅ See how often it happens in human sessions
  ✅ Maybe never in practice
  ❌ When it happens, words are at risk
D) Defer
  ✅ No work now
  ✅ Revisit before the gate
  ❌ Undefined behaviour in the offline path
Net: a small manual step versus a risky auto-merge.
Header: Stale queue
Options:
A) Apply: no merge, save or Door (recommended)
On reconnect after takeover the stale queue isn't applied; the student sees the unsent text with "Save as a file" or "Bring it in through the Door"; E2E: offline A, takeover B, A reconnects. human: ~2h / CC: ~10 min.
B) Automatic rebase
Rebase the stale queue onto the new head.
C) Investigate first
Measure in human sessions.
D) Defer
Revisit before the gate.

State: approved
Actual answer: A) "Apply: no merge, save or Door (recommended)", D32 answer 2026-10-23
Accepted scope: on reconnect after takeover the stale queue isn't applied; student sees unsent text with "Save as a file" / "Bring it in through the Door"; E2E offline A, takeover B, A reconnects.
History: none

### V9: golden sessions follow the real schema
Finding: OV-10, Medium, 7/10, build-plan.md:51 "frozen after S1"; D19, outside voice
Plan baseline: D19 (Playwright drives the S1 page, later the M3 editor; outputs frozen).
Runtime evidence: none.
Comparison grid:
| Choice | Current | A | B | C | D |
|---|---|---|---|---|---|
| Schema | S1 page's own | one schema JSON (`web/schema.json`) shared by the S1 page, the M3 editor and the Python replay (D6) from day one | as is | investigate | defer |
| Golden logs | frozen after S1 | regenerated in CI from the YAML scripts whenever schema or editor code changes; expected receipts stay frozen and are the assertion | frozen | — | — |
Question D33:
D33 — Keep golden sessions in step with the real editor?
Project/branch/task: main, eng review of the v1 plan set.
ELI10: Golden sessions are recorded from the S1 test editor. The real editor arrives later (M3) with claim links and new input rules. If the two editors' schemas differ, the recorded logs go stale and stop testing what students will use. Fix: one schema file shared by the test editor, the real editor and the Python replay from day one, and re-record the logs automatically whenever the editor changes, while the expected receipts stay fixed as the thing being checked.
Stakes if we pick wrong: Golden tests keep passing on logs no real student editor would produce.
Recommendation: A because the expected receipts are the spec and the logs should always come from the current editor.
Note: options differ in kind, not coverage — no completeness score.
Pros / cons:
A) Apply: shared schema + regenerate in CI
  ✅ Golden logs always match the editor students use
  ✅ One schema file for JS and Python (helps D6 parity)
  ❌ CI runs Playwright (a few minutes per run)
B) Keep frozen logs
  ✅ Fast CI
  ✅ Logs never change unexpectedly
  ❌ Stale after M3; tests stop meaning anything
C) Investigate first
  ✅ See how much the schema actually changes
  ✅ Maybe little
  ❌ D17 and D21 already change it
D) Defer
  ✅ No work now
  ✅ Revisit at M3
  ❌ 11-05 receipts rest on spike logs
Net: a few CI minutes to keep the executable spec honest.
Header: Golden sync
Options:
A) Apply: shared schema + CI regen (recommended)
`web/schema.json` used by S1 page, M3 editor and prosemirror-py; CI regenerates golden logs from YAML scripts on schema/editor changes; expected receipts frozen as assertions. human: ~3h / CC: ~15 min.
B) Keep frozen logs
As D19.
C) Investigate first
Measure schema churn after S1.
D) Defer
Revisit at M3.

State: approved
Actual answer: A) "Apply: shared schema + CI regen (recommended)", D33 answer 2026-10-23
Accepted scope: web/schema.json shared by S1 page, M3 editor and prosemirror-py; CI regenerates golden logs from YAML scripts on schema/editor changes; expected receipts frozen as assertions.
History: none

### V10: deploys during the assignment window
Finding: OV-12, Low, 7/10, D3 (one SQLite machine), outside voice
Plan baseline: D3; D10 submit guards.
Runtime evidence: none.
Comparison grid:
| Choice | Current | A | B | C | D |
|---|---|---|---|---|---|
| Deploys in the window | allowed | frozen from window open to release of the last receipt, except fixes announced to the teacher | allowed | investigate | defer |
| Submit during a restart | fails | client retries submit with backoff (same idempotency key, D10) until acked; "Submitting…" shown | fails | — | — |
Question D34:
D34 — Freeze deploys during the assignment, and make submit retry?
Project/branch/task: main, eng review of the v1 plan set.
ELI10: With one database machine (D3), each deploy restarts the server for a few seconds. Typing is safe because edits wait on the device, but a Submit click during that moment would fail. Two cheap fixes: don't deploy while the class is writing (except urgent fixes you tell the teacher about), and make Submit quietly retry until the server is back.
Stakes if we pick wrong: A student clicks Submit at 11:59 during a deploy and sees an error at the deadline.
Recommendation: A because both parts are nearly free and remove a deadline-night failure.
Note: options differ in kind, not coverage — no completeness score.
Pros / cons:
A) Apply: freeze + retrying submit
  ✅ No deploy surprises during the window
  ✅ Submit survives a restart; idempotency prevents doubles
  ❌ Non-urgent fixes wait until after the window
B) Keep as is
  ✅ Deploy any time
  ✅ No retry code
  ❌ Submit can fail at the deadline
C) Investigate first
  ✅ Measure restart time on the host
  ✅ Might be sub-second
  ❌ The retry is cheap either way
D) Defer
  ✅ No work now
  ✅ Add at M5
  ❌ Easy to forget before the window
Net: two near-free habits against a deadline-night error.
Header: Deploy freeze
Options:
A) Apply: freeze + retry (recommended)
No deploys from window open to last release except announced fixes (runbook line); client retries submit with backoff and the same idempotency key until acked, showing "Submitting…". human: ~1h / CC: ~5 min.
B) Keep as is
Deploy any time; submit may fail during a restart.
C) Investigate first
Measure restart time first.
D) Defer
Add at M5.

State: approved
Actual answer: A) "Apply: freeze + retry (recommended)", D34 answer 2026-10-23
Accepted scope: no deploys from window open to last release except announced fixes (runbook line); client retries submit with backoff + same idempotency key until acked, showing "Submitting…".
History: none

## TODOS.md proposals

### TD1: move to Postgres when the pilot grows
Finding: from D3 upgrade trigger, Claude (main)
Plan baseline: D3 (SQLite everywhere; upgrade when >1 class or >1 app machine). L2 already approved for TODOS by D1 (no question).
Runtime evidence: none.
Comparison grid:
| Choice | Current | A | B | C |
|---|---|---|---|---|
| TODOS entry | none | add "Move to Postgres" with trigger, steps (same schema via SQLAlchemy, append rule = unique + retry, job locking via SKIP LOCKED, backups) | skip | build now |
Question D35:
D35 — Add 'move to Postgres when the pilot grows' to TODOS?
Project/branch/task: main, eng review of the v1 plan set.
ELI10: We chose SQLite for one class on one machine. When a second class or a second server arrives, we'll need Postgres. Writing that down now, with the trigger and the three things that change (the append rule, job locking, backups), means future-you or an agent knows exactly when and how to switch.
Stakes if we pick wrong: Growth arrives and nobody remembers that SQLite was a deliberate one-class choice.
Recommendation: A because a TODO with a trigger is free and prevents a surprise later.
Note: options differ in kind, not coverage — no completeness score.
Pros / cons:
A) Add to TODOS.md
  ✅ Trigger and steps recorded where the next agent looks
  ✅ Costs nothing now
  ❌ One more TODO to keep current
B) Skip
  ✅ Shorter TODO list
  ✅ The decision is in this record anyway
  ❌ Easy to miss when the second class arrives
C) Build it now
  ✅ Ready for more classes on day one
  ✅ No later migration
  ❌ Reverses D3; extra work before the pilot
Net: write down the exit now, build it when it's needed.
Header: Postgres TODO
Options:
A) Add to TODOS.md (recommended)
TODO "Move to Postgres" — trigger: >1 class or >1 app machine; steps: same SQLAlchemy schema, append = unique + retry, jobs via SKIP LOCKED, managed backups, name the DB host in consent.
B) Skip
No TODO entry.
C) Build it now
Reverse D3 and use Postgres from the start.

State: approved
Actual answer: A) "Add to TODOS.md (recommended)", D35 answer 2026-10-23
Accepted scope: TODOS entry "Move to Postgres": trigger >1 class or >1 app machine; same SQLAlchemy schema, append = unique + retry, jobs via SKIP LOCKED, managed backups, DB host named in consent.
History: none

Outside-voice dispositions: V1 accepted (D25), V2 (D26), V3 (D27), V4 (D28), V5 (D29), V6 (D30), V7 (D31), V8 (D32), V9 (D33), V10 (D34); #2 covered by D24; #11 rejected (factual). No remaining disagreement.
TODO dispositions: L2 → TODOS (D1, prior approval); TD1 Postgres → TODOS (D35).

**Approval readiness: PASS.** Every accepted remedy cites its own answer:
- Scope: D1, D2
- Decisions: SC2/D3, P-7/D4, A1/D5, A2/D6, A3/D7, A4/D8, P-9/D9, P-10/D10, P-11/D11, A5/D12, P-6/D13, P-17/D14, P-8/D15, A6/D16, Q1/D17, P-13/D18, P-16/D19, Q2/D20, T1/D21, R1/D22, P-12/D23, P-14/D24
- Outside voice: V1–V10/D25–D34
- TODO: TD1/D35

P-15 (deletion between submit and release) stays with /plan-design-review, as the CEO review set. It was not decided here.

## Accepted changes applied this session

- **Design docs:** all nine rewritten with CEO-1..24 and D1..D35 (D24); override boxes removed; design/README statuses "reviewed (CEO + eng)".
- **Build plan:** re-baselined to about 28 build days; engine + receipt + walkthrough about 11-08; options in §2a, not applied (D25).
- **TODOS.md:** L2 embeddings (D1) and "Move to Postgres" (D35) added.
- **READMEs:** kit marked frozen (D18); prototype/README layout and rules (D2, D22).
- **Repo docs:** PRODUCT §7 and CLAUDE.md §5/§7 updated. DECISIONS D-034. OPEN_LOOPS: OL-008, OL-031, OL-038 closed. STATUS, UPDATE_LOG and CHANGELOG updated.

## NOT in scope
- L2 embeddings: deferred to TODOS (D1). Trigger: more than ~30 claim nodes per essay.
- Postgres: deferred to TODOS (D35). Trigger: more than one class or app machine.
- Everything the CEO review deferred: scholarly search, LLM pins, Coach A/D/E, graph view, polish band, policy dial, receipt PDF, Blackboard LTI, more classes.
- P-15 (wording when a student deletes between submit and release): /plan-design-review.
- OL-043 (what else estimates AI involvement): founder research, not an engineering choice.

## What already exists
- `shared/llm.py`: the DeepSeek transport. Reused unchanged and wrapped (D22). Its OpenAI-compatible format also carries backend 2 (D14).
- `writing-room-kit/v04/policies/*.md` and the law-1 judge prompt in `audit.py`: ported as prompts (D18).
- `writing-room-kit/v04/room.py`, `audit.py` and `coach.py` code: not reused. It is bound to the fictional corpus (room.py:20-22).
- `writing-room-kit/v04/llmx.py` stub pattern (`ROOM_LLM=stub`): the model for the prototype's stub backend.
- Kit + web tests (29, passing): kept in CI as the regression guard.
- prosemirror-py (PyPI `prosemirror`): reused for server replay (D6), [Layer 1].

## Failure modes (new paths)
| Path | Realistic failure | Handling | Test | User sees |
|---|---|---|---|---|
| Mark check | forged quote/coach mark | untraced + chain note | golden forged-mark session | "origin mark didn't match its source" |
| Card / Coach answer | pasted AI prose moved to the draft | paste_ext kept → untraced | golden session | "pasted into a Coach answer" |
| Replay | JS/Python schema drift | checkpoint job alert; labelled fallback receipt | unit + S1 parity | "built from the browser's copy" |
| Staging merge | crash between ack and append | staging is restart-safe; flushed at boot and at submit | unit | nothing |
| Seal | edit after submit | 409 unless resubmission open | S5 + unit | "Submitted. Ask your teacher to reopen." |
| Release | AI down past the cap | L1 released, "questions pending", alert | frozen-clock integration | "questions pending" |
| Job queue | deadline burst / restart | 4 per backend, leases resumed at boot | load test | questions within 15 min |
| Lease | offline device after takeover | stale queue not applied; save or Door | E2E | unsent text with two choices |
| Magic link | mail scanner pre-opens the link | GET shows a page only | integration | normal sign-in |
| Routes | guessed ID | repo layer → 404 | route enumeration | 404 |
| LLM | bad key | boot ping marks backend down + alert | fake-transport unit | "AI help unavailable" |
| Parse | scanned PDF / oversized | status scan / limit message | integration | teacher-facing status |
| Deploy | restart during submit | freeze rule + submit retry | E2E across restart | "Submitting…" then sealed |

**Critical gaps (no test, no handling, silent): 0.**

## Worktree parallelization strategy

| Step | Modules touched | Depends on |
|---|---|---|
| Scaffold + CI + schema.json | prototype/, web/ | — |
| LLM wrapper | server/app/llm | scaffold |
| S1 spike + replay parity | web/editor, server/engine/replay | schema.json |
| S2 parse spike | server/sources | scaffold |
| Engine: events/seal/verify + staging | server/engine/events, server/app | scaffold |
| Golden generator | fixtures/, web/ (Playwright) | S1, engine events |
| Provenance + receipt | server/engine/provenance, receipt | engine events, replay |
| Coach/leak port | server/coach | LLM wrapper |

- **Lane A:** schema.json → S1 + replay → golden generator.
- **Lane B:** LLM wrapper → coach/leak port.
- **Lane C:** S2 parse spike.
- **Lane D:** engine events/seal/verify → provenance + receipt (after Lane A's replay).

**Execution order:** run the scaffold first. Then launch A, B and C in parallel, and D once the scaffold is in. Merge A before D's provenance step. **Conflict flags:** `web/schema.json` is shared by A and D, so it changes only in Lane A.

## Implementation Tasks
Synthesized from this review's findings. Effort assumptions: features ~30x, tests ~50x, architecture ~5x.

- [ ] **T1 (P1, human: ~1d / CC: ~45min)** — engine/replay — prosemirror-py replay on shared schema.json + checkpoint replay job + labelled fallback
  - Surfaced by: Section 1 A2 (D6), outside voice #3 (D28), #10 (D33)
  - Files: prototype/server/engine/replay/, prototype/web/schema.json
  - Verify: S1 parity on all cases; mismatch fixture → fallback receipt
- [ ] **T2 (P1, human: ~4h / CC: ~15min)** — engine/provenance — mark check (per-block quotes ≥ 4 words; coach typed-parts only)
  - Surfaced by: A1 (D5), outside voice #6 (D29), #4 (D26)
  - Files: prototype/server/engine/provenance/
  - Verify: golden forged-mark + Coach-paste sessions
- [ ] **T3 (P1, human: ~3h / CC: ~15min)** — engine/events — seal = submit event, post-seal whitelist, staging + 5-min merge, ts rounding
  - Surfaced by: A4 (D8), A5 (D12), outside voice #7 (D30)
  - Files: prototype/server/engine/events/, prototype/server/app/
  - Verify: S5 post-seal case; 10 min typing → ≤ 3 chained batches
- [ ] **T4 (P1, human: ~0.5d / CC: ~25min)** — web — claim marks + input plugin + paste-tracked cards/answers
  - Surfaced by: Q1 (D17), T1 (D21), outside voice #4 (D26)
  - Files: prototype/web/editor/, prototype/web/map/, prototype/web/coach/
  - Verify: widened S1 cases; golden "edit above linked sentence"
- [ ] **T5 (P1, human: ~2h / CC: ~10min)** — engine/provenance — "linked by student, not checked" band in bars and stop-rule metric
  - Surfaced by: outside voice #5 (D27)
  - Files: prototype/server/engine/provenance/, receipt/
  - Verify: band table row tests; golden CEO-17 session
- [ ] **T6 (P1, human: ~1d / CC: ~45min)** — app — edit lease, stale-queue rule, submit guards + retry
  - Surfaced by: P-10 (D10), outside voice #9 (D32), #12 (D34)
  - Files: prototype/server/app/, prototype/web/editor/
  - Verify: Playwright two tabs, offline takeover, submit across restart
- [ ] **T7 (P1, human: ~1d / CC: ~40min)** — app — repo layer + route enumeration + CSP + teacher audit; scanner-safe magic link
  - Surfaced by: P-9 (D9), P-11 (D11)
  - Files: prototype/server/app/
  - Verify: route-enumeration test; GET doesn't consume token
- [ ] **T8 (P1, human: ~0.5d / CC: ~25min)** — app/llm — wrapper with 5 error classes, boot ping, backend-2 slot; kit tests in CI
  - Surfaced by: P-6 (D13), P-17 (D14), R1 (D22)
  - Files: prototype/server/app/llm.py, CI config
  - Verify: fake-transport tests; 29 kit tests green
- [ ] **T9 (P1, human: ~1d / CC: ~40min)** — app/jobs — bounded queue with leases, backoff, release cap
  - Surfaced by: P-12 (D23), A3 (D7)
  - Files: prototype/server/app/
  - Verify: load test 30 submits / 5 min; frozen-clock cap test
- [ ] **T10 (P1, human: ~1d / CC: ~45min)** — fixtures — YAML golden scripts + Playwright generator + ingest builder, regenerated in CI
  - Surfaced by: P-16 (D19), outside voice #10 (D33)
  - Files: prototype/fixtures/, CI config
  - Verify: 10 golden receipts match frozen expectations
- [ ] **T11 (P2, human: ~3h / CC: ~15min)** — engine/receipt — engine stamp + stored AI outputs + byte-identical rebuild
  - Surfaced by: Q2 (D20), outside voice #8 (D31)
  - Files: prototype/server/engine/receipt/
  - Verify: rebuild test
- [ ] **T12 (P2, human: ~1d / CC: ~40min)** — sources — hosted parse with caps, status, immutability
  - Surfaced by: P-7 (D4)
  - Files: prototype/server/sources/
  - Verify: scanned PDF, oversized, re-upload tests
- [ ] **T13 (P2, human: ~1d / CC: ~30min)** — ops — logs, counters, alerts, runbooks, deploy-freeze line
  - Surfaced by: P-8 (D15), outside voice #12 (D34)
  - Files: prototype/server/app/, docs/runbooks/
  - Verify: alert drill; smoke test reads counters
- [ ] **T14 (P2, human: ~0.5d / CC: ~25min)** — coach — port prompts, one leak.py, freeze kit
  - Surfaced by: P-13 (D18)
  - Files: prototype/server/coach/
  - Verify: leak-audit tests import coach/leak.py
- [ ] **T15 (P1, human: ~15min / CC: n/a)** — plan — founder picks a build-plan §2a option before M0
  - Surfaced by: outside voice #1 (D25)
  - Files: design/build-plan.md
  - Verify: choice recorded in UPDATE_LOG

## Unresolved decisions
None in this review.
- P-15 belongs to /plan-design-review.
- OL-043 is founder research.
- The §2a schedule options (T15) are a founder choice outside this review's approvals.

## Reality rows
```
REALITY: premise-table pass unverified=2 (DeepSeek has no embeddings API [unverified]; Docling size [unverified]); both non-blocking after D1/D4 docs/designs/eng-review-v1.md:38
REALITY: already-done pass remote has no refs; prototype/ holds only a README prototype/README.md:3
REALITY: surface-check pass ROOM_LLM=stub verified in llmx.py; pytest command ran (29 passed) writing-room-kit/v04/llmx.py:13
REALITY: binding-decisions pass CEO-1..24 honoured; CEO-21 reopened openly for a concrete risk (D7) docs/designs/ceo-review-v1.md:114
REALITY: numbers finding ~28 build days and 900-call burst are [estimated]; 29 tests [measured: pytest run 2026-10-23] design/build-plan.md:62
REALITY: deferred-asks pass no linked issue; CEO pending P-6..P-17 all decided except P-15 (routed to design review) docs/designs/ceo-review-v1.md:693
REALITY: pr-count pass no .gstack/ship-policy.json; default one PR per wave; docs-only change today design/build-plan.md:1
```

## Completion summary
- Step 0: Scope Challenge — scope reduced per recommendation (L2 deferred); smaller arrangement chosen
- Reality rows: 7/7 applicable rows emitted, 2 unverified premises (non-blocking)
- Architecture Review: 12 issues found
- Code Quality Review: 4 issues found
- Test Review: diagram produced, 2 gaps identified (T1, R1); 48 proposed paths mapped to approved decisions
- Performance Review: 1 issue found
- NOT in scope: written
- What already exists: written
- TODOS.md updates: 2 items (L2 from D1 prior approval; Postgres D35)
- Failure modes: 0 critical gaps flagged
- Unresolved decisions: 0 in this review
- Outside voice: native Plan subagent (Opus, same harness), completed; Codex skipped at the founder's request (not cross-model)
- Parallelization: 4 lanes, 3 parallel / 1 sequential
- Lake Score: 32/32 (every answer scored for completeness picked the 10/10 or complete option; D4 was a kind choice with no score)

## Suppressed findings (appendix)
- [P3] (confidence: 4/10) canonical JSON across languages: only Python verifies today, so there's no cross-language risk until a JS verifier exists.
- [P3] (confidence: 4/10) Fly.io HK region availability: unverified; it belongs to the consent/hosting choice (OL-037), not this review.

## GSTACK REVIEW REPORT

| Review | Trigger | Why | Runs | Status | Findings |
|--------|---------|-----|------|--------|----------|
| CEO Review | `/plan-ceo-review` | Scope & strategy | 3 | CLEAR (2026-10-22, SCOPE_REDUCTION) | mode: SCOPE_REDUCTION, 0 critical gaps |
| Outside Review | codex skipped (founder's request) → native Opus Plan subagent | Independent 2nd opinion | 7 | unavailable (codex); native completed | 12 findings: 10 accepted (D25–D34), 1 covered by D24, 1 rejected (factual) |
| Eng Review | `/plan-eng-review` | Architecture & tests (required) | 2 | ISSUES OPEN (all decided) | 19 issues, 0 critical gaps |
| Design Review | `/plan-design-review` | UI/UX gaps | 0 | — | — |
| DX Review | `/plan-devex-review` | Developer experience gaps | 0 | — | — |

- **OUTSIDE COVERAGE:** codex, plan-review phase: not run (founder asked for Opus instead; earlier runs AUTH_FAILED). The native Plan subagent (Opus 5.5, same harness) completed with 12 findings. This is not external coverage.
- **CROSS-MODEL:** not applicable; no completed external review.
- **VERDICT:** CEO CLEARED. Eng review complete with every finding decided; it is logged as issues_open because findings were found (status rule), so eng review is required again before clearing. The planned work is ready to implement once the founder picks a build-plan §2a option.

NO UNRESOLVED DECISIONS
