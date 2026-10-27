#!/bin/bash
# LONGSESSION addendum 1 driver: 15-turn extension of ls02, ls06, ls08 (MacBook, one llama-server at a time via run_ls.sh, WAIT_MAX 90 min).
# B: ls-ext15-standalone-s42 = turns 6-15 alone. A: ls-ext15-session-s42 = waves t6..t15; history from ls-session-s42 (turns 1-5) + earlier ext waves.
set -u
A=<workspace>/rnd/research/coordinator/arms/longsession; R=$A/runs; Q=<workspace>/boar-eval/bench/slices/longsession-v1/questions.jsonl
SS=ls02,ls06,ls08; ST=ls-ext15-standalone-s42; SE=ls-ext15-session-s42; t0=$(date +%s); export WAIT_MAX=90
MIN_TURN=6 python3 -I $A/tools/mkreq_ls.py standalone $Q $ST $R/$ST.requests.jsonl $SS || exit 1
DUMP=$R/$ST.prompts.jsonl $A/tools/run_ls.sh $R/$ST.requests.jsonl $R/$ST.traces.jsonl || { echo "FAIL $ST"; exit 1; }
: > $R/$SE.traces.jsonl
for k in 6 7 8 9 10 11 12 13 14 15; do W=$SE-t$k
  cat $R/ls-session-s42.traces.jsonl $R/$SE.traces.jsonl > $R/$SE.prev.jsonl
  python3 -I $A/tools/mkreq_ls.py session $Q $SE $R/$W.requests.jsonl $k $R/$SE.prev.jsonl $SS || exit 1
  DUMP=$R/$W.prompts.jsonl $A/tools/run_ls.sh $R/$W.requests.jsonl $R/$W.traces.jsonl || { echo "FAIL $W"; exit 1; }
  cat $R/$W.traces.jsonl >> $R/$SE.traces.jsonl
done
rm -f $R/$SE.prev.jsonl; cat $R/$SE-t?.requests.jsonl $R/$SE-t1?.requests.jsonl > $R/$SE.requests.jsonl
echo "gen ext15 done wall $(( $(date +%s) - t0 )) s; rows standalone $(wc -l < $R/$ST.traces.jsonl) session $(wc -l < $R/$SE.traces.jsonl)"
