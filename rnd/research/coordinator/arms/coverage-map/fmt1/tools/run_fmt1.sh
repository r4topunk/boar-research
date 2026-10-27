#!/bin/bash
# FMT1-SCAN replay (0 LLM, MacBook) on kiln-local/rs-FMT1 with the SEFIX-124 env. usage: run_fmt1.sh <main|t27> <arm>
# arms: P400 P400f65 P2000 P2000f65 FULL FULLf65 (criterion coverage-map/FMT1-criterion.md sha 79fefb9c)
set -u
B=<workspace>; R=$B/rnd/research/coordinator/arms; C=$R/coverage-map; F=$C/fmt1
export BOAR_REPLAY_CACHE=$B/boar-eval/runs/replay-cache
TSX=$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx; TOOL=$R/retrieve-sweep/tools/replay-sweep.ts; TREE=$B/kiln-local/rs-FMT1
SET=$1; ARM=$2; OUT=$F/replays/$SET.$ARM.jsonl; t0=$(date +%s); cd $B
E="RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1"
case $ARM in P400*) ;; P2000*) E="$E RS_FMT1_POOL=2000";; FULL*) E="$E RS_FMT1_POOL=full";; *) echo bad arm; exit 2;; esac
case $ARM in *f65) E="$E RS_FMT1_FLOOR=0.65";; esac
if [ $SET = main ]; then
  PK=$(python3 -I $C/compose/tools/kits.py 10)
  env $E $TSX $TOOL --questions $R/decode-ground/runs/req/dg-S-K1-main-s42.requests.jsonl --tree $TREE --packs $PK \
    --tasks-from $C/replay/funnel-K3.traces.jsonl --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 12 \
    --forward-opts --settings-json '{"packHeadPass":"a2","packDense2":"append-budget"}' --out $OUT 2> $OUT.err
else
  env $E $TSX $TOOL --questions $R/topics27/in/t27-detailed-s42.requests.jsonl --tree $TREE --packs $B/shared-data/packs/wiki-vital5.sqlite --corpus essential \
    --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 12 --gate search \
    --forward-opts --settings-json '{"quickFirst":true,"alwaysComplete":false,"packHeadPass":"a2","packDense2":"append-budget","personalityId":"detailed"}' \
    --out $OUT 2> $OUT.err
fi
echo "$SET.$ARM rc=$? $(( $(date +%s) - t0 ))s [$E] $(grep -h '\[fmt1\]' $OUT.err | head -1) $(tail -1 $OUT.err | cut -c1-160)"
