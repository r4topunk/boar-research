#!/bin/bash
# SFT4B parity (mini): start the CPU llama-server b11010 on the claim Q4_K_M (+ optional LoRA args), run p_gen.py, stop THIS server only.
# usage (nohup): bash p_server.sh <tag> <n prompts> [extra server args...]   -> $K/parity/<tag>.{jsonl,server.log,status}
set -u
K=<runner>/kiln/sft4b; L=<runner>/spikes/llama-b11010; G=<runner>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf; PORT=8097
TAG=$1; N=$2; shift 2; O=$K/parity; mkdir -p "$O"; S=$O/$TAG.status
echo "start $(date '+%F %T') args: $*" > "$S"
lsof -iTCP:$PORT -sTCP:LISTEN >/dev/null 2>&1 && { echo "FAIL port $PORT busy" >> "$S"; exit 1; }
"$L/build-cpu/bin/llama-server" -m "$G" -c 4096 -np 1 -t 4 --seed 42 --host 127.0.0.1 --port $PORT "$@" > "$O/$TAG.server.log" 2>&1 &
SP=$!; echo "server pid $SP" >> "$S"
for i in $(seq 1 120); do curl -sf http://127.0.0.1:$PORT/health >/dev/null && break; kill -0 $SP 2>/dev/null || break; sleep 1; done
curl -sf http://127.0.0.1:$PORT/health >/dev/null || { echo "FAIL server did not start" >> "$S"; kill $SP 2>/dev/null; exit 1; }
curl -s http://127.0.0.1:$PORT/lora-adapters > "$O/$TAG.lora-adapters.json"
"$K/.venv/bin/python" "$K/p_gen.py" server $PORT "$K/parity/parity-prompts.jsonl" "$N" "$O/$TAG.jsonl" >> "$S" 2>&1; rc=$?
kill $SP; wait $SP 2>/dev/null
echo "end $(date '+%F %T') rc=$rc" >> "$S"; [ $rc = 0 ] && echo DONE >> "$S" || echo "FAIL rc=$rc" >> "$S"
