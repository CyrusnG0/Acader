"""Compile: replay check, then the mark check on the document that comes out of it."""
from __future__ import annotations

from dataclasses import dataclass

from engine.events import canonical_json
from engine.replay import EMPTY_DOC, ReplayReport, check_replay, doc_hash

from .markcheck import RunCheck, check_marks
from .sources import ProvenanceSources


@dataclass(frozen=True)
class CompileResult:
    status: str
    replay: ReplayReport
    runs: tuple[RunCheck, ...]

    def to_json(self) -> dict:
        out = {
            "status": self.status,
            "built_from": self.replay.built_from,
            "doc_rev": self.replay.doc_rev,
            "doc_hash": doc_hash(self.replay.doc),
            "seal_seq": self.replay.seal_seq,
            "checkpoints": [c.to_json() for c in self.replay.checkpoints],
            "runs": [r.to_json() for r in self.runs],
            "unconfirmed": sum(1 for r in self.runs if not r.confirmed),
        }
        canonical_json(out)
        return out


def compile_marks(events, load_snapshot, sources: ProvenanceSources, *, seal_seq=None,
                  initial_doc=EMPTY_DOC) -> CompileResult:
    report = check_replay(events, load_snapshot, seal_seq=seal_seq, initial_doc=initial_doc)
    runs = tuple(check_marks(report.doc, sources))
    status = "replay_mismatch" if report.status == "replay_mismatch" else "complete"
    return CompileResult(status, report, runs)


def operator_alerts(result: CompileResult, log_id: str) -> list[dict]:
    return [{"kind": "replay_mismatch", "log_id": log_id, "seq": c.seq, "doc_rev": c.doc_rev,
             "reason": c.reason, "client_hash": c.client_hash, "replayed_hash": c.replayed_hash}
            for c in result.replay.checkpoints if not c.ok]
