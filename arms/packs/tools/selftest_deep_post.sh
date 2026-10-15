#!/bin/bash
# SELFTEST-DEEP post-processing for one run: fetch (arm.sh, fail closed) -> gen checks (selftest_agg.py) -> thinking stats -> Haiku 5.5-low N=4 both orders -> floor_metrics --strict.
# Usage: selftest_deep_post.sh <pack> [--no-pack]     Outputs in ../selftest-runs/deep/, aggregates in ../aggregates/. Skips steps whose output exists.
set -eu
P=$1; NP=${2:-}; H=$(cd "$(dirname "$0")/.." && pwd); D=$H/selftest-runs/deep; A=$H/aggregates; C=$H/tools/selftest-deep.conf; ARM=$H/../_lib/arm.sh
R=st-$P-dt512${NP:+-nopack}-s42
[ -s "$D/$R.traces.jsonl" ] || bash "$ARM" "$C" fetch "$R" "$D/$R.traces.jsonl" "$D/$R.requests.jsonl"
python3 -I "$H/tools/selftest_agg.py" "$P" "$D/$R.traces.jsonl" --json "$A/$R.gen.json" | tail -1
bash "$ARM" "$C" think "$D/$R.traces.jsonl" "" "$A/$R.think.json"
python3 -I -c "import json,sys;[print(json.loads(l)['itemId']) for l in open(sys.argv[1])]" "$D/$R.traces.jsonl" > "$D/$R.ids"
[ "$(wc -l < "$D/$R.ids")" -eq 20 ] || { echo "ABORT $R: $(wc -l < "$D/$R.ids") traces"; exit 3; }
if ! python3 "$H/../_lib/check_judgments.py" "$D/$R.judgments.jsonl" "$D/$R.ids" >/dev/null 2>&1; then
  bash "$H/../deepthink/tools/shard_judge.sh" "$D/$R.traces.jsonl" "$D/$R.judgments.jsonl" $BOAR_WS/boar-eval/bench/selftest/$P "$D/$R.ids" selftest-$P-dt512 4 haiku; fi
python3 $BOAR_WS/boar-eval/bench/v0.2/plan/floor_metrics.py --runs "$R" --dir "$D" --ids "$D/$R.ids" --strict | tee "$A/$R.floor_metrics.txt" | tail -3
