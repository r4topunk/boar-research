#!/usr/bin/env bash
# H2 round 2, selection step (coordinator-approved): run ONLY the H2-off arm, with exactly the frozen run's off-arm
# arguments (run-h2-fresh.sh: tree app-611a4b92-h2, H1=0, H2=0, kit A, greedy, seed 42, quick mode), on Veil's pool.
# Items are selected by the OFF output only (instant FINAL answer), never by H2's decision (H2 is not run here).
# usage (mini): bash kiln/select-off.sh <pool.jsonl in kiln/> <tag>
set -uo pipefail
Q=${1:?pool}; TAG=${2:?tag}
cd <runner>/kiln/app-611a4b92-h2; mkdir -p kiln/runs
KIT=$HOME/boar/shared-data/crypto/boar-crypto.sqlite,$HOME/boar/shared-data/packs/boar-wikivoyage-en.sqlite,$HOME/boar/shared-data/packs/pinned/d3b87d562baba3489f6878bf99783f50d504db94c347029771e53f6d1aecc666/wiki-vital5.sqlite
for P in "ios 4 ios qwen2.5-1.5b-instruct-q4km" "android 12 android qwen3-4b-instruct-2507-q4km"; do
  set -- $P
  rm -f "kiln/runs/sel-$TAG-$1-off.jsonl"
  EXPO_PUBLIC_H1_SUBJECT=0 EXPO_PUBLIC_H2_ANSWERS=0 kiln/node_modules/.bin/tsx kiln/answerer.ts --commit "611a4b92+h1+h2-frozen" --model "$4" \
    --questions "kiln/$Q" --out "kiln/runs/sel-$TAG-$1-off.jsonl" --ram-gb "$2" --platform "$3" --pack "$KIT" --seed 42 --temp 0 \
    --o2 off --label "sel-$TAG-$1-off" --settings '{"quickFirst":true,"alwaysComplete":false}' 2>&1 | grep -E '"done"'
done
echo ALL-DONE
