#!/bin/bash
# DEEPTHINK-V02 L1 after TV s<seed> generation: fetch, thinking stats, Haiku 5.5-low N=4 (both orders, v0.2 refs), paired TV vs D, promotion rule. Aggregates/ids only.
# Usage: TREE=<deepthink|deepthink2> HIT=<1024|3000> l1.sh <seed>
set -u
s=$1; TO=$(cd "$(dirname "$0")" && pwd); AG=$TO/../aggregates; B=<private held-out dir>; O=$B/runs-deepthinkv02; R=dtv-TV-v02-s$s; IDS=$B/runs-deepvpara/judged.ids
$TO/dtv.sh fetch $R $O/$R.traces.jsonl $O/$R.requests.jsonl | tee $AG/gen-TV-s$s.txt
$TO/dtv.sh think $O/$R.traces.jsonl $IDS $O/think-TV-s$s.perItem.json > $AG/think-TV-s$s.json; cat $AG/think-TV-s$s.json
[ "${SKIPJUDGE:-0}" = 1 ] && exit 0
$TO/shard_judge.sh $O/$R.traces.jsonl $O/$R.judgments.haiku55-low.jsonl $B/live/v0.2 $IDS deepthinkv02-TV-haiku55-low 4 haiku
node $TO/paired.mjs $O/$R.judgments.haiku55-low.jsonl $B/runs-deepvpara/dv-D-v02-s$s.judgments.haiku55-low.jsonl $IDS TV D > $O/dtv-v02-s$s.TVvsD.haiku55-low.json
jq 'del(.perItem)' $O/dtv-v02-s$s.TVvsD.haiku55-low.json > $AG/L1-TVvsD-s$s.haiku55-low.json
jq -c '{TV:{ratio:.TV.ratio,ci:.TV.ci,floorAdj:.TV.floorAdj,win:.TV.win}, D:{ratio:.D.ratio,ci:.D.ci,floorAdj:.D.floorAdj,win:.D.win}, paired, missing}' $AG/L1-TVvsD-s$s.haiku55-low.json
jq -r '"RULE wins TV \(.paired.winsVsRef.TV) >= D \(.paired.winsVsRef.D)+3: \(.paired.winsVsRef.TV >= .paired.winsVsRef.D+3) | dRatio \(.paired.dRatio) >= 0.03: \(.paired.dRatio >= 0.03) => \(if (.paired.winsVsRef.TV >= .paired.winsVsRef.D+3) or (.paired.dRatio >= 0.03) then "PROMOTE" else "NO" end)"' $AG/L1-TVvsD-s$s.haiku55-low.json | tee $AG/L1-rule-s$s.txt
