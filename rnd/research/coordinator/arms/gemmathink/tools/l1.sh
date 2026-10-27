#!/bin/bash
# GEMMATHINK L1 after G generation: fetch, thinking stats, Haiku 5.5-low N=4 (both orders, V-para refs), paired G vs T (dt-T-vpara-s42 Haiku rows) on IDS, the two continuation clauses. Aggregates/ids only.
# Usage: l1.sh <runId> <idsFile> <tag>     e.g. l1.sh gt-G-vpara-s42-slice ../../signal20-vpara.ids slice
set -u
R=$1; IDS=$2; TAG=$3; TO=$(cd "$(dirname "$0")" && pwd); AG=$TO/../aggregates; B=<private held-out dir>; O=$B/runs-gemmathink; mkdir -p $O
TT=$B/runs-deepthink/dt-T-vpara-s42
$TO/gt.sh fetch $R $O/$R.traces.jsonl $O/$R.requests.jsonl | tee $AG/gen-$TAG.txt
$TO/gt.sh think $O/$R.traces.jsonl $IDS $O/think-$TAG.perItem.json > $AG/think-G-$TAG.json; cat $AG/think-G-$TAG.json
$TO/gt.sh think $TT.traces.jsonl $IDS "" > $AG/think-T-$TAG.json
[ "${SKIPJUDGE:-0}" = 1 ] && exit 0
$TO/../../deepthink/tools/shard_judge.sh $O/$R.traces.jsonl $O/$R.judgments.haiku55-low.jsonl $B/bench-shim $IDS gemmathink-G-haiku55-low 4 haiku
node $TO/../../deepvpara/tools/paired.mjs $O/$R.judgments.haiku55-low.jsonl $TT.judgments.haiku55-low.jsonl $IDS G T > $O/$R.GvsT.haiku55-low.json
jq 'del(.perItem)' $O/$R.GvsT.haiku55-low.json > $AG/L1-GvsT-$TAG.haiku55-low.json
jq -c '{G:{ratio:.G.ratio,ci:.G.ci,floorAdj:.G.floorAdj,win:.G.win}, T:{ratio:.T.ratio,ci:.T.ci,floorAdj:.T.floorAdj,win:.T.win}, paired, missing}' $AG/L1-GvsT-$TAG.haiku55-low.json
gp=$(jq .totalMsMedian $AG/think-G-$TAG.json); tp=$(jq .totalMsMedian $AG/think-T-$TAG.json)
jq -r --argjson gp "$gp" --argjson tp "$tp" '"(a) wins G \(.paired.winsVsRef.G) >= T \(.paired.winsVsRef.T)+3: \(.paired.winsVsRef.G >= .paired.winsVsRef.T+3) | dRatio \(.paired.dRatio) >= 0.03: \(.paired.dRatio >= 0.03) || (b) dRatio >= -0.03: \(.paired.dRatio >= -0.03) & p50 G \($gp) <= 0.75*T \($tp) = \($tp*0.75): \($gp <= $tp*0.75) => \(if (.paired.winsVsRef.G >= .paired.winsVsRef.T+3) or (.paired.dRatio >= 0.03) then "CONTINUE-promotion" elif (.paired.dRatio >= -0.03 and $gp <= $tp*0.75) then "CONTINUE-parity-faster" else "NO" end)"' $AG/L1-GvsT-$TAG.haiku55-low.json | tee $AG/L1-rule-$TAG.txt
