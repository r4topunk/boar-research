#!/usr/bin/env bash
# DEEPCOV-FB: deep-tier retrieval replay (copy of boar-eval replay-retrieval.ts + --deep/--pool); header of replay-pg.ts.
H="$(cd "$(dirname "$0")" && pwd)"; B="$(cd "$H/../../../../../.." && pwd)"
exec "$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx" "$H/replay-pg.ts" "$@"
