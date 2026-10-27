# TOPICS27-SUCCINCT aggregation (0 LLM): agg.py's frozen verdict rule on the Succinct audit + side-by-side with the Detailed aggregates.
import json, os
P = json.load(open("judge-succinct/prep.json")); A = {json.loads(l)["key"]: json.loads(l) for l in open("judge-succinct/audit.jsonl")}
T = {o["key"]: o for o in json.load(open("aggregates/titles.json"))}
D = {r["key"]: r for r in json.load(open("aggregates/topics27.json"))}; DS = json.load(open("aggregates/summary.json"))
def score(us):
    n = len(us); uns = sum(a["label"] == "UNSUPPORTED" for a in us); par = sum(a["label"] == "PARTIAL" for a in us)
    inv = sum(1 for a in us if a["label"] in ("UNSUPPORTED", "PARTIAL") and a["invented_specific"]); return n, uns, par, inv
def verdict(present, n, uns, inv, declined, inkept):
    share = uns / n if n else 1.0
    if not present or (share >= 1/3 and inv >= 1) or n == 0 or declined: v = "SWAP"
    elif not inkept: v = "FIX-PACK"
    else: v = "KEEP"
    return v, round(share, 3), v == "KEEP" and ((share >= 1/3 and inv == 0) or (inv >= 1 and share < 1/3))
rows = []
for it in P["items"]:
    k = it["key"]; t = T[k]; anchors = {x.lower() for g in t["groups"] for x in g}
    inkept = any(x.lower() in anchors for x in it["kept"]); inraw = any(x.lower() in anchors for x in it["raw"])
    us = [A[u["key"]] for u in P["units"] if u["topic"] == k]; n, uns, par, inv = score(us)
    v, share, watch = verdict(t["present"], n, uns, inv, it["declined"], inkept)
    d = D[k]
    rows.append(dict(key=k, area=it["area"], present=t["present"], in_raw=inraw, in_kept=inkept, kept=it["kept"], kept_same_as_detailed=[x.lower() for x in it["kept"]] == [x.lower() for x in d["kept"]],
        banner=bool(it["banner"]), words=it["words"], sentences=n, unsupported=uns, partial=par, invented=inv, unsup_share=share, num_absent=sum(it["num_absent"]),
        batched=any(a["mode"] == "batched" for a in us), verdict=v, watch=watch,
        detailed=dict(words=d["words"], sentences=d["sentences"], unsupported=d["unsupported"], partial=d["partial"], invented=d["invented"], unsup_share=d["unsup_share"], banner=d["banner"], verdict=d["verdict"], watch=d["watch"])))
json.dump(rows, open("aggregates/succinct-topics27.json", "w"), indent=1)
S = sum(r["sentences"] for r in rows); X = sum(r["unsupported"] for r in rows); I = sum(r["invented"] for r in rows); B = sum(r["banner"] for r in rows)
V = {v: [r["key"] for r in rows if r["verdict"] == v] for v in ("KEEP", "FIX-PACK", "SWAP")}
agg = dict(arm="succinct", sentences=S, unsupported=X, unsup_share=round(X / S, 3), partial=sum(r["partial"] for r in rows), invented=I, banner=B,
    banner_keys=[r["key"] for r in rows if r["banner"]], in_kept=sum(r["in_kept"] for r in rows), kept_same_as_detailed=sum(r["kept_same_as_detailed"] for r in rows),
    mean_words=round(sum(r["words"] for r in rows) / len(rows), 1), num_absent=sum(r["num_absent"] for r in rows), verdicts=V, watch=[r["key"] for r in rows if r["watch"]],
    flips={"SWAP->KEEP": [r["key"] for r in rows if r["detailed"]["verdict"] == "SWAP" and r["verdict"] == "KEEP"], "KEEP->SWAP": [r["key"] for r in rows if r["detailed"]["verdict"] == "KEEP" and r["verdict"] == "SWAP"]},
    detailed=dict(sentences=DS["sentences"], unsupported=DS["unsupported"], unsup_share=DS["unsup_share"], invented=DS["invented"], banner=DS["banner"], keep=len(DS["verdicts"]["KEEP"]),
        mean_words=round(sum(d["words"] for d in D.values()) / len(D), 1)),
    predictions=dict(P1_unsup_le_0318=X / S <= DS["unsup_share"] - 0.15, P2_invented_le_half=I <= DS["invented"] / 2, P3_banner_le_5=B <= 5, P4_keep_ge_12=len(V["KEEP"]) >= 12))
# sensitivity (never changes a verdict): both arms fully per-sentence (batched labels replaced by per-sentence re-audits)
def allsingle(prepf, auditf, sensf, items_present_kept):
    if not os.path.exists(sensf): return None
    Pp = json.load(open(prepf)); Aa = {json.loads(l)["key"]: json.loads(l) for l in open(auditf)}
    Aa.update({json.loads(l)["key"]: json.loads(l) for l in open(sensf)})
    out = {}; tot = [0, 0, 0]
    for it in Pp["items"]:
        k = it["key"]; us = [Aa[u["key"]] for u in Pp["units"] if u["topic"] == k]; n, uns, par, inv = score(us)
        pres, inkept, dec = items_present_kept[k]; v = verdict(pres, n, uns, inv, dec, inkept)[0]
        out[k] = v; tot[0] += n; tot[1] += uns; tot[2] += inv
    return dict(sentences=tot[0], unsupported=tot[1], unsup_share=round(tot[1] / tot[0], 3), invented=tot[2], keep=sum(v == "KEEP" for v in out.values()),
                verdicts_b14_b21={k: v for k, v in out.items() if k in ("b14","b15","b16","b17","b18","b19","b20","b21")})
pk_s = {r["key"]: (r["present"], r["in_kept"], False) for r in rows}
pk_d = {k: (D[k]["present"], D[k]["in_kept"], False) for k in D}
agg["sensitivity_all_per_sentence"] = dict(succinct=allsingle("judge-succinct/prep.json", "judge-succinct/audit.jsonl", "judge-succinct/sens-succinct.jsonl", pk_s),
    detailed=allsingle("judge/prep.json", "judge/audit.jsonl", "judge-succinct/sens-detailed.jsonl", pk_d))
json.dump(agg, open("aggregates/succinct-summary.json", "w"), indent=1); print(json.dumps(agg, indent=1))
for r in rows: d = r["detailed"]; print(f'{r["key"]:4} D {d["sentences"]:2} {d["unsupported"]:2} {d["invented"]:2} {int(d["banner"])} {d["verdict"]:5} | S {r["sentences"]:2} {r["unsupported"]:2} {r["invented"]:2} {int(r["banner"])} {r["verdict"]:5} {"watch" if r["watch"] else ""} kept={r["kept"]} same={r["kept_same_as_detailed"]}')
