#!/usr/bin/env bash
# H8-ST step 0 replays (0 LLM / 0 judge). REF = tk2off tree (pristine cut-7 copy) + PUBLISHED packs, modes off;
# H8 = kiln-local/be-0cfd4a77-cut7-h8 (cut 7 + h8st.vs-cut7.patch) + h8proto COPIES, modes off,lead,off.
# Public sets only: v0.1 public (kit) and the 9 x 20 self-tests (kit + the item's pack). 4 runs in parallel.
set -uo pipefail
B=<workspace>; cd $B
A=$B/rnd/research/coordinator/arms/h8st; R=$A/tools/replay-h8.sh; O=$A/runs; H=shared-data/packs/h8proto
pub() { case "$1" in boar-crypto) echo shared-data/crypto/boar-crypto.sqlite;; boar-wikivoyage-en) echo shared-data/packs/boar-wikivoyage-en.sqlite;;
  boar-factbook|boar-simplewiki-en) echo shared-data/packs/wave2/$1.sqlite;; *) echo shared-data/packs/wave1/$1.sqlite;; esac; }
job() { local cell=$1 set=$2 p=$3; local T M PK
  if [ $cell = ref ]; then T=kiln-local/be-0cfd4a77-cut7-tk2off; M=off; PK=$(pub boar-crypto),$(pub boar-wikivoyage-en); [ -n "$p" ] && PK=$PK,$(pub $p)
  else T=kiln-local/be-0cfd4a77-cut7-h8; M=off,lead,off; PK=$H/boar-crypto.sqlite,$H/boar-wikivoyage-en.sqlite; [ -n "$p" ] && PK=$PK,$H/$p.sqlite; fi
  local out=$O/$set.$cell.jsonl; [ -s $out ] && return
  if [ $set = v01-kit ]; then Q="--questions boar-eval/bench/v0.1/questions.public.jsonl --gold boar-eval/bench/v0.1/gold/sources.json"
  else Q="--questions rnd/research/packs/selftest/$p.jsonl --gold none"; fi
  $R --gate search --k 6 --tree $T --modes $M --pool 8 --packs $PK $Q --out $out 2>&1 | grep -E '^\{|app dir|FATAL|error' | sed "s/^/[$set $cell] /"; }
N=0
for cell in ref h8; do
  job $cell v01-kit "" & N=$((N+1)); [ $((N % 4)) -eq 0 ] && wait
  for p in qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en; do
    job $cell st-$p $p & N=$((N+1)); [ $((N % 4)) -eq 0 ] && wait
  done
done; wait
echo RUN-H8-DONE
