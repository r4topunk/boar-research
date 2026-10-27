#!/bin/bash
# NOTES35 mini-side generation: start a llama-server on the 35B (port 8097), wait for /health, run gen_notes.mjs for N
# titles of order-bf.txt, stop THAT server only (never the detector on :8094), write STATUS (DONE / FAIL ...).
# Usage (on the mini, under nohup):  gen_notes_mini.sh <N> <out_dir> [think_budget]
#   e.g. nohup <runner>/kiln/notes35/tools/gen_notes_mini.sh 300 <runner>/kiln/notes35/run-n300 > /dev/null 2>&1 &
# Resumable: rerun with the same <out_dir> (and a larger N to extend 300 -> 1000); titles already in notes.jsonl are skipped.
# Server flags = the adapter's llama-server backend (boar-eval/adapters/desktop-node/runner/adapter.ts:422-424) with the
# deep runs' --threads 4 (arms/*/tools/remote-run.sh) and the b11010 CPU build those runs used.
set -u
N=${1:?N}; OUT=${2:?out_dir}; BUDGET=${3:-0}
HERE="$(cd "$(dirname "$0")" && pwd)"
SRV=${NOTES35_SERVER_BIN:-<runner>/spikes/llama-b11010/build-cpu/bin/llama-server}
M=${NOTES35_MODEL:-$HOME/boar/shared-models/Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf}
M_SHA=${NOTES35_MODEL_SHA:-96b9c0af5c77a4ecaabe3983175112b5ece763261c1ece12b2494b692a70dad7}   # rnd/kiln/MODELS.md, adapter.ts DEEP_MODELS
PORT=${NOTES35_PORT:-8097}; THREADS=${NOTES35_THREADS:-4}
ORDER=${NOTES35_ORDER:-$HERE/../topics/order-bf.txt}
mkdir -p "$OUT"; S=$OUT/STATUS; LOG=$OUT/llama-server-$PORT.log
echo "start $(date +%s) $(date '+%F %T') N=$N budget=$BUDGET" > "$S"
fail() { echo "FAIL $*" >> "$S"; [ -n "${PID:-}" ] && kill "$PID" 2>/dev/null; exit 1; }

command -v node >/dev/null || fail "no node"
[ "$(node -p 'process.versions.node.split(".")[0]')" -ge 22 ] || fail "node < 22"
[ -x "$SRV" ] || fail "no llama-server at $SRV"
[ -f "$M" ] || fail "35B GGUF missing at $M (deleted 2026-10-10; re-download per rnd/kiln/MODELS.md, verify sha $M_SHA)"
if [ ! -f "$OUT/model.sha256.ok" ]; then
  got=$(shasum -a 256 "$M" | cut -d' ' -f1); [ "$got" = "$M_SHA" ] || fail "model sha $got"
  echo "$got" > "$OUT/model.sha256.ok"
fi
(cd "$HERE" && shasum -a 256 -c note.system.md.sha256 --status) || fail "system prompt sha"
(cd "$HERE/../topics" && shasum -a 256 -c order-bf.txt.sha256 --status) || fail "order-bf.txt sha"
if pgrep -fl "llama-server.*Qwen3.6-35B" >/dev/null; then fail "a 35B llama-server is already running"; fi
curl -sf "http://127.0.0.1:$PORT/health" >/dev/null && fail "port $PORT busy"
df -g ~ | awk 'NR==2{print "free_gib " $4}' >> "$S"
[ "$(df -g ~ | awk 'NR==2{print $4}')" -ge "${NOTES35_MIN_FREE_GIB:-25}" ] || fail "free disk < ${NOTES35_MIN_FREE_GIB:-25} GiB (rnd/DISK-POLICY.md)"
curl -sf http://127.0.0.1:8094/health >/dev/null && echo "detector up (untouched)" >> "$S"

"$SRV" -m "$M" -t "$THREADS" -tb "$THREADS" -c 4096 -ngl 0 -np 1 --jinja --no-webui --cache-ram 0 --reasoning-format deepseek \
  --host 127.0.0.1 --port "$PORT" > "$LOG" 2>&1 < /dev/null &
PID=$!
trap '[ -n "${PID:-}" ] && kill "$PID" 2>/dev/null' EXIT   # only this server, on any exit
echo "server pid $PID" >> "$S"
for i in $(seq 1 300); do
  curl -sf "http://127.0.0.1:$PORT/health" >/dev/null && break
  kill -0 "$PID" 2>/dev/null || fail "llama-server exited during load (see $LOG)"
  sleep 2
done
curl -sf "http://127.0.0.1:$PORT/health" >/dev/null || fail "llama-server not healthy after 600 s"
echo "healthy $(date +%s)" >> "$S"

EXTRA=(); [ "$BUDGET" -gt 0 ] && EXTRA=(--think-budget "$BUDGET")
node "$HERE/gen_notes.mjs" --order "$ORDER" --n "$N" --out "$OUT/notes.jsonl" --server-url "http://127.0.0.1:$PORT" \
  --model "${NOTES35_MODEL_NAME:-qwen3.6-35b-a3b-ud-q2kxl}" ${EXTRA[@]+"${EXTRA[@]}"} 2> "$OUT/gen.log"
rc=$?
kill "$PID" 2>/dev/null; wait "$PID" 2>/dev/null; PID=
curl -sf http://127.0.0.1:8094/health >/dev/null && echo "detector still up" >> "$S"
lines=$(grep -c . "$OUT/notes.jsonl" 2>/dev/null || echo 0)
echo "end $(date +%s) rc=$rc notes=$lines" >> "$S"
[ -f "$OUT/notes.jsonl" ] && shasum -a 256 "$OUT/notes.jsonl" >> "$S"
if [ $rc -eq 0 ]; then echo DONE >> "$S"; else echo "FAIL rc=$rc" >> "$S"; exit $rc; fi
