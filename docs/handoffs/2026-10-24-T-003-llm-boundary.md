# T-003: LLM boundary `complete()` + Python lock file

- **Lead:** lead-opus-T003   **Workers used:** none (the error mapping and schemas needed judgment, so the lead wrote them)
- **Branch or worktree:** `task/T-003-llm-boundary`   **Commit(s):** see `git log main..task/T-003-llm-boundary` (one commit)

## What changed
- `prototype/server/app/llm.py`: new. `complete(task, messages, schema=None, *, backend=None, max_tokens=900) -> dict`.
  - `Task` enum: `claim_extract`, `claim_compare`, `contradiction`, `coach_question`, `receipt_question`, `limitation_tag`, `leak_check`, `map_suggest`. A task outside the enum raises `UnknownTask` (a `ValueError`).
  - One pydantic output schema per task in `TASK_SCHEMAS` (all `extra="forbid"`), and one fixture per task in `STUB_FIXTURES`. `schema` defaults to the task's registered schema; a caller may pass its own. Output is validated, then returned as `model_dump()`.
  - `map_suggest` output is links only: `{links: [{claim_id, paragraph_id, start, end}]}`. No prose field is allowed, and the span must be non-empty. The checks that the claim_id exists and the span lies inside the changed paragraphs need the log, so they belong to the mapper job (M4m), not here.
  - `ROOM_LLM=stub`: returns the task's fixture, validated against the schema like live output. No network, no key, and the same output whatever the messages.
  - Errors (D13): `LLMTimeout`, `LLMRateLimited`, `LLMAuth`, `LLMRefusal`, `LLMSchema`, all subclasses of `LLMError`. Mapping: missing key or 401/402/403 → Auth; 429 → RateLimited; network errors, 408 and 5xx → Timeout; empty output or other 4xx → Refusal; non-JSON, bad response shape or a schema mismatch → Schema. Error messages carry no prompt text, output or key.
  - Backend `deepseek`: calls `shared.llm.chat(..., json_mode=True)` and `shared.llm.parse_json` and maps `NoKey/Upstream/BadOutput` onto the five classes. `shared/llm.py` is unchanged (D22).
  - Backend `openai_compat` (D14): base URL, model, key and auth header name come from `ROOM_LLM2_*` env vars. An `Authorization` header is sent as `Bearer <key>`; any other header name, such as Azure's `api-key`, is sent as the raw key. It takes full message lists. `ROOM_LLM_BACKEND` picks the default backend.
  - Boot ping: `ping_backends()` makes one 5-token call per configured backend (deepseek always; backend 2 when `ROOM_LLM2_BASE_URL` is set). It never raises; it returns `PingResult(backend, ok, error_kind)` and logs a warning when a backend fails.
- `prototype/server/app/main.py`: a FastAPI lifespan runs the boot ping and stores the results in `app.state.llm_ping`. A failing ping does not stop the app, because writing has to continue when AI help is down (ceo-review-v1 §2: "AI help unavailable; writing continues").
- `prototype/server/tests/test_llm.py`: new, 50 tests. No live calls: a fake transport replaces `httpx.post`, the key is a dummy env value, and `shared.llm.ROOT_ENV` is pointed at an empty temp path so `.env` is never read.
- `prototype/requirements.lock`: new. Made with uv (`--universal --python-version 3.12 --generate-hashes`) from `pyproject.toml` plus the `dev` extra. Every package is pinned with hashes.
- `prototype/requirements.txt`: deleted. The lock replaces it, so there is one source of truth.
- `.github/workflows/ci.yml`: now runs `pip install --require-hashes -r prototype/requirements.lock`.
- `prototype/README.md`: the Run line now installs from the lock. New "Dependencies (D-040)" section with the regenerate command, and a short "LLM boundary" section listing the env vars.
- `prototype/pyproject.toml`: the pytest `pythonpath` now also includes `..`, so tests can import `shared.llm`.
- `docs/TASKS.md`: T-003 Owner set, status `in progress`, then `review`.

## Tests run
- `cd prototype && ROOM_LLM=stub python3 -m pytest -q` → `119 passed` (50 new boundary tests; the rest are T-001/T-002/T-005, after rebasing onto `main` at `942aeb6`)
- `cd writing-room-kit && ROOM_LLM=stub python3 -m pytest -q v04/tests web/tests` → `29 passed`
- I installed the lock into a fresh venv with `pip install --require-hashes -r prototype/requirements.lock`. In that venv the prototype gave `119 passed` and the kit gave `29 passed`, so the lock covers the kit's needs too.
- `git diff main -- shared/` → empty.
- I checked that the tests fail when the behaviour breaks. Each change below was made temporarily and then reverted:
  - 429 no longer mapped → 3 failed
  - `extra="forbid"` loosened → 1 failed
  - unknown task silently accepted → 4 failed
  - empty output mapped to Schema → 1 failed
  - backend 2 left out of the ping → 1 failed
  - empty span allowed → 1 failed
- `ci.yml` parses as YAML.
- I grepped the changed files for the banned words in EXPECTATIONS A: no hits.
- Local runs used Python 3.14. CI uses 3.12, and the lock was resolved for 3.12.

## EXPECTATIONS sections claimed
- **A**: all lines. The design/README line does not apply because no design doc changed.
- **I-M0**: the "`complete()` with stub, error classes, boot ping, backend-2 slot" part.
- **F**: none. This task only adds the `map_suggest` task, its links-only schema and its fixture. The F lines (flag, payload, caps, cancel, claim_id/span grounding against the log) belong to the mapper task in M4m.

## Not done / open
- The engine stamp does not include the lock hash yet. The stamp does not exist until M1 (D-040 consequence).
- There are no retries or fallback to the second backend in `complete()`. `shared.chat` keeps its own 2 attempts on 429/5xx; backend 2 makes a single attempt. The rescue policy per class (backoff 1/4/16 min, then the second backend) belongs to the jobs loop (architecture §4, D23).
- Not wired anywhere yet: rescue per class, operator alerts, model names on the receipt stamp. The boot ping result is only logged and kept in `app.state`. The operator page will surface it later.
- `DEEPSEEK_BASE_URL`, `DEEPSEEK_MODEL` and `DEEPSEEK_API_KEY` are still read by `shared/llm.py` at import or call time, as before.
- CI has still not run on GitHub. The lock was installed and tested locally on 3.14 only.

## Proposed decisions (the checker takes these to the founder; nothing here is decided)
- **PD-1: the per-task output schemas are provisional.** architecture.md §5 says each task has a pydantic schema but defines no fields, except that `map_suggest` returns links (claim_id + span). I picked minimal shapes, for example `coach_question = {question, cites[≥1]}` and `receipt_question = {questions[{text, event_ids[≥1]}]}`. Recommended: each feature task (Coach, receipt, provenance L3, reading aid, mapper) owns its schema and fixture and may change them when it writes the prompt, without a new decision. The R14 `map.finding` kinds (eng v2) stay deferred to M4m and are not in the schema yet.
- **PD-2: the error mapping for codes D13 does not name.** D13 lists five classes but not every status code. I chose: network errors, 408 and 5xx → `LLMTimeout` (transient; same rescue as a timeout); 402 (payment or quota) → `LLMAuth` (account problem: alert the operator); other 4xx, such as a provider content filter → `LLMRefusal`. Recommended: accept. The alternative is a sixth class, `LLMUnavailable`, for 5xx.
- **PD-3: the deepseek backend accepts only `[system, user]` messages.** `shared.chat` takes exactly one system and one user string, and D22 forbids changing its behaviour. Recommended: keep this until a task needs multi-turn calls. At that point, add an optional `messages=` keyword to `shared.chat` (allowed by D22 as an optional keyword param).
- **PD-4: lock tool = uv; `requirements.txt` removed.** The lock is universal (any OS), Python 3.12 and hash-checked. Recommended: accept. The alternative, pip-tools, needs one lock per platform for the same guarantee.

## Checker review (2026-10-24): passed, merged to `main`
- Fresh venv, `pip install --require-hashes -r prototype/requirements.lock`: prototype `119 passed`, kit `29 passed`. `shared/` unchanged; no banned words; no keys.
- Task enum, error classes, stub fixtures and boot ping match architecture.md §5.
- **A:** all lines ticked (incl. "shared/llm.py unchanged").
- Note for M1: `ReceiptQuestion.event_ids` is `list[str]`; if the founder accepts PD-S5-2 (event id = `seq`), it becomes `list[int]` when the receipt compiler owns that schema.
- PD-1…PD-4 go to the founder.
