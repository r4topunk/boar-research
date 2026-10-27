#!/bin/bash
# X2B-OFF-MAIN addendum 1 step 1: Opus judge.v1, N 4, both orders, on the 9 seed-42 CEu-flip items, ON (lpctl-K1-main-s42) and OFF (x2boffmain s42) traces. Cap 36 calls.
set -u
A=<workspace>/rnd/research/coordinator/arms; X=$A/x2b-retest; O=$X/main/opus9; SJ=$A/deepthink/tools/shard_judge.sh; BE=<workspace>/boar-eval/bench
CR=$X/X2B-OFF-MAIN-criterion-addendum2.md  # addendum 2 = preflight format of addendum 1
printf '%s\n' lan-rsn-001 lan-cmp-002 lan-cmp-004 vit-cry-006 vit-cry-007 lan-cmp-005 > $O/in/v01.ids
printf '%s\n' st-qa-cooking-se-016 > $O/in/qa-cooking-se.ids
printf '%s\n' st-qa-money-se-007 st-qa-money-se-009 > $O/in/qa-money-se.ids
for arm in on off; do
  [ $arm = on ] && TR=$A/lp-screens/control/traces/lpctl-K1-main-s42.traces.jsonl || TR=$X/main/x2boffmain/traces/x2boffmain-K1-main-live77-s42.traces.jsonl
  for u in v01 qa-cooking-se qa-money-se; do
    case $u in v01) B=$BE/v0.1; PS=v01;; *) B=$BE/selftest/$u; PS=st-$u;; esac
    I=$O/in/$u.ids; OUT=$O/out/$arm-$u.judgments.jsonl; m=$(wc -l < $I | tr -d ' '); SYS=x2boffmain-opus9-$arm-$u-opus
    if python3 -I $A/_lib/check_judgments.py $OUT $I > /dev/null 2>&1; then echo "done already $arm $u"; continue; fi
    env PREFLIGHT_PROBE_IDS=0 PREFLIGHT_SET=$PS PREFLIGHT_DECLARED_CALLS=$((2*m)) PREFLIGHT_CRITERION=$CR bash $SJ --preflight $TR $OUT $B $I $SYS 4 opus || { echo "PREFLIGHT FAIL $arm $u"; exit 8; }
    bash $SJ $TR $OUT $B $I $SYS 4 opus > $O/out/$arm-$u.log 2>&1 || { echo "judge FAIL $arm $u"; exit 1; }
    python3 -I $A/_lib/check_judgments.py $OUT $I "opus9-$arm-$u" || exit 1
    echo "$(date '+%F %T') $arm $u ids=$m calls=$((2*m))" >> $O/calls.log
  done
done
echo OPUS9 ALLDONE
