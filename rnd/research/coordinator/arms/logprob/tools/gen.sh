#!/bin/bash
# LOGPROB generation only (no judge): MAIN n 97 K0 on the Mac mini with the logprob-capture patch, via the LP-SCREENS mini job
# (tools/mini_gen.sh: slot lock gen1/gen2, one llama-server on an OS-assigned port started/stopped by the adapter, detector :8094 used).
# Same requests as the control lpctl-K0-main-s42 (mkreq.py, runId/config.arm replaced only). Copies traces + <traces>.logprobs.jsonl back.
set -u
A=<workspace>/rnd/research/coordinator/arms; H=$A/lp-screens; TL=$H/tools; D=$A/logprob
M=MINI_HOST; MK=<runner>/kiln; BASE=$MK/be-0cfd4a77-cut7-litepacks; RUN=logprob-K0-main-s42; J=$MK/lp-screens/jobs/$RUN
CFGARM=cut7-headpass-x2+litepacks+logprob; PF=$D/logprob.patch
mkdir -p $D/runs/req $D/runs/logs $D/traces
REQ=$D/runs/req/$RUN.requests.jsonl; python3 -I $TL/mkreq.py K0 $H/main-97.ids $RUN $CFGARM $REQ || exit 1
patch -p1 --dry-run -d <workspace>/kiln-local/be-0cfd4a77-cut7-litepacks < $PF > /dev/null || { echo "patch does not apply"; exit 2; }
INSHA=$( { cat $REQ; echo kind=patch; cat $PF; } | shasum -a 256 | cut -c1-16)
scp -q $TL/mini_gen.sh $M:$MK/lp-screens-mini_gen.sh || exit 1
ssh $M bash -s -- "$J" "$BASE" "$CFGARM" "$INSHA" <<'EOF' || exit 1
set -e; J=$1; B=$2; CA=$3; IS=$4
[ "$(shasum -a 256 $B/src/routing/answer.ts | cut -c1-16)" = 0d1ac07dd1d664be ] && [ "$(shasum -a 256 $B/be/adapter-litedecline.ts | cut -c1-16)" = d53c14878ce4cbd3 ] && [ "$(cat $B/ARM)" = cut7-headpass-x2+litepacks ] || { echo "base tree mismatch"; exit 1; }
if [ -f $J/STATUS ] && ! grep -q -E '^(DONE|FAIL)' $J/STATUS; then echo "job $J still running"; exit 1; fi
rm -rf $J; mkdir -p $J; cp -cR $B $J/tree; rm -rf $J/tree/be/.cache; echo "$CA" > $J/tree/ARM; echo $IS > $J/INPUTS
EOF
scp -q $REQ $M:$J/requests.jsonl && scp -q $PF $M:$J/candidate.patch && ssh -T -n $M "cd $J/tree && patch -p1 -s < ../candidate.patch && find . -name '*.orig' -delete" || exit 1
ssh -T -n $M "nohup bash $MK/lp-screens-mini_gen.sh $J > $J/nohup.log 2>&1 < /dev/null &" || exit 1
echo "$(date +%T) started $RUN inputs $INSHA"
while :; do sleep 30; s=$(ssh -T -n -o ConnectTimeout=20 $M "tail -1 $J/STATUS" 2>/dev/null) || continue
  case $s in DONE) break;; FAIL*) echo "mini $s"; ssh -T -n $M "cat $J/STATUS; tail -20 $J/run.log"; exit 1;; esac; done
TR=$D/traces/$RUN.traces.jsonl
scp -q $M:$J/traces.jsonl $TR && scp -q $M:$J/traces.logprobs.jsonl $D/traces/$RUN.logprobs.jsonl && scp -q $M:$J/STATUS $D/runs/logs/$RUN.status.mini || exit 1
echo "llama-servers on the mini after the job (detector :8094 + other arms' jobs expected):"; ssh -T -n $M "pgrep -fl llama-server | cut -c1-160" || true
ssh -T -n $M "rm -rf $J/tree"
{ echo "inputs $INSHA kind=patch patch=$(shasum -a 256 $PF | cut -c1-16) host=mini job=$J"; cat $D/runs/logs/$RUN.status.mini; } > $D/runs/logs/$RUN.status
echo "$(date +%T) DONE rows $(wc -l < $TR) logprob rows $(wc -l < $D/traces/$RUN.logprobs.jsonl)"
