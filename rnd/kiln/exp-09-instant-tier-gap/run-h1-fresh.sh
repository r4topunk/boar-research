#!/usr/bin/env bash
# exp-09 FROZEN out-of-sample run of H1 (coordinator, 2026-10-01). Do not edit: hashed in FROZEN-h1.sha256.
# Tree <runner>/kiln/app-611a4b92-h1 = boar-app 611a4b92 + h1-subject-check.patch; kit A; greedy; seed 42; quick mode.
# Per profile: H1 off, H1 off again (determinism), H1 on. Only EXPO_PUBLIC_H1_SUBJECT differs.
# usage (mini): bash kiln/run-h1-fresh.sh <questions.jsonl, in kiln/> <tag>
set -uo pipefail
Q=${1:?questions file under kiln/}; TAG=${2:?tag}
cd <runner>/kiln/app-611a4b92-h1; mkdir -p kiln/runs
KIT=$HOME/boar/shared-data/crypto/boar-crypto.sqlite,$HOME/boar/shared-data/packs/boar-wikivoyage-en.sqlite,$HOME/boar/shared-data/packs/pinned/d3b87d562baba3489f6878bf99783f50d504db94c347029771e53f6d1aecc666/wiki-vital5.sqlite
run() { # label h1 ram platform model
  rm -f "kiln/runs/$1.jsonl"
  EXPO_PUBLIC_H1_SUBJECT=$2 kiln/node_modules/.bin/tsx kiln/answerer.ts --commit "611a4b92+h1-frozen" --model "$5" \
    --questions "kiln/$Q" --out "kiln/runs/$1.jsonl" --ram-gb "$3" --platform "$4" --pack "$KIT" --seed 42 --temp 0 \
    --o2 off --label "$1" --settings '{"quickFirst":true,"alwaysComplete":false}' 2>&1 | grep -E '"done"' ; }
for P in "ios 4 ios qwen2.5-1.5b-instruct-q4km" "android 12 android qwen3-4b-instruct-2507-q4km"; do
  set -- $P
  run "h1f-$TAG-$1-off" 0 "$2" "$3" "$4"
  run "h1f-$TAG-$1-off-rep" 0 "$2" "$3" "$4"
  run "h1f-$TAG-$1-on" 1 "$2" "$3" "$4"
done
echo ALL-DONE
