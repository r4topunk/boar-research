#!/usr/bin/env python3
"""PACKPROOF aggregate (0 LLM). python3 -I agg.py -> ../aggregates/packproof.json + packproof.table.md
Labels: A; if B exists and differs from A -> C; majority of A/B/C (three different -> A, flagged). Funnel by url+title match (criterion). Supplementary cm rows from UXMATRIX Succinct (reused, never pooled)."""
import json, re, random, statistics, os
P = "<workspace>/rnd/research/coordinator/arms/packproof"; U = "<workspace>/rnd/research/coordinator/arms/uxmatrix"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()] if os.path.exists(f) else []
ITEMS = json.load(open(P + "/in/items.json")); PACKS = ITEMS["packs"]; OWN = json.load(open(P + "/in/own.json"))
HEALTH = {"qa-health-se", "boar-firstaid-en", "boar-medlineplus-en"}
def resolve(lf):
    by = {}
    for r in rd(lf):
        if r["ok"]: by.setdefault(r["key"], {})[r["call"]] = r
    out = {}
    for k, c in by.items():
        if "A" not in c: continue
        L = [c[x]["label"] for x in "ABC" if x in c]
        if len(L) == 1 or ("B" in c and c["A"]["label"] == c["B"]["label"] and "C" not in c): out[k] = (c["A"]["label"], "single" if len(L) == 1 else "agree")
        else:
            m = max(set(L), key=L.count); out[k] = (m if L.count(m) >= 2 else c["A"]["label"], "majority" if L.count(m) >= 2 else ("ab_disagree_noC" if len(L) == 2 else "flag3"))
    return out
def match(arts, title, source):
    for a in arts:
        if re.search(re.escape(a["url"]) + r"(?![\w/])", source or "") and a["title"].lower() in title.lower(): return True
    return False
def funnel(a, arts):
    f = dict(retrieved=any(match(arts, t, s) for t, s in a["raw"]), kept=any(match(arts, t, s) for t, s in a["kept"]))
    kt = {t for t, s in a["kept"] if match(arts, t, s)}
    f["shown"] = bool(kt & set(a["shown"])); f["cited"] = bool(kt & set(a["cited"])); return f
CORR = {"CORRECT_WITH_SOURCE", "CORRECT_FROM_MEMORY"}
LABS = ["CORRECT_WITH_SOURCE", "CORRECT_FROM_MEMORY", "HONEST_UNKNOWN", "REFUSED_WRONGLY", "WRONG_WARNED", "WRONG_CONFIDENT"]
BANNER = "Not found in this phone's offline library"; HDECL = "I don't have a reliable offline source"
def boot(pairs, B=2000):
    rng = random.Random(11); n = len(pairs); pt = sum(a - b for a, b in pairs) / n; ds = []
    for _ in range(B):
        s = [pairs[rng.randrange(n)] for _ in range(n)]; ds.append(sum(a - b for a, b in s) / n)
    ds.sort(); return round(pt, 3), round(ds[int(.025 * B)], 3), round(ds[int(.975 * B) - 1], 3)
def summarize(rows):
    """rows: list of dict(id, on=dict(label, funnel, ux...), off=...)"""
    n = len(rows); r = dict(n=n)
    for st in ("on", "off"):
        lab = [x[st]["label"] for x in rows]; nl = sum(l is not None for l in lab) or 1
        r[st] = {l: round(sum(v == l for v in lab) / nl, 3) for l in LABS}; r[st]["labelled"] = sum(l is not None for l in lab)
        r[st]["correct_any"] = round(sum(v in CORR for v in lab) / nl, 3)
        for k in ("retrieved", "kept", "shown", "cited"): r[st][k] = round(sum(x[st]["funnel"][k] for x in rows) / n, 3)
        r[st]["banner"] = round(sum(x[st]["text"].startswith(BANNER) for x in rows) / n, 3); r[st]["health_decline"] = round(sum(x[st]["text"].startswith(HDECL) for x in rows) / n, 3)
        r[st]["declined"] = round(sum(x[st]["declined"] for x in rows) / n, 3); r[st]["sources_shown_mean"] = round(sum(len(x[st]["shown"]) for x in rows) / n, 2)
        ms = [x[st]["totalMs"] for x in rows if x[st]["totalMs"]]; r[st]["time_p50_s"] = round(statistics.median(ms) / 1000, 1) if ms else None
    lab_rows = [x for x in rows if x["on"]["label"] and x["off"]["label"]]
    if lab_rows:
        r["d_correct_any"] = boot([(x["on"]["label"] in CORR, x["off"]["label"] in CORR) for x in lab_rows])
        r["d_cws"] = boot([(x["on"]["label"] == "CORRECT_WITH_SOURCE", x["off"]["label"] == "CORRECT_WITH_SOURCE") for x in lab_rows])
        k = [x for x in lab_rows if x["on"]["funnel"]["kept"]]; nk = [x for x in lab_rows if not x["on"]["funnel"]["kept"]]
        r["on_correct_given_kept"] = [round(sum(x["on"]["label"] in CORR for x in k) / len(k), 3) if k else None, len(k)]
        r["on_correct_given_not_kept"] = [round(sum(x["on"]["label"] in CORR for x in nk) / len(nk), 3) if nk else None, len(nk)]
    return r
def verdict(s):
    ca, wc = s["on"]["correct_any"], s["off"]["WRONG_CONFIDENT"]
    return "PROVES" if ca >= .75 and wc <= .25 else ("DOES NOT PROVE" if ca < .60 else "PARTIAL")
# main 180
L = resolve(P + "/judge/labels.jsonl"); A = json.load(open(P + "/judge/answers.json")) if os.path.exists(P + "/judge/answers.json") else {}
rows = {p: [] for p in PACKS}; flags = {"single": 0, "agree": 0, "majority": 0, "ab_disagree_noC": 0, "flag3": 0}
for it in ITEMS["items"]:
    i = it["id"]; x = dict(id=i)
    for st in ("on", "off"):
        a = A.get(f"{st}|{i}")
        if not a: break
        lab = L.get(a["key"]); x[st] = dict(a, label=lab[0] if lab else None, funnel=funnel(a, OWN[i]))
        if lab: flags[lab[1]] += 1
    else: rows[it["pack"]].append(x)
out = dict(criterion="37f74d6f", per_pack={}, label_resolution=flags)
for p in PACKS:
    if rows[p]: s = summarize(rows[p]); s["verdict"] = verdict(s); s["health"] = p in HEALTH; out["per_pack"][p] = s
allr = [x for p in PACKS for x in rows[p]]
if allr: out["pooled"] = summarize(allr); out["pooled"]["verdict"] = verdict(out["pooled"])
# supplementary cm (UXMATRIX Succinct, reused)
UL = resolve(U + "/judge/labels.jsonl"); UA = json.load(open(U + "/judge/answers.json")) if os.path.exists(U + "/judge/answers.json") else {}
UT = {}
for g in ("on", "off-qa-cooking-se", "off-qa-money-se"):
    for t in rd(f"{U}/gen/succinct/{g}/traces.jsonl"):
        a = t["answer"]; UT[("on" if g == "on" else "off", t["itemId"])] = dict(text=a["text"], declined=bool(a.get("declined")), shown=a.get("shown") or [], cited=a.get("cited") or [],
            raw=[(k["title"], k["source"]) for k in t["retrieval"]["raw"]], kept=[(k["title"], k["source"]) for k in t["retrieval"]["kept"]], totalMs=t["timing"].get("totalMs"))
out["supplementary_uxmatrix"] = {}
for p in ("qa-cooking-se", "qa-money-se"):
    sr = []
    for n in range(1, 21):
        i = f"st-{p}-{n:03d}"; x = dict(id=i)
        for st in ("on", "off"):
            t = UT.get((st, i)); ua = UA.get(f"succinct|{st}|{i}")
            if not t: break
            lab = UL.get(ua["key"]) if ua else None; x[st] = dict(t, label=lab[0] if lab else None, funnel=funnel(t, OWN[i]))
        else: sr.append(x)
    if sr: s = summarize(sr); s["verdict"] = verdict(s) if s["on"]["labelled"] == len(sr) == s["off"]["labelled"] else "labels missing"; out["supplementary_uxmatrix"][p] = s
json.dump(out, open(P + "/aggregates/packproof.json", "w"), indent=1)
def line(name, s):
    on, off = s["on"], s["off"]; d = s.get("d_correct_any", (None,) * 3)
    return (f"| {name} | {s['n']} | {on['CORRECT_WITH_SOURCE']:.2f} | {on['correct_any']:.2f} | {on['REFUSED_WRONGLY']:.2f} | {off['HONEST_UNKNOWN']:.2f} | {off['WRONG_CONFIDENT']:.2f} | {off['WRONG_WARNED']:.2f} | {off['correct_any']:.2f} | "
            f"{d[0]:+.2f} ({d[1]:+.2f}..{d[2]:+.2f}) | {on['retrieved']:.2f} / {on['kept']:.2f} / {on['shown']:.2f} / {on['cited']:.2f} | {on['time_p50_s']} / {off['time_p50_s']} | {s['verdict']} |")
H = "| pack | n | ON CWS | ON correct-any | ON refused-wrongly | OFF honest-unknown | OFF wrong-confident | OFF wrong-warned | OFF correct-any | Δ correct-any ON-OFF (CI) | ON funnel retrieved / kept / shown / cited | time p50 s ON / OFF | verdict |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|"
T = [H] + [line(p + (" (health*)" if p in HEALTH else ""), out["per_pack"][p]) for p in PACKS if p in out["per_pack"]]
if "pooled" in out: T.append(line("**pooled 180**", out["pooled"]))
for p, s in out["supplementary_uxmatrix"].items():
    if s["on"]["labelled"]: T.append(line(p + " (UXMATRIX reuse, not pooled)", s))
open(P + "/aggregates/packproof.table.md", "w").write("\n".join(T) + "\n"); print("\n".join(T)); print(flags)
