"""Sonar exp-16: pre-registered P1/P2 diagnostic for option 6 (deep35), PRELIMINARY on seed 42 only.
Paired per-item judge ratio, deep35-s42 vs the fast-tier base it was diffed against (srv-s42, Qwen3-4B via server backend),
split by kit-A coverage class (tools/coverage_classes.py on public v0.1, no --vital5)."""
import json, collections, statistics
R = "<workspace>/boar-eval/runs/night-2026-10-01/"
cls = json.load(open("classes-kitA-v01.json"))
def judge(f):
    s = collections.defaultdict(list)
    for l in open(R + f):
        j = json.loads(l)
        if j.get("ok") and j.get("mapped"):
            b, r = j["mapped"]["boar"], j["mapped"]["ref"]; s[j["queryId"]].append((sum(b.values()) / 3, sum(r.values()) / 3))
    return {k: (statistics.mean(x[0] for x in v), statistics.mean(x[1] for x in v)) for k, v in s.items()}
A = judge("srv/srv-s42.judgments.jsonl"); B = judge("deep35/and-deep35-s42.judgments.jsonl")
ids = sorted(set(A) & set(B))
ratio = lambda J, sel: sum(J[i][0] for i in sel) / sum(J[i][1] for i in sel)
print(f"all: n={len(ids)} fast {ratio(A, ids):.3f} deep {ratio(B, ids):.3f} Δ {ratio(B, ids) - ratio(A, ids):+.3f}")
groups = {"in-kit-key": ["in-kit-key"], "out (not-in-kit + in-kit-no-key)": ["not-in-kit", "in-kit-no-key"], "unkeyed": ["unkeyed"]}
res = {}
for name, cs in groups.items():
    sel = [i for i in ids if cls.get(i) in cs]
    if sel:
        d = ratio(B, sel) - ratio(A, sel); res[name] = d
        print(f"{name}: n={len(sel)} fast {ratio(A, sel):.3f} deep {ratio(B, sel):.3f} Δ {d:+.3f}")
p1 = res.get("out (not-in-kit + in-kit-no-key)", 0) > res.get("in-kit-key", 0)
p2 = abs(res.get("in-kit-key", 0)) <= 0.05
print(f"P1 (Δ out > Δ in-kit-key): {'HOLDS' if p1 else 'FAILS'} | P2 (|Δ in-kit-key| <= 0.05): {'HOLDS' if p2 else 'FAILS'}  [seed 42 only, preliminary]")
