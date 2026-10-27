#!/usr/bin/env bash
# Compass's precedence-only arm b6precedence (97684006…2d950), criteria .../replylang/precedence/CRITERIA.md.
# (1) arm on the 48 Spanish items (es_ids.json, 16 per v0/v1/v2), 4B + 1.5B, s42; refs = existing B6-alone runs.
# (2) seed 43 on v2-038, v2-039 for arm AND B6 alone, both models. v1/v2 outputs restricted; mini copies of v1/v2 runs deleted.
set -uo pipefail
B=<workspace>; E=$B/boar-eval; CS=$B/rnd/research/compass/chat-slice; P=$CS/replylang/precedence
export HEAVY_CLASS=normal
C4=$E/runs/kiln/chat-slice-base-s42/config.json; C15=$E/adapters/desktop-node/configs/p2-iphone13-0cfd4a77.json
run() { # slice model arm seed ids outdir
  local s=$1 m=$2 arm=$3 seed=$4 ids=$5 d=$6 cfg slicef label=kiln-prec-$1-$2-$3-s$4
  [ $m = 4b ] && cfg=$C4 || cfg=$C15
  case $s in v0) slicef=$CS/slice.v0.jsonl ;; v1) slicef=$CS/v1-fresh/slice.v1.jsonl ;; v2) slicef=$CS/v2-fresh/slice.v2.jsonl ;; esac
  mkdir -p $d
  python3 -c "import json; c=json.load(open('$cfg')); c['arm']='$arm'; c['seed']=$seed; json.dump(c, open('$d/config.json','w'))"
  pnpm -s -C $E/packages/protocol exec tsx src/makeRequests.ts --questions $slicef --config $d/config.json --run-id $label > $d/requests.jsonl 2>/dev/null
  BOAR_EVAL_RUNNER_DIR=be-$arm $E/adapters/desktop-node/run.sh --commit 0cfd4a77 --arm $arm --requests $d/requests.jsonl --out $d/traces.jsonl --ids "$ids" > $d/runsh.out 2>&1
  echo "$s $m $arm s$seed rc=$? $(date +%H:%M)"
  [ $s != v0 ] && <on the mini> "rm -rf <runner>/kiln/be-0cfd4a77-$arm/be-$arm/runs/$label"
}
for s in v0 v1 v2; do
  ids=$(python3 -c "import json; print(','.join(json.load(open('$P/es_ids.json'))['$s']))")
  for m in 4b 15b; do
    [ $s = v0 ] && d=$E/runs/kiln/b6precedence/v0-$m-b6precedence-s42 || d=$CS/$s-fresh/runs/prec-$m-b6precedence-s42
    run $s $m b6precedence 42 "$ids" $d
  done
done
for m in 4b 15b; do for arm in b6precedence b6gate; do run v2 $m $arm 43 v2-038,v2-039 $CS/v2-fresh/runs/prec-$m-$arm-s43; done; done
echo B6PRECEDENCE-L1-DONE
