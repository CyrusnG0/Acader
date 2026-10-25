"""Issue a receipt for a sealed log: compile marks, L1, then the receipt, then `receipt.issued`.

The receipt, its AI artifacts and `receipt.issued` are written in one transaction after the
model calls finish (app/receipt_store.py). A retry for the same log, seal and version returns
the stored bytes and does not ask the model again.
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
from app.receipt_store import ReceiptConflict, ReceiptStore
from engine.events import sha256_hex, ts_seconds
from engine.provenance import CompileResult, compile_marks, l1_from_compile
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


def _latest_submit(events: list) -> dict | None:
    submits = [e for e in events if e["type"] == "submit"]
    return submits[-1] if submits else None


def _issued_event(events: list, receipt_id: str, version: int) -> dict | None:
    for e in reversed(events):
        if e["type"] != "receipt.issued":
            continue
        payload = e.get("payload") or {}
        if payload.get("receipt_id") == receipt_id and payload.get("version") == version:
            return e
    return None


def _issued_result(store: ReceiptStore, log_id: str, receipt, version: int,
                   events: list) -> tuple:
    """The ReceiptResult and event for an already stored receipt."""
    event = _issued_event(events, receipt.receipt_id, version)
    if event is None:
        raise ReceiptConflict("a stored receipt has no receipt.issued event")
    if event["payload"].get("receipt_hash") != receipt.receipt_hash:
        raise ReceiptConflict("the stored receipt differs from its receipt.issued event")
    return ReceiptResult(receipt.receipt, store.stored_artifacts(log_id),
                         receipt.receipt_hash), event


def _stored_result(store: ReceiptStore, log_id: str, version: int,
                   events: list) -> tuple | None:
    """The already-issued receipt for the current seal, if there is one (model-free retry)."""
    seal = _latest_submit(events)
    if seal is None:
        return None
    receipt = store.get(log_id, seal_hash=seal["hash"], version=version)
    if receipt is None:
        return None
    return _issued_result(store, log_id, receipt, version, events)


def _persist(service: EventService, store: ReceiptStore, log_id: str, res: ReceiptResult,
             *, version: int, extra_artifacts=None) -> tuple:
    """Store the receipt and artifacts with `receipt.issued`, atomically and idempotently.

    The first issuance wins. If another caller stored this log/seal/version between our
    pre-check and this transaction, return that stored receipt, even when the two engine
    stamps differ (PD-T018-1).
    """
    receipt = res.receipt
    seal_hash, seal_seq = receipt["seal_hash"], receipt["seal_seq"]
    with service._lock, service._tx():
        existing = store.get(log_id, seal_hash=seal_hash, version=version)
        if existing is not None:
            return _issued_result(store, log_id, existing, version,
                                  service.store.events(log_id))
        store.store_in_tx(log_id, receipt=receipt, receipt_hash=res.receipt_hash,
                          artifacts=res.artifacts, extra_artifacts=extra_artifacts,
                          seal_hash=seal_hash, seal_seq=seal_seq, version=version)
        # Same housekeeping as EventService.append_event: write any due staging batch first.
        service._flush(log_id, force=False, now=service.clock())
        events = service.store.events(log_id)
        event = _issued_event(events, receipt["receipt_id"], version)
        if event is not None:
            if event["payload"].get("receipt_hash") != res.receipt_hash:
                raise ReceiptConflict("a receipt.issued event names different receipt bytes")
            return res, event
        event = service.store.append_in_tx(
            log_id, type="receipt.issued", actor="system", payload=res.issued_payload(),
            ts=ts_seconds(service.clock()))
        return res, event


def _seal_for(events: list, seal_hash: str | None) -> dict:
    """The submit event named by `seal_hash`, or the latest submit when it is None."""
    submits = [e for e in events if e["type"] == "submit"]
    if seal_hash is None:
        if not submits:
            raise ValueError("log has no submit event")
        return submits[-1]
    seal = next((e for e in submits if e["hash"] == seal_hash), None)
    if seal is None:
        raise ValueError("seal_hash does not name a submit event")
    return seal


def build_receipt(service: EventService, log_id: str, sources, *, seal_hash: str | None = None,
                  version: int = 1, ask, stored, stamp=None,
                  block_kinds=None) -> tuple[ReceiptResult, CompileResult]:
    """Compile one receipt without writing anything. `seal_hash=None` means the latest submit.

    Asking the model and reading snapshots happen with no write transaction open.
    """
    events = service.events(log_id)
    seal = _seal_for(events, seal_hash)
    result = compile_marks(events, load_snapshot_fn(service, log_id), sources,
                           seal_seq=seal["seq"])
    l1 = l1_from_compile(result, events, block_kinds=block_kinds)
    res: ReceiptResult = compile_receipt(
        events=events, l1=l1, doc=result.replay.doc, log_id=log_id, seal_hash=seal["hash"],
        sources=sources, stamp=stamp or build_stamp(), ask=ask, stored=stored, version=version)
    return res, result


def stored_receipt(service: EventService, store: ReceiptStore, log_id: str, *,
                   seal_hash: str, version: int) -> tuple | None:
    """The already-issued receipt for an explicit seal, if there is one (model-free retry)."""
    with service._lock:
        receipt = store.get(log_id, seal_hash=seal_hash, version=version)
        if receipt is None:
            return None
        events = service.store.events(log_id)
        return _issued_result(store, log_id, receipt, version, events)


def store_artifacts(service: EventService, store: ReceiptStore, log_id: str,
                    artifacts) -> int:
    """Store compile artifacts in a transaction owned by this call."""
    with service._lock, service._tx():
        return store.store_artifacts_in_tx(log_id, artifacts)


def issue_receipt(service: EventService, log_id: str, sources, *, version: int = 1, stored=None,
                  ask=llm_ask, stamp=None, block_kinds=None, receipts: ReceiptStore | None = None,
                  extra_artifacts=None, seal_hash: str | None = None) -> tuple:
    store = receipts or ReceiptStore(service.db)
    if seal_hash is None:
        events = service.events(log_id)
        with service._lock:
            issued = _stored_result(store, log_id, version, events)
            if issued is not None:
                return issued
            if stored is None:
                stored = store.stored_artifacts(log_id)
    else:
        issued = stored_receipt(service, store, log_id, seal_hash=seal_hash, version=version)
        if issued is not None:
            return issued
        if stored is None:
            with service._lock:
                stored = store.stored_artifacts(log_id)
    res, _ = build_receipt(service, log_id, sources, seal_hash=seal_hash, version=version,
                           ask=ask, stored=stored, stamp=stamp, block_kinds=block_kinds)
    res, ev = _persist(service, store, log_id, res, version=version,
                       extra_artifacts=extra_artifacts)
    return res, ev
