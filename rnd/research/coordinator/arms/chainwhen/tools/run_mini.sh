#!/bin/bash
# CHAINWHEN chain on the mini: start M4 on :8191 (same flags as prompt3m/serve.sh), generate, stop the server. Never touches :8094.
export PATH=/opt/homebrew/bin:$PATH; D=<runner>/kiln/chainwhen; cd $D
log(){ echo "$(date '+%F %T') $*" >> chain.log; }
pkill -f "llama-server.*--port 8191" 2>/dev/null; sleep 2
nohup $HOME/boar/spikes/llama-b11010/build-cpu/bin/llama-server -m $HOME/boar/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf -t 4 -tb 4 -c 4096 -ngl 0 -np 1 --jinja --reasoning-format deepseek --no-webui --cache-ram 0 --host 127.0.0.1 --port 8191 > $D/server.log 2>&1 &
ok=0; for i in $(seq 1 90); do curl -s 127.0.0.1:8191/health | grep -q ok && { ok=1; break; }; sleep 2; done
[ $ok = 1 ] || { log SERVE-FAIL; exit 1; }
log start; python3 -I gen.py >> gen.log 2>&1; log "done rc=$? rows=$(wc -l < answers-M4.jsonl)"
pkill -f "llama-server.*--port 8191"; log CHAIN-DONE
