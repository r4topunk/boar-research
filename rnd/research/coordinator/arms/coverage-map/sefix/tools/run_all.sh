#!/bin/bash
# the SEFIX MAIN replays, sequential (wall comparable)
cd <workspace>/rnd/research/coordinator/arms/coverage-map/sefix
run() { lab=$1; shift; f=replays/main.$lab.jsonl; [ -s $f ] && [ $(wc -l < $f) -ge 97 ] && return; bash tools/run_main.sh $lab "$@"; }
run F1 RS_SE_LEAD=0.78
run F2 RS_SE_MAXDF=0.25
run F3 RS_HEALTH_NOSOURCE_FALLBACK=1
run F4 RS_KEEP_NOPROPER=1
run F1F3 RS_SE_LEAD=0.78 RS_HEALTH_NOSOURCE_FALLBACK=1
run F1F2F3 RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_HEALTH_NOSOURCE_FALLBACK=1
run F1F2F3F4 RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_HEALTH_NOSOURCE_FALLBACK=1 RS_KEEP_NOPROPER=1
run F1N2 RS_SE_LEAD=0.78 RS_SE_LEAD_N=2
run F2g RS_SE_GLOBALDF=1
run F2g25 RS_SE_GLOBALDF=1 RS_SE_MAXDF=0.25
run F3b RS_HEALTH_NOSOURCE_FALLBACK=2
run F4lit RS_KEEP_NOPROPER=lit
run F1N2F3 RS_SE_LEAD=0.78 RS_SE_LEAD_N=2 RS_HEALTH_NOSOURCE_FALLBACK=1
run off2
echo ALLDONE
