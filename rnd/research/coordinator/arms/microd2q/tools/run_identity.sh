#!/usr/bin/env bash
# MICROD2Q default-off identity + smoke (0 LLM / 0 judge). ID: d2q tree (cut 7 + d2q.vs-cut7.patch) + PUBLISHED packs, modes
# off,x2 (no fts_d2q table -> both must equal the tk2off reference h8st/runs/<set>.ref.jsonl). SMOKE: d2q tree + kit published
# + d2qproto medlineplus copy (1 chunk with questions), modes off,x1,x2,off. Public sets only; 4 jobs in parallel.
set -uo pipefail
B=<workspace>; cd $B
A=$B/rnd/research/coordinator/arms/microd2q; R=$A/tools/replay-d2q.sh; O=$A/runs; T=kiln-local/be-0cfd4a77-cut7-d2q
pub() { case "$1" in boar-crypto) echo shared-data/crypto/boar-crypto.sqlite;; boar-wikivoyage-en) echo shared-data/packs/boar-wikivoyage-en.sqlite;;
  boar-factbook|boar-simplewiki-en) echo shared-data/packs/wave2/$1.sqlite;; *) echo shared-data/packs/wave1/$1.sqlite;; esac; }
job() { local set=$1 p=$2 M=$3 PK=$4 out=$5; [ -s $out ] && return
  if [ $set = v01-kit ]; then Q="--questions boar-eval/bench/v0.1/questions.public.jsonl --gold boar-eval/bench/v0.1/gold/sources.json"
  else Q="--questions rnd/research/packs/selftest/$p.jsonl --gold none"; fi
  $R --gate search --k 6 --tree $T --modes $M --pool 8 --packs $PK $Q --out $out 2>&1 | grep -E '^\{|app dir|FATAL|error' | sed "s/^/[$set] /"; }
KIT=$(pub boar-crypto),$(pub boar-wikivoyage-en)
job st-boar-medlineplus-en boar-medlineplus-en off,x1,x2,off $KIT,shared-data/packs/d2qproto/boar-medlineplus-en.sqlite $O/smoke-medlineplus.d2q.jsonl &
job v01-kit "" off,x2 $KIT $O/id-v01-kit.jsonl &
N=2
for p in qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en; do
  job st-$p $p off,x2 $KIT,$(pub $p) $O/id-st-$p.jsonl & N=$((N+1)); [ $((N % 4)) -eq 0 ] && wait
done; wait
echo RUN-ID-DONE
