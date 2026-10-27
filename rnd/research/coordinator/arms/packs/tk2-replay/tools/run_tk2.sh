#!/usr/bin/env bash
# TK2-REPLAY: OFF = kiln-local/be-0cfd4a77-cut7-tk2off (byte clone of cut 7 src), ON = kiln-local/be-0cfd4a77-cut7-tk2 (cut 7 + tk2.vs-cut7.patch).
# Public sets only: v0.1 public (kit) and the 9 x 20 self-tests (kit + the item's pack). Passes off,off (repeat identity). 0 LLM / 0 judge.
set -uo pipefail
B=<workspace>; cd $B
A=$B/rnd/research/coordinator/arms/packs/tk2-replay; R=$A/tools/replay-tk2.sh; O=$A/runs
KIT=shared-data/crypto/boar-crypto.sqlite,shared-data/packs/boar-wikivoyage-en.sqlite
pub() { case "$1" in boar-factbook|boar-simplewiki-en) echo shared-data/packs/wave2/$1.sqlite;; *) echo shared-data/packs/wave1/$1.sqlite;; esac; }
for cell in off on; do
  T=kiln-local/be-0cfd4a77-cut7-tk2$([ $cell = off ] && echo off); C=(--gate search --k 6 --tree $T --modes off,off)
  [ -s $O/v01-kit.$cell.jsonl ] || $R "${C[@]}" --packs $KIT --questions boar-eval/bench/v0.1/questions.public.jsonl \
     --gold boar-eval/bench/v0.1/gold/sources.json --out $O/v01-kit.$cell.jsonl 2>&1 | grep -E '^\{|app dir' | sed "s/^/[v01 $cell] /"
  for p in qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en; do
    [ -s $O/st-$p.$cell.jsonl ] || $R "${C[@]}" --packs $KIT,$(pub $p) --questions rnd/research/packs/selftest/$p.jsonl --gold none \
       --out $O/st-$p.$cell.jsonl 2>&1 | grep -E '^\{|app dir' | sed "s/^/[st $p $cell] /"
  done
done
echo RUN-TK2-DONE
