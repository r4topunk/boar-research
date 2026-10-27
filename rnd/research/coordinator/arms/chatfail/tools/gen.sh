#!/usr/bin/env bash
H="$(cd "$(dirname "$0")" && pwd)"; exec <workspace>/boar-eval/adapters/desktop-node/node_modules/.bin/tsx "$H/gen.mts" "$@"
