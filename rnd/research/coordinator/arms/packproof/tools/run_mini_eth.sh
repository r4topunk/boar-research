#!/bin/bash
# PACKPROOF ON group on-k13+qa-ethereum-se on the mini (rerun after the 14:10 session restart killed the MacBook run at 6/20; MacBook scratch tree lost): same recipe as run_mini_off.sh, pack dirs = job packs/ (link to v3proto qa-ethereum-se c58d44eb) then compose/packs-k13.
# SEFIX-124 env, pack dir compose/packs-k13 (OFF kits are K13 subsets), Succinct maxTokens 512 (tree unchanged), ARM +packproof; groups: 00-ident5 (host identity) then the 8 OFF groups.
# mini_gen_multi.sh under nohup (kiln slot lock). Usage: run_mini_off.sh start | fetch
set -u
P=<workspace>/rnd/research/coordinator/arms/packproof; R=<workspace>/rnd/research/coordinator/arms
M=MINI_HOST; MK=<runner>/kiln; BASE=$MK/be-0cfd4a77-cut7-litepacks; J=$MK/lp-screens/jobs/pp-on-eth-s42
if [ "$1" = fetch ]; then ssh -T -n $M "cat $J/STATUS"; for g in $(ssh -T -n $M "ls $J/out"); do [ "$(ssh -T -n $M "[ -f $J/out/$g/DONE ] && echo y")" = y ] || continue
  d=$P/gen/$g; [ $g = 00-ident5 ] && d=$P/gen/ident5-mini; mkdir -p $d; scp -q "$M:$J/out/$g/traces.jsonl" "$M:$J/out/$g/prompts.jsonl" "$M:$J/out/$g/run.log" $d/ && echo "DONE mini $(date '+%F %T')" > $d/STATUS && echo "fetched $g"; done; exit 0; fi
ssh $M bash -s -- "$J" "$BASE" <<'Y' || { echo "FAIL setup"; exit 1; }
set -e; J=$1; B=$2
[ "$(shasum -a 256 $B/src/routing/answer.ts | cut -c1-16)" = 0d1ac07dd1d664be ] && [ "$(shasum -a 256 $B/be/adapter-litedecline.ts | cut -c1-16)" = d53c14878ce4cbd3 ] && [ "$(cat $B/ARM)" = cut7-headpass-x2+litepacks ] || { echo "base tree mismatch"; exit 1; }
if [ -f $J/STATUS ] && ! grep -q -E '^(DONE|FAIL)' $J/STATUS; then echo "job running"; exit 1; fi
rm -rf $J; mkdir -p $J/req; cp -cR $B $J/tree; rm -rf $J/tree/be/.cache; echo "cut7-headpass-x2+litepacks+sefix124+packproof" > $J/tree/ARM
mkdir -p $J/packs; ln -s <runner>/shared-data/packs/v3proto/qa-ethereum-se.sqlite $J/packs/; ls $J/packs | wc -l; printf "BOAR_EVAL_PACK_DIRS=$J/packs:<runner>/kiln/compose/packs-k13\nRS_MERGE=gidf\nRS_SE_LEAD=0.78\nRS_SE_MAXDF=0.25\nRS_KEEP_NOPROPER=1\n" > $J/env
Y
scp -q $R/retrieve-sweep/patches/H4-MERGE.patch $M:$J/candidate.patch && scp -q $R/retrieve-sweep/patches/SEFIX-ALL.patch $M:$J/candidate2.patch && scp -q "$P/in/on-k13+qa-ethereum-se.requests.jsonl" $M:$J/req/ && scp -q $P/tools/mini_gen_multi.sh $M:$MK/pp-mini_gen_multi.sh || exit 1
ssh $M bash -s -- "$J" <<'Z' || { echo "FAIL patch"; exit 1; }
set -e; cd $1/tree; patch -p1 -s < ../candidate.patch; patch -p1 -s < ../candidate2.patch; find . -name '*.orig' -delete
grep -q 'styleReminder: persona.styleReminder, maxTokens: 512 };' be/adapter-litedecline.ts
for k in RS_MERGE RS_SE_LEAD RS_SE_MAXDF RS_KEEP_NOPROPER; do echo "$k files=$(grep -rl $k src | wc -l)"; done; ls ../req
Z
ssh -T -n $M "nohup bash $MK/pp-mini_gen_multi.sh $J > $J/nohup.log 2>&1 < /dev/null &" && echo "$(date +%T) started pp-off-s42"
