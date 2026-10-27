#!/usr/bin/env bash
# exp-07: 4 runs of vitalik58 on the SAME tree (14de107 + T2 patch), seed 42; only answerSettings.expandOnMiss changes.
# (a) iPhone 13: 4 GB, ios, Qwen2.5-1.5B (compact tier declines on a miss)   (b) Android: 12 GB, android, Qwen3-4B
set -uo pipefail
cd <runner>/kiln/app-14de107-t2; mkdir -p kiln/runs
PACKS=$HOME/boar/shared-data/crypto/boar-crypto.sqlite,$HOME/boar/shared-data/packs/boar-wikivoyage-en.sqlite
run() { # label ram platform model expand
  kiln/node_modules/.bin/tsx kiln/answerer.ts --commit "14de107+t2patch" --model "$4" --questions kiln/questions.vitalik58.jsonl \
    --out "kiln/runs/$1.jsonl" --ram-gb "$2" --platform "$3" --pack "$PACKS" --seed 42 --label "$1" \
    --settings "{\"quickFirst\":true,\"alwaysComplete\":false,\"expandOnMiss\":$5}" 2>&1 | grep -E '"done"' ; }
rm -f kiln/runs/{ios-1.5b,android-4b}-{off,on}.jsonl
run ios-1.5b-off 4 ios qwen2.5-1.5b-instruct-q4km false
run ios-1.5b-on 4 ios qwen2.5-1.5b-instruct-q4km true
run android-4b-off 12 android qwen3-4b-instruct-2507-q4km false
run android-4b-on 12 android qwen3-4b-instruct-2507-q4km true
echo ALL-DONE
