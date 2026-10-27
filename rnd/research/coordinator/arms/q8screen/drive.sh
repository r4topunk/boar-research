#!/bin/bash
cd <workspace>/rnd/research/coordinator/arms
J=<runner>/kiln/lp-screens/jobs/q8-K0-screen2-K0-s42
while ! <on the mini> "tail -1 $J/STATUS" 2>/dev/null | grep -qE '^(DONE|FAIL)'; do sleep 30; done
for K in K0 K1; do OUT_BASE=$PWD/q8screen/arms SCREEN_JSON=null-cal/pool/screen2-$K.json bash null-cal/tools/run_pool.sh q8 $K null-cal/pool/screen2-$K.ids $PWD/q8screen/q8.patch > q8screen/run-$K.log 2>&1; done
echo ALLFINISHED > q8screen/drive.done
