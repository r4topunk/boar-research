#!/usr/bin/env bash
# exp-08: O2 v2 as a deterministic paired counterfactual. Same tree (611a4b92 + o2v2.patch), same kit A
# (crypto + wikivoyage + wiki-vital5 = Plumb's D10 kit), iPhone 13 profile, Qwen2.5-1.5B, greedy (--temp 0), seed 42.
# Arms differ only in --o2. "off" runs twice to prove the arms are deterministic.
set -uo pipefail
cd <runner>/kiln/app-611a4b92; mkdir -p kiln/runs
KIT=$HOME/boar/shared-data/crypto/boar-crypto.sqlite,$HOME/boar/shared-data/packs/boar-wikivoyage-en.sqlite,$HOME/boar/shared-data/packs/pinned/d3b87d562baba3489f6878bf99783f50d504db94c347029771e53f6d1aecc666/wiki-vital5.sqlite
run() { # label o2
  rm -f "kiln/runs/$1.jsonl"
  kiln/node_modules/.bin/tsx kiln/answerer.ts --commit "611a4b92+o2v2patch" --model qwen2.5-1.5b-instruct-q4km \
    --questions kiln/questions.o2-ab82.jsonl --out "kiln/runs/$1.jsonl" --ram-gb 4 --platform ios --pack "$KIT" \
    --seed 42 --temp 0 --o2 "$2" --label "$1" --settings '{"quickFirst":true,"alwaysComplete":false}' 2>&1 | grep -E '"done"' ; }
run o2-off off
run o2-off-rep off
run o2-v1 v1
run o2-v2a a
run o2-v2c c
echo ALL-DONE
