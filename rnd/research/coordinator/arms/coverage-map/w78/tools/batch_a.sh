#!/bin/bash
cd <workspace>/rnd/research/coordinator/arms/coverage-map/w78
for spec in "D32 32 0" "D64 64 0" "K32 32 32" "K64 64 32" "D128 128 0" "B2 0 0"; do tools/run_w78b_a.sh $spec; done > replays-b/batchA.log 2>&1
