"""Quality ratio on a set of items from judge.v1 rows (judge-core summarize: sum mean-rubric(system) / sum mean-rubric(ref)),
plus labels (pass c>=4 / cw c<=2 / fail). python3 ratio.py ids.txt name=judgments.jsonl[,more.jsonl] ..."""
import json, sys, statistics as st
ids = set(open(sys.argv[1]).read().strip().split(","))
def rub(d): return st.mean([d["correctness"], d["completeness"], d["usefulness"]])
for spec in sys.argv[2:]:
    name, files = spec.split("=", 1)
    per = {}
    for f in files.split(","):
        for l in open(f):
            r = json.loads(l)
            if not r.get("ok") or r["queryId"] not in ids: continue
            per.setdefault(r["queryId"], []).append(r["mapped"])
    b = {i: st.mean(rub(m["boar"]) for m in v) for i, v in per.items()}; rf = {i: st.mean(rub(m["ref"]) for m in v) for i, v in per.items()}
    c = {i: st.mean(m["boar"]["correctness"] for m in v) for i, v in per.items()}
    lab = {"pass": sum(x >= 4 for x in c.values()), "cw": sum(x <= 2 for x in c.values())}; lab["fail"] = len(c) - lab["pass"] - lab["cw"]
    print(f"{name:22} n={len(per):2} ratio {sum(b.values())/sum(rf.values()):.3f}  boar {st.mean(b.values()):.2f}  labels {lab}")
