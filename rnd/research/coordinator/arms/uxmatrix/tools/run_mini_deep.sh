#!/bin/bash
# UXMATRIX Deep Research arms on the mini: APFS clone of be-0cfd4a77-cut7-litepacks + H4-MERGE + SEFIX-ALL (as sefix/ans-tools/run_124_gen.sh), SEFIX-124 env,
# pack dir compose/packs-k13 (kit list per request selects the packs), adapter maxTokens 2048 (DEEPMODE), ARM uxm-deep; mini_gen_multi.sh under nohup.
# Usage: run_mini_deep.sh start | fetch
set -u
U=<workspace>/rnd/research/coordinator/arms/uxmatrix; R=<workspace>/rnd/research/coordinator/arms
M=MINI_HOST; MK=<runner>/kiln; BASE=$MK/be-0cfd4a77-cut7-litepacks; J=$MK/lp-screens/jobs/uxm-deep-s42
if [ "$1" = fetch ]; then mkdir -p $U/gen/deep; ssh -T -n $M "cat $J/STATUS"; for g in $(ssh -T -n $M "ls $J/out"); do mkdir -p $U/gen/deep/$g; scp -q "$M:$J/out/$g/*" $U/gen/deep/$g/ 2>/dev/null; done; exit 0; fi
ssh $M bash -s -- "$J" "$BASE" <<'Y' || { echo "FAIL setup"; exit 1; }
set -e; J=$1; B=$2
[ "$(shasum -a 256 $B/src/routing/answer.ts | cut -c1-16)" = 0d1ac07dd1d664be ] && [ "$(shasum -a 256 $B/be/adapter-litedecline.ts | cut -c1-16)" = d53c14878ce4cbd3 ] && [ "$(cat $B/ARM)" = cut7-headpass-x2+litepacks ] || { echo "base tree mismatch"; exit 1; }
if [ -f $J/STATUS ] && ! grep -q -E '^(DONE|FAIL)' $J/STATUS; then echo "job running"; exit 1; fi
rm -rf $J; mkdir -p $J/req; cp -cR $B $J/tree; rm -rf $J/tree/be/.cache; echo "cut7-headpass-x2+litepacks+sefix124+uxm-deep" > $J/tree/ARM
printf 'BOAR_EVAL_PACK_DIRS=<runner>/kiln/compose/packs-k13\nRS_MERGE=gidf\nRS_SE_LEAD=0.78\nRS_SE_MAXDF=0.25\nRS_KEEP_NOPROPER=1\n' > $J/env
Y
scp -q $R/retrieve-sweep/patches/H4-MERGE.patch $M:$J/candidate.patch && scp -q $R/retrieve-sweep/patches/SEFIX-ALL.patch $M:$J/candidate2.patch && scp -q $U/in/deep/*.jsonl $M:$J/req/ && scp -q $U/tools/mini_gen_multi.sh $M:$MK/uxm-mini_gen_multi.sh || exit 1
ssh $M bash -s -- "$J" <<'Z' || { echo "FAIL patch"; exit 1; }
set -e; cd $1/tree; patch -p1 -s < ../candidate.patch; patch -p1 -s < ../candidate2.patch; find . -name '*.orig' -delete
A=be/adapter-litedecline.ts; [ "$(grep -c 'styleReminder: persona.styleReminder, maxTokens: 512 };' $A)" = 1 ]
sed -i '' 's/styleReminder: persona.styleReminder, maxTokens: 512 };/styleReminder: persona.styleReminder, maxTokens: 2048 }; \/\/ UXMATRIX deep: Max Output Tokens 2048/' $A; grep -q 'maxTokens: 2048 }; // UXMATRIX' $A
for k in RS_MERGE RS_SE_LEAD RS_SE_MAXDF RS_KEEP_NOPROPER; do echo "$k files=$(grep -rl $k src | wc -l)"; done; ls ../req | wc -l
Z
ssh -T -n $M "nohup bash $MK/uxm-mini_gen_multi.sh $J > $J/nohup.log 2>&1 < /dev/null &" && echo "$(date +%T) started uxm-deep-s42"
