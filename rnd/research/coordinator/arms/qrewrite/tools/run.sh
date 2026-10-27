#!/bin/bash
# QREWRITE replay (0 LLM, MacBook). usage: run.sh <set main|st> <label> [QRW_MAP=file QRW_MODE=replace|concat]
# MAIN = sefix/tools/run_main.sh recipe with the QREWRITE driver; ST = PACKPROOF 180 in 3 kit groups. SEFIX-124 env always.
set -u
B=<workspace>; R=$B/rnd/research/coordinator/arms; C=$R/coverage-map; Q=$R/qrewrite; PP=$R/packproof
export BOAR_REPLAY_CACHE=$B/boar-eval/runs/replay-cache
TSX=$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx; TOOL=$Q/tools/replay-qrw.ts; TREE=$B/kiln-local/rs-SEFIX
SET=$1; LAB=$2; shift 2; t0=$(date +%s); cd $B
ENV="RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1"
PK=$(python3 -I $C/compose/tools/kits.py 10); V=$B/shared-data/packs/v3proto
run() { # questions tasks packs out
  env $ENV "$@" ; }
if [ $SET = main ]; then
  OUT=$Q/replays/main.$LAB.jsonl
  env $ENV "$@" $TSX $TOOL --questions $R/decode-ground/runs/req/dg-S-K1-main-s42.requests.jsonl --tree $TREE --packs $PK \
    --tasks-from $C/replay/funnel-K3.traces.jsonl --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 12 \
    --forward-opts --settings-json '{"packHeadPass":"a2","packDense2":"append-budget"}' --out $OUT 2> $OUT.err
  echo "main $LAB rc=$? $(( $(date +%s) - t0 ))s [$*] $(tail -1 $OUT.err | cut -c1-120)"
else
  OUT=$Q/replays/st.$LAB.jsonl; : > $OUT
  for g in on-k13 on-k13+qa-bitcoin-se on-k13+qa-ethereum-se; do
    P=$PK; case $g in *bitcoin*) P=$PK,$V/qa-bitcoin-se.sqlite;; *ethereum*) P=$PK,$V/qa-ethereum-se.sqlite;; esac
    O=$Q/replays/st.$LAB.$g.jsonl
    env $ENV "$@" $TSX $TOOL --questions $PP/in/$g.requests.jsonl --tree $TREE --packs $P \
      --tasks-from $PP/gen/$g/traces.jsonl --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 12 \
      --forward-opts --settings-json '{"packHeadPass":"a2","packDense2":"append-budget"}' --out $O 2> $O.err
    echo "st $LAB $g rc=$? $(tail -1 $O.err | cut -c1-120)"; cat $O >> $OUT
  done
  echo "st $LAB rows=$(wc -l < $OUT) $(( $(date +%s) - t0 ))s [$*]"
fi
