#!/bin/bash
# JAN-V1-EDGE onboarding (runs on the mini; 1 short generation): loads the GGUF twice in llama-server b11010 (A = embedded template, B = the HF
# chat_template.jinja via --chat-template-file), dumps /props chat_template, /apply-template renders of the first LITEPACKS prompt (kwargs none /
# enable_thinking false / true), /tokenize counts for every LITEPACKS prompt, and one 64-token greedy generation on A (support + thought-leak check).
# JAN: + gen2 engine-like (thinking_budget_tokens 256, no kwarg) and gen3 (enable_thinking false), 200 tokens greedy.
# Usage: template_check.sh <workdir with hf-chat_template.jinja + prompts-litepacks.jsonl> <gguf>
set -u; W=$1; G=$2; SRV=$HOME/boar/spikes/llama-b11010/build-cpu/bin/llama-server; cd $W
$SRV -m $G -t 2 -c 4096 -ngl 0 -np 1 --jinja --no-webui --reasoning off --host 127.0.0.1 --port 18831 > srvA.log 2>&1 & PA=$!
$SRV -m $G -t 2 -c 4096 -ngl 0 -np 1 --jinja --no-webui --reasoning off --chat-template-file $W/hf-chat_template.jinja --host 127.0.0.1 --port 18832 > srvB.log 2>&1 & PB=$!
trap 'kill $PA $PB 2>/dev/null' EXIT
for p in 18831 18832; do for i in $(seq 1 300); do curl -sf http://127.0.0.1:$p/health > /dev/null && break; sleep 0.5; done; done
/usr/bin/python3 - <<'PY'
import json, urllib.request
def post(p, path, body):
    r = urllib.request.Request(f"http://127.0.0.1:{p}{path}", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(r))
def get(p, path): return json.load(urllib.request.urlopen(f"http://127.0.0.1:{p}{path}"))
rows = [json.loads(l) for l in open("prompts-litepacks.jsonl")]
open("gguf-embedded_template.jinja", "w").write(get(18831, "/props")["chat_template"])
open("server-B_template.jinja", "w").write(get(18832, "/props")["chat_template"])
ET = '<think>' + chr(10)*2 + '</think>' + chr(10)*2
m = rows[0]["messages"]; out = {"itemId": rows[0]["itemId"]}
for name, kw in (("none", None), ("false", {"enable_thinking": False}), ("true", {"enable_thinking": True})):
    for p, tag in ((18831, "gguf"), (18832, "hf")):
        b = {"messages": m}
        if kw is not None: b["chat_template_kwargs"] = kw
        out[f"{tag}_{name}"] = post(p, "/apply-template", b)["prompt"]
json.dump(out, open("renders.json", "w"), indent=1)
for name in ("none", "false", "true"):
    pr = out['gguf_'+name]
    print(f"render kwargs={name}: gguf == hf: {pr == out['hf_'+name]}; ends with empty think: {pr.endswith(ET)}; head={pr[:60]!r}; tail={pr[-60:]!r}")
toks = []
for r in rows:
    pr = post(18831, "/apply-template", {"messages": r["messages"]})["prompt"]
    n = len(post(18831, "/tokenize", {"content": pr, "add_special": False})["tokens"])
    toks.append((n, r["itemId"], r["nPredict"]))
toks.sort()
json.dump(toks, open("prompt-tokens.json", "w"))
print(f"prompts {len(toks)} tokens min {toks[0][0]} median {toks[len(toks)//2][0]} max {toks[-1][0]} ({toks[-1][1]}); max nPredict {max(t[2] for t in toks)}; max prompt+nPredict {max(t[0]+t[2] for t in toks)} vs -c 4096")
g = post(18831, "/v1/chat/completions", {"messages": m, "max_tokens": 64, "temperature": 0, "top_k": 1, "seed": 42})
json.dump(g, open("gen1.json", "w"), indent=1)
msg = g["choices"][0]["message"]; c = msg.get("content") or ""
leak = any(t in c for t in ('<think>', '</think>'))
print(f"gen1: finish {g['choices'][0]['finish_reason']} tokens {g['usage']['completion_tokens']} reasoning_content {len(msg.get('reasoning_content') or '')} chars; "
      f"thought markers in content: {leak}; content={c[:200]!r}")
for nm, extra in (("gen2-engine-like", {"thinking_budget_tokens": 256}), ("gen3-kwarg-false", {"chat_template_kwargs": {"enable_thinking": False}})):
    g = post(18831, "/v1/chat/completions", {"messages": m, "max_tokens": 200, "temperature": 0, "top_k": 1, "seed": 42, **extra})
    json.dump(g, open(nm + ".json", "w"), indent=1)
    msg = g["choices"][0]["message"]; c = msg.get("content") or ""
    print(f"{nm}: finish {g['choices'][0]['finish_reason']} tokens {g['usage']['completion_tokens']} reasoning_content {len(msg.get('reasoning_content') or '')} chars; think markers {any(t in c for t in ('<think>', '</think>'))}; content={c[:160]!r}")
PY
grep -i -E "arch|n_ctx_train|chat template|thinking|reasoning|general.name|file type|model params|n_layer|error|unknown" srvA.log | head -25
