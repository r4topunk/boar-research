#!/usr/bin/env python3
"""UXMATRIX requests (0 LLM). python3 -I mk_req.py -> ../in/<mode>/<group>.requests.jsonl
Template = coverage-map/sefix/ans-req/sefix124-main-s42.requests.jsonl (SEFIX-124 K13 kit, settings quickFirst/packHeadPass a2/packDense2 append-budget, seed 42).
Modes: succinct = settings unchanged (adapter default persona = the app's DEFAULT_PERSONALITY_ID 'succinct'; tree maxTokens 512);
detailed = + personalityId 'detailed' (tree maxTokens 1024, PARA135 app setting); deep = + personalityId 'detailed' + alwaysComplete true (tree maxTokens 2048, DEEPMODE).
Groups: 'on' = all 60 items, K13; 'off-<packs>' = items whose OFF kit is K13 minus <packs> (gen-nopack items have no OFF group: ON = OFF)."""
import json, os, collections
A = "<workspace>/rnd/research/coordinator/arms"; U = A + "/uxmatrix"
T = {json.loads(l)["item"]["id"]: json.loads(l) for l in open(A + "/coverage-map/sefix/ans-req/sefix124-main-s42.requests.jsonl")}
IT = json.load(open(U + "/items.json"))["items"]
for mode in ("succinct", "detailed", "deep"):
    G = collections.defaultdict(list)
    for x in IT:
        G["on"].append((x, [])); 
        if x["off_minus"]: G["off-" + "+".join(x["off_minus"])].append((x, x["off_minus"]))
    os.makedirs(f"{U}/in/{mode}", exist_ok=True)
    for g, rows in G.items():
        out = []
        for x, minus in rows:
            r = json.loads(json.dumps(T[x["id"]])); s = r["config"]["settings"]
            if mode != "succinct": s["personalityId"] = "detailed"
            if mode == "deep": s["alwaysComplete"] = True
            r["config"]["kit"] = [k for k in r["config"]["kit"] if k["id"] not in minus]; assert len(r["config"]["kit"]) == 13 - len(minus)
            r["runId"] = f"uxm-{mode}-{g}-s42"; r["config"]["arm"] = "cut7-headpass-x2+litepacks+sefix124+uxm-" + mode; out.append(json.dumps(r, ensure_ascii=False))
        open(f"{U}/in/{mode}/{g}.requests.jsonl", "w").write("\n".join(out) + "\n")
    print(mode, {g: len(v) for g, v in G.items()}, sum(len(v) for v in G.values()))
