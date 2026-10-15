#!/bin/bash
# LONGSESSION generation driver (MacBook, sequential, one llama-server at a time via run_ls.sh).
# Usage: gen_ls.sh <prefix> [sessions csv]   e.g. gen_ls.sh ls-smoke ls01   |   gen_ls.sh ls
#   <prefix>-standalone-s42: all items of the sessions, no history (one adapter call).
#   <prefix>-session-s42: 5 waves; wave k = turn k of every session with history = turns 1..k-1 (questions + this run's own earlier answers).
#   Waves concatenated into <prefix>-session-s42.traces.jsonl. Stops on the first failure.
set -u
A=$BOAR_WS/rnd/research/coordinator/arms/longsession; R=$A/runs; Q=$BOAR_WS/boar-eval/bench/slices/longsession-v1/questions.jsonl
P=$1; SS=${2:-}; ST=$P-standalone-s42; SE=$P-session-s42; t0=$(date +%s)
python3 -I $A/tools/mkreq_ls.py standalone $Q $ST $R/$ST.requests.jsonl $SS || exit 1
DUMP=$R/$ST.prompts.jsonl $A/tools/run_ls.sh $R/$ST.requests.jsonl $R/$ST.traces.jsonl || { echo "FAIL $ST"; exit 1; }
: > $R/$SE.traces.jsonl
for k in 1 2 3 4 5; do W=$SE-t$k
  python3 -I $A/tools/mkreq_ls.py session $Q $SE $R/$W.requests.jsonl $k $R/$SE.traces.jsonl $SS || exit 1
  DUMP=$R/$W.prompts.jsonl $A/tools/run_ls.sh $R/$W.requests.jsonl $R/$W.traces.jsonl || { echo "FAIL $W"; exit 1; }
  cat $R/$W.traces.jsonl >> $R/$SE.traces.jsonl
done
cat $R/$SE-t?.requests.jsonl > $R/$SE.requests.jsonl
echo "gen $P done wall $(( $(date +%s) - t0 )) s; rows standalone $(wc -l < $R/$ST.traces.jsonl) session $(wc -l < $R/$SE.traces.jsonl)"
