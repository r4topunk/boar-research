#!/bin/bash
# SEFIX queue 2 (after the F2 scope fix: F2 acts on Stack Exchange packs WITHOUT chunk_vecs; the first F2 runs are *_allSE) + the F1b combined reads
cd <workspace>/rnd/research/coordinator/arms/coverage-map/sefix
run() { lab=$1; shift; f=replays/main.$lab.jsonl; [ -s $f ] && [ $(wc -l < $f) -ge 97 ] && return; bash tools/run_main.sh $lab "$@"; }
runx() { lab=$1; shift; f=replays/main.$lab.jsonl; [ -s $f ] && [ $(wc -l < $f) -ge 97 ] && return; bash tools/run_f1bx.sh $lab "$@"; }
run F2 RS_SE_MAXDF=0.25
run F1F2F3 RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_HEALTH_NOSOURCE_FALLBACK=1
run F1F2F3F4 RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_HEALTH_NOSOURCE_FALLBACK=1 RS_KEEP_NOPROPER=1
run F2g RS_SE_GLOBALDF=1
run F2g25 RS_SE_GLOBALDF=1 RS_SE_MAXDF=0.25
runx F1b0 RS_X=0
runx F1bF3F4 RS_HEALTH_NOSOURCE_FALLBACK=1 RS_KEEP_NOPROPER=1
runx F1bF3 RS_HEALTH_NOSOURCE_FALLBACK=1
runx F1bF4 RS_KEEP_NOPROPER=1
run F3b RS_HEALTH_NOSOURCE_FALLBACK=2
run F4lit RS_KEEP_NOPROPER=lit
run F1N2F3 RS_SE_LEAD=0.78 RS_SE_LEAD_N=2 RS_HEALTH_NOSOURCE_FALLBACK=1
run off2
echo ALLDONE
