#!/usr/bin/env bash
# PACKCOND P4b (PACKDENSE D0): replay-pg.ts + dense-router diagnostic; header of replay-p4b.ts.
H="$(cd "$(dirname "$0")" && pwd)"; B="$(cd "$H/../../../../../.." && pwd)"
exec "$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx" "$H/replay-p4b.ts" "$@"
