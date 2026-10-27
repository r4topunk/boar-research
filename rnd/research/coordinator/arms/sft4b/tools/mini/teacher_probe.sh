#!/bin/bash
# SFT4B TEACHER-PROBE (mini): start the deep-tier CPU llama-server b11010 (Qwen3.6-35B-A3B UD-Q2_K_XL, -t 8 -c 4096 -np 1 --jinja)
# on port 8098, run tp_gen.py (resumable), stop THIS server only. Never touches :8094.
# usage (nohup): bash teacher_probe.sh   -> <runner>/kiln/sft4b/teacher-probe/{deep.jsonl,gen.log,server.log,status}
set -u
K=<runner>/kiln/sft4b; L=<runner>/spikes/llama-b11010; G=<runner>/shared-models/Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf; PORT=8098
O=$K/teacher-probe; S=$O/status; mkdir -p "$O"
echo "start $(date '+%F %T') free=$(df -g ~ | tail -1 | awk '{print $4}')GiB" >> "$S"
lsof -iTCP:$PORT -sTCP:LISTEN >/dev/null 2>&1 && { echo "FAIL port $PORT busy" >> "$S"; exit 1; }
"$L/build-cpu/bin/llama-server" -m "$G" -t 8 -c 4096 -np 1 --jinja --no-webui --seed 42 --host 127.0.0.1 --port $PORT > "$O/server.log" 2>&1 &
SP=$!; echo "server pid $SP" >> "$S"
for i in $(seq 1 300); do curl -sf http://127.0.0.1:$PORT/health >/dev/null && break; kill -0 $SP 2>/dev/null || break; sleep 1; done
curl -sf http://127.0.0.1:$PORT/health >/dev/null || { echo "FAIL server did not start" >> "$S"; kill $SP 2>/dev/null; exit 1; }
python3 -I "$K/tp_gen.py" $PORT "$O/contexts.jsonl" "$O/deep.jsonl" >> "$O/gen.log" 2>&1; rc=$?
kill $SP; wait $SP 2>/dev/null
echo "end $(date '+%F %T') rc=$rc free=$(df -g ~ | tail -1 | awk '{print $4}')GiB" >> "$S"; [ $rc = 0 ] && echo DONE >> "$S" || echo "FAIL rc=$rc" >> "$S"
