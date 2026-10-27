#!/bin/bash
# DEEPMODE generation on the mini (PARA135 run_gen.sh recipe = TOPICS27 recipe): APFS clone of the K1 litepacks tree, no engine patch;
# the ONLY tree change is the adapter Max Output Tokens 512 -> 2048 (= the native app Deep Research auto cap AUTO_MAX_TOKENS_RESEARCH), by sed in the clone.
# Deep mode = request settings alwaysComplete true + personalityId detailed (tools/mk_req.py).
# Usage: run_gen.sh a|b   (a = 27 Research Topics, kit wiki-vital5 via compose/packs-k13; b = CV5 51, K1 kit via compose/packs-k1)
set -u
S=$1; D=<workspace>/rnd/research/coordinator/arms/deepmode; RUN=dm-$S-deep-s42; REQ=$D/in/$RUN.requests.jsonl; OUT=$D/gen/$RUN
case $S in a) PD=packs-k13;; b) PD=packs-k1;; *) echo "set a|b"; exit 2;; esac
M=MINI_HOST; MK=<runner>/kiln; BASE=$MK/be-0cfd4a77-cut7-litepacks; J=$MK/lp-screens/jobs/$RUN
mkdir -p $OUT; scp -q $D/../topics27/tools/mini_gen_dump.sh $M:$MK/dm-mini_gen.sh || exit 1
ssh $M bash -s -- "$J" "$BASE" "$PD" <<'Y' || { echo "FAIL setup"; exit 1; }
set -e; J=$1; B=$2; PD=$3
[ "$(shasum -a 256 $B/src/routing/answer.ts | cut -c1-16)" = 0d1ac07dd1d664be ] && [ "$(shasum -a 256 $B/be/adapter-litedecline.ts | cut -c1-16)" = d53c14878ce4cbd3 ] && [ "$(cat $B/ARM)" = cut7-headpass-x2+litepacks ] || { echo "base tree mismatch"; exit 1; }
if [ -f $J/STATUS ] && ! grep -q -E '^(DONE|FAIL)' $J/STATUS; then echo "job running"; exit 1; fi
rm -rf $J; mkdir -p $J; cp -cR $B $J/tree; rm -rf $J/tree/be/.cache; echo "cut7-headpass-x2+litepacks+deepmode" > $J/tree/ARM
A=$J/tree/be/adapter-litedecline.ts
[ "$(grep -c 'styleReminder: persona.styleReminder, maxTokens: 512 };' $A)" = 1 ] || { echo "adapter line not found"; exit 1; }
sed -i '' 's/styleReminder: persona.styleReminder, maxTokens: 512 };/styleReminder: persona.styleReminder, maxTokens: 2048 }; \/\/ DEEPMODE: Max Output Tokens 2048 (native research auto cap)/' $A
grep -q 'maxTokens: 2048 }; // DEEPMODE' $A || { echo "sed failed"; exit 1; }
printf 'BOAR_EVAL_PACK_DIRS=<runner>/kiln/compose/%s\n' $PD > $J/env
Y
scp -q $REQ $M:$J/requests.jsonl || exit 1
ssh -T -n $M "nohup bash $MK/dm-mini_gen.sh $J > $J/nohup.log 2>&1 < /dev/null &" || exit 1
echo "$(date +%T) started $RUN"
f=0; while :; do sleep 30; s=$(ssh -T -n -o ConnectTimeout=20 $M "tail -1 $J/STATUS" 2>/dev/null) || { f=$((f+1)); [ $f -ge 20 ] && { echo "FAIL unreachable"; exit 1; }; continue; }
  f=0; case $s in DONE) break;; FAIL*) echo "mini $s"; ssh -T -n $M "cat $J/STATUS; tail -20 $J/run.log"; exit 1;; esac; done
for f in traces.jsonl prompts.jsonl STATUS run.log; do scp -q $M:$J/$f $OUT/$f; done
ssh -T -n $M "rm -rf $J/tree"; echo "$(date +%T) DONE $RUN rows=$(wc -l < $OUT/traces.jsonl)"
