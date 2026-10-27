#!/bin/bash
# CHATFAIL S1 v0.1 non-regression judge: Haiku 5.5-low judge.v1 via shard_judge.sh, N = 4, both orders, seed 7. Usage: run_v01_judge.sh <C0|A1> [preflight]
# Budget (criterion): Haiku 57 x 2 orders x 2 arms = 228 (+ <= 8 preflight).
set -u
H=<workspace>/rnd/research/coordinator/arms/chatfail; A=<workspace>/rnd/research/coordinator/arms; arm=$1
B=<workspace>/boar-eval/bench/v0.1; T=$H/tools/out/traces-v01-$arm.jsonl; O=$H/tools/out/judgments-v01-$arm.jsonl; IDS=$H/tools/out/ids-v01.ids; SYS=chatfail-s1-v01-$arm-haiku55-low
export PREFLIGHT_SET=v01 PREFLIGHT_DECLARED_CALLS=114 PREFLIGHT_PROBE_IDS=1
if [ "${2:-}" = preflight ]; then exec "$A/deepthink/tools/shard_judge.sh" --preflight "$T" "$O" "$B" "$IDS" "$SYS" 4 haiku; fi
exec "$A/deepthink/tools/shard_judge.sh" "$T" "$O" "$B" "$IDS" "$SYS" 4 haiku
