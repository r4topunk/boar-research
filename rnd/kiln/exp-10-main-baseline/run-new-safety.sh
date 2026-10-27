#!/usr/bin/env bash
# exp-10 comparison arm: the NEW engine (611a4b92, the tree of the exp-09 base runs, O2 off) on the 12 safety-track
# items, same kit A / greedy / seed / profiles as exp-09 (whose runs already cover the bench 60).
set -uo pipefail
cd <runner>/kiln/app-611a4b92; mkdir -p kiln/runs
KIT=$HOME/boar/shared-data/crypto/boar-crypto.sqlite,$HOME/boar/shared-data/packs/boar-wikivoyage-en.sqlite,$HOME/boar/shared-data/packs/pinned/d3b87d562baba3489f6878bf99783f50d504db94c347029771e53f6d1aecc666/wiki-vital5.sqlite
for P in "ios 4 ios qwen2.5-1.5b-instruct-q4km" "android 12 android qwen3-4b-instruct-2507-q4km"; do
  set -- $P
  kiln/node_modules/.bin/tsx kiln/answerer.ts --commit 611a4b92 --model "$4" --questions kiln/questions.safety12.jsonl \
    --out "kiln/runs/new-$1-safety.jsonl" --ram-gb "$2" --platform "$3" --pack "$KIT" --seed 42 --temp 0 --o2 off --label "new-$1-safety" \
    --settings '{"quickFirst":true,"alwaysComplete":false}' 2>&1 | grep -E '"done"'
done
echo ALL-DONE
