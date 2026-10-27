#!/bin/bash
# UXMATRIX arms on the mini (detailed: maxTokens 1024; deep: 2048): APFS clone of be-0cfd4a77-cut7-litepacks + H4-MERGE + SEFIX-ALL (as sefix/ans-tools/run_124_gen.sh), SEFIX-124 env,
# pack dir compose/packs-k13 (kit list per request selects the packs), adapter maxTokens per mode, ARM uxm-<mode>; mini_gen_multi.sh under nohup.
# Usage: run_mini.sh <mode> <job suffix> <request glob: on | off-*> start|fetch
# 12:37 coordinator scope cut: deep arms dropped (job killed, slot released); detailed moved here from the MacBook (mini free, M4 faster), two jobs (on / off-*) = one host.
set -u; MODE=$1; JS=$2; GL=$3; ACT=$4; case $MODE in detailed) MT=1024;; deep) MT=2048;; *) exit 2;; esac
U=<workspace>/rnd/research/coordinator/arms/uxmatrix; R=<workspace>/rnd/research/coordinator/arms
M=MINI_HOST; MK=<runner>/kiln; BASE=$MK/be-0cfd4a77-cut7-litepacks; J=$MK/lp-screens/jobs/uxm-$MODE-$JS-s42
if [ "$ACT" = fetch ]; then mkdir -p $U/gen/$MODE; ssh -T -n $M "cat $J/STATUS"; for g in $(ssh -T -n $M "ls $J/out"); do mkdir -p $U/gen/$MODE/$g; scp -q "$M:$J/out/$g/*" $U/gen/$MODE/$g/ 2>/dev/null; done; exit 0; fi
ssh $M bash -s -- "$J" "$BASE" "$MODE" <<'Y' || { echo "FAIL setup"; exit 1; }
set -e; J=$1; B=$2; MODE=$3
[ "$(shasum -a 256 $B/src/routing/answer.ts | cut -c1-16)" = 0d1ac07dd1d664be ] && [ "$(shasum -a 256 $B/be/adapter-litedecline.ts | cut -c1-16)" = d53c14878ce4cbd3 ] && [ "$(cat $B/ARM)" = cut7-headpass-x2+litepacks ] || { echo "base tree mismatch"; exit 1; }
if [ -f $J/STATUS ] && ! grep -q -E '^(DONE|FAIL)' $J/STATUS; then echo "job running"; exit 1; fi
rm -rf $J; mkdir -p $J/req; cp -cR $B $J/tree; rm -rf $J/tree/be/.cache; echo "cut7-headpass-x2+litepacks+sefix124+uxm-$MODE" > $J/tree/ARM
printf 'BOAR_EVAL_PACK_DIRS=<runner>/kiln/compose/packs-k13\nRS_MERGE=gidf\nRS_SE_LEAD=0.78\nRS_SE_MAXDF=0.25\nRS_KEEP_NOPROPER=1\n' > $J/env
Y
scp -q $R/retrieve-sweep/patches/H4-MERGE.patch $M:$J/candidate.patch && scp -q $R/retrieve-sweep/patches/SEFIX-ALL.patch $M:$J/candidate2.patch && scp -q $U/in/$MODE/$GL.requests.jsonl $M:$J/req/ && scp -q $U/tools/mini_gen_multi.sh $M:$MK/uxm-mini_gen_multi.sh || exit 1
ssh $M bash -s -- "$J" "$MT" <<'Z' || { echo "FAIL patch"; exit 1; }
set -e; cd $1/tree; patch -p1 -s < ../candidate.patch; patch -p1 -s < ../candidate2.patch; find . -name '*.orig' -delete
A=be/adapter-litedecline.ts; [ "$(grep -c 'styleReminder: persona.styleReminder, maxTokens: 512 };' $A)" = 1 ]
sed -i '' 's/styleReminder: persona.styleReminder, maxTokens: 512 };/styleReminder: persona.styleReminder, maxTokens: '$2' }; \/\/ UXMATRIX: Max Output Tokens '$2'/' $A; grep -q "maxTokens: $2 }; // UXMATRIX" $A
for k in RS_MERGE RS_SE_LEAD RS_SE_MAXDF RS_KEEP_NOPROPER; do echo "$k files=$(grep -rl $k src | wc -l)"; done; ls ../req | wc -l
Z
ssh -T -n $M "nohup bash $MK/uxm-mini_gen_multi.sh $J > $J/nohup.log 2>&1 < /dev/null &" && echo "$(date +%T) started $J"
