#!/usr/bin/env python3
"""NATIVE-RC R2 (0 LLM from labels): the 20 boar-factbook self-tests with factbook v1 (catalog c5854353, arm fb) vs the shaped v2 (981f7b4b, arm fb2),
rest of the kit identical. PACKPROOF/UXMATRIX labels, final() as uxmatrix agg. Rule (frozen): LEVER-TRANSFERS iff v2 correct-any >= v1 + 3 items
and 0 new wrong-unwarned (items WRONG_CONFIDENT under v2 and not under v1). Also: factbook chunk kept (title prefix 'CIA World Factbook' or a factbook source).
usage: python3 -I r2.py -> aggregates/r2.json"""
import json, collections, os
A = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
L = collections.defaultdict(dict)
for r in rd(A + "/judge/r2/labels.jsonl"):
    if r["ok"]: L[r["key"]][r["call"]] = r
def final(k):
    c = L.get(k)
    if not c or "A" not in c: return None, None
    a = c["A"]
    if a["conf"] != "borderline" or "B" not in c or c["B"]["label"] == a["label"] or "C" not in c: return a["label"], a["conf"]
    v = collections.Counter([a["label"], c["B"]["label"], c["C"]["label"]]).most_common(1)[0]
    return (a["label"] if v[1] == 1 else v[0]), "rechecked"
ANS = json.load(open(A + "/judge/r2/answers.json"))
REN = {(r["arm"], r["id"]): r for r in rd(A + "/gen/all.render.jsonl") if r["arm"] in ("fb", "fb2")}
fbk = lambda r: any("factbook" in ((s.get("source") or "") + s["title"]).lower() for s in r["sourcesShown"])
ids = sorted({k.split("|")[2] for k in ANS})
CA = ("CORRECT_WITH_SOURCE", "CORRECT_FROM_MEMORY")
rows = []
for i in ids:
    (l1, c1), (l2, c2) = final(ANS[f"fb|on|{i}"]["key"]), final(ANS[f"fb2|on|{i}"]["key"])
    rows.append(dict(id=i, v1=l1, v2=l2, v1_conf=c1, v2_conf=c2, v1_factbook_shown=fbk(REN[("fb", i)]), v2_factbook_shown=fbk(REN[("fb2", i)]),
                     same_text=ANS[f"fb|on|{i}"]["text"] == ANS[f"fb2|on|{i}"]["text"]))
ca = lambda k: sum(r[k] in CA for r in rows)
new_wu = [r["id"] for r in rows if r["v2"] == "WRONG_CONFIDENT" and r["v1"] != "WRONG_CONFIDENT"]
res = dict(n=len(rows), correct_any=dict(v1=ca("v1"), v2=ca("v2")), CWS=dict(v1=sum(r["v1"] == "CORRECT_WITH_SOURCE" for r in rows), v2=sum(r["v2"] == "CORRECT_WITH_SOURCE" for r in rows)),
           WU=dict(v1=sum(r["v1"] == "WRONG_CONFIDENT" for r in rows), v2=sum(r["v2"] == "WRONG_CONFIDENT" for r in rows)), new_wrong_unwarned=new_wu,
           better=[r["id"] for r in rows if r["v2"] in CA and r["v1"] not in CA], worse=[r["id"] for r in rows if r["v1"] in CA and r["v2"] not in CA],
           factbook_source_shown=dict(v1=sum(r["v1_factbook_shown"] for r in rows), v2=sum(r["v2_factbook_shown"] for r in rows)),
           borderline_single=sum((r["v1_conf"] == "borderline") + (r["v2_conf"] == "borderline") for r in rows), labels=dict(collections.Counter(r["v1"] for r in rows)), labels_v2=dict(collections.Counter(r["v2"] for r in rows)), rows=rows)
res["verdict"] = "LEVER-TRANSFERS" if res["correct_any"]["v2"] >= res["correct_any"]["v1"] + 3 and not new_wu else "DOES-NOT-TRANSFER"
json.dump(res, open(A + "/aggregates/r2.json", "w"), indent=1)
print(json.dumps({k: v for k, v in res.items() if k != "rows"}, indent=1))
