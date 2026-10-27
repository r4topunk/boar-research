#!/bin/bash
# CB17 generation on the Mac mini (LP-SCREENS job layout, run_arm.sh step 3): APFS clone of the base tree + tools/cb17-noretrieval.patch,
# ARM = cut7-headpass-x2+litepacks+cb17, requests runs/req/cb17-main-s42.requests.jsonl (kit []), lp-screens/tools/mini_gen.sh (2-slot guard,
# disk >= 25 GiB, detector used never started). Usage: gen_cb17.sh [requests file] [run name]
set -u
H=<workspace>/rnd/research/coordinator/arms/cb17; LS=$H/../lp-screens/tools
REQ=${1:-$H/runs/req/cb17-main-s42.requests.jsonl}; RUN=${2:-cb17-main-s42}
M=MINI_HOST; MK=<runner>/kiln; BASE=$MK/be-0cfd4a77-cut7-litepacks; J=$MK/lp-screens/jobs/$RUN; PF=$H/tools/cb17-noretrieval.patch
TR=$H/traces/$RUN.traces.jsonl; ST=$H/runs/logs/$RUN.status; n=$(wc -l < $REQ | tr -d ' ')
[ "$(shasum -a 256 $H/CB17-criterion.md | cut -d' ' -f1)" = "$(cut -d' ' -f1 $H/CB17-criterion.sha256)" ] || { echo "criterion sha mismatch"; exit 9; }
scp -q $LS/mini_gen.sh $M:$MK/lp-screens-mini_gen.sh || exit 1
ssh $M bash -s -- "$J" "$BASE" <<'X' || { echo "FAIL setup"; exit 1; }
set -e; J=$1; B=$2
[ "$(shasum -a 256 $B/src/routing/answer.ts | cut -c1-16)" = 0d1ac07dd1d664be ] && [ "$(shasum -a 256 $B/be/adapter-litedecline.ts | cut -c1-16)" = d53c14878ce4cbd3 ] && [ "$(cat $B/ARM)" = cut7-headpass-x2+litepacks ] || { echo "base tree mismatch"; exit 1; }
if [ -f $J/STATUS ] && ! grep -q -E '^(DONE|FAIL)' $J/STATUS; then echo "job running"; exit 1; fi
rm -rf $J; mkdir -p $J; cp -cR $B $J/tree; rm -rf $J/tree/be/.cache; echo cut7-headpass-x2+litepacks+cb17 > $J/tree/ARM
X
scp -q $REQ $M:$J/requests.jsonl && scp -q $PF $M:$J/candidate.patch || exit 1
ssh -T -n $M "cd $J/tree && patch -p1 -s < ../candidate.patch && find . -name '*.orig' -delete && grep -c 'CB17 (closed-book' src/rag/retrieve.ts" || { echo "FAIL patch"; exit 1; }
ssh -T -n $M "nohup bash $MK/lp-screens-mini_gen.sh $J > $J/nohup.log 2>&1 < /dev/null &" || exit 1
echo "$(date +%T) started $RUN on mini ($n items)"
f=0; while :; do sleep 30; s=$(ssh -T -n -o ConnectTimeout=20 $M "tail -1 $J/STATUS" 2>/dev/null) || { f=$((f+1)); [ $f -ge 20 ] && { echo "FAIL unreachable"; exit 1; }; continue; }
  f=0; case $s in DONE) break;; FAIL*) echo "mini $s"; ssh -T -n $M "cat $J/STATUS; tail -20 $J/run.log"; exit 1;; esac; done
scp -q $M:$J/traces.jsonl $TR && scp -q $M:$J/STATUS $ST || exit 1
ssh -T -n $M "rm -rf $J/tree" || true
[ "$(wc -l < $TR | tr -d ' ')" = "$n" ] || { echo "FAIL rows"; exit 1; }
echo "$(date +%T) DONE $RUN rows=$n"
