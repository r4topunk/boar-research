import json, sys, collections
REQ = ["id","category","question","why_1b_fails","rubric","reference_sources"]
ids=set(); cats=collections.Counter(); n=0
for i,l in enumerate(open(sys.argv[1]),1):
    d=json.loads(l); n+=1
    for k in REQ: assert k in d and d[k], f"line {i} missing {k}"
    assert d["id"] not in ids, f"dup id {d['id']}"; ids.add(d["id"])
    assert isinstance(d["rubric"], list) and len(d["rubric"])>=1, f"line {i} rubric"
    assert isinstance(d["reference_sources"], list), f"line {i} refs"
    for r in d["reference_sources"]: assert str(r).startswith("http"), f"line {i} ref not url: {r}"
    cats[d["category"]]+=1
print(n, "items OK"); print(dict(cats))
