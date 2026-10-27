#!/usr/bin/env bash
# MICROD2Q replays (0 LLM / 0 judge): d2q tree + d2qproto/<variant> COPIES. full: modes off,x1,x2,off on the 9 x 20 self-tests
# (kit + item's pack) and v0.1 public (kit only); deinfl: modes x1,x2 on the self-tests only. REF = runs/id-<set>.jsonl
# (same tree, published packs, first pass = OFF; identical to the tk2off reference modulo the prompt's date line). 4 in parallel.
set -uo pipefail
V=$1; B=<workspace>; cd $B
A=$B/rnd/research/coordinator/arms/microd2q; R=$A/tools/replay-d2q.sh; O=$A/runs; T=kiln-local/be-0cfd4a77-cut7-d2q; H=shared-data/packs/d2qproto/$V
M=off,x1,x2,off; [ $V = deinfl ] && M=x1,x2
job() { local set=$1 p=$2 PK=$H/boar-crypto.sqlite,$H/boar-wikivoyage-en.sqlite; [ -n "$p" ] && PK=$PK,$H/$p.sqlite
  local out=$O/$set.$V.jsonl; [ -s $out ] && return
  if [ $set = v01-kit ]; then Q="--questions boar-eval/bench/v0.1/questions.public.jsonl --gold boar-eval/bench/v0.1/gold/sources.json"
  else Q="--questions rnd/research/packs/selftest/$p.jsonl --gold none"; fi
  $R --gate search --k 6 --tree $T --modes $M --pool 8 --packs $PK $Q --out $out 2>&1 | grep -E '^\{|app dir|FATAL|error' | sed "s/^/[$set $V] /"; }
N=0
[ $V = full ] && { job v01-kit "" & N=$((N+1)); }
for p in qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en; do
  job st-$p $p & N=$((N+1)); [ $((N % 4)) -eq 0 ] && wait
done; wait
echo RUN-D2Q-DONE $V
