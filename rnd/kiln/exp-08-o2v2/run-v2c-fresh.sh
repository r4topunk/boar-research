#!/usr/bin/env bash
# exp-08 FROZEN out-of-sample run of O2 v2c (coordinator, 2026-10-01). Do not edit: hashed in FROZEN-v2c.sha256.
# Same tree, kit, profile, model, decoding as the in-sample arms (run-arms.sh); only the question file is new.
# usage (mini): bash kiln/run-v2c-fresh.sh <questions.jsonl, in kiln/> <tag>
set -uo pipefail
Q=${1:?questions file under kiln/}; TAG=${2:?tag}
cd <runner>/kiln/app-611a4b92; mkdir -p kiln/runs
KIT=$HOME/boar/shared-data/crypto/boar-crypto.sqlite,$HOME/boar/shared-data/packs/boar-wikivoyage-en.sqlite,$HOME/boar/shared-data/packs/pinned/d3b87d562baba3489f6878bf99783f50d504db94c347029771e53f6d1aecc666/wiki-vital5.sqlite
run() { # label o2
  rm -f "kiln/runs/$1.jsonl"
  kiln/node_modules/.bin/tsx kiln/answerer.ts --commit "611a4b92+o2v2c-frozen" --model qwen2.5-1.5b-instruct-q4km \
    --questions "kiln/$Q" --out "kiln/runs/$1.jsonl" --ram-gb 4 --platform ios --pack "$KIT" \
    --seed 42 --temp 0 --o2 "$2" --label "$1" --settings '{"quickFirst":true,"alwaysComplete":false}' 2>&1 | grep -E '"done"' ; }
run "fresh-$TAG-off" off
run "fresh-$TAG-off-rep" off
run "fresh-$TAG-v2c" c
echo ALL-DONE
