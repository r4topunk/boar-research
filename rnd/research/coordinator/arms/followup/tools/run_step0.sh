#!/usr/bin/env bash
# FOLLOWUP step 0 (0 LLM / 0 judge): replay cells on the followup tree (modes off,off,fu,fu) and on wt/pr1 (mode off) for OFF identity.
set -uo pipefail
B=<workspace>; cd $B
A=$B/rnd/research/coordinator/arms/followup; R=$A/tools/replay-fu.sh; O=$A/runs/replay; mkdir -p $O
KIT=shared-data/crypto/boar-crypto.sqlite,shared-data/packs/boar-wikivoyage-en.sqlite
FT=kiln-local/be-cut7-followup; PT=wt/pr1
pub() { case "$1" in boar-factbook|boar-simplewiki-en) echo shared-data/packs/wave2/$1.sqlite;; *) echo shared-data/packs/wave1/$1.sqlite;; esac; }
PACKS="qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en"
rr() { local tree=$1 modes=$2 packs=$3 q=$4 out=$5; [ -s $out ] && return 0
  $R --gate search --k 6 --tree $tree --modes $modes --packs $packs --questions $q --gold none --out $out 2>&1 | grep -E '^\{|app dir|rror|FATAL' | sed "s|^|[$(basename $out)] |"; }
phase=${1:-all}
if [ $phase = t1 ] || [ $phase = all ]; then
  python3 -I $A/tools/mkq.py t1
  for p in $PACKS; do rr $FT off,off,fu,fu $KIT,$(pub $p) $A/runs/q/t1-$p.jsonl $O/t1-$p.fu.jsonl; done
  rr $FT off,off,fu,fu $KIT boar-eval/bench/v0.1/questions.public.jsonl $O/v01-kit.fu.jsonl
  rr $PT off $KIT boar-eval/bench/v0.1/questions.public.jsonl $O/v01-kit.pr1.jsonl
fi
if [ $phase = t2 ] || [ $phase = all ]; then
  python3 -I $A/tools/mkq.py t2
  for p in $PACKS; do rr $FT off,off,fu,fu $KIT,$(pub $p) $A/runs/q/t2-$p.jsonl $O/t2-$p.fu.jsonl
                      rr $PT off $KIT,$(pub $p) $A/runs/q/t2-$p.jsonl $O/t2-$p.pr1.jsonl; done
fi
echo STEP0-DONE
