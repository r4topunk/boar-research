#!/bin/bash
# NUMGUARD-FINAL generation driver (MacBook, sequential, one llama-server at a time via run_ngf.sh/busy.sh).
# slice 26 (ngf-A-s42) + v0.1 60 (v01-ngf-on-s42), NUMGUARD=1, seed 42 (mkreq_mr.py).
set -u
A=<workspace>/rnd/research/coordinator/arms; N=$A/numguard; R=$N/runs; MK=$A/mathroute/tools/mkreq_mr.py
SL=<workspace>/boar-eval/bench/slices/mathroute-v1/questions.jsonl; V1=<workspace>/boar-eval/bench/v0.1/questions.public.jsonl
T=<workspace>/kiln-local/be-0cfd4a77-cut7-numguard-r2; t0=$(date +%s)
for pair in "ngf-A-s42:$SL" "v01-ngf-on-s42:$V1"; do run=${pair%%:*}; q=${pair#*:}
  python3 -I $MK $q $run cut7+numguard-final $R/$run.requests.jsonl || exit 1
  env NUMGUARD=1 NUMGUARD_NORETRIEVE=1 DUMP=$R/$run.prompts.jsonl $N/tools/run_ngf.sh $T $R/$run.requests.jsonl $R/$run.traces.jsonl || { echo "FAIL $run"; exit 1; }
done
echo "gen done wall $(( $(date +%s) - t0 )) s"
