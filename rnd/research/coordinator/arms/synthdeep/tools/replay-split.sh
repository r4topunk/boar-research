#!/usr/bin/env bash
# SYNTHDEEP: deep-tier retrieval replay + --cmp-split; header of replay-split.ts.
H="$(cd "$(dirname "$0")" && pwd)"; B="$(cd "$H/../../../../../.." && pwd)"
exec "$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx" "$H/replay-split.ts" "$@"
