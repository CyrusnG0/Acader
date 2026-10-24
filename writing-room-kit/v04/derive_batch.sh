#!/bin/bash
# retries derive.py per run file (derive.py is frozen; transient empty model output is retried here, not in the code)
cd /Users/micmic/Documents/GitHub/Acader/writing-room-kit
for f in "$@"; do
  id=$(basename $f .json)
  for attempt in 1 2 3; do
    [ -f v04/reports-v05/$id.derive.json ] && break
    python3 v04/derive.py $f 2>&1 | tail -1
  done
done
