#!/bin/bash
# DEEPTHINK-2 stage 1 after generation: fetch, thinking stats, Haiku L1 N=4 (both orders), paired T2 vs T. Prints aggregates/ids only.
# Usage: l1.sh <seed>
set -u
s=$1; TO=$(cd "$(dirname "$0")" && pwd); AG=$TO/../aggregates; B=<private held-out dir>; O=$B/runs-deepthink2; R=dt2-T2-vpara-s$s; IDS=$B/runs-cut6/judged.ids
$TO/dt2.sh fetch $R $O/$R.traces.jsonl $O/$R.requests.jsonl
HIT=3000 $TO/dt2.sh think $O/$R.traces.jsonl $IDS $O/think-T2-s$s.perItem.json > $AG/think-T2-s$s.json; cat $AG/think-T2-s$s.json
$TO/shard_judge.sh $O/$R.traces.jsonl $O/$R.judgments.haiku55-low.jsonl $B/bench-shim $IDS deepthink2-T2-haiku55-low 4 haiku
node $TO/paired.mjs $O/$R.judgments.haiku55-low.jsonl $B/runs-deepthink/dt-T-vpara-s$s.judgments.haiku55-low.jsonl $IDS T2 T > $O/dt2-vpara-s$s.T2vsT.haiku55-low.json
jq 'del(.perItem)' $O/dt2-vpara-s$s.T2vsT.haiku55-low.json > $AG/L1-T2vsT-s$s.haiku55-low.json
jq -c '{T2:{ratio:.T2.ratio,ci:.T2.ci,floorAdj:.T2.floorAdj}, T:{ratio:.T.ratio,floorAdj:.T.floorAdj}, paired}' $AG/L1-T2vsT-s$s.haiku55-low.json
