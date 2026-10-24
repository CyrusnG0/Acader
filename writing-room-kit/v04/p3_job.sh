#!/bin/bash
# one P3 relay job: p3_job.sh ID STYLE [extra relay args]; one rerun on failure (PREREG-v0.5 B.4)
cd /Users/micmic/Documents/GitHub/Acader/writing-room-kit
export ROOM_RUNS_DIR=v04/runs-v05 ROOM_SESSIONS_DIR=v04/sessions-v05 ROOM_RUN_ID=$1
id=$1; style=$2; shift 2
for attempt in 1 2; do
  [ -f v04/runs-v05/$id.json ] && break
  rm -f v04/sessions-v05/$id.json
  python3 v04/relay.py $id --style $style "$@" >> v04/runs-v05/_$id.log 2>&1
done
