#!/bin/bash
# PACK-VISA copy of arms/packs/tools/score_selftest.sh (paths -> arms/pack-visa; same steps): convert -> 4B cut 7 generation (MacBook)
# -> gen checks -> Haiku 5.5-low L1 (N=4, both orders, 40 calls) -> floor_metrics.
# Usage: score_selftest.sh <pack> [seed=42] [--no-pack]
set -eu -o pipefail
P=$1; SEED=${2:-42}; NP=${3:-}; H=<workspace>/rnd/research/coordinator/arms/pack-visa; D=$H/selftest-runs; A=$H/aggregates; mkdir -p "$A" "$D"
R=st-$P-cut7${NP:+-nopack}-s$SEED
python3 -I "$H/tools/selftest_to_bench.py" "$P" --seed "$SEED" $NP
[ -s "$D/$R.traces.jsonl" ] || "$H/tools/run_selftest.sh" "$D/$R.requests.jsonl" "$D/$R.traces.jsonl"
python3 -I "$H/tools/selftest_agg.py" "$P" "$D/$R.traces.jsonl" --json "$A/$R.gen.json" | tail -1
python3 -I -c "import json,sys;[print(json.loads(l)['itemId']) for l in open(sys.argv[1])]" "$D/$R.traces.jsonl" > "$D/$R.ids"
bash <workspace>/rnd/research/coordinator/arms/deepthink/tools/shard_judge.sh "$D/$R.traces.jsonl" "$D/$R.judgments.jsonl" <workspace>/boar-eval/bench/selftest/$P "$D/$R.ids" selftest-$P-cut7 4 haiku
python3 <workspace>/boar-eval/bench/v0.2/plan/floor_metrics.py --runs "$R" --dir "$D" --ids "$D/$R.ids" --strict | tee "$A/$R.floor_metrics.txt"
