#!/bin/bash
# MATHROUTE generation driver (MacBook, sequential). Usage: gen_mr.sh <prefix> [ids csv]   (prefix: mr-smoke | mr)
set -u
A=<workspace>/rnd/research/coordinator/arms/mathroute; R=$A/runs; Q=<workspace>/boar-eval/bench/slices/mathroute-v1/questions.jsonl
K=<workspace>/kiln-local; P=$1; IDS=${2:-}; t0=$(date +%s)
for arm in A B C; do run=$P-$arm-s42
  if [ $arm = A ]; then tree=$K/be-0cfd4a77-cut7; label=cut7; envs=(); else tree=$K/be-0cfd4a77-cut7-mathroute; label=cut7+mathroute; fi
  [ $arm = B ] && envs=(MATHROUTE_NOCALC=1 MATHROUTE_RETRIEVE=off); [ $arm = C ] && envs=(MATHROUTE_NOCALC=1 MATHROUTE_RETRIEVE=on)
  python3 -I $A/tools/mkreq_mr.py $Q $run $label $R/$run.requests.jsonl $IDS || exit 1
  env ${envs[@]+"${envs[@]}"} DUMP=$R/$run.prompts.jsonl $A/tools/run_mr.sh $tree $R/$run.requests.jsonl $R/$run.traces.jsonl || { echo "FAIL $run"; exit 1; }
done
echo "gen $P done wall $(( $(date +%s) - t0 )) s"
