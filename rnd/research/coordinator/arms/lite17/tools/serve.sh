#!/bin/bash
# LITE17: Qwen3-1.7B Q4_K_M on llama-server b11010 (4bc272f) CPU, MacBook, port 8192 ONLY (never :8094/:8196). Stop: pkill -f "llama-server.*--port 8192"
L=<workspace>/rnd/research/coordinator/arms/lite17/server.log
nohup <workspace>/spikes/llama-b11010-cpu/bin/llama-server -m <workspace>/shared-models/lite/Qwen3-1.7B-Q4_K_M.gguf \
  -t 4 -tb 4 -c 6144 -ngl 0 -np 1 --jinja --no-webui --cache-ram 0 --reasoning-format deepseek --host 127.0.0.1 --port 8192 > "$L" 2>&1 &
disown
for i in $(seq 1 60); do curl -s 127.0.0.1:8192/health | grep -q ok && { echo UP; exit 0; }; sleep 2; done; echo FAIL; exit 1
