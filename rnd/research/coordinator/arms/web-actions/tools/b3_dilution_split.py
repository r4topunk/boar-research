#!/usr/bin/env python3
"""WEB-ACTIONS-B item 3 (T4.1 / W12): re-split DILUTION-K's extra passages into same-article siblings vs other-article related chunks.
Article id = kept passage source URL (fallback title) in the R (ORACLE-REAL) trace; passage 1 = gold. Per-item scores from aggregates/dilution-k.json
(Haiku judge.v1-low, existing). 0 LLM, 0 judge. Usage: python3 -I b3_dilution_split.py -> ../aggregates/b3-dilution-split.json"""
import json, os, random, hashlib, collections
A = "<workspace>/rnd/research/coordinator/arms"; DK = f"{A}/dilution-k"; OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rd = lambda f: {t["itemId"]: t for t in (json.loads(l) for l in open(f) if l.strip())}
TR = {"R": rd(f"{A}/oracle-real/traces/oracle-K3-v01gold-s42.traces.jsonl"), **{k: rd(f"{DK}/traces/dilution-{k}-K3-v01gold-s42.traces.jsonl") for k in ("k1", "k2", "k3")}}
AG = json.load(open(f"{DK}/aggregates/dilution-k.json")); IT = AG["items"]; IDS = list(IT)
art = lambda x: (x.get("source") or "").split(" (")[0] or x.get("title")
cls, order_ok = {}, collections.Counter()
for i in IDS:
    k = TR["R"][i]["retrieval"]["kept"]
    if not k: cls[i] = None; continue
    g = art(k[0]); cls[i] = ["sib" if art(x) == g else "other" for x in k[1:]]
    for a, n in (("k2", 2), ("k3", 3)):
        kk = TR[a][i]["retrieval"]["kept"]; order_ok[f"{a}_prefix_of_R"] += [art(x) for x in kk] == [art(x) for x in k[:n]]
s = lambda a, i: IT[i][a]["s"]; sref = lambda i: IT[i]["R"]["sref"]
def grp(ids, hi, lo):
    if not ids: return dict(n=0)
    d = sum(s(hi, i) - s(lo, i) for i in ids) / sum(sref(i) for i in ids); r = random.Random(11); bs = []
    for _ in range(2000):
        b = [r.choice(ids) for _ in ids]; bs.append(sum(s(hi, i) - s(lo, i) for i in b) / sum(sref(i) for i in b))
    bs.sort(); ce = lambda a: sum(IT[i][a]["corr"] <= 1.5 and not IT[i][a]["warned"] and not IT[i][a]["declined"] for i in ids)
    return dict(n=len(ids), dU=round(d, 3), ci=[round(bs[50], 3), round(bs[1949], 3)], up=sum(s(hi, i) > s(lo, i) for i in ids), down=sum(s(hi, i) < s(lo, i) for i in ids),
                CEu_hi=ce(hi), CEu_lo=ce(lo))
withx = [i for i in IDS if cls[i]]
res = {"note": "dU = (sum s_hi - sum s_lo) / sum sref over the group; item bootstrap B 2000 seed 11; CEu = corr<=1.5, unwarned, not declined",
       "order_check": dict(order_ok), "n_items": len(IDS), "no_kept_list": [i for i in IDS if cls[i] is None],
       "extras_in_R": dict(sib=sum(c.count("sib") for c in cls.values() if c), other=sum(c.count("other") for c in cls.values() if c)),
       "items_by_extra_mix": collections.Counter(("all-sib" if set(c) == {"sib"} else "all-other" if set(c) == {"other"} else "mixed" if c else "none") for c in cls.values() if c is not None)}
mix = lambda c: "all-sib" if set(c) == {"sib"} else "all-other" if set(c) == {"other"} else "mixed"
res["R_minus_k1_by_mix"] = {m: grp([i for i in withx if mix(cls[i]) == m], "R", "k1") for m in ("all-sib", "mixed", "all-other")}
res["R_minus_k1_by_sib_share"] = {"sib share >= 0.5": grp([i for i in withx if cls[i].count("sib") / len(cls[i]) >= 0.5], "R", "k1"),
                                  "sib share < 0.5": grp([i for i in withx if cls[i].count("sib") / len(cls[i]) < 0.5], "R", "k1")}
res["passage2_k2_minus_k1"] = {c: grp([i for i in withx if len(cls[i]) >= 1 and cls[i][0] == c], "k2", "k1") for c in ("sib", "other")}
res["passage3_k3_minus_k2"] = {c: grp([i for i in withx if len(cls[i]) >= 2 and cls[i][1] == c], "k3", "k2") for c in ("sib", "other")}
res["per_item"] = {i: dict(extras=cls[i], s={a: round(IT[i][a]["s"], 3) for a in ("k1", "k2", "k3", "R")}, gold=IT[i]["gold_source"]) for i in IDS}
o = json.dumps(res, indent=1); open(f"{OUT}/aggregates/b3-dilution-split.json", "w").write(o)
print(json.dumps({k: v for k, v in res.items() if k != "per_item"}, indent=1)); print("sha256", hashlib.sha256(o.encode()).hexdigest())
