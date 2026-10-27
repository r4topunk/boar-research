#!/bin/bash
# usage: build.sh <pack-id> "<name>" <manifest> <jsonl...>
set -euo pipefail
export PATH=/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin
cd <runner>/kiln/packs/builder
id=$1; name=$2; man=$3; shift 3
out=<runner>/kiln/packs/out/$id.sqlite
mkdir -p <runner>/kiln/packs/out
echo "CMD: BOAR_EMBED_GPU=metal node scripts/build-wiki-pack.mjs --out $out --manifest $man --name \"$name\" --shards $*"
s=$(date +%s)
BOAR_EMBED_GPU=metal node scripts/build-wiki-pack.mjs --out "$out" --manifest "$man" --name "$name" --shards "$@"
echo "WALL seconds: $(( $(date +%s) - s ))"
ls -la "$out" "$out.json" 2>&1
shasum -a 256 "$out"
