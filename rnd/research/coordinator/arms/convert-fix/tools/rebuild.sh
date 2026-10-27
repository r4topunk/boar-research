#!/bin/bash
# CONVERT-FIX test rebuild of boar-simplewiki-en into a scratch dir on the mini (0 LLM, 0 paid; local Metal embeddings).
# usage (on the mini): bash rebuild.sh   -- needs convert-fix.patch + simplewiki-convert.mjs copy in $S; resumable per phase.
# phase C = convert with the unpatched builder lib (control), phase P = convert with the patched lib (builder-cf), phase B = build the pack from P.
set -euo pipefail
export PATH=/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin
K=<runner>/kiln/packs; S=$K/work/convert-fix; B=$K/builder-cf
DUMP=$K/dl/simplewiki/simplewiki-20261001-pages-articles-multistream.xml.bz2
free() { df -Pk ~ | awk 'NR==2{printf "%d", $4/1048576}'; }
echo "$(date '+%F %T') start free=$(free)GiB"
if [ ! -d $B ]; then
  mkdir -p $B && cp -R $K/builder/scripts $B/scripts && ln -s $K/builder/node_modules $B/node_modules && cp $K/builder/package*.json $B/
  (cd $B && patch -p1 < $S/convert-fix.patch)
fi
mkdir -p $S/work
if [ ! -f $S/work/C.done ]; then
  ( cd $K/builder && node --max-old-space-size=6144 $K/scripts/wave2/simplewiki-convert.mjs $DUMP $S/work/ctrl $K/builder/scripts/lib 2026-10-01 )
  touch $S/work/C.done
fi
if [ ! -f $S/work/P.done ]; then
  ( cd $B && node --max-old-space-size=6144 $K/scripts/wave2/simplewiki-convert.mjs $DUMP $S/work/patched $B/scripts/lib 2026-10-01 )
  touch $S/work/P.done
fi
if [ ! -f $S/work/B.done ]; then
  s=$(date +%s); rm -f $S/work/boar-simplewiki-en.sqlite*
  ( cd $B && BOAR_EMBED_GPU=metal node --max-old-space-size=6144 scripts/build-wiki-pack.mjs --out $S/work/boar-simplewiki-en.sqlite \
      --manifest $S/work/patched/manifest.json --name "Simple English Wikipedia (2026-10-01)" --min-free-gb 25 \
      --shards $(ls $S/work/patched/simplewiki.*.jsonl | tr '\n' ' ') )
  echo "build wall $(( $(date +%s) - s ))s"; touch $S/work/B.done
fi
ls -la $S/work/boar-simplewiki-en.sqlite*; shasum -a 256 $S/work/boar-simplewiki-en.sqlite
echo "$(date '+%F %T') CF-DONE free=$(free)GiB"
