#!/usr/bin/env python3
"""W78B part A scorer (0 LLM): MAIN 97, arms B / D32 / D64 / D128 / K32 / K64 (+ B2 rerun) vs B and vs the W78 B replay.
Chunk-level delivery = coverage-map/tools/chunklevel.py score() (W78 rule), kept identity, health changes, stage-1 bytes/ms from RS_DENSE_LOG + RS_SE_LEAD_LOG.
Usage: python3 -I score_w78b_a.py <out json>"""
import json, sys, statistics as st
CM = "<workspace>/rnd/research/coordinator/arms/coverage-map/"; W = CM + "w78/"
src = open(CM + "tools/chunklevel.py").read(); exec(src[: src.index("\nARMS = {")])  # score(), ids92, rd
ARMS = {"W78 B (ref)": W + "replays/main.B.jsonl", **{a: W + f"replays-b/main.{a}.jsonl" for a in ("B", "B2", "D32", "D64", "D128", "D256", "D512", "K32", "K64")}}
import os
ARMS = {a: p for a, p in ARMS.items() if os.path.exists(p)}
rows = {a: {r["id"]: r for r in rd(p)} for a, p in ARMS.items()}
kid = lambda r: [c["chunkId"] for c in r["keptFull"]]
ishealth = lambda r: any(x.startswith("grounding:health") or x.startswith("instant:off-health") for x in r["reasonCodes"])
def lg(a, ext):
    try: return [json.loads(l) for l in open(ARMS[a].replace(W + "replays/", W + "replays-b/") + ext)] if a != "W78 B (ref)" else []
    except FileNotFoundError: return []
sc = {a: score(p) for a, p in ARMS.items()}
B = rows["B"]; ids = list(B)
nret = json.loads(open(W + "replays-b/main.B.jsonl.err").read().strip().splitlines()[-1])["retrieved"]  # items that retrieved (86); rawFull is empty for one of them
deliv_B = [i for i in ids92 if sc["B"][i] and sc["B"][i]["chunk"]]
dlB = lg("B", ".denselog"); f1B = lg("B", ".f1log")
out = {"criterion_sha256": open(CM + "W78B-criterion.sha256").read().split()[0], "retrieving_items": nret, "arms": {}}
for a in ARMS:
    R = rows[a]
    rec = dict(n=len(R), ident_kept_vs_B=sum(kid(R[i]) == kid(B[i]) for i in ids), ident_kept_and_codes_vs_B=sum(kid(R[i]) == kid(B[i]) and R[i]["reasonCodes"] == B[i]["reasonCodes"] for i in ids))
    d = sc[a]; deliv = [i for i in ids92 if d[i] and d[i]["chunk"]]
    rec.update(chunk92=len(deliv), of_B42=len([i for i in deliv_B if i in deliv]), lost=[i for i in deliv_B if i not in deliv], gained=[i for i in deliv if i not in deliv_B])
    health = [i for i in ids if ishealth(R[i]) or ishealth(B[i])]
    rec.update(health_items=len(health), health_changed=[i for i in health if kid(R[i]) != kid(B[i])], changed_vs_B=[i for i in ids if kid(R[i]) != kid(B[i])])
    ms = [float(R[i]["ms"]) for i in ids if R[i].get("ms") is not None]; rec.update(ms_mean=round(st.mean(ms), 1), ms_p50=round(st.median(ms), 1))
    dl = lg(a, ".denselog"); f1 = lg(a, ".f1log")
    if dl:
        per = {}
        for x in dl: per.setdefault(x["pack"], []).append(x)
        rec["dense_calls"] = len(dl); rec["dense_calls_per_retrieving_q"] = round(len(dl) / nret, 2)
        rec["dense_bytes_per_q"] = round(sum(x["scanBytes"] for x in dl) / nret)
        rec["dense_scan_ms_mean_per_call"] = round(st.mean(x["scanMs"] for x in dl), 2)
        rec["dense_scan_ms_per_q"] = round(sum(x["scanMs"] for x in dl) / nret, 2)
        rec["dense_load_ms_total"] = sum(x["loadMs"] for x in dl)
        rec["resident_bytes_total"] = sum({x["pack"]: x["residentBytes"] for x in dl}.values())
        rec["per_pack"] = {p: dict(rows=v[0]["rows"], calls=len(v), bytes_per_call=round(st.mean(x["scanBytes"] for x in v)), scan_ms_mean=round(st.mean(x["scanMs"] for x in v), 2),
                                    rescore_rows_mean=round(st.mean(x["rescoreRows"] for x in v), 1), resident=v[0]["residentBytes"]) for p, v in per.items()}
        if len(dl) == len(dlB):
            ag = [(x["pack"] == y["pack"], set(x["art"]) == set(y["art"]), len(set(x["art"]) & set(y["art"])) / max(1, len(y["art"]))) for x, y in zip(dl, dlB)]
            rec["stage1_pack_order_same"] = all(g[0] for g in ag); rec["stage1_set_equal_calls"] = f"{sum(g[1] for g in ag)}/{len(ag)}"
            rec["stage1_mean_recall_of_B_top50"] = round(st.mean(g[2] for g in ag), 4)
            rec["stage1_B_top1_in_arm"] = f"{sum(1 for x, y in zip(dl, dlB) if y['art'] and y['art'][0] in x['art'])}/{len(dl)}"
        else: rec["stage1_calls_mismatch"] = [len(dl), len(dlB)]
    if f1:
        rec["f1_calls"] = len(f1); rec["f1_bytes_per_q"] = round(sum(x["scanBytes"] for x in f1) / nret); rec["f1_scan_ms_per_q"] = round(sum(x["scanMs"] for x in f1) / nret, 2)
    if dl:
        f1b = rec.get("f1_bytes_per_q", round(sum(x["scanBytes"] for x in f1B) / nret))
        rec["kit_bytes_per_q"] = rec["dense_bytes_per_q"] + f1b
    out["arms"][a] = rec
json.dump(out, open(sys.argv[1], "w"), indent=1)
for a, r in out["arms"].items(): print(a, {k: v for k, v in r.items() if k not in ("changed_vs_B", "per_pack")})
