import json, sys
from collections import defaultdict
def load(p):
    return [json.loads(l) for l in open(p) if l.strip()]
def per_item(files):
    # pooled ratio per item: sum boar rubric / sum ref rubric over orders (per seed), then mean over seeds
    seeds = []
    for f in files:
        b = defaultdict(float); r = defaultdict(float)
        for j in load(f):
            if not j.get("ok"): continue
            m = j["mapped"]; q = j["queryId"]
            b[q] += sum(m["boar"].values()); r[q] += sum(m["ref"].values())
        seeds.append({q: b[q] / r[q] for q in b})
    items = sorted(set().union(*seeds))
    return {q: (sum(s[q] for s in seeds if q in s) / sum(1 for s in seeds if q in s), [round(s.get(q, float('nan')), 3) for s in seeds]) for q in items}
if __name__ == "__main__":
    for q, (m, per) in per_item(sys.argv[1:]).items(): print(q, round(m, 3), per)
