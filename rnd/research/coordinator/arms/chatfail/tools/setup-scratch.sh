#!/bin/bash
# Builds the scratch trees for CHATFAIL S0 (never touches wt/pr1; read-only copies).
#   scratch/base    = wt/pr1 src (cut 7 + PR #85) + src/routing/followUp.ts(+test) from upstream/fullnative-dev (TS twin of Kotlin FollowUp.kt; absent on upstream/main)
#   scratch/patched = base + tools/chatfail-l2l3.patch
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"; PR1=<workspace>/wt/pr1; APP=<workspace>/boar-app
S="$HERE/scratch"; rm -rf "$S/base" "$S/patched"; mkdir -p "$S/base"
cp -R "$PR1/src" "$S/base/src"; cp "$PR1/package.json" "$PR1/vitest.config.ts" "$PR1/tsconfig.json" "$S/base/"
ln -s "$PR1/node_modules" "$S/base/node_modules"
git -C "$APP" show upstream/fullnative-dev:src/routing/followUp.ts      > "$S/base/src/routing/followUp.ts"
git -C "$APP" show upstream/fullnative-dev:src/routing/followUp.test.ts > "$S/base/src/routing/followUp.test.ts"
if [ -f "$HERE/tools/chatfail-l2l3.patch" ]; then
  cp -R "$S/base" "$S/patched" 2>/dev/null || true   # node_modules symlink copied as link
  (cd "$S/patched" && patch -p1 -s < "$HERE/tools/chatfail-l2l3.patch")
fi
echo ok
