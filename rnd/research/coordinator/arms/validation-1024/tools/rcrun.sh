#!/bin/bash
# VALIDATION 2026-10-24 replays (0 LLM, MacBook). usage: rcrun.sh <name> <mode> [sets...]
#   mode off  = rs-RC, every RC switch off, v1 kit (K13 = kits.py 10)      -> V0 (a) vs retbench/replays/base
#   mode w78  = rs-RC, W78 PF32 switches + w78pf packs, v1 factbook        -> V0 (b) vs w78/replays-pf/main.PF32 (W78 recipe: --wide 12)
#   mode rc   = ENGINE-RC (tools/rc-env.sh)                                -> V0 (c), V1, V3 L1, S1, S8
#   mode rb   = kiln-local/rs-RETBENCH + SEFIX-124 + RS_RB_K=4 RS_RB_COMPRESS=0.4 (B-k4comp40), v1 kit -> probes only
# sets: main st topics f8 ls probes (retbench.sh / x2b-budget run.sh recipes). Writes replays/<name>/<set>.jsonl (+ .denselog .f1log .err), runs.log.
set -u
B=<workspace>; A=$B/rnd/research/coordinator/arms; VD=$A/validation-1024; C=$A/coverage-map; PP=$A/packproof; R5=$C/searchpar/r5; F3=$C/sefix/f3-safety
NAME=$1; MODE=$2; shift 2; SETS=${*:-main st topics f8 ls probes}
export BOAR_REPLAY_CACHE=$B/boar-eval/runs/replay-cache-v7
TSX=$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx; SW=$A/retrieve-sweep/tools/replay-sweep.ts; ST5=$R5/tools/replay-sticky.ts
V=$B/shared-data/packs/v3proto; O=$VD/replays/$NAME; mkdir -p $O; cd $B
K1S='{"packHeadPass":"a2","packDense2":"append-budget"}'; PS='{"quickFirst":true,"alwaysComplete":false,"packHeadPass":"a2","packDense2":"append-budget"}'
TS='{"quickFirst":true,"alwaysComplete":false,"packHeadPass":"a2","packDense2":"append-budget","personalityId":"detailed"}'
WIDE=0; TREE=$B/kiln-local/rs-RC; PK=$(python3 -I $C/compose/tools/kits.py 10)
SEFIX="RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1"; MENV=""
W78ENV="RS_SE_LEAD_BIN=32 RS_SE_LEAD_BIN_DIR=$C/w78/sidecars RS_DENSE_Q_DIR=$C/w78/sidecars-c RS_DENSE_IVFP=32"
pfk() { local p=$1; p=${p//$V\/boar-simplewiki-en.sqlite/$B/kiln-local/w78pf-packs/boar-simplewiki-en.sqlite}; echo ${p//$V\/qa-travel-se.sqlite/$B/kiln-local/w78pf-packs/qa-travel-se.sqlite}; }
case $MODE in
 off) ;;
 w78) WIDE=12; MENV=$W78ENV; PK=$(pfk $PK);;
 rc)  . $VD/tools/rc-env.sh; MENV=$W78ENV; PK=$RC_PACKS; K1S=$RC_SETTINGS; PS=$RC_SETTINGS
      TS='{"quickFirst":true,"alwaysComplete":false,"packHeadPass":"a2","packDense2":"append-budget","personalityId":"succinct"}';;
 rb)  TREE=$B/kiln-local/rs-RETBENCH; MENV="RS_RB_K=4 RS_RB_COMPRESS=0.4";;
 rb0) TREE=$B/kiln-local/rs-RETBENCH;;   # control: rs-RETBENCH, knobs off
 *) echo "bad mode"; exit 2;;
esac
run() { local L=$1; shift; local t0=$(date +%s); rm -f $O/$L.denselog $O/$L.f1log
  while [ "$(sysctl -n vm.loadavg | awk '{print int($2)}')" -gt 20 ]; do sleep 60; done
  local l0=$(sysctl -n vm.loadavg | awk '{print $2}')
  env -u RS_HEALTH_NOSOURCE_FALLBACK -u RS_STICKY -u RS_X2B_BUDGET -u RS_RB_K -u RS_RB_COMPRESS -u RS_DENSE_IVF -u RS_DENSE_IVFP -u RS_SE_LEAD_BIN \
    $SEFIX $MENV RS_DENSE_LOG=$O/$L.denselog RS_SE_LEAD_LOG=$O/$L.f1log "$@" --out $O/$L.jsonl 2> $O/$L.err
  echo "$NAME $MODE $L rc=$? $(( $(date +%s) - t0 ))s load0=$l0 load1=$(sysctl -n vm.loadavg | awk '{print $2}')" | tee -a $O/runs.log; }
for S in $SETS; do case $S in
 main) run main $TSX $SW --questions $A/decode-ground/runs/req/dg-S-K1-main-s42.requests.jsonl --tree $TREE --packs $PK \
   --tasks-from $C/replay/funnel-K3.traces.jsonl --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide $WIDE --forward-opts --settings-json "$K1S";;
 st) for g in on-k13 on-k13+qa-bitcoin-se on-k13+qa-ethereum-se; do
   P=$PK; case $g in *bitcoin*) P=$PK,$V/qa-bitcoin-se.sqlite;; *ethereum*) P=$PK,$V/qa-ethereum-se.sqlite;; esac
   run st.$g $TSX $SW --questions $PP/in/$g.requests.jsonl --tree $TREE --packs $P --tasks-from $PP/gen/$g/traces.jsonl \
     --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide $WIDE --forward-opts --settings-json "$K1S"; done;;
 topics) run topics $TSX $SW --questions $A/topics27/in/t27-detailed-s42.requests.jsonl --tree $TREE --packs $B/shared-data/packs/wiki-vital5.sqlite --corpus essential \
   --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 0 --gate search --forward-opts --settings-json "$TS";;
 f8) run f8 $TSX $ST5 --questions $R5/qform.chain.jsonl --tree $TREE --packs $PK --gate search --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 0 --forward-opts --settings-json "$K1S";;
 ls) run ls $TSX $ST5 --questions $R5/longsession.chain.jsonl --tree $TREE --packs $PK --gate search --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 0 --forward-opts --settings-json "$K1S";;
 probes) run probes $TSX $SW --questions $F3/req/f3safety-off-s42.requests.jsonl --tree $TREE --packs $PK --tasks-from $F3/runs/f3safety-off-s42.traces.jsonl \
   --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 0 --forward-opts --settings-json "$PS";;
esac; done
