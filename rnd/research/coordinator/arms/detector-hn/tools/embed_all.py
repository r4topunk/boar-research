#!/usr/bin/env python3
"""DETECTOR-HN: embed every set once with the v3b GGUF (local servers, dlib) -> work/emb.<set>.npz {ids, labels, vecs}. 0 LLM.
usage: embed_all.py [set ...]"""
import json, os, sys, time, numpy as np
sys.path.insert(0, os.path.dirname(__file__)); import dlib, common2
H = "<workspace>/rnd/research/"; A = H + "coordinator/arms/"; D = A + "detector-hn/"; W = D + "work/"; os.makedirs(W, exist_ok=True)
rj = lambda p: [json.loads(l) for l in open(p) if l.strip()]
def sets():
    S = {}
    os.environ["DETECTOR_HOWTO"] = "pos"; os.environ["DETECTOR_EXTRA"] = "terse"; common2.HOWTO_POS = True
    cwd = os.getcwd(); os.chdir(dlib.SONAR); tr, va = common2.split(common2.load_aligned()); os.chdir(cwd)
    S["v3b_train"] = [(x["id"], x["y"], x["turns"]) for x in tr]; S["v3b_val"] = [(x["id"], x["y"], x["turns"]) for x in va]
    cd = rj(H + "compass/exp/emergency-dev/dev.jsonl")
    S["compass300"] = [(d["id"], d["emergency"], [t["text"] for t in d["turns"] if t["role"] == "user"]) for d in cd]
    P = json.load(open(dlib.SONAR + "/dev/pool.raw.json")); L = rj(dlib.SONAR + "/dev/labels.sonar.jsonl")
    S["sonar903"] = [(p.get("id", str(i)), l["label"], p["turns"]) for i, (p, l) in enumerate(zip(P, L))]
    S["terse30"] = [(t["id"], t["label"], t["turns"]) for t in rj(dlib.SONAR + "/probes/terse-live.heldout.jsonl")]
    S["ptmirror28"] = [(x["id"], 1, [x["q"]]) for x in rj(H + "compass/exp/pt-recall/pt-mirror.jsonl")]
    for nm in ("train", "heldout"):
        S["titles_" + nm] = [(x["id"], 0, [x["title"]]) for x in rj(D + f"data/titles.{nm}.jsonl")]
    pr = rj(A + "coverage-map/sefix/f3-safety/req/f3safety-off-s42.requests.jsonl")
    S["probes65"] = [(r["item"]["id"], -1, [t["text"] for t in r["item"].get("history", {}).get("turns", []) if t["role"] == "user"] + [r["item"]["question"]]) for r in pr]
    mn = rj(A + "decode-ground/runs/req/dg-S-K1-main-s42.requests.jsonl")
    S["main97"] = [(r["item"]["id"], -1, [r["item"]["question"]]) for r in mn]
    return S
if __name__ == "__main__":
    S = sets(); want = sys.argv[1:] or list(S)
    for k in want:
        ids, ys, U = zip(*S[k]); t0 = time.time()
        X, texts = dlib.embed_turns(list(U), cache=W + "cache.npz")
        np.savez(W + f"emb.{k}.npz", ids=np.array(ids), labels=np.array(ys), vecs=X)
        print(k, len(ids), f"{time.time()-t0:.0f}s", flush=True)
