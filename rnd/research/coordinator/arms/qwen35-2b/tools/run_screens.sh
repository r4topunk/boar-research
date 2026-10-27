#!/bin/bash
# QWEN35-2B stage-1 screens (GATE v2), sequential: V K0, V K1, E K0, E K1.
A=<workspace>/rnd/research/coordinator/arms; Q=<workspace>/rnd/research/coordinator/arms/qwen35-2b
for arm in q35v q35e; do
  P=$Q/qwen35-2b.patch; [ $arm = q35e ] && P=$Q/qwen35-2b-engsamp.patch
  for K in K0 K1; do
    OUT_BASE=$Q/screens SCREEN_JSON=$A/null-cal/pool/screen2-$K.json CRITERION=$Q/QWEN35-criterion.md bash $A/null-cal/tools/run_pool.sh $arm $K $A/null-cal/pool/screen2-$K.ids $P
    echo "EXIT $arm $K rc=$?"
  done
done
echo ALLSCREENS
