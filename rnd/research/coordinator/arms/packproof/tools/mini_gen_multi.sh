#!/bin/bash
# PACKPROOF copy of uxmatrix/tools/mini_gen_multi.sh (unchanged logic): runs EVERY request file in <job>/req/*.jsonl
# inside ONE generation slot (kiln slot lock gen1|gen2, 2-slot guard, disk >= 25 GiB, detector :8094 used, never started/stopped). Out: <job>/out/<group>/{traces,prompts}.jsonl, STATUS.
set -u
J=$1; K=<runner>/kiln; T=$J/tree; S=$J/STATUS; SL=$K/slots
export PATH=/opt/homebrew/bin:$PATH
MD=$HOME/boar/shared-models/emergency-detector; SRV=$HOME/boar/spikes/llama-b11010/build-cpu/bin/llama-server; DATA=$HOME/boar/shared-data
echo "queued $(date +%s) $(date '+%F %T') host=$(hostname -s)" > $S
mkdir -p $SL; SLOT=""
while [ -z "$SLOT" ]; do
  for s in gen1 gen2; do
    if [ -d $SL/$s ] && [ -f $SL/$s.owner ]; then op=$(awk '{print $1}' $SL/$s.owner); kill -0 "$op" 2>/dev/null || { rm -f $SL/$s.owner; rmdir $SL/$s 2>/dev/null && echo "reclaimed stale $s (pid $op)" >> $S; }; fi
    if mkdir $SL/$s 2>/dev/null; then SLOT=$s; echo "$$ $(date '+%F %T') $J" > $SL/$s.owner; break; fi
  done
  [ -z "$SLOT" ] && sleep 20
done
trap 'rm -f $SL/$SLOT.owner; rmdir $SL/$SLOT 2>/dev/null' EXIT
echo "slot $SLOT $(date '+%F %T')" >> $S
fail() { echo "FAIL $*" >> $S; exit 1; }
cd $T || fail "no tree"
export BOAR_EVAL_PACK_DIRS=$DATA/packs/v3proto:$DATA/packs/wave3:$DATA/packs/wave2:$DATA/packs/wave1:$DATA/packs:$DATA/crypto
export BOAR_SHARED_MODELS=$HOME/boar/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 \
  BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal
export BOAR_SERVER_EXTRA_ARGS="--reasoning off" LITEDECLINE_OFF=5
if [ -s $J/env ]; then set -a; . $J/env; set +a; echo "env overrides: $(grep -v '^#' $J/env | grep = | cut -d= -f1 | tr '\n' ' ')" >> $S; fi
for R in $J/req/*.jsonl; do g=$(basename $R .requests.jsonl); O=$J/out/$g; mkdir -p $O
  [ -f $O/DONE ] && continue
  while [ "$(pgrep -f 'bin/llama-server -m' | while read p; do ps -o command= -p $p; done | grep -vc -- '--port 8094')" -ge 2 ]; do sleep 20; done
  curl -sf http://127.0.0.1:8094/health > /dev/null || fail "detector :8094 down (not started here)"
  FREE=$(df -g ~ | awk 'NR==2{print $4}'); [ "$FREE" -ge 25 ] || fail "disk ${FREE} GiB < 25"
  echo "start $g $(date '+%F %T') free=${FREE}GiB answer.ts=$(shasum -a 256 src/routing/answer.ts | cut -c1-16)" >> $S
  be/node_modules/tsx/dist/cli.mjs be/adapter-litedecline.ts --requests $R --out $O/traces.jsonl --backend server --server-bin $SRV \
    --threads 4 --timeout-ms 600000 --dump-prompts $O/prompts.jsonl > $O/run.log 2>&1; rc=$?
  n=$(wc -l < $O/traces.jsonl 2>/dev/null | tr -d ' '); echo "end $g $(date '+%F %T') rc=$rc rows=$n" >> $S
  [ $rc = 0 ] && [ "$n" = "$(wc -l < $R | tr -d ' ')" ] && touch $O/DONE || fail "group $g rc=$rc"
done
echo DONE >> $S
