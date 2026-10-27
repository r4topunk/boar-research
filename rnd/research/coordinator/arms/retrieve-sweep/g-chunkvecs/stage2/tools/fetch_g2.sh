#!/bin/bash
# wait for both mini jobs, fetch traces/status/log
M=MINI_HOST; H=<workspace>/rnd/research/coordinator/arms/retrieve-sweep/g-chunkvecs/stage2
for W in ctl arm; do J=<runner>/kiln/lp-screens/jobs/g2-$W
  until s=$(ssh -T -n -o ConnectTimeout=20 $M "tail -1 $J/STATUS" 2>/dev/null); case $s in DONE|FAIL*) true;; *) false;; esac; do sleep 20; done
  echo "$W $s"; scp -q $M:$J/traces.jsonl $H/traces/g2-$W.traces.jsonl; scp -q $M:$J/STATUS $H/logs/g2-$W.status; scp -q $M:$J/run.log $H/logs/g2-$W.run.log
  scp -q $M:$J/requests.jsonl /dev/null 2>/dev/null
done; echo FETCHED
