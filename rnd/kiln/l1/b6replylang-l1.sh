#!/usr/bin/env bash
# Compass's stacked arm b6replylang (1b37161c…afaf7) L1, criteria rnd/research/compass/chat-slice/replylang/stack-b6/CRITERIA.md.
# 1 rep, s42, node, multi-turn. 4B = chat-slice-base-s42 profile, 1.5B = p2-iphone13-0cfd4a77. Reference = B6 alone (b6gate).
# v1/v2 outputs stay in their restricted folders (v1-fresh/runs, v2-fresh/runs); mini copies of v1/v2 runs are deleted.
set -uo pipefail
B=<workspace>; E=$B/boar-eval; CS=$B/rnd/research/compass/chat-slice
export HEAVY_CLASS=normal
C4=$E/runs/kiln/chat-slice-base-s42/config.json; C15=$E/adapters/desktop-node/configs/p2-iphone13-0cfd4a77.json
chat() { # slice(v0|v1|v2) model(4b|15b) arm(b6replylang|b6gate)
  local s=$1 m=$2 arm=$3 cfg slicef d label
  [ $m = 4b ] && cfg=$C4 || cfg=$C15
  case $s in v0) slicef=$CS/slice.v0.jsonl; d=$E/runs/kiln/b6replylang/$s-$m-$arm ;; v1) slicef=$CS/v1-fresh/slice.v1.jsonl; d=$CS/v1-fresh/runs/stack-$m-$arm ;; v2) slicef=$CS/v2-fresh/slice.v2.jsonl; d=$CS/v2-fresh/runs/stack-$m-$arm ;; esac
  label=kiln-stack-$s-$m-$arm; mkdir -p $d
  python3 -c "import json; c=json.load(open('$cfg')); c['arm']='$arm'; c['seed']=42; json.dump(c, open('$d/config.json','w'))"
  pnpm -s -C $E/packages/protocol exec tsx src/makeRequests.ts --questions $slicef --config $d/config.json --run-id $label > $d/requests.jsonl 2>/dev/null
  BOAR_EVAL_RUNNER_DIR=be-$arm $E/adapters/desktop-node/run.sh --commit 0cfd4a77 --arm $arm --requests $d/requests.jsonl --out $d/traces.jsonl > $d/runsh.out 2>&1
  echo "$s $m $arm rc=$? $(date +%H:%M)"
  [ $s != v0 ] && <on the mini> "rm -rf <runner>/kiln/be-0cfd4a77-$arm/be-$arm/runs/$label"
  python3 $CS/score_l0.py --slice $slicef --traces $d/traces.jsonl --json $d/score_l0.json --quiet > $d/score_l0.txt 2>&1
}
for s in v0 v1 v2; do for m in 4b 15b; do chat $s $m b6replylang; done; done
chat v0 4b b6gate; chat v1 4b b6gate
for s in v0 v1 v2; do chat $s 15b b6gate; done
# (c) outofkit-quality, 4B (and-qwen config), stacked vs B6 alone
for arm in b6replylang b6gate; do
  BOAR_EVAL_RUNNER_DIR=be-$arm $B/rnd/kiln/l1/run_l1.sh outofkit-quality $arm $E/runs/night-2026-10-01/and-qwen-s42.config.json --arm $arm --no-judge > $E/runs/kiln/b6replylang/l1-$arm.out 2>&1; echo "outofkit $arm rc=$? $(date +%H:%M)"
done
echo B6REPLYLANG-L1-DONE
