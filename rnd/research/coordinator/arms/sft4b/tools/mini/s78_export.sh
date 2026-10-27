#!/bin/bash
# SFT4B stage 1 steps 7-8 (+P1) on the mini: MLX adapter -> PEFT -> GGUF LoRA f16 (config-only --base), then P1.
# usage: bash s78_export.sh [adapter dir, default $K/train/adapter] [export dir, default $K/export]  -> <export>/{status, convert.log, p1.json, peft/}
set -u
K=<runner>/kiln/sft4b; V=$K/.venv/bin; L=<runner>/spikes/llama-b11010; A=${1:-$K/train/adapter}; E=${2:-$K/export}; P=$E/peft; mkdir -p "$E"; S=$E/status
OUTF=$E/qwen3-4b-instruct-2507-sft4b-lora-f16.gguf
echo "start $(date '+%F %T') adapter=$A" > "$S"
"$V/python" "$K/mlx2peft.py" "$A" "$P" >> "$S" 2>&1 || { echo "FAIL mlx2peft" >> "$S"; exit 1; }
"$V/python" "$L/convert_lora_to_gguf.py" --base "$K/base-config" --outtype f16 --outfile "$OUTF" "$P" > "$E/convert.log" 2>&1 || { echo "FAIL convert" >> "$S"; exit 1; }
ls -l "$OUTF" >> "$S"; shasum -a 256 "$OUTF" >> "$S"
"$V/python" "$K/p1_check.py" "$A" "$OUTF" > "$E/p1.json" 2>&1; rc=$?
echo "p1 rc=$rc" >> "$S"; [ $rc = 0 ] && echo "P1 PASS" >> "$S" || echo "P1 FAIL" >> "$S"; echo DONE >> "$S"
