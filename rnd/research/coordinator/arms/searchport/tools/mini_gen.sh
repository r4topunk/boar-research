#!/bin/bash
# NATIVE-RC generation on the Mac mini (kiln lock mini-long held by the caller): copies a prompts file, runs llama-server b11010 CPU
# (Qwen3-1.7B Q4_K_M sha b139949c, -c 4096 -t 4, port 8197) and tools/s3_gen.py (native Sampling defaults: temp 0.7, top_k 40, top_p 0.95,
# min_p 0.05, repeat 1.0, seed 42, stop <|im_end|>, n_predict = maxTokens), fetches the generations back. usage: mini_gen.sh <prompts.jsonl> <gen.jsonl>
set -euo pipefail
A=<workspace>/rnd/research/coordinator/arms/native-rc; D=searchport; P=$1; G=$2; N=$(basename $P .jsonl)
<on the mini> 'mkdir -p <runner>/kiln/searchport'
scp -q $A/tools/s3_gen.py $P MINI_HOST:boar/kiln/searchport/
[ -f $G ] && scp -q $G MINI_HOST:boar/kiln/searchport/$N.gen.jsonl || true
<on the mini> "bash -c '
set -e; cd <runner>/kiln/searchport
df -g ~ | tail -1 | awk \"{ if (\\\$4 < 25) { print \\\"DISK LOW\\\"; exit 3 } }\"
M=<runner>/shared-models/lite/Qwen3-1.7B-Q4_K_M.gguf
pgrep -f \"port 8197\" >/dev/null || { <runner>/spikes/llama-b11010/build-cpu/bin/llama-server -m \$M -c 4096 -t 4 -np 1 --port 8197 > server-$N.log 2>&1 & }
for i in \$(seq 120); do curl -sf localhost:8197/health >/dev/null && break; sleep 1; done
python3 -I s3_gen.py $N.jsonl $N.gen.jsonl 8197 > gen-$N.log 2>&1
pkill -f \"port 8197\" || true
wc -l $N.gen.jsonl'"
scp -q MINI_HOST:boar/kiln/searchport/$N.gen.jsonl $G
