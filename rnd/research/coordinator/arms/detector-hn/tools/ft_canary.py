#!/usr/bin/env python3
"""DETECTOR-FT canary (Forge contract, sonar detector-canary.v3b.json): reference = MacBook b11010 4bc272f llama-server (mean pooling,
-np 1 -c/-b/-ub 512, embd_normalize -1) on the candidate GGUF; check = the mini build (b11010 build-cpu 4bc272f, tunnel :18301) must pass
cos >= .99, |l2 - ref|/ref <= .02, |p - ref p| <= .05 on both strings; wrong pooling (last :18312, cls :18313) must FAIL.
usage: ft_canary.py <head.json> <gguf sha256> <out canary.json> <out check.json>"""
import json, sys, os, numpy as np, requests
sys.path.insert(0, os.path.dirname(__file__)); import dlib
ref = json.load(open(dlib.SONAR + "/detector-canary.v3b.json")); T = ref["thresholds"]; H = dlib.load_head(sys.argv[1])
def emb(port, text):
    j = requests.post(f"http://127.0.0.1:{port}/embedding", json={"content": text, "embd_normalize": -1}, timeout=60).json()
    e = j[0]["embedding"] if isinstance(j, list) else j["embedding"]; return np.array(e[0] if isinstance(e[0], list) else e, dtype=np.float64)
def tokn(port, text): return len(requests.post(f"http://127.0.0.1:{port}/tokenize", json={"content": text, "add_special": False}).json()["tokens"])
items = []
for it in ref["items"]:
    t = dlib.detector_text([it["text"]]); v = emb(18311, t)
    items.append({"text": it["text"], "tokens": tokn(18311, t), "p": round(float(dlib.head_p(H, v[None])[0]), 4), "l2": round(float(np.linalg.norm(v)), 4), "vec": [round(float(x), 6) for x in v]})
can = {"about": "DETECTOR-FT candidate canary (NOT shipped). Same contract as detector-canary.v3b.json; reference = MacBook llama.cpp b11010 4bc272f llama-server --embeddings --pooling mean -np 1 -c 512 -b 512 -ub 512, embd_normalize -1.",
       "model_sha256": sys.argv[2], "head_sha256": __import__("hashlib").sha256(open(sys.argv[1], "rb").read()).hexdigest(), "thresholds": T, "items": items}
json.dump(can, open(sys.argv[3], "w"))
chk = {}
for name, port in (("mini_mean", 18301), ("mb_last_pooling", 18312), ("mb_cls_pooling", 18313)):
    rows = []
    for it in items:
        v = emb(port, dlib.detector_text([it["text"]])); rv = np.array(it["vec"]); cos = float(v @ rv / np.linalg.norm(v) / np.linalg.norm(rv))
        l2 = float(np.linalg.norm(v)); p = float(dlib.head_p(H, v[None])[0])
        ok = cos >= T["cos_min"] and abs(l2 - it["l2"]) / it["l2"] <= T["l2_rel_max"] and abs(p - it["p"]) <= T["p_abs_max"]
        rows.append({"text": it["text"][:30], "cos": round(cos, 6), "l2": round(l2, 3), "ref_l2": it["l2"], "p": round(p, 4), "ref_p": it["p"], "ok": ok})
    chk[name] = {"pass": all(r["ok"] for r in rows), "rows": rows}
json.dump(chk, open(sys.argv[4], "w"), indent=1); print(json.dumps(chk))
