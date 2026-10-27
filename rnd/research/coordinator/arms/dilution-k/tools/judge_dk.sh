#!/bin/bash
# DILUTION-K judge (MacBook): Haiku 5.5-low judge.v1-low, N = 4, both orders, via deepthink/tools/shard_judge.sh; only texts with no judged twin
# (cc_agg.py --need); preflight with the frozen criterion; check_judgments.py after (fail closed); one ledger row per arm. Usage: judge_dk.sh k1|k2|k3
set -u
H=<workspace>/rnd/research/coordinator/arms/dilution-k; L=$H/../_lib; SJ=$H/../deepthink/tools/shard_judge.sh; B=<workspace>/boar-eval/bench/v0.1
C=$H/DILUTION-criterion.md; [ "$(shasum -a 256 $C | cut -d' ' -f1)" = "$(cut -d' ' -f1 $H/DILUTION-criterion.sha256)" ] || { echo "criterion sha mismatch"; exit 9; }
A=$1; TR=$H/traces/dilution-$A-K3-v01gold-s42.traces.jsonl; O=$H/judgments/dk-$A.judgments.jsonl; I=$H/judgments/dk-$A.jids
python3 -I $H/tools/dk_agg.py --need $A $I; n=$(wc -l < $I | tr -d ' '); [ "$n" = 0 ] && { echo "nothing to judge $A"; exit 0; }
used=$(awk -F'calls=' '{split($2,a," "); s+=a[1]} END{print s+0}' $H/runs/logs/calls.ledger 2>/dev/null); [ $((used + 2*n)) -le 200 ] || { echo "cap 200 would be exceeded ($used + $((2*n)))"; exit 7; }
SYS=dilution-$A-haiku55-low
PREFLIGHT_PROBE_IDS=0 PREFLIGHT_SET=v01 PREFLIGHT_CRITERION=$C PREFLIGHT_DECLARED_CALLS=$((2*n)) bash $SJ --preflight $TR $O $B $I $SYS 4 haiku || { echo "PREFLIGHT FAIL"; exit 8; }
bash $SJ $TR $O $B $I $SYS 4 haiku > $H/runs/logs/dk-$A.judge.log 2>&1; rc=$?
python3 -I $L/check_judgments.py $O $I dk-$A || rc=1
echo "$(date '+%F %T') dk-$A ids=$n calls=$((2*n)) rc=$rc" >> $H/runs/logs/calls.ledger; tail -1 $H/runs/logs/calls.ledger; exit $rc
