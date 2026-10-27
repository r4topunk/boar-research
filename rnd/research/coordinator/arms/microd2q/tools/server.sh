#!/bin/bash
# MICROD2Q generator server: the engine's llama-server build (b11010 CPU) + Qwen3-4B-Instruct-2507-Q4_K_M (same GGUF as the
# cut-7 runs), -np 4 (proposal §2 spec), port 8097. Never touches :8094. usage: server.sh start|stop
set -u
A=<workspace>/rnd/research/coordinator/arms/microd2q; SRV=<workspace>/spikes/llama-b11010-cpu/bin/llama-server
G=<workspace>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf; PORT=8097; PID=$A/logs/server.pid
case "$1" in
start)
  pgrep -f "llama-server .*Qwen3-4B" >/dev/null && { echo "FAIL: a 4B llama-server is already running"; exit 1; }
  lsof -iTCP:$PORT -sTCP:LISTEN >/dev/null 2>&1 && { echo "FAIL: port $PORT busy"; exit 1; }
  "$SRV" -m "$G" -t ${THREADS:-6} -tb ${THREADS:-6} -c 8192 -np 4 -ngl 0 --jinja --no-webui --seed 42 --host 127.0.0.1 --port $PORT > $A/logs/server.log 2>&1 &
  echo $! > $PID
  for i in $(seq 1 120); do curl -sf http://127.0.0.1:$PORT/health >/dev/null && { echo "up pid $(cat $PID)"; exit 0; }; sleep 1; done
  echo "FAIL: server did not start"; kill $(cat $PID); exit 1;;
stop) [ -f $PID ] && kill $(cat $PID) && rm -f $PID && echo stopped;;
esac
