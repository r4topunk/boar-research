#!/bin/bash
# CONVERT-FIX-SHIP: rebuild boar-wikivoyage-en with the convert-fix lib (builder-cf) on the mini. Resumable per phase.
# Same two-pass recipe as WIKIVOYAGE-REBUILD's wv2-build.sh (pass 1 text/FTS, pass 2 embed-only), only the builder tree differs.
set -euo pipefail
export PATH=/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin
K=<runner>/kiln/packs; D=<runner>/shared-data; W=$K/work/wvcf
DUMP=$D/dumps/enwikivoyage-latest-pages-articles.xml.bz2
CAND=$D/packs/candidates/boar-wikivoyage-en-convfix
mkdir -p $W $CAND
free() { df -Pk ~ | awk 'NR==2{printf "%d", $4/1048576}'; }
echo "$(date '+%F %T') start free=$(free)GiB lib=$(md5 -q $K/builder-cf/scripts/lib/wiki-pack-lib.mjs)"
[ "$(free)" -ge 25 ] || { echo "disk below 25 GiB, stop"; exit 2; }
if [ ! -f $W/cand1.done ]; then
  rm -f $CAND/boar-wikivoyage-en.sqlite*; s=$(date +%s)
  ( cd $K/builder-cf && node --max-old-space-size=6000 scripts/build-wiki-pack.mjs --out $CAND/boar-wikivoyage-en.sqlite --shards $D/packs/empty.jsonl --wikivoyage $DUMP --name "English Wikivoyage" --no-embed --min-free-gb 25 )
  echo "cand pass1 wall $(( $(date +%s) - s ))s"; touch $W/cand1.done
fi
if [ ! -f $W/cand2.done ]; then
  s=$(date +%s)
  ( cd $K/builder-cf && BOAR_EMBEDDING_GGUF=$HOME/boar/shared-models/bge-small-en-v1.5-q8_0.gguf BOAR_EMBED_GPU=metal node --max-old-space-size=6000 scripts/build-wiki-pack.mjs --out $CAND/boar-wikivoyage-en.sqlite --shards none.jsonl --wikivoyage $DUMP --name "English Wikivoyage" --embed-only --embed-threads 2 --min-free-gb 25 )
  echo "cand pass2 wall $(( $(date +%s) - s ))s"; touch $W/cand2.done
fi
shasum -a 256 $CAND/boar-wikivoyage-en.sqlite; ls -la $CAND
echo "$(date '+%F %T') WVCF-DONE free=$(free)GiB"
