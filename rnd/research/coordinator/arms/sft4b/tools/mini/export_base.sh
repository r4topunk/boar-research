#!/bin/bash
# SFT4B stage 0 (mini): export-path parity input = BASE bf16 (no LoRA) -> GGUF f16 -> Q4_K_M with llama.cpp b11010 (4bc272f),
# the tag whose llama-server serves the claim runs. Needs ~10 GB transient (f16 7.5 GiB is deleted after quantize).
# Output <runner>/kiln/sft4b/export/qwen3-4b-instruct-2507-base-requant-q4km.gguf (+ sha). Refuses below the 25 GiB floor.
set -u
K=<runner>/kiln/sft4b; L=<runner>/spikes/llama-b11010; M=<runner>/shared-models/hf/Qwen3-4B-Instruct-2507; O=$K/export; mkdir -p "$O"
freek=$(df -k ~ | tail -1 | awk '{print $4}'); [ $(( freek/1048576 - 10 )) -ge 25 ] || { echo "BLOCKED: free $((freek/1048576)) GiB - 10 GiB transient < 25" | tee "$O/status"; exit 3; }
"$K/.venv/bin/python" "$L/convert_hf_to_gguf.py" "$M" --outtype f16 --outfile "$O/base-f16.gguf" > "$O/convert.log" 2>&1 || { echo FAIL convert > "$O/status"; exit 1; }
"$L/build-cpu/bin/llama-quantize" "$O/base-f16.gguf" "$O/qwen3-4b-instruct-2507-base-requant-q4km.gguf" Q4_K_M > "$O/quantize.log" 2>&1 || { echo FAIL quantize > "$O/status"; exit 1; }
rm -f "$O/base-f16.gguf"; shasum -a 256 "$O"/*.gguf > "$O/status"; ls -l "$O"/*.gguf >> "$O/status"; echo DONE >> "$O/status"
