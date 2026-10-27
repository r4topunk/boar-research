#!/bin/bash
# CROWDQ arm P generation chain: run_all9.sh per pack in order; skips packs whose traces exist with status DONE.
# Stops at the first failure. Usage: nohup tools/chain.sh [pack ...] >> runs/chain.log 2>&1 &
set -u
H=$(cd "$(dirname "$0")/.." && pwd); R=$H/runs
PACKS=("$@"); [ ${#PACKS[@]} -eq 0 ] && PACKS=(qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en)
for p in "${PACKS[@]}"; do
  run=st-$p-cut7-all9-s42; tr=$R/$run.traces.jsonl
  if [ -s "$tr" ] && [ "$(tail -1 "$R/$run.traces.status" 2>/dev/null)" = DONE ]; then echo "$(date '+%F %T') skip $p (DONE)"; continue; fi
  echo "$(date '+%F %T') start $p"
  "$H/tools/run_all9.sh" "$R/$run.requests.jsonl" "$tr"; rc=$?
  echo "$(date '+%F %T') end $p rc=$rc lines=$(wc -l < "$tr" 2>/dev/null)"
  [ $rc -eq 0 ] || { echo "chain STOP at $p"; exit $rc; }
done
echo "$(date '+%F %T') chain complete"
