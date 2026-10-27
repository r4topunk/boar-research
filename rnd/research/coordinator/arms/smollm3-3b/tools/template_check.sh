#!/bin/bash
# SMOLLM3-3B onboarding (runs on the mini; 2 short generations): loads the GGUF in llama-server b11010 three times: A = embedded template + --reasoning off
# (the harness setting), B = HF chat_template.jinja via --chat-template-file + --reasoning off, C = embedded template, no reasoning flag (diagnostic: what
# the template does when nothing turns thinking off). Dumps /props chat_template, /apply-template renders of the first LITEPACKS prompt (kwargs none /
# enable_thinking false / true), /tokenize counts for every LITEPACKS prompt, and greedy 64-token generations on A with the engine's request shape
# (thinking_budget_tokens 256, no chat_template_kwargs) for support + thought-leak checks.
# Usage: template_check.sh <workdir with hf-chat_template.jinja + prompts-litepacks.jsonl> <gguf>
set -u; W=$1; G=$2; SRV=$HOME/boar/spikes/llama-b11010/build-cpu/bin/llama-server; cd $W
$SRV -m $G -t 2 -c 4096 -ngl 0 -np 1 --jinja --no-webui --reasoning off --host 127.0.0.1 --port 18831 > srvA.log 2>&1 & PA=$!
$SRV -m $G -t 2 -c 4096 -ngl 0 -np 1 --jinja --no-webui --reasoning off --chat-template-file $W/hf-chat_template.jinja --host 127.0.0.1 --port 18832 > srvB.log 2>&1 & PB=$!
$SRV -m $G -t 2 -c 4096 -ngl 0 -np 1 --jinja --no-webui --host 127.0.0.1 --port 18833 > srvC.log 2>&1 & PC=$!
trap 'kill $PA $PB $PC 2>/dev/null' EXIT
for p in 18831 18832 18833; do for i in $(seq 1 300); do curl -sf http://127.0.0.1:$p/health > /dev/null && break; sleep 0.5; done; done
/usr/bin/python3 - <<'PY'
import json, urllib.request
def post(p, path, body):
    r = urllib.request.Request(f"http://127.0.0.1:{p}{path}", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(r))
def get(p, path): return json.load(urllib.request.urlopen(f"http://127.0.0.1:{p}{path}"))
rows = [json.loads(l) for l in open("prompts-litepacks.jsonl")]
open("gguf-embedded_template.jinja", "w").write(get(18831, "/props")["chat_template"])
open("server-B_template.jinja", "w").write(get(18832, "/props")["chat_template"])
m = rows[0]["messages"]; out = {"itemId": rows[0]["itemId"]}
for name, kw in (("none", None), ("false", {"enable_thinking": False}), ("true", {"enable_thinking": True})):
    for p, tag in ((18831, "A_gguf"), (18832, "B_hf"), (18833, "C_gguf_noflag")):
        b = {"messages": m}
        if kw is not None: b["chat_template_kwargs"] = kw
        out[f"{tag}_{name}"] = post(p, "/apply-template", b)["prompt"]
json.dump(out, open("renders.json", "w"), indent=1)
for name in ("none", "false", "true"):
    for tag in ("A_gguf", "C_gguf_noflag"):
        pr = out[f"{tag}_{name}"]
        mode = "/no_think" if "Reasoning Mode: /no_think" in pr else "/think" if "Reasoning Mode: /think" in pr else "?"
        print(f"{tag} kwargs={name}: == B_hf: {pr == out['B_hf_'+name]}; mode {mode}; ends with empty think: {pr.endswith('<think>' + chr(10) + chr(10) + '</think>' + chr(10))}; "
              f"system closed by <|im_end|> before user: {'<|im_end|>' + chr(10) + '<|im_start|>user' in pr}; tail={pr[-50:]!r}")
toks = []
for r in rows:
    pr = post(18831, "/apply-template", {"messages": r["messages"]})["prompt"]
    n = len(post(18831, "/tokenize", {"content": pr, "add_special": False})["tokens"])
    toks.append((n, r["itemId"], r["nPredict"]))
toks.sort()
json.dump(toks, open("prompt-tokens.json", "w"))
print(f"prompts {len(toks)} tokens min {toks[0][0]} median {toks[len(toks)//2][0]} max {toks[-1][0]} ({toks[-1][1]}); max nPredict {max(t[2] for t in toks)}; max prompt+nPredict+256 {max(t[0]+t[2]+256 for t in toks)} vs -c 4096")
for k, r in enumerate(rows[:2]):
    g = post(18831, "/v1/chat/completions", {"messages": r["messages"], "max_tokens": 64, "temperature": 0, "top_k": 1, "seed": 42, "thinking_budget_tokens": 256})
    json.dump(g, open(f"gen{k+1}.json", "w"), indent=1)
    msg = g["choices"][0]["message"]; c = msg.get("content") or ""
    leak = any(t in c for t in ("<think>", "</think>"))
    print(f"gen{k+1} {r['itemId']}: finish {g['choices'][0]['finish_reason']} tokens {g['usage']['completion_tokens']} reasoning_content {len(msg.get('reasoning_content') or '')} chars; "
          f"think tags in content: {leak}; content={c[:220]!r}")
PY
grep -i -E "arch|n_ctx_train|chat template|thinking|reasoning|general.name|file type|model params|n_layer|error|unknown" srvA.log | head -25
