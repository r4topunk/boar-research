#!/usr/bin/env python3
"""GATE17 mini-side scorer (stdlib only). Usage: python3 -I mini_gate.py <job dir>
<job dir>/inputs.jsonl rows {key, prompt} (prompt = the card's chat-rendered string, Qwen3 template, enable_thinking=False, rendered on the MacBook).
Assumes a llama-server (base Qwen3-1.7B Q4_K_M + --lora gate17-lora-f16.gguf) on the port in <job dir>/PORT.
Per row: POST /completion {prompt, n_predict 1, temperature 0, n_probs 50, cache_prompt false}; reads the first-token probability list
(raw softmax over the full vocabulary, post_sampling_probs off) and records p(PASS), p(FAIL) by the FIRST token id of tokenize("PASS") /
tokenize("FAIL") (as the card: tok.encode("PASS")[0]). A missing token gets the smallest listed probability as an upper bound and a flag.
P(FAIL) = pF / (pP + pF) (= the card's 2-way softmax over the two logits). Writes <job dir>/outputs.jsonl."""
import json, sys, time, urllib.request

J = sys.argv[1]
port = open(f"{J}/PORT").read().strip()
U = f"http://127.0.0.1:{port}"


def post(path, body):
    r = urllib.request.Request(U + path, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=600) as f:
        return json.loads(f.read())


ids = {w: post("/tokenize", {"content": w})["tokens"] for w in ("PASS", "FAIL")}
pid, fid = ids["PASS"][0], ids["FAIL"][0]
with open(f"{J}/outputs.jsonl", "w") as out:
    for l in open(f"{J}/inputs.jsonl"):
        row = json.loads(l)
        t0 = time.time()
        r = post("/completion", {"prompt": row["prompt"], "n_predict": 1, "temperature": 0, "n_probs": 50, "cache_prompt": False})
        wall = (time.time() - t0) * 1000
        probs = r["completion_probabilities"][0]["top_logprobs"] if "top_logprobs" in r["completion_probabilities"][0] else r["completion_probabilities"][0]["probs"]
        import math
        byid = {}
        for p in probs:
            pr = math.exp(p["logprob"]) if "logprob" in p else p["prob"]
            byid[p["id"]] = pr
        lo = min(byid.values())
        pP, pF = byid.get(pid), byid.get(fid)
        miss = [n for n, v in (("PASS", pP), ("FAIL", pF)) if v is None]
        pP = lo if pP is None else pP; pF = lo if pF is None else pF
        tm = r.get("timings", {})
        out.write(json.dumps({"key": row["key"], "tok": r.get("content"), "pPASS": pP, "pFAIL": pF, "P_FAIL": pF / (pP + pF), "missing": miss,
                              "token_ids": ids, "prompt_n": tm.get("prompt_n"), "prompt_ms": tm.get("prompt_ms"),
                              "predicted_ms": tm.get("predicted_ms"), "wall_ms": round(wall, 1)}) + "\n")
        out.flush()
print("done")
