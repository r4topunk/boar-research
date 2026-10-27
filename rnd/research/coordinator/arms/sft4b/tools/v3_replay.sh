#!/usr/bin/env bash
# SFT4B v3 step 1b: engine retrieval (no LLM, no judge) for every (pack, question): kit + that pack, raw top-6 (--topk 6).
#   v3_replay.sh [pack ...]  (default: all 11). Resumable: an existing output is skipped.
set -uo pipefail
B=<workspace>; cd $B
A=$B/rnd/research/coordinator/arms/sft4b; R=$A/tools/replay-v3.sh; O=$A/runs/v3/replay
KIT=shared-data/crypto/boar-crypto.sqlite,shared-data/packs/boar-wikivoyage-en.sqlite
ALLP="boar-factbook boar-firstaid-en boar-medlineplus-en boar-simplewiki-en qa-bitcoin-se qa-cooking-se qa-ethereum-se qa-health-se qa-money-se qa-outdoors-se qa-travel-se"
pub() { for w in wave1 wave2 wave3; do [ -f shared-data/packs/$w/$1.sqlite ] && echo shared-data/packs/$w/$1.sqlite && return; done; }
for p in ${*:-$ALLP}; do
  [ -s $O/$p.raw.jsonl ] && continue
  $R --gate search --k 6 --topk 6 --tree wt/packs --packs $KIT,$(pub $p) --questions $O/$p.questions.jsonl --gold none --modes off \
    --out $O/$p.raw.jsonl.tmp 2>&1 | grep -E '^\{|app dir|FATAL' | sed "s/^/[$p] /"
  [ -s $O/$p.raw.jsonl.tmp ] && mv $O/$p.raw.jsonl.tmp $O/$p.raw.jsonl
done
echo V3-REPLAY-DONE
