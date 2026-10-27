"""LITEREACH2 stage 2 run gate (0 LLM): 20 rows, 0 errors, 0 empty, 0 reasoning tokens, no <think>; kept (title, section) list and appended ids = step-0 b20 replay on >= 18/20."""
import json, sys
L = "<workspace>/rnd/research/coordinator/arms/litereach2"
ids = [l.strip() for l in open(f"{L}/random20-st180-s888.ids") if l.strip()]
T = {(t := json.loads(l))["itemId"]: t for l in open(f"{L}/runs/r20.all.traces.jsonl") if l.strip()}
P = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se", "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
R = {(l := json.loads(x))["id"]: l for p in P for x in open(f"{L}/runs/step0/b20.{p}.jsonl") if x.strip()}
err = sum(T[i]["error"] is not None for i in ids); empty = sum(not (T[i]["answer"]["text"] or "").strip() for i in ids)
rt = sum((T[i]["timing"].get("reasoningTokens") or 0) > 0 for i in ids); th = sum("<think>" in (T[i]["answer"]["text"] or "") for i in ids)
app = lambda t: [x.split(":add:")[1] for x in t["route"]["reasonCodes"] if x.startswith(("headpass:add:", "headpass:dense:add:"))]
kept_same = sum([[k["title"], k.get("section")] for k in T[i]["retrieval"]["kept"]] == [[k["title"], k.get("section")] for k in R[i]["kept"]] and app(T[i]) == R[i]["appended"] for i in ids)
res = {"n": len(set(ids) & set(T)), "errors": err, "empty": empty, "reasoning_items": rt, "think": th, "kept_and_appended_eq_replay": kept_same}
res["verdict"] = "PASS" if res["n"] == 20 and err == empty == rt == th == 0 and kept_same >= 18 else "FAIL"
json.dump(res, open(f"{L}/aggregates/gate-r20.json", "w"), indent=1); print(json.dumps(res)); sys.exit(0 if res["verdict"] == "PASS" else 8)
