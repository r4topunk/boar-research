#!/usr/bin/env python3 -I
"""DEVICE-FINAL M3/M4 aggregate (0 LLM). usage: m34_agg.py m3|m4 <answers.json> <labels.jsonl> <out.json>
Label resolution = uxmatrix/tools/agg.py final(): A; if A borderline and B exists: A==B -> A, else C -> majority of A/B/C (all differ -> A, flagged); B/C missing -> A (flagged single).
Shares over items (single state = ON, one seed); CI = item bootstrap B 2000, random.Random(11).
CWS = CORRECT_WITH_SOURCE; correct_any = CWS + CORRECT_FROM_MEMORY; WU = WRONG_CONFIDENT (wrong, no warning); WW = WRONG_WARNED; wrong_any = WW + WC.
On the phone every model answer carries 'May contain errors; check the source.', so wrong model answers land in WW (see m34_prep.py)."""
import json, sys, random, collections, re
kind, af, lf, outp = sys.argv[1:5]
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
ANS = json.load(open(af)); LAB = ["CORRECT_WITH_SOURCE", "CORRECT_FROM_MEMORY", "HONEST_UNKNOWN", "REFUSED_WRONGLY", "WRONG_WARNED", "WRONG_CONFIDENT"]
AB = dict(zip(LAB, ["CWS", "CFM", "HU", "RW", "WW", "WC"]))
L = collections.defaultdict(dict)
for r in rd(lf):
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
rows = {}
for i, a in ANS.items():
    lab, sh = final(a["key"]); st = lambda t: re.sub(r"^[^:]{3,40}: ", "", t).strip().lower(); own = {st(o) for o in a["own"]}; match = [t for t in a["titles"] if st(t) in own]
    rows[i] = dict(a, label=lab, source_holds=sh, own_kept=bool(match))
def boot(vals, B=2000):
    r = random.Random(11); v = sorted(sum(r.choice(vals) for _ in vals) / len(vals) for _ in range(B)); return [round(v[int(.025 * B)], 3), round(v[int(.975 * B) - 1], 3)]
def share(xs):
    n = len(xs); c = collections.Counter(rows[k]["label"] for k in xs); lab = n - c.get(None, 0)
    d = dict(n=n, unlabelled=c.get(None, 0), counts={AB[l]: c.get(l, 0) for l in LAB})
    for l in LAB: d[AB[l]] = round(c.get(l, 0) / n, 3) if n else None
    corr = [int(rows[k]["label"] in LAB[:2]) for k in xs if rows[k]["label"]]; cws = [int(rows[k]["label"] == LAB[0]) for k in xs if rows[k]["label"]]
    d.update(correct_any=round(sum(corr) / lab, 3) if lab else None, correct_any_ci=boot(corr) if corr else None, CWS_ci=boot(cws) if cws else None,
             wrong_any=round((c[LAB[4]] + c[LAB[5]]) / n, 3) if n else None, WU=round(c[LAB[5]] / n, 3) if n else None)
    return d
grp = "pack" if kind == "m3" else "cls"
ids = list(rows); res = dict(kind=kind, n=len(ids), all=share(ids), by_layer={}, by_group={}, flags=dict(flags))
for l in sorted({rows[k]["layer"] for k in ids}): res["by_layer"][l] = share([k for k in ids if rows[k]["layer"] == l])
for g in sorted({rows[k][grp] for k in ids}): res["by_group"][g] = share([k for k in ids if rows[k][grp] == g])
res["surface"] = dict(zero_sources=round(sum(rows[k]["n_src"] == 0 for k in ids) / len(ids), 3), any_citation=round(sum(bool(rows[k]["cited"]) for k in ids) / len(ids), 3),
                      sources_mean=round(sum(rows[k]["n_src"] for k in ids) / len(ids), 2), own_article_kept=round(sum(rows[k]["own_kept"] for k in ids) / len(ids), 3) if kind == "m3" else None,
                      chunks_without_desktop_text=sum(rows[k]["n_src_no_text"] for k in ids),
                      latency_ms_p50=sorted(r["totalMs"] for r in rows.values() if r["totalMs"])[len(ids) // 2] if any(r["totalMs"] for r in rows.values()) else None)
if kind == "m3":
    k = [x for x in ids if rows[x]["own_kept"] and rows[x]["label"]]; nk = [x for x in ids if not rows[x]["own_kept"] and rows[x]["label"]]
    f = lambda xs: [round(sum(rows[x]["label"] in LAB[:2] for x in xs) / len(xs), 3) if xs else None, len(xs)]
    res["correct_given_own_article_kept"] = f(k); res["correct_given_not_kept"] = f(nk)
res["per_item"] = {i: dict(label=r["label"], source_holds=r["source_holds"], layer=r["layer"], group=r[grp], n_src=r["n_src"], own_kept=r["own_kept"]) for i, r in rows.items()}
json.dump(res, open(outp, "w"), indent=1)
s = res["all"]; print(f"{kind.upper()} n={s['n']} unlabelled={s['unlabelled']} counts={s['counts']}")
print(f"  CWS {s['CWS']} (CI {s['CWS_ci']})  correct-any {s['correct_any']} (CI {s['correct_any_ci']})  WU(WC) {s['WU']}  wrong-any (WW+WC) {s['wrong_any']}  HU {s['HU']}  RW {s['RW']}")
for g, v in res["by_group"].items(): print(f"  {g:22} n={v['n']:3} CWS {v['CWS']} correct-any {v['correct_any']} wrong-any {v['wrong_any']}")
print("  surface", res["surface"], "flags", dict(flags))
