#!/bin/bash
# second pass of the 12 replays, warm file cache, stock/gidf interleaved per N: wall repeat + kept-list determinism check
cd <workspace>/rnd/research/coordinator/arms/coverage-map/compose
for N in 0 2 4 6 8 10; do for V in stock gidf; do bash tools/run_rerun.sh $N $V; done; done; echo ALLDONE
