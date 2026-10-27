#!/bin/bash
# COMBINED judge (copy of sefix/ans-tools/judge_s43.sh); original: SEFIX-ALL seed-43 replicate judge (MacBook, Haiku 5.5-low judge.v1, N 4, both orders). Usage: judge_s43.sh <traces> <ids file> <out dir> <run id>
# Judges exactly the ids in the ids file (no control filter); units v01 / qa-cooking-se / qa-money-se; ledger line appended to <out dir>/calls.log (2 calls per id).
set -u
TR=$1; IDS=$2; D=$3; RUN=$4
A=<workspace>/rnd/research/coordinator/arms; LP=$A/litepacks; L=$A/_lib; SJ=$A/deepthink/tools/shard_judge.sh; BE=<workspace>/boar-eval/bench
mkdir -p $D
for u in v01 qa-cooking-se qa-money-se; do
  case $u in v01) B=$BE/v0.1; PS=v01; SEL="grep -Fx -f $LP/data/v01-57.ids";; *) B=$BE/selftest/$u; PS=st-$u; SEL="grep ^st-$u-";; esac
  O=$D/$RUN-$u.judgments.jsonl; I=$D/$RUN-$u.jids
  $SEL $IDS > $I || true; m=$(wc -l < $I | tr -d ' ')
  [ "$m" = 0 ] && { rm -f $I; continue; }
  if python3 -I $L/check_judgments.py $O $I > /dev/null 2>&1; then echo "judged already $u ($m)"; continue; fi
  SYS=cb-$RUN-$u-haiku55-low
  env PREFLIGHT_PROBE_IDS=0 PREFLIGHT_SET=$PS PREFLIGHT_DECLARED_CALLS=$((2*m)) bash $SJ --preflight $TR $O $B $I $SYS 4 haiku > /dev/null || { echo "PREFLIGHT FAIL $u"; exit 8; }
  t=$(date +%s); bash $SJ $TR $O $B $I $SYS 4 haiku > $D/$RUN-$u.judge.log 2>&1 || { echo "judge FAIL $u"; exit 1; }
  python3 -I $L/check_judgments.py $O $I "$RUN-$u" || exit 1
  echo "$(date '+%F %T') $u ids=$m calls=$((2*m)) wall=$(( $(date +%s) - t ))s" >> $D/calls.log; echo "judged $u ids=$m calls=$((2*m))"
done
echo JUDGED
