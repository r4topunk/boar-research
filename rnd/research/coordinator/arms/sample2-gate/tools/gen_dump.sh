#!/bin/bash
# SAMPLE2-GATE step 1 (0 judge calls): seed-43 sample of the LITEPACKS K0 system on stage1-pool.ids, on the mini, with --dump-prompts
# (null-cal/null-s43.patch applied: be/server.ts sends seed 43). Requests = null-cal/tools/mkreq_pool.py (byte-identical LITEPACKS rows).
# Mini job = refuse-unsupported/tools/mini_gen_dump.sh unchanged (slot lock gen1/gen2, disk >= 25 GiB, detector :8094 used never started).
set -u
D=<workspace>/rnd/research/coordinator/arms/sample2-gate; A=<workspace>/rnd/research/coordinator/arms
M=MINI_HOST; MK=<runner>/kiln; BASE=$MK/be-0cfd4a77-cut7-litepacks; RUN=s2g-K0-stage1-pool-s43dump; J=$MK/lp-screens/jobs/$RUN
IDS=$A/../ruler/ids/stage1-pool.ids; PF=$A/null-cal/null-s43.patch
REQ=$D/runs/req/$RUN.requests.jsonl; python3 -I $A/null-cal/tools/mkreq_pool.py K0 $IDS $RUN cut7-headpass-x2+litepacks+sample2-gate-s43 $REQ || exit 1
patch -p1 --dry-run -d <workspace>/kiln-local/be-0cfd4a77-cut7-litepacks < $PF > /dev/null || { echo "patch does not apply"; exit 2; }
INSHA=$( { cat $REQ; echo kind=dump-prompts+patch; cat $PF; } | shasum -a 256 | cut -c1-16)
scp -q $A/refuse-unsupported/tools/mini_gen_dump.sh $M:$MK/s2g-mini_gen_dump.sh || exit 1
ssh $M bash -s -- "$J" "$BASE" "$INSHA" <<'EOS' || exit 1
set -e; J=$1; B=$2; IS=$3
[ "$(shasum -a 256 $B/src/routing/answer.ts | cut -c1-16)" = 0d1ac07dd1d664be ] && [ "$(shasum -a 256 $B/be/adapter-litedecline.ts | cut -c1-16)" = d53c14878ce4cbd3 ] && [ "$(cat $B/ARM)" = cut7-headpass-x2+litepacks ] || { echo "base tree mismatch"; exit 1; }
if [ -f $J/STATUS ] && ! grep -q -E '^(DONE|FAIL)' $J/STATUS; then echo "job $J still running"; exit 1; fi
rm -rf $J; mkdir -p $J; cp -cR $B $J/tree; rm -rf $J/tree/be/.cache; echo cut7-headpass-x2+litepacks+sample2-gate-s43 > $J/tree/ARM; echo $IS > $J/INPUTS
EOS
scp -q $REQ $M:$J/requests.jsonl && scp -q $PF $M:$J/candidate.patch && ssh -T -n $M "cd $J/tree && patch -p1 -s < ../candidate.patch && find . -name '*.orig' -delete" || exit 1
ssh -T -n $M "nohup bash $MK/s2g-mini_gen_dump.sh $J > $J/nohup.log 2>&1 < /dev/null &" || exit 1
echo "$(date +%T) started $RUN inputs $INSHA"
while :; do sleep 30; s=$(ssh -T -n -o ConnectTimeout=20 $M "tail -1 $J/STATUS" 2>/dev/null) || continue
  case $s in DONE) break;; FAIL*) echo "mini $s"; ssh -T -n $M "cat $J/STATUS; tail -20 $J/run.log"; exit 1;; esac; done
scp -q $M:$J/traces.jsonl $D/traces/$RUN.traces.jsonl && scp -q $M:$J/prompts.jsonl $D/traces/$RUN.prompts.jsonl && scp -q $M:$J/STATUS $D/runs/logs/$RUN.status.mini || exit 1
ssh -T -n $M "rm -rf $J/tree"
{ echo "inputs $INSHA kind=dump-prompts+patch patch=$(shasum -a 256 $PF | cut -c1-16) host=mini job=$J"; cat $D/runs/logs/$RUN.status.mini; } > $D/runs/logs/$RUN.status
echo "$(date +%T) DONE rows $(wc -l < $D/traces/$RUN.traces.jsonl) prompt rows $(wc -l < $D/traces/$RUN.prompts.jsonl)"
