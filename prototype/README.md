# prototype/

The Writing Room v1 code goes here. **Nothing is built yet.** The build starts after the gstack reviews and spikes in [../design/build-plan.md](../design/build-plan.md).

Planned layout ([../design/architecture.md](../design/architecture.md) §6):

```
prototype/
├── server/      FastAPI: app/ (routes, auth, jobs, llm.py), engine/ (events, replay, provenance, receipt; pure, CLI), sources/, coach/, tests/
├── web/         Vite + TypeScript: schema.json, editor/, reader/, map/, coach/, receipt/
├── fixtures/    golden session scripts (YAML), regenerated logs, expected receipts, openly licensed readings
└── spikes/      S1–S5 code and result notes
```

Rules:
- The LLM client is `../shared/llm.py` (DeepSeek). Don't change its behaviour; wrap it in `server/app/llm.py` (eng D22). Tests run with `ROOM_LLM=stub`.
- Stack and layout: [../design/architecture.md](../design/architecture.md) §4 and §6 (locked by /plan-eng-review, D-034).
- Don't import from `../writing-room-kit/`. Port what you need, so the experiments stay frozen and reproducible.
- No secrets in the repo; the key lives in the repo-root `.env` (gitignored) or the host's secret store.
