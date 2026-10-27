#!/bin/bash
# SFT4B stage 0 (mini): download Qwen/Qwen3-4B-Instruct-2507 bf16 (Apache-2.0) at a pinned revision into
# <runner>/shared-models/hf/Qwen3-4B-Instruct-2507/, REFUSING to start if free space after it would be < 25 GiB (DISK-POLICY floor).
# Run on the mini: bash download_base.sh   (writes <runner>/kiln/sft4b/download.status: BLOCKED | DONE + shas, sizes, df before/after)
set -u
REV=cdbee75f17c01a7cc42f958dc650907174af0554   # HF main on 2026-10-13 (lastModified 2025-09-17)
NEED=8060917568                                # sum of the 13 repo files (bytes, HF tree API)
D=<runner>/shared-models/hf/Qwen3-4B-Instruct-2507; V=<runner>/kiln/sft4b/.venv; S=<runner>/kiln/sft4b/download.status
freek=$(df -k ~ | tail -1 | awk '{print $4}'); after=$(( (freek*1024 - NEED) / 1073741824 ))
echo "start $(date '+%F %T') free_GiB=$((freek/1048576)) after_GiB=$after" > "$S"
[ "$after" -ge 25 ] || { echo "BLOCKED: after-download free $after GiB < 25 GiB floor" | tee -a "$S"; exit 3; }
mkdir -p "$D"
HF_HUB_DISABLE_TELEMETRY=1 "$V/bin/hf" download Qwen/Qwen3-4B-Instruct-2507 --revision "$REV" --local-dir "$D" >> "$S" 2>&1 || { echo FAIL >> "$S"; exit 1; }
( cd "$D" && ls -l && shasum -a 256 config.json model.safetensors.index.json model-0000*-of-00003.safetensors ) >> "$S"
echo "df after: $(df -g ~ | tail -1)" >> "$S"; echo DONE >> "$S"
