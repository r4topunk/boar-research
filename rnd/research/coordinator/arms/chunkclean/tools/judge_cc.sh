#!/bin/bash
# CHUNKCLEAN judge (MacBook): Haiku 5.5-low judge.v1-low, N = 4, both orders, via deepthink/tools/shard_judge.sh; only texts with no judged twin
# (cc_agg.py --need); preflight with the frozen criterion; check_judgments.py after (fail closed); one ledger row per arm. Usage: judge_cc.sh C|P
set -u
H=<workspace>/rnd/research/coordinator/arms/chunkclean; L=$H/../_lib; SJ=$H/../deepthink/tools/shard_judge.sh; B=<workspace>/boar-eval/bench/v0.1
C=$H/CHUNKCLEAN-criterion.md; [ "$(shasum -a 256 $C | cut -d' ' -f1)" = "$(cut -d' ' -f1 $H/CHUNKCLEAN-criterion.sha256)" ] || { echo "criterion sha mismatch"; exit 9; }
A=$1; TR=$H/traces/chunkclean-$A-K3-v01gold-s42.traces.jsonl; O=$H/judgments/cc-$A.judgments.jsonl; I=$H/judgments/cc-$A.jids
python3 -I $H/tools/cc_agg.py --need $A $I; n=$(wc -l < $I | tr -d ' '); [ "$n" = 0 ] && { echo "nothing to judge $A"; exit 0; }
used=$(awk -F'calls=' '{split($2,a," "); s+=a[1]} END{print s+0}' $H/runs/logs/calls.ledger 2>/dev/null); [ $((used + 2*n)) -le 200 ] || { echo "cap 200 would be exceeded ($used + $((2*n)))"; exit 7; }
SYS=chunkclean-$A-haiku55-low
PREFLIGHT_PROBE_IDS=0 PREFLIGHT_SET=v01 PREFLIGHT_CRITERION=$H/CHUNKCLEAN-budget.md PREFLIGHT_DECLARED_CALLS=$((2*n)) bash $SJ --preflight $TR $O $B $I $SYS 4 haiku || { echo "PREFLIGHT FAIL"; exit 8; }
bash $SJ $TR $O $B $I $SYS 4 haiku > $H/runs/logs/cc-$A.judge.log 2>&1; rc=$?
python3 -I $L/check_judgments.py $O $I cc-$A || rc=1
echo "$(date '+%F %T') cc-$A ids=$n calls=$((2*n)) rc=$rc" >> $H/runs/logs/calls.ledger; tail -1 $H/runs/logs/calls.ledger; exit $rc
