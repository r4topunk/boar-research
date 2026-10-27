#!/bin/bash
# P-7b step 0 (sonar/cards/p7-pack-block-size.md): rebuild boar-wikivoyage-en + boar-crypto exactly as knowledge-build/voyage.sh
# and crypto-rd.sh did on 2026-09-26 (same builder scripts-crypto/, same inputs, same embedding model on Metal), changing only
# --block-kb. New files under <runner>/kiln/p7/BLK/, never the current packs. 16 KB only (P-7b card); page size unchanged (builder: 8192).
set -euo pipefail
cd <runner>/knowledge-build
D=<runner>/shared-data; B=$D/crypto/build; P=<runner>/kiln/p7b
export BOAR_EMBEDDING_GGUF=<runner>/shared-models/bge-small-en-v1.5-q8_0.gguf BOAR_EMBED_GPU=metal
: > $P/empty.jsonl
for blk in 16; do
  mkdir -p $P/$blk; V=$P/$blk/boar-wikivoyage-en.sqlite; C=$P/$blk/boar-crypto.sqlite
  node --max-old-space-size=6000 scripts-crypto/build-wiki-pack.mjs --out $V --shards $P/empty.jsonl \
    --wikivoyage $D/dumps/enwikivoyage-latest-pages-articles.xml.bz2 --name "English Wikivoyage" --no-embed --block-kb $blk
  node scripts-crypto/build-wiki-pack.mjs --out $V --shards none.jsonl --wikivoyage $D/dumps/enwikivoyage-latest-pages-articles.xml.bz2 \
    --name "English Wikivoyage" --embed-only --embed-threads 2 --block-kb $blk
  node --max-old-space-size=6000 scripts-crypto/build-wiki-pack.mjs --out $C \
    --shards $B/eips.jsonl $B/bips.jsonl $B/specs.jsonl $B/ethereumorg.jsonl $B/wikipedia.jsonl \
    --manifest $B/pack-manifest.json --name "Ethereum and cryptography" \
    --redirects $D/dumps/enwiki-latest-redirect.sql.gz --index $D/dumps/enwiki-latest-pages-articles-multistream-index.txt.bz2 --no-embed --block-kb $blk
  node scripts-crypto/build-wiki-pack.mjs --out $C --shards none.jsonl --manifest $B/pack-manifest.json --name "Ethereum and cryptography" \
    --redirects $D/dumps/enwiki-latest-redirect.sql.gz --index $D/dumps/enwiki-latest-pages-articles-multistream-index.txt.bz2 --embed-only --embed-threads 2 --block-kb $blk
  df -g ~ | tail -1
done
shasum -a 256 $P/*/*.sqlite <runner>/shared-data/packs/boar-wikivoyage-en.sqlite <runner>/shared-data/crypto/boar-crypto.sqlite
ls -l $P/*/*.sqlite <runner>/shared-data/packs/boar-wikivoyage-en.sqlite <runner>/shared-data/crypto/boar-crypto.sqlite
echo P7-BUILD-DONE
