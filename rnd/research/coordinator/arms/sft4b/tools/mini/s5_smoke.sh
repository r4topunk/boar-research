#!/bin/bash
# SFT4B stage 1 step 5 (mini): 50-step smoke on the 8-bit base (or $1 = alternate model dir for the declared 4-bit fallback),
# grad_checkpoint on, recipe as declared; 64 train / 16 hold-out (v2) examples. Then: bash lora_job.sh $K/smoke1
set -u
K=<runner>/kiln/sft4b; M=${1:-$HOME/boar/shared-models/hf/Qwen3-4B-Instruct-2507-mlx8}; O=$K/smoke1; mkdir -p "$O/data"
head -64 "$K/train/data/train.jsonl" > "$O/data/train.jsonl"; head -16 "$K/train/data/valid.jsonl" > "$O/data/valid.jsonl"
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
grad_checkpoint: true
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
bash "$K/lora_job.sh" "$O"
