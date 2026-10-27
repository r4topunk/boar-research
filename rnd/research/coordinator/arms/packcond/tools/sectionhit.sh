#!/usr/bin/env bash
# PACKCOND SECTIONHIT: replay-p4b.ts + fact-section diagnostic; header of sectionhit.ts.
H="$(cd "$(dirname "$0")" && pwd)"; B="$(cd "$H/../../../../../.." && pwd)"
exec "$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx" "$H/sectionhit.ts" "$@"
