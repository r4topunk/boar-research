#!/bin/bash
# JAN-V1-EDGE stage 1: 2 variants x {K0, K1} gate v2 screens (JAN-criterion.md §2), launched in the background; mini slots queue them.
A=<workspace>/rnd/research/coordinator/arms; G=$A/jan-v1-edge; mkdir -p $G/screens/logs
for v in "jan-v1-edge:$G/jan-v1-edge.patch" "jan-v1-edge-eng:$G/jan-v1-edge-engsamp.patch"; do ARM=${v%%:*}; P=${v#*:}
  for K in K0 K1; do
    OUT_BASE=$G/screens SCREEN_JSON=$A/null-cal/pool/screen2-$K.json CRITERION=$G/JAN-criterion.md \
      nohup bash $A/null-cal/tools/run_pool.sh $ARM $K $A/null-cal/pool/screen2-$K.ids $P > $G/screens/logs/$ARM-$K.log 2>&1 < /dev/null &
    sleep 8
  done
done
