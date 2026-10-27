#!/usr/bin/env bash
# Compass chat-slice v2-fresh confirm (BAR.md): 1 b4gate run + 1 main reference, chat-slice-base-s42 profile
# (Android 12 GB, qwen3-4b, seed 42, node backend, multi-turn). Outputs only under the restricted v1-fresh/runs/.
# The mini's copies (requests carry item texts) are deleted after fetch. Prints only aggregate lines.
set -uo pipefail
B=<workspace>; E=$B/boar-eval; V=$B/rnd/research/compass/chat-slice/v2-fresh; OUT=$V/runs
export HEAVY_CLASS=normal
( cd $V && shasum -a 256 -c FROZEN.sha256 2>/dev/null | grep -v ': OK$' ) && { echo "FREEZE CHECK FAILED"; exit 1; }
run() { # label arm runnerdir tree
  local label="$1" arm="$2" rd="$3" tree="$4" d="$OUT/$1"; mkdir -p "$d"
  python3 -c "import json; c=json.load(open('$E/runs/kiln/chat-slice-base-s42/config.json')); c['arm']='$arm'; c['seed']=42; json.dump(c, open('$d/config.json','w'))"
  pnpm -s -C $E/packages/protocol exec tsx src/makeRequests.ts --questions $V/slice.v2.jsonl --config $d/config.json --run-id "kiln-v2-$label" > $d/requests.jsonl 2>/dev/null
  BOAR_EVAL_RUNNER_DIR=$rd $E/adapters/desktop-node/run.sh --commit 0cfd4a77 --arm $arm --requests $d/requests.jsonl --out $d/traces.jsonl > $d/runsh.out 2>&1
  echo "$label rc=$? $(date +%H:%M)"
  <on the mini> "rm -rf <runner>/kiln/$tree/$rd/runs/kiln-v2-$label"
  python3 $V/score_l0.frozen.py --slice $V/slice.v2.jsonl --traces $d/traces.jsonl --json $d/score.json > $d/score.txt 2>&1
  head -1 $d/score.txt; grep '^ALL' $d/score.txt
}
run b6gate b6gate be-b6gate be-0cfd4a77-b6gate
run main main be-kiln be-0cfd4a77
echo V2-CONFIRM-DONE
