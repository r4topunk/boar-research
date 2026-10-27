#!/usr/bin/env bash
# TK2-FIX step 0: cells cut7 / tk2 / tk2fix, public sets only, replay-tk2.sh (0 LLM / 0 judge). Usage: run_fix.sh [cells...]
set -uo pipefail
B=<workspace>; cd $B
A=$B/rnd/research/coordinator/arms/tk2fix; R=$B/rnd/research/coordinator/arms/packs/tk2-replay/tools/replay-tk2.sh; O=$A/runs
KIT=shared-data/crypto/boar-crypto.sqlite,shared-data/packs/boar-wikivoyage-en.sqlite
pub() { case "$1" in boar-factbook|boar-simplewiki-en) echo shared-data/packs/wave2/$1.sqlite;; *) echo shared-data/packs/wave1/$1.sqlite;; esac; }
tree() { case "$1" in cut7) echo kiln-local/be-0cfd4a77-cut7-tk2off;; tk2) echo kiln-local/be-0cfd4a77-cut7-tk2;; tk2fix) echo kiln-local/be-0cfd4a77-cut7-tk2fix;; esac; }
for cell in "${@:-cut7 tk2 tk2fix}"; do for c in $cell; do
  C=(--gate search --k 6 --tree $(tree $c) --modes off,off)
  [ -s $O/v01-kit.$c.jsonl ] || $R "${C[@]}" --packs $KIT --questions boar-eval/bench/v0.1/questions.public.jsonl \
     --gold boar-eval/bench/v0.1/gold/sources.json --out $O/v01-kit.$c.jsonl 2>&1 | grep -E '^\{|app dir|rror' | sed "s/^/[v01 $c] /"
  for p in qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en; do
    [ -s $O/st-$p.$c.jsonl ] || $R "${C[@]}" --packs $KIT,$(pub $p) --questions rnd/research/packs/selftest/$p.jsonl --gold none \
       --out $O/st-$p.$c.jsonl 2>&1 | grep -E '^\{|app dir|rror' | sed "s/^/[st $p $c] /"
  done
done; done
echo RUN-FIX-DONE
