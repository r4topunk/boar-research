#!/bin/bash
# UXMATRIX MacBook driver: per mode (succinct|detailed), clone the scratch SEFIX-124 base tree, set ARM + adapter maxTokens, run every request group with local_gen.sh.
# Usage: run_local.sh <mode>...   outputs gen/<mode>/<group>/{traces,prompts}.jsonl (gitignored), log gen/<mode>.log
set -u
U=<workspace>/rnd/research/coordinator/arms/uxmatrix; S=<scratch>
for M in "$@"; do
  case $M in succinct) MT=512;; detailed) MT=1024;; *) echo "mode?"; exit 2;; esac
  T=$S/trees/uxm-$M; rm -rf $T; cp -cR $S/trees/base $T; rm -rf $T/be/.cache; echo "cut7-headpass-x2+litepacks+sefix124+uxm-$M" > $T/ARM
  A=$T/be/adapter-litedecline.ts
  [ "$(grep -c 'styleReminder: persona.styleReminder, maxTokens: 512 };' $A)" = 1 ] || { echo "adapter line not found"; exit 1; }
  [ $MT = 512 ] || sed -i '' "s/styleReminder: persona.styleReminder, maxTokens: 512 };/styleReminder: persona.styleReminder, maxTokens: $MT }; \/\/ UXMATRIX: Max Output Tokens $MT/" $A
  for R in $U/in/$M/*.requests.jsonl; do g=$(basename $R .requests.jsonl); O=$U/gen/$M/$g
    [ -f $O/STATUS ] && grep -q '^DONE' $O/STATUS && continue
    rm -rf $O; $U/tools/local_gen.sh $T $R $O; echo "$(date +%T) $M $g $(tail -1 $O/STATUS)"; done >> $U/gen/$M.log 2>&1
done
