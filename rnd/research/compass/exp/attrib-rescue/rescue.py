# Compact-model answers kept only because attribution added a citation (v0.1 runs only; no blind sets).
import json, re, collections, importlib.util, os
R = "<workspace>/boar-eval/runs/"
RUNS = ["night-2026-10-01/ios-main-s42", "night-2026-10-01/ios-main-s43", "night-2026-10-01/ios-main-s44",
        "g75desk/g75desk-s42", "g75desk/g75desk-s43", "devices/2026-10-02/and-q15-r1", "devices/2026-10-02/and-q15-r2",
        "devices/2026-10-02/ios-q15-r1", "devices/2026-10-02/ios-q15-r2"]
spec = importlib.util.spec_from_file_location("sc", "../safety-v07/safety_check.v0.7.py"); sc = importlib.util.module_from_spec(spec); spec.loader.exec_module(sc)
S = sc.load(rules_path="../safety-v07/rules.v0.7.json", overlay_path="../safety-v07/overlay.v0.4.json")
Q = {json.loads(l)["id"]: json.loads(l) for l in open("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl")}
for l in open("<workspace>/boar-eval/scorers/vendor/safety/track.v0.3.jsonl"): r = json.loads(l); Q.setdefault(r["id"], r)
split = lambda t: [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", t) if s.strip()]
def judged(p):
    if not os.path.exists(p + ".judgments.jsonl"): return {}
    by = collections.defaultdict(list)
    for l in open(p + ".judgments.jsonl"):
        j = json.loads(l)
        if j.get("ok"): v = j["verdict"]; by[j["queryId"]].append((v["scores_A"] if j["order"] == "boarA" else v["scores_B"])["correctness"])
    return {k: sum(v) / len(v) for k, v in by.items() if len(v) == 2}
rows = []
for p in RUNS:
    J = judged(R + p)
    for l in open(R + p + ".traces.jsonl"):
        t = json.loads(l); codes = t["route"]["reasonCodes"]; a = t["answer"]
        if a["declined"] or not a["shown"] or not any("qwen2.5-1.5b" in c for c in codes) or any(c.startswith("grounding:health") for c in codes): continue
        added = [int(x) for c in codes if c.startswith("citations:added-") for x in c.split("-")[1:]]
        ncit = len(re.findall(r"\[\d+\]", a["text"]))
        if not added or ncit > len(added): continue  # only answers whose every [n] came from attribution
        sents = [s for s in split(a["text"]) if len(s.split()) >= 4]
        unc = [s for s in sents if not re.search(r"\[\d+\]", s)]
        q = Q.get(t["itemId"], {}); rules = sc.rules_for_v06(q, S) if q.get("danger") else []
        hits = [h for h in sc.check(a["text"], rules, S) if h.get("status") == "unsafe"] if rules else []
        c = J.get(t["itemId"]); lab = None if c is None else ("pass" if c >= 4 else "cw" if c <= 1 else "fail")
        rows.append({"run": p.split("/")[-1], "id": t["itemId"], "danger": bool(q.get("danger")), "nSent": len(sents), "nUncited": len(unc), "label": lab, "unsafe": [h["rule"] for h in hits], "uncited": unc[:3]})
json.dump(rows, open("rescued.json", "w"), indent=1, ensure_ascii=False)
tot = collections.Counter()
for p in RUNS:
    n = sum(1 for l in open(R + p + ".traces.jsonl") if not json.loads(l)["answer"]["declined"])
    tot[p.split("/")[-1]] = n
print(f"rescued (every [n] from attribution) answers: {len(rows)} over {len(RUNS)} runs; with ≥1 uncited sentence: {sum(r['nUncited']>0 for r in rows)}")
print("labels:", collections.Counter(r["label"] for r in rows), "| danger items:", sum(r["danger"] for r in rows), "| unsafe:", [(r["run"], r["id"], r["unsafe"]) for r in rows if r["unsafe"]])
print("per run:", collections.Counter(r["run"] for r in rows))
print("uncited share of sentences in rescued answers:", round(sum(r["nUncited"] for r in rows)/max(1,sum(r["nSent"] for r in rows)),2))
