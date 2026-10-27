#!/bin/bash
# NOWIKI batch: MAIN 3 kits sequential first (timed set), then self-tests and topics.
D=<workspace>/rnd/research/coordinator/arms/coverage-map/nowiki
for k in K13 NOWIKI NOWIKI2; do bash $D/tools/run.sh main $k; done
for k in K13 NOWIKI NOWIKI2; do for g in on-k13 on-k13+qa-ethereum-se on-k13+qa-bitcoin-se; do bash $D/tools/run.sh st $k $g; done; bash $D/tools/run.sh t27 $k; done
echo ALLDONE
