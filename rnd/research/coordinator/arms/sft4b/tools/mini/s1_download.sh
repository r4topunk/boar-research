#!/bin/bash
# SFT4B stage 1 (mini), PIPELINE-OPTIONS §2 steps 1-3 (addendum-1 path b): disk gate -> 8-bit MLX base download (sha+size check)
# -> config-only dir from the Qwen repo. Resumable (hf download skips complete files). Status: $K/s1_download.status (DONE | BLOCKED | FAIL ...)
set -u
K=<runner>/kiln/sft4b; V=$K/.venv/bin; M=<runner>/shared-models/hf/Qwen3-4B-Instruct-2507-mlx8; S=$K/s1_download.status
REV8=0e42af58449718de7931ee04f28191fbe6c43a56; SHA8=a6d98b6b22bd3928f0a9e38aea84c085e678bba1e03d028f21cbf6e0f6ed9f2c; SIZE8=4274158989
REVQ=cdbee75f17c01a7cc42f958dc650907174af0554
export HF_HUB_DISABLE_TELEMETRY=1
freek=$(df -k ~ | tail -1 | awk '{print $4}'); freeg=$(( freek/1048576 ))
echo "start $(date '+%F %T') free_KiB=$freek free_GiB=$freeg" > "$S"
[ $(( freeg - 5 )) -ge 28 ] || { echo "BLOCKED: free $freeg - 5 < 28 GiB" >> "$S"; exit 3; }
echo "cache_before_KiB=$(du -sk ~/.cache/huggingface 2>/dev/null | cut -f1)" >> "$S"
mkdir -p "$M"
"$V/hf" download mlx-community/Qwen3-4B-Instruct-2507-8bit --revision "$REV8" --local-dir "$M" >> "$S" 2>&1 || { echo "FAIL download8" >> "$S"; exit 1; }
sz=$(stat -f %z "$M/model.safetensors"); sh=$(shasum -a 256 "$M/model.safetensors" | cut -d' ' -f1)
echo "model.safetensors size=$sz sha256=$sh" >> "$S"
[ "$sz" = "$SIZE8" ] && [ "$sh" = "$SHA8" ] || { echo "FAIL sha/size mismatch" >> "$S"; exit 1; }
( cd "$M" && ls -l && shasum -a 256 *.json *.jinja 2>/dev/null ) >> "$S"
echo "du_M_KiB=$(du -sk "$M" | cut -f1) cache_after_KiB=$(du -sk ~/.cache/huggingface 2>/dev/null | cut -f1)" >> "$S"
mkdir -p "$K/base-config"
"$V/hf" download Qwen/Qwen3-4B-Instruct-2507 config.json generation_config.json tokenizer_config.json tokenizer.json vocab.json merges.txt --revision "$REVQ" --local-dir "$K/base-config" >> "$S" 2>&1 || { echo "FAIL base-config" >> "$S"; exit 1; }
( cd "$K/base-config" && shasum -a 256 * ) >> "$S" 2>/dev/null
freek2=$(df -k ~ | tail -1 | awk '{print $4}'); echo "free_after_KiB=$freek2 free_after_GiB=$(( freek2/1048576 )) delta_KiB=$(( freek - freek2 ))" >> "$S"
echo DONE >> "$S"
