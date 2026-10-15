#!/bin/bash
# SELFTEST-DEEP local watcher: polls the mini chain every 5 min; post-processes each run once its STATUS is DONE (selftest_deep_post.sh). Exits when all 18 are judged
# or when the chain log shows a halt. Log: ../selftest-runs/deep/watch.log (chain log mirrored to chain.log).
H=$(cd "$(dirname "$0")/.." && pwd); D=$H/selftest-runs/deep; T=boar/runner/be-0cfd4a77-dt512/be-repo/runs
while :; do
  scp -q $RUNNER_HOST:boar/runner/stdeep-chain.log "$D/chain.log" 2>/dev/null
  left=0
  for r in $(cat "$D/runs.list"); do
    [ -s "$D/$r.floor_metrics.done" ] && continue; left=$((left+1))
    ssh -n $RUNNER_HOST "grep -cx DONE ~/$T/$r/STATUS" 2>/dev/null | grep -qx 1 || continue
    p=${r#st-}; p=${p%-dt512*}; np=""; case $r in *-nopack-*) np=--no-pack;; esac
    echo "$(date '+%F %T') post $r" >> "$D/watch.log"
    if bash "$H/tools/selftest_deep_post.sh" "$p" $np >> "$D/watch.log" 2>&1; then date '+%F %T' > "$D/$r.floor_metrics.done"; left=$((left-1)); else echo "$(date '+%F %T') post FAILED $r" >> "$D/watch.log"; fi
  done
  [ $left -eq 0 ] && { echo "$(date '+%F %T') ALL POSTED" >> "$D/watch.log"; exit 0; }
  grep -q "halt" "$D/chain.log" 2>/dev/null && { echo "$(date '+%F %T') chain halted, watcher exits" >> "$D/watch.log"; exit 2; }
  sleep 300
done
