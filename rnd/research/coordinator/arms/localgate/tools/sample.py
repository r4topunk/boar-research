#!/usr/bin/env python3
"""LOCALGATE stratified sample from blind/localgate/harvest-*.jsonl. Prints counts only.
Per type: all positives (jev p>=0.7, up to POS), a 0.3-0.7 band slice (BAND), negatives (p<0.3) = max(#pos, TOTAL-#pos-#band),
each stratum split across sources (wikifull, wikisection, packcond) as evenly as availability allows. seed 20261012.
usage: sample.py [--pos 300] [--band 60]"""
import json, random, glob, collections, argparse
D = "<private held-out dir>"
ap = argparse.ArgumentParser(); ap.add_argument("--pos", type=int, default=300); ap.add_argument("--band", type=int, default=120); ap.add_argument("--total", type=int, default=500); a = ap.parse_args()
R = []; seen = set()
for f in sorted(glob.glob(f"{D}/harvest-*.jsonl")):
    for l in open(f):
        r = json.loads(l)
        if r["rid"] in seen: continue
        seen.add(r["rid"]); R.append(r)
def band(p): return "pos" if p >= 0.7 else ("neg" if p < 0.3 else "mid")
cnt = collections.Counter((r["type"], r["src"], band(r["jev_p"])) for r in R if r["jev_p"] >= 0)
print("available", json.dumps({"|".join(k): v for k, v in sorted(cnt.items())}))
rng = random.Random(20261012); out = []; summ = {}
for t in ("has_fact", "quote_supports"):
    pool = collections.defaultdict(list)
    for r in R:
        if r["type"] == t and r["jev_p"] >= 0: pool[(r["src"], band(r["jev_p"]))].append(r)
    for v in pool.values(): rng.shuffle(v)
    def take(b, n):
        srcs = [s for s in ("wikifull", "wikisection", "packcond") if pool[(s, b)]]; got = []
        # even split, spill over when one source runs out
        while len(got) < n and any(pool[(s, b)] for s in srcs):
            for s in srcs:
                if pool[(s, b)] and len(got) < n: got.append(pool[(s, b)].pop())
        return got
    pos = take("pos", a.pos); mid = take("mid", a.band); neg = take("neg", max(len(pos), a.total - len(pos) - len(mid)))
    S = pos + neg + mid; out += S
    summ[t] = dict(n=len(S), pos=len(pos), neg=len(neg), mid=len(mid), by_src=dict(collections.Counter(r["src"] for r in S)))
with open(f"{D}/sample.jsonl", "w") as fo:
    for r in out: fo.write(json.dumps(r, ensure_ascii=False) + "\n")
print("sample", json.dumps(summ))
json.dump(dict(available={"|".join(k): v for k, v in sorted(cnt.items())}, sample=summ), open(f"{D}/sample-meta.json", "w"))
