# Session JSON schema (v0.2, two task families)

score.js routes by the `task` field: anything containing "matrix" uses Matrix Lab scoring, everything else uses Writing Room scoring.

## Writing Room (essay)
```json
{
  "version": "0.2", "session_id": "any-string", "created": "ISO date", "task": "URBP3010-w9-essay",
  "notes": "scratchpad text",
  "essay": "full essay text",
  "queries":    [ {"text": "question asked", "ts": 1} ],
  "retrievals": ["D1p1", "D6p4"],
  "hooks":      [ {"passage": "D6p4", "pos": 520} ],
  "pasteChars": 0, "editBursts": 14,
  "hinge": {"expectedPassage": "D10p3", "keywords": ["enforcement", "inspection"]}
}
```
`hinge` is OPTIONAL (professor-set). If present and the passage was never retrieved, or the keywords are absent from the essay, flags are raised.

## Matrix Lab (black-box)
```json
{
  "version": "0.2", "session_id": "any-string", "created": "ISO date", "task": "MATH2010-w3-matrix",
  "b": [3,4,5], "budget": 4,
  "probes": [ {"x": [1,0,0], "predicted": [2,1,0], "actual": [2,1,0]} ],
  "explanation": "the final answer + reasoning", "notes": ""
}
```
Engine rules: a hook is verified only if its passage is in `retrievals`; pasteChars>=300 raises a flag; 1-burst long essays raise a flag; continuity compares essay vocabulary with queries+retrieved passages; `pos` is clamped to essay length, so hooks placed beyond the essay collapse the spread score.
