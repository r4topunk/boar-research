#!/bin/bash
# QUANTLITE mini batch driver: sequential per-pack runs. Usage (nohup): quantlite-batch.sh <dir> <prefix> <q8|q4>; writes <dir>/<prefix>.BATCH
set -u; D=$(cd "$1" && pwd); PFX=$2; Q=$3; B=$D/$PFX.BATCH; H=$(cd "$(dirname "$0")" && pwd)
echo "batch start $(date '+%F %T')" > $B
for r in $D/$PFX-*.requests.jsonl; do o=${r%.requests.jsonl}.traces.jsonl
  if [ -s $o ] && grep -qx DONE ${o%.jsonl}.status 2>/dev/null; then echo "skip $(basename $r)" >> $B; continue; fi
  t=$(date +%s); bash $H/quantlite-remote-run.sh $r $o $Q || { echo "FAIL $(basename $r)" >> $B; echo BATCH-FAIL >> $B; exit 2; }
  echo "done $(basename $r) wall=$(( $(date +%s) - t ))s" >> $B
done
echo BATCH-DONE >> $B
