#!/bin/bash
# ENGINE-RC on ruler v0.4 (R3), runs ON THE MINI (detached via nohup). Same recipe as validation-1024 night/tools/mini_queue.sh run_group:
# tree = val1024/trees/rs-RC (APFS clone), env = val1024/env/rc.env, kit = val1024/packs-rc, adapter be/adapter-litedecline.ts, --threads 4,
# LITEDECLINE_OFF=5, --reasoning off, detector mmBERT v3b. Deviation: :8094 is down after a mini reboot and is never started here; this script runs
# the identical detector command on port 8095 (own instance, stopped at the end) and points BOAR_DETECTOR_URL there.
# Turns: t1 (75 items) -> v04_stage.py builds t2 / t3 from the earlier traces (history as ChatScreen sends it). kiln slot gen1|gen2 held for the job.
# usage (mini): bash engine_v04_mini.sh <seed> [<seed> ...]     dir <runner>/kiln/native-rc/v04e/s<seed>/{turn1.requests.jsonl,turns.template.jsonl}
set -u
export PATH=/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin
NR=$HOME/boar/kiln/native-rc; MR=$HOME/boar/kiln/val1024; SL=$HOME/boar/kiln/slots; LOG=$NR/v04e/RUN.log
SRV=$HOME/boar/spikes/llama-b11010/build-cpu/bin/llama-server; MD=$HOME/boar/shared-models/emergency-detector
log() { echo "$(date '+%F %T') $*" >> $LOG; }
free_gib() { df -g $HOME | awk 'NR==2{print $4}'; }
mkdir -p $SL; SLOT=""
while [ -z "$SLOT" ]; do for s in gen1 gen2; do
  if [ -d $SL/$s ] && [ -f $SL/$s.owner ]; then op=$(awk '{print $1}' $SL/$s.owner); kill -0 "$op" 2>/dev/null || { rm -f $SL/$s.owner; rmdir $SL/$s 2>/dev/null; }; fi
  if mkdir $SL/$s 2>/dev/null; then SLOT=$s; echo "$$ $(date '+%F %T') native-rc/v04e" > $SL/$s.owner; break; fi; done; [ -z "$SLOT" ] && sleep 20; done
DETPID=""
if ! curl -sf http://127.0.0.1:8095/health >/dev/null; then
  (cd $MD && shasum -a 256 -c SHA256SUMS >/dev/null) || { log "FAIL detector sha"; exit 1; }
  nohup $SRV -m $MD/sonar-mmbert-small-emergency-v3b-q8te4.gguf --embeddings --pooling mean -np 1 -t 2 -c 512 -b 512 -ub 512 --host 127.0.0.1 --port 8095 > $NR/v04e/detector-8095.log 2>&1 < /dev/null &
  DETPID=$!; for i in $(seq 60); do curl -sf http://127.0.0.1:8095/health >/dev/null && break; sleep 1; done
fi
trap 'rm -f $SL/$SLOT.owner; rmdir $SL/$SLOT 2>/dev/null; [ -n "$DETPID" ] && kill $DETPID; log "exit"' EXIT
curl -sf http://127.0.0.1:8095/health >/dev/null || { log "FAIL detector 8095 down"; exit 1; }
T=$NR/v04e/tree; rm -rf $T; cp -cR $MR/trees/rs-RC $T; rm -rf $T/be/.cache; echo "ENGINE-RC+native-rc-v04" > $T/ARM
log "start slot=$SLOT tree answer.ts=$(shasum -a 256 $T/src/routing/answer.ts | cut -c1-16) adapter=$(shasum -a 256 $T/be/adapter-litedecline.ts | cut -c1-16) free=$(free_gib)GiB"
rows() { [ -f "$1" ] && wc -l < "$1" | tr -d ' ' || echo 0; }
run_group() { # <seed dir> <group>
  local D=$1 g=$2 R=$1/req/$2.requests.jsonl O=$1/out/$2
  [ -f $O/DONE ] && [ "$(rows $O/traces.jsonl)" = "$(rows $R)" ] && return 0
  [ "$(rows $R)" = 0 ] && { mkdir -p $O; : > $O/traces.jsonl; touch $O/DONE; return 0; }
  local F=$(free_gib); [ "$F" -ge 25 ] || { log "STOP disk ${F} GiB"; return 3; }
  rm -rf $O; mkdir -p $O; log "group $D $g n=$(rows $R) free=${F}GiB"
  ( cd $T && env -u RS_HEALTH_NOSOURCE_FALLBACK -u RS_STICKY -u RS_X2B_BUDGET -u RS_RB_K -u RS_RB_COMPRESS -u RS_RB_CAP -u RS_DENSE_IVF -u RS_DENSE_Q -u RS_DENSE_QN \
      -u RS_DENSE_IVFP -u RS_SE_LEAD_BIN -u RS_SE_LEAD_BIN_DIR -u RS_DENSE_Q_DIR bash -c '
      set -a; . "$1"; set +a
      export BOAR_SHARED_MODELS=$HOME/boar/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8095 \
        BOAR_DETECTOR_HEAD=$2/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal BOAR_SERVER_EXTRA_ARGS="--reasoning off" LITEDECLINE_OFF=5
      exec node be/node_modules/tsx/dist/cli.mjs be/adapter-litedecline.ts --requests "$3" --out "$4/traces.jsonl" --backend server --server-bin "$5" \
        --threads 4 --timeout-ms 600000 --dump-prompts "$4/prompts.jsonl"' _ "$MR/env/rc.env" "$MD" "$R" "$O" "$SRV" ) > $O/run.log 2>&1
  local rc=$? n=$(rows $O/traces.jsonl); log "end $g rc=$rc rows=$n"
  [ $rc = 0 ] && [ "$n" = "$(rows $R)" ] && { touch $O/DONE; return 0; }; return 1; }
for S in "$@"; do
  D=$NR/v04e/s$S; mkdir -p $D/req; cp $D/turn1.requests.jsonl $D/req/t1.requests.jsonl
  for K in 1 2 3; do
    [ $K -gt 1 ] && { python3 -I $NR/v04_stage.py $D $K >> $LOG 2>&1 || { log "FAIL stage $K"; exit 1; }; }
    run_group $D t$K; rc=$?; [ $rc = 1 ] && { log "retry t$K"; run_group $D t$K; rc=$?; }
    [ $rc = 0 ] || { log "FAIL s$S t$K rc=$rc"; exit 1; }
  done
  log "DONE s$S"
done
rm -rf $T; log "ALL-END"
