#!/bin/bash
# RU step 1 (0 judge calls): regenerate the LITEPACKS K3 system on the mini with --dump-prompts for MAIN 97 + 80 candidate-pack self-tests
# (requests = tools/mkreq.py), to recover the exact context the 1.7B saw. Base tree <runner>/kiln/be-0cfd4a77-cut7-litepacks (sha-checked, as gate17/tools/gen_dump.sh);
# mini job tools/mini_gen_dump.sh (slot lock gen1/gen2, detector :8094 used never started, disk >= 25 GiB, own llama-server on an OS-assigned port).
set -u
D=<workspace>/rnd/research/coordinator/arms/refuse-unsupported
M=MINI_HOST; MK=<runner>/kiln; BASE=$MK/be-0cfd4a77-cut7-litepacks; RUN=ru-K3-dump-s42; J=$MK/lp-screens/jobs/$RUN
REQ=$D/runs/req/$RUN.requests.jsonl
INSHA=$( { cat $REQ; echo kind=dump-prompts; } | shasum -a 256 | cut -c1-16)
scp -q $D/tools/mini_gen_dump.sh $M:$MK/ru-mini_gen_dump.sh || exit 1
ssh $M bash -s -- "$J" "$BASE" "$INSHA" <<'EOS' || exit 1
set -e; J=$1; B=$2; IS=$3
[ "$(shasum -a 256 $B/src/routing/answer.ts | cut -c1-16)" = 0d1ac07dd1d664be ] && [ "$(shasum -a 256 $B/be/adapter-litedecline.ts | cut -c1-16)" = d53c14878ce4cbd3 ] && [ "$(cat $B/ARM)" = cut7-headpass-x2+litepacks ] || { echo "base tree mismatch"; exit 1; }
if [ -f $J/STATUS ] && ! grep -q -E '^(DONE|FAIL)' $J/STATUS; then echo "job $J still running"; exit 1; fi
rm -rf $J; mkdir -p $J; cp -cR $B $J/tree; rm -rf $J/tree/be/.cache; echo $IS > $J/INPUTS
EOS
scp -q $REQ $M:$J/requests.jsonl || exit 1
ssh -T -n $M "nohup bash $MK/ru-mini_gen_dump.sh $J > $J/nohup.log 2>&1 < /dev/null &" || exit 1
echo "$(date +%T) started $RUN inputs $INSHA"
while :; do sleep 30; s=$(ssh -T -n -o ConnectTimeout=20 $M "tail -1 $J/STATUS" 2>/dev/null) || continue
  case $s in DONE) break;; FAIL*) echo "mini $s"; ssh -T -n $M "cat $J/STATUS; tail -20 $J/run.log"; exit 1;; esac; done
scp -q $M:$J/traces.jsonl $D/traces/$RUN.traces.jsonl && scp -q $M:$J/prompts.jsonl $D/traces/$RUN.prompts.jsonl && scp -q $M:$J/STATUS $D/runs/logs/$RUN.status.mini || exit 1
ssh -T -n $M "rm -rf $J/tree"
{ echo "inputs $INSHA kind=dump-prompts host=mini job=$J"; cat $D/runs/logs/$RUN.status.mini; } > $D/runs/logs/$RUN.status
echo "$(date +%T) DONE rows $(wc -l < $D/traces/$RUN.traces.jsonl) prompt rows $(wc -l < $D/traces/$RUN.prompts.jsonl)"
