#!/bin/bash
# VITALADD stage 3 (2026-10-13): Opus judge.v1 N=4 shards, both orders, on the existing full-110 v0.2 s42 A traces (0 generation).
# Prints counts/rc only (shard_judge summary lines); judge.mjs output stays in the shard logs.
set -u
B=<private held-out dir>; A=<workspace>/rnd/research/coordinator/arms
R=va-A-v02-s42; TR=$B/runs-vitaladd/$R.traces.jsonl; OUT=$B/runs-vitaladd/$R.judgments.opus.jsonl; IDS=$B/runs-deepvpara/judged.ids
echo "== $(date '+%F %T') start $R opus N=4"
"$A/deepthink/tools/shard_judge.sh" "$TR" "$OUT" "$B/live/v0.2" "$IDS" vitaladd-v02-s42-opus 4 opus 2>&1 | grep -E '^(rows|wall|shard|MISSING|LOCKED|STOP)' 
rc=${PIPESTATUS[0]}; echo "shard_judge rc=$rc"
grep -h "### exit" "${OUT%.jsonl}.shards"/shard-*.log 2>/dev/null | awk '{print $1,$2,$3}' | sort | uniq -c
python3 "$A/_lib/check_judgments.py" "$OUT" "$IDS" "l2 $R"; echo "check rc=$?"
echo "== $(date '+%F %T') done"
