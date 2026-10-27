#!/usr/bin/env bash
# lat.sh <base tree> <sel tree> <requests> <outprefix> : 3 interleaved replays each (cache effects cancel)
S=<scratch>; T=<workspace>/rnd/research/coordinator/arms/travelsel/tools
for i in 1 2 3; do $T/replay.sh $1 $3 $4-base$i.jsonl 18510 >/dev/null; $T/replay.sh $2 $3 $4-sel$i.jsonl 18510 >/dev/null; done; echo done
