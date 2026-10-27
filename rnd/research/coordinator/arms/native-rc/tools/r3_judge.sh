#!/bin/bash
# R3 Claude half: judge.v1 Opus, both orders, vs the Claude references (refs-v2 claude.jsonl sha b27eac37, copied unchanged into work/v04/bench/refs/),
# author notes = checklist (+ time-sensitive / location lines; no errata yet), multi-turn frame of spec 6.3 (tools/mk_v04.py). Sharded N 4
# (deepthink/tools/shard_judge.sh, judge.mjs --gap-ms 0 --seed 7). 75 items x 2 orders = 150 Opus calls per traces file; cap 320 per arm (2 files = 300).
# Never prints item text. usage: r3_judge.sh <native|engine> <seed>
set -euo pipefail
A=<workspace>/rnd/research/coordinator/arms/native-rc; V=$A/work/v04; ARM=$1; S=$2
TR=$V/traces/$ARM-s$S.traces.jsonl; OUT=$A/judge/r3/$ARM-s$S.opus.judgments.jsonl
mkdir -p $A/judge/r3; python3 -I -c 'import json,sys;[print(json.loads(l)["id"]) for l in open(sys.argv[1]) if l.strip()]' $V/bench/questions.jsonl > $A/judge/r3/ids.txt
[ "$(shasum -a 256 $V/bench/refs/claude.jsonl | cut -c1-16)" = b27eac37a88918ca ] || { echo "refs sha mismatch"; exit 1; }
bash $A/../deepthink/tools/shard_judge.sh $TR $OUT $V/bench $A/judge/r3/ids.txt "nrc-v04-$ARM-s$S" 4 opus > $A/judge/r3/$ARM-s$S.log 2>&1
echo "rc=$? rows=$(wc -l < $OUT)"
