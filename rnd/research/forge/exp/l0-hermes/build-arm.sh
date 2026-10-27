#!/bin/sh
# Replay bundles of the arm tree: rec/arm-<flags>.hbc for each flag set given (default: "" and "vectorCache").
# The recording has no rows for P-8's batched queries, so sqlBatch can't be replayed here (Kiln's desktop step 0 covers it).
set -e
cd "$(dirname "$0")"
ESB=<workspace>/boar-eval/node_modules/.pnpm/esbuild@0.28.2/node_modules/esbuild/bin/esbuild
HERMESC=${HERMESC:-$HOME/src/hermes-v1/build_release/bin/hermesc}
for F in "${@:-}" vectorCache; do
  N=${F:-none}
  $ESB replay/main-arm.ts --bundle --format=iife --target=es2020 --platform=neutral --main-fields=module,main --conditions=react-native,import \
    --alias:expo-sqlite=./replay/sqlite.ts --alias:expo-file-system/legacy=./replay/fs.ts --alias:expo-file-system=./replay/fs.ts \
    --alias:llama.rn=./replay/llama.ts --alias:react-native=./replay/rn.ts --alias:ram-monitor=./replay/ram.ts --alias:fzstd=./replay/fzstd.ts \
    --define:__DEV__=false --define:process.env.NODE_ENV='"production"' --define:__FORGE_FLAGS__="\"$F\"" --loader:.json=json \
    --banner:js='var process = globalThis.process || { env: {} };' --log-level=warning --outfile=rec/arm-$N.bundle.js
  { printf 'globalThis.__REC_RAW = '; cat rec/rec.json; printf ';\n'; cat rec/arm-$N.bundle.js; } > rec/arm-$N.js
  $HERMESC -O -emit-binary -out rec/arm-$N.hbc rec/arm-$N.js
  rm rec/arm-$N.js
done
