#!/bin/bash
# MINISTRAL3-3B onboarding (runs on the mini, 0 generation). Loads the GGUF twice in llama-server b11010: A = GGUF-embedded template,
# B = the HF chat_template.jinja (mistralai/Ministral-3-3B-Instruct-2512 @ b35d4dfe) via --chat-template-file. Same flags as the adapter
# (--jinja --reasoning off --reasoning-format deepseek, -c 4096). Renders the first LITEPACKS prompt (system + user) through /apply-template with
# kwargs absent and with the engine's enable_thinking:false; checks BOS (rendered prefix + /tokenize add_special true vs false) and tokenizes every
# LITEPACKS prompt for the context fit. No mmproj is loaded.
# Usage: template_check.sh <workdir with hf-chat_template.jinja + prompts-litepacks.jsonl> <gguf>
set -u; W=$1; G=$2; SRV=$HOME/boar/spikes/llama-b11010/build-cpu/bin/llama-server; cd $W
COMMON="-t 2 -c 4096 -ngl 0 -np 1 --jinja --no-webui --reasoning off --reasoning-format deepseek --host 127.0.0.1"
$SRV -m $G $COMMON --port 18821 > srvA.log 2>&1 & PA=$!
$SRV -m $G $COMMON --chat-template-file $W/hf-chat_template.jinja --port 18822 > srvB.log 2>&1 & PB=$!
trap 'kill $PA $PB 2>/dev/null' EXIT
for p in 18821 18822; do for i in $(seq 1 300); do curl -sf http://127.0.0.1:$p/health > /dev/null && break; sleep 0.5; done; done
/usr/bin/python3 -I - <<'PY'
import json, urllib.request
def post(p, path, body):
    r = urllib.request.Request(f"http://127.0.0.1:{p}{path}", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(r))
def get(p, path): return json.load(urllib.request.urlopen(f"http://127.0.0.1:{p}{path}"))
rows = [json.loads(l) for l in open("prompts-litepacks.jsonl")]
pa = get(18821, "/props"); open("gguf-embedded_template.jinja", "w").write(pa["chat_template"])
open("server-B_template.jinja", "w").write(get(18822, "/props")["chat_template"])
m = rows[0]["messages"]; out = {"itemId": rows[0]["itemId"]}
for name, kw in (("none", None), ("false", {"enable_thinking": False})):
    for p, tag in ((18821, "gguf"), (18822, "hf")):
        b = {"messages": m}
        if kw is not None: b["chat_template_kwargs"] = kw
        out[f"{tag}_{name}"] = post(p, "/apply-template", b)["prompt"]
# no-system variant: does the template inject its default system prompt? (the engine always sends one; informational)
out["gguf_nosys"] = post(18821, "/apply-template", {"messages": [m[-1]]})["prompt"][:200]
json.dump(out, open("renders.json", "w"), indent=1)
for name in ("none", "false"):
    print(f"render kwargs={name}: gguf == hf: {out['gguf_'+name] == out['hf_'+name]}; head={out['gguf_'+name][:60]!r}; tail={out['gguf_'+name][-60:]!r}")
pr = out["gguf_false"]
t_sp = post(18821, "/tokenize", {"content": pr, "add_special": True, "with_pieces": True})["tokens"]
t_ns = post(18821, "/tokenize", {"content": pr, "add_special": False, "with_pieces": True})["tokens"]
print("tokens add_special=True first3:", t_sp[:3], " add_special=False first3:", t_ns[:3])
print("system text present inside [SYSTEM_PROMPT]:", "[SYSTEM_PROMPT]" in pr and m[0]["content"][:40] in pr.split("[/SYSTEM_PROMPT]")[0])
toks = []
for r in rows:
    p2 = post(18821, "/apply-template", {"messages": r["messages"], "chat_template_kwargs": {"enable_thinking": False}})["prompt"]
    n = len(post(18821, "/tokenize", {"content": p2, "add_special": False})["tokens"])
    toks.append((n, r["itemId"], r["nPredict"]))
toks.sort(); json.dump(toks, open("prompt-tokens.json", "w"))
print(f"prompts {len(toks)} tokens min {toks[0][0]} median {toks[len(toks)//2][0]} max {toks[-1][0]} ({toks[-1][1]}); max nPredict {max(t[2] for t in toks)}; max prompt+nPredict {max(t[0]+t[2] for t in toks)} vs -c 4096")
PY
grep -i -E "arch|n_ctx_train|chat template|general.name|file type|model params|n_layer|BOS|add_bos|warn" srvA.log | head -30
