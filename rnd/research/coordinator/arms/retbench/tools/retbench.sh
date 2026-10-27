#!/bin/bash
# RETBENCH v1 (0 LLM, MacBook only): one config -> replays of MAIN 97, ST 180 (3 kit groups), TOPICS 27, F8 48 pairs, LONGSESSION 50 turns
# on kiln-local/rs-RETBENCH (= rs-SEFIX + RETBENCH-KNOBS.patch) with SEFIX-124 env + the config's env, then aggregates/<name>.json.
# usage: retbench.sh <config.json>   config = {"name": "...", "env": {"RS_RB_CAP": "4", ...}}   env LANE=<n> -> own replay cache (parallel-safe)
# SETS env (default "main st topics f8 ls") limits the sets; SKIP_SCORE=1 skips the scorer.
set -u
B=<workspace>; A=$B/rnd/research/coordinator/arms; RB=$A/retbench; C=$A/coverage-map; PP=$A/packproof; R5=$C/searchpar/r5
CFG=$1; NAME=$(python3 -I -c "import json,sys;print(json.load(open(sys.argv[1]))['name'])" $CFG)
CENV=$(python3 -I -c "import json,sys;print(' '.join(f'{k}={v}' for k,v in json.load(open(sys.argv[1])).get('env',{}).items()))" $CFG)
LANE=${LANE:-0}; export BOAR_REPLAY_CACHE=$B/boar-eval/runs/replay-cache-rb$LANE; mkdir -p ${BOAR_REPLAY_CACHE}
TSX=$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx; SW=$A/retrieve-sweep/tools/replay-sweep.ts; ST5=$R5/tools/replay-sticky.ts
TREE=${TREE:-$B/kiln-local/rs-RETBENCH}; SETS=${SETS:-main st topics f8 ls}
SEFIX="RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1"
PK=$(python3 -I $C/compose/tools/kits.py 10); V=$B/shared-data/packs/v3proto; O=$RB/replays/$NAME; mkdir -p $O; cd $B
K1S='{"packHeadPass":"a2","packDense2":"append-budget"}'
run() { # label tool args...
  local L=$1; shift; local t0=$(date +%s); rm -f $O/$L.bytes
  env -u RS_HEALTH_NOSOURCE_FALLBACK -u RS_STICKY $SEFIX $CENV RS_BYTES_LOG=$O/$L.bytes "$@" --out $O/$L.jsonl 2> $O/$L.err
  local rc=$?; echo "$NAME $L rc=$rc $(( $(date +%s) - t0 ))s load=$(sysctl -n vm.loadavg | awk '{print $2}')" | tee -a $O/runs.log; }
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
 f8) run f8 $TSX $ST5 --questions $R5/qform.chain.jsonl --tree $TREE --packs $PK --gate search --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 0 --forward-opts --settings-json "$K1S";;
 ls) run ls $TSX $ST5 --questions $R5/longsession.chain.jsonl --tree $TREE --packs $PK --gate search --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 0 --forward-opts --settings-json "$K1S";;
esac; done
[ "${SKIP_SCORE:-0}" = 1 ] || python3 -I $RB/tools/score.py $NAME
