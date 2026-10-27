#!/bin/bash
# RD2 generation on the mini = sefix/ans-tools/run_f1b_gen.sh (G mode: H4-MERGE patch, RS_MERGE=gidf, v3 pack dir compose/packs-f1b) + the RD2 patch + extra env lines.
# Usage: run_rd2_gen.sh REQUESTS RUN "KEY=VAL KEY=VAL"   (traces -> reader/traces/RUN.traces.jsonl)
set -u
REQ=$1; RUN=$2; XENV=${3:-}
R=<workspace>/rnd/research/coordinator/arms; C=$R/coverage-map/reader; LS=$R/lp-screens/tools; PF=$R/retrieve-sweep/patches/H4-MERGE.patch
PR=$R/retrieve-sweep/patches/RD2-READ-GROUND-cite-or-ground-for-uncited-but-supported-compact-answers.patch
M=MINI_HOST; MK=<runner>/kiln; BASE=$MK/be-0cfd4a77-cut7-litepacks; J=$MK/lp-screens/jobs/$RUN
TR=$C/traces/$RUN.traces.jsonl; ST=$C/logs/$RUN.status
n=$(wc -l < $REQ | tr -d ' '); CA=$(head -1 $REQ | python3 -I -c "import json,sys;print(json.loads(sys.stdin.readline())['config']['arm'])")
ENVF=$(mktemp); printf 'BOAR_EVAL_PACK_DIRS=<runner>/kiln/compose/packs-f1b\nRS_MERGE=gidf\n' > $ENVF
for kv in $XENV; do echo "$kv" >> $ENVF; done
scp -q $LS/mini_gen.sh $M:$MK/lp-screens-mini_gen.sh || exit 1
ssh $M bash -s -- "$J" "$BASE" "$CA" <<'Y' || { echo "FAIL setup"; exit 1; }
set -e; J=$1; B=$2; CA=$3
[ "$(shasum -a 256 $B/src/routing/answer.ts | cut -c1-16)" = 0d1ac07dd1d664be ] && [ "$(shasum -a 256 $B/be/adapter-litedecline.ts | cut -c1-16)" = d53c14878ce4cbd3 ] && [ "$(cat $B/ARM)" = cut7-headpass-x2+litepacks ] || { echo "base tree mismatch"; exit 1; }
if [ -f $J/STATUS ] && ! grep -q -E '^(DONE|FAIL)' $J/STATUS; then echo "job running"; exit 1; fi
rm -rf $J; mkdir -p $J; cp -cR $B $J/tree; rm -rf $J/tree/be/.cache; echo "$CA" > $J/tree/ARM
Y
scp -q $REQ $M:$J/requests.jsonl && scp -q $ENVF $M:$J/env && scp -q $PF $M:$J/candidate.patch && scp -q $PR $M:$J/rd2.patch || exit 1; rm -f $ENVF
ssh -T -n $M "cd $J/tree && patch -p1 -s < ../candidate.patch && patch -p1 -s < ../rd2.patch && find . -name '*.orig' -delete && grep -c 'RS_MERGE' src/rag/packs.ts && grep -c 'READ_GROUND' src/routing/answer.ts && shasum -a 256 src/routing/answer.ts src/routing/citations.ts | cut -c1-16 && cat ../env" || { echo "FAIL patch"; exit 1; }
ssh -T -n $M "nohup bash $MK/lp-screens-mini_gen.sh $J > $J/nohup.log 2>&1 < /dev/null &" || exit 1
echo "$(date +%T) started $RUN on mini ($n items, job $J)"
f=0; while :; do sleep 30; s=$(ssh -T -n -o ConnectTimeout=20 $M "tail -1 $J/STATUS" 2>/dev/null) || { f=$((f+1)); [ $f -ge 20 ] && { echo "FAIL unreachable"; exit 1; }; continue; }
  f=0; case $s in DONE) break;; FAIL*) echo "mini $s"; ssh -T -n $M "cat $J/STATUS; tail -20 $J/run.log"; scp -q $M:$J/STATUS $ST; exit 1;; esac; done
scp -q $M:$J/traces.jsonl $TR && scp -q $M:$J/STATUS $ST && scp -q $M:$J/run.log $C/logs/$RUN.run.log || exit 1
ssh -T -n $M "rm -rf $J/tree" || true
[ "$(wc -l < $TR | tr -d ' ')" = "$n" ] || { echo "FAIL rows"; exit 1; }
echo "$(date +%T) DONE $RUN rows=$n"
