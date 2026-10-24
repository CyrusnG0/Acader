"""DeepSeek client (OpenAI-compatible chat API). The key stays server-side, never logged."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

import httpx

BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
ROOT_ENV = Path(__file__).resolve().parent.parent / ".env"


class LLMError(Exception):
    kind = "llm_error"


class NoKey(LLMError):
    kind = "no_key"


class Upstream(LLMError):
    kind = "upstream"


class BadOutput(LLMError):
    kind = "bad_output"


def api_key() -> str:
    k = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not k and ROOT_ENV.exists():
        from dotenv import dotenv_values
        k = (dotenv_values(ROOT_ENV).get("DEEPSEEK_API_KEY") or "").strip()
    if not k:
        raise NoKey("DEEPSEEK_API_KEY is not set (env var or repo-root .env)")
    return k


def chat(system: str, user: str, *, json_mode: bool = False, max_tokens: int = 900,
         temperature: float = 0.4) -> str:
    body = {"model": MODEL, "max_tokens": max_tokens, "temperature": temperature,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    if json_mode:
        body["response_format"] = {"type": "json_object"}
    headers = {"Authorization": f"Bearer {api_key()}"}
    last = None
    for attempt in range(2):
        try:
            r = httpx.post(f"{BASE_URL}/chat/completions", headers=headers, json=body, timeout=60)
        except httpx.HTTPError as e:
            last = Upstream(f"network error: {type(e).__name__}")
            continue
        if r.status_code == 200:
            try:
                text = r.json()["choices"][0]["message"]["content"] or ""
            except (KeyError, IndexError, ValueError) as e:
                raise BadOutput("unexpected response shape") from e
            if not text.strip():
                raise BadOutput("empty model output")
            return text
        last = Upstream(f"HTTP {r.status_code}")
        if r.status_code not in (429, 500, 502, 503):
            break
    raise last or Upstream("unknown")


def parse_json(text: str):
    """Parse a JSON object/array from model text (tolerates ```json fences)."""
    t = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        m = re.search(r"[\[{].*[\]}]", t, re.S)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                pass
    raise BadOutput("model did not return valid JSON")
