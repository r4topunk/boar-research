#!/usr/bin/env python3
"""Make an aLoRA copy of a LoRA GGUF: identical tensors and KV + adapter.alora.invocation_tokens (uint32 array).
Usage (mini): python3 mk_alora.py <llama.cpp dir> <in.gguf> <out.gguf> <comma-separated token ids>
Uses llama.cpp gguf-py's gguf_new_metadata.copy_with_new_metadata (no tensor changes)."""
import sys
from pathlib import Path
L, src, dst, ids = sys.argv[1], sys.argv[2], sys.argv[3], [int(x) for x in sys.argv[4].split(",")]
sys.path.insert(0, f"{L}/gguf-py"); sys.path.insert(0, f"{L}/gguf-py/gguf/scripts")
import types
sys.modules.setdefault('yaml', types.ModuleType('yaml'))  # gguf.metadata imports yaml only for model-card parsing (unused here); stdlib-only mini python
_t = types.ModuleType('tqdm')
class _Q:
    def __init__(self, it=None, *a, **k): self.it = it
    def __iter__(self): return iter(self.it)
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def update(self, *a, **k): pass
    def close(self): pass
_t.tqdm = _Q; sys.modules.setdefault('tqdm', _t)  # progress bar only
import gguf
import gguf_new_metadata as gnm

r = gguf.GGUFReader(src, "r")
arch = gnm.get_field_data(r, gguf.Keys.General.ARCHITECTURE)
w = gguf.GGUFWriter(dst, arch=arch, endianess=r.endianess)
al = gnm.get_field_data(r, gguf.Keys.General.ALIGNMENT)
if al is not None: w.data_alignment = al
new = {"adapter.alora.invocation_tokens": gnm.MetadataDetails(gguf.GGUFValueType.ARRAY, ids, sub_type=gguf.GGUFValueType.UINT32)}
_akv = w.add_key_value  # copy_with_new_metadata adds new keys without sub_type (ints would default to INT32); force UINT32
w.add_key_value = lambda k, v, t, sub_type=None: _akv(k, v, t, sub_type=gguf.GGUFValueType.UINT32 if k == "adapter.alora.invocation_tokens" else sub_type)
gnm.copy_with_new_metadata(r, w, new, [])
r2 = gguf.GGUFReader(dst, "r")
f = r2.get_field("adapter.alora.invocation_tokens")
print("written", dst, "invocation", f.contents(), "elem type", f.types, "tensors", len(r2.tensors), "vs", len(r.tensors))
