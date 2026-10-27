#!/bin/bash
# LITEPACKS judge (MacBook): Haiku 5.5-low judge.v1-low, N = 4 shards, both orders, via deepthink/tools/shard_judge.sh (absolute paths), preflight with
# the frozen criterion (calls_cap), check_judgments.py after (fail closed). Units: v01 (57 ids), cm-qa-cooking-se / cm-qa-money-se (20 each, from the cm run),
# st-<pack> (20 each, from the st run). K0: every id. K1-K4: ids whose answer text differs from K0 (tools/changed_ids.py); identical answers reuse K0 rows.
# Only units whose generation is DONE are judged; already-complete units are skipped. Usage: judge.sh <K0|K1|K2|K3|K4>...
set -u
H=<workspace>/rnd/research/coordinator/arms/litepacks; L=$H/../_lib; SJ=$H/../deepthink/tools/shard_judge.sh; BE=<workspace>/boar-eval/bench
C=$H/LITEPACKS-criterion.md
[ "$(shasum -a 256 $C | cut -d' ' -f1)" = "$(cut -d' ' -f1 $H/LITEPACKS-criterion.sha256)" ] || { echo "criterion sha mismatch"; exit 9; }
UNITS="v01 cm-qa-cooking-se cm-qa-money-se st-qa-travel-se st-qa-ethereum-se st-qa-bitcoin-se st-qa-health-se st-qa-outdoors-se st-boar-firstaid-en st-boar-medlineplus-en st-boar-factbook st-boar-simplewiki-en"
for K in "$@"; do for u in $UNITS; do
  case $u in v01) run=v01; B=$BE/v0.1; PS=v01;; cm-*) run=cm; B=$BE/selftest/${u#cm-}; PS=st-${u#cm-};; st-*) run=st; B=$BE/selftest/${u#st-}; PS=selftest-180;; esac
  R=lp-$K-$run-s42; TR=$H/traces/$R.traces.jsonl; T0=$H/traces/lp-K0-$run-s42.traces.jsonl
  grep -q '^DONE' $H/runs/logs/$R.status 2>/dev/null || { echo "not generated $R ($u)"; continue; }
  grep -q '^DONE' $H/runs/logs/lp-K0-$run-s42.status 2>/dev/null || { echo "K0 not generated ($u)"; continue; }
  X=lp-$K-$u-s42; O=$H/judgments/$X.judgments.jsonl; I=$H/judgments/$X.jids; U=$H/judgments/$X.unit.ids
  if [ $u = v01 ]; then cp $H/data/v01-57.ids $U; else python3 -I -c "import json,sys;[print(json.loads(l)['itemId']) for l in open(sys.argv[1]) if json.loads(l)['itemId'].startswith('st-'+sys.argv[2]+'-')]" $TR ${u#*-} > $U; fi
  if [ $K = K0 ]; then cp $U $I; else python3 -I $H/tools/changed_ids.py $T0 $TR $U > $I; fi
  n=$(wc -l < $I | tr -d ' '); [ "$n" = 0 ] && { echo "none changed $X"; continue; }
  if python3 -I $L/check_judgments.py $O $I > /dev/null 2>&1; then echo "skip $X"; continue; fi
  SYS=litepacks-$K-$u-haiku55-low
  PREFLIGHT_PROBE_IDS=0 PREFLIGHT_SET=$PS PREFLIGHT_CRITERION=$C PREFLIGHT_DECLARED_CALLS=$((2*n)) \
    bash $SJ --preflight $TR $O $B $I $SYS 4 haiku || { echo "PREFLIGHT FAIL $X"; exit 8; }
  t=$(date +%s); bash $SJ $TR $O $B $I $SYS 4 haiku || { echo "judge FAIL $X"; exit 1; }
  python3 -I $L/check_judgments.py $O $I $X || exit 1
  echo "$(date +%T) JUDGED $X ids=$n rows=$(wc -l < $O | tr -d ' ') wall=$(( $(date +%s) - t ))s"
done; done
echo "ALLDONE judge $*"
