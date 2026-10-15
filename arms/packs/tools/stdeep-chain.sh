#!/bin/bash
# SELFTEST-DEEP mini-side chain: runs stdeep-remote-run.sh <run> D noplaces for each run id in order (requests already in be-repo/runs/<run>/requests.jsonl).
# Skips runs whose STATUS has DONE; stops at the first FAIL. Log: $RUNNER_ROOT/runner/stdeep-chain.log (copied locally to selftest-runs/deep/chain.log on fetch).
# Usage (on the mini, under nohup): stdeep-chain.sh <runId>...
R=$RUNNER_ROOT/runner/be-0cfd4a77-dt512/be-repo/runs; LOG=$RUNNER_ROOT/runner/stdeep-chain.log
echo "chain start $(date '+%F %T') runs=$#" >> $LOG
for run in "$@"; do
  [ -f $RUNNER_ROOT/runner/stdeep-chain.STOP ] && { echo "$(date '+%F %T') STOP file present, halting before $run" >> $LOG; exit 4; }
  grep -qx DONE $R/$run/STATUS 2>/dev/null && { echo "$(date '+%F %T') skip $run (DONE)" >> $LOG; continue; }
  [ -s $R/$run/requests.jsonl ] || { echo "$(date '+%F %T') FAIL $run: no requests" >> $LOG; exit 2; }
  echo "$(date '+%F %T') start $run" >> $LOG
  bash -l $RUNNER_ROOT/runner/stdeep-remote-run.sh $run D noplaces > $RUNNER_ROOT/runner/dt512-$run.nohup.log 2>&1 < /dev/null; rc=$?
  df -g ~ | awk 'NR==2{print "free_gib " $4}' | sed "s/^/$(date '+%F %T') /" >> $LOG
  echo "$(date '+%F %T') end $run rc=$rc $(tail -1 $R/$run/STATUS)" >> $LOG
  [ $rc -eq 0 ] || { echo "$(date '+%F %T') chain halted on $run" >> $LOG; exit $rc; }
  avail=$(df -g ~ | awk 'NR==2{print $4}'); [ "$avail" -lt 25 ] && { echo "$(date '+%F %T') disk $avail GiB < 25, halting" >> $LOG; exit 5; }
done
echo "chain end $(date '+%F %T') ALL-DONE" >> $LOG
