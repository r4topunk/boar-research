#!/usr/bin/env bash
# SPECDEC extras (descriptive), queued behind the main matrix in the heavy lock:
#  (a) measured c on the mini: the draft models decoding ALONE on the first 10 prompts (greedy), vs the 4B alone (base1/baseg first 10 items)
#  (b) why Qwen2.5-1.5B is refused: llama-server -lv 4 start with -md, grep the speculative vocab check
set -uo pipefail
scp -q $(dirname $0)/specdec_replay.py MINI_HOST:boar/kiln/specdec/
cat > /tmp/specdec-extra-remote.sh <<'R'
cd <runner>/kiln/specdec
export HEAVY_CLASS=normal
SPECDEC_LIMIT=10 SPECDEC_TARGET=<runner>/kiln/specdec/Qwen3-0.6B-Q8_0.gguf <runner>/bin/run-heavy Kiln python3 specdec_replay.py prompts.jsonl res_c d06alone:greedy:none:0 > run_c.log 2>&1
SPECDEC_LIMIT=10 SPECDEC_TARGET=<runner>/shared-models/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf <runner>/bin/run-heavy Kiln python3 specdec_replay.py prompts.jsonl res_c d15alone:greedy:none:0 >> run_c.log 2>&1
SPECDEC_LIMIT=10 <runner>/bin/run-heavy Kiln python3 specdec_replay.py prompts.jsonl res_c base10g:greedy:none:0 >> run_c.log 2>&1
( timeout 60 <runner>/spikes/llama-b11010/build-cpu/bin/llama-server -m <runner>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf -md <runner>/shared-models/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf --spec-type draft-simple -ngl 0 -np 1 -c 512 -lv 4 --host 127.0.0.1 --port 8188 > res_c/q15-verbose.log 2>&1 ) 
echo done >> run_c.log
R
scp -q /tmp/specdec-extra-remote.sh MINI_HOST:boar/kiln/specdec/extra.sh
<on the mini> "bash -c 'cd <runner>/kiln/specdec && mkdir -p res_c && nohup bash extra.sh > extra.out 2>&1 < /dev/null &'" >/dev/null 2>&1
echo queued
