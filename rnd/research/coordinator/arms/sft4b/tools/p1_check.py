# SFT4B parity P1 (conversion math): for 6 tensors (q, k, down in layers 0, 17, 35) compare the MLX weight delta
# scale * lora_b^T @ lora_a^T with the GGUF LoRA delta alpha/r * B @ A (read with gguf-py). Gate: max rel diff <= 2e-3,
# rel diff = max|dG - dM| / max|dM| per tensor. usage: python p1_check.py <mlx adapter dir> <lora.gguf>  -> JSON, exit 0 iff PASS
import json, sys, pathlib
import mlx.core as mx, numpy as np
from gguf import GGUFReader
A, G = pathlib.Path(sys.argv[1]), sys.argv[2]
lp = json.loads((A / "adapter_config.json").read_text())["lora_parameters"]; scale = float(lp["scale"])
w = mx.load(str(A / "adapters.safetensors"))
rd = GGUFReader(G); t = {x.name: x for x in rd.tensors}
alpha = float(rd.fields["adapter.lora.alpha"].parts[-1][0])
names = {"self_attn.q_proj": "attn_q", "self_attn.k_proj": "attn_k", "mlp.down_proj": "ffn_down"}
res = []; n_lora = sum(1 for k in t if k.endswith(".lora_a"))
for L in (0, 17, 35):
    for hf, gg in names.items():
        a = np.array(w[f"model.layers.{L}.{hf}.lora_a"].astype(mx.float32)); b = np.array(w[f"model.layers.{L}.{hf}.lora_b"].astype(mx.float32))
        dM = scale * (b.T @ a.T)
        ga = np.array(t[f"blk.{L}.{gg}.weight.lora_a"].data, dtype=np.float32); gb = np.array(t[f"blk.{L}.{gg}.weight.lora_b"].data, dtype=np.float32)
        r = ga.shape[0]; dG = (alpha / r) * (gb @ ga)
        rel = float(np.abs(dG - dM).max() / np.abs(dM).max()); fro = float(np.linalg.norm(dG - dM) / np.linalg.norm(dM))
        res.append({"layer": L, "tensor": gg, "shape": list(dM.shape), "rel_max": rel, "rel_fro": fro, "max_abs_dM": float(np.abs(dM).max())})
out = {"alpha": alpha, "mlx_scale": scale, "gguf_lora_pairs": n_lora, "tensors": res, "max_rel": max(x["rel_max"] for x in res)}
out["PASS"] = out["max_rel"] <= 2e-3 and all(x["max_abs_dM"] > 0 for x in res)
print(json.dumps(out, indent=1)); sys.exit(0 if out["PASS"] else 2)
