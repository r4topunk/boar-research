#!/usr/bin/env bash
# Cross-encoder rerank replay over the engine's real retrieve() (no LLM, no judge); usage at the top of rerank-replay.ts.
H="$(cd "$(dirname "$0")" && pwd)"; B="$(cd "$H/../../../../../.." && pwd)"
exec "$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx" "$H/rerank-replay.ts" "$@"
