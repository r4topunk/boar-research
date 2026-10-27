#!/usr/bin/env bash
# T-K4a: replay-pg.ts + per-ref `pack` (chunkId pack id, "seed" otherwise); header of replay-crowd.ts.
H="$(cd "$(dirname "$0")" && pwd)"; B="$(cd "$H/../../../../../.." && pwd)"
exec "$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx" "$H/replay-crowd.ts" "$@"
