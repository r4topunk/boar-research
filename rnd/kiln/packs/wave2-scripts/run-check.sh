#!/bin/bash
# usage: PACK=/abs/x.sqlite PACKID=x QUERIES='q1|q2|q3' FTS='a|b' run-check.sh <scratch dir>
set -euo pipefail
S=${1:?scratch dir}; H="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$S"; cp "$H/check-pack.test.ts" "$S/"; ln -sfn <workspace>/wt/packs/node_modules "$S/node_modules"
echo 'export default { test: {} };' > "$S/vitest.config.mjs"
cd <workspace>/wt/packs
node_modules/.bin/vitest run --root "$S" --config "$S/vitest.config.mjs" --reporter=verbose 2>&1 | grep -v "^ *$"
