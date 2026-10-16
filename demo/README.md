# Acader Room demo

Showable demo of the product vision: several **Spaces** (courses/projects), each with its own **Sources** (lecture, paper, handout, note), a typing-only **writing sandbox**, a **Helper** and a **Coach**, a **coverage map**, an in-room **citation check**, and a **Proof of Understanding** at the end. LLM: **DeepSeek** (`deepseek-chat`). Decision: D-016. This is a demo, not pilot evidence.

## Run
```bash
cd demo
pip install -r requirements.txt
# put DEEPSEEK_API_KEY=... in the repo-root .env (gitignored) or export it
uvicorn server:app --port 8770      # open http://localhost:8770
python3 -m pytest -q
```
Env: `DEEPSEEK_MODEL` (default `deepseek-chat`), `DEEPSEEK_BASE_URL` (default `https://api.deepseek.com`).

## What each part does (and which product rule it demonstrates)
| Part | Behavior | Rule |
|---|---|---|
| Spaces + sources | Two seeded rooms (Econ essay, CS FYP). Add/remove sources; paste is allowed here (the Door is source-neutral). Sample sources are **fictional**. | Door, Spaces |
| Sandbox | Typing only: paste/drop is blocked and counted; bulk insertions (>40 chars in one input) count as "large inputs". "Assisted input" toggle allows paste/dictation as an accessibility alternative but escalates the Coach and recommends an oral check. | Typing is entry condition, not proof; accessibility |
| Helper | Answers questions, finds evidence in the room's sources, points to the **lecture first**; declines to write your claims or paragraphs. | Helper vs Coach; professors first |
| Coach | Asks one grounded question about your draft (anchor quote validated against the draft); never answers. Frequency tunable (Off/Low/High); escalation on large input is not tunable. Your answers get a formative signal: strong / partial / a short oral check would help. | Coach asks; formative only |
| Coverage map | Claims in your draft mapped to sources, plus gap/conflict **questions**. Claims with quotes not found in the draft are dropped. | Questions, not answers |
| Citation check | Each `[S1]`-style marker checked against that source: supported / partial / unsupported / not found / unverified. Evidence quotes must exist in the source or the verdict is downgraded to "unverified". | Citations real and supportive |
| Proof | Computed deterministically (not by the LLM): **Standard**, **Oral-verified recommended**, or **Returned with reasons**. States it is a learning record, not a verdict; a human decides. | Never a cheat report |

## Honest limits
- **Citation check covers this room's sources only.** Live DOI/Crossref/full-text verification (proposal 4.4) is not implemented.
- No lecture-mining here: the "lecture" sources are hand-written text. The miner is separate (OL-002).
- Code track is not in this demo (see `../runner/` for the viva runner).
- State is in the browser's localStorage; no accounts, no multi-user, no school dashboard, no LMS.
- Your text goes to DeepSeek. **Do not enter real student data.** For the pilot, `runner/` uses its own consent policy (D-014).
- Prompt-injection is mitigated (student text is quoted data, anchors/quotes/evidence are validated) but not exhaustively tested.
