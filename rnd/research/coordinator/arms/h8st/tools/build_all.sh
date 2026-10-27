#!/usr/bin/env bash
# H8-ST: build the 11 h8proto copies (9 published wave-1/2 packs + 2 kit packs), 3 at a time; df check before each.
set -uo pipefail
B=<workspace>; cd $B; A=$B/rnd/research/coordinator/arms/h8st; O=shared-data/packs/h8proto
one() { local src=$1 id; id=$(basename $src .sqlite)
  local free; free=$(df -g <home> | awk 'NR==2{print $4}'); echo "[$id] df free ${free} GiB"
  if [ "$free" -lt 9 ]; then echo "[$id] SKIP: disk < 9 GiB"; return; fi
  local t=$(date +%s); node $A/tools/build_h8.mjs $src $O/$id.sqlite && echo "[$id] built in $(( $(date +%s) - t )) s"
  shasum -a 256 $O/$id.sqlite >> $A/logs/h8proto.sha256; shasum -a 256 $src >> $A/logs/published-src.sha256; }
L="shared-data/packs/wave1/boar-medlineplus-en.sqlite shared-data/packs/wave2/boar-factbook.sqlite shared-data/packs/wave1/boar-firstaid-en.sqlite
shared-data/packs/wave1/qa-health-se.sqlite shared-data/packs/wave1/qa-outdoors-se.sqlite shared-data/crypto/boar-crypto.sqlite shared-data/packs/wave1/qa-bitcoin-se.sqlite
shared-data/packs/wave1/qa-ethereum-se.sqlite shared-data/packs/wave1/qa-travel-se.sqlite shared-data/packs/boar-wikivoyage-en.sqlite shared-data/packs/wave2/boar-simplewiki-en.sqlite"
N=0; for s in $L; do one $s & N=$((N+1)); if [ $((N % 3)) -eq 0 ]; then wait; fi; done; wait
echo BUILD-ALL-DONE
