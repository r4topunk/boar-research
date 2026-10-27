#!/usr/bin/env bash
# QWRITE step 0 replays (0 LLM / 0 judge): tk2off tree (pristine cut-7 copy) + PUBLISHED packs (claim kit + item pack), modes off,qw,off.
set -uo pipefail
B=<workspace>; cd $B
A=$B/rnd/research/coordinator/arms/qwrite; R=$A/tools/replay-qw.sh; O=$A/runs; T=kiln-local/be-0cfd4a77-cut7-tk2off
pub() { case "$1" in boar-crypto) echo shared-data/crypto/boar-crypto.sqlite;; boar-wikivoyage-en) echo shared-data/packs/boar-wikivoyage-en.sqlite;;
  boar-factbook|boar-simplewiki-en) echo shared-data/packs/wave2/$1.sqlite;; *) echo shared-data/packs/wave1/$1.sqlite;; esac; }
job() { local p=$1; local out=$O/st-$p.qw.jsonl; [ -s $out ] && return
  $R --gate search --k 6 --tree $T --modes off,qw,off --pool 8 --qmap $O/qmap.json --packs $(pub boar-crypto),$(pub boar-wikivoyage-en),$(pub $p) \
     --questions rnd/research/packs/selftest/$p.jsonl --gold none --out $out 2>&1 | grep -E '^\{|FATAL|rror' | sed "s/^/[$p] /"; }
N=0
for p in qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en; do
  job $p & N=$((N+1)); [ $((N % 3)) -eq 0 ] && wait
done; wait; echo RUN-QW-DONE
