#!/bin/bash
# PACKSHAPE stage 2 on the mini: run_mini_eth.sh recipe (PACKPROOF), job pshape-on-s42; pack dirs = job packs/ (a COPY of the shaped
# boar-factbook.sqlite, scratch inside the job dir) then compose/packs-k13. Usage: run_mini.sh start | fetch
set -u
P=<workspace>/rnd/research/coordinator/arms/packproof; D=<workspace>/rnd/research/coordinator/arms/packshape; R=<workspace>/rnd/research/coordinator/arms
M=MINI_HOST; MK=<runner>/kiln; BASE=$MK/be-0cfd4a77-cut7-litepacks; J=$MK/lp-screens/jobs/pshape-on-s42; SH=<workspace>/kiln-local/shape-packs/shaped/boar-factbook.sqlite
if [ "$1" = fetch ]; then ssh -T -n $M "cat $J/STATUS"; for g in $(ssh -T -n $M "ls $J/out"); do [ "$(ssh -T -n $M "[ -f $J/out/$g/DONE ] && echo y")" = y ] || continue
  d=$D/gen/$g; mkdir -p $d; scp -q "$M:$J/out/$g/traces.jsonl" "$M:$J/out/$g/prompts.jsonl" "$M:$J/out/$g/run.log" $d/ && echo "DONE mini $(date '+%F %T')" > $d/STATUS && echo "fetched $g"; done; exit 0; fi
ssh $M bash -s -- "$J" "$BASE" <<'Y' || { echo "FAIL setup"; exit 1; }
set -e; J=$1; B=$2
[ "$(shasum -a 256 $B/src/routing/answer.ts | cut -c1-16)" = 0d1ac07dd1d664be ] && [ "$(shasum -a 256 $B/be/adapter-litedecline.ts | cut -c1-16)" = d53c14878ce4cbd3 ] && [ "$(cat $B/ARM)" = cut7-headpass-x2+litepacks ] || { echo "base tree mismatch"; exit 1; }
if [ -f $J/STATUS ] && ! grep -q -E '^(DONE|FAIL)' $J/STATUS; then echo "job running"; exit 1; fi
rm -rf $J; mkdir -p $J/req $J/packs; cp -cR $B $J/tree; rm -rf $J/tree/be/.cache; echo "cut7-headpass-x2+litepacks+sefix124+packproof+packshape" > $J/tree/ARM
printf "BOAR_EVAL_PACK_DIRS=$J/packs:<runner>/kiln/compose/packs-k13\nRS_MERGE=gidf\nRS_SE_LEAD=0.78\nRS_SE_MAXDF=0.25\nRS_KEEP_NOPROPER=1\n" > $J/env
Y
scp -q $SH $M:$J/packs/boar-factbook.sqlite && scp -q $R/retrieve-sweep/patches/H4-MERGE.patch $M:$J/candidate.patch && scp -q $R/retrieve-sweep/patches/SEFIX-ALL.patch $M:$J/candidate2.patch && scp -q "$D/in/on-k13s.requests.jsonl" $M:$J/req/ && scp -q $P/tools/mini_gen_multi.sh $M:$MK/pp-mini_gen_multi.sh || exit 1
ssh $M bash -s -- "$J" "$(shasum -a 256 $SH | cut -c1-64)" <<'Z' || { echo "FAIL patch"; exit 1; }
set -e; [ "$(shasum -a 256 $1/packs/boar-factbook.sqlite | cut -c1-64)" = "$2" ] || { echo "pack sha mismatch"; exit 1; }
cd $1/tree; patch -p1 -s < ../candidate.patch; patch -p1 -s < ../candidate2.patch; find . -name '*.orig' -delete
grep -q 'styleReminder: persona.styleReminder, maxTokens: 512 };' be/adapter-litedecline.ts
for k in RS_MERGE RS_SE_LEAD RS_SE_MAXDF RS_KEEP_NOPROPER; do echo "$k files=$(grep -rl $k src | wc -l)"; done; ls ../req
Z
ssh -T -n $M "nohup bash $MK/pp-mini_gen_multi.sh $J > $J/nohup.log 2>&1 < /dev/null &" && echo "$(date +%T) started pshape-on-s42"
