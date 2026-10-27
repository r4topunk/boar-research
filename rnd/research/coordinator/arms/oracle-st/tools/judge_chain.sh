#!/bin/bash
# ORACLE-ST stage 2 driver: judges each (cell, judge, pack) as soon as that pack run's generation is done (20 traces + DONE + ids), with
# deepthink/tools/shard_judge.sh (N = 4, both orders). Priority = Opus ADD, Haiku ADD, Opus ONLY, Haiku ONLY (first ready item in that order each pass).
# Out: runs/<R>.judgments.opus.jsonl (system selftest-<pack>-cut7-<cell>-opus) and runs/<R>.judgments.jsonl (…-<cell>-haiku55-low).
# Resumable: an item is done when its output has 40 ok rows and an empty .missing; a failed item is retried at most twice.
# Usage: nohup judge_chain.sh > logs/judge_chain.log 2>&1 &
A=<workspace>/rnd/research/coordinator/arms/oracle-st; D=$A/runs; SJ=<workspace>/rnd/research/coordinator/arms/deepthink/tools/shard_judge.sh
PACKS="qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en"
ITEMS=(); for st in oracleadd:opus oracleadd:haiku oracleonly:opus oracleonly:haiku; do for p in $PACKS; do ITEMS+=("$st:$p"); done; done
out() { local c=$1 m=$2 p=$3 R=st-$3-cut7-$1-s42; [ $m = opus ] && echo "$D/$R.judgments.opus.jsonl" || echo "$D/$R.judgments.jsonl"; }
done_() { local O; O=$(out "$@"); [ -s "$O" ] && [ "$(grep -c '"ok":true' "$O")" -eq 40 ] && [ ! -s "${O%.jsonl}.missing" ]; }
ready() { local R=st-$3-cut7-$1-s42; [ "$(cat "$D/$R.traces.jsonl" 2>/dev/null | wc -l | tr -d ' ')" = 20 ] && grep -q DONE "$D/$R.traces.status" 2>/dev/null && [ -s "$D/$R.ids" ]; }
declare -i tries; TRIES=$A/logs/judge_tries; touch $TRIES
while true; do
  left=0; did=0
  for it in "${ITEMS[@]}"; do IFS=: read -r c m p <<< "$it"
    done_ $c $m $p && continue
    n=$(grep -c "^$it$" $TRIES); [ $n -ge 3 ] && continue
    left=1; ready $c $m $p || continue
    R=st-$p-cut7-$c-s42; O=$(out $c $m $p); [ $m = opus ] && SYS=selftest-$p-cut7-$c-opus || SYS=selftest-$p-cut7-$c-haiku55-low
    echo "$it" >> $TRIES; t=$(date +%s)
    "$SJ" "$D/$R.traces.jsonl" "$O" <workspace>/boar-eval/bench/selftest/$p "$D/$R.ids" "$SYS" 4 $m; rc=$?
    echo "JUDGED $R $m rc=$rc wall=$(( $(date +%s) - t ))s rows=$(cat "$O" | wc -l | tr -d ' ') $(date '+%T')"; did=1; break
  done
  [ $left = 0 ] && break; [ $did = 0 ] && sleep 30
done; echo ALLDONE
