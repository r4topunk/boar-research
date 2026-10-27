#!/bin/bash
# DT512 L1 after H generation: fetch, thinking stats, Haiku 5.5-low N=4 (both orders, V-para refs), paired H vs T (dt-T-vpara-s42 Haiku rows) on IDS, the two continuation clauses (cheaper = 0.7 × T p50). Aggregates/ids only.
# Usage: l1.sh <runId> <idsFile> <tag>
set -u
R=$1; IDS=$2; TAG=$3; TO=$(cd "$(dirname "$0")" && pwd); AG=$TO/../aggregates; B=<private held-out dir>; O=$B/runs-dt512; mkdir -p $O
TT=$B/runs-deepthink/dt-T-vpara-s42
$TO/dh.sh fetch $R $O/$R.traces.jsonl $O/$R.requests.jsonl | tee $AG/gen-$TAG.txt
$TO/dh.sh think $O/$R.traces.jsonl $IDS $O/think-$TAG.perItem.json > $AG/think-H-$TAG.json; cat $AG/think-H-$TAG.json
$TO/dh.sh think $TT.traces.jsonl $IDS "" > $AG/think-T-$TAG.json
[ "${SKIPJUDGE:-0}" = 1 ] && exit 0
$TO/../../deepthink/tools/shard_judge.sh $O/$R.traces.jsonl $O/$R.judgments.haiku55-low.jsonl $B/bench-shim $IDS dt512-H-haiku55-low 4 haiku
node $TO/../../deepvpara/tools/paired.mjs $O/$R.judgments.haiku55-low.jsonl $TT.judgments.haiku55-low.jsonl $IDS H T > $O/$R.HvsT.haiku55-low.json
jq 'del(.perItem)' $O/$R.HvsT.haiku55-low.json > $AG/L1-HvsT-$TAG.haiku55-low.json
jq -c '{H:{ratio:.H.ratio,ci:.H.ci,floorAdj:.H.floorAdj,win:.H.win}, T:{ratio:.T.ratio,ci:.T.ci,floorAdj:.T.floorAdj,win:.T.win}, paired, missing}' $AG/L1-HvsT-$TAG.haiku55-low.json
gp=$(jq .totalMsMedian $AG/think-H-$TAG.json); tp=$(jq .totalMsMedian $AG/think-T-$TAG.json)
jq -r --argjson gp "$gp" --argjson tp "$tp" '"(a) wins H \(.paired.winsVsRef.H) >= T \(.paired.winsVsRef.T)+3: \(.paired.winsVsRef.H >= .paired.winsVsRef.T+3) | dRatio \(.paired.dRatio) >= 0.03: \(.paired.dRatio >= 0.03) || (b) dRatio >= -0.03: \(.paired.dRatio >= -0.03) & p50 H \($gp) <= 0.7*T \($tp) = \($tp*0.7): \($gp <= $tp*0.7) => \(if (.paired.winsVsRef.H >= .paired.winsVsRef.T+3) or (.paired.dRatio >= 0.03) then "CONTINUE-promotion" elif (.paired.dRatio >= -0.03 and $gp <= $tp*0.7) then "CONTINUE-cheaper" else "NO" end)"' $AG/L1-HvsT-$TAG.haiku55-low.json | tee $AG/L1-rule-$TAG.txt
