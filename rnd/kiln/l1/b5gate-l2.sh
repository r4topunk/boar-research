#!/usr/bin/env bash
# Anvil's b5gate L2 (criterion FROZEN in rnd/research/anvil/exp/chat-routing/arm/README.md, original, not amended):
# v0.1 72 items (ios8 requests), ios8 4B profile (--installed 1.5B+4B, ios 8 GB), node backend, 2 reps (s42/s43),
# arm vs same-tree control (BOAR_ROUTE_GATE=0), interleaved per seed; judge.v1 opus both orders on every run.
set -uo pipefail
E=<workspace>/boar-eval; OUT=$E/runs/kiln/b5gate/l2; mkdir -p $OUT
export BOAR_EVAL_RUNNER_DIR=be-b5gate HEAVY_CLASS=normal
INST=(--installed qwen2.5-1.5b-instruct-q4km,qwen3-4b-instruct-2507-q4km)
jobs_j=()
for seed in 42 43; do
  for side in arm ctl; do
    label=$side-s$seed
    python3 - "$E/runs/ios8/ios8-s$seed.requests.jsonl" "$OUT/$label.requests.jsonl" "kiln-b5gate-l2-$label" <<'PY'
import json, sys
rows = [json.loads(l) for l in open(sys.argv[1])]
for r in rows: r["runId"] = sys.argv[3]; r["config"]["arm"] = "b5gate"
open(sys.argv[2], "w").write("".join(json.dumps(r) + "\n" for r in rows))
PY
    if [ $side = ctl ]; then G=0; else G=; fi
    BOAR_ROUTE_GATE=$G $E/adapters/desktop-node/run.sh --commit 0cfd4a77 --arm b5gate --requests $OUT/$label.requests.jsonl --out $OUT/$label.traces.jsonl "${INST[@]}" > $OUT/$label.runsh.out 2>&1
    echo "$label rc=$? $(date +%H:%M)"
    (cd $E && node harness/judge.mjs --traces $OUT/$label.traces.jsonl --out $OUT/$label.judgments.jsonl --bench bench/v0.1 --system b5gate-$label > $OUT/$label.judge.log 2>&1; echo "judge $label rc=$? $(date +%H:%M)") &
    jobs_j+=($!)
  done
done
for p in "${jobs_j[@]}"; do wait $p; done
echo B5GATE-L2-RUNS-JUDGED
