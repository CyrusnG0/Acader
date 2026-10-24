"""replay/: rebuild a document from its recorded editor steps with prosemirror-py.

Loads the same `web/schema.json` as the browser editor (D33), replays the
steps the editor recorded, and computes the `doc_hash` the client sends at
each checkpoint (event-log.md §5, D6). Spike S1 showed both replays give the
same document and marks (prototype/spikes/S1/RESULT.md).
"""
from .replay import ALLOWED_STEP_TYPES, ReplayError, doc_hash, load_schema, replay_steps
from .rebuild import (EMPTY_DOC, CheckpointCheck, ReplayReport, SnapshotLoader, check_replay,
                      rebuild_at, step_segments, steps_between)

__all__ = ["ALLOWED_STEP_TYPES", "ReplayError", "doc_hash", "load_schema", "replay_steps",
           "EMPTY_DOC", "CheckpointCheck", "ReplayReport", "SnapshotLoader", "check_replay",
           "rebuild_at", "step_segments", "steps_between"]
