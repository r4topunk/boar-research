#!/usr/bin/env python3
"""SPEED-PRECHECK (RJ5 step 1): ruler speed row from existing Pixel 8a traces. 0 LLM.
Criterion: ruler/SPEED-PRECHECK-criterion.md (sha in .sha256). Usage: python3 -I speed_precheck.py <out.json>"""
import csv, hashlib, json, os, sys
import numpy as np

COORD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BOAR = os.path.abspath(os.path.join(COORD, "..", "..", ".."))
H = os.path.join(BOAR, "handoff/pixel8-2026-10-20/bench/results")
A = os.path.join(COORD, "arms")
RUNS = [  # (tier, run, path, primary)
    ("1.7B + A-union", "aunion73-a", f"{A}/aunion-pixel/aunion73-a", True),
    ("1.7B + A-union", "aunion10-a", f"{A}/aunion-pixel/aunion10-a", False),
    ("1.7B claim kit", "q17b73-a", f"{A}/gemma4-e2b/phone/q17b73-a", True),
    ("1.7B claim kit", "q17b10-a", f"{A}/gemma4-e2b/phone/q17b10-a", False),
    ("1.7B claim kit", "batchret-1a", f"{H}/batchret-1a", False),
    ("1.7B claim kit", "batchret-2b", f"{H}/batchret-2b", False),
    ("1.7B claim kit", "batchret-3a", f"{H}/batchret-3a", False),
    ("1.7B claim kit", "batchret-4b", f"{H}/batchret-4b", False),
    ("1.7B claim kit", "cmp30-q17", f"{H}/cmp30-q17", False),
    ("1.7B claim kit", "cmp30off-q17", f"{H}/cmp30off-q17", False),
    ("Gemma 4 E2B", "gemma73-a", f"{A}/gemma4-e2b/phone/gemma73-a", True),
    ("Gemma 4 E2B", "gemma10-b", f"{A}/gemma4-e2b/phone/gemma10-b", False),
    ("4B", "final-cut7-v01", f"{H}/final-cut7-v01", True),
    ("4B", "final-a-cut7", f"{H}/final-a-cut7", False),
    ("4B", "live-4b-final2", f"{H}/live-4b-final2", False),
]
BATCHRET_TTFT_GAIN_MS = 3494.0
DET = set(l.strip() for l in open(f"{COORD}/ruler/ids/deterministic-v01.ids") if l.strip())
TH = dict(p50_t30=30.0, p90_t30=60.0, p50_complete=60.0)

def pct(xs, q):
    return round(float(np.percentile(np.array(xs) / 1000.0, q)), 1) if xs else None

def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

def run_stats(tier, name, path, primary):
    rows = [json.loads(l) for l in open(f"{path}/rows.jsonl")]
    rows = [r for r in rows if r["queryId"] != "warmup-000"]
    b = json.load(open(f"{path}/bench.json"))
    comps = [c for c in b.get("completions", []) if (c.get("predictedN") or 0) >= 1]
    dec = [c["predictedN"] / (c["predictedMs"] / 1000.0) for c in comps if c.get("predictedMs")]
    pre = [c["promptPerSecond"] for c in comps if c.get("promptPerSecond")]
    med_dec = float(np.median(dec)) if dec else None
    tel = list(csv.DictReader(open(f"{path}/telemetry.csv")))
    pss = [int(t["app_pss_kb"]) for t in tel if t.get("app_pss_kb")]
    out_rows, resid, derived = [], [], 0
    for r in rows:
        n = r.get("tokensGenerated") or 0
        wall = float(r["wallMs"])
        if n > 0:
            ft = float(r.get("firstTokenMs") or r.get("ttftMs"))
            tps = r.get("tokPerSec") or 0
            if tps <= 0: tps = med_dec
            if n >= 30:
                t30 = ft + 29 * 1000.0 / tps; derived += 1
            else:
                t30 = wall
            resid.append(abs(ft + (n - 1) * 1000.0 / tps - float(r["totalLatencyMs"])))
            cls = "declined" if r["declined"] else "llm"
        else:
            ft, t30 = wall, wall
            cls = "declined" if r["declined"] else "deterministic"
        out_rows.append(dict(id=r["queryId"], cls=cls, tokens=n, ttft=ft, t30=t30, complete=wall,
                             retrieval=bool(r.get("retrievalUsed")), det_id=r["queryId"] in DET))
    def summ(sel, adj=0.0):
        t = [x["t30"] - (adj if x["cls"] == "llm" else 0) for x in sel]
        c = [x["complete"] - (adj if x["cls"] == "llm" else 0) for x in sel]
        f = [x["ttft"] - (adj if x["cls"] == "llm" else 0) for x in sel]
        d = dict(n=len(sel), ttft_p50=pct(f, 50), ttft_p90=pct(f, 90), t30_p50=pct(t, 50), t30_p90=pct(t, 90),
                 complete_p50=pct(c, 50), complete_p90=pct(c, 90),
                 share_complete_le60=round(sum(1 for x in c if x <= 60000) / len(c), 3) if c else None)
        if sel:
            d["usable"] = bool(d["t30_p50"] <= TH["p50_t30"] and d["t30_p90"] <= TH["p90_t30"] and d["complete_p50"] <= TH["p50_complete"])
            d["fails"] = [k for k, v in (("p50 T30", d["t30_p50"] > 30), ("p90 T30", d["t30_p90"] > 60), ("p50 complete", d["complete_p50"] > 60)) if v]
        return d
    S1 = [x for x in out_rows if x["cls"] != "declined"]
    sets = dict(S1_answered=summ(S1),
                S1_llm_only=summ([x for x in S1 if x["cls"] == "llm"]),
                S2_answered_no_det_ids=summ([x for x in S1 if not x["det_id"]]),
                S3_all=summ(out_rows),
                S4_declined=summ([x for x in out_rows if x["cls"] == "declined"]))
    if tier == "4B":
        sets["S1_batchret_adjusted"] = summ(S1, BATCHRET_TTFT_GAIN_MS)
    t0 = tel[0] if tel else {}
    return dict(tier=tier, run=name, primary=primary, path=os.path.relpath(path, BOAR),
                rows_sha256=sha(f"{path}/rows.jsonl"), tree=b["engine"].get("treeHash", "")[:8], arm=b["engine"].get("arm"),
                model=(b["flags"].get("models") or [None])[0], n_rows=len(rows),
                classes={k: sum(1 for x in out_rows if x["cls"] == k) for k in ("llm", "deterministic", "declined")},
                t30_derived_rows=derived, derivation_residual_ms_p50=round(float(np.median(resid)), 1) if resid else None,
                decode_tps_p50=round(med_dec, 1) if med_dec else None, prefill_tps_p50=round(float(np.median(pre)), 1) if pre else None,
                n_completions=len(comps), thermal_start=dict(status=t0.get("thermal_status"), battery_c=int(t0["battery_temp_dC"]) / 10 if t0 else None),
                thermal_max=max((int(t["thermal_status"]) for t in tel), default=None),
                pss_peak_gb=round(max(pss) / 1e6, 2) if pss else None, sets=sets)

def main():
    crit = f"{COORD}/ruler/SPEED-PRECHECK-criterion.md"
    res = dict(criterion_sha256=sha(crit), frozen=open(f"{COORD}/ruler/SPEED-PRECHECK-criterion.sha256").read().split()[0],
               script_sha256=sha(os.path.abspath(__file__)), thresholds=TH, phone="Pixel 8a (8 GB, Tensor G3)",
               runs=[run_stats(*r) for r in RUNS])
    assert res["criterion_sha256"] == res["frozen"], "criterion changed after freeze"
    v = {r["tier"]: r["sets"]["S1_answered"] for r in res["runs"] if r["primary"]}
    res["verdicts"] = {t: ("USABLE" if s["usable"] else "NOT USABLE (" + ", ".join(s["fails"]) + ")") for t, s in v.items()}
    res["rj5_step1_holds"] = bool(v["1.7B + A-union"]["usable"] and v["1.7B claim kit"]["usable"] and not v["4B"]["usable"])
    json.dump(res, open(sys.argv[1], "w"), indent=1)
    for r in res["runs"]:
        s = r["sets"]
        print(r["tier"], r["run"], "P" if r["primary"] else " ", r["tree"], r["classes"], "dec", r["decode_tps_p50"], "pre", r["prefill_tps_p50"],
              "therm", r["thermal_start"], r["thermal_max"], "pss", r["pss_peak_gb"], "resid", r["derivation_residual_ms_p50"], "derived", r["t30_derived_rows"])
        for k, d in s.items(): print("   ", k, d)
    print(res["verdicts"], "RJ5 step1 holds:", res["rj5_step1_holds"])

main()
