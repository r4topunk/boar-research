#!/bin/bash
# Pre-generate 4B (cut 7) self-test traces for packs WITHOUT judging (judge + floor_metrics run later with score_selftest.sh, which skips generation when traces exist).
# Usage: pregen_selftests.sh <pack> [<pack> ...]   (seed 42, with the pack installed)
set -u
H=$(cd "$(dirname "$0")/.." && pwd); D=$H/selftest-runs; A=$H/aggregates; mkdir -p "$A" "$D"
for P in "$@"; do
  R=st-$P-cut7-s42
  echo "== $P $(date +%H:%M:%S)"
  python3 -I "$H/tools/selftest_to_bench.py" "$P" --seed 42 || { echo "convert FAIL $P"; continue; }
  [ -s "$D/$R.traces.jsonl" ] || "$H/tools/run_selftest.sh" "$D/$R.requests.jsonl" "$D/$R.traces.jsonl" || { echo "gen FAIL $P"; continue; }
  python3 -I "$H/tools/selftest_agg.py" "$P" "$D/$R.traces.jsonl" --json "$A/$R.gen.json" | tail -1
done
echo "== done $(date +%H:%M:%S)"
