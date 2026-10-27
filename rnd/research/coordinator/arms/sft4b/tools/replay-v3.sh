#!/usr/bin/env bash
# SFT4B v3: replay-v3.ts (copy of packroute replay-pr.ts + chunk bodies) with the adapter's tsx (engine retrieval, no LLM, no judge).
H="$(cd "$(dirname "$0")" && pwd)"; B="$(cd "$H/../../../../../.." && pwd)"
exec "$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx" "$H/replay-v3.ts" "$@"
