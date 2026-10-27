#!/usr/bin/env python3
"""W78-PACKFMT scorer (0 LLM): MAIN 97 arms IVF32 / PF32 / B (replays-pf) vs the W78C IVF32 and B replays (replays-c), + cold-start runs (replays-pf/cold).
Usage: python3 -I score_w78pf.py <out json>"""
import json, sys, os, glob, statistics as st
CM = "<workspace>/rnd/research/coordinator/arms/coverage-map/"; W = CM + "w78/"
src = open(CM + "tools/chunklevel.py").read(); exec(src[: src.index("\nARMS = {")])  # score(), ids92, rd
ARMS = {"W78C B": W + "replays-c/main.B.jsonl", "W78C IVF32": W + "replays-c/main.IVF32.jsonl", **{a: W + f"replays-pf/main.{a}.jsonl" for a in ("B", "IVF32", "PF32")}}
ARMS = {a: p for a, p in ARMS.items() if os.path.exists(p)}
rows = {a: {r["id"]: r for r in rd(p)} for a, p in ARMS.items()}
ARMS = {a: p for a, p in ARMS.items() if len(rows[a]) == 97}; rows = {a: rows[a] for a in ARMS}
kid = lambda r: [c["chunkId"] for c in r["keptFull"]]
ishealth = lambda r: any(x.startswith("grounding:health") or x.startswith("instant:off-health") for x in r["reasonCodes"])
jl = lambda p: [json.loads(l) for l in open(p)] if os.path.exists(p) else []
sc = {a: score(p) for a, p in ARMS.items()}
B = rows["W78C B"]; REF = rows["W78C IVF32"]; ids = list(B)
nret = json.loads(open(W + "replays-c/main.B.jsonl.err").read().strip().splitlines()[-1])["retrieved"]
deliv_B = [i for i in ids92 if sc["W78C B"][i] and sc["W78C B"][i]["chunk"]]
dlREF = jl(ARMS["W78C IVF32"] + ".denselog")
def growth(dl):  # rss after the last stage-1 call minus rss before the first
    dl = [x for x in dl if "rssBefore" in x]
    return (dl[-1]["rssAfter"] - dl[0]["rssBefore"]) if dl else None
out = {"criterion_sha256": open(CM + "W78PACKFMT-criterion.sha256").read().split()[0], "retrieving_items": nret, "arms": {}, "cold": {}}
for a in ARMS:
    R = rows[a]
    rec = dict(ident_vs_W78C_IVF32=sum(kid(R[i]) == kid(REF[i]) for i in ids), ident_and_codes_vs_W78C_IVF32=sum(kid(R[i]) == kid(REF[i]) and R[i]["reasonCodes"] == REF[i]["reasonCodes"] for i in ids),
               ident_vs_B=sum(kid(R[i]) == kid(B[i]) for i in ids))
    d = sc[a]; deliv = [i for i in ids92 if d[i] and d[i]["chunk"]]
    rec.update(chunk92=len(deliv), of_B42=len([i for i in deliv_B if i in deliv]), lost=[i for i in deliv_B if i not in deliv])
    health = [i for i in ids if ishealth(R[i]) or ishealth(B[i])]
    rec.update(health_items=len(health), health_changed=[i for i in health if kid(R[i]) != kid(B[i])], changed_vs_B=[i for i in ids if kid(R[i]) != kid(B[i])],
               changed_vs_W78C_IVF32=[i for i in ids if kid(R[i]) != kid(REF[i])])
    ms = [float(R[i]["ms"]) for i in ids if R[i].get("ms") is not None]; rec.update(replay_ms_mean=round(st.mean(ms), 1))
    dl = jl(ARMS[a] + ".denselog"); f1 = jl(ARMS[a] + ".f1log")
    if dl:
        rec["dense_calls"] = len(dl); rec["modes"] = sorted({x["mode"] for x in dl})
        rec["dense_bytes_per_q"] = round(sum(x["scanBytes"] for x in dl) / nret)
        rec["dense_scan_ms_per_q"] = round(sum(x["scanMs"] for x in dl) / nret, 2)
        rec["dense_load_ms_total"] = sum(x["loadMs"] for x in dl)
        rec["resident_bytes_total"] = sum({x["pack"]: x["residentBytes"] for x in dl}.values())
        pf = [x for x in dl if x["mode"].startswith("ivfp")]
        if pf:
            rec["ivfp_payload_bytes_per_q"] = round(sum(x["payloadBytes"] for x in pf) / nret); rec["ivfp_page_bytes_per_q"] = round(sum(x["pageBytes"] for x in pf) / nret)
            rec["ivfp_read_ms_per_q"] = round(sum(x["readMs"] for x in pf) / nret, 2)
            per = {}
            for x in pf: per.setdefault(x["pack"], []).append(x)
            rec["ivfp_per_pack"] = {p: dict(calls=len(v), rows_read_mean=round(st.mean(x["rows"] for x in v)), page_bytes_mean=round(st.mean(x["pageBytes"] for x in v)),
                                            scan_ms_mean=round(st.mean(x["scanMs"] for x in v), 2), read_ms_mean=round(st.mean(x["readMs"] for x in v), 2)) for p, v in per.items()}
        if len(dl) == len(dlREF):
            rec["stage1_pack_order_same_as_W78C_IVF32"] = all(x["pack"] == y["pack"] for x, y in zip(dl, dlREF))
            rec["stage1_art_lists_identical_to_W78C_IVF32"] = f"{sum(x['art'] == y['art'] for x, y in zip(dl, dlREF))}/{len(dl)}"
        else: rec["stage1_calls_mismatch"] = [len(dl), len(dlREF)]
        rec["rss_growth_full_replay"] = growth(dl); rec["rss_growth_first_q_7calls"] = growth(dl[:7])
        rec["rss_after_last_call"] = dl[-1].get("rssAfter")
    if f1:
        rec["f1_bytes_per_q"] = round(sum(x["scanBytes"] for x in f1) / nret)
        if dl: rec["kit_bytes_per_q"] = rec["dense_bytes_per_q"] + rec["f1_bytes_per_q"]
    out["arms"][a] = rec
# cold start: replays-pf/cold/main.<arm>-r<k>.jsonl, one item
for a in ("B", "IVF32", "PF32"):
    reps = []
    for p in sorted(glob.glob(W + f"replays-pf/cold/main.{a}-r*.jsonl")):
        dl = jl(p + ".denselog"); f1 = jl(p + ".f1log"); r = jl(p)
        if not dl: continue
        # bytes read from storage at the first query: int8/ivf = whole lead matrix (rows x 384) + sidecar file; ivfp = centroid row + probed pages; F1 = sidecar file + rescore
        def coldb(x):
            if x["mode"] == "int8": return x["rows"] * 384
            if x["mode"].startswith("ivfp"): return x["scanBytes"]
            if x["mode"].startswith("ivf"): return x["rows"] * 384 + x["residentBytes"]
            return x["scanBytes"]
        f1b = sum(x["rows"] * 384 if x["mode"] == "int8" else x["residentBytes"] + x.get("rescoreRows", 0) * 384 for x in f1)  # exact: whole matrix load; binary: sidecar file + int8 rescore rows
        reps.append(dict(file=os.path.basename(p), item=r[0]["id"] if r else None, calls=len(dl), stage1_ms_incl_load=sum(x["scanMs"] + x["loadMs"] for x in dl),
                         stage1_load_ms=sum(x["loadMs"] for x in dl), dense_bytes_read=sum(coldb(x) for x in dl), f1_bytes_read=f1b, rss_growth=growth(dl),
                         rss_before_first=dl[0].get("rssBefore"), rss_after_last=dl[-1].get("rssAfter"), replay_ms=r[0].get("ms") if r else None,
                         art_lists=[x["art"] for x in dl]))
    if reps:
        med = lambda k: st.median(x[k] for x in reps)
        out["cold"][a] = dict(n=len(reps), median_rss_growth=med("rss_growth"), median_stage1_ms_incl_load=med("stage1_ms_incl_load"), median_dense_bytes_read=med("dense_bytes_read"),
                              median_f1_bytes_read=med("f1_bytes_read"), median_rss_after_last=med("rss_after_last"), art_lists_equal_across_reps=all(x["art_lists"] == reps[0]["art_lists"] for x in reps),
                              reps=[{k: v for k, v in x.items() if k != "art_lists"} for x in reps])
if "PF32" in out["cold"] and "IVF32" in out["cold"]:
    out["cold"]["PF32_over_IVF32_rss_growth"] = round(out["cold"]["PF32"]["median_rss_growth"] / out["cold"]["IVF32"]["median_rss_growth"], 3)
    out["cold"]["PF32_art_equal_IVF32"] = jl(sorted(glob.glob(W + "replays-pf/cold/main.PF32-r*.jsonl"))[0] + ".denselog")[0]["art"] == jl(sorted(glob.glob(W + "replays-pf/cold/main.IVF32-r*.jsonl"))[0] + ".denselog")[0]["art"]
json.dump(out, open(sys.argv[1], "w"), indent=1)
for a, r in out["arms"].items(): print(a, {k: v for k, v in r.items() if k not in ("changed_vs_B", "ivfp_per_pack", "changed_vs_W78C_IVF32")})
for a, r in out["cold"].items(): print("cold", a, r if not isinstance(r, dict) else {k: v for k, v in r.items() if k != "reps"})
