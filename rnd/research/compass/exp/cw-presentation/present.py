# What does the user see on the Android 4B's confident-wrong answers? (v0.1 dev runs only)
import json, collections, sys
R = "<workspace>/boar-eval/runs/"
RUNS = [("night-2026-10-01/and-qwen-s42", ), ("night-2026-10-01/and-qwen-s43",), ("and-qwen-s44/and-qwen-s44",)]
def judged(p):
    by = collections.defaultdict(list)
    for l in open(p + ".judgments.jsonl"):
        j = json.loads(l)
        if not j.get("ok"): continue
        v = j["verdict"]; s = v["scores_A"] if j["order"] == "boarA" else v["scores_B"]
        by[j["queryId"]].append(s["correctness"])
    return {k: sum(v) / len(v) for k, v in by.items() if len(v) == 2}
def present(t):
    a = t["answer"]; codes = t["route"]["reasonCodes"]
    if a["declined"]: return "declined"
    if not a["shown"]: return "no source (memory label)"
    if a["cited"] and not a["warnings"] and "grounding:uncited-warning" not in codes: return "cited, no warning"
    if a["cited"]: return "cited + weak-source warning"
    return "sources shown, uncited warning"
rows = []
for (p,) in RUNS:
    J = judged(R + p); T = {json.loads(l)["itemId"]: json.loads(l) for l in open(R + p + ".traces.jsonl")}
    for i, c in J.items():
        t = T.get(i)
        if not t: continue
        lab = "pass" if c >= 4 else "cw" if c <= 1 else "fail"
        rows.append({"run": p.split("/")[-1], "id": i, "label": lab, "c": c, "present": present(t), "codes": [x for x in t["route"]["reasonCodes"] if x.startswith(("grounding", "citations", "task"))], "nShown": len(t["answer"]["shown"]), "weak": t["answer"]["weakSources"]})
json.dump(rows, open("rows.json", "w"), indent=0)
tab = collections.Counter((r["present"], r["label"]) for r in rows)
cats = ["cited, no warning", "cited + weak-source warning", "sources shown, uncited warning", "no source (memory label)", "declined"]
print(f"{'presentation':34s} {'n':>4} {'pass':>5} {'fail':>5} {'cw':>4}  cw-rate")
for c in cats:
    n = sum(tab[(c, l)] for l in ("pass", "fail", "cw"))
    if n: print(f"{c:34s} {n:4d} {tab[(c,'pass')]:5d} {tab[(c,'fail')]:5d} {tab[(c,'cw')]:4d}  {tab[(c,'cw')]/n:.0%}")
cw = [r for r in rows if r["label"] == "cw"]
print("cw total", len(cw), "| of which look backed (cited, no warning):", sum(r["present"] == "cited, no warning" for r in cw))
for r in cw:
    if r["present"] == "cited, no warning": print("  BACKED-LOOKING cw:", r["run"][-3:], r["id"], r["codes"])
