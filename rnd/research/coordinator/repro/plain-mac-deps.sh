#!/usr/bin/env bash
# Install the Node dependencies the desktop-node runner needs on a plain Mac (no shared mini checkout).
# The original setup symlinked two pre-installed node_modules dirs; this creates one dir and you point both
# variables at it:   export BOAR_EVAL_APP_NM=$DIR/node_modules BOAR_EVAL_RUNNER_NM=$DIR/node_modules
# Versions: node-llama-cpp 3.21.1 is pinned as in the claim runs; tsx is any 4.x; fzstd and @noble/hashes are the
# only bare-specifier imports of the engine that are not shimmed (react-native, expo-*, llama.rn are shimmed).
# UNTESTED on a clean machine at the time of writing (the claim runs used the pre-installed dirs): see REPRODUCE.md.
set -euo pipefail
DIR="${1:-${BOAR_EVAL_DEPS:-$HOME/boar-repro-deps}}"
mkdir -p "$DIR"; cd "$DIR"
[[ -f package.json ]] || cat > package.json <<'J'
{ "name": "boar-repro-deps", "private": true, "type": "module",
  "dependencies": { "tsx": "^4.23.15", "node-llama-cpp": "3.21.1", "fzstd": "*", "@noble/hashes": "*" } }
J
npm install --no-audit --no-fund
echo "export BOAR_EVAL_APP_NM=$DIR/node_modules BOAR_EVAL_RUNNER_NM=$DIR/node_modules"
