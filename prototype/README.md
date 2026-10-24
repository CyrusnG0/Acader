# prototype/

The Writing Room v1 code goes here. **The empty scaffold exists (T-001); no features are built yet.** The build starts after the gstack reviews and spikes in [../design/build-plan.md](../design/build-plan.md).

Planned layout ([../design/architecture.md](../design/architecture.md) §6):

```
prototype/
├── server/      FastAPI: app/ (routes, auth, jobs, llm.py), engine/ (events, replay, provenance, receipt; pure, CLI), sources/, coach/, tests/
├── web/         Vite + TypeScript: schema.json, editor/, reader/, map/, coach/, receipt/
├── fixtures/    golden session scripts (YAML), regenerated logs, expected receipts, openly licensed readings
└── spikes/      S1–S5 code and result notes
```

## Run

```
pip install --require-hashes -r requirements.lock      # locked deps (D-040), same as CI
ROOM_LLM=stub python -m pytest -q                      # server tests (from prototype/)
cd server && uvicorn app.main:app --reload             # API on :8000, GET /healthz
cd server && python -m engine compile LOG              # engine CLI stub (exits 2)
cd web && npm install && npm run dev                   # front end
cd web && npm run typecheck && npm test && npm run build
```

### Dependencies (D-040)

`pyproject.toml` lists the direct dependencies; `requirements.lock` pins every package (direct and transitive) with hashes, for Python 3.12 on any platform. CI installs only the lock. To add or upgrade a dependency, edit `pyproject.toml`, then regenerate the lock from `prototype/` and commit both files:

```
pip install uv    # once
uv pip compile pyproject.toml --extra dev --universal --python-version 3.12 --generate-hashes -o requirements.lock
```

Add `--upgrade` to move every pin to the newest allowed version. Never edit the lock by hand. The lock's hash goes into the engine stamp once the stamp exists (M1).

### LLM boundary

`server/app/llm.py`: `complete(task, messages, schema=None) -> dict` (architecture.md §5). Backends: `deepseek` (through `../shared/llm.py`) and `openai_compat` (env `ROOM_LLM2_BASE_URL`, `ROOM_LLM2_MODEL`, `ROOM_LLM2_API_KEY`, optional `ROOM_LLM2_AUTH_HEADER`); `ROOM_LLM_BACKEND` picks the default. `ROOM_LLM=stub` returns a fixed fixture per task. The boot ping runs once at startup; failures are logged and the app still starts.

Rules:
- The LLM client is `../shared/llm.py` (DeepSeek). Don't change its behaviour; wrap it in `server/app/llm.py` (eng D22). Tests run with `ROOM_LLM=stub`.
- Stack and layout: [../design/architecture.md](../design/architecture.md) §4 and §6 (locked by /plan-eng-review, D-034).
- Don't import from `../writing-room-kit/`. Port what you need, so the experiments stay frozen and reproducible.
- No secrets in the repo; the key lives in the repo-root `.env` (gitignored) or the host's secret store.
