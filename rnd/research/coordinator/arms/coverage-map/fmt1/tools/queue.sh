#!/bin/bash
# FMT1 sequential queue (wall comparable)
D=<workspace>/rnd/research/coordinator/arms/coverage-map/fmt1
for a in P400 P400f65 P2000 P2000f65 FULL FULLf65; do bash $D/tools/run_fmt1.sh main $a; done
for a in P400f65 P2000 P2000f65 FULL FULLf65; do bash $D/tools/run_fmt1.sh t27 $a; done
echo ALLDONE
