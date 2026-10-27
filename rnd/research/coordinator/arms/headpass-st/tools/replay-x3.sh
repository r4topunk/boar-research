#!/usr/bin/env bash
# HEADPASS-X2: replay-x3.ts with the adapter's tsx (engine retrieval + keep step, no LLM, no judge).
H="$(cd "$(dirname "$0")" && pwd)"; B="$(cd "$H/../../../../../.." && pwd)"
exec "$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx" "$H/replay-x3.ts" "$@"
