#!/usr/bin/env bash
# exp-09 O-H2 in-sample (exploratory, NOT frozen): tree 611a4b92 + H1 + H2 patches; arms off / H2 / H1+H2; 2 profiles;
# the questions (of 137 + 24) whose base run showed anything from the instant tier (others never reach the H2 code).
set -uo pipefail
cd <runner>/kiln/app-611a4b92-h2; mkdir -p kiln/runs
KIT=$HOME/boar/shared-data/crypto/boar-crypto.sqlite,$HOME/boar/shared-data/packs/boar-wikivoyage-en.sqlite,$HOME/boar/shared-data/packs/pinned/d3b87d562baba3489f6878bf99783f50d504db94c347029771e53f6d1aecc666/wiki-vital5.sqlite
run() { # label h1 h2 ram platform model
  rm -f "kiln/runs/$1.jsonl"
  EXPO_PUBLIC_H1_SUBJECT=$2 EXPO_PUBLIC_H2_ANSWERS=$3 kiln/node_modules/.bin/tsx kiln/answerer.ts --commit "611a4b92+h1+h2" --model "$6" \
    --questions kiln/questions.h2.jsonl --out "kiln/runs/$1.jsonl" --ram-gb "$4" --platform "$5" --pack "$KIT" --seed 42 --temp 0 \
    --o2 off --label "$1" --settings '{"quickFirst":true,"alwaysComplete":false}' 2>&1 | grep -E '"done"' ; }
for P in "ios 4 ios qwen2.5-1.5b-instruct-q4km" "android 12 android qwen3-4b-instruct-2507-q4km"; do
  set -- $P
  run "h2-$1-off" 0 0 "$2" "$3" "$4"
  run "h2-$1-h2" 0 1 "$2" "$3" "$4"
  run "h2-$1-h1h2" 1 1 "$2" "$3" "$4"
done
echo ALL-DONE
