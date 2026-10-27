#!/bin/bash
cd <workspace>/rnd/research/coordinator/arms/coverage-map/w78
while [ "$(grep -c rc= replays-b/batchA.log)" -lt 6 ]; do sleep 5; done
for m in true extra; do for spec in "B 0" "N32 32" "N64 64" "N128 128" "B2 0"; do set -- $spec; tools/run_w78b_q.sh $m-$1 $m $2; done; done > replays-b/batchQ.log 2>&1
