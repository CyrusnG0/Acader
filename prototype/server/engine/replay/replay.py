"""Python replay of editor steps (event-log.md §5, D6, D33).

`load_schema()` builds a prosemirror-py Schema from web/schema.json, turning
every `enum` list into a validate check (as web/src/schema.ts does), so a mark
outside the closed list fails here too. `replay_steps()` applies the recorded
step JSON in order. The step log holds only step types both replays know
(replace, replaceAround, addMark, removeMark, ...); the editor flattens
prosemirror-transform's `markSet` before recording (spike S1).
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from prosemirror.model import Node, Schema
from prosemirror.transform import Step

from engine.events.canonical import canonical_json, sha256_hex

SCHEMA_PATH = Path(__file__).resolve().parents[3] / "web" / "schema.json"

_TYPES = {"string": str, "null": type(None), "number": int, "boolean": bool}


class ReplayError(ValueError):
    """A step failed to load or apply, or the result is not a valid document."""


def _validator(where: str, validate: str | None, allowed: list | None):
    def check(value):
        if validate is not None:
            kinds = validate.split("|")
            ok = any(
                isinstance(value, _TYPES[k]) and not (k == "number" and isinstance(value, bool))
                for k in kinds
            )
            if not ok:
                raise ValueError(f"Expected {validate} for {where}, got {type(value).__name__}")
        if allowed is not None and value not in allowed:
            raise ValueError(f"{where} must be one of {', '.join(map(str, allowed))}, got {value}")
    return check


def _map_specs(specs: dict) -> dict:
    out = {}
    for name, spec in specs.items():
        spec = dict(spec)
        attrs = spec.pop("attrs", None)
        if attrs:
            spec["attrs"] = {}
            for attr, a in attrs.items():
                a_out = {}
                if "default" in a:
                    a_out["default"] = a["default"]
                if "validate" in a or "enum" in a:
                    a_out["validate"] = _validator(f"{name}.{attr}", a.get("validate"), a.get("enum"))
                spec["attrs"][attr] = a_out
        out[name] = spec
    return out


def build_schema(spec: dict) -> Schema:
    return Schema({
        "topNode": spec.get("topNode"),
        "nodes": _map_specs(spec["nodes"]),
        "marks": _map_specs(spec["marks"]),
    })


@lru_cache(maxsize=1)
def load_schema() -> Schema:
    return build_schema(json.loads(SCHEMA_PATH.read_text(encoding="utf-8")))


def replay_steps(start: dict, steps: list[dict], schema: Schema | None = None) -> Node:
    schema = schema or load_schema()
    try:
        doc = Node.from_json(schema, start)
        doc.check()
    except Exception as e:  # prosemirror-py raises ValueError and friends
        raise ReplayError(f"start doc: {e}") from e
    for i, step_json in enumerate(steps):
        try:
            result = Step.from_json(schema, step_json).apply(doc)
        except Exception as e:
            raise ReplayError(f"step {i}: {e}") from e
        if result.failed or result.doc is None:
            raise ReplayError(f"step {i}: {result.failed}")
        doc = result.doc
    try:
        doc.check()
    except Exception as e:
        raise ReplayError(f"result: {e}") from e
    return doc


def doc_hash(doc: Node | dict) -> str:
    """sha256 of the canonical JSON of the document (same bytes as web/src/editor/canonical.ts)."""
    as_json = doc.to_json() if isinstance(doc, Node) else doc
    return sha256_hex(canonical_json(as_json))
