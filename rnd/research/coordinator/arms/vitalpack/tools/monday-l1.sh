#!/usr/bin/env bash
# Monday 2026-10-12 first judge step (week caps reset): L1 Haiku N=4 on both pre-generated slices, in stage order, then print the rules.
# Each l1 = 40 Haiku calls (20 ids x 2 orders). Run from the repo root. Stops at the first failure (fail-closed rc 5/6).
set -u; A=rnd/research/coordinator/arms
echo "== $(date +%H:%M) VITALADD L1"; $A/_lib/arm.sh $A/vitalpack/arm.conf l1 va-A-v02-s42-slice $A/random20-v02.ids AvsH-slice || { echo "L1 VITALADD rc=$?"; exit 1; }
echo "== $(date +%H:%M) DEEPCOVER L1"; $A/_lib/arm.sh $A/deepcover/arm.conf l1 dc-C-v02-s42-slice $A/random20-v02.ids CvsH-slice || { echo "L1 DEEPCOVER rc=$?"; exit 1; }
cat $A/vitalpack/aggregates/L1-rule-*slice*.txt $A/deepcover/aggregates/L1-rule-*slice*.txt 2>/dev/null; echo "== $(date +%H:%M) done"
