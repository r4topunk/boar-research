#!/bin/bash
# BONSAI2 S0 addendum: llama-bench pp512 / tg64, CPU only, -t 8, both models (one at a time).
W=<runner>/kiln/bonsai2; S=$W/BENCH.status; cd $W; echo "start $(date '+%F %T')" > $S
<runner>/spikes/llama-prism/bin/llama-bench -m <runner>/shared-models/bonsai2/Ternary-Bonsai-2-9B-PTQ1_0.gguf -t 8 -ngl 0 -dev none -p 512 -n 64 -r 2 -o md > bench-9b.md 2>bench-9b.err; echo "9b_rc=$?" >> $S
<runner>/spikes/llama-b11010/build-cpu/bin/llama-bench -m <runner>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf -t 8 -ngl 0 -p 512 -n 64 -r 2 -o md > bench-4b.md 2>bench-4b.err; echo "4b_rc=$?" >> $S
echo "end $(date '+%F %T')" >> $S
