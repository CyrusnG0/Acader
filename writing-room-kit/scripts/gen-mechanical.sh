#!/bin/sh
# A5 (outside-coached) and A6 (outsourced floor): fully mechanical runs. usage: sh scripts/gen-mechanical.sh <first> <last>
cd "$(dirname "$0")/.." || exit 1
for n in $(seq "$1" "$2"); do
  # A5
  rm -f work/A5-$n.draft.json
  python3 scripts/outside.py coach work/A5-$n.coach.txt >/dev/null
  while IFS= read -r q; do [ -n "$q" ] && node scripts/librarian.js work/A5-$n.draft.json "$q" --id A5-$n >/dev/null; done < work/A5-$n.coach.txt
  python3 scripts/outside.py write work/A5-$n.draft.json work/A5-$n.txt >/dev/null
  node scripts/finalize.js work/A5-$n.draft.json --essay work/A5-$n.txt --arm A5 --n $n --struct retyped --writer deepseek-chat
  # A6
  echo '{"version":"0.1","task":"URBP3010-w9-essay","notes":"","queries":[],"retrievals":[],"hooks":[],"essay":""}' > work/A6-$n.draft.json
  python3 scripts/outside.py bare work/A6-$n.txt >/dev/null
  node scripts/finalize.js work/A6-$n.draft.json --essay work/A6-$n.txt --arm A6 --n $n --struct pasted --writer deepseek-chat
done
