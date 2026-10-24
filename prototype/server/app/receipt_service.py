"""Issue a receipt for a sealed log: compile marks, L1, then the receipt, then `receipt.issued`.

Writes no table other than the chain (storing receipts and artifacts is a later task).
"""
from __future__ import annotations

import importlib.metadata
import json
import os
import subprocess
from pathlib import Path

from app.compile_service import load_snapshot_fn
from app.events_service import EventService
from app.llm import LLMError, LLMSchema, Task, complete, default_backend
from engine.events import sha256_hex
from engine.provenance import compile_marks, l1_from_compile
from engine.receipt import (ENGINE_VERSION, LLMUnavailable, OutputRejected, ReceiptResult,
                            compile_receipt, prompt_file_hash)

_PROTOTYPE = Path(__file__).resolve().parents[2]


def llm_ask(messages) -> dict:
    try:
        return complete(Task.receipt_question, messages)
    except LLMSchema as e:
        raise OutputRejected(str(e)) from None
    except LLMError as e:
        raise LLMUnavailable(str(e)) from None


def _git_sha() -> str:
    try:
        p = subprocess.run(["git", "rev-parse", "HEAD"], cwd=_PROTOTYPE, capture_output=True,
                           text=True, timeout=5)
        out = p.stdout.strip()
        return out if p.returncode == 0 and out else "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def _models() -> dict:
    if os.environ.get("ROOM_LLM", "") == "stub":
        return {"receipt_question": "stub"}
    backend = default_backend()
    if backend == "openai_compat":
        model = os.environ.get("ROOM_LLM2_MODEL", "").strip()
    else:
        model = os.environ.get("DEEPSEEK_MODEL", "").strip() or "deepseek-chat"
    return {"receipt_question": f"{backend}/{model}"}


def build_stamp(*, git_sha: str | None = None) -> dict:
    sha = git_sha or os.environ.get("ROOM_GIT_SHA", "").strip() or _git_sha()
    lock = sha256_hex((_PROTOTYPE / "requirements.lock").read_bytes())
    pkg = json.loads((_PROTOTYPE / "web" / "package.json").read_text(encoding="utf-8"))
    tiptap = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}["@tiptap/pm"]
    pair = f"tiptap-pm {tiptap} / prosemirror-py {importlib.metadata.version('prosemirror')}"
    return {"version": ENGINE_VERSION, "git_sha": sha, "lock_hash": lock, "editor_pair": pair,
            "models": _models(), "prompt_hashes": {"receipt_question": prompt_file_hash()}}


def issue_receipt(service: EventService, log_id: str, sources, *, version: int = 1, stored=None,
                  ask=llm_ask, stamp=None, block_kinds=None) -> tuple:
    events = service.events(log_id)
    result = compile_marks(events, load_snapshot_fn(service, log_id), sources)
    l1 = l1_from_compile(result, events, block_kinds=block_kinds)
    seal_seq = result.replay.seal_seq
    seal_hash = next(e["hash"] for e in events if e["seq"] == seal_seq)
    res: ReceiptResult = compile_receipt(
        events=events, l1=l1, doc=result.replay.doc, log_id=log_id, seal_hash=seal_hash,
        sources=sources, stamp=stamp or build_stamp(), ask=ask, stored=stored, version=version)
    ev = service.append_event(log_id, type="receipt.issued", actor="system",
                              payload=res.issued_payload())
    return res, ev
