#!/bin/bash
# SEFIX queue 6 (after the reboot): main variants first, then the single-arm QFORM reads, then wall rerun
cd <workspace>/rnd/research/coordinator/arms/coverage-map/sefix
n() { wc -l < replays/$1.jsonl 2>/dev/null || echo 0; }
run() { lab=$1; shift; [ "$(n main.$lab)" -ge 97 ] && return; bash tools/run_main.sh $lab "$@"; }
runq() { lab=$1; shift; [ "$(n qform.$lab)" -ge 432 ] && return; bash tools/run_qform.sh $lab "$@"; }
run F3b RS_HEALTH_NOSOURCE_FALLBACK=2
run F4lit RS_KEEP_NOPROPER=lit
run F1N2F3 RS_SE_LEAD=0.78 RS_SE_LEAD_N=2 RS_HEALTH_NOSOURCE_FALLBACK=1
runq F3 RS_HEALTH_NOSOURCE_FALLBACK=1
runq F4 RS_KEEP_NOPROPER=1
run off2
echo ALLDONE
