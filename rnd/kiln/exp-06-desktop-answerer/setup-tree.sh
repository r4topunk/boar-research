#!/usr/bin/env bash
# exp-06: put boar-app src/ AT A COMMIT on the Mac mini (git archive from the MacBook clone; nothing copied into this
# harness), plus this harness's runner under <tree>/kiln/. Node deps are symlinked, not installed:
#   <tree>/node_modules      -> <runner>/official-6c3d6c6/node_modules  (app deps: fzstd, i18next, …)
#   <tree>/kiln/node_modules -> <runner>/eval-runner/eval/node_modules  (node-llama-cpp 3.21.1, tsx)
# Usage (MacBook): bash setup-tree.sh <commit>      -> MINI_HOST:<runner>/kiln/app-<commit>/
set -euo pipefail
SHA="${1:?commit}"; HERE="$(cd "$(dirname "$0")" && pwd)"
APP=<workspace>/boar-app
FULL=$(git -C "$APP" rev-parse "$SHA")
DST="boar/kiln/app-${SHA}"
<on the mini> "mkdir -p ~/$DST/kiln"
git -C "$APP" archive "$FULL" src assets locales modules package.json tsconfig.json | <on the mini> "tar -x -C ~/$DST"
rsync -az --delete --exclude .cache "$HERE/runner/" "MINI_HOST:$DST/kiln/"
<on the mini> "cd ~/$DST && echo $FULL > COMMIT && ln -sfn <runner>/official-6c3d6c6/node_modules node_modules && ln -sfn <runner>/eval-runner/eval/node_modules kiln/node_modules && du -sh ~/$DST"
echo "tree ready: MINI_HOST:~/$DST (commit $FULL)"
