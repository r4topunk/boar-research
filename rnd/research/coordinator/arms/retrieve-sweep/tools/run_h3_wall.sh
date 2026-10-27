#!/bin/bash
# H3 wall pair on QFORM, adjacent in time (machine shared with other workers: load recorded). OFF, ON, OFF, ON.
cd <workspace>/rnd/research/coordinator/arms/retrieve-sweep
K=<workspace>/kiln-local; QQ=../qform/items/qform.questions.jsonl
for n in 1 2; do
  echo "load $(uptime | sed 's/.*averages: //')"
  env -u RS_COMPRESS_HEAD tools/replay.sh $K/rs-H3 $QQ replay/H3wall.off$n.qform.jsonl qform 2>&1 | grep -E '^\{"n"|FATAL' | cut -c1-200
  echo "load $(uptime | sed 's/.*averages: //')"
  env RS_COMPRESS_HEAD=1 tools/replay.sh $K/rs-H3 $QQ replay/H3wall.on$n.qform.jsonl qform 2>&1 | grep -E '^\{"n"|FATAL' | cut -c1-200
done
echo WALLDONE
