#!/bin/bash
cd <workspace>/rnd/research/coordinator/arms/coverage-map/searchpar
rm -f replays/dedupe.main.log replays/dedupe.qform.log
tools/run_main.sh r4 RS_DEDUPE=0.9 RS_DEDUPE_LOG=$PWD/replays/dedupe.main.log
for kb in "0.9 0.75" "1.5 0.75" "1.2 0.4" "0.9 0.4" "1.5 0.4"; do set -- $kb; tools/run_main.sh r3_k$1_b$2 RS_BM25_K1=$1 RS_BM25_B=$2; done
tools/run_qform.sh q6gidf RS_MERGE=gidf
tools/run_qform.sh q6r4 RS_MERGE=gidf RS_DEDUPE=0.9 RS_DEDUPE_LOG=$PWD/replays/dedupe.qform.log
echo QUEUE1DONE
