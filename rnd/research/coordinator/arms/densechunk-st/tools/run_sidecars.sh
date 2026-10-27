#!/usr/bin/env bash
# DENSECHUNK-ST: build every chunk_vecs sidecar (resumable; finished packs are skipped). Log: arms/densechunk-st/logs/sidecars.log
set -u
T=<workspace>; cd $T
TSX=$T/boar-eval/adapters/desktop-node/node_modules/.bin/tsx; S=$T/rnd/research/coordinator/arms/densechunk-st/tools/sidecar_embed.mjs
export BOAR_EMBEDDING_GGUF=$T/shared-models/bge-small-en-v1.5-q8_0.gguf BOAR_EMBED_GPU=metal
V=$T/shared-data/packs/v3proto
$TSX $S shared-data/crypto/boar-crypto.sqlite --out $V/boar-crypto.sqlite --name crypto
$TSX $S shared-data/packs/boar-wikivoyage-en.sqlite --out $V/boar-wikivoyage-en.sqlite --name wikivoyage
for p in wave1/boar-medlineplus-en wave2/boar-factbook wave1/qa-health-se wave1/boar-firstaid-en wave1/qa-outdoors-se wave1/qa-bitcoin-se wave1/qa-ethereum-se wave1/qa-travel-se wave2/boar-simplewiki-en; do
  df=$(df -g ~ | tail -1 | awk '{print $4}'); if [ "$df" -lt 8 ]; then echo "STOP: disk ${df} GiB < 8"; exit 3; fi
  $TSX $S shared-data/packs/$p.sqlite --out $V/$(basename $p).sqlite || echo "FAIL $p"
done
echo ALL-DONE
