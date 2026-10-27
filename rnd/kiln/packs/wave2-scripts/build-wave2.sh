#!/bin/bash
# T-K6 wave-2 builds as run on the mini (2026-10-13). Paths relative to <runner>/kiln/packs; this dir is copied to
# <runner>/kiln/packs/scripts/wave2/ (build.sh = wave1-scripts/build.sh, also at <runner>/kiln/packs/scripts/build.sh).
set -euo pipefail
export PATH=/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin
cd <runner>/kiln/packs
mkdir -p dl/simplewiki dl/factbook-src logs <runner>/shared-data/packs/wave2
# --- boar-factbook (convert 1 s, build 2 s)
[ -d dl/factbook-src/factbook.json ] || git clone --depth 1 https://github.com/factbook/factbook.json.git dl/factbook-src/factbook.json  # 144d6977
node convert/convert.mjs factbook dl/factbook-src/factbook.json --out work/boar-factbook --snapshot "2026-09-11 (repo commit 144d6977)"
node convert/validate.mjs work/boar-factbook
bash scripts/build.sh boar-factbook "CIA World Factbook (CC0 archive, data as of 2026-09-11)" \
  <runner>/kiln/packs/work/boar-factbook/manifest.json <runner>/kiln/packs/work/boar-factbook/factbook.jsonl > logs/build-boar-factbook.log 2>&1
# --- boar-simplewiki-en (download 2 min, convert 60 s, build 928 s of which lead embeddings ≈ 14 min at ≈ 225/s)
D=dl/simplewiki/simplewiki-20261001-pages-articles-multistream.xml.bz2   # 387,919,857 B, sha1 8a12322b… (dumpstatus.json)
[ -f $D ] || curl -sS -L -o $D https://dumps.wikimedia.org/simplewiki/20261001/simplewiki-20261001-pages-articles-multistream.xml.bz2
node --max-old-space-size=6144 scripts/wave2/simplewiki-convert.mjs $D work/boar-simplewiki-en <runner>/kiln/packs/builder/scripts/lib 2026-10-01 \
  > logs/convert-boar-simplewiki-en.log 2>&1
W=<runner>/kiln/packs/work/boar-simplewiki-en
bash scripts/build.sh boar-simplewiki-en "Simple English Wikipedia (2026-10-01)" $W/manifest.json $W/simplewiki.000.jsonl $W/simplewiki.001.jsonl \
  > logs/build-boar-simplewiki-en.log 2>&1
cp out/boar-factbook.sqlite* out/boar-simplewiki-en.sqlite* <runner>/shared-data/packs/wave2/
# MacBook: rsync MINI_HOST:boar/shared-data/packs/wave2/ shared-data/packs/wave2/
# Engine check (MacBook, T-K2 tree wt/packs): PACK=… PACKID=… QUERIES='q1|q2|q3' FTS='a|b' rnd/kiln/packs/wave2-scripts/run-check.sh <scratch dir>
