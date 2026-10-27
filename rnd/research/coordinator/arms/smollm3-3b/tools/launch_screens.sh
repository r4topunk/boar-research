#!/bin/bash
# SMOLLM3-3B stage 1: 2 variants x {K0, K1} gate v2 screens (SMOL-criterion.md §2), launched in the background; the mini slot lock queues them.
# Rerunning resumes (cached generation / judgments).
A=<workspace>/rnd/research/coordinator/arms; G=$A/smollm3-3b; mkdir -p $G/screens/logs
for v in "smollm3-3b:$G/smollm3-3b.patch" "smollm3-3b-eng:$G/smollm3-3b-engsamp.patch"; do ARM=${v%%:*}; P=${v#*:}
  for K in K0 K1; do
    OUT_BASE=$G/screens SCREEN_JSON=$A/null-cal/pool/screen2-$K.json CRITERION=$G/SMOL-criterion.md \
      nohup bash $A/null-cal/tools/run_pool.sh $ARM $K $A/null-cal/pool/screen2-$K.ids $P >> $G/screens/logs/$ARM-$K.log 2>&1 < /dev/null &
    sleep 8
  done
done
