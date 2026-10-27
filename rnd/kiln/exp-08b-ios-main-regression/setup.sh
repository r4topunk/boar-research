#!/usr/bin/env bash
# exp-08b: put boar-app src at a commit on the mini under <runner>/kiln/app-<sha>-x8b (own trees: never touches exp-06's),
# with exp-06's CURRENT runner (sha256 recorded in README) + the vitalik58 questions. Usage (MacBook): bash setup.sh <sha>
set -euo pipefail
SHA="${1:?commit}"; HERE="$(cd "$(dirname "$0")" && pwd)"; E6="$HERE/../exp-06-desktop-answerer"
APP=<workspace>/boar-app
FULL=$(git -C "$APP" rev-parse "$SHA")
DST="boar/kiln/app-${SHA}-x8b"
<on the mini> "mkdir -p ~/$DST/kiln/runs"
git -C "$APP" archive "$FULL" src assets locales modules package.json tsconfig.json | <on the mini> "tar -x -C ~/$DST"
rsync -az --exclude .cache "$E6/runner/" "MINI_HOST:$DST/kiln/"
scp -q "$E6/questions.vitalik58.jsonl" "MINI_HOST:$DST/kiln/"
<on the mini> "cd ~/$DST && echo $FULL > COMMIT && ln -sfn <runner>/official-6c3d6c6/node_modules node_modules && ln -sfn <runner>/eval-runner/eval/node_modules kiln/node_modules && du -sh ~/$DST"
