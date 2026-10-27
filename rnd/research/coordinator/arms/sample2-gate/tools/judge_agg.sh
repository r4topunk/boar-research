#!/bin/bash
# SAMPLE2-GATE judge + aggregate (= steps 4-5 of null-cal/tools/run_pool.sh on the composite traces): Haiku 5.5-low, N = 4 shards, both orders,
# only answers whose text differs from null-cal/control/pool-K0.json (= the S43 picks). Usage: judge_agg.sh   env: CRITERION
set -u
A=<workspace>/rnd/research/coordinator/arms; D=$A/sample2-gate; NC=$A/null-cal; TL=$A/lp-screens/tools; L=$A/_lib; SJ=$A/deepthink/tools/shard_judge.sh
BE=<workspace>/boar-eval/bench; LP=$A/litepacks; IDS=$A/../ruler/ids/stage1-pool.ids
RUN=sample2-gate-K0-stage1-pool-s42s43; TR=$D/traces/$RUN.traces.jsonl; CTLAGG=$NC/control/pool-K0.json; NAME=sample2-gate; K=K0; STAGE=stage1-pool
log() { echo "$(date +%T) [$RUN] $*"; }
CALLS=0
for u in v01 qa-cooking-se qa-money-se qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en; do
  case $u in v01) B=$BE/v0.1; PS=v01; SEL="grep -Fx -f $LP/data/v01-57.ids";; qa-cooking-se|qa-money-se) B=$BE/selftest/$u; PS=st-$u; SEL="grep ^st-$u-";; *) B=$BE/selftest/$u; PS=selftest-180; SEL="grep ^st-$u-";; esac
  O=$D/judgments/$RUN-$u.judgments.jsonl; I=$D/judgments/$RUN-$u.jids
  $SEL $IDS > $I.all || true
  python3 -I -c "import json,sys;c=json.load(open(sys.argv[1]))['items'];t={json.loads(l)['itemId']:json.loads(l)['answer']['text'] for l in open(sys.argv[2])};[print(i) for i in open(sys.argv[3]).read().split() if c[i]['text']!=t[i]]" $CTLAGG $TR $I.all > $I || exit 1
  rm -f $I.all; m=$(wc -l < $I | tr -d ' ')
  [ "$m" = 0 ] && { rm -f $I; continue; }
  if python3 -I $L/check_judgments.py $O $I > /dev/null 2>&1; then log "judged already $u ($m)"; continue; fi
  SYS=pool-$NAME-$K-$STAGE-$u-haiku55-low
  env PREFLIGHT_PROBE_IDS=0 PREFLIGHT_SET=$PS PREFLIGHT_DECLARED_CALLS=$((2*m)) ${CRITERION:+PREFLIGHT_CRITERION=$CRITERION} \
    bash $SJ --preflight $TR $O $B $I $SYS ${JUDGE_N:-4} haiku > /dev/null || { log "PREFLIGHT FAIL $u"; exit 8; }
  t=$(date +%s); bash $SJ $TR $O $B $I $SYS ${JUDGE_N:-4} haiku > $D/runs/logs/$RUN-$u.judge.log 2>&1 || { log "judge FAIL $u"; exit 1; }
  python3 -I $L/check_judgments.py $O $I "$RUN-$u" || exit 1
  CALLS=$((CALLS + 2*m)); echo "$(date '+%F %T') $u ids=$m calls=$((2*m)) wall=$(( $(date +%s) - t ))s" >> $D/runs/logs/$RUN.calls
  log "judged $u ids=$m calls=$((2*m))"
done
python3 -I $TL/agg_run.py $TR $IDS $D/aggregates/$RUN.json "$D/judgments/$RUN-*.judgments.jsonl" --control $CTLAGG || exit 1
log "ALLDONE calls=$CALLS"
