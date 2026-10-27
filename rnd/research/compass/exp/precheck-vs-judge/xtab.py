# Gate-mode truthfulness validity: precheck v2.2 label vs judge label on the same answered items (night main runs + d1 runs).
import json, sys, collections
sys.path.insert(0, "<workspace>/boar-eval/scorers/vendor/lantern"); import precheck
sys.path.insert(0, "<workspace>/boar-eval/scorers"); from score import PRECHECK_MAP
B = "<workspace>/boar-eval/"
Q = {}
for f in ["bench/v0.1/questions.public.jsonl", "runs/night-2026-10-01/d1/slice40.jsonl"]:
    for l in open(B + f): r = json.loads(l); Q[r["id"]] = r
runs = [("runs/night-2026-10-01/ios-main-s42", "runs/night-2026-10-01/ios-main-s42"), ("runs/night-2026-10-01/ios-main-s43", "runs/night-2026-10-01/ios-main-s43"),
        ("runs/night-2026-10-01/d1/ios-d1a-slice40-s42", "runs/night-2026-10-01/d1/ios-d1a-slice40-s42")]
X = collections.Counter(); rows = []
for tr, jd in runs:
    T = {json.loads(l)["itemId"]: json.loads(l) for l in open(B + tr + ".traces.jsonl")}
    C = collections.defaultdict(list)
    for l in open(B + jd + ".judgments.jsonl"):
        r = json.loads(l)
        if r.get("ok"): C[r["queryId"]].append(r["mapped"]["boar"]["correctness"])
    for q, cs in C.items():
        t, it = T.get(q), Q.get(q)
        if not t or len(cs) != 2 or not it or (it.get("grading") or {}).get("type") != "precheck" or t["answer"]["declined"]: continue
        c = sum(cs) / 2; jl = "pass" if c >= 4 else "cw" if c <= 1.0 else "fail"
        st, why = precheck.grade(it, {"answer": t["answer"]["text"], "declined": False}); pl = PRECHECK_MAP[st]
        if pl == "refused": continue
        X[(pl, jl)] += 1; rows.append({"run": tr.split("/")[-1], "id": q, "precheck": pl, "judge": jl, "corr": c, "why": why})
print("precheck label → judge label (answered, precheck-graded items):")
for pl in ("pass", "fail", "cw"):
    print(f"  precheck {pl:5}: " + "  ".join(f"judge {jl} {X[(pl, jl)]:3}" for jl in ("pass", "fail", "cw")))
n = sum(X.values()); agree = sum(X[(l, l)] for l in ("pass", "fail", "cw"))
jcw = sum(X[(p, "cw")] for p in ("pass", "fail", "cw")); pcw = sum(X[("cw", j)] for j in ("pass", "fail", "cw"))
print(f"n={n} exact agreement {agree}/{n}; judge-cw {jcw} vs precheck-cw {pcw} (precheck catches {X[('cw','cw')]}/{jcw} of the judge's cw)")
print("by run:", collections.Counter(r["run"] for r in rows))
json.dump(rows, open("rows.json", "w"))
