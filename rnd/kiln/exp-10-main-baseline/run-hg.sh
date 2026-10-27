#!/usr/bin/env bash
# exp-10 O-main-1 FROZEN run (coordinator protocol). Do not edit: hashed in FROZEN-hg.sha256.
# Tree <runner>/kiln/app-6b53ee83-hg = boar-app 6b53ee83 + main-health-guard.patch; runner-main.ts; kit A as installed
# (main reads vital5 only); essential corpus; greedy; seed 42. Per profile: guard off, off again (determinism), on.
# usage (mini): bash kiln/run-hg.sh <questions.jsonl in kiln/> <tag>
set -uo pipefail
Q=${1:?questions}; TAG=${2:?tag}
cd <runner>/kiln/app-6b53ee83-hg; mkdir -p kiln/runs
KIT=$HOME/boar/shared-data/packs/pinned/d3b87d562baba3489f6878bf99783f50d504db94c347029771e53f6d1aecc666/wiki-vital5.sqlite,$HOME/boar/shared-data/crypto/boar-crypto.sqlite,$HOME/boar/shared-data/packs/boar-wikivoyage-en.sqlite
run() { # label guard ram platform model
  EXPO_PUBLIC_MAIN_HEALTH_GUARD=$2 kiln/node_modules/.bin/tsx kiln/runner-main.ts --commit "6b53ee83+health-guard-frozen" --model "$5" \
    --questions "kiln/$Q" --out "kiln/runs/$1.jsonl" --ram-gb "$3" --platform "$4" --pack "$KIT" --temp 0 --seed 42 --label "$1" 2>&1 | grep -E '"done"' ; }
for P in "ios 4 ios qwen2.5-1.5b-instruct-q4km" "android 12 android qwen3-4b-instruct-2507-q4km"; do
  set -- $P
  run "hg-$TAG-$1-off" 0 "$2" "$3" "$4"
  run "hg-$TAG-$1-off-rep" 0 "$2" "$3" "$4"
  run "hg-$TAG-$1-on" 1 "$2" "$3" "$4"
done
echo ALL-DONE
