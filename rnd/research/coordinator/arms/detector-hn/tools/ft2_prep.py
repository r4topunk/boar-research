#!/usr/bin/env python3
"""DETECTOR-FT2 step 1 (0 LLM): per dose D, train = v3b's exact 3,153 items (ft/train.jsonl rows with src v3b, same order) + the top-D
hard negatives of the DETECTOR-HN mined set (train titles, v3b p >= 0.05) by highest v3b p (ties by index), label 0; val = v3b's 555 (ft/val.jsonl).
Also writes ft2/small2.jsonl = ft/small_sets.jsonl + sonar903 (detector_text) for the HF recall screen.
usage: ft2_prep.py -> ft2/D<dose>/{train,val}.jsonl, ft2/prep.manifest.json"""
import json, os, sys, hashlib, numpy as np
sys.path.insert(0, os.path.dirname(__file__)); import dlib, embed_all
D = "<workspace>/rnd/research/coordinator/arms/detector-hn/"; W = D + "work/"; O = D + "ft2/"
rd = lambda p: [json.loads(l) for l in open(p) if l.strip()]
base = [r for r in rd(D + "ft/train.jsonl") if r["src"] == "v3b"]; assert len(base) == 3153
val = rd(D + "ft/val.jsonl"); assert len(val) == 555
tt = np.load(W + "emb.titles_train.npz"); pt = np.load(W + "p_v3b.titles_train.npy")
titles = {r["id"]: r["title"] for r in rd(D + "data/titles.train.jsonl")}
mined = [i for i in np.where(pt >= 0.05)[0].tolist()]; assert len(mined) == 2129
order = sorted(mined, key=lambda i: (-float(pt[i]), i))
man = {"v3b_train": len(base), "val": len(val), "mined": len(mined), "doses": {}}
for dose in (150, 300, 600):
    sel = order[:dose]; ids = [str(tt["ids"][i]) for i in sel]
    rows = base + [{"id": i, "text": dlib.detector_text([titles[i]]), "y": 0, "src": "hn"} for i in ids]
    os.makedirs(O + f"D{dose}", exist_ok=True)
    for nm, rr in (("train", rows), ("val", val)):
        with open(O + f"D{dose}/{nm}.jsonl", "w") as f:
            for r in rr: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    cook = sum(i.startswith("qa-cooking") for i in ids)
    man["doses"][dose] = {"n_train": len(rows), "hn": dose, "hn_cooking": cook, "hn_money": dose - cook, "p_min": round(float(pt[sel[-1]]), 4),
                          "p_max": round(float(pt[sel[0]]), 4), "hn_ids_sha256": hashlib.sha256("\n".join(ids).encode()).hexdigest(),
                          "train_sha256": hashlib.sha256(open(O + f"D{dose}/train.jsonl", "rb").read()).hexdigest(), "first5": [titles[i] for i in ids[:5]]}
S = embed_all.sets(); sm = rd(D + "ft/small_sets.jsonl")
sm += [{"set": "sonar903", "id": i, "y": int(y), "text": dlib.detector_text(list(u))} for i, y, u in S["sonar903"]]
with open(O + "small2.jsonl", "w") as f:
    for r in sm: f.write(json.dumps(r, ensure_ascii=False) + "\n")
man["small2"] = len(sm); json.dump(man, open(O + "prep.manifest.json", "w"), indent=1); print(json.dumps(man, ensure_ascii=False)[:3000])
