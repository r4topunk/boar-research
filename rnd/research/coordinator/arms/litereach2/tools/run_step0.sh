#!/usr/bin/env bash
# LITEREACH2 step 0 (criterion LITEREACH2-criterion.md sha b418afd6...; 0 LLM / 0 judge / 0 paid; MacBook).
# One replay process per (cell, pack): env BOAR_LR2_* is read at import. Resumable (finished outputs skipped).
# Cells: i3 = env unset, no --tasks-from (clone sanity vs headpass-st runs-x2 x2b); u1 = env unset + tasks-from; c1 b15 b20 t15 t20 = env set + tasks-from.
set -uo pipefail
B=<workspace>; cd $B
A=$B/rnd/research/coordinator/arms; L=$A/litereach2; R=$A/headpass-st/tools/replay-x2.sh; O=$L/runs/step0; mkdir -p $O
TREE=kiln-local/be-0cfd4a77-cut7-litereach2; V=shared-data/packs/v3proto
KIT=shared-data/crypto/boar-crypto.sqlite,shared-data/packs/boar-wikivoyage-en.sqlite
PACKS="qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en"
pub() { case "$1" in boar-factbook|boar-simplewiki-en) echo shared-data/packs/wave2/$1.sqlite;; *) echo shared-data/packs/wave1/$1.sqlite;; esac; }
envof() { case "$1" in c1) echo "600 2 4";; b15) echo "900 3 6";; b20) echo "1200 4 8";; t15) echo "900 2 4";; t20) echo "1200 2 4";; *) echo "";; esac; }
for cell in ${*:-i3 u1 c1 b15 b20 t15 t20}; do
  for p in $PACKS; do out=$O/$cell.$p.jsonl
    [ -s $out ] && { echo "[$cell $p] skip"; continue; }
    free=$(df -m <home> | awk 'NR==2{print int($4/1024)}'); [ "$free" -ge 5 ] || { echo "STOP disk ${free} GiB < 5"; exit 3; }
    args=(--gate search --k 6 --tree $TREE --modes x2b --packs $KIT,$(pub $p) --questions rnd/research/packs/selftest/$p.jsonl --gold none --sidecars $V --out $out.tmp)
    [ $cell != i3 ] && args+=(--tasks-from $A/lite5/runs/180/lite5-180-on-$p-s42.traces.jsonl)
    e=$(envof $cell); t0=$SECONDS
    if [ -n "$e" ]; then set -- $e; env BOAR_LR2_BUDGET_TOKENS=$1 BOAR_LR2_DENSE_D=$2 BOAR_LR2_MAX_APPEND=$3 $R "${args[@]}" > $O/$cell.$p.log 2>&1
    else env -u BOAR_LR2_BUDGET_TOKENS -u BOAR_LR2_DENSE_D -u BOAR_LR2_MAX_APPEND $R "${args[@]}" > $O/$cell.$p.log 2>&1; fi
    n=$(grep -c . $out.tmp 2>/dev/null || echo 0)
    if [ "$n" = 20 ]; then mv $out.tmp $out; echo "[$cell $p] ok $((SECONDS-t0)) s"; else echo "[$cell $p] INCOMPLETE $n/20 (see $O/$cell.$p.log)"; exit 2; fi
  done
done
echo STEP0-DONE $(date +%T)
