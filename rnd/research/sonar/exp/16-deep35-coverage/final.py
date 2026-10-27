"""exp-16 final: P1/P2 on both seeds. Pairs: (srv-s42, deep35-s42) and (and-qwen-s43, deep35-s43; node backend for the fast
base, since no srv-s43 exists). Pooled ratio Δ per kit-A coverage class, item bootstrap (2,000, seed 11)."""
import json, collections, statistics, random
R = "<workspace>/boar-eval/runs/night-2026-10-01/"
cls = json.load(open("classes-kitA-v01.json"))
def judge(f):
    s = collections.defaultdict(list)
    for l in open(R + f):
        j = json.loads(l)
        if j.get("ok") and j.get("mapped"):
            b, r = j["mapped"]["boar"], j["mapped"]["ref"]; s[j["queryId"]].append((sum(b.values()) / 3, sum(r.values()) / 3))
    return {k: (statistics.mean(x[0] for x in v), statistics.mean(x[1] for x in v)) for k, v in s.items()}
pairs = [(judge("srv/srv-s42.judgments.jsonl"), judge("deep35/and-deep35-s42.judgments.jsonl")), (judge("and-qwen-s43.judgments.jsonl"), judge("deep35/and-deep35-s43.judgments.jsonl"))]
ids = sorted(set.intersection(*[set(a) & set(b) for a, b in pairs]))
def d(sel):
    A = sum(a[i][0] for a, _ in pairs for i in sel) / sum(a[i][1] for a, _ in pairs for i in sel)
    B = sum(b[i][0] for _, b in pairs for i in sel) / sum(b[i][1] for _, b in pairs for i in sel)
    return B - A
random.seed(11)
groups = {"all": None, "in-kit-key": ["in-kit-key"], "out (not-in-kit + in-kit-no-key)": ["not-in-kit", "in-kit-no-key"], "unkeyed": ["unkeyed"]}
res = {}
for name, cs in groups.items():
    sel = ids if cs is None else [i for i in ids if cls.get(i) in cs]
    bs = sorted(d([random.choice(sel) for _ in sel]) for _ in range(2000)); res[name] = d(sel)
    print(f"{name}: n={len(sel)} Δ {d(sel):+.3f}  95% CI {bs[50]:+.3f} … {bs[1949]:+.3f}")
print(f"P1 (Δ out > Δ in-kit-key): {'HOLDS' if res['out (not-in-kit + in-kit-no-key)'] > res['in-kit-key'] else 'FAILS'} | P2 (|Δ in-kit-key| <= 0.05): {'HOLDS' if abs(res['in-kit-key']) <= 0.05 else 'FAILS'}  [2 seeds; s43 fast base = node backend]")
