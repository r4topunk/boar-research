#!/usr/bin/env python3
"""GATELAT mini-side runner (stdlib only). Usage: python3 -I mini_gatelat.py <job dir> <mode>
modes:
  tok    tokenize A_prompt, A, V1, V2, V3 and the aLoRA invocation; write tok.jsonl (counts, common token prefix with A).
  plain  server = base + plain LoRA: V1f (V1 string) and V2, /completion cache_prompt false -> plain.jsonl
  hyb    server = base + aLoRA LoRA: per item, prefill A (cache_prompt true, n_predict 1, adapter inactive: no invocation),
         then the gate request V1 (cache_prompt true) -> V1h; prefill A again, then V3 -> V3h. -> hyb.jsonl
Scoring = arms/gate17/tools/mini_gate.py: n_predict 1, temperature 0, n_probs 50, P(FAIL) = pF / (pP + pF) by first-token ids of PASS / FAIL."""
import json, math, sys, time, urllib.request

J, MODE = sys.argv[1], sys.argv[2]
U = f"http://127.0.0.1:{open(f'{J}/PORT').read().strip()}"
INVOCATION = "<|im_start|>user\nYou are a groundedness guardrail"


def post(path, body):
    r = urllib.request.Request(U + path, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=900) as f:
        return json.loads(f.read())


def tok(s):
    return post("/tokenize", {"content": s, "add_special": True})["tokens"]


def cp(a, b):
    n = 0
    for x, y in zip(a, b):
        if x != y: break
        n += 1
    return n


ids = {w: tok(w) for w in ("PASS", "FAIL")}
pid, fid = ids["PASS"][0], ids["FAIL"][0]


def gate(prompt, cache):
    t0 = time.time()
    r = post("/completion", {"prompt": prompt, "n_predict": 1, "temperature": 0, "n_probs": 50, "cache_prompt": cache})
    wall = (time.time() - t0) * 1000
    c0 = r["completion_probabilities"][0]
    probs = c0["top_logprobs"] if "top_logprobs" in c0 else c0["probs"]
    byid = {p["id"]: (math.exp(p["logprob"]) if "logprob" in p else p["prob"]) for p in probs}
    lo = min(byid.values()); pP, pF = byid.get(pid), byid.get(fid)
    miss = [n for n, v in (("PASS", pP), ("FAIL", pF)) if v is None]
    pP = lo if pP is None else pP; pF = lo if pF is None else pF
    tm = r.get("timings", {})
    return {"tok": r.get("content"), "P_FAIL": pF / (pP + pF), "missing": miss, "prompt_n": tm.get("prompt_n"),
            "cache_n": tm.get("cache_n"), "prompt_ms": tm.get("prompt_ms"), "wall_ms": round(wall, 1)}


def prefill(prompt):
    t0 = time.time()
    r = post("/completion", {"prompt": prompt, "n_predict": 1, "temperature": 0, "cache_prompt": True})
    tm = r.get("timings", {})
    return {"prompt_n": tm.get("prompt_n"), "cache_n": tm.get("cache_n"), "prompt_ms": tm.get("prompt_ms"), "wall_ms": round((time.time() - t0) * 1000, 1)}


rows = [json.loads(l) for l in open(f"{J}/inputs.jsonl")]
with open(f"{J}/{MODE}.jsonl", "w") as out:
    if MODE == "tok":
        inv = tok(INVOCATION)
        out.write(json.dumps({"key": "_meta", "invocation_tokens": inv, "PASS": ids["PASS"], "FAIL": ids["FAIL"]}) + "\n")
        for r in rows:
            T = {k: tok(r[k]) for k in ("A_prompt", "A", "V1", "V2", "V3")}
            o = {"key": r["key"], **{f"n_{k}": len(v) for k, v in T.items()},
                 "cp_V1_A": cp(T["V1"], T["A"]), "cp_V2_A": cp(T["V2"], T["A"]), "cp_V3_A": cp(T["V3"], T["A"]),
                 "A_is_prefix_V1": T["V1"][:len(T["A"])] == T["A"]}
            for k in ("V1", "V3"):
                s = T[k]; o[f"inv_{k}"] = any(s[i:i + len(inv)] == inv for i in range(len(s) - len(inv), -1, -1))
            out.write(json.dumps(o) + "\n"); out.flush()
    elif MODE == "plain":
        for r in rows:
            out.write(json.dumps({"key": r["key"], "V1f": gate(r["V1"], False), "V2": gate(r["V2"], False)}) + "\n"); out.flush()
    elif MODE == "hyb":
        for r in rows:
            a1 = prefill(r["A"]); v1 = gate(r["V1"], True)
            a2 = prefill(r["A"]); v3 = gate(r["V3"], True)
            out.write(json.dumps({"key": r["key"], "A1": a1, "V1h": v1, "A2": a2, "V3h": v3}) + "\n"); out.flush()
print("done", MODE)
