#!/bin/bash
# DT256 stage 3 on arm.sh: full s42 → L1 (51 ids) → on CONTINUE: Opus s42, s43 generation, Opus s43, two-seed scales beside T, H, D.
set -u; A=<workspace>/rnd/research/coordinator/arms; C=$A/dt256/arm.conf; B=<private held-out dir>; IDS=$B/runs-cut6/judged.ids; AG=$A/dt256/aggregates
export WAIT_EVERY=300 WAIT_HARD=9000
$A/_lib/arm.sh $C launch $B/runs-dt256/dq-Q-vpara-s42.requests.jsonl dq-Q-vpara-s42 && $A/_lib/arm.sh $C wait dq-Q-vpara-s42 || exit 3
$A/_lib/arm.sh $C l1 dq-Q-vpara-s42 $IDS full-s42 2>&1 | grep -v " boar" | tail -3
grep -q CONTINUE $AG/L1-rule-full-s42.txt || { echo STAGE3-NO; exit 0; }
$A/_lib/arm.sh $C judge 42 2>&1 | tail -3
$A/_lib/arm.sh $C launch $B/runs-dt256/dq-Q-vpara-s43.requests.jsonl dq-Q-vpara-s43 && $A/_lib/arm.sh $C wait dq-Q-vpara-s43 || exit 3
SKIPJUDGE=1 $A/_lib/arm.sh $C l1 dq-Q-vpara-s43 $IDS full-s43 2>&1 | tail -1
$A/_lib/arm.sh $C judge 43 2>&1 | tail -3
$A/_lib/arm.sh $C scales "42 43" 2>&1 | grep -v "^{\"comparison" | head -14
$A/_lib/arm.sh $C exposure
echo FULL-DONE
