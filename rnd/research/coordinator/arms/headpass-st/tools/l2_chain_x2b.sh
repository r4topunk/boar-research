#!/bin/bash
# HEADPASS-X2b Opus L2 (copy of l2_chain.sh; gen-x2b/): Opus judge.v1 N=4 shards, both orders, on the 9 ON traces (copy of packs-l2/tools/chain.sh pattern).
# Usage: l2_chain.sh <pack> [<pack> ...]; output gen/<run>.judgments.opus.jsonl (Haiku .judgments.jsonl untouched). Fail-closed.
set -u
H=<workspace>/rnd/research/coordinator/arms/headpass-st; A=$H/..; L=$A/_lib; B=<workspace>/boar-eval/bench/selftest
for p in "$@"; do
  R=$H/gen-x2b/st-$p-cut7-headpassx2b-s42; OUT=$R.judgments.opus.jsonl; SYS=selftest-$p-cut7-headpassx2b-opus
  if python3 -I "$L/check_judgments.py" "$OUT" "$R.ids" >/dev/null 2>&1; then echo "$(date +%T) skip $p (judged)"; continue; fi
  echo "$(date +%T) judge $p -> $OUT"; s=$(date +%s)
  bash "$A/deepthink/tools/shard_judge.sh" "$R.traces.jsonl" "$OUT" "$B/$p" "$R.ids" "$SYS" 4 opus; rc=$?
  w=$(( $(date +%s) - s )); D=${OUT%.jsonl}.shards
  e34=$(cat "$D"/shard-*.log 2>/dev/null | grep -cE '^### exit (3|4) '); e7=$(cat "$D"/shard-*.log 2>/dev/null | grep -cE '^### exit 7 ')
  rl=$(cat "$D"/shard-*.log 2>/dev/null | grep -ciE 'RATE LIMITED|429')
  st=$(python3 -I -c "import json,sys;r=[json.loads(l) for l in open(sys.argv[1]) if l.strip()];print(f'rows {len(r)} ok {sum(bool(x.get(\"ok\")) for x in r)} models {sorted(set(str(x.get(\"judgeModel\")) for x in r))}')" "$OUT" 2>/dev/null)
  python3 -I "$L/check_judgments.py" "$OUT" "$R.ids" "$p"; ck=$?
  echo "SETLOG $p rc=$rc check=$ck wall=${w}s $st exit34=$e34 exit7=$e7 ratelimit_lines=$rl"
  [ $rc -ne 0 ] || [ $ck -ne 0 ] && { echo "$(date +%T) STOP: $p failed"; exit 1; }
done
echo "$(date +%T) lane complete: $*"
