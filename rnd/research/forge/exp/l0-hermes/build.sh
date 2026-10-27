#!/bin/sh
# Build the L0 replay: rec/replay.bundle.js (app code + replay shims) and rec/run.js (recording + bundle) for Node and Hermes,
# plus rec/run.hbc (hermesc -O, as a release build ships). Needs rec/rec.json from record.mts.
set -e
cd "$(dirname "$0")"
ESB=<workspace>/boar-eval/node_modules/.pnpm/esbuild@0.28.2/node_modules/esbuild/bin/esbuild
HERMESC=${HERMESC:-$HOME/src/hermes-v1/build_release/bin/hermesc}
$ESB replay/main.ts --bundle --format=iife --target=es2020 --platform=neutral --main-fields=module,main --conditions=react-native,import \
  --alias:expo-sqlite=./replay/sqlite.ts --alias:expo-file-system/legacy=./replay/fs.ts --alias:expo-file-system=./replay/fs.ts \
  --alias:llama.rn=./replay/llama.ts --alias:react-native=./replay/rn.ts --alias:ram-monitor=./replay/ram.ts --alias:fzstd=./replay/fzstd.ts \
  --define:__DEV__=false --define:process.env.NODE_ENV='"production"' --loader:.json=json \
  --banner:js='var process = globalThis.process || { env: {} };' --log-level=warning --outfile=rec/replay.bundle.js
{ printf 'globalThis.__REC_RAW = '; cat rec/rec.json; printf ';\n'; cat rec/replay.bundle.js; } > rec/run.js
$HERMESC -O -emit-binary -out rec/run.hbc rec/run.js
