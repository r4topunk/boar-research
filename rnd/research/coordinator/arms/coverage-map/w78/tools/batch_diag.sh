#!/bin/bash
cd <workspace>/rnd/research/coordinator/arms/coverage-map/w78
for spec in "D256 256 0" "D512 512 0"; do tools/run_w78b_a.sh $spec; done > replays-b/batchDiagA.log 2>&1
for m in true extra; do for spec in "N256 256" "N512 512"; do set -- $spec; tools/run_w78b_q.sh $m-$1 $m $2; done; done > replays-b/batchDiagQ.log 2>&1
