#!/bin/bash
# GEMMA4-E2B stage 1: 2 variants x {K0, K1} gate v2 screens (GEMMA4-criterion.md §2), launched in the background; mini slots queue them.
A=<workspace>/rnd/research/coordinator/arms; G=$A/gemma4-e2b; mkdir -p $G/screens/logs
for v in "gemma4-e2b:$G/gemma4-e2b.patch" "gemma4-e2b-eng:$G/gemma4-e2b-engsamp.patch"; do ARM=${v%%:*}; P=${v#*:}
  for K in K0 K1; do
    OUT_BASE=$G/screens SCREEN_JSON=$A/null-cal/pool/screen2-$K.json CRITERION=$G/GEMMA4-criterion.md \
      nohup bash $A/null-cal/tools/run_pool.sh $ARM $K $A/null-cal/pool/screen2-$K.ids $P > $G/screens/logs/$ARM-$K.log 2>&1 < /dev/null &
    sleep 8
  done
done
