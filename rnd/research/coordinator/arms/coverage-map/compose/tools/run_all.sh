#!/bin/bash
# the 12 COMPOSE replays, sequential (wall comparable); N=0 stock may already exist
cd <workspace>/rnd/research/coordinator/arms/coverage-map/compose
for N in 0 2 4 6 8 10; do for V in stock gidf; do
  f=replays/main.N$N.$V.jsonl; [ -s $f ] && [ $(wc -l < $f) -ge 97 ] && continue
  bash tools/run_compose.sh $N $V; done; done; echo ALLDONE
