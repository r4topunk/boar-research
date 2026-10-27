#!/usr/bin/env bash
# Follow-up to PARALLEL.md: node backend (the L1/L2 default), retrieval-inkit 24, 4B Android 12 GB, seed 42: --threads 4 vs 8 vs 6.
set -uo pipefail
cd <workspace>
until grep -q REPLYLANG-DONE <scratch> 2>/dev/null; do sleep 20; done
CFG=boar-eval/runs/night-2026-10-01/and-qwen-s42.config.json; T=rnd/kiln/l1/thread-bench.times.tsv
printf 'label\trc\twall_s\tload1_before\tend\n' > $T
for th in 4 8 6; do
  la=$(<on the mini> 'sysctl -n vm.loadavg' | awk '{print $2}'); s=$(date +%s)
  BOAR_EVAL_RUNNER_DIR=be-kiln rnd/kiln/l1/run_l1.sh retrieval-inkit node-t$th $CFG --no-judge -- --threads $th > <scratch> 2>&1
  printf 'node-t%s\t%s\t%s\t%s\t%s\n' $th $? $(( $(date +%s) - s )) "$la" "$(date +%H:%M)" | tee -a $T
done
echo THREAD-BENCH-DONE
