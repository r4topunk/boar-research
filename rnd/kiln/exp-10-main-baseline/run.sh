#!/usr/bin/env bash
# exp-10: main 6b53ee83 (restored pre-#18 engine) baseline. runner-main.ts, kit A as installed (vital5 + crypto +
# wikivoyage; main reads only vital5, see README), essential corpus, greedy, seed 42. Each profile twice (determinism).
set -uo pipefail
cd <runner>/kiln/app-6b53ee83; mkdir -p kiln/runs
KIT=$HOME/boar/shared-data/packs/pinned/d3b87d562baba3489f6878bf99783f50d504db94c347029771e53f6d1aecc666/wiki-vital5.sqlite,$HOME/boar/shared-data/crypto/boar-crypto.sqlite,$HOME/boar/shared-data/packs/boar-wikivoyage-en.sqlite
run() { # label ram platform model
  kiln/node_modules/.bin/tsx kiln/runner-main.ts --commit 6b53ee83 --model "$4" --questions kiln/questions.exp10.jsonl \
    --out "kiln/runs/$1.jsonl" --ram-gb "$2" --platform "$3" --pack "$KIT" --temp 0 --seed 42 --label "$1" 2>&1 | grep -E '"done"' ; }
run main-ios-1.5b 4 ios qwen2.5-1.5b-instruct-q4km
run main-ios-1.5b-rep 4 ios qwen2.5-1.5b-instruct-q4km
run main-android-4b 12 android qwen3-4b-instruct-2507-q4km
run main-android-4b-rep 12 android qwen3-4b-instruct-2507-q4km
echo ALL-DONE
