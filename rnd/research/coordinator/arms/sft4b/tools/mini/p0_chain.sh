#!/bin/bash
# SFT4B parity chain (mini), sequential light jobs: P0 determinism baseline (no LoRA, 2 fresh server runs x 10 prompts),
# export-path test on the smoke adapter (steps 7-8 + P1), then P0 identity with that LoRA at scale 0 (10 prompts).
set -u
K=<runner>/kiln/sft4b; cd "$K"
bash p_server.sh p0-base-a 10
bash p_server.sh p0-base-b 10
bash s78_export.sh "$K/smoke1/adapter" "$K/smoke1/export"
bash p_server.sh p0-smoke-scale0 10 --lora-scaled "$K/smoke1/export/qwen3-4b-instruct-2507-sft4b-lora-f16.gguf:0"
echo CHAIN DONE > "$K/parity/chain.status"
