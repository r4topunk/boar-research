#!/bin/bash
# F3-SAFETY copy of ans-tools/run_all_gen.sh: only change = F3=1 env makes RS_HEALTH_NOSOURCE_FALLBACK=1 conditional, traces/status go to f3-safety/runs. Usage: F3=0|1 run_f3_gen.sh REQUESTS RUN G
# 13-pack kit from the verified per-run pack dir <runner>/kiln/compose/packs-k13, lp-screens/tools/mini_gen.sh under nohup (2-slot guard, disk >= 25 GiB, detector :8094 used, never started/stopped). No judging here.
# Usage: run_cmp.sh REQUESTS RUN S|G        NOWAIT=1 = start and exit
set -u
REQ=$1; RUN=$2; ARMK=$3
R=<workspace>/rnd/research/coordinator/arms; C=$R/coverage-map/sefix; LS=$R/lp-screens/tools; PF=$R/retrieve-sweep/patches/H4-MERGE.patch; PS=$R/retrieve-sweep/patches/SEFIX-ALL.patch
M=MINI_HOST; MK=<runner>/kiln; BASE=$MK/be-0cfd4a77-cut7-litepacks; J=$MK/lp-screens/jobs/$RUN
TR=$C/f3-safety/runs/$RUN.traces.jsonl; ST=$C/f3-safety/runs/$RUN.status
n=$(wc -l < $REQ | tr -d ' '); CA=$(head -1 $REQ | python3 -I -c "import json,sys;print(json.loads(sys.stdin.readline())['config']['arm'])")
ENVF=$(mktemp); printf 'BOAR_EVAL_PACK_DIRS=<runner>/kiln/compose/packs-k13\n' > $ENVF
printf 'RS_MERGE=gidf\nRS_SE_LEAD=0.78\nRS_SE_MAXDF=0.25\nRS_KEEP_NOPROPER=1\n' >> $ENVF; [ "${F3:-0}" = 1 ] && printf 'RS_HEALTH_NOSOURCE_FALLBACK=1\n' >> $ENVF
scp -q $LS/mini_gen.sh $M:$MK/lp-screens-mini_gen.sh || exit 1
ssh $M bash -s -- "$J" "$BASE" "$CA" <<'Y' || { echo "FAIL setup"; exit 1; }
set -e; J=$1; B=$2; CA=$3
[ "$(shasum -a 256 $B/src/routing/answer.ts | cut -c1-16)" = 0d1ac07dd1d664be ] && [ "$(shasum -a 256 $B/be/adapter-litedecline.ts | cut -c1-16)" = d53c14878ce4cbd3 ] && [ "$(cat $B/ARM)" = cut7-headpass-x2+litepacks ] || { echo "base tree mismatch"; exit 1; }
if [ -f $J/STATUS ] && ! grep -q -E '^(DONE|FAIL)' $J/STATUS; then echo "job running"; exit 1; fi
rm -rf $J; mkdir -p $J; cp -cR $B $J/tree; rm -rf $J/tree/be/.cache; echo "$CA" > $J/tree/ARM
Y
scp -q $REQ $M:$J/requests.jsonl && scp -q $ENVF $M:$J/env || exit 1; rm -f $ENVF
scp -q $PF $M:$J/candidate.patch && scp -q $PS $M:$J/candidate2.patch || exit 1
[ "$(shasum -a 256 $PS | cut -c1-64)" = e3d6c3db8b85779ac8d7bdeaf01a670244ceff1a903f678d8b8cb05a4f858380 ] || { echo "SEFIX-ALL sha mismatch"; exit 1; }
ssh $M bash -s -- "$J" <<'Z' || { echo "FAIL patch"; exit 1; }
set -e; cd $1/tree; patch -p1 -s < ../candidate.patch; patch -p1 -s < ../candidate2.patch; find . -name '*.orig' -delete
for k in RS_MERGE RS_SE_LEAD RS_SE_MAXDF RS_HEALTH_NOSOURCE_FALLBACK RS_KEEP_NOPROPER; do echo "$k files=$(grep -rl $k src | wc -l)"; done; cat ../env
Z
ssh -T -n $M "nohup bash $MK/lp-screens-mini_gen.sh $J > $J/nohup.log 2>&1 < /dev/null &" || exit 1
echo "$(date +%T) started $RUN on mini ($n items, job $J)"
[ "${NOWAIT:-0}" = 1 ] && exit 0
f=0; while :; do sleep 30; s=$(ssh -T -n -o ConnectTimeout=20 $M "tail -1 $J/STATUS" 2>/dev/null) || { f=$((f+1)); [ $f -ge 20 ] && { echo "FAIL unreachable"; exit 1; }; continue; }
  f=0; case $s in DONE) break;; FAIL*) echo "mini $s"; ssh -T -n $M "cat $J/STATUS; tail -20 $J/run.log"; scp -q $M:$J/STATUS $ST; exit 1;; esac; done
scp -q $M:$J/traces.jsonl $TR && scp -q $M:$J/STATUS $ST && scp -q $M:$J/run.log $C/f3-safety/runs/$RUN.run.log || exit 1
ssh -T -n $M "rm -rf $J/tree" || true
[ "$(wc -l < $TR | tr -d ' ')" = "$n" ] || { echo "FAIL rows"; exit 1; }
echo "$(date +%T) DONE $RUN rows=$n"
