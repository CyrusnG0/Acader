"""The LLM boundary: `complete(task, messages, schema) -> dict` (architecture.md §5).

- Backend `deepseek` goes through `shared/llm.py` unchanged (eng D22): `chat()` + `parse_json()`.
- Backend `openai_compat` is the generic OpenAI-compatible slot (eng D14): base URL, model, key
  and auth header name come from config (env vars below). The school picks it; consent names it.
- `ROOM_LLM=stub` returns a fixed fixture per task, validated against the schema like live output.
  No network, no key, same output for the same task every time.
- Errors are the five D13 classes. Callers rescue per class (ceo-review-v1.md §2).
- `ping_backends()` is the boot ping: one tiny call per configured backend.

Never log prompt text, model output or keys.

Config (env):
  ROOM_LLM=stub                  stub mode (tests)
  ROOM_LLM_BACKEND               default backend: deepseek (default) | openai_compat
  ROOM_LLM2_BASE_URL             backend 2 base URL (the slot is "configured" when this is set)
  ROOM_LLM2_MODEL                backend 2 model / deployment name
  ROOM_LLM2_API_KEY              backend 2 key (host secret store; never in the repo)
  ROOM_LLM2_AUTH_HEADER          default "Authorization" (sent as "Bearer <key>"); any other name
                                 (e.g. Azure's "api-key") is sent as the raw key
  DEEPSEEK_API_KEY / DEEPSEEK_BASE_URL / DEEPSEEK_MODEL   read by shared/llm.py
"""
from __future__ import annotations

import logging
import os
import sys
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Literal

import httpx
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from shared import llm as shared_llm  # noqa: E402  (namespace package; shared/ stays untouched)

log = logging.getLogger("room.llm")


# --- errors (D13) -------------------------------------------------------------------------------

class LLMError(Exception):
    """Base class. `kind` is safe to log; the message never holds prompt text or a key."""
    kind = "llm_error"


class LLMTimeout(LLMError):
    """Provider timed out or was temporarily unavailable (network error, 408, 5xx)."""
    kind = "timeout"


class LLMRateLimited(LLMError):
    """429 / quota."""
    kind = "rate_limited"


class LLMAuth(LLMError):
    """No key, bad key, or an account problem (401, 402, 403). Fail fast; alert the operator."""
    kind = "auth"


class LLMRefusal(LLMError):
    """Empty output, or the provider declined the request (other 4xx)."""
    kind = "refusal"


class LLMSchema(LLMError):
    """Output is not JSON, or does not fit the task's output schema."""
    kind = "schema"


class UnknownTask(ValueError):
    """`task` is not one of the Task enum values."""


# --- tasks and their output schemas -------------------------------------------------------------

class Task(StrEnum):
    claim_extract = "claim_extract"
    claim_compare = "claim_compare"
    contradiction = "contradiction"
    coach_question = "coach_question"
    receipt_question = "receipt_question"
    limitation_tag = "limitation_tag"
    leak_check = "leak_check"
    map_suggest = "map_suggest"


class _Out(BaseModel):
    model_config = ConfigDict(extra="forbid")


# PROVISIONAL shapes (PD-1 in the T-003 handoff): the design names the tasks but not their
# fields. Each feature task owns and may refine its schema (and fixture) when it builds the prompt.

class ExtractedClaim(_Out):
    text: str = Field(min_length=1)


class ClaimExtractOut(_Out):
    claims: list[ExtractedClaim]


class ClaimCompareOut(_Out):
    relation: Literal["same", "related", "different"]


class ContradictionPair(_Out):
    claim_a: str = Field(min_length=1)
    claim_b: str = Field(min_length=1)


class ContradictionOut(_Out):
    pairs: list[ContradictionPair]


class CoachQuestionOut(_Out):
    question: str = Field(min_length=1)
    cites: list[str] = Field(min_length=1)  # block or claim ids (law 2: grounded, never generic)


class ReceiptQuestion(_Out):
    text: str = Field(min_length=1)
    event_ids: list[str] = Field(min_length=1)  # every receipt line cites events (receipt.md §6)


class ReceiptQuestionOut(_Out):
    questions: list[ReceiptQuestion]


class LimitationTagOut(_Out):
    passages: list[str]  # passage ids inside the discussion block that state a limitation


class LeakCheckOut(_Out):
    result: Literal["pass", "fail"]


class MapLink(_Out):
    """Links only, never prose (D-035). Existence of claim_id and paragraph_id is checked by the
    mapper against the current log (dropped if absent), not here."""
    claim_id: str = Field(min_length=1)
    paragraph_id: str = Field(min_length=1)
    start: int = Field(ge=0)
    end: int

    @model_validator(mode="after")
    def _span(self) -> "MapLink":
        if self.end <= self.start:
            raise ValueError("span end must be after start")
        return self


class MapSuggestOut(_Out):
    links: list[MapLink]


TASK_SCHEMAS: dict[Task, type[BaseModel]] = {
    Task.claim_extract: ClaimExtractOut,
    Task.claim_compare: ClaimCompareOut,
    Task.contradiction: ContradictionOut,
    Task.coach_question: CoachQuestionOut,
    Task.receipt_question: ReceiptQuestionOut,
    Task.limitation_tag: LimitationTagOut,
    Task.leak_check: LeakCheckOut,
    Task.map_suggest: MapSuggestOut,
}

# Stub fixtures: fixed, content-free placeholders (tests only; never shown to a student).
STUB_FIXTURES: dict[Task, dict] = {
    Task.claim_extract: {"claims": [{"text": "stub claim"}]},
    Task.claim_compare: {"relation": "related"},
    Task.contradiction: {"pairs": []},
    Task.coach_question: {"question": "stub question", "cites": ["stub-block-1"]},
    Task.receipt_question: {"questions": [{"text": "stub question", "event_ids": ["stub-event-1"]}]},
    Task.limitation_tag: {"passages": []},
    Task.leak_check: {"result": "pass"},
    Task.map_suggest: {"links": [{"claim_id": "stub-claim-1", "paragraph_id": "stub-para-1",
                                  "start": 0, "end": 1}]},
}


# --- config -------------------------------------------------------------------------------------

BACKENDS = ("deepseek", "openai_compat")


def stub_mode() -> bool:
    return os.environ.get("ROOM_LLM", "") == "stub"


def default_backend() -> str:
    b = os.environ.get("ROOM_LLM_BACKEND", "deepseek").strip() or "deepseek"
    if b not in BACKENDS:
        raise ValueError(f"ROOM_LLM_BACKEND must be one of {BACKENDS}")
    return b


@dataclass(frozen=True)
class CompatConfig:
    base_url: str
    model: str
    api_key: str
    auth_header: str = "Authorization"

    @classmethod
    def from_env(cls) -> "CompatConfig | None":
        base = os.environ.get("ROOM_LLM2_BASE_URL", "").strip()
        if not base:
            return None
        return cls(base_url=base.rstrip("/"),
                   model=os.environ.get("ROOM_LLM2_MODEL", "").strip(),
                   api_key=os.environ.get("ROOM_LLM2_API_KEY", "").strip(),
                   auth_header=os.environ.get("ROOM_LLM2_AUTH_HEADER", "").strip() or "Authorization")


def configured_backends() -> list[str]:
    """deepseek is always configured (a missing key shows up as LLMAuth at the ping)."""
    out = ["deepseek"]
    if CompatConfig.from_env() is not None:
        out.append("openai_compat")
    return out


# --- error mapping ------------------------------------------------------------------------------

def _from_status(code: int) -> LLMError:
    msg = f"HTTP {code}"
    if code in (401, 402, 403):
        return LLMAuth(msg)
    if code == 429:
        return LLMRateLimited(msg)
    if code == 408 or code >= 500:
        return LLMTimeout(msg)
    return LLMRefusal(msg)


def _from_shared(e: shared_llm.LLMError) -> LLMError:
    msg = str(e)
    if isinstance(e, shared_llm.NoKey):
        return LLMAuth("no key")
    if isinstance(e, shared_llm.Upstream):
        if msg.startswith("HTTP "):
            try:
                return _from_status(int(msg.split()[1]))
            except (IndexError, ValueError):
                pass
        return LLMTimeout(msg)  # "network error: <Name>", "unknown"
    if isinstance(e, shared_llm.BadOutput):
        if msg == "empty model output":
            return LLMRefusal(msg)
        return LLMSchema(msg)
    return LLMTimeout(type(e).__name__)


# --- transports ---------------------------------------------------------------------------------

def _split(messages: list[dict]) -> tuple[str, str]:
    """shared.chat takes one system and one user message, so the deepseek backend needs exactly that."""
    if (len(messages) != 2 or messages[0].get("role") != "system"
            or messages[1].get("role") != "user"):
        raise ValueError("the deepseek backend takes exactly [system, user] messages")
    return str(messages[0].get("content", "")), str(messages[1].get("content", ""))


def _call_deepseek(messages: list[dict], max_tokens: int) -> str:
    system, user = _split(messages)
    try:
        return shared_llm.chat(system, user, json_mode=True, max_tokens=max_tokens, temperature=0.2)
    except shared_llm.LLMError as e:
        raise _from_shared(e) from None


def _call_compat(cfg: CompatConfig, messages: list[dict], max_tokens: int, *,
                 json_mode: bool = True) -> str:
    if not cfg.api_key:
        raise LLMAuth("no key")
    value = f"Bearer {cfg.api_key}" if cfg.auth_header.lower() == "authorization" else cfg.api_key
    body = {"model": cfg.model, "messages": messages, "max_tokens": max_tokens, "temperature": 0.2}
    if json_mode:
        body["response_format"] = {"type": "json_object"}
    try:
        r = httpx.post(f"{cfg.base_url}/chat/completions", headers={cfg.auth_header: value},
                       json=body, timeout=60)
    except httpx.HTTPError as e:
        raise LLMTimeout(f"network error: {type(e).__name__}") from None
    if r.status_code != 200:
        raise _from_status(r.status_code)
    try:
        text = r.json()["choices"][0]["message"]["content"] or ""
    except (KeyError, IndexError, TypeError, ValueError):
        raise LLMSchema("unexpected response shape") from None
    if not text.strip():
        raise LLMRefusal("empty model output")
    return text


def _raw(backend: str, messages: list[dict], max_tokens: int) -> str:
    if backend == "deepseek":
        return _call_deepseek(messages, max_tokens)
    if backend == "openai_compat":
        cfg = CompatConfig.from_env()
        if cfg is None:
            raise LLMAuth("backend openai_compat is not configured")
        return _call_compat(cfg, messages, max_tokens)
    raise ValueError(f"unknown backend {backend!r}; one of {BACKENDS}")


# --- the boundary -------------------------------------------------------------------------------

def _task(task: str | Task) -> Task:
    try:
        return Task(task)
    except ValueError:
        raise UnknownTask(f"unknown LLM task {task!r}") from None


def _validate(schema: type[BaseModel], data: object) -> dict:
    try:
        return schema.model_validate(data).model_dump()
    except ValidationError as e:
        raise LLMSchema(f"output does not fit {schema.__name__} ({e.error_count()} errors)") from None


def complete(task: str | Task, messages: list[dict], schema: type[BaseModel] | None = None, *,
             backend: str | None = None, max_tokens: int = 900) -> dict:
    """Run one LLM task and return its validated output as a dict.

    `schema` defaults to the task's registered output schema (TASK_SCHEMAS). Raises UnknownTask
    for a task outside the enum, and one of the five LLM* classes for provider or output failures.
    """
    t = _task(task)
    schema = schema or TASK_SCHEMAS[t]
    if not (isinstance(schema, type) and issubclass(schema, BaseModel)):
        raise TypeError("schema must be a pydantic BaseModel subclass")
    if stub_mode():
        return _validate(schema, STUB_FIXTURES[t])  # validation builds fresh objects
    text = _raw(backend or default_backend(), messages, max_tokens)
    try:
        data = shared_llm.parse_json(text)
    except shared_llm.BadOutput:
        raise LLMSchema("model did not return valid JSON") from None
    return _validate(schema, data)


# --- boot ping (D13) ----------------------------------------------------------------------------

@dataclass(frozen=True)
class PingResult:
    backend: str
    ok: bool
    error: str | None = None  # an LLMError.kind, never a message with secrets


_PING = [{"role": "system", "content": "Reply with the single word OK."},
         {"role": "user", "content": "ping"}]


def ping_backends() -> list[PingResult]:
    """One tiny call per configured backend. Never raises; the caller logs and alerts."""
    if stub_mode():
        return [PingResult(b, True) for b in configured_backends()]
    out = []
    for b in configured_backends():
        try:
            if b == "deepseek":
                try:
                    shared_llm.chat(_PING[0]["content"], _PING[1]["content"], max_tokens=5)
                except shared_llm.LLMError as e:
                    raise _from_shared(e) from None
            else:
                _call_compat(CompatConfig.from_env(), _PING, 5, json_mode=False)
            out.append(PingResult(b, True))
        except LLMError as e:
            out.append(PingResult(b, False, e.kind))
    for r in out:
        if not r.ok:
            log.warning("LLM backend %s failed the boot ping: %s", r.backend, r.error)
    return out
