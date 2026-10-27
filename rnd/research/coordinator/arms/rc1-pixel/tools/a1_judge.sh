#!/bin/bash
# A1-RC1-SHIPPED-U Opus pass: judge.v1 (judge.mjs default opus), both orders, seed 7, --gap-ms 0, N = 4 shards via arms/deepthink/tools/shard_judge.sh
# model opus, JUDGE_FLOOR_ERRORED=1 (errored traces floor-scored, 0 calls). Checks the criterion sha and the 102-call plan first.
set -u
C=<workspace>/rnd/research/coordinator; A=$C/arms; D=$A/rc1-pixel/a1; BE=<workspace>/boar-eval/bench/v0.1
[ "$(shasum -a 256 $A/rc1-pixel/A1-criterion.md | cut -d' ' -f1)" = "$(cut -d' ' -f1 $A/rc1-pixel/A1-criterion.sha256)" ] || { echo "criterion sha mismatch"; exit 9; }
n=$(grep -c . $D/in/v01-51.ids); [ $((2*n)) -le 102 ] || { echo "planned calls $((2*n)) > 102"; exit 9; }
JUDGE_FLOOR_ERRORED=1 bash $A/deepthink/tools/shard_judge.sh $D/in/rc-cv5-51-15b.traces.jsonl $D/judgments/rc1-shipped.opus.judgments.jsonl $BE $D/in/v01-51.ids a1-rc1-shipped 4 opus
