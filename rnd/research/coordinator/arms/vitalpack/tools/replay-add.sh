#!/usr/bin/env bash
# VITALPACK-ADD: deepcovfb replay-deep.ts + --add-pack id:k (settings.addPack); lines marked VITALADD.
H="$(cd "$(dirname "$0")" && pwd)"; B="$(cd "$H/../../../../../.." && pwd)"
exec "$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx" "$H/replay-add.ts" "$@"
