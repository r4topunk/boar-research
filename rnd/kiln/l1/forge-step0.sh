#!/usr/bin/env bash
# Forge job 1, desktop step 0 (p8-step0 recipe): g75-matched profile, v0.1 72 items, s42, --event-source-text, current packs.
# base 0cfd4a77 (main~g75) | arm forge flags OFF | arm forge flags ON (vectorCache,sqlBatch,nativeZstd -> fzstd fallback in Node).
set -uo pipefail
E=<workspace>/boar-eval; OUT=$E/runs/kiln/forge
export BOAR_EVAL_RUNNER_DIR=be-kiln HEAVY_CLASS=normal BOAR_EVAL_SQL_COUNT=1
mk() { python3 - "$1" "$2" "$3" <<'PY'
import json, sys
src, arm, run = sys.argv[1:]
rows = [json.loads(l) for l in open("<workspace>/boar-eval/runs/p8/base-s42-kic.requests.jsonl")]
for r in rows: r["runId"] = run; r["config"]["arm"] = arm
open(src, "w").write("".join(json.dumps(r) + "\n" for r in rows))
PY
}
run() { # label arm tree-arm [env]
  local label="$1" arm="$2" tarm="$3"; mk $OUT/$label.requests.jsonl "$arm" "forge-$label-s42"
  env ${4:-} $E/adapters/desktop-node/run.sh --commit 0cfd4a77 --arm "$tarm" --requests $OUT/$label.requests.jsonl --out $OUT/$label.traces.jsonl --event-source-text > $OUT/$label.runsh.out 2>&1
  echo "$label rc=$? $(date +%H:%M)"
}
run base main~g75 main
run arm-off forge forge
run arm-on forge forge EXPO_PUBLIC_BOAR_PERF=vectorCache,sqlBatch,nativeZstd
python3 <workspace>/rnd/kiln/l1/forge-compare.py $OUT
echo FORGE-STEP0-DONE
