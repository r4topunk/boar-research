#!/bin/bash
# resume after the 2026-10-22 21:3x restart: base part 2 (missing ids), then the sticky arms and LONGSESSION
cd <workspace>/rnd/research/coordinator/arms/coverage-map/searchpar/r5
while pgrep -f "replay-sticky.ts" >/dev/null; do sleep 5; done
[ -s replays/qform.off.part2.jsonl ] && [ -z "${REDO:-}" ] || IDS=$(cat replays/qform.off.missing.ids) tools/run_r5.sh qform off.part2 off
cat replays/qform.off.part1.jsonl replays/qform.off.part2.jsonl > replays/qform.off.jsonl
for a in "qform s1 1" "qform s2 2" "longsession off off" "longsession s1 1" "longsession s2 2"; do
  [ -s replays/${a%% *}.$(echo $a | cut -d' ' -f2).jsonl ] && grep -q totalSeconds replays/${a%% *}.$(echo $a | cut -d' ' -f2).jsonl.err 2>/dev/null && continue
  tools/run_r5.sh $a; done
echo ALLDONE
