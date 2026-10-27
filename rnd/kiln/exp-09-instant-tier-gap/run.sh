#!/usr/bin/env bash
# exp-09: instant-tier gap. Real createAnswerer (exp-06 harness), boar-app 611a4b92 (main + O2 flag, O2 OFF), kit A
# (crypto + wikivoyage + wiki-vital5 + essential corpus), greedy (--temp 0), seed 42, quick mode. Two profiles.
set -uo pipefail
cd <runner>/kiln/app-611a4b92; mkdir -p kiln/runs
KIT=$HOME/boar/shared-data/crypto/boar-crypto.sqlite,$HOME/boar/shared-data/packs/boar-wikivoyage-en.sqlite,$HOME/boar/shared-data/packs/pinned/d3b87d562baba3489f6878bf99783f50d504db94c347029771e53f6d1aecc666/wiki-vital5.sqlite
run() { # label ram platform model
  rm -f "kiln/runs/$1.jsonl"
  kiln/node_modules/.bin/tsx kiln/answerer.ts --commit "611a4b92" --model "$4" --questions kiln/questions.exp09.jsonl \
    --out "kiln/runs/$1.jsonl" --ram-gb "$2" --platform "$3" --pack "$KIT" --seed 42 --temp 0 --o2 off --label "$1" \
    --settings '{"quickFirst":true,"alwaysComplete":false}' 2>&1 | grep -E '"done"' ; }
run exp09-ios-1.5b 4 ios qwen2.5-1.5b-instruct-q4km
run exp09-android-4b 12 android qwen3-4b-instruct-2507-q4km
echo ALL-DONE
