#!/usr/bin/env bash
# exp-07 rerun of the 4 T2-ON runs after the adapter fix (enableThinking:false wrapper; see README §Harness bug).
# OFF runs are unaffected (no enableThinking:false call on the answer path); checked by the 0-regression test.
set -uo pipefail
cd <runner>/kiln/app-14de107-t2; mkdir -p kiln/runs
P2=$HOME/boar/shared-data/crypto/boar-crypto.sqlite,$HOME/boar/shared-data/packs/boar-wikivoyage-en.sqlite
P3=$P2,$HOME/boar/shared-data/packs/pinned/d3b87d562baba3489f6878bf99783f50d504db94c347029771e53f6d1aecc666/wiki-vital5.sqlite
run() { # label ram platform model packs
  rm -f "kiln/runs/$1.jsonl"
  kiln/node_modules/.bin/tsx kiln/answerer.ts --commit "14de107+t2patch" --model "$4" --questions kiln/questions.vitalik58.jsonl \
    --out "kiln/runs/$1.jsonl" --ram-gb "$2" --platform "$3" --pack "$5" --seed 42 --label "$1" \
    --settings '{"quickFirst":true,"alwaysComplete":false,"expandOnMiss":true}' 2>&1 | grep -E '"done"' ; }
run ios-1.5b-on 4 ios qwen2.5-1.5b-instruct-q4km "$P2"
run android-4b-on 12 android qwen3-4b-instruct-2507-q4km "$P2"
run ios-1.5b-v5-on 4 ios qwen2.5-1.5b-instruct-q4km "$P3"
run android-4b-v5-on 12 android qwen3-4b-instruct-2507-q4km "$P3"
echo ALL-DONE
