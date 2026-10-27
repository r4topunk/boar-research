# SFT4B stage 1 step 7: MLX LoRA adapter -> HF PEFT layout for llama.cpp convert_lora_to_gguf.py.
# MLX: y += scale * (x @ lora_a) @ lora_b, lora_a (in x r), lora_b (r x out)  =>  dW (out x in) = scale * lora_b^T @ lora_a^T
# PEFT: dW = (alpha/r) * B @ A with A = lora_a^T (r x in), B = lora_b^T (out x r); alpha = scale * r so alpha/r = MLX scale.
# usage: python mlx2peft.py <mlx adapter dir> <out peft dir>
import json, sys, pathlib
import mlx.core as mx, numpy as np
from safetensors.numpy import save_file
A, O = map(pathlib.Path, sys.argv[1:3]); O.mkdir(parents=True, exist_ok=True)
cfg = json.loads((A / "adapter_config.json").read_text()); lp = cfg["lora_parameters"]
r, scale = int(lp["rank"]), float(lp["scale"])
w = mx.load(str(A / "adapters.safetensors")); out = {}; mods = set()
for k, v in w.items():
    v = np.array(v.astype(mx.float32))
    base = k.rsplit(".", 1)[0]  # model.layers.N.self_attn.q_proj
    mods.add(base.rsplit(".", 1)[1])
    if k.endswith(".lora_a"): out[f"base_model.model.{base}.lora_A.weight"] = np.ascontiguousarray(v.T)
    elif k.endswith(".lora_b"): out[f"base_model.model.{base}.lora_B.weight"] = np.ascontiguousarray(v.T)
    else: raise SystemExit(f"unexpected key {k}")
save_file(out, str(O / "adapter_model.safetensors"))
(O / "adapter_config.json").write_text(json.dumps({"peft_type": "LORA", "r": r, "lora_alpha": scale * r, "lora_dropout": 0.0, "bias": "none",
    "target_modules": sorted(mods), "base_model_name_or_path": "Qwen/Qwen3-4B-Instruct-2507", "task_type": "CAUSAL_LM"}, indent=1))
print(json.dumps({"tensors": len(out), "pairs": len(out) // 2, "r": r, "alpha": scale * r, "modules": sorted(mods)}))
