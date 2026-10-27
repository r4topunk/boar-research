#!/bin/bash
# RD1 copy of compose/screen/tools/judge_cmp.sh: ids file = items whose RD1 answer text differs from F1b (cut to the cap by the caller); no control filter. Original header: COMPOSE answer screen: Haiku 5.5-low judge.v1, N 4, both orders, on the changed ids (kept differs AND text differs vs the mini baseline) whose answer text also differs from the
# judged control (null-cal/control/pool-K1.json; = the mini baseline except lan-exp-007 and st-qa-money-se-005). = decode-ground/tools/run_pool_dg.sh judge loop.
# Usage: judge_cmp.sh <traces> <ids file> <out judgments dir> <run id>      Calls per unit = 2 x ids; ledger line appended to $OUT/calls.log
set -u
TR=$1; IDS=$2; D=$3; RUN=$4
A=<workspace>/rnd/research/coordinator/arms; LP=$A/litepacks; L=$A/_lib; SJ=$A/deepthink/tools/shard_judge.sh; BE=<workspace>/boar-eval/bench
CTLAGG=$A/null-cal/control/pool-K1.json; mkdir -p $D
for u in v01 qa-cooking-se qa-money-se qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se; do
  case $u in v01) B=$BE/v0.1; PS=v01; SEL="grep -Fx -f $LP/data/v01-57.ids";; qa-cooking-se|qa-money-se) B=$BE/selftest/$u; PS=st-$u; SEL="grep ^st-$u-";; *) B=$BE/selftest/$u; PS=selftest-180; SEL="grep ^st-$u-";; esac
  O=$D/$RUN-$u.judgments.jsonl; I=$D/$RUN-$u.jids
  $SEL $IDS > $I.all || true
  mv $I.all $I; m=$(wc -l < $I | tr -d ' ')   # RD1: the ids file is already the divergence set vs F1b (text differs), cut to the call cap; no control filter
  [ "$m" = 0 ] && { rm -f $I; continue; }
  if python3 -I $L/check_judgments.py $O $I > /dev/null 2>&1; then echo "judged already $u ($m)"; continue; fi
  SYS=cmp-$RUN-$u-haiku55-low
  DECL=$((2*m)); pl=$(env PREFLIGHT_PROBE_IDS=0 PREFLIGHT_SET=$PS PREFLIGHT_DECLARED_CALLS=$DECL bash $SJ --preflight $TR $O $B $I $SYS 4 haiku 2>&1 >/dev/null | sed -n 's/.*planned \([0-9]*\) != declared.*/\1/p')
  [ -n "$pl" ] && DECL=$pl   # resume: some rows of an interrupted run are already ok, declare only the calls still to do
  env PREFLIGHT_PROBE_IDS=0 PREFLIGHT_SET=$PS PREFLIGHT_DECLARED_CALLS=$DECL bash $SJ --preflight $TR $O $B $I $SYS 4 haiku > /dev/null || { echo "PREFLIGHT FAIL $u"; exit 8; }
  t=$(date +%s); bash $SJ $TR $O $B $I $SYS 4 haiku > $D/$RUN-$u.judge.log 2>&1 || { echo "judge FAIL $u"; exit 1; }
  python3 -I $L/check_judgments.py $O $I "$RUN-$u" || exit 1
  echo "$(date '+%F %T') $u ids=$m calls=$((2*m)) wall=$(( $(date +%s) - t ))s" >> $D/calls.log; echo "judged $u ids=$m calls=$((2*m))"
done
echo JUDGED
