"""Canonical JSON and hashing for the event chain (event-log.md §3).

Canonical JSON: UTF-8 (no ASCII escaping), sorted keys, no whitespace, no floats.
"""
import hashlib
import json


class CanonicalError(ValueError):
    """The value cannot be put in the chain (a float, or a non-JSON type)."""


def _check(value, path="$"):
    if isinstance(value, bool) or value is None or isinstance(value, (int, str)):
        return
    if isinstance(value, float):
        raise CanonicalError(f"float not allowed in the chain at {path}")
    if isinstance(value, dict):
        for k, v in value.items():
            if not isinstance(k, str):
                raise CanonicalError(f"non-string key at {path}")
            _check(v, f"{path}.{k}")
        return
    if isinstance(value, list):
        for i, v in enumerate(value):
            _check(v, f"{path}[{i}]")
        return
    raise CanonicalError(f"type {type(value).__name__} not allowed at {path}")


def canonical_json(value) -> bytes:
    _check(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
