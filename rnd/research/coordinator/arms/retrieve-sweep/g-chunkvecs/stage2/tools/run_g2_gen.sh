#!/bin/bash
# Arm G stage 2 generation on the Mac mini = arms/qform/gen/tools/run_qform_gen.sh with a per-run pack dir (BOAR_EVAL_PACK_DIRS in the job env):
# ctl -> <runner>/kiln/g2/packs-ctl (symlinks to shared-data/packs/persona-a-union/{boar-factbook,boar-firstaid-en,boar-medlineplus-en}.sqlite, v2),
# arm -> <runner>/kiln/g2/packs-arm (symlinks to shared-data/packs/v3proto/..., chunk_vecs). Base tree <runner>/kiln/be-0cfd4a77-cut7-litepacks (checked), no patch.
# Usage: run_g2_gen.sh ctl|arm        (NOWAIT=1 = start and exit)
set -u
W=$1; RUN=g2-$W
H=<workspace>/rnd/research/coordinator/arms/retrieve-sweep/g-chunkvecs/stage2; LS=<workspace>/rnd/research/coordinator/arms/lp-screens/tools
REQ=$H/req/$RUN.requests.jsonl
M=MINI_HOST; MK=<runner>/kiln; BASE=$MK/be-0cfd4a77-cut7-litepacks; J=$MK/lp-screens/jobs/$RUN
TR=$H/traces/$RUN.traces.jsonl; ST=$H/logs/$RUN.status; n=$(wc -l < $REQ | tr -d ' ')
CA=$(head -1 $REQ | python3 -I -c "import json,sys;print(json.loads(sys.stdin.readline())['config']['arm'])")
scp -q $LS/mini_gen.sh $M:$MK/lp-screens-mini_gen.sh || exit 1
ssh $M bash -s -- "$J" "$BASE" "$CA" "$W" <<'Y' || { echo "FAIL setup"; exit 1; }
set -e; J=$1; B=$2; CA=$3; W=$4
[ "$(shasum -a 256 $B/src/routing/answer.ts | cut -c1-16)" = 0d1ac07dd1d664be ] && [ "$(shasum -a 256 $B/be/adapter-litedecline.ts | cut -c1-16)" = d53c14878ce4cbd3 ] && [ "$(cat $B/ARM)" = cut7-headpass-x2+litepacks ] || { echo "base tree mismatch"; exit 1; }
if [ -f $J/STATUS ] && ! grep -q -E '^(DONE|FAIL)' $J/STATUS; then echo "job running"; exit 1; fi
rm -rf $J; mkdir -p $J; cp -cR $B $J/tree; rm -rf $J/tree/be/.cache; echo "$CA" > $J/tree/ARM
echo "BOAR_EVAL_PACK_DIRS=$HOME/boar/kiln/g2/packs-$W" > $J/env
Y
scp -q $REQ $M:$J/requests.jsonl || exit 1
ssh -T -n $M "nohup bash $MK/lp-screens-mini_gen.sh $J > $J/nohup.log 2>&1 < /dev/null &" || exit 1
echo "$(date +%T) started $RUN on mini ($n items, job $J)"
[ "${NOWAIT:-0}" = 1 ] && exit 0
f=0; while :; do sleep 30; s=$(ssh -T -n -o ConnectTimeout=20 $M "tail -1 $J/STATUS" 2>/dev/null) || { f=$((f+1)); [ $f -ge 20 ] && { echo "FAIL unreachable"; exit 1; }; continue; }
  f=0; case $s in DONE) break;; FAIL*) echo "mini $s"; ssh -T -n $M "cat $J/STATUS; tail -20 $J/run.log"; scp -q $M:$J/STATUS $ST; exit 1;; esac; done
scp -q $M:$J/traces.jsonl $TR && scp -q $M:$J/STATUS $ST && scp -q $M:$J/run.log $H/logs/$RUN.run.log || exit 1
ssh -T -n $M "rm -rf $J/tree" || true
[ "$(wc -l < $TR | tr -d ' ')" = "$n" ] || { echo "FAIL rows"; exit 1; }
echo "$(date +%T) DONE $RUN rows=$n"
