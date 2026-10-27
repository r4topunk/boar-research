#!/usr/bin/env python3
"""PIN2-SCREEN section 1 (0 LLM): total kept tokens arm/base per set + compressor tokensAfter vs its own budget. python3 -I tools/screen_ctx.py -> screen_ctx.json"""
import json, math, re
D = "<workspace>/rnd/research/coordinator/arms/coverage-map/pin2"
rd = lambda f: {r["id"]: r for r in (json.loads(l) for l in open(f) if l.strip())}
tok = lambda r: sum(math.ceil(len(c["title"] + "\n" + c["body"]) / 4) for c in r["keptFull"])
out = {}
for s, n in (("main", 97), ("t27", 27)):
    B, X = rd(f"{D}/replays/{s}.off.jsonl"), rd(f"{D}/replays/{s}.PIN2.jsonl"); assert len(B) == len(X) == n
    tb, tx = sum(tok(B[i]) for i in B), sum(tok(X[i]) for i in X)
    over, nocomp, nobud = [], [], []
    for i, r in X.items():
        a = [x for x in r["reasonCodes"] if re.fullmatch(r"context:\d+->\d+", x)]; b = [x for x in r["reasonCodes"] if x.startswith("context:pin2-budget-")]
        if not a: nocomp.append(i); continue
        if not b: nobud.append(i); continue
        after = int(a[0].split("->")[1]); bud = int(b[0].rsplit("-", 1)[1])
        if after > bud: over.append([i, after, bud])
    out[s] = dict(n=n, total_base=tb, total_arm=tx, ratio=round(tx / tb, 4), total_pass=tx / tb <= 1.10, compressor_over_budget=over, no_compressor_call=len(nocomp), compressor_without_budget_code=nobud)
out["PASS"] = all(out[s]["total_pass"] and not out[s]["compressor_over_budget"] and not out[s]["compressor_without_budget_code"] for s in ("main", "t27"))
json.dump(out, open(f"{D}/screen_ctx.json", "w"), indent=1); print(json.dumps(out, indent=1))
