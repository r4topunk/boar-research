#!/bin/bash
cd <workspace>/rnd/research/coordinator/arms/coverage-map/searchpar/r1
for m in cos mix; do ./run_qform.sh $m $m; done > replays/run_qf.log 2>&1
echo ALLDONE >> replays/run_qf.log
