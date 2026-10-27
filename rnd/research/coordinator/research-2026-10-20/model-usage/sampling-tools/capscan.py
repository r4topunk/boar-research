import json, sys, re, collections, glob
def ng_rep(t, n=4):
    w = re.findall(r"\w+", t.lower())
    c = collections.Counter(tuple(w[i:i+n]) for i in range(len(w)-n+1))
    return max(c.values()) if c else 0
def ends_ok(t):
    t = t.rstrip()
    t = re.sub(r"(\s*\[\d+(,\s*\d+)*\])+$", "", t).rstrip()
    t = re.sub(r"[\*\)\"'”’_`]+$", "", t).rstrip()
    return bool(re.search(r"[.!?:;…]$", t)) or t.endswith("```")
for path in sys.argv[1:]:
    rows = [json.loads(l) for l in open(path) if l.strip()]
    st = collections.defaultdict(lambda: collections.Counter())
    for r in rows:
        tm = r.get("timing") or {}; out = tm.get("outputTokens"); rt = r.get("route") or {}
        tier = rt.get("tier"); txt = (r.get("answer") or {}).get("text") or ""
        rc = rt.get("reasonCodes") or []
        health = any("health" in c for c in rc)
        key = ((r.get("runtime") or {}).get("model"), tier)
        s = st[key]; s["n"] += 1
        if out is None: s["noout"] += 1; continue
        if out >= 512: s["cap512"] += 1
        if 195 <= out <= 200 and tier == "deep": s["cap200"] += 1
        if out >= 400: s["ge400"] += 1
        if not ends_ok(txt) and txt: s["midsent"] += 1
        if ng_rep(txt) >= 4: s["rep4"] += 1
        s["sumout"] += out; s["maxout"] = max(s["maxout"], out)
        if r.get("error"): s["err"] += 1
    for k, s in st.items():
        n = s["n"]; m = s["sumout"]/max(1, n - s["noout"])
        print(f"{path.split('/')[-1][:60]:60s} {k} n={n} meanOut={m:.0f} max={s['maxout']} >=512:{s['cap512']} >=400:{s['ge400']} deep195-200:{s['cap200']} midSent:{s['midsent']} rep4gram>=4:{s['rep4']} err:{s['err']}")
