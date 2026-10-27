#!/bin/bash
# SEFIX queue 3 (priority order under machine load): finish F1b0, combined F1b read, QFORM six-file, then the optional variants
cd <workspace>/rnd/research/coordinator/arms/coverage-map/sefix
while pgrep -f "run_f1bx.sh F1bF3F4" >/dev/null; do sleep 5; done
n() { wc -l < replays/$1.jsonl 2>/dev/null || echo 0; }
runx() { lab=$1; shift; [ "$(n main.$lab)" -ge 97 ] && return; bash tools/run_f1bx.sh $lab "$@"; }
run() { lab=$1; shift; [ "$(n main.$lab)" -ge 97 ] && return; bash tools/run_main.sh $lab "$@"; }
runq() { lab=$1; shift; [ "$(n qform.$lab)" -ge 432 ] && return; bash tools/run_qform.sh $lab "$@"; }
runq FULL RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_HEALTH_NOSOURCE_FALLBACK=1 RS_KEEP_NOPROPER=1
runq F3 RS_HEALTH_NOSOURCE_FALLBACK=1
runq F4 RS_KEEP_NOPROPER=1
runq off RS_X=0
echo CORE_DONE
run F3b RS_HEALTH_NOSOURCE_FALLBACK=2
run F4lit RS_KEEP_NOPROPER=lit
run F1N2F3 RS_SE_LEAD=0.78 RS_SE_LEAD_N=2 RS_HEALTH_NOSOURCE_FALLBACK=1
runq FULLg RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_HEALTH_NOSOURCE_FALLBACK=1 RS_KEEP_NOPROPER=1
run off2
runx F1bF3 RS_HEALTH_NOSOURCE_FALLBACK=1
runx F1bF4 RS_KEEP_NOPROPER=1
echo ALLDONE
