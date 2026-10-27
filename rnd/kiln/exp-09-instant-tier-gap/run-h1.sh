#!/usr/bin/env bash
# exp-09 H1 end-to-end: same tree (611a4b92 + h1-subject-check.patch), H1 off vs on (EXPO_PUBLIC_H1_SUBJECT), on the 51
# questions whose answer showed something from the instant tier in the exp-09 run; greedy, seed 42, kit A, 2 profiles.
set -uo pipefail
cd <runner>/kiln/app-611a4b92-h1; mkdir -p kiln/runs
KIT=$HOME/boar/shared-data/crypto/boar-crypto.sqlite,$HOME/boar/shared-data/packs/boar-wikivoyage-en.sqlite,$HOME/boar/shared-data/packs/pinned/d3b87d562baba3489f6878bf99783f50d504db94c347029771e53f6d1aecc666/wiki-vital5.sqlite
IDS=vit-fa-003,vit-trv-001,vit-trv-002,vit-trv-004,vit-cry-011,vit-fa-011,vit-fa-015,vit-fa-017,vit-fa-020,vit-fa-022,vit-fa-023,vit-fa-024,vit-fa-025,vit-fa-027,food-001,food-002,food-006,dng-001,dng-002,dng-005,vit-o2b-001,vit-o2b-003,vit-o2b-006,vit-o2b-007,vit-o2b-008,vit-o2b-009,vit-o2b-011,vit-o2b-013,vit-o2b-014,vit-o2b-020,vit-o2b-021,vit-o2b-022,vit-o2b-023,vit-o2b-024,vit-o2c-003,vit-o2c-004,vit-o2c-005,vit-o2c-013,vit-o2c-014,vit-o2c-015,vit-o2c-016,vit-o2c-018,vit-o2c-019,vit-o2c-020,vit-o2c-027,vit-o2c-029,vit-o2c-030,vit-o2c-035,vit-o2c-037,vit-o2c-038,vit-o2c-039
run() { # label h1 ram platform model
  rm -f "kiln/runs/$1.jsonl"
  EXPO_PUBLIC_H1_SUBJECT=$2 kiln/node_modules/.bin/tsx kiln/answerer.ts --commit "611a4b92+h1patch" --model "$5" --questions kiln/questions.exp09.jsonl \
    --ids "$IDS" --out "kiln/runs/$1.jsonl" --ram-gb "$3" --platform "$4" --pack "$KIT" --seed 42 --temp 0 --o2 off --label "$1" \
    --settings '{"quickFirst":true,"alwaysComplete":false}' 2>&1 | grep -E '"done"' ; }
run h1-ios-off 0 4 ios qwen2.5-1.5b-instruct-q4km
run h1-ios-on 1 4 ios qwen2.5-1.5b-instruct-q4km
run h1-android-off 0 12 android qwen3-4b-instruct-2507-q4km
run h1-android-on 1 12 android qwen3-4b-instruct-2507-q4km
echo ALL-DONE
