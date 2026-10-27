#!/bin/bash
# D2Q replay (0 LLM, MacBook). usage: run.sh <set main|st> <arm off|x1|x2> [group for st: on-k13|on-k13+qa-ethereum-se|on-k13+qa-bitcoin-se]
# arm off = D2Q kit with RS_D2Q unset (identity vs K13 on rs-SEFIX); x1/x2 = D2Q kit + RS_D2Q.
set -u
B=<workspace>; R=$B/rnd/research/coordinator/arms; C=$R/coverage-map; D=$R/d2q
export BOAR_REPLAY_CACHE=$B/boar-eval/runs/replay-cache
TSX=$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx; TOOL=$R/retrieve-sweep/tools/replay-sweep.ts; TREE=$B/kiln-local/rs-D2Q
SET=$1; ARM=$2; G=${3:-}; t0=$(date +%s); cd $B; mkdir -p $D/replay
ENV="RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1"; [ $ARM != off ] && ENV="$ENV RS_D2Q=$ARM"
case $SET in
 main) OUT=$D/replay/main.$ARM.jsonl; PK=$(python3 -I $D/tools/kits.py D2Q)
   env $ENV $TSX $TOOL --questions $R/decode-ground/runs/req/dg-S-K1-main-s42.requests.jsonl --tree $TREE --packs $PK \
     --tasks-from $C/replay/funnel-K3.traces.jsonl --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 12 \
     --forward-opts --settings-json '{"packHeadPass":"a2","packDense2":"append-budget"}' --out $OUT 2> $OUT.err ;;
 st) OUT=$D/replay/st.$ARM.$G.jsonl; X=""; case $G in *+*) X=$B/shared-data/packs/v3proto/${G#on-k13+}.sqlite;; esac
   PK=$(python3 -I $D/tools/kits.py D2Q $X)
   env $ENV $TSX $TOOL --questions $R/packproof/in/$G.requests.jsonl --tree $TREE --packs $PK \
     --tasks-from $R/packproof/gen/$G/traces.jsonl --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 12 \
     --forward-opts --settings-json '{"packHeadPass":"a2","packDense2":"append-budget"}' --out $OUT 2> $OUT.err ;;
esac
echo "$SET $ARM $G rc=$? $(( $(date +%s) - t0 ))s $(tail -1 $OUT.err | cut -c1-200)"
