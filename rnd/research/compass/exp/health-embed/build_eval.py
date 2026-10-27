# Builds eval.jsonl from existing R&D question sets (read-only). Labels: danger / health_info / neg.
import json, re
R = "<workspace>/rnd/"
def rd(f): return [json.loads(l) for l in open(R + f) if l.strip()]
items = {}
def add(src, rid, q, label):
    k = re.sub(r"\W+", " ", q.lower()).strip()
    if k in items:
        # keep strongest label
        order = {"danger": 2, "health_info": 1, "neg": 0}
        if order[label] > order[items[k]["label"]]: items[k]["label"] = label
        items[k]["src"].append(src); return
    items[k] = {"id": rid, "q": q, "label": label, "src": [src]}
for f, s in [("kiln/exp-10-main-baseline/questions.danger17.jsonl", "danger17"),
             ("kiln/exp-10-main-baseline/questions.safety12.jsonl", "safety12"),
             ("bench/safety/track.v0.3.jsonl", "track03")]:
    for r in rd(f): add(s, r["id"], r["question"], "danger")
for r in rd("veil/hm-fresh.jsonl"): add("hm-fresh", r["id"], r["question"], "danger")
for f, s in [("veil/h1-fresh.jsonl", "h1"), ("veil/h2-fresh.jsonl", "h2"), ("veil/h2-pool.jsonl", "h2pool"),
             ("veil/o2v2c-fresh.jsonl", "o2c1"), ("veil/o2v2c-fresh2.jsonl", "o2c2"),
             ("bench/questions/v0/questions.public.jsonl", "pub"),
             ("kiln/exp-06-desktop-answerer/questions.vitalik58.jsonl", "v58"),
             ("kiln/exp-08-o2v2/questions.o2-ab82.jsonl", "ab82")]:
    for r in rd(f):
        q = r.get("question") or r.get("query"); c = r.get("category", "")
        if r.get("danger") is True or c in ("danger", "danger-situation"): lab = "danger"
        elif c == "health": lab = "danger" if s == "h1" else "health_info"
        else: lab = "neg"
        add(s, r["id"], q, lab)
for r in rd("kiln/exp-10-main-baseline/questions.exp10.jsonl"): add("exp10", r["id"], r["question"], "neg")
import collections
out = list(items.values())
print(collections.Counter(i["label"] for i in out), len(out))
with open("eval.jsonl", "w") as f:
    for i in out: f.write(json.dumps(i, ensure_ascii=False) + "\n")
