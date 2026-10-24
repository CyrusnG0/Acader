"""The LLM boundary (architecture.md §5, D13, D14, D22). No live calls: a fake transport replaces
httpx.post, and the key is a dummy set in the environment (the repo .env is never read)."""
import json

import httpx
import pytest
from pydantic import BaseModel

from app import llm
from app.main import app
from shared import llm as shared_llm

MSGS = [{"role": "system", "content": "sys"}, {"role": "user", "content": "usr"}]
EXPECTED_TASKS = {"claim_extract", "claim_compare", "contradiction", "coach_question",
                  "receipt_question", "limitation_tag", "leak_check", "map_suggest"}


@pytest.fixture
def live(monkeypatch, tmp_path):
    """Live mode against a fake transport. Records each request."""
    monkeypatch.delenv("ROOM_LLM", raising=False)
    monkeypatch.delenv("ROOM_LLM_BACKEND", raising=False)
    for k in ("ROOM_LLM2_BASE_URL", "ROOM_LLM2_MODEL", "ROOM_LLM2_API_KEY", "ROOM_LLM2_AUTH_HEADER"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("DEEPSEEK_API_KEY", "dummy-test-key")
    monkeypatch.setattr(shared_llm, "ROOT_ENV", tmp_path / "no.env")
    calls = []
    state = {"respond": lambda url, kw: _ok("{}")}

    def fake_post(url, **kw):
        calls.append({"url": url, **kw})
        return state["respond"](url, kw)

    monkeypatch.setattr(httpx, "post", fake_post)
    return calls, state


def _resp(status, payload):
    return httpx.Response(status, json=payload, request=httpx.Request("POST", "http://fake"))


def _ok(content):
    return _resp(200, {"choices": [{"message": {"content": content}}]})


# --- tasks and stub ---------------------------------------------------------------------------

def test_task_enum_is_the_spec_list():
    assert {t.value for t in llm.Task} == EXPECTED_TASKS
    assert set(llm.TASK_SCHEMAS) == set(llm.Task)
    assert set(llm.STUB_FIXTURES) == set(llm.Task)


@pytest.mark.parametrize("task", sorted(EXPECTED_TASKS))
def test_stub_is_deterministic_and_valid(monkeypatch, task):
    monkeypatch.setenv("ROOM_LLM", "stub")
    monkeypatch.setattr(httpx, "post", lambda *a, **k: pytest.fail("network call in stub mode"))
    a = llm.complete(task, MSGS)
    b = llm.complete(task, [{"role": "system", "content": "other"}, {"role": "user", "content": "x"}])
    assert a == b == llm.TASK_SCHEMAS[llm.Task(task)].model_validate(llm.STUB_FIXTURES[task]).model_dump()
    a.clear()  # the caller mutating its result must not change the next stub output
    assert llm.complete(task, MSGS) == b


def test_stub_validates_against_given_schema(monkeypatch):
    monkeypatch.setenv("ROOM_LLM", "stub")

    class Other(BaseModel):
        something_else: str

    with pytest.raises(llm.LLMSchema):
        llm.complete("leak_check", MSGS, Other)


@pytest.mark.parametrize("bad", ["write_essay", "", "MAP_SUGGEST", None])
def test_unknown_task_rejected(monkeypatch, bad):
    monkeypatch.setenv("ROOM_LLM", "stub")
    with pytest.raises(llm.UnknownTask):
        llm.complete(bad, MSGS)


def test_schema_must_be_pydantic(monkeypatch):
    monkeypatch.setenv("ROOM_LLM", "stub")
    with pytest.raises(TypeError):
        llm.complete("leak_check", MSGS, dict)


# --- live path through shared/llm.py (fake transport) ------------------------------------------

def test_live_deepseek_returns_validated_dict(live):
    calls, state = live
    state["respond"] = lambda url, kw: _ok('```json\n{"result": "pass"}\n```')
    assert llm.complete("leak_check", MSGS) == {"result": "pass"}
    (c,) = calls
    assert c["url"].endswith("/chat/completions")
    assert c["json"]["response_format"] == {"type": "json_object"}
    assert c["json"]["messages"] == MSGS


def test_map_suggest_links_only(live):
    _, state = live
    good = {"links": [{"claim_id": "c1", "paragraph_id": "p1", "start": 3, "end": 9}]}
    state["respond"] = lambda url, kw: _ok(json.dumps(good))
    assert llm.complete("map_suggest", MSGS) == good
    for bad in ({"links": [], "note": "Here is some prose."},                    # no prose fields
                {"links": [{"claim_id": "c1", "paragraph_id": "p1", "start": 5, "end": 5}]},
                {"links": [{"claim_id": "", "paragraph_id": "p1", "start": 0, "end": 2}]},
                {"links": [{"paragraph_id": "p1", "start": 0, "end": 2}]}):
        state["respond"] = lambda url, kw, bad=bad: _ok(json.dumps(bad))
        with pytest.raises(llm.LLMSchema):
            llm.complete("map_suggest", MSGS)


@pytest.mark.parametrize("content", ["not json at all", '{"result": "maybe"}', '{"other": 1}', "[1, 2]"])
def test_schema_errors(live, content):
    _, state = live
    state["respond"] = lambda url, kw: _ok(content)
    with pytest.raises(llm.LLMSchema):
        llm.complete("leak_check", MSGS)


@pytest.mark.parametrize("status,cls", [
    (401, llm.LLMAuth), (402, llm.LLMAuth), (403, llm.LLMAuth),
    (429, llm.LLMRateLimited),
    (408, llm.LLMTimeout), (500, llm.LLMTimeout), (503, llm.LLMTimeout),
    (400, llm.LLMRefusal), (422, llm.LLMRefusal),
])
def test_status_mapping_deepseek(live, status, cls):
    _, state = live
    state["respond"] = lambda url, kw: _resp(status, {"error": "x"})
    with pytest.raises(cls):
        llm.complete("leak_check", MSGS)


def test_timeout_mapping(live):
    _, state = live

    def boom(url, kw):
        raise httpx.ReadTimeout("slow")

    state["respond"] = boom
    with pytest.raises(llm.LLMTimeout):
        llm.complete("leak_check", MSGS)


def test_empty_output_is_refusal(live):
    _, state = live
    state["respond"] = lambda url, kw: _ok("   ")
    with pytest.raises(llm.LLMRefusal):
        llm.complete("leak_check", MSGS)


def test_bad_response_shape_is_schema(live):
    _, state = live
    state["respond"] = lambda url, kw: _resp(200, {"nope": []})
    with pytest.raises(llm.LLMSchema):
        llm.complete("leak_check", MSGS)


def test_no_key_is_auth(live, monkeypatch):
    calls, _ = live
    monkeypatch.setenv("DEEPSEEK_API_KEY", "")
    with pytest.raises(llm.LLMAuth):
        llm.complete("leak_check", MSGS)
    assert calls == []


def test_errors_never_carry_the_key(live):
    _, state = live
    state["respond"] = lambda url, kw: _resp(401, {"error": "dummy-test-key"})
    with pytest.raises(llm.LLMAuth) as ei:
        llm.complete("leak_check", MSGS)
    assert "dummy-test-key" not in str(ei.value)


def test_deepseek_needs_system_user_pair(live):
    with pytest.raises(ValueError):
        llm.complete("leak_check", [{"role": "user", "content": "only user"}])


# --- backend 2: the OpenAI-compatible slot ----------------------------------------------------

@pytest.fixture
def compat(live, monkeypatch):
    monkeypatch.setenv("ROOM_LLM2_BASE_URL", "https://school.example/openai/")
    monkeypatch.setenv("ROOM_LLM2_MODEL", "school-model")
    monkeypatch.setenv("ROOM_LLM2_API_KEY", "dummy-key-2")
    return live


def test_compat_request_shape(compat):
    calls, state = compat
    state["respond"] = lambda url, kw: _ok('{"result": "fail"}')
    three = MSGS + [{"role": "user", "content": "more"}]  # backend 2 takes full message lists
    assert llm.complete("leak_check", three, backend="openai_compat") == {"result": "fail"}
    (c,) = calls
    assert c["url"] == "https://school.example/openai/chat/completions"
    assert c["headers"] == {"Authorization": "Bearer dummy-key-2"}
    assert c["json"]["model"] == "school-model"
    assert c["json"]["messages"] == three


def test_compat_custom_auth_header(compat, monkeypatch):
    calls, state = compat
    monkeypatch.setenv("ROOM_LLM2_AUTH_HEADER", "api-key")
    state["respond"] = lambda url, kw: _ok('{"result": "pass"}')
    llm.complete("leak_check", MSGS, backend="openai_compat")
    assert calls[0]["headers"] == {"api-key": "dummy-key-2"}


def test_compat_selected_by_env(compat, monkeypatch):
    calls, state = compat
    monkeypatch.setenv("ROOM_LLM_BACKEND", "openai_compat")
    state["respond"] = lambda url, kw: _ok('{"result": "pass"}')
    llm.complete("leak_check", MSGS)
    assert calls[0]["url"].startswith("https://school.example/")


@pytest.mark.parametrize("status,cls", [(401, llm.LLMAuth), (429, llm.LLMRateLimited),
                                        (502, llm.LLMTimeout), (400, llm.LLMRefusal)])
def test_compat_status_mapping(compat, status, cls):
    _, state = compat
    state["respond"] = lambda url, kw: _resp(status, {})
    with pytest.raises(cls):
        llm.complete("leak_check", MSGS, backend="openai_compat")


def test_compat_timeout_empty_and_schema(compat):
    _, state = compat

    def boom(url, kw):
        raise httpx.ConnectTimeout("x")

    state["respond"] = boom
    with pytest.raises(llm.LLMTimeout):
        llm.complete("leak_check", MSGS, backend="openai_compat")
    state["respond"] = lambda url, kw: _ok("")
    with pytest.raises(llm.LLMRefusal):
        llm.complete("leak_check", MSGS, backend="openai_compat")
    state["respond"] = lambda url, kw: _ok('{"result": 3}')
    with pytest.raises(llm.LLMSchema):
        llm.complete("leak_check", MSGS, backend="openai_compat")


def test_compat_unconfigured_or_keyless_is_auth(live, monkeypatch):
    calls, _ = live
    with pytest.raises(llm.LLMAuth):
        llm.complete("leak_check", MSGS, backend="openai_compat")
    monkeypatch.setenv("ROOM_LLM2_BASE_URL", "https://school.example")
    with pytest.raises(llm.LLMAuth):
        llm.complete("leak_check", MSGS, backend="openai_compat")
    assert calls == []


def test_unknown_backend(live, monkeypatch):
    with pytest.raises(ValueError):
        llm.complete("leak_check", MSGS, backend="other")
    monkeypatch.setenv("ROOM_LLM_BACKEND", "other")
    with pytest.raises(ValueError):
        llm.complete("leak_check", MSGS)


# --- boot ping ----------------------------------------------------------------------------------

def test_ping_stub(monkeypatch):
    monkeypatch.setenv("ROOM_LLM", "stub")
    monkeypatch.setattr(httpx, "post", lambda *a, **k: pytest.fail("network call in stub mode"))
    assert all(r.ok for r in llm.ping_backends())


def test_ping_checks_each_configured_backend(compat):
    calls, state = compat
    state["respond"] = lambda url, kw: (_ok("OK") if "school.example" in url
                                        else _resp(401, {}))
    res = {r.backend: r for r in llm.ping_backends()}
    assert set(res) == {"deepseek", "openai_compat"}
    assert res["deepseek"].ok is False and res["deepseek"].error == "auth"
    assert res["openai_compat"].ok is True
    assert len(calls) == 2


def test_ping_only_deepseek_when_slot_empty(live):
    calls, state = live
    state["respond"] = lambda url, kw: _resp(429, {})
    (r,) = llm.ping_backends()
    assert (r.backend, r.ok, r.error) == ("deepseek", False, "rate_limited")


def test_app_boot_runs_ping_and_still_starts(live):
    calls, state = live
    state["respond"] = lambda url, kw: _resp(401, {})
    from fastapi.testclient import TestClient
    with TestClient(app) as client:
        assert client.get("/healthz").status_code == 200
        assert [r.error for r in app.state.llm_ping] == ["auth"]

