#!/usr/bin/env python3
"""RETBENCH: write items/ (one gold file per set) from the existing public dev gold. python3 -I build_items.py ; never reads blind/, rnd/veil/, bench/v0.4."""
import json, glob, hashlib, os
B = "<workspace>"; A = B + "/rnd/research/coordinator/arms"; BE = B + "/boar-eval/bench/"; OUT = A + "/retbench/items"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
for bad in ("blind/", "rnd/veil", "bench/v0.4"): pass
QS = {q["id"]: q for q in rd(BE + "v0.1/questions.public.jsonl")}
for f in glob.glob(BE + "selftest/*/questions.jsonl"):
    for q in rd(f): QS[q["id"]] = q
POOL = json.load(open(A + "/coverage-map/aggregates/coverage-pool.json"))["items"]; O = json.load(open(A + "/coverage-map/aggregates/cm-oracle.json"))
main = []
for i in sorted(POOL):
    q = QS[i]; e = dict(id=i, set=POOL[i]["set"], question=q["question"], health=i.startswith(("lan-hlt-", "vit-hlt-", "dng-")))
    if POOL[i]["set"] == "cm": e.update(rule="chunk: a normalised in_pack_facts quote is a substring of one kept chunk body", in_pack_facts=q["selftest"]["in_pack_facts"], oracle_doc=f"pack:local-{O[i]['pack']}:a{O[i]['article_id']}")
    else: e.update(rule="chunk: share_v01(grading, [one kept chunk body]) >= 0.5 (FACTPRESENT, pc.hits, echo terms dropped)", grading=q.get("grading", {}))
    main.append(e)
assert len(main) == 92
ITEMS = json.load(open(A + "/packproof/in/items.json"))["items"]; OWN = json.load(open(A + "/packproof/in/own.json")); OF = json.load(open(A + "/oracle-st/tools/oracle-facts.json"))
HP = {"qa-health-se", "boar-firstaid-en", "boar-medlineplus-en"}
st = [dict(id=x["id"], pack=x["pack"], health=x["pack"] in HP, own_docs=[f"pack:local-{x['pack']}:a{a['article']}" for a in OWN[x["id"]]], fact_chunks=sorted(OF[x["id"]]["fact_chunks"])) for x in ITEMS]
assert len(st) == 180
T = json.load(open(A + "/topics27/aggregates/titles.json")); TOP = {t["key"]: t for t in json.load(open(A + "/topics27/in/topics.json"))}
topics = [dict(key=t["key"], kind=t["kind"], area=TOP[t["key"]]["area"], health=TOP[t["key"]]["area"] == "Health" or t["key"] in "q2 q4 b2 b8 b13 b14 b21".split(),
               topic=TOP[t["key"]]["en"], expected_groups=t["groups"], rule="expected-in-kept: any title of any group equals a kept chunk title") for t in T]
assert len(topics) == 27
QF = {d["id"]: d for d in rd(A + "/qform/items/qform.jsonl")}
f8 = [dict(id=i, turn1=i[:-1] + "0", pack=QF[i]["pack"], gold_doc=f"pack:local-{QF[i]['pack']}:a{QF[i]['gold']['article_id']}", gold_quote=QF[i]["gold"]["quote"],
           rule="source survival: gold quote (normalised) in a kept chunk on turn 1 AND on turn 2") for i in sorted(QF) if i.endswith("-F8")]
assert len(f8) == 48
LQ = {d["id"]: d for d in rd(BE + "slices/longsession-v1/questions.jsonl")}
ls = [dict(id=i, prev=LQ[i].get("prevId") or i.rsplit("-t", 1)[0] + f"-t{int(i.split('-t')[1]) - 1}", referent=LQ[i].get("referent", []),
           rule="source survival: a referent string in a kept chunk of the previous turn AND of this turn") for i in sorted(LQ) if LQ[i].get("followup") and 2 <= int(i.split("-t")[1]) <= 5]
os.makedirs(OUT, exist_ok=True)
for n, d in [("main92", main), ("st180", st), ("topics27", topics), ("f8-48", f8), ("longsession", ls)]:
    json.dump(d, open(f"{OUT}/{n}.json", "w"), indent=1, ensure_ascii=False)
with open(f"{OUT}/SHA256SUMS", "w") as f:
    for n in ("main92", "st180", "topics27", "f8-48", "longsession"):
        f.write(hashlib.sha256(open(f"{OUT}/{n}.json", "rb").read()).hexdigest() + f"  {n}.json\n")
print({n: len(d) for n, d in [("main92", main), ("st180", st), ("topics27", topics), ("f8", f8), ("ls", ls)]})
