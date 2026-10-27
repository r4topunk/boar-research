#!/usr/bin/env python3
"""DETECTOR-FT step 1a (0 LLM): training/val texts for the v3d encoder+head fine-tune = v3b's exact data (common2: DETECTOR_HOWTO=pos,
DETECTOR_EXTRA=terse, split seed 30 -> train 3,153 / val 555, same order) + the DETECTOR-HN hard-negative set (2,129 mined at v3b p >= 0.05
+ 1,000 random, seed 42; ids sha must equal v3c manifest b3bf04ff...), appended after v3b's train items, label 0.
Texts = common2.detector_text (HF mmBERT tokenizer counts), the same string HF training, GGUF parity and the engine use.
usage: ft_prep.py -> ft/train.jsonl, ft/val.jsonl, ft/prep.manifest.json"""
import json, os, sys, random, hashlib, numpy as np
sys.path.insert(0, os.path.dirname(__file__)); import dlib, common2
D = "<workspace>/rnd/research/coordinator/arms/detector-hn/"; W = D + "work/"; O = D + "ft/"
os.environ["DETECTOR_HOWTO"] = "pos"; os.environ["DETECTOR_EXTRA"] = "terse"; common2.HOWTO_POS = True
cwd = os.getcwd(); os.chdir(dlib.SONAR); tr, va = common2.split(common2.load_aligned()); os.chdir(cwd)
tt = np.load(W + "emb.titles_train.npz"); pt = np.load(W + "p_v3b.titles_train.npy")
titles = {json.loads(l)["id"]: json.loads(l)["title"] for l in open(D + "data/titles.train.jsonl") if l.strip()}
mined = np.where(pt >= 0.05)[0].tolist(); rest = np.where(pt < 0.05)[0].tolist(); rnd = random.Random(42).sample(rest, 1000)
hn = sorted(mined + rnd); hn_ids = [str(tt["ids"][i]) for i in hn]
sha = hashlib.sha256("\n".join(hn_ids).encode()).hexdigest(); assert sha.startswith("b3bf04ff"), sha
row = lambda i, t, y, src: {"id": i, "text": t, "y": int(y), "src": src}
train = [row(x["id"], dlib.detector_text(x["turns"]), x["y"], "v3b") for x in tr] + [row(i, dlib.detector_text([titles[i]]), 0, "hn") for i in hn_ids]
val = [row(x["id"], dlib.detector_text(x["turns"]), x["y"], "v3b") for x in va]
os.makedirs(O, exist_ok=True)
for nm, rows in (("train", train), ("val", val)):
    with open(O + f"{nm}.jsonl", "w") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
man = {"train": len(train), "train_pos": sum(r["y"] for r in train), "v3b_train": len(tr), "hn": len(hn_ids), "hn_mined": len(mined), "hn_random": len(rnd),
       "hn_ids_sha256": sha, "val": len(val), "val_pos": sum(r["y"] for r in val),
       "train_sha256": hashlib.sha256(open(O + "train.jsonl", "rb").read()).hexdigest(), "val_sha256": hashlib.sha256(open(O + "val.jsonl", "rb").read()).hexdigest()}
json.dump(man, open(O + "prep.manifest.json", "w"), indent=1); print(json.dumps(man))
