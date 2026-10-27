#!/usr/bin/env bash
# GROUND-ST: replay-stack.ts with the adapter's tsx (engine retrieval, no LLM, no judge).
H="$(cd "$(dirname "$0")" && pwd)"; B="$(cd "$H/../../../../../.." && pwd)"
exec "$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx" "$H/replay-stack.ts" "$@"
