#!/usr/bin/env bash
# Compass's chat-line arm b6chatline (75456159…c044), criteria .../replylang/chatline/CRITERIA.md. 1 rep each, node, multi-turn.
# (1) arm on chat-slice v0+v1+v2 (192) × 4B (chat-slice-base-s42) + 1.5B (p2-iphone13) × s42 + s43;
# (2) s43 references = b6precedence on all 192 × both models. v1/v2 outputs restricted; mini copies of v1/v2 runs deleted.
set -uo pipefail
B=<workspace>; E=$B/boar-eval; CS=$B/rnd/research/compass/chat-slice
export HEAVY_CLASS=normal
C4=$E/runs/kiln/chat-slice-base-s42/config.json; C15=$E/adapters/desktop-node/configs/p2-iphone13-0cfd4a77.json
run() { # slice model arm seed
  local s=$1 m=$2 arm=$3 seed=$4 cfg slicef d label=kiln-chatline-$1-$2-$3-s$4
  [ $m = 4b ] && cfg=$C4 || cfg=$C15
  case $s in v0) slicef=$CS/slice.v0.jsonl; d=$E/runs/kiln/b6chatline/v0-$m-$arm-s$seed ;; v1) slicef=$CS/v1-fresh/slice.v1.jsonl; d=$CS/v1-fresh/runs/chatline-$m-$arm-s$seed ;; v2) slicef=$CS/v2-fresh/slice.v2.jsonl; d=$CS/v2-fresh/runs/chatline-$m-$arm-s$seed ;; esac
  mkdir -p $d
  python3 -c "import json; c=json.load(open('$cfg')); c['arm']='$arm'; c['seed']=$seed; json.dump(c, open('$d/config.json','w'))"
  pnpm -s -C $E/packages/protocol exec tsx src/makeRequests.ts --questions $slicef --config $d/config.json --run-id $label > $d/requests.jsonl 2>/dev/null
  BOAR_EVAL_RUNNER_DIR=be-$arm $E/adapters/desktop-node/run.sh --commit 0cfd4a77 --arm $arm --requests $d/requests.jsonl --out $d/traces.jsonl > $d/runsh.out 2>&1
  echo "$s $m $arm s$seed rc=$? $(date +%H:%M)"
  [ $s != v0 ] && <on the mini> "rm -rf <runner>/kiln/be-0cfd4a77-$arm/be-$arm/runs/$label"
  python3 $CS/score_l0.py --slice $slicef --traces $d/traces.jsonl --json $d/score_l0.json --quiet > $d/score_l0.txt 2>&1
}
for seed in 42 43; do for s in v0 v1 v2; do for m in 4b 15b; do run $s $m b6chatline $seed; done; done; done
for s in v0 v1 v2; do for m in 4b 15b; do run $s $m b6precedence 43; done; done
echo B6CHATLINE-L1-DONE
