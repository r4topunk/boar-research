#!/bin/bash
# QWRITE step 0 generation: one llama-server (4B, :8097), gen_qw.py, stop. busy.sh + disk floor 5 GiB.
set -uo pipefail
B=<workspace>; A=$B/rnd/research/coordinator/arms/qwrite; SRV=$B/spikes/llama-b11010-cpu/bin/llama-server
$B/rnd/research/coordinator/arms/headpass-st/tools/busy.sh && { echo "FAIL busy"; exit 1; }
FREE=$(df -g / | awk 'NR==2{print $4}'); [ "$FREE" -lt 5 ] && { echo "FAIL disk $FREE GiB"; exit 1; }
$SRV -m $B/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf --port 8097 --host 127.0.0.1 -c 2048 -t 4 --seed 42 > $A/runs/server.log 2>&1 &
PID=$!; trap "kill $PID 2>/dev/null; wait $PID 2>/dev/null" EXIT
for i in $(seq 1 120); do curl -sf http://127.0.0.1:8097/health >/dev/null && break; sleep 1; done
T0=$(date +%s); python3 $A/tools/gen_qw.py http://127.0.0.1:8097; echo "wall $(( $(date +%s) - T0 )) s"
