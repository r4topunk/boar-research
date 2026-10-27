# Pre-registered replay (card unconfirmed-draft-cosine-gate, frozen threshold 0.70): newly shown d1a answers on slice40 s42.
import json, sys, re, collections
sys.path.insert(0, "../verify"); 
R = "<workspace>/boar-eval/runs/night-2026-10-01/d1/"
ACR, UWS = "grounding:all-citations-removed-declined-compact", "grounding:uncited-with-sources-declined-compact"
rd = lambda f: {json.loads(l)["itemId"]: json.loads(l) for l in open(R + f)}
main, arm = rd("ios-main-slice40-s42.traces.jsonl"), rd("ios-d1a-slice40-s42.traces.jsonl")
J = collections.defaultdict(list)
for l in open(R + "ios-d1a-slice40-s42.judgments.jsonl"):
    r = json.loads(l)
    if r.get("ok"): J[r["queryId"]].append(r["mapped"]["boar"]["correctness"])
exec(open("../verify/collect.py").read().split("CODES =")[0].split("out, seen")[0])  # reuse article() + packs
out = []
for q, m in main.items():
    codes = m["route"]["reasonCodes"]
    if not (m["answer"]["declined"] and any(c in codes for c in (ACR, UWS))): continue
    a = arm.get(q)
    if not a or a["answer"]["declined"]: continue
    draft = "".join(e.get("text", "") for e in a["events"] if e["type"] == "token").strip()
    c = J.get(q); corr = sum(c) / len(c) if c and len(c) == 2 else None
    lab = None if corr is None else ("pass" if corr >= 4 else "cw" if corr <= 1.0 else "fail")
    titles = list(dict.fromkeys((a["answer"].get("shown") or []) + [s["title"] for s in a["retrieval"].get("raw", [])]))
    out.append({"id": q, "pt": q.endswith("-pt"), "label": lab, "corr": corr, "draft": draft, "question": a["question"],
                "sources": [{"title": t, "text": (article(t) or "")[:6000]} for t in titles[:4]],
                "unconfirmed": any("unconfirmed-shown" in x for x in a["route"]["reasonCodes"])})
json.dump(out, open("drafts.json", "w"), ensure_ascii=False)
print(len(out), collections.Counter((o["pt"], o["label"]) for o in out), "unconfirmed-coded", sum(o["unconfirmed"] for o in out),
      "with text", sum(any(s["text"] for s in o["sources"]) for o in out))
