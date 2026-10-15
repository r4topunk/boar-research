#!/bin/bash
# STACK generation chain (criterion sha 56ed7ccf…): run_stack.sh per request file in order; skips runs whose traces exist with status DONE.
# Stops at the first failure. Usage: nohup tools/chain.sh [runId ...] >> runs/chain.log 2>&1 &
#   default order: the 9 self-test packs (st-<pack>-cut7-stack-s42), then v01-cut7-stack-off-s42, v01-cut7-stack-on-s42
set -u
H=$(cd "$(dirname "$0")/.." && pwd); R=$H/runs
RUNS=("$@"); if [ ${#RUNS[@]} -eq 0 ]; then
  for p in qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en; do RUNS+=(st-$p-cut7-stack-s42); done
  RUNS+=(v01-cut7-stack-off-s42 v01-cut7-stack-on-s42); fi
for run in "${RUNS[@]}"; do
  tr=$R/$run.traces.jsonl
  if [ -s "$tr" ] && [ "$(tail -1 "$R/$run.traces.status" 2>/dev/null)" = DONE ]; then echo "$(date '+%F %T') skip $run (DONE)"; continue; fi
  echo "$(date '+%F %T') start $run"
  "$H/tools/run_stack.sh" "$R/$run.requests.jsonl" "$tr"; rc=$?
  echo "$(date '+%F %T') end $run rc=$rc lines=$(wc -l < "$tr" 2>/dev/null)"
  [ $rc -eq 0 ] || { echo "chain STOP at $run"; exit $rc; }
done
echo "$(date '+%F %T') chain complete"
