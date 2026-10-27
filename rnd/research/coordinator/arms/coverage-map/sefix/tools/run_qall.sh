#!/bin/bash
# SEFIX QFORM 432 six-file replays, after the MAIN queue (sequential)
cd <workspace>/rnd/research/coordinator/arms/coverage-map/sefix
until grep -q ALLDONE replays/run_all2.log; do sleep 5; done
run() { lab=$1; shift; f=replays/qform.$lab.jsonl; [ -s $f ] && [ $(wc -l < $f) -ge 432 ] && return; bash tools/run_qform.sh $lab "$@"; }
run off RS_X=0
run F2 RS_SE_MAXDF=0.25
run F3 RS_HEALTH_NOSOURCE_FALLBACK=1
run F4 RS_KEEP_NOPROPER=1
run FULL RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_HEALTH_NOSOURCE_FALLBACK=1 RS_KEEP_NOPROPER=1
run FULLg RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_HEALTH_NOSOURCE_FALLBACK=1 RS_KEEP_NOPROPER=1
echo QALLDONE
