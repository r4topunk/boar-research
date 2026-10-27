#!/bin/bash
# VEXACT-ACCEPT generation on the Mac mini (copied to <runner>/kiln/vexact-accept/tools by run.sh; called over ssh).
# Engine = kiln tree be-0cfd4a77-cut7-headpass-x2 (cut 7 + HEADPASS-X2b, opts-forwarding adapter 8dd1faff), Qwen3-4B-Instruct-2507 Q4_K_M,
# llama-server b11010 CPU on OUR port only (default 8193; same args the adapter uses for its own server), detector :8094 (never started/stopped here),
# --places kit-vexact (gazetteer + Berlin/Lisbon/Tokyo tiles = device location + area tile, as V-exact/VENUEGPS-2).
# Usage: mini_gen.sh <requests.jsonl> <out traces.jsonl>
# Env: VXA_PORT (8193) VXA_PROMPT (D4|engine; D4 -> vxa-hook rewrite with tools/d4.json) VXA_FACTS_JSON (optional facts table on the mini)
#      VXA_EXTRA_PACK_DIRS (optional, prepended to BOAR_EVAL_PACK_DIRS) VXA_FAKE_SERVER=1 (smoke: a stub already listens on VXA_PORT; no llama-server started)
#      VXA_MIN_FREE_GIB (25)
# Writes <out>.status (start/end/DONE|FAIL ...), <out>.log (adapter), <out>.rewrites.jsonl (hook audit), <out>.prompts.jsonl (engine dump, pre-rewrite),
#        <out>.llama.log (our server).
set -u
REQ=$1; OUT=$2; S=${OUT%.jsonl}.status
PORT=${VXA_PORT:-8193}; PROMPT=${VXA_PROMPT:-D4}; MINFREE=${VXA_MIN_FREE_GIB:-25}
H=$HOME; T=$H/boar/kiln/be-0cfd4a77-cut7-headpass-x2; TOOLS=$(cd "$(dirname "$0")" && pwd)
MD=$H/boar/shared-models/emergency-detector; MODEL=$H/boar/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf
SRV=$H/boar/spikes/llama-b11010/build-cpu/bin/llama-server; P=$H/boar/shared-data/poi/kit-vexact
export PATH=/opt/homebrew/bin:$PATH
fail() { echo "FAIL $*" >> "$S"; echo "FAIL $*" >&2; exit 1; }
echo "start $(date +%s) $(date '+%F %T') port=$PORT prompt=$PROMPT facts=${VXA_FACTS_JSON:-tree} extra=${VXA_EXTRA_PACK_DIRS:-none} fake=${VXA_FAKE_SERVER:-0}" > "$S"
[ "$PORT" = 8191 ] || [ "$PORT" = 8094 ] && fail "port $PORT belongs to another job"
cd "$T" || fail "tree"
[ "$(cut -c1-16 PATCH_SHA256)" = 0fba26b8c55aa776 ] || fail "patch sha"
[ "$(shasum -a 256 be/adapter.ts | cut -c1-16)" = 8dd1faff2b157d00 ] || fail "adapter sha"
[ "$(cat ARM)" = cut7-headpass-x2 ] || fail "ARM"
[ "$(cut -c1-16 HEADPASS_X2B_PATCH_SHA256)" = be413d7d5d9b3afd ] || fail "x2b patch sha"
(cd "$P" && shasum -a 256 -c SHA256SUMS >/dev/null 2>&1) || fail "kit-vexact SHA256SUMS"
curl -sf http://127.0.0.1:8094/health >/dev/null || fail "detector :8094 down (not started by this script)"
FREE=$(df -k "$H" | tail -1 | awk '{print int($4/1048576)}'); [ "$FREE" -ge "$MINFREE" ] || fail "disk ${FREE} GiB < $MINFREE"
HOOKENV=()
if [ "$PROMPT" = D4 ]; then HOOKENV+=(VXA_PROMPT_JSON="$TOOLS/d4.json"); elif [ "$PROMPT" != engine ]; then fail "VXA_PROMPT must be D4 or engine"; fi
[ -n "${VXA_FACTS_JSON:-}" ] && HOOKENV+=(VXA_FACTS_JSON="$VXA_FACTS_JSON")
rm -f "${OUT%.jsonl}.rewrites.jsonl" "${OUT%.jsonl}.prompts.jsonl" "$OUT"
SPID=""
cleanup() { [ -n "$SPID" ] && kill "$SPID" 2>/dev/null && wait "$SPID" 2>/dev/null; }
trap cleanup EXIT INT TERM
if [ "${VXA_FAKE_SERVER:-0}" != 1 ]; then
  lsof -tiTCP:$PORT -sTCP:LISTEN >/dev/null 2>&1 && fail "port $PORT already in use"
  "$SRV" -m "$MODEL" -t 4 -tb 4 -c 4096 -ngl 0 -np 1 --jinja --no-webui --cache-ram 0 --reasoning-format deepseek --host 127.0.0.1 --port $PORT \
    > "${OUT%.jsonl}.llama.log" 2>&1 < /dev/null & SPID=$!
  for i in $(seq 1 300); do curl -sf http://127.0.0.1:$PORT/health >/dev/null 2>&1 && break; kill -0 $SPID 2>/dev/null || fail "llama-server exited"; sleep 1; done
  curl -sf http://127.0.0.1:$PORT/health >/dev/null || fail "llama-server not healthy"
fi
PACKDIRS=$H/boar/shared-data/packs:$H/boar/shared-data/crypto; [ -n "${VXA_EXTRA_PACK_DIRS:-}" ] && PACKDIRS=$VXA_EXTRA_PACK_DIRS:$PACKDIRS
PLACES=$P/world-places.sqlite,$P/t-N52E013.sqlite,$P/t-N38W010.sqlite,$P/t-N35E139.sqlite,$P/t-N35E140.sqlite
echo "cmd adapter.ts --requests $REQ --out $OUT --backend server --server-url http://127.0.0.1:$PORT --places kit-vexact(5) packdirs=$PACKDIRS" >> "$S"
env BOAR_EVAL_PACK_DIRS="$PACKDIRS" BOAR_SHARED_MODELS=$H/boar/shared-models BOAR_RUNNER_PROFILE=ship HEAVY_CLASS=normal \
    BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json \
    BOAR_PROMPT_DUMP="${OUT%.jsonl}.prompts.jsonl" VXA_REWRITE_LOG="${OUT%.jsonl}.rewrites.jsonl" ${HOOKENV[@]+"${HOOKENV[@]}"} \
    NODE_OPTIONS="--import file://$TOOLS/vxa-hook.mjs" \
    node be/node_modules/tsx/dist/cli.mjs be/adapter.ts --requests "$REQ" --out "$OUT" --backend server --server-bin "$SRV" \
    --server-url http://127.0.0.1:$PORT --threads 4 --timeout-ms 600000 --places "$PLACES" > "${OUT%.jsonl}.log" 2>&1; rc=$?
cleanup; SPID=""
curl -sf http://127.0.0.1:8094/health >/dev/null && echo "detector still up" >> "$S" || echo "DETECTOR-LOST" >> "$S"
echo "end $(date +%s) rc=$rc" >> "$S"; if [ $rc = 0 ]; then echo DONE >> "$S"; else echo "FAIL rc=$rc" >> "$S"; fi; exit $rc
