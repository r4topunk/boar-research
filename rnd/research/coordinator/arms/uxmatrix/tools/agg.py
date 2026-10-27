#!/usr/bin/env python3
"""UXMATRIX aggregate (0 LLM). python3 -I agg.py -> ../aggregates/uxmatrix.json, ../aggregates/matrix.md
Final label per unit: A; if A borderline and B exists: A==B -> A; else C exists -> majority of A/B/C (all differ -> A, flagged); B/C missing -> A (flagged single).
gen-nopack items: ON row reused for OFF (ON = OFF). Shares over items; CI = item bootstrap B 2000 random.Random(11), paired ON-OFF on the 55 items with an OFF state."""
import json, random, collections, os
U = "<workspace>/rnd/research/coordinator/arms/uxmatrix"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
ANS = json.load(open(U + "/judge/answers.json")); IT = json.load(open(U + "/items.json"))["items"]
LAB = ["CORRECT_WITH_SOURCE", "CORRECT_FROM_MEMORY", "HONEST_UNKNOWN", "REFUSED_WRONGLY", "WRONG_WARNED", "WRONG_CONFIDENT"]
AB = dict(zip(LAB, ["CWS", "CFM", "HU", "RW", "WW", "WC"]))
L = collections.defaultdict(dict)
for r in rd(U + "/judge/labels.jsonl"):
    if r["ok"]: L[r["key"]][r["call"]] = r
flags = collections.Counter()
def final(k):
    c = L.get(k)
    if not c or "A" not in c: return None, None
    A = c["A"]
    if A["conf"] != "borderline": return A["label"], A["source_holds"]
    if "B" not in c: flags["single"] += 1; return A["label"], A["source_holds"]
    if c["B"]["label"] == A["label"]: return A["label"], A["source_holds"]
    if "C" not in c: flags["single"] += 1; return A["label"], A["source_holds"]
    v = collections.Counter([A["label"], c["B"]["label"], c["C"]["label"]]).most_common(1)[0]
    if v[1] == 1: flags["three-way"] += 1; return A["label"], A["source_holds"]
    w = next(x for x in (A, c["B"], c["C"]) if x["label"] == v[0]); return w["label"], w["source_holds"]
W = "Not found in this phone's offline library. From the model's memory, may be wrong:"; H = "I don't have a reliable offline source"
rows = {}
for x in IT:
    for m in ("succinct", "detailed", "deep"):
        for st in ("on", "off"):
            a = ANS.get(f"{m}|{st}|{x['id']}") or (ANS.get(f"{m}|on|{x['id']}") if not x["off_minus"] and st == "off" else None)
            if a is None: continue
            lab, sh = final(a["key"])
            rows[(m, st, x["id"])] = dict(a, label=lab, source_holds=sh, warn=a["text"].startswith(W), hdecl=a["text"].startswith(H), cls=x["cls"])
def share(xs):
    n = len(xs); c = collections.Counter(rows[k]["label"] for k in xs)
    return dict(n=n, unlabelled=c.get(None, 0), **{AB[l]: round(c.get(l, 0) / n, 3) if n else None for l in LAB}, counts={AB[l]: c.get(l, 0) for l in LAB})
def surf(xs):
    n = len(xs); g = lambda f: round(sum(f(rows[k]) for k in xs) / n, 3) if n else None
    med = lambda v: sorted(v)[len(v) // 2] if v else None
    return dict(n=n, warn_line=g(lambda r: r["warn"]), health_decline=g(lambda r: r["hdecl"]), declined=g(lambda r: r["declined"]), passages_found_line=0.0,
                zero_sources=g(lambda r: r["shown"] == 0), shown_mean=g(lambda r: r["shown"]), cited_mean=g(lambda r: r["cited"]), cited_any=g(lambda r: r["cited"] > 0),
                outTok_mean=g(lambda r: r["outTok"] or 0), totalMs_p50=med([rows[k]["totalMs"] for k in xs if rows[k]["totalMs"]]), hosts=sorted({rows[k]["host"][:20] for k in xs}))
CLS = {"all": None, "cm": "cm", "gen-delivered": "gen-delivered", "gen-nopack": "gen-nopack"}
res = dict(matrix={}, surface={}, deltas={}, flags=None, n_rows=len(rows))
for m in ("succinct", "detailed", "deep"):
    for st in ("on", "off"):
        for cn, cv in CLS.items():
            xs = [k for k in rows if k[0] == m and k[1] == st and (cv is None or rows[k]["cls"] == cv)]
            res["matrix"][f"{m}|{st}|{cn}"] = share(xs); res["surface"][f"{m}|{st}|{cn}"] = surf(xs)
def boot(ids, f, B=2000):
    r = random.Random(11); v = sorted(f([r.choice(ids) for _ in ids]) for _ in range(B)); return [round(v[int(.025 * B)], 3), round(v[int(.975 * B) - 1], 3)]
corr = lambda l: l in ("CORRECT_WITH_SOURCE", "CORRECT_FROM_MEMORY")
for m in ("succinct", "detailed", "deep"):
    for cn, cv in (("all-with-off", None), ("cm", "cm"), ("gen-delivered", "gen-delivered")):
        ids = [x["id"] for x in IT if x["off_minus"] and (cv is None or x["cls"] == cv) and (m, "on", x["id"]) in rows and (m, "off", x["id"]) in rows and rows[(m, "on", x["id"])]["label"] and rows[(m, "off", x["id"])]["label"]]
        if not ids: continue
        d = {}
        for nm, f in (("CWS", lambda l: l == "CORRECT_WITH_SOURCE"), ("correct", corr), ("WC", lambda l: l == "WRONG_CONFIDENT"), ("HU", lambda l: l == "HONEST_UNKNOWN")):
            g = lambda s, f=f: sum(f(rows[(m, "on", i)]["label"]) - f(rows[(m, "off", i)]["label"]) for i in s) / len(s)
            d[nm] = dict(on_minus_off=round(g(ids), 3), ci=boot(ids, g))
        res["deltas"][f"{m}|{cn}"] = dict(n=len(ids), **d)
# mode-vs-mode paired (same state), correct and WC, on items present in both
for st in ("on", "off"):
    for a, b in (("detailed", "succinct"), ("deep", "succinct"), ("deep", "detailed")):
        ids = [x["id"] for x in IT if (a, st, x["id"]) in rows and (b, st, x["id"]) in rows and rows[(a, st, x["id"])]["label"] and rows[(b, st, x["id"])]["label"]]
        if not ids: continue
        d = {}
        for nm, f in (("correct", corr), ("WC", lambda l: l == "WRONG_CONFIDENT"), ("CWS", lambda l: l == "CORRECT_WITH_SOURCE")):
            g = lambda s, f=f: sum(f(rows[(a, st, i)]["label"]) - f(rows[(b, st, i)]["label"]) for i in s) / len(s)
            d[nm] = dict(d=round(g(ids), 3), ci=boot(ids, g))
        res["deltas"][f"{a}-{b}|{st}"] = dict(n=len(ids), **d)
res["flags"] = dict(flags)
res["per_item"] = {f"{k[0]}|{k[1]}|{k[2]}": dict(label=v["label"], source_holds=v["source_holds"], warn=v["warn"], shown=v["shown"], cls=v["cls"], group=v["group"]) for k, v in rows.items()}
os.makedirs(U + "/aggregates", exist_ok=True); json.dump(res, open(U + "/aggregates/uxmatrix.json", "w"), indent=1)
# markdown tables
o = []
for cn in CLS:
    o.append(f"\n### {cn}\n| mode | state | n | CWS | CFM | HU | RW | WW | WC |\n|---|---|---|---|---|---|---|---|---|")
    for m in ("succinct", "detailed", "deep"):
        for st in ("on", "off"):
            s = res["matrix"][f"{m}|{st}|{cn}"]
            if not s["n"]: continue
            o.append(f"| {m} | {st.upper()} | {s['n']}{' (' + str(s['unlabelled']) + ' unlabelled)' if s['unlabelled'] else ''} | " + " | ".join(f"{s[AB[l]]:.2f}" for l in LAB) + " |")
o.append("\n### UX surface (all items)\n| mode | state | n | Not-found warning line | health decline | 0 sources | sources shown (mean) | any citation | out tokens (mean) | total ms p50 | host |\n|---|---|---|---|---|---|---|---|---|---|---|")
for m in ("succinct", "detailed", "deep"):
    for st in ("on", "off"):
        s = res["surface"][f"{m}|{st}|all"]
        if s["n"]: o.append(f"| {m} | {st.upper()} | {s['n']} | {s['warn_line']:.2f} | {s['health_decline']:.2f} | {s['zero_sources']:.2f} | {s['shown_mean']:.1f} | {s['cited_any']:.2f} | {s['outTok_mean']:.0f} | {s['totalMs_p50']:.0f} | {','.join(s['hosts'])} |")
o.append("\n### Deltas\n| comparison | n | CWS | correct | WC | HU |\n|---|---|---|---|---|---|")
for k, v in res["deltas"].items():
    f = lambda nm: (f"{v[nm].get('on_minus_off', v[nm].get('d')):+.3f} ({v[nm]['ci'][0]:+.2f}..{v[nm]['ci'][1]:+.2f})" if nm in v else "-")
    o.append(f"| {k} | {v['n']} | {f('CWS')} | {f('correct')} | {f('WC')} | {f('HU')} |")
o.append(f"\nflags {dict(flags)}; rows {len(rows)}")
open(U + "/aggregates/matrix.md", "w").write("\n".join(o) + "\n"); print("\n".join(o))
