#!/bin/bash
# STACK-2 judge (criterion sha e875d463…): Haiku 5.5-low L1, N=4 shards, both orders = arms/crowdq/tools/judge_all9.sh pattern.
# 9 self-test runs (bench boar-eval/bench/selftest/<pack>, 40 calls each = 360) + v0.1 OFF/ON (bench boar-eval/bench/v0.1, 120 each = 240).
# Pipelined: waits until a run's traces status is DONE. Fail-closed: shard_judge.sh rc + _lib/check_judgments.py + floor_metrics --strict.
# Skips runs already checked ok. Usage: nohup tools/judge_stack.sh >> runs/judge.log 2>&1 &
set -u
H=$(cd "$(dirname "$0")/.." && pwd); R=$H/runs; A=$H/aggregates; L=$H/../_lib; B=<workspace>/boar-eval/bench
RUNS=(); for p in qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en; do RUNS+=("st-$p-cut7-stack-s42|$B/selftest/$p"); done
RUNS+=("v01-cut7-stack-off-s42|$B/v0.1" "v01-cut7-stack-on-s42|$B/v0.1")
for x in "${RUNS[@]}"; do
  run=${x%%|*}; bench=${x#*|}
  until [ "$(tail -1 "$R/$run.traces.status" 2>/dev/null)" = DONE ]; do
    case "$(tail -1 "$R/$run.traces.status" 2>/dev/null)" in FAIL*) echo "$(date +%T) generation FAIL $run: stop"; exit 1;; esac; sleep 30; done
  # ids = the run's trace ids minus the bench's venue-list items (judge.mjs never judges them: v0.1 food-001/002/006 -> 57 judged)
  python3 -I -c "import json,sys,os;q=sys.argv[2]+'/questions.public.jsonl';v={d['id'] for d in map(json.loads,open(q)) if (d.get('grading') or {}).get('type')=='venue-list'} if os.path.exists(q) else set();[print(i) for i in (json.loads(l)['itemId'] for l in open(sys.argv[1])) if i not in v]" "$R/$run.traces.jsonl" "$bench" > "$R/$run.ids"
  if python3 -I "$L/check_judgments.py" "$R/$run.judgments.jsonl" "$R/$run.ids" >/dev/null 2>&1; then echo "$(date +%T) skip $run (judged)"; continue; fi
  echo "$(date +%T) judge $run"
  bash "$H/../deepthink/tools/shard_judge.sh" "$R/$run.traces.jsonl" "$R/$run.judgments.jsonl" "$bench" "$R/$run.ids" "$run" 4 haiku || { echo "judge FAIL $run"; exit 1; }
  python3 -I "$L/check_judgments.py" "$R/$run.judgments.jsonl" "$R/$run.ids" "$run" || exit 1
  python3 $B/v0.2/plan/floor_metrics.py --runs "$run" --dir "$R" --ids "$R/$run.ids" --strict > "$A/$run.floor_metrics.txt" || { echo "floor_metrics FAIL $run"; exit 1; }
done
echo "$(date +%T) judge chain complete; judgment rows: $(cat "$R"/*.judgments.jsonl | wc -l)"
