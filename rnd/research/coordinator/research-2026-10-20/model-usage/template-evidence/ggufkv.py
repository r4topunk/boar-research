# Minimal GGUF metadata reader (stdlib only). Usage: ggufkv.py file.gguf
import struct, sys, json
f = open(sys.argv[1], "rb")
def rd(fmt): return struct.unpack("<"+fmt, f.read(struct.calcsize("<"+fmt)))[0]
def rstr(): n = rd("Q"); return f.read(n).decode("utf-8", "replace")
SC = {0:"B",1:"b",2:"H",3:"h",4:"I",5:"i",6:"f",7:"?",10:"Q",11:"q",12:"d"}
def rval(t):
    if t in SC: return rd(SC[t])
    if t == 8: return rstr()
    if t == 9:
        et = rd("I"); n = rd("Q"); return [rval(et) for _ in range(n)]
    raise ValueError(t)
assert f.read(4) == b"GGUF"; ver = rd("I"); nt = rd("Q"); nkv = rd("Q")
kv = {}
for _ in range(nkv):
    k = rstr(); t = rd("I"); kv[k] = rval(t)
toks = kv.get("tokenizer.ggml.tokens", []); tt = kv.get("tokenizer.ggml.token_type", [])
out = {k: v for k, v in kv.items() if not k.startswith("tokenizer.ggml.") or k in ("tokenizer.ggml.bos_token_id","tokenizer.ggml.eos_token_id","tokenizer.ggml.eot_token_id","tokenizer.ggml.eog_token_ids","tokenizer.ggml.padding_token_id","tokenizer.ggml.add_bos_token","tokenizer.ggml.pre","tokenizer.ggml.model")}
out["n_tokens"] = len(toks)
out["special_tail"] = [(i, toks[i], tt[i] if i < len(tt) else None) for i in range(151640, min(len(toks), 151700))]
tpl = out.pop("tokenizer.chat_template", "")
json.dump(out, sys.stdout, indent=0, default=str)
sys.stdout.write("\n===TEMPLATE===\n" + tpl)
