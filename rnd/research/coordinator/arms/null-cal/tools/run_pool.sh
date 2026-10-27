#!/bin/bash
# NULLCAL pool runner: run_arm.sh generalised to an arbitrary ids file over the LITEPACKS v01 / cm / st (180 self-test) requests and all 12 judge units.
# Usage: run_pool.sh <arm|_control> <K0|K1> <ids file> <patch|file.env|none>   env: OUT_BASE (arm output root, default arms/), CRITERION, JUDGE_N, SCREEN_JSON (runs gate v2 after aggregation)
# _control = the MINI control of the ids (null-cal/control, run poolctl-<K>-<tag>-s42, every id judged); an arm judges only answers that differ from null-cal/control/pool-<K>.json (merged control).
set -u
ARM=$1; K=$2; IDSF=$3; PF=${4:-none}; STAGE=$(basename $IDSF .ids)
A=<workspace>/rnd/research/coordinator/arms; H=$A/lp-screens; NC=$A/null-cal; TL=$H/tools; NT=$NC/tools; L=$A/_lib; SJ=$A/deepthink/tools/shard_judge.sh
BE=<workspace>/boar-eval/bench; LP=$A/litepacks
M=MINI_HOST; MK=<runner>/kiln; BASE=$MK/be-0cfd4a77-cut7-litepacks; JOBS=$MK/lp-screens/jobs
case $K in K0|K1) ;; *) echo "pack set must be K0 or K1"; exit 2;; esac
IDS0=$IDSF; [ -s "$IDS0" ] || { echo "no ids file $IDS0"; exit 2; }
[ "$ARM" = _control ] && { D=$NC/control; NAME=poolctl; CFGARM=cut7-headpass-x2+litepacks; } || { D=${OUT_BASE:-$A}/$ARM; NAME=$ARM; CFGARM=cut7-headpass-x2+litepacks+$ARM; }
case $ARM in */*|.*|lp-screens|litepacks) echo "bad arm name $ARM"; exit 2;; esac
RUN=$NAME-$K-$STAGE-s42; IDS=$IDS0
mkdir -p $D/runs/req $D/runs/logs $D/traces $D/judgments $D/aggregates
log() { echo "$(date +%T) [$RUN] $*"; }
CTLAGG=$NC/control/pool-$K.json

# (1) control: pool-<K>.json must exist for an arm (tools/merge_ctl.py)
[ "$ARM" = _control ] || [ -s $CTLAGG ] || { log "FAIL no merged control $CTLAGG"; exit 1; }

# (2) requests + candidate inputs
REQ=$D/runs/req/$RUN.requests.jsonl; python3 -I $NT/mkreq_pool.py $K $IDS $RUN $CFGARM $REQ > /dev/null || exit 1
KIND=none; if [ "$PF" != none ] && [ -s "$PF" ]; then case $PF in *.env) KIND=env;; *) KIND=patch;; esac; fi
[ "$KIND" = patch ] && { patch -p1 --dry-run -d <workspace>/kiln-local/be-0cfd4a77-cut7-litepacks < "$PF" > /dev/null || { log "FAIL patch does not apply (-p1 to the tree root)"; exit 2; }; }
INSHA=$( { cat $REQ; echo "kind=$KIND"; [ $KIND != none ] && cat "$PF"; } | shasum -a 256 | cut -c1-16)
TR=$D/traces/$RUN.traces.jsonl; ST=$D/runs/logs/$RUN.status; J=$JOBS/$RUN
n=$(wc -l < $REQ | tr -d ' ')

# (3) generation on the mini
if grep -q "^inputs $INSHA" $ST 2>/dev/null && grep -q '^DONE' $ST && [ "$(wc -l < $TR 2>/dev/null | tr -d ' ')" = "$n" ]; then log "traces present (inputs $INSHA), skip generation"
else
  rst=$(ssh -T -n $M "cat $J/INPUTS 2>/dev/null; tail -1 $J/STATUS 2>/dev/null" 2>/dev/null | tr '\n' ' ')
  if [ "$rst" = "$INSHA DONE " ]; then log "mini job already DONE for these inputs"
  else
    scp -q $TL/mini_gen.sh $M:$MK/lp-screens-mini_gen.sh 2>/dev/null || { ssh -T -n $M "mkdir -p $JOBS" && scp -q $TL/mini_gen.sh $M:$MK/lp-screens-mini_gen.sh; } || { log "FAIL scp"; exit 1; }
    ssh $M bash -s -- "$J" "$BASE" "$KIND" "$CFGARM" "$INSHA" <<'EOF' || { log "FAIL mini job setup"; exit 1; }
set -e; J=$1; B=$2; KIND=$3; CA=$4; IS=$5
[ "$(shasum -a 256 $B/src/routing/answer.ts | cut -c1-16)" = 0d1ac07dd1d664be ] && [ "$(shasum -a 256 $B/be/adapter-litedecline.ts | cut -c1-16)" = d53c14878ce4cbd3 ] && [ "$(cat $B/ARM)" = cut7-headpass-x2+litepacks ] || { echo "base tree mismatch"; exit 1; }
if [ -f $J/STATUS ] && ! grep -q -E '^(DONE|FAIL)' $J/STATUS; then echo "job $J is still running/queued"; exit 1; fi
rm -rf $J; mkdir -p $J; cp -cR $B $J/tree; rm -rf $J/tree/be/.cache; echo "$CA" > $J/tree/ARM; echo $IS > $J/INPUTS
EOF
    scp -q $REQ $M:$J/requests.jsonl || exit 1
    if [ $KIND = patch ]; then scp -q "$PF" $M:$J/candidate.patch && ssh -T -n $M "cd $J/tree && patch -p1 -s < ../candidate.patch && find . -name '*.orig' -delete" || { log "FAIL patch on mini"; exit 1; }; fi
    [ $KIND = env ] && { scp -q "$PF" $M:$J/env || exit 1; }
    ssh -T -n $M "nohup bash $MK/lp-screens-mini_gen.sh $J > $J/nohup.log 2>&1 < /dev/null &" || exit 1
    log "started on mini ($n items, kind $KIND, inputs $INSHA)"
    fails=0
    while :; do
      sleep 30; s=$(ssh -T -n -o ConnectTimeout=20 $M "tail -1 $J/STATUS" 2>/dev/null) || { fails=$((fails+1)); [ $fails -ge 20 ] && { log "FAIL mini unreachable"; exit 1; }; continue; }
      fails=0; case $s in DONE) break;; FAIL*) log "mini $s"; ssh -T -n $M "cat $J/STATUS; tail -20 $J/run.log"; exit 1;; esac
    done
  fi
  scp -q $M:$J/traces.jsonl $TR && scp -q $M:$J/STATUS $ST.mini || exit 1
  ssh -T -n $M "rm -rf $J/tree" || true
  { echo "inputs $INSHA kind=$KIND patch=$( [ $KIND != none ] && shasum -a 256 "$PF" | cut -c1-16 || echo -) host=mini job=$J"; cat $ST.mini; } > $ST
  [ "$(wc -l < $TR | tr -d ' ')" = "$n" ] || { log "FAIL traces rows != $n"; exit 1; }
  log "generated $(grep '^end' $ST)"
fi

# (4) judge (MacBook, Haiku 5.5-low, N shards, both orders)
CALLS=0
for u in v01 qa-cooking-se qa-money-se qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en; do
  case $u in v01) B=$BE/v0.1; PS=v01; SEL="grep -Fx -f $LP/data/v01-57.ids";; qa-cooking-se|qa-money-se) B=$BE/selftest/$u; PS=st-$u; SEL="grep ^st-$u-";; *) B=$BE/selftest/$u; PS=selftest-180; SEL="grep ^st-$u-";; esac
  O=$D/judgments/$RUN-$u.judgments.jsonl; I=$D/judgments/$RUN-$u.jids
  $SEL $IDS > $I.all || true
  if [ "$ARM" = _control ]; then cp $I.all $I; else
    python3 -I -c "import json,sys;c=json.load(open(sys.argv[1]))['items'];t={json.loads(l)['itemId']:json.loads(l)['answer']['text'] for l in open(sys.argv[2])};[print(i) for i in open(sys.argv[3]).read().split() if c[i]['text']!=t[i]]" $CTLAGG $TR $I.all > $I || exit 1; fi
  rm -f $I.all; m=$(wc -l < $I | tr -d ' ')
  [ "$m" = 0 ] && { rm -f $I; continue; }
  if python3 -I $L/check_judgments.py $O $I > /dev/null 2>&1; then log "judged already $u ($m)"; continue; fi
  SYS=pool-$NAME-$K-$STAGE-$u-haiku55-low
  env PREFLIGHT_PROBE_IDS=0 PREFLIGHT_SET=$PS PREFLIGHT_DECLARED_CALLS=$((2*m)) ${CRITERION:+PREFLIGHT_CRITERION=$CRITERION} \
    bash $SJ --preflight $TR $O $B $I $SYS ${JUDGE_N:-4} haiku > /dev/null || { log "PREFLIGHT FAIL $u"; exit 8; }
  t=$(date +%s); bash $SJ $TR $O $B $I $SYS ${JUDGE_N:-4} haiku > $D/runs/logs/$RUN-$u.judge.log 2>&1 || { log "judge FAIL $u (see runs/logs/$RUN-$u.judge.log)"; exit 1; }
  python3 -I $L/check_judgments.py $O $I "$RUN-$u" || exit 1
  CALLS=$((CALLS + 2*m)); echo "$(date '+%F %T') $u ids=$m calls=$((2*m)) wall=$(( $(date +%s) - t ))s" >> $D/runs/logs/$RUN.calls
  log "judged $u ids=$m calls=$((2*m))"
done

# (5) aggregate + gate
AG=$D/aggregates/$RUN.json
if [ "$ARM" = _control ]; then python3 -I $TL/agg_run.py $TR $IDS $AG "$D/judgments/$RUN-*.judgments.jsonl" || exit 1
else
  python3 -I $TL/agg_run.py $TR $IDS $AG "$D/judgments/$RUN-*.judgments.jsonl" --control $CTLAGG || exit 1
  if [ -n "${SCREEN_JSON:-}" ]; then python3 -I $NC/tools/screen_gate_v2.py $AG $CTLAGG $SCREEN_JSON --json $D/aggregates/$RUN.gate2.json | tee $D/aggregates/$RUN.gate2.txt; fi
fi
log "ALLDONE calls_this_invocation=$CALLS calls_total_run=$(awk '{s+=substr($5,7)} END{print s+0}' $D/runs/logs/$RUN.calls 2>/dev/null)"
