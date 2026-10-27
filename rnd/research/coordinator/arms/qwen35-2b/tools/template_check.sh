#!/bin/bash
# QWEN35-2B onboarding (runs on the mini, 0 generation): loads the GGUF twice in llama-server b11010 (embedded template vs the HF chat_template.jinja
# via --chat-template-file), dumps /props chat_template, /apply-template renders of the first prompt (kwargs none / enable_thinking false / true),
# and /tokenize counts for every LITEPACKS prompt in prompts.jsonl. Usage: template_check.sh <workdir with hf-chat_template.jinja + prompts-litepacks.jsonl> <gguf>
set -u; W=$1; G=$2; SRV=$HOME/boar/spikes/llama-b11010/build-cpu/bin/llama-server; cd $W
$SRV -m $G -t 2 -c 4096 -ngl 0 -np 1 --jinja --no-webui --reasoning off --host 127.0.0.1 --port 18811 > srvA.log 2>&1 & PA=$!
$SRV -m $G -t 2 -c 4096 -ngl 0 -np 1 --jinja --no-webui --reasoning off --chat-template-file $W/hf-chat_template.jinja --host 127.0.0.1 --port 18812 > srvB.log 2>&1 & PB=$!
trap 'kill $PA $PB 2>/dev/null' EXIT
for p in 18811 18812; do for i in $(seq 1 300); do curl -sf http://127.0.0.1:$p/health > /dev/null && break; sleep 0.5; done; done
/usr/bin/python3 - <<'PY'
import json, urllib.request
def post(p, path, body):
    r = urllib.request.Request(f"http://127.0.0.1:{p}{path}", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(r))
def get(p, path): return json.load(urllib.request.urlopen(f"http://127.0.0.1:{p}{path}"))
rows = [json.loads(l) for l in open("prompts-litepacks.jsonl")]
open("gguf-embedded_template.jinja", "w").write(get(18811, "/props")["chat_template"])
open("server-B_template.jinja", "w").write(get(18812, "/props")["chat_template"])
m = rows[0]["messages"]; out = {"itemId": rows[0]["itemId"]}
for name, kw in (("none", None), ("false", {"enable_thinking": False}), ("true", {"enable_thinking": True})):
    for p, tag in ((18811, "gguf"), (18812, "hf")):
        b = {"messages": m}; 
        if kw is not None: b["chat_template_kwargs"] = kw
        out[f"{tag}_{name}"] = post(p, "/apply-template", b)["prompt"]
json.dump(out, open("renders.json", "w"), indent=1)
for name in ("none", "false", "true"):
    print(f"render kwargs={name}: gguf == hf: {out['gguf_'+name] == out['hf_'+name]}; tail={out['gguf_'+name][-40:]!r}")
toks = []
for r in rows:
    pr = post(18811, "/apply-template", {"messages": r["messages"], "chat_template_kwargs": {"enable_thinking": False}})["prompt"]
    n = len(post(18811, "/tokenize", {"content": pr, "add_special": False})["tokens"])
    toks.append((n, r["itemId"], r["nPredict"]))
toks.sort()
json.dump(toks, open("prompt-tokens.json", "w"))
print(f"prompts {len(toks)} tokens min {toks[0][0]} median {toks[len(toks)//2][0]} max {toks[-1][0]} ({toks[-1][1]}); max nPredict {max(t[2] for t in toks)}; max prompt+nPredict {max(t[0]+t[2] for t in toks)} vs -c 4096")
PY
grep -i -E "arch|n_ctx_train|chat template|thinking|reasoning|general.name|file type|model params|n_layer" srvA.log | head -20
