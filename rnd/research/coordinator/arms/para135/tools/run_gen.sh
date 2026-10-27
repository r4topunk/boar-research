#!/bin/bash
# PARA135 generation on the mini (TOPICS27 recipe = topics27/tools/run_gen_succinct.sh): APFS clone of the K1 litepacks tree, no engine patch;
# the ONLY tree change is the adapter's Max Output Tokens 512 -> 1024 (= the app's maxTokens user setting 1024, the STYLE15B/style17-detailed Detailed cap),
# applied by sed in the clone. Persona = literal override in the request settings (personaSystemPrompt + personaStyleReminder, personas/paraN.json).
# Usage: run_gen.sh a|b N   (a = 27 Research Topics, kit wiki-vital5 via compose/packs-k13; b = CV5 51, K1 kit via compose/packs-k1)
set -u
S=$1; N=$2; D=<workspace>/rnd/research/coordinator/arms/para135; RUN=p135-$S-p$N-s42; REQ=$D/in/$RUN.requests.jsonl; OUT=$D/gen/$RUN
case $S in a) PD=packs-k13;; b) PD=packs-k1;; *) echo "set a|b"; exit 2;; esac
M=MINI_HOST; MK=<runner>/kiln; BASE=$MK/be-0cfd4a77-cut7-litepacks; J=$MK/lp-screens/jobs/$RUN
mkdir -p $OUT; scp -q $D/../topics27/tools/mini_gen_dump.sh $M:$MK/p135-mini_gen.sh || exit 1
ssh $M bash -s -- "$J" "$BASE" "$PD" <<'Y' || { echo "FAIL setup"; exit 1; }
set -e; J=$1; B=$2; PD=$3
[ "$(shasum -a 256 $B/src/routing/answer.ts | cut -c1-16)" = 0d1ac07dd1d664be ] && [ "$(shasum -a 256 $B/be/adapter-litedecline.ts | cut -c1-16)" = d53c14878ce4cbd3 ] && [ "$(cat $B/ARM)" = cut7-headpass-x2+litepacks ] || { echo "base tree mismatch"; exit 1; }
if [ -f $J/STATUS ] && ! grep -q -E '^(DONE|FAIL)' $J/STATUS; then echo "job running"; exit 1; fi
rm -rf $J; mkdir -p $J; cp -cR $B $J/tree; rm -rf $J/tree/be/.cache; echo "cut7-headpass-x2+litepacks+para135" > $J/tree/ARM
A=$J/tree/be/adapter-litedecline.ts
[ "$(grep -c 'styleReminder: persona.styleReminder, maxTokens: 512 };' $A)" = 1 ] || { echo "adapter line not found"; exit 1; }
sed -i '' 's/styleReminder: persona.styleReminder, maxTokens: 512 };/styleReminder: persona.styleReminder, maxTokens: 1024 }; \/\/ PARA135: Max Output Tokens 1024 (app setting)/' $A
grep -q 'maxTokens: 1024 }; // PARA135' $A || { echo "sed failed"; exit 1; }
printf 'BOAR_EVAL_PACK_DIRS=<runner>/kiln/compose/%s\n' $PD > $J/env
Y
scp -q $REQ $M:$J/requests.jsonl || exit 1
ssh -T -n $M "nohup bash $MK/p135-mini_gen.sh $J > $J/nohup.log 2>&1 < /dev/null &" || exit 1
echo "$(date +%T) started $RUN"
f=0; while :; do sleep 30; s=$(ssh -T -n -o ConnectTimeout=20 $M "tail -1 $J/STATUS" 2>/dev/null) || { f=$((f+1)); [ $f -ge 20 ] && { echo "FAIL unreachable"; exit 1; }; continue; }
  f=0; case $s in DONE) break;; FAIL*) echo "mini $s"; ssh -T -n $M "cat $J/STATUS; tail -20 $J/run.log"; exit 1;; esac; done
for f in traces.jsonl prompts.jsonl STATUS run.log; do scp -q $M:$J/$f $OUT/$f; done
ssh -T -n $M "rm -rf $J/tree"; echo "$(date +%T) DONE $RUN rows=$(wc -l < $OUT/traces.jsonl)"
