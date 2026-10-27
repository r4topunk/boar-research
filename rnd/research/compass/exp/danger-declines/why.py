import json, collections, glob
B = "<workspace>/boar-eval/"
Q = {json.loads(l)["id"]: json.loads(l) for l in open(B + "bench/v0.1/questions.public.jsonl")}
S = {json.loads(l)["id"]: json.loads(l) for l in open("<workspace>/rnd/bench/safety/track.v0.3.jsonl")}
danger = {q for q, r in Q.items() if r.get("danger")} | set(S)
C = collections.Counter(); rows = []
for f in sorted(glob.glob(B + "runs/night-2026-10-01/ios-main-s4[234].traces.jsonl")):
    for l in open(f):
        t = json.loads(l)
        if t["itemId"] not in danger: continue
        a = t["answer"]; codes = [c for c in t["route"]["reasonCodes"] if c.startswith(("grounding:", "health", "weak", "decline", "card", "firstaid", "instant"))]
        state = "card" if any("no-source" in c or "card" in c for c in codes) else "declined" if a["declined"] else ("sourced" if a.get("shown") else "memory")
        C[state] += 1
        rows.append((f.split("/")[-1][:12], t["itemId"], state, [s for s in a.get("shown") or []][:2], codes[:6], [s["title"] for s in t["retrieval"].get("raw", [])][:4]))
print(C)
for r in rows:
    if r[2] in ("declined", "memory"): print(r)
