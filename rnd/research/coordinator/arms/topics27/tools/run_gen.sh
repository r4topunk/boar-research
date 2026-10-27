#!/bin/bash
# TOPICS27 generation on the mini: APFS clone of the K1 litepacks tree (no patch), wiki-vital5 from compose/packs-k13 (sha pinned in the request), mini_gen.sh + --dump-prompts.
set -u
D=<workspace>/rnd/research/coordinator/arms/topics27; REQ=$D/in/t27-detailed-s42.requests.jsonl; RUN=t27-detailed-s42
M=MINI_HOST; MK=<runner>/kiln; BASE=$MK/be-0cfd4a77-cut7-litepacks; J=$MK/lp-screens/jobs/$RUN
scp -q $D/tools/mini_gen_dump.sh $M:$MK/t27-mini_gen.sh || exit 1
ssh $M bash -s -- "$J" "$BASE" <<'Y' || { echo "FAIL setup"; exit 1; }
set -e; J=$1; B=$2
[ "$(shasum -a 256 $B/src/routing/answer.ts | cut -c1-16)" = 0d1ac07dd1d664be ] && [ "$(shasum -a 256 $B/be/adapter-litedecline.ts | cut -c1-16)" = d53c14878ce4cbd3 ] && [ "$(cat $B/ARM)" = cut7-headpass-x2+litepacks ] || { echo "base tree mismatch"; exit 1; }
rm -rf $J; mkdir -p $J; cp -cR $B $J/tree; rm -rf $J/tree/be/.cache; echo "cut7-headpass-x2+litepacks+topics27" > $J/tree/ARM
printf 'BOAR_EVAL_PACK_DIRS=<runner>/kiln/compose/packs-k13\n' > $J/env
Y
scp -q $REQ $M:$J/requests.jsonl || exit 1
ssh -T -n $M "nohup bash $MK/t27-mini_gen.sh $J > $J/nohup.log 2>&1 < /dev/null &" || exit 1
echo "$(date +%T) started $RUN"
while :; do sleep 30; s=$(ssh -T -n -o ConnectTimeout=20 $M "tail -1 $J/STATUS" 2>/dev/null) || continue
  case $s in DONE) break;; FAIL*) echo "mini $s"; ssh -T -n $M "cat $J/STATUS; tail -20 $J/run.log"; exit 1;; esac; done
for f in traces.jsonl prompts.jsonl STATUS run.log; do scp -q $M:$J/$f $D/gen/$f; done
ssh -T -n $M "rm -rf $J/tree"; echo "$(date +%T) DONE rows=$(wc -l < $D/gen/traces.jsonl)"
