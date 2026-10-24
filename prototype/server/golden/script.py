"""Load and validate the golden session scripts (fixtures/README.md, "Executable golden sessions")."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

from engine.events import canonical_json, sha256_hex

GOLDEN_DIR = Path(__file__).resolve().parents[2] / "fixtures" / "golden"
RECORDED_DIR = GOLDEN_DIR / "recorded"

EDITOR_ACTIONS = frozenset({"type_paragraph", "type", "insert", "paste", "replace", "delete",
                            "link", "accept_suggestion"})
OTHER_ACTIONS = frozenset({"open_source", "view_blocks", "open_pin", "create_card", "anchor_card",
                           "create_claim", "edit_claim", "set_aside", "declare_import",
                           "extract_claim", "coach_ask", "coach_outcome", "helper_serve",
                           "map_suggestion", "map_answer", "checkpoint", "submit"})
KNOWN_ACTIONS = EDITOR_ACTIONS | OTHER_ACTIONS


class ScriptError(ValueError):
    pass


def load_blocks() -> dict:
    with open(GOLDEN_DIR / "blocks.json", encoding="utf-8") as f:
        return json.load(f)["blocks"]


def load_sources() -> dict:
    """Read the local source manifest; URLs are metadata and are never fetched."""
    with open(GOLDEN_DIR.parent / "sources.yaml", encoding="utf-8") as f:
        manifest = yaml.safe_load(f)
    if not isinstance(manifest, dict) or not isinstance(manifest.get("sources"), list):
        raise ScriptError("source manifest must contain a sources list")
    sources = {}
    for source in manifest["sources"]:
        if not isinstance(source, dict) or not isinstance(source.get("id"), str):
            raise ScriptError("source manifest entry needs a string id")
        sid = source["id"]
        if sid in sources:
            raise ScriptError(f"duplicate source in manifest: {sid}")
        if not isinstance(source.get("title"), str) or not source["title"].strip():
            raise ScriptError(f"source {sid} needs a title")
        if not isinstance(source.get("content_url"), str) or not source["content_url"].strip():
            raise ScriptError(f"source {sid} needs a content_url")
        sources[sid] = source
    return sources


def source_metadata(script: dict) -> list[dict]:
    """Resolve declared fixture sources, retaining the script's deterministic order."""
    ids = script.get("source_ids", [])
    if not isinstance(ids, list) or any(not isinstance(sid, str) for sid in ids):
        raise ScriptError("source_ids must be a list of strings")
    if len(ids) != len(set(ids)):
        raise ScriptError("duplicate source_ids")
    sources = load_sources()
    missing = [sid for sid in ids if sid not in sources]
    if missing:
        raise ScriptError(f"unknown source_ids: {missing}")
    return [sources[sid] for sid in ids]


def list_sessions() -> list[str]:
    return sorted(p.stem for p in GOLDEN_DIR.glob("*.yaml"))


def validate_script(script: dict, session_id: str, blocks: dict | None = None) -> None:
    blocks = load_blocks() if blocks is None else blocks
    if not isinstance(script, dict):
        raise ScriptError(f"{session_id}: script is not a mapping")
    if script.get("schema_version") != 1:
        raise ScriptError(f"{session_id}: schema_version must be 1")
    if script.get("session_id") != session_id:
        raise ScriptError(f"{session_id}: session_id {script.get('session_id')!r} != file name")
    if "mapper_enabled" in script and not isinstance(script["mapper_enabled"], bool):
        raise ScriptError(f"{session_id}: mapper_enabled must be a bool")
    source_metadata(script)
    actions = script.get("actions")
    if not isinstance(actions, list) or not actions:
        raise ScriptError(f"{session_id}: actions must be a non-empty list")
    last_minute = 0
    for i, a in enumerate(actions):
        where = f"{session_id} action {i}"
        if not isinstance(a, dict):
            raise ScriptError(f"{where}: not a mapping")
        m = a.get("minute")
        if isinstance(m, bool) or not isinstance(m, int) or m < 0:
            raise ScriptError(f"{where}: minute must be an int >= 0")
        if m < last_minute:
            raise ScriptError(f"{where}: minute {m} goes back before {last_minute}")
        last_minute = m
        name = a.get("action")
        if name not in KNOWN_ACTIONS:
            raise ScriptError(f"{where}: unknown action {name!r}")
        if name == "insert":
            for run in a.get("runs") or []:
                if run.get("kind") != "quote":
                    continue
                ref = run.get("ref")
                if ref not in blocks:
                    raise ScriptError(f"{where}: quote run references unknown block {ref!r}")
                text = run.get("text")
                if run.get("forged") is True:
                    continue
                if not text or text not in blocks[ref]["text"]:
                    raise ScriptError(
                        f"{where}: quote text is not an exact substring of block {ref}: {text!r}")
    subs = [i for i, a in enumerate(actions) if a["action"] == "submit"]
    if len(subs) != 1 or subs[0] != len(actions) - 1:
        raise ScriptError(f"{session_id}: submit must appear exactly once, as the last action")


def load_script(session_id: str) -> dict:
    path = GOLDEN_DIR / f"{session_id}.yaml"
    try:
        with open(path, encoding="utf-8") as f:
            script = yaml.safe_load(f)
    except OSError as e:
        raise ScriptError(f"cannot read {path}: {e}") from e
    validate_script(script, session_id)
    return script


def editor_actions(script: dict) -> list[dict]:
    return [{"index": i, **a} for i, a in enumerate(script["actions"])
            if a["action"] in EDITOR_ACTIONS]


def editor_actions_sha256(script: dict) -> str:
    return sha256_hex(canonical_json(editor_actions(script)))


def main_actions(session_id: str) -> int:
    script = load_script(session_id)
    print(json.dumps({"session_id": session_id,
                      "editor_actions_sha256": editor_actions_sha256(script),
                      "actions": editor_actions(script)}, ensure_ascii=False))
    return 0
