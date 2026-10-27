#!/bin/bash
# LITEREADERS generation driver (MacBook, sequential). Usage: nohup gen.sh <slice: smoke|r20> > runs/gen-<slice>.log 2>&1 &
# Resumable: skips runs whose traces row count = requests row count and status DONE.
H=<workspace>/rnd/research/coordinator/arms/litereaders; R=$H/runs; SL=$1
for X in $(grep -- "-$SL-" $R/RUNS); do
  n=$(wc -l < $R/$X.requests.jsonl | tr -d ' ')
  if [ -s $R/$X.traces.jsonl ] && [ "$(wc -l < $R/$X.traces.jsonl | tr -d ' ')" = $n ] && grep -q DONE $R/$X.traces.status 2>/dev/null; then echo "skip $X"; continue; fi
  w=0; while bash $H/../headpass-st/tools/busy.sh > /dev/null 2>&1; do [ $w = 0 ] && echo "wait-busy $X $(date +%T)"; w=1; sleep 30; done
  rm -f $R/$X.traces.jsonl; t=$(date +%s)
  bash $H/tools/run_lr.sh $R/$X.requests.jsonl $R/$X.traces.jsonl || { echo "FAIL $X"; tail -3 $R/$X.traces.log; exit 2; }
  echo "$(date +%T) done $X n=$n wall=$(( $(date +%s) - t ))s"
done; echo ALLDONE $SL
