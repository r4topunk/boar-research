#!/bin/bash
# NUMGUARD generation driver (MacBook, sequential, one llama-server at a time via run_ng.sh/busy.sh).
# Usage: gen_ng.sh on|off   on: slice 26 (ng-A-s42) + v0.1 60 (v01-ng-on-s42) with NUMGUARD=1; off: v0.1 60 OFF control (v01-ng-off-s42).
set -u
A=<workspace>/rnd/research/coordinator/arms; N=$A/numguard; R=$N/runs; MK=$A/mathroute/tools/mkreq_mr.py
SL=<workspace>/boar-eval/bench/slices/mathroute-v1/questions.jsonl; V1=<workspace>/boar-eval/bench/v0.1/questions.public.jsonl
T=<workspace>/kiln-local/be-0cfd4a77-cut7-numguard; t0=$(date +%s)
if [ "$1" = on ]; then
  for pair in "ng-A-s42:$SL" "v01-ng-on-s42:$V1"; do run=${pair%%:*}; q=${pair#*:}
    python3 -I $MK $q $run cut7+numguard $R/$run.requests.jsonl || exit 1
    env NUMGUARD=1 DUMP=$R/$run.prompts.jsonl $N/tools/run_ng.sh $T $R/$run.requests.jsonl $R/$run.traces.jsonl || { echo "FAIL $run"; exit 1; }
  done
else
  run=v01-ng-off-s42; python3 -I $MK $V1 $run cut7+numguard $R/$run.requests.jsonl || exit 1
  env -u NUMGUARD DUMP=$R/$run.prompts.jsonl $N/tools/run_ng.sh $T $R/$run.requests.jsonl $R/$run.traces.jsonl || { echo "FAIL $run"; exit 1; }
fi
echo "gen $1 done wall $(( $(date +%s) - t0 )) s"
