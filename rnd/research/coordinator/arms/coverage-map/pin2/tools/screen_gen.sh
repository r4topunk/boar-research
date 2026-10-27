#!/bin/bash
# PIN2-SCREEN generation on the mini = sefix/ans-tools/run_124_gen.sh recipe (base + H4-MERGE + SEFIX-ALL, packs-k13, SEFIX-124 env) [+ PIN2.patch + RS_PIN2=1].
# Usage: screen_gen.sh base|pin2 main|t27 (the adapter needs one runId/config per file, so 2 jobs per arm)     (mini_gen.sh under nohup: 2-slot guard, disk >= 25 GiB, detector :8094 used, never started/stopped)
set -u
ARM=$1; SET=$2; R=<workspace>/rnd/research/coordinator/arms; D=$R/coverage-map/pin2; LS=$R/lp-screens/tools; P=$R/retrieve-sweep/patches
REQ=$D/req/screen-$ARM-$SET-s42.requests.jsonl; RUN=pin2screen-$ARM-$SET-s42
M=MINI_HOST; MK=<runner>/kiln; BASE=$MK/be-0cfd4a77-cut7-litepacks; J=$MK/lp-screens/jobs/$RUN; TR=$D/traces/$RUN.traces.jsonl
[ "$(shasum -a 256 $P/SEFIX-ALL.patch | cut -c1-16)" = e3d6c3db8b85779a ] && [ "$(shasum -a 256 $P/H4-MERGE.patch | cut -c1-16)" = 4cd947558331df2e ] && [ "$(shasum -a 256 $P/PIN2.patch | cut -c1-16)" = d6c0533c511e0a43 ] || { echo "patch sha mismatch"; exit 1; }
CA=$(head -1 $REQ | python3 -I -c "import json,sys;print(json.loads(sys.stdin.readline())['config']['arm'])")
ENVF=$(mktemp); printf 'BOAR_EVAL_PACK_DIRS=<runner>/kiln/compose/packs-k13\nRS_MERGE=gidf\nRS_SE_LEAD=0.78\nRS_SE_MAXDF=0.25\nRS_KEEP_NOPROPER=1\n' > $ENVF
[ $ARM = pin2 ] && printf 'RS_PIN2=1\n' >> $ENVF
scp -q $LS/mini_gen.sh $M:$MK/lp-screens-mini_gen.sh || exit 1
ssh $M bash -s -- "$J" "$BASE" "$CA" <<'Y' || { echo "FAIL setup"; exit 1; }
set -e; J=$1; B=$2; CA=$3
[ "$(shasum -a 256 $B/src/routing/answer.ts | cut -c1-16)" = 0d1ac07dd1d664be ] && [ "$(shasum -a 256 $B/be/adapter-litedecline.ts | cut -c1-16)" = d53c14878ce4cbd3 ] && [ "$(cat $B/ARM)" = cut7-headpass-x2+litepacks ] || { echo "base tree mismatch"; exit 1; }
if [ -f $J/STATUS ] && ! grep -q -E '^(DONE|FAIL)' $J/STATUS; then echo "job running"; exit 1; fi
rm -rf $J; mkdir -p $J; cp -cR $B $J/tree; rm -rf $J/tree/be/.cache; echo "$CA" > $J/tree/ARM
Y
scp -q $REQ $M:$J/requests.jsonl && scp -q $ENVF $M:$J/env && scp -q $P/H4-MERGE.patch $M:$J/p1.patch && scp -q $P/SEFIX-ALL.patch $M:$J/p2.patch && scp -q $P/PIN2.patch $M:$J/p3.patch || exit 1; rm -f $ENVF
ssh $M bash -s -- "$J" "$ARM" <<'Z' || { echo "FAIL patch"; exit 1; }
set -e; cd $1/tree; patch -p1 -s < ../p1.patch; patch -p1 -s < ../p2.patch; [ "$2" = pin2 ] && patch -p1 -s < ../p3.patch; find . -name '*.orig' -delete
for k in RS_MERGE RS_KEEP_NOPROPER RS_PIN2; do echo "$k files=$(grep -rl $k src | wc -l)"; done; cat ../env
Z
ssh -T -n $M "nohup bash $MK/lp-screens-mini_gen.sh $J > $J/nohup.log 2>&1 < /dev/null &" || exit 1
echo "$(date +%T) started $RUN"
f=0; while :; do sleep 20; s=$(ssh -T -n -o ConnectTimeout=20 $M "tail -1 $J/STATUS" 2>/dev/null) || { f=$((f+1)); [ $f -ge 20 ] && { echo "FAIL unreachable"; exit 1; }; continue; }
  f=0; case $s in DONE) break;; FAIL*) echo "mini $s"; ssh -T -n $M "cat $J/STATUS; tail -20 $J/run.log"; exit 1;; esac; done
scp -q $M:$J/traces.jsonl $TR && scp -q $M:$J/STATUS $D/traces/$RUN.status && scp -q $M:$J/run.log $D/traces/$RUN.run.log || exit 1
ssh -T -n $M "rm -rf $J/tree" || true
[ "$(wc -l < $TR | tr -d ' ')" = "$(wc -l < $REQ | tr -d " ")" ] || { echo "FAIL rows"; exit 1; }
echo "$(date +%T) DONE $RUN"
