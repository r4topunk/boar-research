#!/bin/bash
# Offline tests for tools/queue.sh (LOOP v2 T1): T-Q1..T-Q6. 0 LLM calls, mktemp dirs, never reads blind/.
# Run: bash rnd/research/coordinator/arms/_lib/tests/queue-tests.sh   (exit 0 = all pass, ~1 min)
set -u
TD=$(cd "$(dirname "$0")" && pwd); Q=$(cd "$TD/../../../tools" && pwd)/queue.sh
PASS=0; FAIL=0; ok() { if [ "$2" = 0 ]; then PASS=$((PASS+1)); echo "  [pass] $1"; else FAIL=$((FAIL+1)); echo "  [FAIL] $1"; fi; }
export QUEUE_WRAP= QUEUE_POLL_S=0.2
mk() { W=$(mktemp -d "${TMPDIR:-/tmp}/queuetest.XXXXXX"); export QUEUE_DIR=$W/q DISK_FLOOR_GIB=0; mkdir -p $QUEUE_DIR; }
step() { # step <name> <eta> <body> [extra header lines...]
  local n=$1 e=$2 b=$3; shift 3; { echo "# ETA_MIN=$e"; for h in "$@"; do echo "# $h"; done; echo "$b"; } > $QUEUE_DIR/$n.step; }
waitrun() { local i=0; while [ $i -lt ${1:-150} ]; do [ ! -f $QUEUE_DIR/runner.pid ] && return 0; sleep 0.1; i=$((i+1)); done; return 1; }
last() { tail -1 $QUEUE_DIR/$1.status 2>/dev/null | cut -d' ' -f1-2; }

echo "T-Q1 3-step stub queue survives kill -9 of the launching shell (also the mini selftest)"
bash $Q selftest 2>/dev/null; ok "T-Q1 selftest: 3 DONE, runner exited" $?

echo "T-Q2 failing step -> FAIL rc=1, dependent -> SKIP"
mk; step 001-a-x 1 "true"; step 002-a-y 1 "exit 1"; step 003-a-z 1 "echo never > $W/ran" "NEEDS=002-a-y"
bash $Q start >/dev/null; waitrun; r=0
[ "$(last 001-a-x | cut -d' ' -f1)" = DONE ] && grep -q '^FAIL rc=1 ' $QUEUE_DIR/002-a-y.status && grep -q '^SKIP ' $QUEUE_DIR/003-a-z.status && [ ! -e $W/ran ] || r=1
ok "T-Q2 DONE / FAIL rc=1 / SKIP ($(last 001-a-x | cut -d' ' -f1) $(last 002-a-y) $(last 003-a-z | cut -d' ' -f1))" $r

echo "T-Q3 rm guard"
mk; step 001-g-x 1 "sleep 1" "MODELS=$W/model.gguf"; touch $W/model.gguf
bash $Q rm-guard $W/model.gguf >/dev/null; a=$?
bash $Q start >/dev/null; waitrun; bash $Q rm-guard $W/model.gguf >/dev/null; b=$?
r=0; [ $a = 1 ] && [ $b = 0 ] || r=1; ok "T-Q3 rm-guard rc queued=$a (want 1), after DONE=$b (want 0)" $r
mk; step 001-g-y 1 "true" "MODELS=$W/absent.gguf"; bash $Q start >/dev/null; waitrun
grep -q '^FAIL model-missing' $QUEUE_DIR/001-g-y.status; ok "T-Q3b missing model -> FAIL model-missing, step not run" $?

echo "T-Q4 disk refusal"
mk; export DISK_FLOOR_GIB=999999; step 001-d-x 1 "echo ran > $W/ran"; bash $Q start >/dev/null; waitrun
r=0; grep -q '^FAIL disk ' $QUEUE_DIR/001-d-x.status && [ ! -e $W/ran ] && [ ! -e $QUEUE_DIR/001-d-x.log ] || r=1; ok "T-Q4 $(last 001-d-x)" $r; export DISK_FLOOR_GIB=0

echo "T-Q5 restart idempotence"
mk; step 001-r-x 1 "echo hi"; step 002-r-y 1 "echo hi"; bash $Q start >/dev/null; waitrun
s1=$(cat $QUEUE_DIR/[0-9]*.log $QUEUE_DIR/*.status | wc -c); bash $Q start >/dev/null; sleep 1; waitrun; s2=$(cat $QUEUE_DIR/[0-9]*.log $QUEUE_DIR/*.status | wc -c)
[ "$s1" = "$s2" ]; ok "T-Q5 log+status bytes $s1 -> $s2" $?
mk; step 001-s-x 1 "sleep 5"; bash $Q start >/dev/null; bash $Q start >/dev/null; rc=$?; [ $rc = 2 ]; ok "T-Q5b second instance refused (rc=$rc)" $?; touch $QUEUE_DIR/KILL-NOW; waitrun 100

echo "T-Q6 KILL-NOW kills the running step's process group"
mk; step 001-k-x 1 "sleep 20 & echo \$! > $W/sleep.pid; wait"; bash $Q start >/dev/null; sleep 1.5; t0=$(date +%s); bash $Q stop-now >/dev/null
i=0; while [ $i -lt 50 ] && ! grep -q '^KILL ' $QUEUE_DIR/001-k-x.status 2>/dev/null; do sleep 0.1; i=$((i+1)); done
sp=$(cat $W/sleep.pid 2>/dev/null); sleep 0.3; gone=1; kill -0 "$sp" 2>/dev/null && gone=0
r=0; grep -q '^KILL ' $QUEUE_DIR/001-k-x.status && [ $gone = 1 ] && [ $(( $(date +%s) - t0 )) -le 5 ] || r=1; ok "T-Q6 KILL line, sleep gone=$gone" $r
mk; step 001-q-x 1 "sleep 2"; step 002-q-y 1 "true"; bash $Q start >/dev/null; sleep 0.5; bash $Q stop >/dev/null; waitrun
r=0; [ "$(last 001-q-x | cut -d' ' -f1)" = DONE ] && [ -z "$(last 002-q-y)" ] && [ ! -e $QUEUE_DIR/KILL ] || r=1; ok "T-Q6b KILL sentinel finishes current step, skips rest" $r
echo "queue-tests: $PASS pass, $FAIL fail"; [ $FAIL = 0 ]
