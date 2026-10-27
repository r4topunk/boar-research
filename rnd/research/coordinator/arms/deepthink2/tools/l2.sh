#!/bin/bash
# DEEPTHINK-2 L2 (on promotion): Opus judge.v1 N=4 sharded on T2 seed <s>. Prints counts only.
# Usage: l2.sh judge <seed>      |  l2.sh scales "<seeds>"  (claim scales T2 beside T and D via floor_metrics, stratified; paired per seed)
set -u
TO=$(cd "$(dirname "$0")" && pwd); AG=$TO/../aggregates; B=<private held-out dir>; O=$B/runs-deepthink2; IDS=$B/runs-cut6/judged.ids
FM=<workspace>/boar-eval/bench/v0.2/plan/floor_metrics.py
case $1 in
judge) s=$2; R=dt2-T2-vpara-s$s
  $TO/shard_judge.sh $O/$R.traces.jsonl $O/$R.judgments.jsonl $B/bench-shim $IDS deepthink2-T2-opus 4 opus 2>&1 | tee $O/$R.opus.shardrun.out
  grep -h "### exit" $O/$R.judgments.shards/shard-*.log | sort | uniq -c;;
scales) seeds=$2; r2=""; rt=""; rd=""; for s in $seeds; do r2="$r2 dt2-T2-vpara-s$s"; rt="$rt dt-T-vpara-s$s"; rd="$rd dv-D-vpara-s$s"; done
  f2=$(python3 $FM --runs $r2 --dir $O --decline-ratio 0.306 --ids $IDS --questions $B/items.jsonl)
  ft=$(python3 $FM --runs $rt --dir $B/runs-deepthink --decline-ratio 0.306 --ids $IDS --questions $B/items.jsonl)
  fd=$(python3 $FM --runs $rd --dir $B/runs-deepvpara --decline-ratio 0.306 --ids $IDS --questions $B/items.jsonl)
  P=(); for s in $seeds; do
    P+=("$(node $TO/paired.mjs $O/dt2-T2-vpara-s$s.judgments.jsonl $B/runs-deepthink/dt-T-vpara-s$s.judgments.jsonl $IDS T2 T | jq -c --arg s $s '{seed:$s,vs:"T"} + del(.perItem)')")
    P+=("$(node $TO/paired.mjs $O/dt2-T2-vpara-s$s.judgments.jsonl $B/runs-deepvpara/dv-D-vpara-s$s.judgments.jsonl $IDS T2 D | jq -c --arg s $s '{seed:$s,vs:"D"} + del(.perItem)')"); done
  n=$(echo $seeds | wc -w | tr -d ' ')
  jq -n --argjson a "$f2" --argjson t "$ft" --argjson d "$fd" --argjson p "$(printf '%s\n' "${P[@]}" | jq -s .)" '{T2:$a, T:$t, D:$d, paired:$p}' > $AG/L2-T2-${n}seed.opus.json
  jq -c 'to_entries[] | select(.key!="paired") | {arm:.key, runs:.value.runs, n:.value.n_items, raw:.value.raw, floorAdj:.value.above_min, aboveDecl:.value.above_decl}' $AG/L2-T2-${n}seed.opus.json
  jq -c '.paired[] | {seed, vs, n:.paired.n, T2ratio:.T2.ratio, winT2:.T2.win, dRatio:.paired.dRatio, dRatioCI:.paired.dRatioCI, dFloor:.paired.dFloor, dFloorCI:.paired.dFloorCI, h2h:.paired.headToHead}' $AG/L2-T2-${n}seed.opus.json;;
esac
