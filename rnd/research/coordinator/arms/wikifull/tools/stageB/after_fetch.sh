#!/bin/bash
# WIKIFULL stage B: after fetch.py -> convert -> build format-2 pack (FTS, no embeddings) -> sha. Resumable by step.
set -eu
W=<runner>/kiln/wikifull-b/work; B=<runner>/kiln/packs/builder; NODE=/opt/homebrew/bin/node
until grep -q '^DONE' <runner>/kiln/wikifull-b/logs/fetch.log; do pgrep -f tools/fetch.py >/dev/null || { echo "fetch not running and not DONE"; exit 1; }; sleep 60; done
cd $B
[ -s $W/delta-docs.stats.json ] || $NODE scripts/wikifullb_convert.mjs $W/fetch/raw.jsonl $W/delta-docs
[ -s $W/boar-wiki-en-B.sqlite.json ] || $NODE scripts/build-wiki-pack.mjs --out $W/boar-wiki-en-B.sqlite --shards $W/delta-docs.*.jsonl --no-embed \
  --name "English Wikipedia 20261001 pages outside FineWiki Aug-2025 (WIKIFULL stage B)"
shasum -a 256 $W/boar-wiki-en-B.sqlite > $W/boar-wiki-en-B.sqlite.sha256
echo ALLDONE
