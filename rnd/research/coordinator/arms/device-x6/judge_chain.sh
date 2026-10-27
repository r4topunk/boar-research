#!/bin/bash
set -u; cd <workspace>
SJ=rnd/research/coordinator/arms/deepthink/tools/shard_judge.sh; J=rnd/research/coordinator/arms/device-x6/v01.jids; B=boar-eval/bench/v0.1
bash $SJ boar-eval/runs/device-poco-x6pro/final-cut7-v01/traces.jsonl boar-eval/runs/device-poco-x6pro/final-cut7-v01/judgments.haiku.jsonl $B $J v01-x6pro-cut7-haiku55-low 4 haiku > boar-eval/runs/device-poco-x6pro/final-cut7-v01/judge.log 2>&1 & p1=$!
bash $SJ boar-eval/runs/device-poco-x6pro/native-x6-v01/traces.jsonl boar-eval/runs/device-poco-x6pro/native-x6-v01/judgments.haiku.jsonl $B $J v01-x6pro-native-haiku55-low 4 haiku > boar-eval/runs/device-poco-x6pro/native-x6-v01/judge.log 2>&1 & p2=$!
wait $p1; r1=$?; wait $p2; r2=$?; echo "$(date +%T) DONE phone rc=$r1 native rc=$r2 rows $(wc -l < boar-eval/runs/device-poco-x6pro/final-cut7-v01/judgments.haiku.jsonl) $(wc -l < boar-eval/runs/device-poco-x6pro/native-x6-v01/judgments.haiku.jsonl)"
