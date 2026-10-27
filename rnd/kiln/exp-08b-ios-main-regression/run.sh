#!/usr/bin/env bash
# exp-08b: one arm = exp-06's P2 config (iPhone 13 profile: 4 GB iOS, Qwen2.5-1.5B Q4_K_M, quick mode, crypto + Wikivoyage,
# seed 42, temp default 0.7) through the mini's heavy lock. Usage (MacBook): bash run.sh <sha>
set -euo pipefail
SHA="${1:?commit}"; SUF="${2:-}"; EXTRA="${3:-}"; HERE="$(cd "$(dirname "$0")" && pwd)"
<on the mini> "bash -lc 'cd <runner>/kiln/app-${SHA}-x8b && HEAVY_CLASS=short <runner>/bin/run-heavy Kiln kiln/node_modules/.bin/tsx kiln/answerer.ts \
  --commit ${SHA} --model qwen2.5-1.5b-instruct-q4km --questions kiln/questions.vitalik58.jsonl --out kiln/runs/x8b-${SHA}${SUF}.jsonl \
  --ram-gb 4 --platform ios --label exp-08b ${EXTRA} --pack \$HOME/boar/shared-data/crypto/boar-crypto.sqlite,\$HOME/boar/shared-data/packs/boar-wikivoyage-en.sqlite \
  > kiln/runs/x8b-${SHA}${SUF}.log 2>&1'"
scp -q "MINI_HOST:boar/kiln/app-${SHA}-x8b/kiln/runs/x8b-${SHA}${SUF}.*" "$HERE/runs/"
