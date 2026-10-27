# Aggregate per (model, tier): answer tokens (outputTokens - reasoningTokens), cap hits, mid-sentence endings, 4-gram loops.
import json, sys, re, collections
def rep(t, n=4):
    w = re.findall(r"\w+", t.lower()); c = collections.Counter(tuple(w[i:i+n]) for i in range(len(w)-n+1))
    return max(c.values()) if c else 0
def ends_ok(t):
    t = t.rstrip(); t = re.sub(r"(\s*\[\d+(,\s*\d+)*\])+$", "", t).rstrip(); t = re.sub(r"[\*\)\"'”’_`]+$", "", t).rstrip()
    return bool(re.search(r"[.!?:;…]$", t)) or t.endswith("```")
agg = collections.defaultdict(collections.Counter); ex = collections.defaultdict(list)
for path in sys.argv[1:]:
    for l in open(path):
        try: r = json.loads(l)
        except Exception: continue
        if "timing" not in r or not isinstance(r.get("runtime"), dict): continue
        tm = r["timing"] or {}; out = tm.get("outputTokens")
        if not out: continue
        rt = r.get("route") or {}; tier = rt.get("tier"); model = r["runtime"].get("model")
        be = r["runtime"].get("backend", "node")
        ans = out - (tm.get("reasoningTokens") or 0)
        txt = (r.get("answer") or {}).get("text") or ""
        k = (model, tier, be); s = agg[k]; s["n"] += 1; s["sum"] += ans; s["max"] = max(s["max"], ans)
        cap = 200 if tier == "deep" else 512
        if ans >= cap - 3: s["cap"] += 1; ex[k].append((path.split('/')[-1], r.get("itemId"), ans, txt[-80:]))
        if rt.get("thinkingBudgetExceeded"): s["budgetX"] += 1
        if txt and not ends_ok(txt): s["mid"] += 1
        if rep(txt) >= 4: s["rep"] += 1
for k, s in sorted(agg.items(), key=lambda x: -x[1]["n"]):
    n = s["n"]; print(f"{str(k):55s} n={n:5d} meanAns={s['sum']/n:6.1f} max={s['max']:5d} atCap={s['cap']}({100*s['cap']/n:.1f}%) midSent={s['mid']}({100*s['mid']/n:.1f}%) loop4g={s['rep']} budgetX={s['budgetX']}")
for k, v in ex.items():
    for e in v[:4]: print("  CAP", k[0], k[1], e)
