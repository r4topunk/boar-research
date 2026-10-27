#!/bin/bash
# DEEPBO2 mini-side selector runner (criterion sha256 c7e2232f...). Copied by the coordinator to <runner>/kiln/deepbo2-run.sh,
# with select.py next to it and the prompts at <runner>/kiln/deepbo2/prompts.jsonl.
# Usage (on the mini, under nohup): deepbo2-run.sh <S1|S2>
# Refuses if any llama-server other than the detector (:8094) runs, or a heavy job holds/queues the lock; then re-execs itself
# under `<runner>/bin/run-heavy Kiln`, starts llama-server b11010 on :8097, runs select.py, and kills ONLY the server it started (by pid).
# STATUS lines -> <runner>/kiln/deepbo2/<S>.STATUS. Never touches the detector or Docker.
set -u
SEL=${1:-}; MODE=${2:-outer}
case "$SEL" in
  S1) MODEL=<runner>/shared-models/Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf ;;
  S2) MODEL=<runner>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf ;;
  *) echo "usage: $0 <S1|S2>"; exit 2 ;;
esac
HERE=$(cd "$(dirname "$0")" && pwd); SELPY=${SELECT_PY:-$HERE/select.py}
D=<runner>/kiln/deepbo2; PROMPTS=$D/prompts.jsonl; S=$D/$SEL.STATUS
SRV=<runner>/spikes/llama-b11010/build-cpu/bin/llama-server; PORT=8097
PROMPTS_SHA=affdd1abe459b25f6ed4de11799d09bbcec8844c008d79316adf92ab94e7c86b
mkdir -p $D

if [ "$MODE" = outer ]; then
  echo "start $(date +%s) $(date '+%F %T') sel=$SEL" > $S
  [ -f "$SELPY" ] || { echo "FAIL select.py missing" >> $S; exit 1; }
  [ -f "$MODEL" ] || { echo "FAIL model missing" >> $S; exit 1; }
  [ "$(shasum -a 256 $PROMPTS | cut -d' ' -f1)" = $PROMPTS_SHA ] || { echo "FAIL prompts sha" >> $S; exit 1; }
  echo "select.py sha $(shasum -a 256 $SELPY | cut -c1-16)" >> $S
  if pgrep -fl llama-server | grep -v -- "--port 8094" | grep -q .; then echo "FAIL another llama-server is running" >> $S; exit 1; fi
  if pgrep -f "boar/bin/run-heavy" >/dev/null; then echo "FAIL a heavy job is running/queued" >> $S; tail -1 <runner>/heavy.log >> $S 2>/dev/null; exit 1; fi
  if lsof -nP -iTCP:$PORT -sTCP:LISTEN >/dev/null 2>&1; then echo "FAIL port $PORT busy" >> $S; exit 1; fi
  FREE=$(df -g ~ | awk 'NR==2{print $4}'); echo "free_gib $FREE" >> $S
  [ "$FREE" -ge 25 ] || { echo "FAIL disk < 25 GiB" >> $S; exit 1; }
  sysctl -n vm.swapusage >> $S
  curl -sf http://127.0.0.1:8094/health >/dev/null && echo "detector up (untouched)" >> $S || echo "detector not running (not started; not needed)" >> $S
  export HEAVY_CLASS=normal
  <runner>/bin/run-heavy Kiln "$HERE/$(basename "$0")" "$SEL" inner >> $D/$SEL.run.log 2>&1
  rc=$?
  curl -sf http://127.0.0.1:8094/health >/dev/null && echo "detector up at end" >> $S || echo "detector not up at end" >> $S
  echo "end $(date +%s) rc=$rc" >> $S; echo DONE >> $S
  exit $rc
fi

# inner: runs under the heavy lock
echo "lock $(date +%s) $(date '+%F %T')" >> $S
"$SRV" -m "$MODEL" -t 4 -tb 4 -c 4096 -ngl 0 -np 1 --jinja --no-webui --cache-ram 0 --reasoning-format deepseek \
  --host 127.0.0.1 --port $PORT > $D/$SEL.server.log 2>&1 < /dev/null &
SPID=$!
echo "server pid $SPID" >> $S
cleanup() { if kill -0 $SPID 2>/dev/null; then kill $SPID; for i in $(seq 1 30); do kill -0 $SPID 2>/dev/null || break; sleep 1; done; kill -9 $SPID 2>/dev/null; fi; echo "server $SPID stopped" >> $S; }
trap cleanup EXIT
ok=0
for i in $(seq 1 300); do
  kill -0 $SPID 2>/dev/null || { echo "FAIL server exited during load" >> $S; exit 1; }
  curl -sf http://127.0.0.1:$PORT/health >/dev/null && { ok=1; break; }; sleep 2
done
[ $ok = 1 ] || { echo "FAIL server health timeout" >> $S; exit 1; }
echo "server ready $(date +%s)" >> $S
python3 -I "$SELPY" "$SEL" http://127.0.0.1:$PORT --prompts $PROMPTS --replies-dir $D --agg-dir $D > $D/$SEL.select.log 2>&1
rc=$?
echo "select rc=$rc $(tail -1 $D/$SEL.select.log | cut -c1-300)" >> $S
sysctl -n vm.swapusage >> $S
exit $rc
