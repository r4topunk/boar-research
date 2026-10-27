"""PHONEFAIL aggregate (0 LLM calls): per-trace duplicate sources and truncation heuristics, our 27 traces + the X6 run (phone cut 7 rows, native raw).
dup = entries in the source list whose title (or url) already appeared earlier in the same list. app-shown = the Android bridge shows the
whole final source list when the answer cites >= 1 (answerBridge.ts:224). trunc = answer ends without terminal punctuation after stripping
trailing [n] marks / markdown, or tokens >= the 512 cap."""
import json, re, glob, sys
X6 = "<workspace>/boar-eval/runs/device-poco-x6pro"
def dups(xs): seen, d = set(), 0
def ndup(xs):
    seen, d = set(), 0
    for x in xs:
        k = (x or "").strip().lower()
        if k in seen: d += 1
        seen.add(k)
    return d
def trunc(text):
    s = re.sub(r"(\s*\[\d+(?:[,-]\s*\d+)*\])+\s*$", "", text.strip()).rstrip("*_` \n")
    return bool(s) and not re.search(r"[.!?)\]\"'”’:…]$", s)
L = lambda v: v if isinstance(v, list) else (eval(v) if isinstance(v, str) and v.startswith("[") else [])
out = {"desktop": [], "x6_phone": {}, "x6_native": {}}
for f in ["runs/w1.traces.jsonl", "runs/w2.traces.jsonl", "runs/w3.traces.jsonl"]:
    for l in open(f):
        t = json.loads(l); ev = [e for e in t["events"] if e["type"] == "sources"]; src = ev[-1]["sources"] if ev else []
        a = t["answer"]; cited = a.get("cited") or []
        out["desktop"].append({"id": t["itemId"], "tier": t["route"]["tier"], "nSources": len(src), "dupTitle": ndup([s["title"] for s in src]),
            "dupUrl": ndup([s.get("source") for s in src]), "appShown": len(cited) > 0, "outTokens": t["timing"].get("outputTokens"),
            "trunc": trunc(a["text"]), "thinkingBudgetExceeded": t["route"].get("thinkingBudgetExceeded"),
            "reasonCodes": t["route"]["reasonCodes"], "text150": a["text"][:150]})
D = out["desktop"]
out["desktop_summary"] = {"n": len(D), "withDupTitle": sum(d["dupTitle"] > 0 for d in D), "dupTitleEntries": sum(d["dupTitle"] for d in D),
    "withDupUrl": sum(d["dupUrl"] > 0 for d in D), "withDupShownInApp": sum(d["dupTitle"] > 0 and d["appShown"] for d in D),
    "trunc": sum(d["trunc"] for d in D), "atCap": sum((d["outTokens"] or 0) >= 512 for d in D), "maxOut": max(d["outTokens"] or 0 for d in D)}
P = [json.loads(l) for l in open(f"{X6}/final-cut7-v01/rows.jsonl")]
gen = [p for p in P if int(p["tokensGenerated"] or 0) > 0]
out["x6_phone"] = {"rows": len(P), "withRetrieved": sum(bool(L(p["retrievedTitles"])) for p in P),
    "withDupRetrievedTitle": sum(ndup(L(p["retrievedTitles"])) > 0 for p in P), "dupRetrievedEntries": sum(ndup(L(p["retrievedTitles"])) for p in P),
    "withDupCitedTitle": sum(ndup(L(p["citedTitles"])) > 0 for p in P), "llmRows": len(gen),
    "trunc": [p["queryId"] for p in gen if trunc(p["answer"])], "atCap": [p["queryId"] for p in P if int(p["tokensGenerated"] or 0) >= int(p["maxTokens"])],
    "maxTokensGenerated": max(int(p["tokensGenerated"] or 0) for p in P), "timedOut": sum(str(p["timedOut"]) == "True" for p in P)}
N = [json.loads(l) for f in glob.glob(f"{X6}/native-x6-v01/raw/eval-*.jsonl") for l in open(f)]
out["x6_native"] = {"rows": len(N), "withRetrieved": sum(bool(L(p["retrievedTitles"])) for p in N),
    "withDupRetrievedTitle": sum(ndup(L(p["retrievedTitles"])) > 0 for p in N), "dupRetrievedEntries": sum(ndup(L(p["retrievedTitles"])) for p in N),
    "trunc": [p["queryId"] for p in N if trunc(p["answer"])], "atCap": [p["queryId"] for p in N if int(p["tokensGenerated"] or 0) >= int(p["maxTokens"])],
    "maxTokensGenerated": max(int(p["tokensGenerated"] or 0) for p in N), "timedOut": sum(str(p["timedOut"]) == "True" for p in N)}
json.dump(out, open("aggregates/phonefail.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps({k: v for k, v in out.items() if k != "desktop"}, indent=1, ensure_ascii=False))
for d in D: print(d["id"], d["nSources"], d["dupTitle"], d["dupUrl"], d["appShown"], d["outTokens"], d["trunc"])
