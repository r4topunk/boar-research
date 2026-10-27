#!/bin/bash
# fetch a finished COMBINED mini job (traces, STATUS, run.log), drop the tree. usage: fetch.sh combined-main-s42
RUN=$1; M=MINI_HOST; J=<runner>/kiln/lp-screens/jobs/$RUN; C=<workspace>/rnd/research/coordinator/arms/coverage-map/combined
while :; do s=$(ssh -T -n -o ConnectTimeout=20 $M "tail -1 $J/STATUS" 2>/dev/null); case $s in DONE) break;; FAIL*) echo "FAIL $RUN: $s"; exit 1;; esac; sleep 30; done
scp -q $M:$J/traces.jsonl $C/traces/$RUN.traces.jsonl && scp -q $M:$J/STATUS $C/logs/$RUN.status && scp -q $M:$J/run.log $C/logs/$RUN.run.log || exit 1
ssh -T -n $M "rm -rf $J/tree" || true
echo "$(date +%T) fetched $RUN rows=$(wc -l < $C/traces/$RUN.traces.jsonl)"
