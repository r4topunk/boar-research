#!/usr/bin/env bash
# exp-08c: one arm on the mini (exp-06 P2 config, seed 42) via exp-08b's trees. Usage: bash run.sh <sha> <v58|hm>
set -euo pipefail
SHA="${1:?commit}"; SET="${2:?v58|hm}"; HERE="$(cd "$(dirname "$0")" && pwd)"; X8B="$HERE/../exp-08b-ios-main-regression"
<on the mini> "test -d <runner>/kiln/app-${SHA}-x8b" || bash "$X8B/setup.sh" "$SHA"
Q=kiln/questions.vitalik58.jsonl
if [ "$SET" = hm ]; then scp -q "$HERE/../../veil/hm-fresh.jsonl" "MINI_HOST:boar/kiln/app-${SHA}-x8b/kiln/hm-fresh.jsonl"; Q=kiln/hm-fresh.jsonl; fi
<on the mini> "bash -lc 'cd <runner>/kiln/app-${SHA}-x8b && HEAVY_CLASS=short <runner>/bin/run-heavy Kiln kiln/node_modules/.bin/tsx kiln/answerer.ts \
  --commit ${SHA} --model qwen2.5-1.5b-instruct-q4km --questions ${Q} --out kiln/runs/x8c-${SET}-${SHA}.jsonl \
  --ram-gb 4 --platform ios --label exp-08c --pack \$HOME/boar/shared-data/crypto/boar-crypto.sqlite,\$HOME/boar/shared-data/packs/boar-wikivoyage-en.sqlite \
  > kiln/runs/x8c-${SET}-${SHA}.log 2>&1'"
scp -q "MINI_HOST:boar/kiln/app-${SHA}-x8b/kiln/runs/x8c-${SET}-${SHA}.jsonl" "$HERE/runs/${SET}-${SHA}.jsonl"
scp -q "MINI_HOST:boar/kiln/app-${SHA}-x8b/kiln/runs/x8c-${SET}-${SHA}.log" "$HERE/runs/${SET}-${SHA}.log"
