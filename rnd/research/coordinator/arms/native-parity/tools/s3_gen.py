#!/usr/bin/env python3
"""Step-3 generation (mini): POST each harness prompt string to a local llama-server /completion with the native Sampling defaults.
Usage: python3 -I s3_gen.py <prompts.jsonl> <out.jsonl> <port>. Resumes (skips (arm, id) already in out)."""
import json, sys, urllib.request, time
P, OUT, PORT = sys.argv[1], sys.argv[2], sys.argv[3]
done = set()
try:
    for l in open(OUT): r = json.loads(l); done.add((r["arm"], r["id"]))
except FileNotFoundError: pass
with open(OUT, "a") as o:
    for l in open(P):
        q = json.loads(l)
        if (q["arm"], q["id"]) in done: continue
        body = {"prompt": q["prompt"], "n_predict": q["maxTokens"], "temperature": 0.7, "top_k": 40, "top_p": 0.95, "min_p": 0.05,
                "repeat_penalty": 1.0, "seed": 42, "stop": ["<|im_end|>"], "cache_prompt": False}
        t = time.time()
        req = urllib.request.Request(f"http://127.0.0.1:{PORT}/completion", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        r = json.loads(urllib.request.urlopen(req, timeout=900).read())
        o.write(json.dumps({"arm": q["arm"], "id": q["id"], "persona": q["persona"], "style": q["style"], "maxTokens": q["maxTokens"],
                            "text": r["content"].strip(), "tokens_predicted": r.get("tokens_predicted"), "tokens_evaluated": r.get("tokens_evaluated"),
                            "stopped_limit": r.get("stop_type") == "limit" or r.get("stopped_limit"), "wall_s": round(time.time() - t, 2)}) + "\n"); o.flush()
