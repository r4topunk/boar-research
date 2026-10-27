#!/bin/bash
# CROWDQ step 3: Haiku 5.5-low L1, N=4 shards, both orders, per pack (= arms/packs/tools/score_selftest.sh judge half; 40 calls/pack, 360 total).
# Fail-closed: shard_judge.sh rc + _lib/check_judgments.py; floor_metrics --strict -> aggregates/<run>.floor_metrics.txt. Skips packs already checked ok.
set -u
H=$(cd "$(dirname "$0")/.." && pwd); R=$H/runs; A=$H/aggregates; L=$H/../_lib
for p in qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en; do
  run=st-$p-cut7-all9-s42
  python3 -I -c "import json,sys;[print(json.loads(l)['itemId']) for l in open(sys.argv[1])]" "$R/$run.traces.jsonl" > "$R/$run.ids"
  if python3 -I "$L/check_judgments.py" "$R/$run.judgments.jsonl" "$R/$run.ids" >/dev/null 2>&1; then echo "$(date +%T) skip $p (judged)"; continue; fi
  echo "$(date +%T) judge $p"
  bash "$H/../deepthink/tools/shard_judge.sh" "$R/$run.traces.jsonl" "$R/$run.judgments.jsonl" <workspace>/boar-eval/bench/selftest/$p "$R/$run.ids" selftest-$p-cut7-all9 4 haiku || { echo "judge FAIL $p"; exit 1; }
  python3 -I "$L/check_judgments.py" "$R/$run.judgments.jsonl" "$R/$run.ids" "$run" || exit 1
  python3 <workspace>/boar-eval/bench/v0.2/plan/floor_metrics.py --runs "$run" --dir "$R" --ids "$R/$run.ids" --strict > "$A/$run.floor_metrics.txt" || { echo "floor_metrics FAIL $p"; exit 1; }
done
echo "$(date +%T) judge chain complete; judgment rows: $(cat "$R"/*.judgments.jsonl | wc -l)"
