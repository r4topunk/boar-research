#!/bin/bash
# DEEPTHINK-V02 L2 (on promotion). Usage: l2.sh judge <seed>  |  l2.sh scales "<seeds>"
# scales: floor_metrics (stratified by questions.v02-new categories, D_decl 0.306) for TV, D (runs-deepvpara), K (runs-cut6);
# paired.mjs TV vs D / TV vs K per seed; paired_gap.py two-seed (TV vs D, TV vs K); per-category Δ (percat.mjs). Aggregates only.
set -u
TO=$(cd "$(dirname "$0")" && pwd); AG=$TO/../aggregates; B=<private held-out dir>; O=$B/runs-deepthinkv02; IDS=$B/runs-deepvpara/judged.ids
Q=$B/live/v0.2/questions.v02-new.jsonl; PL=<workspace>/boar-eval/bench/v0.2/plan
case $1 in
judge) s=$2; R=dtv-TV-v02-s$s
  $TO/shard_judge.sh $O/$R.traces.jsonl $O/$R.judgments.jsonl $B/live/v0.2 $IDS deepthinkv02-TV-opus 4 opus 2>&1 | tee $O/$R.opus.shardrun.out
  grep -h "### exit" $O/$R.judgments.shards/shard-*.log | sort | uniq -c;;
scales) seeds=$2; rt=""; rd=""; rk=""; for s in $seeds; do rt="$rt dtv-TV-v02-s$s"; rd="$rd dv-D-v02-s$s"; rk="$rk cut6-v02-s$s"; done
  ft=$(python3 $PL/floor_metrics.py --runs $rt --dir $O --decline-ratio 0.306 --ids $IDS --questions $Q)
  fd=$(python3 $PL/floor_metrics.py --runs $rd --dir $B/runs-deepvpara --decline-ratio 0.306 --ids $IDS --questions $Q)
  fk=$(python3 $PL/floor_metrics.py --runs $rk --dir $B/runs-cut6 --decline-ratio 0.306 --ids $IDS --questions $Q)
  P=(); PC=(); for s in $seeds; do
    P+=("$(node $TO/paired.mjs $O/dtv-TV-v02-s$s.judgments.jsonl $B/runs-deepvpara/dv-D-v02-s$s.judgments.jsonl $IDS TV D | jq -c --arg s $s '{seed:$s,vs:"D"} + del(.perItem)')")
    P+=("$(node $TO/paired.mjs $O/dtv-TV-v02-s$s.judgments.jsonl $B/runs-cut6/cut6-v02-s$s.judgments.jsonl $IDS TV K | jq -c --arg s $s '{seed:$s,vs:"K"} + del(.perItem)')"); done
  n=$(echo $seeds | wc -w | tr -d ' ')
  PG=$O/paired-${n}seed; mkdir -p $PG; G=null
  for s in $seeds; do for f in $O/dtv-TV-v02-s$s $B/runs-deepvpara/dv-D-v02-s$s $B/runs-cut6/cut6-v02-s$s; do for x in judgments traces; do ln -sf $f.$x.jsonl $PG/; done; done; done
  gd=$(python3 $PL/paired_gap.py --dir $PG --a $rt --b $rd --questions $Q --decline-ratio 0.306 2>/dev/null | jq -c .)
  gk=$(python3 $PL/paired_gap.py --dir $PG --a $rt --b $rk --questions $Q --decline-ratio 0.306 2>/dev/null | jq -c .)
  echo "$gd" > $AG/paired_gap-TVvsD-${n}seed.txt; echo "$gk" > $AG/paired_gap-TVvsK-${n}seed.txt
  pd=(); pk=(); for s in $seeds; do pd+=($O/dtv-TV-v02-s$s.judgments.jsonl $B/runs-deepvpara/dv-D-v02-s$s.judgments.jsonl); pk+=($O/dtv-TV-v02-s$s.judgments.jsonl $B/runs-cut6/cut6-v02-s$s.judgments.jsonl); done
  node $TO/percat.mjs $IDS TV D "${pd[@]}" > $AG/percat-TVvsD-${n}seed.opus.json; node $TO/percat.mjs $IDS TV K "${pk[@]}" > $AG/percat-TVvsK-${n}seed.opus.json
  jq -n --argjson a "$ft" --argjson d "$fd" --argjson k "$fk" --argjson p "$(printf '%s\n' "${P[@]}" | jq -s .)" '{TV:$a, D:$d, K:$k, paired:$p}' > $AG/L2-TV-${n}seed.opus.json
  jq -c 'to_entries[] | select(.key!="paired") | {arm:.key, runs:.value.runs, n:.value.n_items, raw:.value.raw, floorAdj:.value.above_min, aboveDecl:.value.above_decl}' $AG/L2-TV-${n}seed.opus.json
  jq -c '.paired[] | {seed, vs, n:.paired.n, TVratio:.TV.ratio, winTV:.TV.win, winRateCI:.TV.winRateCI, dRatio:.paired.dRatio, dRatioCI:.paired.dRatioCI, dFloor:.paired.dFloor, dFloorCI:.paired.dFloorCI, h2h:.paired.headToHead}' $AG/L2-TV-${n}seed.opus.json
  echo "gapD $gd"; echo "gapK $gk"; cat $AG/percat-TVvsD-${n}seed.opus.json; echo; cat $AG/percat-TVvsK-${n}seed.opus.json;;
esac
