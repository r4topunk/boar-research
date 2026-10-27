#!/bin/bash
# WIKIVOYAGE-REBUILD builds on the mini. Resume: rerun this script (each phase skips when its marker file exists).
# phase C = control (unpatched builder, pass 1 only), phase V = candidate (patched builder-wv2, pass 1 + embed-only pass 2).
set -euo pipefail
export PATH=/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin
K=<runner>/kiln/packs; D=<runner>/shared-data; W=$K/work/wv2
DUMP=$D/dumps/enwikivoyage-latest-pages-articles.xml.bz2
CAND=$D/packs/candidates/boar-wikivoyage-en-v2
mkdir -p $W $CAND
free() { df -Pk ~ | awk 'NR==2{printf "%d", $4/1048576}'; }
echo "$(date '+%F %T') start free=$(free)GiB"
if [ ! -f $W/control.done ]; then
  rm -f $W/control.sqlite*; s=$(date +%s)
  ( cd $K/builder && node --max-old-space-size=6000 scripts/build-wiki-pack.mjs --out $W/control.sqlite --shards $D/packs/empty.jsonl --wikivoyage $DUMP --name "English Wikivoyage" --no-embed --min-free-gb 25 )
  echo "control wall $(( $(date +%s) - s ))s"; touch $W/control.done
fi
if [ ! -f $W/cand1.done ]; then
  rm -f $CAND/boar-wikivoyage-en.sqlite*; s=$(date +%s)
  ( cd $K/builder-wv2 && node --max-old-space-size=6000 scripts/build-wiki-pack.mjs --out $CAND/boar-wikivoyage-en.sqlite --shards $D/packs/empty.jsonl --wikivoyage $DUMP --name "English Wikivoyage" --no-embed --min-free-gb 25 )
  echo "cand pass1 wall $(( $(date +%s) - s ))s"; touch $W/cand1.done
fi
if [ ! -f $W/cand2.done ]; then
  s=$(date +%s)
  ( cd $K/builder-wv2 && BOAR_EMBEDDING_GGUF=$HOME/boar/shared-models/bge-small-en-v1.5-q8_0.gguf BOAR_EMBED_GPU=metal node --max-old-space-size=6000 scripts/build-wiki-pack.mjs --out $CAND/boar-wikivoyage-en.sqlite --shards none.jsonl --wikivoyage $DUMP --name "English Wikivoyage" --embed-only --embed-threads 2 --min-free-gb 25 )
  echo "cand pass2 wall $(( $(date +%s) - s ))s"; touch $W/cand2.done
fi
shasum -a 256 $CAND/boar-wikivoyage-en.sqlite; ls -la $CAND
echo "$(date '+%F %T') WV2-DONE free=$(free)GiB"
