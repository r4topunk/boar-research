#!/bin/bash
# VALIDATION 2026-10-24 mini queue (ADDENDUM-1 section 4). Runs ENTIRELY on the mini, detached; never needs the MacBook after start.
# ADDENDUM-2 extension: mini_queue.sh start-ext (waits for queue.pid, then jobs-ext.json; job.json not_after "YYYY-MM-DD HH:MM" skips a late job).
# Start (from the MacBook, after sync_mini.sh):  <on the mini> 'bash <runner>/kiln/val1024/night/tools/mini_queue.sh start'
#   -> nohup caffeinate -i (no idle sleep) bash mini_queue.sh run, pid in $MR/queue.pid, progress in $MR/QUEUE.log, one STATUS per job in $MR/run/<job>/STATUS.
# Read:  <on the mini> 'tail -30 <runner>/kiln/val1024/QUEUE.log'      Stop: <on the mini> 'bash <runner>/kiln/val1024/night/tools/mini_queue.sh stop'
# Per job (order = night/jobs.json): skip if run/<job>/DONE; APFS clone of trees/<tree> (be/node_modules = the mini base tree's, set up by sync);
# kiln slot lock (slots/gen1|gen2 as lp-screens mini_gen_multi.sh, held for the whole job); per group: wait while >= 2 non-detector llama-servers run,
# detector :8094 must answer (never started/stopped here), disk >= 25 GiB else the QUEUE STOPS; a group is complete iff DONE and rows = requests
# (complete groups are skipped on a restart); a failed group is retried once, then the job is marked FAIL and the queue moves to the next job.
# V3 jobs: after group 00-turn1, v3_stage2.py builds 01-turn2 from the turn-1 traces (history as ChatScreen sends it), then it runs.
# Never touches Docker, ollama, :8094; never runs llama.cpp builds; deletes only its own tree clones.
set -u
export PATH=/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin
MR=$HOME/boar/kiln/val1024; K=$HOME/boar/kiln; SL=$K/slots; N=$MR/night; LOG=$MR/QUEUE.log
SRV=$HOME/boar/spikes/llama-b11010/build-cpu/bin/llama-server; MD=$HOME/boar/shared-models/emergency-detector
log() { echo "$(date '+%F %T') $*" >> $LOG; }
case "${1:-}" in
  start)
    if [ -f $MR/queue.pid ] && kill -0 "$(cat $MR/queue.pid)" 2>/dev/null; then echo "queue already running pid $(cat $MR/queue.pid)"; exit 1; fi
    nohup caffeinate -i bash $N/tools/mini_queue.sh run > $MR/queue.nohup 2>&1 < /dev/null &
    echo $! > $MR/queue.pid; sleep 1; echo "started pid $(cat $MR/queue.pid)"; exit 0;;
  stop)
    p=$(cat $MR/queue.pid 2>/dev/null); [ -n "$p" ] && pkill -P "$p" 2>/dev/null; [ -n "$p" ] && kill "$p" 2>/dev/null
    for q in $(pgrep -f "be/adapter-litedecline.ts --requests $MR/run/"); do for c in $(pgrep -P $q); do kill $c; done; kill $q; done  # adapter + its llama-server
    log "STOP requested"; echo stopped; exit 0;;
  status) tail -15 $LOG; for d in $MR/run/*/; do echo "$(basename $d): $(tail -1 $d/STATUS 2>/dev/null)"; done; exit 0;;
  start-ext)  # ADDENDUM-2: second detached invocation; waits for the main queue pid to exit, then runs night/jobs-ext.json's order
    if [ -f $MR/queue-ext.pid ] && kill -0 "$(cat $MR/queue-ext.pid)" 2>/dev/null; then echo "ext queue already running pid $(cat $MR/queue-ext.pid)"; exit 1; fi
    nohup caffeinate -i bash $N/tools/mini_queue.sh run-ext > $MR/queue-ext.nohup 2>&1 < /dev/null &
    echo $! > $MR/queue-ext.pid; sleep 1; echo "started ext pid $(cat $MR/queue-ext.pid) (waits for $(cat $MR/queue.pid 2>/dev/null))"; exit 0;;
  run-ext)
    W=$(cat $MR/queue.pid 2>/dev/null); log "QUEUE-EXT waiting for main queue pid ${W:-none}"
    while [ -n "$W" ] && kill -0 "$W" 2>/dev/null; do sleep 60; done
    JOBS=$(python3 -I -c 'import json,sys;print(" ".join(json.load(open(sys.argv[1]))["order"]))' $N/jobs-ext.json); export JOBS; log "QUEUE-EXT go: $JOBS";;
  run) ;;
  *) echo "usage: mini_queue.sh start|stop|status|run"; exit 2;;
esac
log "QUEUE start host=$(hostname -s) pid=$$ order=$(python3 -I -c 'import json,sys;print(",".join(json.load(open(sys.argv[1]))["order"]))' $N/jobs.json)"
free_gib() { df -g $HOME | awk 'NR==2{print $4}'; }
take_slot() {
  mkdir -p $SL; SLOT=""
  while [ -z "$SLOT" ]; do
    for s in gen1 gen2; do
      if [ -d $SL/$s ] && [ -f $SL/$s.owner ]; then op=$(awk '{print $1}' $SL/$s.owner); kill -0 "$op" 2>/dev/null || { rm -f $SL/$s.owner; rmdir $SL/$s 2>/dev/null && log "reclaimed stale slot $s (pid $op)"; }; fi
      if mkdir $SL/$s 2>/dev/null; then SLOT=$s; echo "$$ $(date '+%F %T') val1024/$1" > $SL/$s.owner; break; fi
    done
    [ -z "$SLOT" ] && sleep 20
  done; }
drop_slot() { [ -n "${SLOT:-}" ] && { rm -f $SL/$SLOT.owner; rmdir $SL/$SLOT 2>/dev/null; }; SLOT=""; }
trap 'drop_slot; log "QUEUE exit pid=$$"' EXIT
rows() { [ -f "$1" ] && wc -l < "$1" | tr -d ' ' || echo 0; }
run_group() { # <job dir> <group> -> rc 0 ok / 1 fail / 3 disk stop
  local J=$1 g=$2 R=$1/req/$2.requests.jsonl O=$1/out/$2
  [ -f $O/DONE ] && [ "$(rows $O/traces.jsonl)" = "$(rows $R)" ] && return 0
  while [ "$(pgrep -f 'bin/llama-server -m' | while read p; do ps -o command= -p $p; done | grep -vc -- '--port 8094')" -ge 2 ]; do sleep 20; done
  curl -sf http://127.0.0.1:8094/health > /dev/null || { echo "FAIL detector :8094 down (not started here) $g" >> $J/STATUS; return 1; }
  local F=$(free_gib); [ "$F" -ge 25 ] || { echo "STOP disk ${F} GiB < 25 at $g" >> $J/STATUS; return 3; }
  rm -rf $O; mkdir -p $O; echo "start $g $(date '+%F %T') free=${F}GiB n=$(rows $R)" >> $J/STATUS
  ( cd $J/tree && env -u RS_HEALTH_NOSOURCE_FALLBACK -u RS_STICKY -u RS_X2B_BUDGET -u RS_RB_K -u RS_RB_COMPRESS -u RS_RB_CAP -u RS_DENSE_IVF -u RS_DENSE_Q -u RS_DENSE_QN \
      -u RS_DENSE_IVFP -u RS_SE_LEAD_BIN -u RS_SE_LEAD_BIN_DIR -u RS_DENSE_Q_DIR bash -c '
      set -a; . "$1"; set +a
      export BOAR_SHARED_MODELS=$HOME/boar/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 \
        BOAR_DETECTOR_HEAD=$2/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal BOAR_SERVER_EXTRA_ARGS="--reasoning off" LITEDECLINE_OFF=5
      exec node be/node_modules/tsx/dist/cli.mjs be/adapter-litedecline.ts --requests "$3" --out "$4/traces.jsonl" --backend server --server-bin "$5" \
        --threads 4 --timeout-ms 600000 --dump-prompts "$4/prompts.jsonl"' _ "$J/env" "$MD" "$R" "$O" "$SRV" ) > $O/run.log 2>&1
  local rc=$? n=$(rows $O/traces.jsonl); echo "end $g $(date '+%F %T') rc=$rc rows=$n" >> $J/STATUS
  [ $rc = 0 ] && [ "$n" = "$(rows $R)" ] && { touch $O/DONE; return 0; }; return 1; }
# JOBS env (space-separated) overrides the order, for a smoke test. NOTE: never name a variable GROUPS (bash builtin array = the user's gids).
for JOB in ${JOBS:-$(python3 -I -c 'import json,sys;print(" ".join(json.load(open(sys.argv[1]))["order"]))' $N/jobs.json)}; do
  J=$MR/run/$JOB; S=$N/jobs/$JOB
  [ -f $J/DONE ] && { log "skip $JOB (DONE)"; continue; }
  NA=$(python3 -I -c 'import json,sys;print(json.load(open(sys.argv[1])).get("not_after") or "")' $S/job.json)
  [ -n "$NA" ] && [[ ! "$(date '+%Y-%m-%d %H:%M')" < "$NA" ]] && { log "skip $JOB (not_after $NA reached)"; continue; }
  mkdir -p $J/req $J/out; cp $S/job.json $J/; cp $S/req/*.requests.jsonl $J/req/; [ -f $S/turn2.template.jsonl ] && cp $S/turn2.template.jsonl $J/
  TREE=$(python3 -I -c 'import json,sys;print(json.load(open(sys.argv[1]))["tree"])' $J/job.json); ENVN=$(python3 -I -c 'import json,sys;print(json.load(open(sys.argv[1]))["env"])' $J/job.json)
  cp $MR/env/$ENVN.env $J/env || { log "FAIL $JOB no env $ENVN"; continue; }
  echo "queued $(date '+%F %T') tree=$TREE env=$ENVN" >> $J/STATUS; log "job $JOB start tree=$TREE env=$ENVN"
  take_slot $JOB; echo "slot $SLOT $(date '+%F %T')" >> $J/STATUS
  rm -rf $J/tree; cp -cR $MR/trees/$TREE $J/tree; rm -rf $J/tree/be/.cache
  # the adapter requires request config.arm == tree ARM (as every earlier recipe: ARM written per job clone); one arm per job (mk_jobs.py)
  cat $J/req/*.requests.jsonl $J/*.template.jsonl 2>/dev/null | python3 -I -c 'import json,sys;a={json.loads(l)["config"]["arm"] for l in sys.stdin if l.strip()};assert len(a)==1,a;print(a.pop())' > $J/tree/ARM || { log "FAIL $JOB arm"; continue; }
  echo "tree answer.ts=$(shasum -a 256 $J/tree/src/routing/answer.ts | cut -c1-16) adapter=$(shasum -a 256 $J/tree/be/adapter-litedecline.ts | cut -c1-16) ARM=$(cat $J/tree/ARM | cut -c1-60)" >> $J/STATUS
  ok=1; t0=$(date +%s)
  STG=$(python3 -I -c 'import json,sys;s=json.load(open(sys.argv[1])).get("stage2");print(s["group"] if s else "")' $J/job.json)
  GLIST=$(cd $J/req && ls *.requests.jsonl | sed 's/\.requests\.jsonl$//' | grep -vx "${STG:-NONE}" | sort)
  for g in $GLIST $STG; do
    [ "$g" = "$STG" ] && [ -n "$STG" ] && { python3 -I $N/tools/v3_stage2.py $J >> $J/STATUS 2>&1 || { ok=0; echo "FAIL stage2" >> $J/STATUS; break; }; }
    [ "$g" = "$STG" ] || [ -f $J/req/$g.requests.jsonl ] || continue
    run_group $J $g; rc=$?
    [ $rc = 1 ] && { log "$JOB $g failed once, retry"; run_group $J $g; rc=$?; }
    [ $rc = 3 ] && { log "QUEUE STOP: disk < 25 GiB during $JOB $g"; drop_slot; exit 3; }
    [ $rc = 0 ] || { ok=0; break; }
  done
  drop_slot; rm -rf $J/tree
  if [ $ok = 1 ]; then echo DONE >> $J/STATUS; touch $J/DONE; log "job $JOB DONE $(( $(date +%s) - t0 ))s rows=$(cat $J/out/*/traces.jsonl | wc -l | tr -d ' ') free=$(free_gib)GiB"
  else echo "FAIL" >> $J/STATUS; log "job $JOB FAIL (see $J/STATUS, out/*/run.log); next job"; fi
done
log "QUEUE ALL-END"
