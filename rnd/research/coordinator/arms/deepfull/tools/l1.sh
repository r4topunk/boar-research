#!/bin/bash
# DEEPFULL L1: fetch, thinking/length stats, Haiku 5.5-low N=4 (both orders, V-para refs), paired <arm> vs T (dt-T-vpara-s42 Haiku rows) on IDS, promotion rule. Aggregates/ids only.
# Usage: TREE=<deepthink|deepfull> l1.sh <runId> <idsFile> <tag> <F1|F2>
set -u
R=$1; IDS=$2; TAG=$3; A=$4; TO=$(cd "$(dirname "$0")" && pwd); AG=$TO/../aggregates; B=<private held-out dir>; O=$B/runs-deepfull; mkdir -p $O
TT=$B/runs-deepthink/dt-T-vpara-s42
$TO/df.sh fetch $R $O/$R.traces.jsonl $O/$R.requests.jsonl | tee $AG/gen-$TAG.txt
$TO/df.sh think $O/$R.traces.jsonl $IDS $O/think-$TAG.perItem.json > $AG/think-$A-$TAG.json; cat $AG/think-$A-$TAG.json
[ -f $AG/think-T-$TAG.json ] || $TO/df.sh think $TT.traces.jsonl $IDS "" > $AG/think-T-$TAG.json
[ "${SKIPJUDGE:-0}" = 1 ] && exit 0
$TO/../../deepthink/tools/shard_judge.sh $O/$R.traces.jsonl $O/$R.judgments.haiku55-low.jsonl $B/bench-shim $IDS deepfull-$A-haiku55-low 4 haiku
node $TO/../../deepvpara/tools/paired.mjs $O/$R.judgments.haiku55-low.jsonl $TT.judgments.haiku55-low.jsonl $IDS $A T > $O/$R.${A}vsT.haiku55-low.json
jq 'del(.perItem)' $O/$R.${A}vsT.haiku55-low.json > $AG/L1-${A}vsT-$TAG.haiku55-low.json
jq -c --arg a $A '{arm:{ratio:.[$a].ratio,ci:.[$a].ci,floorAdj:.[$a].floorAdj,win:.[$a].win}, T:{ratio:.T.ratio,ci:.T.ci,floorAdj:.T.floorAdj,win:.T.win}, paired, missing}' $AG/L1-${A}vsT-$TAG.haiku55-low.json
jq -r --arg a $A '"RULE wins \($a) \(.paired.winsVsRef[$a]) >= T \(.paired.winsVsRef.T)+3: \(.paired.winsVsRef[$a] >= .paired.winsVsRef.T+3) | dRatio \(.paired.dRatio) >= 0.03: \(.paired.dRatio >= 0.03) => \(if (.paired.winsVsRef[$a] >= .paired.winsVsRef.T+3) or (.paired.dRatio >= 0.03) then "PROMOTE" else "NO" end)"' $AG/L1-${A}vsT-$TAG.haiku55-low.json | tee $AG/L1-rule-$A-$TAG.txt
