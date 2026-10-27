#!/bin/bash
# sequential: MAIN 97 cos, mix; QFORM 432 six-file cos, mix (QFORM off = g2-fullkit qform.v3-extra.jsonl, same recipe)
cd <workspace>/rnd/research/coordinator/arms/coverage-map/searchpar/r1
for m in cos mix; do ./run_main.sh $m $m; done > replays/run_all.log 2>&1
for m in cos mix; do ./run_qform.sh $m $m; done >> replays/run_all.log 2>&1
echo ALLDONE >> replays/run_all.log
