#!/bin/bash
# LP-SCREENS mini-side generation job (copied to the mini by run_arm.sh; runs there under nohup). Usage: mini_gen.sh <job dir>
# <job dir> holds: tree/ (APFS clone of <runner>/kiln/be-0cfd4a77-cut7-litepacks + the candidate patch), requests.jsonl, optional env (KEY=VALUE lines).
# System = LITEPACKS (arms/litepacks/LITEPACKS-criterion.md): adapter be/adapter-litedecline.ts, LITEDECLINE_OFF=5, Qwen3-1.7B Q4_K_M, --reasoning off,
# seed 42 (requests), llama-server b11010 CPU -t 4 on an OS-assigned port (the adapter starts/stops it), detector :8094 used (never started/stopped here).
# Slot lock (r4to 2026-10-20: at most 2 generation jobs on the mini): atomic mkdir <runner>/kiln/slots/gen1|gen2 (empty dir), owner info in slots/genN.owner,
# rmdir on exit; a slot whose owner pid is dead is reclaimed. Guards: free disk >= 25 GiB, detector up, <= 2 non-detector llama-servers.
# FIX 2026-10-21 (DRIFT17 bug report): the 2-slot guard used pgrep -f llama-server, which also matched the node adapters (their cmdline carries --server-bin .../llama-server), so only one job ran at a time; it now matches the real server cmdline (bin/llama-server -m), as in arms/drift17/tools/d17_gen.sh.
# Writes <job dir>/traces.jsonl, STATUS (start/slot/end/DONE|FAIL), run.log.
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
while [ "$(pgrep -f 'bin/llama-server -m' | while read p; do ps -o command= -p $p; done | grep -vc -- '--port 8094')" -ge 2 ]; do sleep 20; done
curl -sf http://127.0.0.1:8094/health > /dev/null || fail "detector :8094 down (not started here)"
FREE=$(df -g ~ | awk 'NR==2{print $4}'); [ "$FREE" -ge 25 ] || fail "disk ${FREE} GiB < 25"
export BOAR_EVAL_PACK_DIRS=$DATA/packs/v3proto:$DATA/packs/wave3:$DATA/packs/wave2:$DATA/packs/wave1:$DATA/packs:$DATA/crypto
export BOAR_SHARED_MODELS=$HOME/boar/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 \
  BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal
export BOAR_SERVER_EXTRA_ARGS="--reasoning off" LITEDECLINE_OFF=5
if [ -s $J/env ]; then set -a; . $J/env; set +a; echo "env overrides: $(grep -v '^#' $J/env | grep = | cut -d= -f1 | tr '\n' ' ')" >> $S; fi
echo "start $(date +%s) $(date '+%F %T') free=${FREE}GiB answer.ts=$(shasum -a 256 src/routing/answer.ts | cut -c1-16) adapter=$(shasum -a 256 be/adapter-litedecline.ts | cut -c1-16) LITEDECLINE_OFF=$LITEDECLINE_OFF extra=${BOAR_SERVER_EXTRA_ARGS}" >> $S
be/node_modules/tsx/dist/cli.mjs be/adapter-litedecline.ts --requests $J/requests.jsonl --out $J/traces.jsonl --backend server --server-bin $SRV \
  --threads 4 --timeout-ms 600000 --dump-prompts $J/prompts.jsonl > $J/run.log 2>&1; rc=$?
echo "end $(date +%s) rc=$rc rows=$(wc -l < $J/traces.jsonl 2>/dev/null | tr -d ' ')" >> $S
curl -sf http://127.0.0.1:8094/health > /dev/null || echo "WARN detector down after run" >> $S
[ $rc = 0 ] && [ "$(wc -l < $J/traces.jsonl | tr -d ' ')" = "$(wc -l < $J/requests.jsonl | tr -d ' ')" ] && echo DONE >> $S || { echo "FAIL rc=$rc" >> $S; exit 1; }
