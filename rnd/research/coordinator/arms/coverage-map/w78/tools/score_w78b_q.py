#!/usr/bin/env python3
"""W78B part B scorer (0 LLM): 216 QFORM items, modes true / extra, arms B / N32 / N64 / N128 (labels qform.<mode>-<arm>.jsonl).
found = verbatim gold quote (items/facts.json, normalised) in title+body of a chunk of keptFull (matrix.py hit_kept quote branch); raw / wide diagnostic.
Usage: python3 -I score_w78b_q.py <out json>"""
import json, sys, re, os, statistics as st
CM = "<workspace>/rnd/research/coordinator/arms/"; Q = CM + "qform/"; W = CM + "coverage-map/w78/"
norm = lambda s: re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", s.lower())).strip()
items = {}
for l in open(Q + "items/qform.jsonl"):
    d = json.loads(l); items[d["id"]] = d
facts = {f["fact_id"]: f for f in json.load(open(Q + "items/facts.json"))}
rd = lambda p: {json.loads(l)["id"]: json.loads(l) for l in open(p)}
ishealth = lambda r: any(x.startswith("grounding:health") or x.startswith("instant:off-health") for x in r["reasonCodes"])
kid = lambda r: [c["chunkId"] for c in r["keptFull"]]
hit = lambda lst, qn: any(qn in norm(c["title"] + " " + c["body"]) for c in lst)
out = {"criterion_sha256": open(W + "../W78B-criterion.sha256").read().split()[0], "modes": {}}
for mode in ("true", "extra"):
    arms = {a: W + f"replays-b/qform.{mode}-{a}.jsonl" for a in ("B", "B2", "N32", "N64", "N128", "N256", "N512")}
    arms = {a: p for a, p in arms.items() if os.path.exists(p)}
    if "B" not in arms: continue
    R = {a: rd(p) for a, p in arms.items()}; B = R["B"]; ids = list(B)
    nret = sum(1 for i in ids if B[i]["rawFull"])
    def dl(a):
        try: return [json.loads(l) for l in open(arms[a] + ".denselog")]
        except FileNotFoundError: return []
    dlB = dl("B"); M = {}
    for a in arms:
        r = R[a]; found = {"kept": {}, "raw": {}, "wide": {}}
        for i in ids:
            qn = norm(facts[items[i]["fact_id"]]["gold"]["quote"])
            found["kept"][i] = hit(r[i]["keptFull"], qn); found["raw"][i] = hit(r[i]["rawFull"], qn); found["wide"][i] = hit(r[i]["wideFull"], qn)
        byform = {f: sum(found["kept"][i] for i in ids if items[i]["form"] == f) for f in range(9)}
        health = [i for i in ids if ishealth(r[i]) or ishealth(B[i])]
        rec = dict(found_kept=sum(found["kept"].values()), found_raw=sum(found["raw"].values()), found_wide=sum(found["wide"].values()), found_kept_by_form=byform,
                   ident_kept_vs_B=sum(kid(r[i]) == kid(B[i]) for i in ids), ident_raw_vs_B=sum([c["chunkId"] for c in r[i]["rawFull"]] == [c["chunkId"] for c in B[i]["rawFull"]] for i in ids),
                   health_items=len(health), health_changed=[i for i in health if kid(r[i]) != kid(B[i])], changed_vs_B=[i for i in ids if kid(r[i]) != kid(B[i])],
                   gained_found=[i for i in ids if found["kept"][i] and not M.get("B", {}).get("_f", {}).get(i, False)] if a != "B" else [])
        rec["_f"] = found["kept"]
        ms = [float(r[i]["ms"]) for i in ids if r[i].get("ms") is not None]; rec.update(ms_mean=round(st.mean(ms), 1), ms_p50=round(st.median(ms), 1))
        d = dl(a)
        if d:
            per = {}
            for x in d: per.setdefault(x["pack"], []).append(x)
            rec.update(dense_calls=len(d), dense_calls_per_retrieving_q=round(len(d) / nret, 2), dense_bytes_per_q=round(sum(x["scanBytes"] for x in d) / nret),
                       dense_scan_ms_per_q=round(sum(x["scanMs"] for x in d) / nret, 3), dense_scan_ms_mean_per_call=round(st.mean(x["scanMs"] for x in d), 3),
                       dense_load_ms_total=sum(x["loadMs"] for x in d), resident_bytes_total=sum({x["pack"]: x["residentBytes"] for x in d}.values()),
                       per_pack={p: dict(rows=v[0]["rows"], calls=len(v), bytes_per_call=round(st.mean(x["scanBytes"] for x in v)), rescore_rows_mean=round(st.mean(x["rescoreRows"] for x in v), 1)) for p, v in per.items()})
            if len(d) == len(dlB):
                rec["stage1_set_equal_calls"] = f"{sum(set(x['art']) == set(y['art']) for x, y in zip(d, dlB))}/{len(d)}"
                rec["stage1_mean_recall_of_B_top50"] = round(st.mean(len(set(x["art"]) & set(y["art"])) / max(1, len(y["art"])) for x, y in zip(d, dlB)), 4)
            else: rec["stage1_calls_mismatch"] = [len(d), len(dlB)]
        M[a] = rec
    for a, rec in M.items():
        if a != "B": rec["found_lost"] = [i for i in ids if M["B"]["_f"][i] and not rec["_f"][i]]; rec["found_gained"] = [i for i in ids if rec["_f"][i] and not M["B"]["_f"][i]]
        rec["found_by_form_delta_vs_B"] = {f: rec["found_kept_by_form"][f] - M["B"]["found_kept_by_form"][f] for f in range(9)}
    for rec in M.values(): rec.pop("_f"); rec.pop("gained_found", None)
    out["modes"][mode] = dict(retrieving_items=nret, arms=M)
json.dump(out, open(sys.argv[1], "w"), indent=1)
for m, v in out["modes"].items():
    for a, r in v["arms"].items(): print(m, a, {k: x for k, x in r.items() if k not in ("per_pack", "changed_vs_B", "found_lost", "found_gained")})
