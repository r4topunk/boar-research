#!/bin/sh
# 3 interleaved reps of each engine config over the same recording (the MacBook is shared; summarize per-question min).
cd "$(dirname "$0")"; H=${HERMES:-$HOME/src/hermes-v1/build_release/bin/hermes}
for i in 1 2 3; do
  node rec/run.js > out/r$i-node-jit.json
  POLY=1 node rec/run.js > out/r$i-node-jit-poly.json
  $H rec/run.hbc > out/r$i-hermes-hbc-O.json
  $H -lazy rec/run.js > out/r$i-hermes-src-lazy.json
  node --jitless rec/run.js > out/r$i-node-jitless.json
done
echo done
