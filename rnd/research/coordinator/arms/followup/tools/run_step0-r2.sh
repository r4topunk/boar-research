#!/usr/bin/env bash
# FOLLOWUP r2 step 0 (0 LLM / 0 judge): modes off,off,anc,anc on the patched tree; mode off on wt/pr1 for OFF identity. Inputs = r1's runs/q (frozen shas).
set -uo pipefail
B=<workspace>; cd $B
A=$B/rnd/research/coordinator/arms/followup; R=$A/tools/replay-fu2.sh; O=$A/runs/replay-r2; mkdir -p $O
KIT=shared-data/crypto/boar-crypto.sqlite,shared-data/packs/boar-wikivoyage-en.sqlite
FT=kiln-local/be-cut7-followup; PT=wt/pr1
pub() { case "$1" in boar-factbook|boar-simplewiki-en) echo shared-data/packs/wave2/$1.sqlite;; *) echo shared-data/packs/wave1/$1.sqlite;; esac; }
PACKS="qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en"
rr() { local tree=$1 modes=$2 packs=$3 q=$4 out=$5; [ -s $out ] && return 0
  $R --gate search --k 6 --tree $tree --modes $modes --packs $packs --questions $q --gold none --out $out 2>&1 | grep -E '^\{|app dir|rror|FATAL' | sed "s|^|[$(basename $out)] |"; }
for p in $PACKS; do
  rr $FT off,off,anc,anc $KIT,$(pub $p) $A/runs/q/t1-$p.jsonl $O/t1-$p.anc.jsonl
  rr $FT off,off,anc,anc $KIT,$(pub $p) $A/runs/q/t2-$p.jsonl $O/t2-$p.anc.jsonl
  rr $PT off $KIT,$(pub $p) $A/runs/q/t2-$p.jsonl $O/t2-$p.pr1.jsonl
done
rr $FT off,off,anc,anc $KIT boar-eval/bench/v0.1/questions.public.jsonl $O/v01-kit.anc.jsonl
rr $PT off $KIT boar-eval/bench/v0.1/questions.public.jsonl $O/v01-kit.pr1.jsonl
echo STEP0-DONE
