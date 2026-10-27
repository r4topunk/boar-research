#!/bin/bash
# SFT4B P2 behaviour arms (mini), sequential: G0 (claim Q4_K_M), G1 (+ GGUF LoRA), M0 (MLX 8-bit base), M1 (+ MLX adapter), 20 prompts each, then p_compare p2.
# usage (nohup): bash p2_chain.sh <tag> <mlx adapter dir> <lora gguf>   -> $K/parity/<tag>-{G0,G1,M0,M1}.jsonl, <tag>-p2.json
set -u
K=<runner>/kiln/sft4b; M=$HOME/boar/shared-models/hf/Qwen3-4B-Instruct-2507-mlx8; T=$1; A=$2; G=$3; O=$K/parity; cd "$K"
bash p_server.sh "$T-G0" 20
bash p_server.sh "$T-G1" 20 --lora "$G"
.venv/bin/python p_gen.py mlx "$M" - "$O/parity-prompts.jsonl" 20 "$O/$T-M0.jsonl" > "$O/$T-M0.log" 2>&1
.venv/bin/python p_gen.py mlx "$M" "$A" "$O/parity-prompts.jsonl" 20 "$O/$T-M1.jsonl" > "$O/$T-M1.log" 2>&1
.venv/bin/python p_compare.py p2 "$O/$T-M0.jsonl" "$O/$T-M1.jsonl" "$O/$T-G0.jsonl" "$O/$T-G1.jsonl" "$O/$T-M0.jsonl" > "$O/$T-p2.json" 2>&1
echo "P2 rc=$?" > "$O/$T-p2.status"
