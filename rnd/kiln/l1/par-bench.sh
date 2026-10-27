#!/usr/bin/env bash
# PARALLEL.md measurement: retrieval-inkit (24), Android 12 GB 4B (and-qwen-s42 config), seed 42, llama-server b11010.
set -uo pipefail
cd <workspace>
CFG=boar-eval/runs/night-2026-10-01/and-qwen-s42.config.json
SRV=(--backend server --server-bin '<runner>/spikes/llama-b11010/build-cpu/bin/llama-server')
T=rnd/kiln/l1/par-bench.times.tsv
run() { # label, extra run.sh args...
  local label="$1"; shift
  local la; la=$(<on the mini> 'sysctl -n vm.loadavg' | awk '{print $2}')
  local s; s=$(date +%s)
  BOAR_EVAL_RUNNER_DIR=be-kiln rnd/kiln/l1/run_l1.sh retrieval-inkit "$label" $CFG --no-judge -- "${SRV[@]}" "$@" > <scratch> 2>&1
  local rc=$?
  printf '%s\t%s\t%s\t%s\t%s\n' "$label" "$rc" "$(( $(date +%s) - s ))" "$la" "$(date +%H:%M)" | tee -a $T
}
printf 'label\trc\twall_s\tload1_before\tend\n' > $T
# warm-up: seeds the app dirs of shards w2, w3 (w0, w1 warmed by the smoke run); not measured
BOAR_EVAL_RUNNER_DIR=be-kiln rnd/kiln/l1/run_l1.sh retrieval-inkit par-warm $CFG --no-judge -- --ids lan-exp-001,lan-exp-002,lan-rsn-001,lan-rsn-002 "${SRV[@]}" --parallel 4 > <scratch> 2>&1
run par-n1 --parallel 1
run par-n4 --parallel 4
run par-n2 --parallel 2
run par-n3 --parallel 3
run par-std
run par-n1rep --parallel 1
echo PAR-BENCH-DONE
