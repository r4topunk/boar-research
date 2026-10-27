# Is the attached source sentence (d1a "From the source [n]: ...") more often right than the draft it backs?
import json, re, sys, collections
sys.path.insert(0, "<workspace>/boar-eval/scorers/vendor/lantern"); import precheck
R = "<workspace>/boar-eval/runs/night-2026-10-01/d1/"
items = {json.loads(l)["id"]: json.loads(l) for l in open(R + "slice40.jsonl")}
D = {d["id"]: d for d in json.load(open("../verify-replay/scored.json"))}
arm = {json.loads(l)["itemId"]: json.loads(l) for l in open(R + "ios-d1a-slice40-s42.traces.jsonl")}
rows = []
for q, d in D.items():
    t = arm[q]; ft = t["answer"]["text"]
    m = re.search(r'(?:From the source|Da fonte offline[^\[]*)\s*\[\d+\]:\s*(.+)$', ft, re.S)
    snip = m.group(1).strip().strip('"“”') if m else None
    it = items.get(q)
    g = lambda s: precheck.grade(it, {"answer": s, "declined": False})[0] if (it and it.get("grading") and s) else None
    rows.append({"id": q, "pt": d["pt"], "judge_draft": d["label"], "pre_draft": g(d["draft"]), "pre_snip": g(snip), "snip": snip,
                 "snippet_code": any("unconfirmed-snippet" in c for c in t["route"]["reasonCodes"])})
print("items", len(rows), "with snippet", sum(r["snip"] is not None for r in rows))
print("draft  precheck:", collections.Counter(r["pre_draft"] for r in rows))
print("snippet precheck:", collections.Counter(r["pre_snip"] for r in rows if r["snip"]))
print("draft precheck vs judge:", collections.Counter((r["pre_draft"], r["judge_draft"]) for r in rows))
for r in rows: print(f"  {r['id']:16} judge={r['judge_draft']:4} pre_draft={str(r['pre_draft']):15} pre_snip={str(r['pre_snip']):15} snip={str(r['snip'])[:90]!r}")
json.dump(rows, open("rows.json", "w"), ensure_ascii=False)
