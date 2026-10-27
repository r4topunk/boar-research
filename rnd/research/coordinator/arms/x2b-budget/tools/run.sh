#!/bin/bash
# X2B-BUDGET replays (0 LLM, MacBook): retbench.sh recipe (main, st x3, topics) + the 65 safety probes, on kiln-local/rs-X2B. usage: run.sh <name> [budget]
set -u
B=<workspace>; A=$B/rnd/research/coordinator/arms; X=$A/x2b-budget; C=$A/coverage-map; PP=$A/packproof; F3=$C/sefix/f3-safety
NAME=$1; BUD=${2:-}; CENV=""; [ -n "$BUD" ] && CENV="RS_X2B_BUDGET=$BUD"
export BOAR_REPLAY_CACHE=$B/boar-eval/runs/replay-cache-x2b; mkdir -p ${BOAR_REPLAY_CACHE}
TSX=$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx; SW=$A/retrieve-sweep/tools/replay-sweep.ts
TREE=$B/kiln-local/rs-X2B; SETS=${SETS:-main st topics probes}
SEFIX="RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1"
PK=$(python3 -I $C/compose/tools/kits.py 10); V=$B/shared-data/packs/v3proto; O=$X/replays/$NAME; mkdir -p $O; cd $B
K1S='{"packHeadPass":"a2","packDense2":"append-budget"}'
run() { local L=$1; shift; local t0=$(date +%s)
  env -u RS_HEALTH_NOSOURCE_FALLBACK -u RS_STICKY -u RS_X2B_BUDGET $SEFIX $CENV "$@" --out $O/$L.jsonl 2> $O/$L.err
  echo "$NAME $L rc=$? $(( $(date +%s) - t0 ))s [$CENV] load=$(sysctl -n vm.loadavg | awk '{print $2}')" | tee -a $O/runs.log; }
for S in $SETS; do case $S in
 main) run main $TSX $SW --questions $A/decode-ground/runs/req/dg-S-K1-main-s42.requests.jsonl --tree $TREE --packs $PK \
   --tasks-from $C/replay/funnel-K3.traces.jsonl --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 0 --forward-opts --settings-json "$K1S";;
 st) for g in on-k13 on-k13+qa-bitcoin-se on-k13+qa-ethereum-se; do
   P=$PK; case $g in *bitcoin*) P=$PK,$V/qa-bitcoin-se.sqlite;; *ethereum*) P=$PK,$V/qa-ethereum-se.sqlite;; esac
   run st.$g $TSX $SW --questions $PP/in/$g.requests.jsonl --tree $TREE --packs $P --tasks-from $PP/gen/$g/traces.jsonl \
     --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 0 --forward-opts --settings-json "$K1S"; done;;
 topics) run topics $TSX $SW --questions $A/topics27/in/t27-detailed-s42.requests.jsonl --tree $TREE --packs $B/shared-data/packs/wiki-vital5.sqlite --corpus essential \
   --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 0 --gate search --forward-opts \
   --settings-json '{"quickFirst":true,"alwaysComplete":false,"packHeadPass":"a2","packDense2":"append-budget","personalityId":"detailed"}';;
 probes) run probes $TSX $SW --questions $F3/req/f3safety-off-s42.requests.jsonl --tree $TREE --packs $PK --tasks-from $F3/runs/f3safety-off-s42.traces.jsonl \
   --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 0 --forward-opts --settings-json '{"quickFirst":true,"alwaysComplete":false,"packHeadPass":"a2","packDense2":"append-budget"}';;
esac; done
