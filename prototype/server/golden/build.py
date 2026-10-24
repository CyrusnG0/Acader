"""The ingest builder: a script plus a browser recording become one sealed log, then L1 (T-015).

Student events go through the real HTTP API (TestClient, no lifespan); server-side events go
through the same EventService with their real actors. Nothing reads the wall clock.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.compile_service import load_snapshot_fn
from app.main import create_app
from app.receipt_service import build_stamp, issue_receipt, llm_ask
from engine.events import canonical_json
from engine.provenance import (InMemorySources, coach_answer_from_runs, compile_marks,
                               l1_from_compile)

from .script import (EDITOR_ACTIONS, RECORDED_DIR, editor_actions_sha256, load_blocks,
                     load_script)

T0 = datetime(2026, 11, 2, 14, 0, tzinfo=timezone.utc)
_TEXTBLOCKS = ("paragraph", "heading")


class BuildError(RuntimeError):
    pass


class StaleRecording(RuntimeError):
    pass


class Clock:
    def __init__(self):
        self.t = T0

    def __call__(self) -> datetime:
        return self.t


@dataclass
class BuildResult:
    session_id: str
    events: list
    seal: str
    seal_seq: int
    compile: dict
    l1: dict
    checkpoints_skipped: int
    verify: dict
    receipt: dict
    artifacts: dict
    receipt_hash: str
    receipt_events: list
    stamp: dict
    doc: object
    sources: InMemorySources


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _paragraph_node(doc: dict, paragraph_id: str) -> dict:
    """The n-th textblock (p1 = first) in document order."""
    if not (paragraph_id.startswith("p") and paragraph_id[1:].isdigit()):
        raise BuildError(f"bad paragraph id {paragraph_id!r}")
    want = int(paragraph_id[1:])
    found: list[dict] = []

    def walk(node: dict) -> None:
        if node.get("type") in _TEXTBLOCKS:
            found.append(node)
            return
        for child in node.get("content") or []:
            walk(child)

    walk(doc)
    if not 1 <= want <= len(found):
        raise BuildError(f"paragraph {paragraph_id} not in the recorded document "
                         f"({len(found)} textblocks)")
    return found[want - 1]


def _runs_from(item: dict, where: str) -> tuple[str, list[dict]]:
    """(text, origin_runs) from an action with `text` or `parts`; offsets are code points."""
    if item.get("parts") is not None:
        text, runs = "", []
        for part in item["parts"]:
            t = part["text"]
            runs.append({"from": len(text), "to": len(text) + len(t), "kind": part["kind"]})
            text += t
        return text, runs
    if "text" in item:
        t = item["text"]
        return t, [{"from": 0, "to": len(t), "kind": "typed"}]
    raise BuildError(f"{where}: needs text or parts")


class _Builder:
    def __init__(self, session_id: str, script: dict, recording: dict, *, ask):
        self.id = session_id
        self.ask = ask
        self.script = script
        self.rec = recording
        self.blocks = load_blocks()
        self.clock = Clock()
        self.app = None
        self.client = None
        self.svc = None
        self.rev = 0
        self.client_seq = 0
        self.rec_entries = list(recording["actions"])
        self.rec_pos = 0
        self.latest_doc_entry: dict | None = None
        self.last_editor_entry: dict | None = None
        self.skipped = 0
        self.seal = None
        self.seal_seq = None
        self.where = ""
        self.artifacts: dict = {}
        self.claims = {c["claim_id"]: c["text"] for c in script.get("claims") or []}

    # ---- plumbing --------------------------------------------------------------------------
    def call(self, method: str, path: str, body: dict | None = None) -> dict:
        r = self.client.request(method, path, json=body)
        if not 200 <= r.status_code < 300:
            raise BuildError(f"{self.where}: {method} {path} -> {r.status_code} {r.text}")
        return r.json()

    def lease(self) -> str:
        return self.call("POST", f"/logs/{self.id}/lease", {"device_id": "golden"})["token"]

    def student(self, type_: str, payload: dict, doc_rev: int | None = None) -> None:
        body: dict = {"type": type_, "payload": payload}
        if doc_rev is not None:
            body["doc_rev"] = doc_rev
        self.call("POST", f"/logs/{self.id}/events", body)

    def server(self, type_: str, actor: str, payload: dict) -> None:
        self.svc.append_event(self.id, type=type_, actor=actor, payload=payload)

    def need_doc(self, what: str) -> dict:
        e = self.last_editor_entry
        if e is None or e.get("doc") is None:
            raise BuildError(f"{self.where}: recording has no doc for {what}")
        return e

    # ---- the walk --------------------------------------------------------------------------
    def run(self) -> BuildResult:
        self.app = create_app(db_path=":memory:", clock=self.clock)
        self.client = TestClient(self.app)
        self.svc = self.app.state.events
        self.where = "open log"
        self.call("POST", "/logs", {"log_id": self.id, "assignment_id": "golden",
                                    "consent_version": 1,
                                    "mapper_enabled": self.script.get("mapper_enabled", False)})
        per_minute: dict[int, int] = {}
        for i, a in enumerate(self.script["actions"]):
            k = per_minute.get(a["minute"], 0)
            per_minute[a["minute"]] = k + 1
            self.clock.t = T0 + timedelta(minutes=a["minute"], seconds=k)
            self.where = f"action {i} ({a['action']})"
            self.handle(i, a)
        if self.seal is None:
            raise BuildError("script never submitted")
        return self.finish()

    def handle(self, i: int, a: dict) -> None:
        name = a["action"]
        if name in EDITOR_ACTIONS:
            return self.editor(i, a)
        getattr(self, "do_" + name)(a)

    # ---- editor actions --------------------------------------------------------------------
    def editor(self, i: int, a: dict) -> None:
        if self.rec_pos >= len(self.rec_entries):
            raise StaleRecording(f"recording is stale for {self.id}: no entry for action {i}")
        e = self.rec_entries[self.rec_pos]
        self.rec_pos += 1
        if e.get("index") != i or e.get("action") != a["action"]:
            raise StaleRecording(f"recording is stale for {self.id}: entry {e.get('index')}/"
                                 f"{e.get('action')} does not match action {i}/{a['action']}")
        self.last_editor_entry = e
        steps = e.get("steps") or []
        if e["doc_rev"] != self.rev + len(steps):
            raise BuildError(f"{self.where}: recorded doc_rev {e['doc_rev']} != "
                             f"{self.rev} + {len(steps)} steps")
        if steps:
            self.client_seq += 1
            kinds = {k: v for k, v in (e.get("input_kind") or {}).items() if v}
            token = self.lease()
            self.call("POST", f"/logs/{self.id}/batches", {
                "client_seq": self.client_seq, "base_rev": self.rev, "doc_rev": e["doc_rev"],
                "steps": steps, "input_kind": kinds, "lease_token": token})
            self.rev = e["doc_rev"]
        name = a["action"]
        if name == "insert":
            for run in a.get("runs") or []:
                kind, ref, text = run.get("kind"), run.get("ref"), run.get("text", "")
                if kind == "quote":
                    self.student("editor.insert_quote", {
                        "block_id": ref, "quote_hash": _sha(text),
                        "citation_id": "cite-" + self.blocks[ref]["source_id"]}, self.rev)
                elif kind == "helper":
                    self.student("editor.insert_helper", {
                        "helper_serve_id": ref, "text_hash": _sha(text)}, self.rev)
        elif name == "paste":
            self.student("editor.paste", {
                "paste_id": e.get("paste_id"), "size_chars": len(a["text"]),
                "kind": "external", "internal_origin": None,
                "target_from": e.get("at"), "target_to": e.get("at")}, self.rev)
        if e.get("doc") is not None:
            self.latest_doc_entry = e

    # ---- student events (HTTP) -------------------------------------------------------------
    def do_open_source(self, a):
        self.student("source.open", {"source_id": a["source_id"]})

    def do_view_blocks(self, a):
        self.student("source.view_span", {"source_id": a["source_id"],
                                          "block_ids": a["block_ids"]})

    def do_open_pin(self, a):
        self.student("aid.pin_opened", {"source_id": a["source_id"], "block_id": a["block_id"],
                                        "pin_kind": a["pin_kind"]})

    def _anchor(self, card_id: str, d: dict) -> None:
        quote = d.get("quote") or ""
        self.student("card.anchor", {"card_id": card_id, "source_id": d["source_id"],
                                     "block_id": d["block_ref"], "quote": quote,
                                     "quote_hash": _sha(quote)})

    def do_create_card(self, a):
        text, runs = _runs_from(a, self.where)
        payload = {"card_id": a["card_id"], "text": text, "origin_runs": runs,
                   "via": a.get("via", "typed")}
        if a.get("via_ref") is not None:
            payload["via_ref"] = a["via_ref"]
        self.student("card.create", payload)
        if a.get("anchor"):
            self._anchor(a["card_id"], a["anchor"])

    def do_anchor_card(self, a):
        self._anchor(a["card_id"], a)

    def _claim(self, type_: str, a: dict) -> None:
        text = a.get("text", self.claims.get(a["claim_id"]))
        if text is None:
            raise BuildError(f"{self.where}: no text for claim {a['claim_id']}")
        self.student(type_, {"claim_id": a["claim_id"], "text": text,
                             "card_ids": a.get("card_ids") or [],
                             "parent_claim_id": a.get("parent_claim_id")})

    def do_create_claim(self, a):
        self._claim("claim.create", a)

    def do_edit_claim(self, a):
        self._claim("claim.edit", a)

    def do_set_aside(self, a):
        self.student("card.set_aside", {"source_id": a["source_id"],
                                        "reason_tag": a["reason_tag"], "note": a.get("note", "")})

    def do_declare_import(self, a):
        imp = self.script["imports"][a["import_id"]]
        self.student("import.declared", {"import_id": a["import_id"],
                                         "tool_name": imp["tool_name"],
                                         "raw_text_ref": "door/" + a["import_id"],
                                         "size_chars": len(imp["text"])})

    def do_coach_outcome(self, a):
        text, runs = _runs_from(a, self.where)
        self.student("coach.outcome", {"q_id": a["q_id"], "outcome": a["outcome"],
                                       "answer_text": text, "origin_runs": runs})

    def do_map_answer(self, a):
        if a.get("answer") not in ("yes", "no"):
            raise BuildError(f"{self.where}: answer must be the string 'yes' or 'no' "
                             f"(got {a.get('answer')!r}; quote it in YAML)")
        self.student("map.answer", {"suggestion_id": a["suggestion_id"], "answer": a["answer"]})

    # ---- server-side events ----------------------------------------------------------------
    def do_extract_claim(self, a):
        self.server("claim.extracted", "system", {
            "claim_id": a["claim_id"], "from": "import", "text": a["text"],
            "artifact_id": "artifact-" + a["claim_id"], "import_id": a["import_id"]})

    def do_coach_ask(self, a):
        self.server("coach.ask", "coach", {
            "q_id": a["q_id"], "case": a["case"], "trigger_ref": a.get("trigger_ref"),
            "pillar": a["pillar"], "target_span": a.get("target_span"),
            "grounding_ids": a["grounding_ids"], "question": a["question"]})

    def do_helper_serve(self, a):
        outputs = self.script.get("helper_outputs") or {}
        if a["serve_id"] not in outputs:
            raise BuildError(f"{self.where}: no helper_outputs entry for {a['serve_id']}")
        self.server("helper.serve", "helper", {
            "helper_serve_id": a["serve_id"], "request_kind": a["request_kind"],
            "policy_id": "mechanics", "served": True, "leak_check": "pass",
            "output_hash": _sha(outputs[a["serve_id"]])})

    def do_map_suggestion(self, a):
        # The scripted mapper event has always hashed the suggestion id as its
        # synthetic output. Retain that exact body so receipt verification can
        # resolve the event's artifact without inventing a live mapper call.
        aid = "artifact-" + a["suggestion_id"]
        self.artifacts[aid] = {"artifact_id": aid, "task": "map_suggest",
                               "body": a["suggestion_id"], "hash": _sha(a["suggestion_id"])}
        e = self.need_doc("map_suggestion")
        doc = (self.latest_doc_entry or e)["doc"]
        node = _paragraph_node(doc, a["paragraph_id"])
        self.server("map.suggestion", "system", {
            "suggestion_id": a["suggestion_id"], "doc_rev": self.rev,
            "paragraph": a["paragraph_id"], "paragraph_hash": _sha(canonical_json(node).decode()),
            "claim_id": a["claim_id"], "artifact_id": "artifact-" + a["suggestion_id"],
            "output_hash": _sha(a["suggestion_id"])})

    # ---- checkpoint / submit ---------------------------------------------------------------
    def _doc_entry(self, what: str) -> dict:
        self.need_doc(what)
        return self.latest_doc_entry

    def do_checkpoint(self, a):
        e = self._doc_entry("checkpoint")
        r = self.call("POST", f"/logs/{self.id}/checkpoint", {
            "doc_rev": e["doc_rev"], "doc_hash": e["doc_hash"], "snapshot": e["doc"],
            "lease_token": self.lease()})
        if r.get("skipped"):
            self.skipped += 1

    def do_submit(self, a):
        e = self._doc_entry("submit")
        r = self.call("POST", f"/logs/{self.id}/submit", {
            "idempotency_key": "golden-" + self.id, "doc_rev": e["doc_rev"],
            "doc_hash": e["doc_hash"], "snapshot": e["doc"], "lease_token": self.lease()})
        self.seal, self.seal_seq = r["seal"], r["seal_seq"]

    # ---- after submit ----------------------------------------------------------------------
    def finish(self) -> BuildResult:
        events = self.svc.events(self.id)
        latest: dict = {}
        for ev in events:
            if ev["type"] == "coach.outcome":
                latest[ev["payload"]["q_id"]] = ev["payload"]
        sources = InMemorySources(
            blocks={k: b["text"] for k, b in self.blocks.items()},
            coach={q: coach_answer_from_runs(p["answer_text"], p["origin_runs"])
                   for q, p in latest.items()},
            imports={k: v["text"] for k, v in (self.script.get("imports") or {}).items()},
            helper=dict(self.script.get("helper_outputs") or {}))
        result = compile_marks(events, load_snapshot_fn(self.svc, self.id), sources)
        l1 = l1_from_compile(result, events,
                             block_kinds={k: b["kind"] for k, b in self.blocks.items()})
        self.where = "verify"
        verify = self.call("GET", f"/logs/{self.id}/verify")
        if not verify.get("ok"):
            raise BuildError(f"verify failed: {verify}")
        # Pin only the commit component: the stamp still fingerprints the actual lock,
        # editor pair and prompt. Fixture expectations never depend on the checkout SHA.
        stamp = build_stamp(git_sha="golden-fixtures-v1")
        receipt, _ = issue_receipt(
            self.svc, self.id, sources, ask=self.ask, stamp=stamp,
            block_kinds={k: b["kind"] for k, b in self.blocks.items()})
        return BuildResult(self.id, events, self.seal, self.seal_seq, result.to_json(), l1,
                           self.skipped, verify, receipt.receipt, {**self.artifacts, **receipt.artifacts},
                           receipt.receipt_hash, self.svc.events(self.id), stamp,
                           result.replay.doc, sources)


def load_recording(session_id: str) -> dict:
    with open(RECORDED_DIR / f"{session_id}.json", encoding="utf-8") as f:
        return json.load(f)


def build_session(session_id: str, *, recording: dict | None = None,
                  script: dict | None = None, ask=llm_ask) -> BuildResult:
    if os.environ.get("ROOM_LLM") != "stub":
        raise BuildError("golden sessions require ROOM_LLM=stub; live calls are not allowed")
    script = load_script(session_id) if script is None else script
    if recording is None:
        recording = load_recording(session_id)
    if recording.get("editor_actions_sha256") != editor_actions_sha256(script):
        raise StaleRecording(f"recording is stale for {session_id}: rerun "
                             f"`node golden/record.mjs {session_id}` from prototype/web")
    builder = _Builder(session_id, script, recording, ask=ask)
    try:
        return builder.run()
    finally:
        # TestClient is deliberately not entered: entering starts the app's LLM
        # boot ping. Close its transport and the in-memory SQLite service ourselves.
        if builder.client is not None:
            builder.client.close()
        if builder.svc is not None:
            builder.svc.close()
