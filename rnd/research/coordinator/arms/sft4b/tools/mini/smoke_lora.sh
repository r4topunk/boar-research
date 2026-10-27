#!/bin/bash
# SFT4B stage 0 (mini): 50-step LoRA smoke with the declared recipe (rank 16, all linear layers of all 36 layers, lr 1e-5,
# max seq 2048, seed 42; prompt masked; batch 4) on the first 64 train examples (valid = 16 hold-out examples, loss only).
# Run on the mini after download_base.sh: bash smoke_lora.sh  -> <runner>/kiln/sft4b/smoke/{log, adapter}
set -u
K=<runner>/kiln/sft4b; M=<runner>/shared-models/hf/Qwen3-4B-Instruct-2507; O=$K/smoke; mkdir -p "$O/data"
head -64 "$K/data/train.jsonl" > "$O/data/train.jsonl"; head -16 "$K/data/holdout.jsonl" > "$O/data/valid.jsonl"
cat > "$O/config.yaml" <<YAML
model: $M
train: true
data: $O/data
fine_tune_type: lora
num_layers: -1
batch_size: 4
iters: 50
learning_rate: 1.0e-5
max_seq_length: 2048
mask_prompt: true
seed: 42
steps_per_report: 5
steps_per_eval: 25
val_batches: 4
save_every: 50
adapter_path: $O/adapter
lora_parameters:
  rank: 16
  scale: 20.0
  dropout: 0.0
  keys: [self_attn.q_proj, self_attn.k_proj, self_attn.v_proj, self_attn.o_proj, mlp.gate_proj, mlp.up_proj, mlp.down_proj]
YAML
/usr/bin/time -l "$K/.venv/bin/python" -m mlx_lm lora -c "$O/config.yaml" > "$O/log" 2>&1; echo "rc=$?" >> "$O/log"
