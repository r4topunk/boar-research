#!/usr/bin/env python3
"""DETECTOR-HN step 2 (0 LLM): head v3c on the FROZEN v3b GGUF pooled embeddings (work/emb.*.npz from embed_all.py).
Head = v3b's (dense 384x384 no bias -> exact GELU -> LayerNorm no bias eps 1e-5 -> linear 384x2 +bias -> softmax[1]), warm-started
from sonar-mmbert-small-emergency-v3b.head.json. Recipe = ft_mmbert2.py's (AdamW lr 3e-5 wd 0.01, batch 16, linear schedule 6 % warmup,
grad clip 1.0, cross-entropy, 3 epochs as run for v3b (log: 3 epochs, best 0.9952), seed 30, best epoch by AUC on v3b's synthetic val 555).
Data = v3b's training items (3,153, howto=pos + terse, common2.split seed 30; positives unchanged) + hard negatives from titles.train:
every title with v3b p >= HN_MINE (mined) + HN_RAND random others (seed 42). usage: train_head.py <tag> [HN_MINE=0.05] [HN_RAND=1000] [HN_CAP=0 (0 = all mined; else a seed-42 sample of the mined)]"""
import json, sys, os, random, hashlib, numpy as np, torch
sys.path.insert(0, os.path.dirname(__file__)); import dlib
from sklearn.metrics import roc_auc_score
D = "<workspace>/rnd/research/coordinator/arms/detector-hn/"; W = D + "work/"
tag = sys.argv[1]; MINE = float(sys.argv[2]) if len(sys.argv) > 2 else 0.05; NR = int(sys.argv[3]) if len(sys.argv) > 3 else 1000; CAP = int(sys.argv[4]) if len(sys.argv) > 4 else 0
EP, LR, WD, BS, SEED = 3, 3e-5, 0.01, 16, 30
L = lambda s: np.load(W + f"emb.{s}.npz")
tr, va, tt = L("v3b_train"), L("v3b_val"), L("titles_train")
pt = np.load(W + "p_v3b.titles_train.npy")
mined = np.where(pt >= MINE)[0].tolist(); mined = sorted(random.Random(42).sample(mined, CAP)) if 0 < CAP < len(mined) else mined; rest = np.where(pt < MINE)[0].tolist(); rnd = random.Random(42).sample(rest, min(NR, len(rest)))
hn = sorted(mined + rnd)
X = np.concatenate([tr["vecs"], tt["vecs"][hn]]).astype(np.float32); Y = np.concatenate([tr["labels"], np.zeros(len(hn), int)])
ids = [str(i) for i in tr["ids"]] + [str(tt["ids"][i]) for i in hn]
man = {"tag": tag, "hn_mine_thr": MINE, "hn_mined": len(mined), "hn_random": len(rnd), "n_train": len(Y), "pos": int(Y.sum()), "neg": int((Y == 0).sum()),
       "hn_ids_sha256": hashlib.sha256("\n".join(ids[len(tr["ids"]):]).encode()).hexdigest(), "recipe": dict(EP=EP, LR=LR, WD=WD, BS=BS, SEED=SEED, warmup=.06, clip=1.0)}
torch.manual_seed(SEED); random.seed(SEED)
H0 = json.load(open(dlib.HEAD_V3B)); d = H0["dim"]
class Head(torch.nn.Module):
    def __init__(s):
        super().__init__(); s.dense = torch.nn.Linear(d, d, bias=False); s.norm = torch.nn.LayerNorm(d, eps=H0["eps"], bias=False); s.cls = torch.nn.Linear(d, 2)
        with torch.no_grad():
            s.dense.weight.copy_(torch.tensor(H0["dense"]).view(d, d)); s.norm.weight.copy_(torch.tensor(H0["norm"]))
            s.cls.weight.copy_(torch.tensor(H0["cls_w"]).view(2, d)); s.cls.bias.copy_(torch.tensor(H0["cls_b"]))
    def forward(s, x): return s.cls(s.norm(torch.nn.functional.gelu(s.dense(x))))
m = Head().double(); Xt = torch.tensor(X, dtype=torch.float64); Yt = torch.tensor(Y); Xv = torch.tensor(va["vecs"], dtype=torch.float64); yv = va["labels"]
def pv(): 
    with torch.no_grad(): return torch.softmax(m(Xv), -1)[:, 1].numpy()
auc0 = roc_auc_score(yv, pv()); print("epoch 0 (= v3b) val AUC", round(auc0, 5))
opt = torch.optim.AdamW(m.parameters(), lr=LR, weight_decay=WD)
from transformers import get_linear_schedule_with_warmup
steps = EP * ((len(Y) + BS - 1) // BS); sch = get_linear_schedule_with_warmup(opt, int(.06 * steps), steps)
order = list(range(len(Y))); best = -1; man["epochs"] = []
for ep in range(EP):
    m.train(); random.shuffle(order)
    for i in range(0, len(order), BS):
        b = order[i:i + BS]; loss = torch.nn.functional.cross_entropy(m(Xt[b]), Yt[b])
        loss.backward(); torch.nn.utils.clip_grad_norm_(m.parameters(), 1.0); opt.step(); sch.step(); opt.zero_grad()
    auc = roc_auc_score(yv, pv()); man["epochs"].append(round(auc, 5)); print(f"epoch {ep+1} val AUC {auc:.5f}", flush=True)
    if auc > best:
        best = auc; man["best_epoch"] = ep + 1
        r = lambda t: [round(float(v), 7) for v in t.detach().flatten().tolist()]
        out = {"kind": "mmbert-cls", "dim": d, "eps": H0["eps"], "dense": r(m.dense.weight), "norm": r(m.norm.weight), "cls_w": r(m.cls.weight), "cls_b": r(m.cls.bias)}
        json.dump(out, open(W + f"{tag}.head.json", "w"))
man["best_auc"] = round(best, 5); man["v3b_auc"] = round(auc0, 5)
json.dump(man, open(W + f"{tag}.manifest.json", "w"), indent=1); print(json.dumps(man))
