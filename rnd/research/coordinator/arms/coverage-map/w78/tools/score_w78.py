#!/usr/bin/env python3
"""W78-BINARY scorer (W8, W16 = post-hoc diagnostics, not in the criterion) (0 LLM): chunk-level delivery (coverage-map/tools/chunklevel.py score(), unchanged rule), kept identity vs B and vs the
SEFIX-124 reference, health-item changes, F1 thread-pick agreement and bytes/ms from the RS_SE_LEAD_LOG lines. Usage: python3 -I score_w78.py <out json>"""
import json, sys, statistics as st
CM = "<workspace>/rnd/research/coordinator/arms/coverage-map/"; W = CM + "w78/replays/"
src = open(CM + "tools/chunklevel.py").read(); exec(src[: src.index("\nARMS = {")])  # score(), ids92, rd
REF = CM + "sefix/replays/main.F1F2F4.jsonl"
ARMS = {"REF (sefix main.F1F2F4)": REF, **{a: W + f"main.{a}.jsonl" for a in ("B", "W32", "W64", "W128", "B2", "W8", "W16")}}
rows = {a: {r["id"]: r for r in rd(p)} for a, p in ARMS.items()}
kid = lambda r: [c["chunkId"] for c in r["keptFull"]]
ishealth = lambda r: any(x.startswith("grounding:health") or x.startswith("instant:off-health") for x in r["reasonCodes"])
def f1log(a):
    try: return [json.loads(l) for l in open(W + f"main.{a}.jsonl.f1log")]
    except FileNotFoundError: return []
sc = {a: score(p) for a, p in ARMS.items()}
base = "B"; deliv_B = [i for i in ids92 if sc[base][i] and sc[base][i]["chunk"]]
logB = f1log("B"); out = {"criterion_sha256": open(CM + "W78-criterion.sha256").read().split()[0], "arms": {}}
for a in ARMS:
    R = rows[a]; B = rows[base]; Rf = rows["REF (sefix main.F1F2F4)"]
    ids = list(B)
    ident_B = sum(kid(R[i]) == kid(B[i]) for i in ids); ident_ref = sum(kid(R[i]) == kid(Rf[i]) for i in ids)
    rc_ref = sum(R[i]["reasonCodes"] == Rf[i]["reasonCodes"] and kid(R[i]) == kid(Rf[i]) for i in ids)
    health = [i for i in ids if ishealth(R[i]) or ishealth(B[i])]
    hchg = [i for i in health if kid(R[i]) != kid(B[i])]
    d = sc[a]; deliv = [i for i in ids92 if d[i] and d[i]["chunk"]]
    kept42 = [i for i in deliv_B if i in deliv]
    lg = f1log(a); ms = [float(R[i]["ms"]) for i in ids if R[i].get("ms") is not None]
    rec = dict(chunk92=len(deliv), cm=sum(d[i]["set"] == "cm" for i in deliv), v01=sum(d[i]["set"] == "v0.1" for i in deliv),
               of_B42=len(kept42), lost=[i for i in deliv_B if i not in deliv], gained=[i for i in deliv if i not in deliv_B],
               ident_kept_vs_B=ident_B, ident_kept_vs_ref=ident_ref, ident_kept_and_codes_vs_ref=rc_ref, n=len(ids),
               health_items=len(health), health_changed=hchg, changed_vs_B=[i for i in ids if kid(R[i]) != kid(B[i])],
               ms_mean=round(st.mean(ms), 1), ms_p50=round(st.median(ms), 1))
    if lg:
        rec["f1_calls"] = len(lg)
        rec["f1_scan_ms_mean"] = round(st.mean(x["scanMs"] for x in lg), 2)
        rec["f1_scan_ms_p50"] = st.median(x["scanMs"] for x in lg)
        rec["f1_load_ms"] = sum(x["loadMs"] for x in lg)
        per_pack = {}
        for x in lg: per_pack.setdefault(x["pack"], x)
        rec["scan_bytes_per_q"] = {p: x["scanBytes"] for p, x in per_pack.items()}
        rec["resident_bytes"] = {p: x["residentBytes"] for p, x in per_pack.items()}
        rec["picks_nonempty"] = sum(1 for x in lg if x["top"])
        if logB and len(logB) == len(lg):
            same = [(x["pack"] == y["pack"]) and [t["id"] for t in x["top"]] == [t["id"] for t in y["top"]] for x, y in zip(lg, logB)]
            rec["pick_agree_vs_B"] = f"{sum(same)}/{len(same)}"
            rec["pick_missed"] = sum(1 for x, y in zip(lg, logB) if y["top"] and not x["top"])
            rec["pick_nonempty_B"] = sum(1 for y in logB if y["top"])
            rec["pick_nonempty_agree"] = sum(1 for s, y in zip(same, logB) if s and y["top"])
    out["arms"][a] = rec
json.dump(out, open(sys.argv[1], "w"), indent=1)
for a, r in out["arms"].items(): print(a, {k: v for k, v in r.items() if k not in ("changed_vs_B",)})
