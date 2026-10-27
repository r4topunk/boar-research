#!/bin/bash
# ADDENDUM-3 job 17 gate (0 LLM, MacBook, one replay at a time, load < 20): kiln-local/rs-RC-STICKY vs rs-RC (validation-1024/replays/RC, rcrun.sh rc mode).
# Same commands as tools/rcrun.sh mode rc (main: replay-sweep; f8/ls: r5 replay-sticky), tree swapped; RS_STICKY unset for the identity sets, =2 for c2.
# usage: carry_gate.sh  -> replays/RCST/{main,f8,f8.c2,ls.c2}.jsonl, then score_carry_gate.py
set -u
B=<workspace>; A=$B/rnd/research/coordinator/arms; VD=$A/validation-1024; C=$A/coverage-map; R5=$C/searchpar/r5
. $VD/tools/rc-env.sh
export BOAR_REPLAY_CACHE=$B/boar-eval/runs/replay-cache-v7st; mkdir -p ${BOAR_REPLAY_CACHE}
TSX=$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx; SW=$A/retrieve-sweep/tools/replay-sweep.ts; ST5=$R5/tools/replay-sticky.ts
TREE=$B/kiln-local/rs-RC-STICKY; O=$VD/replays/RCST; mkdir -p $O; cd $B
SEFIX="RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1"
W78ENV="RS_SE_LEAD_BIN=32 RS_SE_LEAD_BIN_DIR=$C/w78/sidecars RS_DENSE_Q_DIR=$C/w78/sidecars-c RS_DENSE_IVFP=32"
run() { local L=$1 CY=$2; shift 2; local t0=$(date +%s)
  while [ "$(sysctl -n vm.loadavg | awk '{print int($2)}')" -ge 20 ]; do sleep 60; done
  local ST=""; [ "$CY" != 0 ] && ST="RS_STICKY=$CY"
  env -u RS_HEALTH_NOSOURCE_FALLBACK -u RS_STICKY -u RS_X2B_BUDGET -u RS_RB_K -u RS_RB_COMPRESS -u RS_DENSE_IVF -u RS_DENSE_IVFP -u RS_SE_LEAD_BIN \
    $SEFIX $W78ENV $ST RS_DENSE_LOG=$O/$L.denselog RS_SE_LEAD_LOG=$O/$L.f1log "$@" --out $O/$L.jsonl 2> $O/$L.err
  echo "RCST $L rc=$? $(( $(date +%s) - t0 ))s load=$(sysctl -n vm.loadavg | awk '{print $2}')" | tee -a $O/runs.log; }
run main 0 $TSX $SW --questions $A/decode-ground/runs/req/dg-S-K1-main-s42.requests.jsonl --tree $TREE --packs $RC_PACKS \
  --tasks-from $C/replay/funnel-K3.traces.jsonl --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 0 --forward-opts --settings-json "$RC_SETTINGS"
run f8 0 $TSX $ST5 --questions $R5/qform.chain.jsonl --tree $TREE --packs $RC_PACKS --gate search --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 0 --forward-opts --settings-json "$RC_SETTINGS"
run f8.c2 2 $TSX $ST5 --questions $R5/qform.chain.jsonl --tree $TREE --packs $RC_PACKS --gate search --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 0 --forward-opts --settings-json "$RC_SETTINGS"
run ls.c2 2 $TSX $ST5 --questions $R5/longsession.chain.jsonl --tree $TREE --packs $RC_PACKS --gate search --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 0 --forward-opts --settings-json "$RC_SETTINGS"
