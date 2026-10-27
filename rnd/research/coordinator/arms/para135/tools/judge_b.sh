#!/bin/bash
# PARA135 set B judge (MacBook): Haiku 5.5-low judge.v1-low, N 4 shards, both orders, all 51 CV5 ids per arm (style17-detailed recipe). Usage: judge_b.sh N
set -u
N=$1; A=<workspace>/rnd/research/coordinator/arms; D=$A/para135; SJ=$A/deepthink/tools/shard_judge.sh; L=$A/_lib; BE=<workspace>/boar-eval/bench/v0.1
RUN=p135-b-p$N-s42; TR=$D/gen/$RUN/traces.jsonl; J=$D/judge/b; mkdir -p $J; O=$J/$RUN-v01.judgments.jsonl; I=$D/../native-parity/cv5-51.ids
m=$(grep -c . $I); SYS=para135-$RUN-v01-haiku55-low
if python3 -I $L/check_judgments.py $O $I > /dev/null 2>&1; then echo "judged already $RUN"; exit 0; fi
env PREFLIGHT_PROBE_IDS=0 PREFLIGHT_SET=v01 PREFLIGHT_DECLARED_CALLS=$((2*m)) PREFLIGHT_CRITERION=$D/PARA135-criterion.md bash $SJ --preflight $TR $O $BE $I $SYS 4 haiku || { echo "PREFLIGHT FAIL"; exit 8; }
t=$(date +%s); bash $SJ $TR $O $BE $I $SYS 4 haiku > $J/$RUN.judge.log 2>&1 || { echo "judge FAIL"; exit 1; }
python3 -I $L/check_judgments.py $O $I "$RUN" || exit 1
echo "$(date '+%F %T') $RUN ids=$m calls=$((2*m)) wall=$(( $(date +%s) - t ))s" >> $J/calls.log; echo "judged $RUN calls=$((2*m))"
