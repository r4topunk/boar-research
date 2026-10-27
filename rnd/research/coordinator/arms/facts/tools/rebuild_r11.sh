#!/bin/bash
# Rebuild the facts table r11 from the cached Wikidata responses (no network). Usage: tools/rebuild_r11.sh [out.json]
# Network only for a re-fetch: python3 -I tools/fetch_currency_r11.py <any facts.v1.json> data/raw (cached files are not refetched).
set -euo pipefail
cd "$(dirname "$0")/.."
OUT="${1:-data/facts.v1.r11.json}"
BASE="$(mktemp)"
python3 -I tools/build_asset.py data/raw "$BASE" 2> data/build-r11.gates.log | tail -1
python3 -I tools/build_r11.py "$BASE" "$OUT"
rm -f "$BASE"
shasum -a 256 "$OUT"
