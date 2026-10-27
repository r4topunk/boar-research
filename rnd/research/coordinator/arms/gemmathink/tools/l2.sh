#!/bin/bash
# GEMMATHINK L2 (on continuation): Opus judge per seed, then two-seed claim scales G beside T (DEEPTHINK) and D (DEEPVPARA).
# Usage: l2.sh judge <seed> | l2.sh scales "<seeds>"
# scales: floor_metrics stratified by items.jsonl (D_decl 0.306) for G, T, D; paired.mjs G vs T per seed; paired_gap.py two-level (G vs T, G vs D);
# per-category G vs T (dtcat.py pattern). Aggregates only.
set -u
TO=$(cd "$(dirname "$0")" && pwd); AG=$TO/../aggregates; B=<private held-out dir>; O=$B/runs-gemmathink; IDS=$B/runs-cut6/judged.ids
Q=$B/items.jsonl; PL=<workspace>/boar-eval/bench/v0.2/plan; PG=<workspace>/boar-eval/bench/v0.3/plan/paired_gap.py
case $1 in
judge) s=$2; R=gt-G-vpara-s$s
  $TO/../../deepthink/tools/shard_judge.sh $O/$R.traces.jsonl $O/$R.judgments.jsonl $B/bench-shim $IDS gemmathink-G-opus 4 opus 2>&1 | tee $O/$R.opus.shardrun.out | grep -v " boar" | tail -3
  grep -h "### exit" $O/$R.judgments.shards/shard-*.log | sort | uniq -c;;
scales) seeds=$2; rg=""; rt=""; rd=""; for s in $seeds; do rg="$rg gt-G-vpara-s$s"; rt="$rt dt-T-vpara-s$s"; rd="$rd dv-D-vpara-s$s"; done
  fg=$(python3 $PL/floor_metrics.py --runs $rg --dir $O --decline-ratio 0.306 --ids $IDS --questions $Q)
  ft=$(python3 $PL/floor_metrics.py --runs $rt --dir $B/runs-deepthink --decline-ratio 0.306 --ids $IDS --questions $Q)
  fd=$(python3 $PL/floor_metrics.py --runs $rd --dir $B/runs-deepvpara --decline-ratio 0.306 --ids $IDS --questions $Q)
  P=(); for s in $seeds; do
    P+=("$(node $TO/../../deepvpara/tools/paired.mjs $O/gt-G-vpara-s$s.judgments.jsonl $B/runs-deepthink/dt-T-vpara-s$s.judgments.jsonl $IDS G T | jq -c --arg s $s '{seed:$s,vs:"T"} + del(.perItem)')")
    P+=("$(node $TO/../../deepvpara/tools/paired.mjs $O/gt-G-vpara-s$s.judgments.jsonl $B/runs-deepvpara/dv-D-vpara-s$s.judgments.jsonl $IDS G D | jq -c --arg s $s '{seed:$s,vs:"D"} + del(.perItem)')"); done
  n=$(echo $seeds | wc -w | tr -d ' '); PGD=$O/paired-${n}seed; mkdir -p $PGD
  for s in $seeds; do for f in $O/gt-G-vpara-s$s $B/runs-deepthink/dt-T-vpara-s$s $B/runs-deepvpara/dv-D-vpara-s$s; do for x in judgments traces; do ln -sf $f.$x.jsonl $PGD/; done; done; done
  gt=$(python3 $PG --dir $PGD --a $rg --b $rt --questions $Q --decline-ratio 0.306 2>/dev/null | jq -c .)
  gd=$(python3 $PG --dir $PGD --a $rg --b $rd --questions $Q --decline-ratio 0.306 2>/dev/null | jq -c .)
  echo "$gt" > $AG/paired_gap-GvsT-${n}seed.json; echo "$gd" > $AG/paired_gap-GvsD-${n}seed.json
  jg=""; jt=""; for s in $seeds; do jg="$jg $O/gt-G-vpara-s$s.judgments.jsonl"; jt="$jt $B/runs-deepthink/dt-T-vpara-s$s.judgments.jsonl"; done
  python3 $TO/../../deepthink/tools/dtcat.py GvsT-${n}seed $IDS "$jg" "$jt" $AG/cat-GvsT-${n}seed.opus.json > /dev/null 2>&1 || echo "dtcat failed (non-blocking)"
  jq -n --argjson g "$fg" --argjson t "$ft" --argjson d "$fd" --argjson p "$(printf '%s\n' "${P[@]}" | jq -s .)" '{G:$g, T:$t, D:$d, paired:$p}' > $AG/L2-G-${n}seed.opus.json
  jq -c 'to_entries[] | select(.key!="paired") | {arm:.key, runs:.value.runs, n:.value.n_items, raw:.value.raw, floorAdj:.value.above_min, aboveDecl:.value.above_decl}' $AG/L2-G-${n}seed.opus.json
  jq -c '.paired[] | {seed, vs, n:.paired.n, Gratio:.G.ratio, winG:.G.win, winRateCI:.G.winRateCI, dRatio:.paired.dRatio, dRatioCI:.paired.dRatioCI, dFloor:.paired.dFloor, dFloorCI:.paired.dFloorCI, h2h:.paired.headToHead}' $AG/L2-G-${n}seed.opus.json
  echo "gapT $gt"; echo "gapD $gd";;
esac
