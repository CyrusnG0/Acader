# Viva runner (pilot)

Thin async practice-viva tool from [docs/designs/concierge-viva-pilot.md](../docs/designs/concierge-viva-pilot.md). Decisions: D-011 to D-015.

## Run
```bash
cd runner
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...        # without it, an OFFLINE STUB asks canned "[stub]" questions
uvicorn app:app --reload            # http://localhost:8000
python3 -m pytest -q
```
Optional env: `VIVA_MODEL` (default `claude-sonnet-5-5`), `VIVA_DATA` (default `runner/data/`, gitignored).

## Flow
1. Instructor opens `/`, pastes assignment + reference solution (+ structured course context and raw notes for blind-test mode), gets a student link and a private report link.
2. Student opens `/s/<id>`, reads the consent note, pastes code, answers 3-4 line-level questions.
3. Instructor opens `/i/<id>?token=...` for per-session signals. Full answers show only if the student consented. Blind mode: rate set X vs set Y; `/api/assignments/<id>/blind-summary` tallies graph vs raw (pass bar: graph wins >= 6 rated).

## Guardrails (D-013) and data policy (D-014)
Code is quoted data; each question must cite a real line and quote its text (else dropped, up to 2 retries, then a visible "generation failed" with a manual fallback). Sessions are deleted after 30 days (purged at startup); students can export or delete their own via the page. Reports are signals, never a verdict.

## Known limits (demo-grade)
- Real-LLM path is untested without an API key; only the stub and injected fakes are covered by tests.
- Pages were smoke-tested over HTTP, not in a browser. No auth beyond secret links/tokens. File-based storage. No rate limiting. Purge runs only at startup.
- Student answers set X only in blind mode; the instructor rates question sets X vs Y by quality, not by answers.
- Speech-to-text answers are not implemented (text only).
