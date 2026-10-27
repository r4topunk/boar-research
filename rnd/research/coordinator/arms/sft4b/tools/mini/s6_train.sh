#!/bin/bash
# SFT4B stage 1 step 6 (mini): 600 iterations, batch 4, rank 16, scale 20, lr 1e-5, seed 42, mask_prompt, grad_checkpoint,
# save_every 200, eval every 100 on the full 84-example v2 hold-out (val_batches -1). Resume: bash s6_train.sh <adapter ckpt> <remaining iters>
set -u
K=<runner>/kiln/sft4b; M=$HOME/boar/shared-models/hf/Qwen3-4B-Instruct-2507-mlx8; O=$K/train
RES=${1:-}; IT=${2:-600}
cat > "$O/config.yaml" <<YAML
model: $M
train: true
data: $O/data
fine_tune_type: lora
num_layers: -1
batch_size: 4
iters: $IT
learning_rate: 1.0e-5
max_seq_length: 2048
mask_prompt: true
grad_checkpoint: true
seed: 42
steps_per_report: 10
steps_per_eval: 100
val_batches: -1
save_every: 200
adapter_path: $O/adapter
lora_parameters:
  rank: 16
  scale: 20.0
  dropout: 0.0
  keys: [self_attn.q_proj, self_attn.k_proj, self_attn.v_proj, self_attn.o_proj, mlp.gate_proj, mlp.up_proj, mlp.down_proj]
YAML
[ -n "$RES" ] && echo "resume_adapter_file: $RES" >> "$O/config.yaml"
bash "$K/lora_job.sh" "$O"
