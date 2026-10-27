#!/usr/bin/env python3
"""MINI-BASELINE diff (0 LLM). Usage: python3 -I mini_vs_macbook.py [--json out.json]
Per item, MacBook LITEPACKS K1 trace (traces/lp-K1-{cm,v01}-s42) vs the mini same-request trace (traces/mini/lp-K1-{cm,v01}-s42.mini): answer text byte-identical,
first-32-word identity, route (outcome, tier, reasonCodes, declined, warnings), sources (retrieval.kept and raw as (title, section, source) lists, dropped, answer.shown),
promptTokens. Also reports the subset in arms/lp-screens/main-97.ids and, when present, mini-vs-mini determinism vs the older mini control (lp-screens/control)."""
import json, sys, os, hashlib
A = "<workspace>/rnd/research/coordinator/arms"; LP = A + "/litepacks"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
main97 = set(open(A + "/lp-screens/main-97.ids").read().split())
src = lambda l: [(k.get("title"), k.get("section"), k.get("source")) for k in l]
# post-generation reason codes depend on the answer text (citation rewrites, uncited/released grounding); everything else is the pre-generation route
post = lambda c: c.startswith("citations:") or c.startswith("grounding:compact-decline-released") or c.startswith("grounding:uncited") or c.startswith("verdict-guard:")
core = lambda t: [c for c in t["route"]["reasonCodes"] if not post(c)]
w32 = lambda t: t.split()[:32]
def cmp(a, b):
    return dict(text=a["answer"]["text"] == b["answer"]["text"], w32=w32(a["answer"]["text"]) == w32(b["answer"]["text"]),
        kept=src(a["retrieval"]["kept"]) == src(b["retrieval"]["kept"]), raw=src(a["retrieval"]["raw"]) == src(b["retrieval"]["raw"]),
        dropped=src(a["retrieval"].get("dropped") or []) == src(b["retrieval"].get("dropped") or []), shown=a["answer"]["shown"] == b["answer"]["shown"],
        route_core=(a["route"]["outcome"], a["route"]["tier"], a["answer"]["declined"], core(a)) == (b["route"]["outcome"], b["route"]["tier"], b["answer"]["declined"], core(b)),
        route=(a["route"]["outcome"], a["route"]["tier"], a["route"]["reasonCodes"], a["answer"]["declined"], a["answer"].get("warnings"))
              == (b["route"]["outcome"], b["route"]["tier"], b["route"]["reasonCodes"], b["answer"]["declined"], b["answer"].get("warnings")),
        tokens=a["timing"]["promptTokens"] == b["timing"]["promptTokens"])
rows = {}
tot = {"mac_wall": 0.0, "mini_wall": 0.0}
for s in ("cm", "v01"):
    mac = {t["itemId"]: t for t in rd(f"{LP}/traces/lp-K1-{s}-s42.traces.jsonl")}
    mini = {t["itemId"]: t for t in rd(f"{LP}/traces/mini/lp-K1-{s}-s42.mini.traces.jsonl")}
    assert set(mac) == set(mini), (s, set(mac) ^ set(mini))
    for i in mac:
        r = cmp(mac[i], mini[i]); r["set"] = s; r["mini_err"] = bool(mini[i].get("error")); rows[i] = r
        tot["mac_wall"] += mac[i]["timing"]["totalMs"] or 0; tot["mini_wall"] += mini[i]["timing"]["totalMs"] or 0
# older mini control (lpctl-K1-main) vs the new mini baseline: determinism on the mini
ctl = {}
cf = A + "/lp-screens/control/traces/lpctl-K1-main-s42.traces.jsonl"
if os.path.exists(cf):
    ctl = {t["itemId"]: t for t in rd(cf)}
    for s in ("cm", "v01"):
        for t in rd(f"{LP}/traces/mini/lp-K1-{s}-s42.mini.traces.jsonl"):
            if t["itemId"] in ctl:
                c = cmp(ctl[t["itemId"]], t); rows[t["itemId"]]["ctl_text"] = c["text"]; rows[t["itemId"]]["ctl_kept"] = c["kept"]
def summ(ids, label):
    n = len(ids); f = lambda k: sum(rows[i][k] for i in ids)
    o = dict(label=label, n=n, text=f("text"), w32=f("w32"), kept=f("kept"), raw=f("raw"), dropped=f("dropped"), shown=f("shown"), route_core=f("route_core"), route_all=f("route"), tokens=f("tokens"))
    c = [i for i in ids if "ctl_text" in rows[i]]
    if c: o["mini_vs_oldctl_n"] = len(c); o["mini_vs_oldctl_text"] = sum(rows[i]["ctl_text"] for i in c)
    return o
S = [summ(list(rows), "all 100 (cm 40 + v01 60)"), summ([i for i in rows if i in main97], "MAIN 97"),
     summ([i for i in rows if rows[i]["set"] == "cm"], "cm 40"), summ([i for i in rows if rows[i]["set"] == "v01"], "v01 60")]
for o in S: print(" | ".join(f"{k} {v}" for k, v in o.items()))
bad = [i for i in rows if not (rows[i]["kept"] and rows[i]["raw"] and rows[i]["route_core"] and rows[i]["tokens"])]
print("retrieval/route_core/token differences:", bad if bad else "none")
print(f"sum totalMs: MacBook {tot['mac_wall']/1000:.0f} s, mini {tot['mini_wall']/1000:.0f} s; mini errors: {sum(r['mini_err'] for r in rows.values())}")
if "--json" in sys.argv:
    json.dump(dict(summary=S, differences=bad, wall_ms=tot, items=rows), open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
