#!/usr/bin/env python3
"""HON-8 REVEAL-RULE (criterion ruler/RV1-HON8-criterion.md, sha checked). 0 LLM. Usage: python3 -I hon8_reveal.py <out.json>
Rows = tools/warncal_showanyway.py data section (exec'd unchanged; row() wrapped to add cited / first-content-sentence-cited). Haiku labels; Opus labels from WARN-OPUS + CE-OPUS-RU."""
import json, glob, sys, os, hashlib, collections, math, random
C0 = "<workspace>/rnd/research/coordinator"; RU = C0 + "/ruler/"; A = C0 + "/arms/"
CRIT = open(RU + "RV1-HON8-criterion.sha256").read().split()[0]
assert hashlib.sha256(open(RU + "RV1-HON8-criterion.md", "rb").read()).hexdigest() == CRIT
WSRC = RU + "tools/warncal_showanyway.py"; src = open(WSRC).read()
NS = {"__file__": WSRC, "__name__": "warncal_data"}
exec(src[:src.index("R = []")], NS)
_row = NS["row"]
def row2(s_, arm, i, t, j):
    r = _row(s_, arm, i, t, j); d = NS["done_ev"](t); tx = t["answer"]["text"]; body = d.get("finalText") or tx
    if body.startswith(NS["W"]): body = body[len(NS["W"]):].strip()
    cited = d.get("cited") or []
    wr = {"text": body, "cited": cited, "kept": [(k.get("title"), k.get("source")) for k in t["retrieval"]["kept"]], "codes": t["route"]["reasonCodes"]}
    try: unc, n, first = NS["WS"]["coverage"](wr)
    except Exception as e: unc, n, first = [], 0, False
    r.update(cited_n=len(cited), first_cited=bool(first) and len(cited) > 0, sent_n=n, sha16=hashlib.sha256(tx.encode()).hexdigest()[:16])
    return r
NS["row"] = row2
exec(src[src.index("R = []"):src.index("def wilson")], NS)
R = NS["R"]; LP = [r for r in R if r["src"] == "LP"]; MINI = [r for r in R if r["src"] == "MINI"]
# Opus labels
def jl(files):
    by = collections.defaultdict(dict)
    for f in files:
        for l in open(f):
            x = json.loads(l)
            if x.get("ok") is True: by[x["queryId"]][x["order"]] = x["mapped"]["boar"]["correctness"]
    return {q: sum(v.values()) / 2 for q, v in by.items() if len(v) == 2}
Dw = json.load(open(RU + "warn-opus/in/set.json")); ru = jl(glob.glob(A + "refuse-unsupported/ce-opus-ru/out/*.judgments.jsonl")); OP = {}
for k, j in Dw["judge"].items():
    if j["reuse_ceopusru"]: OP[k] = ru[j["id"]]
    else:
        un = "v01" if not j["id"].startswith("st-") else j["id"][3:].rsplit("-", 1)[0]
        OP[k] = jl([RU + f"warn-opus/out/{j['arm']}-{un}.judgments.jsonl"])[j["id"]]
def opus(r):
    k = f'{r["id"]}|{r["sha16"]}'
    if k in OP: return OP[k], k
    if r["src"] == "LP" and r["arm"] == "K3" and r["id"] in ru: return ru[r["id"]], f'ru|{r["id"]}|{r["sha16"]}'
    return None, None
for r in R: r["opus_corr"], r["opus_key"] = opus(r)
FA = lambda r: r["id"].startswith("st-boar-firstaid-en") or r["id"].startswith("dng-")
C = {"C1 warned-but-cited-nh": lambda r: r["w"] and r["bucket"] != "W:all-citations-removed" and r["cited_n"] > 0 and not r["health"],
     "C2 warned-first-cited-nh": lambda r: r["w"] and r["bucket"] != "W:all-citations-removed" and r["cited_n"] > 0 and r["first_cited"] and not r["health"],
     "C3 first-aid": FA,
     "C4 no-source-no-warning-nh": lambda r: r["bucket"] == "U:no-kept(banner)" and not r["health"],
     "C5 warned-no-source-nh": lambda r: r["bucket"] == "W:no-source" and not r["health"],
     "C6 C1-or-C4-nh": lambda r: not r["health"] and ((r["w"] and r["bucket"] != "W:all-citations-removed" and r["cited_n"] > 0) or r["bucket"] == "U:no-kept(banner)")}
def wil(k, n, z=1.96):
    if n == 0: return None
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d; return [c - h, c + h]
def ratio_ci(k, c):
    w = wil(k, k + c)
    if w is None: return None
    f = lambda p: round(p / (1 - p), 3) if p < 1 else float("inf")
    return [f(w[0]), f(w[1])]
def cboot(rows, B=2000, seed=11):
    by = collections.defaultdict(list)
    for r in rows: by[r["id"]].append(r)
    ids = sorted(by); rnd = random.Random(seed); xs = []
    for _ in range(B):
        s = [x for _ in ids for x in by[ids[rnd.randrange(len(ids))]]]; k = sum(x["correct"] for x in s); c = sum(x["CE"] for x in s)
        xs.append(k / c if c else float("inf"))
    xs.sort(); return [round(xs[int(0.025 * B)], 3), round(xs[int(0.975 * B) - 1], 3)] if ids else None
def stats(rows, nrev, boot=True):
    k = sum(r["correct"] for r in rows); c = sum(r["CE"] for r in rows); hce = [f'{r["src"]}-{r["arm"]}-{r["id"]}' for r in rows if r["CE"] and r["health"]]
    return dict(rows=len(rows), items=len({r["id"] for r in rows}), coverage=round(len(rows) / nrev, 3) if nrev else None, correct=k, ce=c, partial=len(rows) - k - c,
                ratio=round(k / c, 3) if c else (float("inf") if k else None), ratio_wilson=ratio_ci(k, c), ratio_cluster=cboot(rows) if boot and rows else None,
                per100=dict(correct=round(100 * k / len(rows), 1), ce=round(100 * c / len(rows), 1)) if rows else None, health_ce_rows=hce,
                U_hidden_only=round(sum(r["s"] for r in rows) / sum(r["sref"] for r in rows), 3) if rows else None)
def opus_stats(rows):
    u = {}
    for r in rows:
        if r["opus_corr"] is not None: u.setdefault(r["opus_key"], r)
    k = sum(r["opus_corr"] >= 4 for r in u.values()); c = sum(r["opus_corr"] <= 1.5 for r in u.values())
    return dict(units=len(u), correct=k, ce=c, ratio=round(k / c, 3) if c else (float("inf") if k else None), ratio_wilson=ratio_ci(k, c),
                health_ce_units=sorted(f'{r["src"]}-{r["arm"]}-{r["id"]}' for r in u.values() if r["opus_corr"] <= 1.5 and r["health"]),
                haiku_same_units=dict(correct=sum(r["correct"] for r in u.values()), ce=sum(r["CE"] for r in u.values())))
revLP = [r for r in LP if r["revealable"]]; revMI = [r for r in MINI if r["revealable"]]
out = {"criterion_sha256": CRIT, "script_sha256": hashlib.sha256(open(__file__, "rb").read()).hexdigest(), "warncal_script_sha256": hashlib.sha256(src.encode()).hexdigest(),
       "revealable": {"LP": len(revLP), "MINI": len(revMI)}, "opus_labelled_revealable_units": len({r["opus_key"] for r in revLP + revMI if r["opus_key"]}),
       "baseline_all_revealable": {"LP": stats(revLP, len(revLP)), "MINI": stats(revMI, len(revMI)), "opus": opus_stats(revLP + revMI)}, "candidates": {}}
for name, f in C.items():
    lp = [r for r in revLP if f(r)]; mi = [r for r in revMI if f(r)]
    out["candidates"][name] = dict(LP=stats(lp, len(revLP)), MINI=stats(mi, len(revMI)), opus=opus_stats(lp + mi),
        by_set_LP={s: stats([r for r in lp if r["set"] == s], len(revLP), boot=False) for s in ("MAIN", "ST-cand", "ST-SE")},
        by_arm_LP={a: stats([r for r in lp if r["arm"] == a], len(revLP), boot=False) for a in ("K0", "K1", "K3")},
        by_bucket_LP={b: stats([r for r in lp if r["bucket"] == b], len(revLP), boot=False) for b in sorted({r["bucket"] for r in lp})})
el = {n: c for n, c in out["candidates"].items() if (c["LP"]["ratio"] or 0) >= 1.0 and c["LP"]["coverage"] >= 0.15}
out["eligible_LP"] = sorted(el)
if not el:
    out["selected"] = None; out["verdict"] = "KILL (no pre-listed subset reaches correct:CE >= 1.0 on LP with >= 15 % of revealable rows)"
else:
    sel = max(el, key=lambda n: (el[n]["LP"]["ratio"], el[n]["LP"]["coverage"])); c = el[sel]; out["selected"] = sel
    a = c["MINI"]["ratio_wilson"] and c["MINI"]["ratio_wilson"][1] >= 1.0 and (c["MINI"]["ratio"] or 0) >= 1.0
    b = None if c["opus"]["units"] < 10 else (c["opus"]["ratio"] or 0) >= 1.0
    s = not c["LP"]["health_ce_rows"] and not c["MINI"]["health_ce_rows"] and not c["opus"]["health_ce_units"]
    out["confirm"] = dict(a_MINI=bool(a), b_opus=b, c_safety=s)
    out["verdict"] = ("PASS" if a and b and s else "PASS-HAIKU-ONLY" if a and b is None and s else "KILL (confirmation failed)")
js = json.dumps(out, indent=1, ensure_ascii=False); open(sys.argv[1], "w").write(js + "\n")
print(json.dumps({k: out[k] for k in ("revealable", "opus_labelled_revealable_units", "eligible_LP", "selected", "verdict")} | {"confirm": out.get("confirm")}))
for n, c in out["candidates"].items():
    print(n, "| LP", {k: c["LP"][k] for k in ("rows", "items", "coverage", "correct", "ce", "ratio", "ratio_wilson", "ratio_cluster")}, "hCE", len(c["LP"]["health_ce_rows"]))
    print("   MINI", {k: c["MINI"][k] for k in ("rows", "coverage", "correct", "ce", "ratio", "ratio_wilson")}, "hCE", len(c["MINI"]["health_ce_rows"]), "| OPUS", {k: c["opus"][k] for k in ("units", "correct", "ce", "ratio", "ratio_wilson", "health_ce_units", "haiku_same_units")})
