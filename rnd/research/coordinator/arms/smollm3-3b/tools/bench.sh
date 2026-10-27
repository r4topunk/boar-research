#!/bin/bash
# SMOLLM3-3B stage 0 (mini, 0 judge): llama-bench b11010 CPU, -t 4 -p 512 -n 128 -r 3, interleaved A B A B so both models see the same
# background load (other lab jobs may hold the gen slots). Prints the bench lines + loadavg per run. Usage: bench.sh <outdir>
set -u; O=$1; mkdir -p $O; B=$HOME/boar/spikes/llama-b11010/build-cpu/bin/llama-bench; L=$HOME/boar/shared-models/lite
for rep in 1 2; do for m in Qwen3-1.7B-Q4_K_M HuggingFaceTB_SmolLM3-3B-Q4_K_M; do
  echo "== rep $rep $m load $(sysctl -n vm.loadavg)"
  $B -m $L/$m.gguf -t 4 -p 512 -n 128 -r 3 -ngl 0 -o md 2>$O/$m-$rep.err | tee $O/$m-$rep.md
done; done
