#!/bin/bash
# PACKS-L2 judge chain (criterion sha ace9dd58…): Opus judge.v1 N=4 shards via deepthink/tools/shard_judge.sh, one set at a time.
# Usage: chain.sh <cell> <pack> [<pack> ...]   cell in nopack|all9|stack|withpack
# Per set: skips if check_judgments passes; logs one SETLOG line: wall, rows, ok, models, exit-3/4 count, rate-limit lines.
set -u
A=$(cd "$(dirname "$0")/../.." && pwd); L=$A/_lib; B=<workspace>/boar-eval/bench/selftest
cell=$1; shift
for p in "$@"; do
  case $cell in
    nopack) R=$A/packs/selftest-runs/st-$p-cut7-nopack-s42;;
    withpack) R=$A/packs/selftest-runs/st-$p-cut7-s42;;
    all9) R=$A/crowdq/runs/st-$p-cut7-all9-s42;;
    stack) R=$A/stack/runs/st-$p-cut7-stack-s42;;
    *) echo "bad cell $cell"; exit 2;;
  esac
  OUT=$R.judgments.opus.jsonl; SYS=selftest-$p-cut7-$cell-opus
  if python3 -I "$L/check_judgments.py" "$OUT" "$R.ids" >/dev/null 2>&1; then echo "$(date +%T) skip $p/$cell (judged)"; continue; fi
  echo "$(date +%T) judge $p/$cell -> $OUT"
  s=$(date +%s)
  bash "$A/deepthink/tools/shard_judge.sh" "$R.traces.jsonl" "$OUT" "$B/$p" "$R.ids" "$SYS" 4 opus; rc=$?
  w=$(( $(date +%s) - s )); D=${OUT%.jsonl}.shards
  e34=$(cat "$D"/shard-*.log 2>/dev/null | grep -cE '^### exit (3|4) ')
  rl=$(cat "$D"/shard-*.log 2>/dev/null | grep -ciE 'RATE LIMITED|429')
  st=$(python3 -I -c "import json,sys;r=[json.loads(l) for l in open(sys.argv[1]) if l.strip()];print(f'rows {len(r)} ok {sum(bool(x.get(\"ok\")) for x in r)} models {sorted(set(str(x.get(\"judgeModel\")) for x in r))} judgeVersion {sorted(set(str(x.get(\"judgeVersion\",x.get(\"judge\"))) for x in r))}')" "$OUT" 2>/dev/null)
  python3 -I "$L/check_judgments.py" "$OUT" "$R.ids" "$p/$cell"; ck=$?
  echo "SETLOG $p/$cell rc=$rc check=$ck wall=${w}s $st exit34=$e34 ratelimit_lines=$rl"
  [ $rc -ne 0 ] || [ $ck -ne 0 ] && { echo "$(date +%T) STOP chain: $p/$cell failed"; exit 1; }
done
echo "$(date +%T) chain $cell complete"
