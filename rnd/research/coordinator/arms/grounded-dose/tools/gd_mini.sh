#!/bin/bash
# GROUNDED-DOSE arms B and C generation (mini side, detached). Same recipe as lp-screens/tools/mini_gen.sh (adapter-litedecline, LITEDECLINE_OFF=5, --reasoning off,
# Qwen3-1.7B seed 42 via requests, llama-server b11010 CPU -t 4), but a PRIVATE detector on :8097 (:8094 is down; never touched), stopped at the end.
# usage: gd_mini.sh <GD root>   (GD/jobs/<arm>/{tree,requests.jsonl,env}; arms run in order B900 then Bk4c40)
set -u
export PATH=/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin
GD=$1; K=$HOME/boar/kiln; SL=$K/slots; LOG=$GD/RUN.log
SRV=$HOME/boar/spikes/llama-b11010/build-cpu/bin/llama-server; MD=$HOME/boar/shared-models/emergency-detector; PORT=8097
log() { echo "$(date '+%F %T') $*" >> $LOG; }
free_gib() { df -g $HOME | awk 'NR==2{print $4}'; }
mkdir -p $SL; SLOT=""
while [ -z "$SLOT" ]; do for s in gen1 gen2; do
  if [ -d $SL/$s ] && [ -f $SL/$s.owner ]; then op=$(awk '{print $1}' $SL/$s.owner); kill -0 "$op" 2>/dev/null || { rm -f $SL/$s.owner; rmdir $SL/$s 2>/dev/null; }; fi
  if mkdir $SL/$s 2>/dev/null; then SLOT=$s; echo "$$ $(date '+%F %T') grounded-dose" > $SL/$s.owner; break; fi; done; [ -z "$SLOT" ] && sleep 20; done
(cd $MD && shasum -a 256 -c SHA256SUMS >/dev/null) || { log "FAIL detector sha"; exit 1; }
nohup $SRV -m $MD/sonar-mmbert-small-emergency-v3b-q8te4.gguf --embeddings --pooling mean -np 1 -t 2 -c 512 -b 512 -ub 512 --host 127.0.0.1 --port $PORT > $GD/detector-$PORT.log 2>&1 < /dev/null &
DETPID=$!
trap 'rm -f $SL/$SLOT.owner; rmdir $SL/$SLOT 2>/dev/null; kill $DETPID 2>/dev/null; log "exit (detector $DETPID stopped)"' EXIT
for i in $(seq 60); do curl -sf http://127.0.0.1:$PORT/health >/dev/null && break; sleep 1; done
curl -sf http://127.0.0.1:$PORT/health >/dev/null || { log "FAIL detector $PORT down"; exit 1; }
for ARM in B900 Bk4c40; do
  J=$GD/jobs/$ARM; S=$J/STATUS; T=$J/tree
  F=$(free_gib); [ "$F" -ge 25 ] || { echo "FAIL disk ${F} GiB < 25" >> $S; log "STOP disk $F"; exit 3; }
  while [ "$(pgrep -f 'bin/llama-server -m' | while read p; do ps -o command= -p $p; done | grep -vc -- "--port $PORT")" -ge 2 ]; do sleep 20; done
  export BOAR_EVAL_PACK_DIRS=$K/compose/packs-k13
  export BOAR_SHARED_MODELS=$HOME/boar/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:$PORT \
    BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal BOAR_SERVER_EXTRA_ARGS="--reasoning off" LITEDECLINE_OFF=5
  env -u RS_HEALTH_NOSOURCE_FALLBACK -u RS_STICKY -u RS_X2B_BUDGET -u RS_RB_K -u RS_RB_COMPRESS true
  echo "start $ARM $(date '+%F %T') free=${F}GiB answer.ts=$(shasum -a 256 $T/src/routing/answer.ts | cut -c1-16) ARM=$(cat $T/ARM)" > $S; log "start $ARM"
  ( cd $T && env -u RS_HEALTH_NOSOURCE_FALLBACK -u RS_STICKY -u RS_X2B_BUDGET -u RS_RB_K -u RS_RB_COMPRESS bash -c '
      set -a; . "$1"; set +a; echo "env: $(grep = "$1" | tr "\n" " ")" >> "$2"
      exec node be/node_modules/tsx/dist/cli.mjs be/adapter-litedecline.ts --requests "$3" --out "$4/traces.jsonl" --backend server --server-bin "$5" \
        --threads 4 --timeout-ms 600000 --dump-prompts "$4/prompts.jsonl"' _ "$J/env" "$S" "$J/requests.jsonl" "$J" "$SRV" ) > $J/run.log 2>&1
  rc=$?; n=$(wc -l < $J/traces.jsonl 2>/dev/null | tr -d ' ')
  echo "end $(date '+%F %T') rc=$rc rows=$n" >> $S; log "end $ARM rc=$rc rows=$n"
  [ $rc = 0 ] && [ "$n" = "$(wc -l < $J/requests.jsonl | tr -d ' ')" ] && echo DONE >> $S || echo "FAIL" >> $S
done
log "ALL-END"
