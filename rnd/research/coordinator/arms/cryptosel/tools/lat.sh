#!/usr/bin/env bash
# lat.sh <base tree> <sel tree> <requests> <outprefix> : 3 interleaved replays each (cache effects cancel)
S=<scratch>; T=<workspace>/rnd/research/coordinator/arms/cryptosel/tools
for i in 1 2 3; do $T/replay.sh $1 $3 $4-base$i.jsonl >/dev/null; $T/replay.sh $2 $3 $4-sel$i.jsonl >/dev/null; done; echo done
