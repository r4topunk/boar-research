#!/usr/bin/env bash
# Compass's replylang arm (patch 5d1c3392…, engine 0cfd4a77), L0/L1, 1 rep, seed 42, node backend. No judge.
set -uo pipefail
B=<workspace>; E=$B/boar-eval; CS=$B/rnd/research/compass/chat-slice; OUT=$E/runs/kiln/replylang
export BOAR_EVAL_RUNNER_DIR=be-kiln HEAVY_CLASS=normal
until grep -q PAR-BENCH-DONE <scratch> 2>/dev/null; do sleep 20; done
chat() { # label, base config, arm
  local label="$1" cfg="$2" arm="$3" d="$OUT/$1"; mkdir -p "$d"
  python3 -c "import json; c=json.load(open('$cfg')); c['arm']='$arm'; c['seed']=42; json.dump(c, open('$d/config.json','w'))"
  pnpm -s -C $E/packages/protocol exec tsx src/makeRequests.ts --questions $CS/slice.v0.jsonl --config $d/config.json --run-id "kiln-$label" > $d/requests.jsonl
  $E/adapters/desktop-node/run.sh --commit 0cfd4a77 --arm "$arm" --requests $d/requests.jsonl --out $d/traces.jsonl > $d/runsh.out 2>&1
  echo "$label rc=$? $(date +%H:%M)"
  python3 $CS/score_l0.py --slice $CS/slice.v0.jsonl --traces $d/traces.jsonl --json $d/score_l0.json --quiet > $d/score_l0.txt 2>&1
}
chat chat-v0-4b-replylang $E/runs/kiln/chat-slice-base-s42/config.json replylang          # (A)
chat chat-v0-15b-main     $E/adapters/desktop-node/configs/p2-iphone13-0cfd4a77.json main  # (B)
chat chat-v0-15b-replylang $E/adapters/desktop-node/configs/p2-iphone13-0cfd4a77.json replylang
# (C) L1 outofkit-quality, 4B (and-qwen-s42 config), arm then main
$B/rnd/kiln/l1/run_l1.sh outofkit-quality replylang $E/runs/night-2026-10-01/and-qwen-s42.config.json --arm replylang --no-judge > $OUT/l1-arm.out 2>&1; echo "C-arm rc=$? $(date +%H:%M)"
$B/rnd/kiln/l1/run_l1.sh outofkit-quality main-node $E/runs/night-2026-10-01/and-qwen-s42.config.json --no-judge > $OUT/l1-main.out 2>&1; echo "C-main rc=$? $(date +%H:%M)"
echo REPLYLANG-DONE
