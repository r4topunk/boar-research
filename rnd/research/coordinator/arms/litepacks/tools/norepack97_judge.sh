#!/bin/bash
# NOREPACK97 judge (MacBook): Haiku 5.5-low, N = 4, both orders. Judges (a) ids whose no-repack text differs from the mini default baseline (arm side) and
# (b) baseline rows whose text differs from lp-screens/control lpctl-K1-main (so the baseline has a judgment). Units as litepacks/tools/judge.sh. Usage: norepack97_judge.sh <arm traces>
set -u
H=<workspace>/rnd/research/coordinator/arms/litepacks; L=$H/../_lib; SJ=$H/../deepthink/tools/shard_judge.sh; BE=<workspace>/boar-eval/bench
C=$H/NOREPACK97-budget.md; ARM=$1; J=$H/norepack97/judg; mkdir -p $J
[ "$(shasum -a 256 $H/NOREPACK97-criterion.md | cut -d' ' -f1)" = "$(cut -d' ' -f1 $H/NOREPACK97-criterion.sha256)" ] || { echo "criterion sha mismatch"; exit 9; }
CTL=$H/../lp-screens/control/traces/lpctl-K1-main-s42.traces.jsonl
cat $H/traces/mini/lp-K1-cm-s42.mini.traces.jsonl $H/traces/mini/lp-K1-v01-s42.mini.traces.jsonl > $J/base.traces.jsonl
python3 -I $H/tools/changed_ids.py $J/base.traces.jsonl $ARM $H/../lp-screens/main-97.ids > $J/arm.ids
python3 -I $H/tools/changed_ids.py $CTL $J/base.traces.jsonl $H/../lp-screens/main-97.ids > $J/base.ids
echo "arm-changed $(wc -l < $J/arm.ids) base-needs-judgment $(wc -l < $J/base.ids)"
for side in arm base; do
 case $side in arm) TRF=$ARM;; base) TRF=$J/base.traces.jsonl;; esac
 for u in v01 qa-cooking-se qa-money-se; do
  case $u in v01) B=$BE/v0.1; PS=v01; pat='^(?!st-)';; *) B=$BE/selftest/$u; PS=st-$u; pat="^st-$u-";; esac
  I=$J/$side-$u.ids; python3 -I -c "import re,sys;[print(x) for x in open(sys.argv[1]).read().split() if re.match(sys.argv[2],x)]" $J/$side.ids "$pat" > $I
  n=$(wc -l < $I | tr -d ' '); [ "$n" = 0 ] && continue
  O=$J/$side-$u.judgments.jsonl
  if python3 -I $L/check_judgments.py $O $I > /dev/null 2>&1; then echo "skip $side $u"; continue; fi
  PREFLIGHT_PROBE_IDS=0 PREFLIGHT_SET=$PS PREFLIGHT_CRITERION=$C PREFLIGHT_DECLARED_CALLS=$((2*n)) bash $SJ --preflight $TRF $O $B $I norepack97-$side-$u 4 haiku || { echo PREFLIGHT FAIL; exit 8; }
  bash $SJ $TRF $O $B $I norepack97-$side-$u 4 haiku || { echo "judge FAIL $side $u"; exit 1; }
  python3 -I $L/check_judgments.py $O $I norepack97-$side-$u || exit 1
  echo "JUDGED $side $u ids=$n"
 done
done
echo ALLDONE
