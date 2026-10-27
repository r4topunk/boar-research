#!/bin/bash
# ORACLE-REAL generation on the mini (as null-cal/tools/run_pool.sh step 3, patch AND env). Usage: run_oracle.sh start|status|fetch
# start: job <runner>/kiln/lp-screens/jobs/oracle-K3-v01gold-s42 = APFS clone of the base tree + oracle.vs-litepacks.patch, env BOAR_ORACLE_FILE=<job>/oracle.json,
#        detached nohup mini_gen.sh (slot lock gen1/gen2; queues behind running jobs). status: tail of STATUS. fetch: copy traces + STATUS when DONE.
set -u
OR=<workspace>/rnd/research/coordinator/arms/oracle-real; TL=$OR/../lp-screens/tools
M=MINI_HOST; MK=<runner>/kiln; BASE=$MK/be-0cfd4a77-cut7-litepacks; RUN=oracle-K3-v01gold-s42; J=$MK/lp-screens/jobs/$RUN
REQ=$OR/runs/req/$RUN.requests.jsonl; PF=$OR/oracle.vs-litepacks.patch; OF=$OR/tools/oracle-file.json; CA=cut7-headpass-x2+litepacks+oracle-real
INSHA=$( { cat $REQ; cat $PF; cat $OF; } | shasum -a 256 | cut -c1-16)
case ${1:-} in
start)
  patch -p1 --dry-run -d <workspace>/kiln-local/be-0cfd4a77-cut7-litepacks < $PF > /dev/null || { echo "FAIL patch does not apply"; exit 2; }
  scp -q $TL/mini_gen.sh $M:$MK/lp-screens-mini_gen.sh || exit 1
  ssh $M bash -s -- "$J" "$BASE" "$CA" "$INSHA" <<'EOS' || { echo "FAIL mini job setup"; exit 1; }
set -e; J=$1; B=$2; CA=$3; IS=$4
[ "$(shasum -a 256 $B/src/routing/answer.ts | cut -c1-16)" = 0d1ac07dd1d664be ] && [ "$(shasum -a 256 $B/be/adapter-litedecline.ts | cut -c1-16)" = d53c14878ce4cbd3 ] && [ "$(cat $B/ARM)" = cut7-headpass-x2+litepacks ] || { echo "base tree mismatch"; exit 1; }
if [ -f $J/STATUS ] && ! grep -q -E '^(DONE|FAIL)' $J/STATUS; then echo "job $J is still running/queued"; exit 1; fi
rm -rf $J; mkdir -p $J; cp -cR $B $J/tree; rm -rf $J/tree/be/.cache; echo "$CA" > $J/tree/ARM; echo $IS > $J/INPUTS
EOS
  scp -q $REQ $M:$J/requests.jsonl && scp -q $PF $M:$J/candidate.patch && scp -q $OF $M:$J/oracle.json || exit 1
  ssh -T -n $M "cd $J/tree && patch -p1 -s < ../candidate.patch && find . -name '*.orig' -delete && echo BOAR_ORACLE_FILE=$J/oracle.json > $J/env" || { echo "FAIL patch on mini"; exit 1; }
  ssh -T -n $M "nohup bash $MK/lp-screens-mini_gen.sh $J > $J/nohup.log 2>&1 < /dev/null &" || exit 1
  echo "$(date '+%F %T') started $RUN inputs $INSHA" | tee -a $OR/runs/logs/$RUN.status.local;;
status) ssh -T -n $M "cat $J/INPUTS; cat $J/STATUS; tail -2 $J/run.log 2>/dev/null";;
fetch)
  s=$(ssh -T -n $M "tail -1 $J/STATUS"); [ "$s" = DONE ] || { echo "not done: $s"; exit 3; }
  [ "$(ssh -T -n $M cat $J/INPUTS)" = $INSHA ] || { echo "FAIL inputs mismatch"; exit 1; }
  scp -q $M:$J/traces.jsonl $OR/traces/$RUN.traces.jsonl && scp -q $M:$J/STATUS $OR/runs/logs/$RUN.status.mini || exit 1
  [ "$(wc -l < $OR/traces/$RUN.traces.jsonl | tr -d ' ')" = "$(wc -l < $REQ | tr -d ' ')" ] || { echo "FAIL rows"; exit 1; }
  ssh -T -n $M "rm -rf $J/tree"; echo "fetched $(wc -l < $OR/traces/$RUN.traces.jsonl) rows";;
*) echo "usage: run_oracle.sh start|status|fetch"; exit 2;;
esac
