#!/bin/bash
# DG stage-1 (GATE v2) runner = null-cal/tools/run_pool.sh with the generation step replaced by tools/run_dg.sh (patched tree + DG env). Judge/aggregate/gate identical.
# Usage: run_pool_dg.sh <dirname> <DGARM S|SB|SC|C1> <K1> <ids file>     env passthrough to run_dg.sh: DG_BIAS DG_PLAUS DG_ALPHA ...   (CRITERION deliberately NOT passed: DG-criterion.md has no calls_cap line; the cap is tracked in runs/logs/CALLS.md)
# Control = null-cal/control/pool-K1.json (merged mini K1 control, judged). Output: screens/<dirname>/.
set -u
DIR=$1; DGARM=$2; K=$3; IDSF=$4; STAGE=$(basename $IDSF .ids)
A=<workspace>/rnd/research/coordinator/arms; H=$A/decode-ground; NC=$A/null-cal; TL=$A/lp-screens/tools; NT=$NC/tools; L=$A/_lib; SJ=$A/deepthink/tools/shard_judge.sh
BE=<workspace>/boar-eval/bench; LP=$A/litepacks
[ "$K" = K1 ] || { echo "K1 only"; exit 2; }
[ "$(shasum -a 256 $H/DG-criterion.md | cut -d' ' -f1)" = "$(cut -d' ' -f1 $H/DG-criterion.sha256)" ] || { echo "criterion sha mismatch"; exit 9; }
D=$H/screens/$DIR; NAME=dg-$DIR; CFGARM=cut7-headpass-x2+litepacks+dg-$DGARM
RUN=$NAME-$STAGE-s42; IDS=$IDSF
mkdir -p $D/runs/req $D/runs/logs $D/traces $D/judgments $D/aggregates
log() { echo "$(date +%T) [$RUN] $*"; }
CTLAGG=$NC/control/pool-$K.json; [ -s $CTLAGG ] || { log "FAIL no control"; exit 1; }
REQ=$D/runs/req/$RUN.requests.jsonl; python3 -I $NT/mkreq_pool.py $K $IDS $RUN $CFGARM $REQ > /dev/null || exit 1
TR=$D/traces/$RUN.traces.jsonl; n=$(wc -l < $REQ | tr -d ' ')
if [ "$(wc -l < $TR 2>/dev/null | tr -d ' ')" = "$n" ] && grep -q '^DONE' $D/runs/logs/$RUN.status 2>/dev/null; then log "traces present, skip generation"
else
  log "generation via run_dg.sh $DGARM ($n items)"
  ( cd $H && bash tools/run_dg.sh $DGARM $REQ $RUN ) > $D/runs/logs/$RUN.gen.log 2>&1 || { log "FAIL generation (see $D/runs/logs/$RUN.gen.log)"; exit 1; }
  cp $H/runs/traces/$RUN.traces.jsonl $TR; cp $H/runs/logs/$RUN.status $D/runs/logs/$RUN.status; cp $H/runs/logs/$RUN.run.log $D/runs/logs/$RUN.run.log
  [ "$(wc -l < $TR | tr -d ' ')" = "$n" ] || { log "FAIL traces rows != $n"; exit 1; }
  log "generated"
fi
# sanity (0 LLM) before any judge call
python3 -I $H/tools/sanity_dg.py $TR $IDS $D/aggregates/$RUN.sanity.json > /dev/null || { log "FAIL sanity script"; exit 1; }
python3 -I -c "import json,sys;r=json.load(open(sys.argv[1]));print('sanity kill=',r['kill'],'det_diff',r['det_diff_ctl'],'empty',r['empty'],'loops',r['loops'],'ratio',r['totalMs_ratio_all']);sys.exit(1 if r['kill'] else 0)" $D/aggregates/$RUN.sanity.json || { log "KILL RULE / det diff: not judging"; exit 3; }
# judge (Haiku 5.5-low judge.v1, N shards, both orders; only answers that differ from the pool control)
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
  env PREFLIGHT_PROBE_IDS=0 PREFLIGHT_SET=$PS PREFLIGHT_DECLARED_CALLS=$((2*m)) \
    bash $SJ --preflight $TR $O $B $I $SYS ${JUDGE_N:-4} haiku > /dev/null || { log "PREFLIGHT FAIL $u"; exit 8; }
  t=$(date +%s); bash $SJ $TR $O $B $I $SYS ${JUDGE_N:-4} haiku > $D/runs/logs/$RUN-$u.judge.log 2>&1 || { log "judge FAIL $u (see runs/logs/$RUN-$u.judge.log)"; exit 1; }
  python3 -I $L/check_judgments.py $O $I "$RUN-$u" || exit 1
  CALLS=$((CALLS + 2*m)); echo "$(date '+%F %T') $u ids=$m calls=$((2*m)) wall=$(( $(date +%s) - t ))s" >> $D/runs/logs/$RUN.calls
  log "judged $u ids=$m calls=$((2*m))"
done
AG=$D/aggregates/$RUN.json
python3 -I $TL/agg_run.py $TR $IDS $AG "$D/judgments/$RUN-*.judgments.jsonl" --control $CTLAGG || exit 1
python3 -I $NC/tools/screen_gate_v2.py $AG $CTLAGG $NC/pool/screen2-$K.json --json $D/aggregates/$RUN.gate2.json | tee $D/aggregates/$RUN.gate2.txt
log "ALLDONE calls_this_invocation=$CALLS"
