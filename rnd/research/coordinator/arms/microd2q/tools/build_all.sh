#!/usr/bin/env bash
# MICROD2Q: build the 11 d2qproto copies (9 self-test packs + 2 kit packs) for one questions variant, 3 at a time; df check.
# usage: build_all.sh <variant: full|deinfl> <questions-by-pack.json>
set -uo pipefail
V=$1; QJ=$(cd "$(dirname "$2")" && pwd)/$(basename "$2"); B=<workspace>; cd $B; A=$B/rnd/research/coordinator/arms/microd2q; O=shared-data/packs/d2qproto/$V; mkdir -p $O $A/runs/q-$V
one() { local src=$1 id; id=$(basename $src .sqlite)
  local free; free=$(df -g <home> | awk 'NR==2{print $4}'); echo "[$V $id] df free ${free} GiB"
  if [ "$free" -lt 9 ]; then echo "[$V $id] SKIP: disk < 9 GiB"; return; fi
  python3 -c "import json,sys; d=json.load(open('$QJ')); json.dump(d.get('$id',{}), open('$A/runs/q-$V/$id.json','w'))"
  local t=$(date +%s); node $A/tools/build_d2q.mjs $src $O/$id.sqlite $A/runs/q-$V/$id.json 2>&1 | grep -v Experimental && echo "[$V $id] built in $(( $(date +%s) - t )) s"
  shasum -a 256 $O/$id.sqlite >> $A/logs/d2qproto-$V.sha256; shasum -a 256 $src >> $A/logs/published-src-$V.sha256; }
L="shared-data/packs/wave1/boar-medlineplus-en.sqlite shared-data/packs/wave2/boar-factbook.sqlite shared-data/packs/wave1/boar-firstaid-en.sqlite
shared-data/packs/wave1/qa-health-se.sqlite shared-data/packs/wave1/qa-outdoors-se.sqlite shared-data/crypto/boar-crypto.sqlite shared-data/packs/wave1/qa-bitcoin-se.sqlite
shared-data/packs/wave1/qa-ethereum-se.sqlite shared-data/packs/wave1/qa-travel-se.sqlite shared-data/packs/boar-wikivoyage-en.sqlite shared-data/packs/wave2/boar-simplewiki-en.sqlite"
N=0; for s in $L; do one $s & N=$((N+1)); if [ $((N % 3)) -eq 0 ]; then wait; fi; done; wait
echo BUILD-ALL-DONE $V
