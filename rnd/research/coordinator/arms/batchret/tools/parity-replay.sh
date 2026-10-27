#!/usr/bin/env bash
# BATCHRET: parity-replay.ts with the adapter's tsx (engine retrieval only, no LLM, no judge).
H="$(cd "$(dirname "$0")" && pwd)"; B="$(cd "$H/../../../../../.." && pwd)"
exec "$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx" "$H/parity-replay.ts" "$@"
