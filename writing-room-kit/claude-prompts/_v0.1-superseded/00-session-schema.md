# Session JSON schema (v0.1)

Every simulated student must output EXACTLY this object, nothing else.

```json
{
  "version": "0.1",
  "session_id": "any-string",
  "created": "2026-10-16T09:00:00Z",
  "task": "URBP3010-w9-essay",
  "notes": "scratchpad text (may be empty)",
  "essay": "the full essay text",
  "queries":  [ {"text": "the question asked", "mark": "FACT|DEEP|BROAD|CONCLUSION|MISS (optional, engine re-classifies)", "ts": 1} ],
  "retrievals": ["D1p1", "D6p4"],        // passage ids the student obtained, in order
  "hooks":     [ {"passage": "D6p4", "pos": 520} ],   // citations anchored in the essay
  "pasteChars": 0,                        // characters pasted into the editor
  "editBursts": 14                        // distinct writing bursts (typing sessions)
}
```

Rules the engine enforces mechanically:
- a hook is VERIFIED only if its `passage` is also in `retrievals`;
- `pasteChars >= 300` raises a structure flag; `editBursts <= 1` with a long essay raises one;
- continuity compares essay vocabulary against queries + retrieved passages.
