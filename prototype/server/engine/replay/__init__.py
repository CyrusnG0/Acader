"""replay/: rebuild a document from its recorded editor steps with prosemirror-py.

Loads the same `web/schema.json` as the browser editor (D33), replays the
steps the editor recorded, and computes the `doc_hash` the client sends at
each checkpoint (event-log.md §5, D6). Spike S1 showed both replays give the
same document and marks (prototype/spikes/S1/RESULT.md).
"""
from .replay import ReplayError, doc_hash, load_schema, replay_steps

__all__ = ["ReplayError", "doc_hash", "load_schema", "replay_steps"]
