#!/bin/bash
# JUDGE-V1_1 runner (criterion ../JUDGE-V1_1-criterion.md). Haiku 5.5-low, judge.mjs unchanged, prompt lib swapped via BOAR_EVAL_LIB, both orders, N = 4 shards
# (deepthink/tools/shard_judge.sh). Usage: run_v1_1.sh <W1|W2> <validity|controls|retest|controls20>
# Calls ledger: runs/calls.ledger (one line per ok row); refuses a step whose planned calls would push the ledger past CAP (400).
set -u
W=$1; STEP=$2; H=<workspace>/rnd/research/coordinator/arms/floor-anchors; V=$H/v1_1; A=$(dirname $H); SJ=$A/deepthink/tools/shard_judge.sh
BE=<workspace>/boar-eval/bench; VEN=<workspace>/boar-eval/scorers/vendor; LED=$V/runs/calls.ledger; CAP=${CAP:-400}
case $W in W1) LIB=$VEN/eval-lib-v1_1; TAG=judge.v1_1-low;; W2) LIB=$VEN/eval-lib-v1_1b; TAG=judge.v1_1b-low;; *) echo "bad wording"; exit 2;; esac
CTL=$A/lp-screens/control/traces/lpctl-K0-main-s42.traces.jsonl; touch $LED
job() { # traces out bench idsfile system
  local m have; m=$(wc -w < $4 | tr -d ' ')
  if python3 -I $A/_lib/check_judgments.py $2 $4 > /dev/null 2>&1; then echo "done $(basename $2)"; return 0; fi
  have=$(wc -l < $LED | tr -d ' '); [ $((have + 2*m)) -le $CAP ] || { echo "CAP: ledger $have + planned $((2*m)) > $CAP"; exit 6; }
  BOAR_EVAL_LIB=$LIB bash $SJ $1 $2 $3 $4 $5 4 haiku > $V/runs/$(basename $2 .judgments.jsonl).log 2>&1 || { echo "judge FAIL $2"; exit 1; }
  python3 -I $A/_lib/check_judgments.py $2 $4 || exit 1
  printf '{"judgeVersion":"%s","lib":"%s","judgeCoreSha256":"%s"}\n' $TAG $LIB $(shasum -a 256 $LIB/judge-core.mjs | cut -d' ' -f1) > ${2%.jsonl}.version
  python3 -I -c "import json,sys;[print(json.dumps({'at':r.get('createdAt'),'tag':sys.argv[2]+':'+r['queryId']+':'+r['order'],'model':'claude-haiku-5-5','effort':'low','ok':r['ok']})) for r in map(json.loads,open(sys.argv[1]))]" $2 "$W:$(basename $2 .judgments.jsonl)" >> $LED
  echo "ok $(basename $2) calls=$((2*m)) ledger=$(wc -l < $LED | tr -d ' ')"; }
setids() { awk -F'\t' -v s=$1 '$2==s{print $1}' $V/data/controls-40.tsv > $V/data/$2-$1.ids; }
bench() { case $1 in v01) echo $BE/v0.1;; *) echo $BE/selftest/$1;; esac; }
case $STEP in
  validity) for v in a b c; do job $H/traces/fa-decline-$v.traces.jsonl $V/judgments/$W-decline-$v.judgments.jsonl $BE/v0.1 $H/decline-30.ids fa11-$W-decline-$v-haiku55-low; done;;
  controls) for s in v01 qa-cooking-se qa-money-se; do setids $s ctl; job $CTL $V/judgments/$W-ctl-$s.judgments.jsonl $(bench $s) $V/data/ctl-$s.ids fa11-$W-ctl-$s-haiku55-low; done;;
  retest)   for s in v01 qa-cooking-se qa-money-se; do grep -xF -f $V/data/retest-20.ids $V/data/ctl-$s.ids > $V/data/rt-$s.ids || true; [ -s $V/data/rt-$s.ids ] || continue
              job $CTL $V/judgments/$W-rt-$s.judgments.jsonl $(bench $s) $V/data/rt-$s.ids fa11-$W-rt-$s-haiku55-low; done;;
  controls20) for s in v01 qa-cooking-se qa-money-se; do setids $s ctl; grep -xF -f $V/data/retest-20.ids $V/data/ctl-$s.ids > $V/data/c20-$s.ids || true; [ -s $V/data/c20-$s.ids ] || continue
              job $CTL $V/judgments/$W-ctl-$s.judgments.jsonl $(bench $s) $V/data/c20-$s.ids fa11-$W-ctl-$s-haiku55-low; done;;
  *) echo "bad step"; exit 2;;
esac
