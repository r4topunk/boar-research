#!/bin/bash
# BONSAI2 S0 runner on the mini: 9B ternary (thinking off) then the 4B control. One server at a time, port 8097.
W=<runner>/kiln/bonsai2; S=$W/S0.status; cd $W
echo "start $(date '+%F %T')" > $S
PRISM=<runner>/spikes/llama-prism/bin/llama-server
STD=<runner>/spikes/llama-b11010/build-cpu/bin/llama-server
NT='{"chat_template_kwargs":{"enable_thinking":false},"temperature":0.7,"top_p":0.8,"top_k":20,"min_p":0,"presence_penalty":1.5}'
python3 smoke.py bonsai2-9b-ptq1 $PRISM <runner>/shared-models/bonsai2/Ternary-Bonsai-2-9B-PTQ1_0.gguf s0-items.json s0-bonsai2-9b.jsonl "$NT" --device none -ngl 0 --no-op-offload >> $S 2>&1
python3 smoke.py qwen3-4b-q4km $STD <runner>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf s0-items.json s0-qwen3-4b.jsonl '{"temperature":0.7,"top_p":0.8,"top_k":20,"min_p":0}' >> $S 2>&1
echo "end $(date '+%F %T')" >> $S
