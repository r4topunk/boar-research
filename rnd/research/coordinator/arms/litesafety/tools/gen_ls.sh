#!/bin/bash
# LITESAFETY generation driver: 4 runs, sequential (one llama-server at a time via run_ls.sh), seed 42; resumable (DONE skipped).
set -u
D=<workspace>/rnd/research/coordinator/arms/litesafety; R=$D/runs; t0=$(date +%s)
for r in probes-1p7b probes-4b v01-1p7b v01-4b; do
  grep -qx DONE $R/ls-$r-s42.traces.status 2>/dev/null || $D/tools/run_ls.sh $R/ls-$r.requests.jsonl $R/ls-$r-s42.traces.jsonl || { echo "FAIL $r"; exit 1; }
  echo "$r done $(( $(date +%s) - t0 )) s"
done
echo "gen done wall $(( $(date +%s) - t0 )) s"
