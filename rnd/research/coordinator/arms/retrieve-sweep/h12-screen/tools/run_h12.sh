#!/bin/bash
# H1+H2 answer screen generation on the Mac mini (= decode-ground/tools/run_dg.sh layout): APFS clone of the K1 litepacks tree + patches/H12-H1plusH2.patch,
# env RS_HP_SLATE=1 RS_HEALTH_TOPIC_FB=1, lp-screens/tools/mini_gen.sh under nohup (2-slot guard, disk >= 25 GiB, detector :8094 used, never started/stopped). No judging here.
# Usage: run_h12.sh REQUESTS RUN        NOWAIT=1 = start and exit
set -u
REQ=$1; RUN=$2
R=<workspace>/rnd/research/coordinator/arms/retrieve-sweep; H=$R/h12-screen; LS=$R/../lp-screens/tools; PF=$R/patches/H12-H1plusH2.patch
M=MINI_HOST; MK=<runner>/kiln; BASE=$MK/be-0cfd4a77-cut7-litepacks; J=$MK/lp-screens/jobs/$RUN
TR=$H/traces/$RUN.traces.jsonl; ST=$H/logs/$RUN.status
n=$(wc -l < $REQ | tr -d ' '); CA=$(head -1 $REQ | python3 -I -c "import json,sys;print(json.loads(sys.stdin.readline())['config']['arm'])")
ENVF=$(mktemp); printf 'RS_HP_SLATE=1\nRS_HEALTH_TOPIC_FB=1\nBOAR_EVAL_PACK_DIRS=<runner>/kiln/h12/packs-k1\n' > $ENVF
scp -q $LS/mini_gen.sh $M:$MK/lp-screens-mini_gen.sh || exit 1
ssh $M bash -s -- "$J" "$BASE" "$CA" <<'X' || { echo "FAIL setup"; exit 1; }
set -e; J=$1; B=$2; CA=$3
[ "$(shasum -a 256 $B/src/routing/answer.ts | cut -c1-16)" = 0d1ac07dd1d664be ] && [ "$(shasum -a 256 $B/be/adapter-litedecline.ts | cut -c1-16)" = d53c14878ce4cbd3 ] && [ "$(cat $B/ARM)" = cut7-headpass-x2+litepacks ] || { echo "base tree mismatch"; exit 1; }
if [ -f $J/STATUS ] && ! grep -q -E '^(DONE|FAIL)' $J/STATUS; then echo "job running"; exit 1; fi
rm -rf $J; mkdir -p $J; cp -cR $B $J/tree; rm -rf $J/tree/be/.cache; echo "$CA" > $J/tree/ARM
X
scp -q $REQ $M:$J/requests.jsonl && scp -q $PF $M:$J/candidate.patch && scp -q $ENVF $M:$J/env || exit 1; rm -f $ENVF
ssh -T -n $M "cd $J/tree && patch -p1 -s < ../candidate.patch && find . -name '*.orig' -delete && grep -c 'RS_HP_SLATE' src/routing/answer.ts && grep -c 'RS_HEALTH_TOPIC_FB' src/routing/healthTopicFallback.ts && cat ../env" || { echo "FAIL patch"; exit 1; }
ssh -T -n $M "nohup bash $MK/lp-screens-mini_gen.sh $J > $J/nohup.log 2>&1 < /dev/null &" || exit 1
echo "$(date +%T) started $RUN on mini ($n items, job $J)"
[ "${NOWAIT:-0}" = 1 ] && exit 0
f=0; while :; do sleep 30; s=$(ssh -T -n -o ConnectTimeout=20 $M "tail -1 $J/STATUS" 2>/dev/null) || { f=$((f+1)); [ $f -ge 20 ] && { echo "FAIL unreachable"; exit 1; }; continue; }
  f=0; case $s in DONE) break;; FAIL*) echo "mini $s"; ssh -T -n $M "cat $J/STATUS; tail -20 $J/run.log"; scp -q $M:$J/STATUS $ST; exit 1;; esac; done
scp -q $M:$J/traces.jsonl $TR && scp -q $M:$J/STATUS $ST && scp -q $M:$J/run.log $H/logs/$RUN.run.log || exit 1
ssh -T -n $M "rm -rf $J/tree" || true
[ "$(wc -l < $TR | tr -d ' ')" = "$n" ] || { echo "FAIL rows"; exit 1; }
echo "$(date +%T) DONE $RUN rows=$n"
