#!/bin/bash
# SELFTEST-LOCALJUDGE generation driver (MacBook, sequential): with-pack traces for the wave-2 packs + the 9 no-pack controls.
# Usage: gen_localjudge.sh   (skips runs whose traces already exist with a DONE status)
H=$(cd "$(dirname "$0")/.." && pwd); D=$H/selftest-runs
RUNS="boar-factbook: boar-simplewiki-en:"
for p in qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en; do RUNS="$RUNS $p:--no-pack"; done
for x in $RUNS; do P=${x%%:*}; NP=${x#*:}; R=st-$P-cut7${NP:+-nopack}-s42
  if [ -s "$D/$R.traces.jsonl" ] && grep -q DONE "$D/$R.traces.status" 2>/dev/null; then echo "skip $R"; continue; fi
  python3 -I "$H/tools/selftest_to_bench.py" "$P" --seed 42 $NP
  rm -f "$D/$R.traces.jsonl"; "$H/tools/run_selftest.sh" "$D/$R.requests.jsonl" "$D/$R.traces.jsonl"; echo "$R rc=$? $(date '+%T')"
  python3 -I -c "import json,sys;[print(json.loads(l)['itemId']) for l in open(sys.argv[1])]" "$D/$R.traces.jsonl" > "$D/$R.ids"
done; echo ALLDONE
