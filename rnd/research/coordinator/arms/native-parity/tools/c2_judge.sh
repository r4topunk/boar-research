#!/bin/bash
# C2-REPLICA-FIDELITY Opus pass (as A1's a1_judge.sh): judge.v1 default opus, both orders, seed 7, --gap-ms 0, N = 4 shards, JUDGE_FLOOR_ERRORED=1.
# Usage: c2_judge.sh N-D|N-S. Checks the criterion sha and the 102-call plan first. Criterion ../C2-criterion.md.
set -u
C=<workspace>/rnd/research/coordinator; A=$C/arms; P=$A/native-parity; BE=<workspace>/boar-eval/bench/v0.1; ARM=${1:?N-D or N-S}
[ "$(shasum -a 256 $P/C2-criterion.md | cut -d' ' -f1)" = "$(cut -d' ' -f1 $P/C2-criterion.sha256)" ] || { echo "criterion sha mismatch"; exit 9; }
n=$(grep -c . $P/cv5-51.ids); [ $((2*n)) -le 102 ] || { echo "planned calls $((2*n)) > 102"; exit 9; }
JUDGE_FLOOR_ERRORED=1 bash $A/deepthink/tools/shard_judge.sh $P/traces/native-$ARM-v01-s42.traces.jsonl $P/judgments/native-$ARM-v01-s42.opus.judgments.jsonl \
  $BE $P/cv5-51.ids c2-native-$ARM-opus 4 opus
