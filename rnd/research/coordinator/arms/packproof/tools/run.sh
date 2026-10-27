#!/bin/bash
# PACKPROOF MacBook driver (criterion 37f74d6f): clone the scratch SEFIX-124 base tree, identity check (ident5), then every request group serially.
# Usage: run.sh ident | run.sh main      outputs gen/<group>/{traces,prompts}.jsonl STATUS (gitignored), log gen/run.log
set -u
P=<workspace>/rnd/research/coordinator/arms/packproof; S=<scratch>; T=$S/trees/packproof
mkdir -p $P/gen
if [ ! -d $T ]; then cp -cR $S/trees/base $T; rm -rf $T/be/.cache; echo "cut7-headpass-x2+litepacks+sefix124+packproof" > $T/ARM; fi
[ "$(shasum -a 256 $T/be/adapter-litedecline.ts | cut -c1-16)" = d53c14878ce4cbd3 ] || { echo "adapter sha mismatch"; exit 1; }
diff -rq $T/src <workspace>/kiln-local/rs-SEFIX/src > /dev/null || { echo "src differs from rs-SEFIX"; exit 1; }
if [ "$1" = ident ]; then O=$P/gen/ident5; rm -rf $O; $P/tools/local_gen.sh $T $P/in/ident5.requests.jsonl $O; echo "$(date +%T) ident5 $(tail -1 $O/STATUS)" >> $P/gen/run.log; exit 0; fi
for R in $P/in/on-k13.requests.jsonl $P/in/off-*.requests.jsonl $P/in/on-k13+*.requests.jsonl; do g=$(basename $R .requests.jsonl); O=$P/gen/$g
  [ -f $O/STATUS ] && grep -q '^DONE' $O/STATUS && continue
  rm -rf $O; $P/tools/local_gen.sh $T $R $O; echo "$(date +%T) $g $(tail -1 $O/STATUS)" >> $P/gen/run.log; done
echo "$(date +%T) ALL-END" >> $P/gen/run.log
