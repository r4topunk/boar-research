#!/bin/bash
# DT512-V02: launch s42 → wait → fetch/think → Opus judge → scales (one seed) → exposure. Progress/aggregates only.
set -u; A=<workspace>/rnd/research/coordinator/arms; C=$A/dt512v02/arm.conf; B=<private held-out dir>; IDS=$B/runs-deepvpara/judged.ids
export WAIT_EVERY=600 WAIT_HARD=12000
$A/_lib/arm.sh $C launch $B/runs-dt512v02/dhv-H-v02-s42.requests.jsonl dhv-H-v02-s42 && $A/_lib/arm.sh $C wait dhv-H-v02-s42 || exit 3
SKIPJUDGE=1 $A/_lib/arm.sh $C l1 dhv-H-v02-s42 $IDS full-s42 2>&1 | tail -2
$A/_lib/arm.sh $C judge 42 2>&1 | tail -3
$A/_lib/arm.sh $C scales "42" 2>&1 | grep -v "^{\"comparison" | head -12
$A/_lib/arm.sh $C exposure
echo V02-DONE
