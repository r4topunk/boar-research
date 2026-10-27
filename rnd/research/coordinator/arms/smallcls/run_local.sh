#!/bin/bash
# SMALLCLS on the MacBook, port 8192 (never touches :8094)
cd <workspace>/rnd/research/coordinator/arms/smallcls
serve(){ pkill -f "llama-server.*--port 8192"; sleep 2; nohup <workspace>/spikes/llama-b11010-cpu/bin/llama-server -m "$1" -t 6 -c 4096 -ngl 0 -np 1 --jinja --no-webui --host 127.0.0.1 --port 8192 > server.log 2>&1 & for i in $(seq 1 90); do curl -s 127.0.0.1:8192/health | grep -q ok && return 0; sleep 2; done; return 1; }
serve <workspace>/shared-models/lite/Qwen3-1.7B-Q4_K_M.gguf && python3 -I run.py Q17 '{"chat_template_kwargs":{"enable_thinking":false}}'
serve <workspace>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf && python3 -I run.py M4 '{}'
pkill -f "llama-server.*--port 8192"; echo LOCAL-DONE
