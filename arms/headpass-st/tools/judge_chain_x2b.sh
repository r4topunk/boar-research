#!/bin/bash
# HEADPASS-X2b stage 2 (copy of judge_chain.sh; gen-x2b/, precheck_x2b.py): Haiku 5.5-low L1, N = 4 shards, both orders, via arms/deepthink/tools/shard_judge.sh.
# 1) wait for the 9 ON self-test runs (DONE + 20 rows); 2) precheck_hp.py (>= 20 % changed vs S, else STOP, nothing judged);
# 3) judge the 9 runs (bench boar-eval/bench/selftest/<pack>, system selftest-<pack>-cut7-headpass-haiku55-low; 40 calls each);
# 4) v0.1+simplewiki OFF and ON (bench boar-eval/bench/v0.1, 57 ids = trace ids minus venue-list items; 114 calls each).
# Fail-closed: shard_judge rc + _lib/check_judgments.py. Skips outputs already checked ok. Usage: nohup judge_chain.sh > logs/judge_chain_x2b.log 2>&1 &
set -u
H=$BOAR_WS/rnd/research/coordinator/arms/headpass-st; D=$H/gen-x2b; L=$H/../_lib; B=$BOAR_WS/boar-eval/bench; SJ=$H/../deepthink/tools/shard_judge.sh
PACKS="qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en"
wait_run() { local R=$1 n=$2; until [ "$(tail -1 "$D/$R.traces.status" 2>/dev/null)" = DONE ] && [ "$(wc -l < "$D/$R.traces.jsonl" | tr -d ' ')" = "$n" ] && [ -s "$D/$R.ids" ]; do
  case "$(tail -1 "$D/$R.traces.status" 2>/dev/null)" in FAIL*) echo "$(date +%T) generation FAIL $R (chain may retry)";; esac; sleep 30; done; }
for p in $PACKS; do wait_run st-$p-cut7-headpassx2b-s42 20; done
echo "$(date +%T) 9 ON runs done; precheck"
python3 -I $H/tools/precheck_x2b.py --out $H/aggregates/precheck-x2b.json || { echo "PRECHECK FAIL: not judging"; exit 8; }
judge() { local R=$1 bench=$2 sys=$3 O=$D/$1.judgments.jsonl
  if python3 -I "$L/check_judgments.py" "$O" "$D/$R.jids" >/dev/null 2>&1; then echo "$(date +%T) skip $R (judged)"; return 0; fi
  echo "$(date +%T) judge $R"; t=$(date +%s)
  bash "$SJ" "$D/$R.traces.jsonl" "$O" "$bench" "$D/$R.jids" "$sys" 4 haiku || { echo "judge FAIL $R"; return 1; }
  python3 -I "$L/check_judgments.py" "$O" "$D/$R.jids" "$R" || return 1
  echo "$(date +%T) JUDGED $R rows=$(wc -l < "$O" | tr -d ' ') wall=$(( $(date +%s) - t ))s"; }
vids() { python3 -I -c "import json,sys,os;q=sys.argv[2]+'/questions.public.jsonl';v={d['id'] for d in map(json.loads,open(q)) if (d.get('grading') or {}).get('type')=='venue-list'} if os.path.exists(q) else set();[print(i) for i in (json.loads(l)['itemId'] for l in open(sys.argv[1])) if i not in v]" "$1" "$2"; }
for p in $PACKS; do R=st-$p-cut7-headpassx2b-s42; vids "$D/$R.traces.jsonl" "$B/selftest/$p" > "$D/$R.jids"; judge $R "$B/selftest/$p" selftest-$p-cut7-headpassx2b-haiku55-low || exit 1; done
for tag in off on; do R=v01-sw-cut7-x2b-$tag-s42; wait_run $R 60; vids "$D/$R.traces.jsonl" "$B/v0.1" > "$D/$R.jids"; judge $R "$B/v0.1" v01-sw-cut7-x2b-$tag-haiku55-low || exit 1; done
echo "$(date +%T) ALLDONE judgment rows: $(cat $D/*.judgments.jsonl | wc -l | tr -d ' ')"
