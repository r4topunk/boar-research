#!/usr/bin/env python3
"""E1-PAR readout (0 LLM, 0 judge): per-arm speed of BOAR Bench pack search on the Pixel 8a, hit identity, frozen clauses.

usage: e1par_readout.py <results_dir> [--arm a=e1par-a] [--arm b=e1par-b] [--arm e=e1par-e] [--arm d=e1par-d]
                        [--ref aunion73-a] [--json out.json]
Reads, per run dir: rows.jsonl (totalLatencyMs, ttftMs, retrievedTitles), bench.json (timeline spans, engine tree),
telemetry.csv (5 s sampler: battery temp, thermal status, app PSS), logcat.txt (LMK grep), e1par-thermal.json (gate
record before/after the run, written by the runner). --ref replays the frozen-prediction basis (same 10 ids from an
older 73-row run) so the metric definition can be checked against the prediction (A search p50 4.02 s, answer 10.05 s).

Definitions (frozen in E1-PAR-criterion.md):
- items = the 10 non-warmup ids of the request, paired by queryId; answer p50/p90 = percentile of totalLatencyMs.
- search_ms = sum of 'search-wikipacks' span ms in that question's timeline; search p50/p90 over items that have it.
- per-pack window = [first sql span start, last sql span end] of that pack's db inside the search span (valid under
  both serial and Promise.all), with that pack's sql ms and the rows fetched by 'FROM blocks' queries (block misses).
- hit identity = ordered retrievedTitles equal to arm A's on every item.
- PSS peak = max app_pss_kb in telemetry.csv (5 s sampling, so a lower bound of the true peak).
Percentiles: linear interpolation (same as partime_analyze.py)."""
import argparse, json, os, re, sys

def pct(xs, p):
    xs = sorted(xs)
    if not xs: return None
    k = (len(xs) - 1) * p; f = int(k); c = min(f + 1, len(xs) - 1)
    return xs[f] + (xs[c] - xs[f]) * (k - f)

def per_question(q):
    it = q["items"]; sw = [i for i in it if i.get("name") == "search-wikipacks"]
    r = {"retrieve_ms": round(sum(i["ms"] for i in it if i.get("kind") == "retrieve"), 1)}
    if not sw: r["search_ms"] = None; r["packs"] = {}; r["blocks_rows"] = 0; return r
    r["search_ms"] = round(sum(i["ms"] for i in sw), 1)
    s0, s1 = min(i["t"] - i["ms"] for i in sw), max(i["t"] for i in sw)
    packs = {}
    for i in it:
        lab = i.get("label") or ""
        if i.get("name") != "sql" or not lab.startswith("boar-"): continue
        a, b = i["t"] - i["ms"], i["t"]
        if a < s0 - 1 or b > s1 + 1: continue
        db = lab.split("|")[0].replace(".sqlite", "")
        p = packs.setdefault(db, {"start": a, "end": b, "sql_ms": 0.0, "blocks_rows": 0, "blocks_q": 0})
        p["start"] = min(p["start"], a); p["end"] = max(p["end"], b); p["sql_ms"] += i["ms"]
        if "FROM blocks" in lab: p["blocks_rows"] += i.get("n") or 0; p["blocks_q"] += 1
    for p in packs.values():
        p["window_ms"] = round(p["end"] - p["start"], 1); p["start_rel_ms"] = round(p["start"] - s0, 1)
        p["sql_ms"] = round(p["sql_ms"], 1); del p["start"], p["end"]
    r["packs"] = packs; r["blocks_rows"] = sum(p["blocks_rows"] for p in packs.values())
    return r

def load_run(d):
    rows = [json.loads(l) for l in open(os.path.join(d, "rows.jsonl"), encoding="utf-8") if l.strip()]
    bench = json.load(open(os.path.join(d, "bench.json")))
    tl = {}
    for q in bench["timeline"]: tl.setdefault(q["query"], q)
    out = {}
    for r in rows:
        q = tl.get(r["query"]); d_ = per_question(q) if q else {"search_ms": None, "packs": {}, "blocks_rows": 0}
        d_.update(total_ms=round(r["totalLatencyMs"], 1), ttft_ms=round(r.get("ttftMs") or 0, 1), titles=r.get("retrievedTitles") or [],
                  declined=r.get("declined"), tier=r.get("tier"), category=r.get("category"))
        out[r["queryId"]] = d_
    return out, bench

def telemetry(d):
    p = os.path.join(d, "telemetry.csv"); t = {"pss_peak_kb": None, "temp_first_dC": None, "temp_last_dC": None, "temp_max_dC": None, "thermal_max": None}
    if not os.path.exists(p): return t
    L = [l.strip().split(",") for l in open(p) if l.strip()][1:]
    pss = [int(x[4]) for x in L if len(x) > 4 and x[4].isdigit()]; tmp = [int(x[2]) for x in L if x[2].isdigit()]
    th = [int(x[3]) for x in L if x[3].isdigit()]
    return {"pss_peak_kb": max(pss) if pss else None, "temp_first_dC": tmp[0] if tmp else None, "temp_last_dC": tmp[-1] if tmp else None,
            "temp_max_dC": max(tmp) if tmp else None, "thermal_max": max(th) if th else None, "samples": len(L)}

def lmk(d):
    p = os.path.join(d, "logcat.txt")
    if not os.path.exists(p): return None
    s = open(p, encoding="utf-8", errors="replace").read()
    return len([l for l in s.splitlines() if re.search(r"lowmemorykiller|lmkd.*[Kk]ill", l) and "boarbench" in l])

def arm_summary(d, ids):
    qs, bench = load_run(d)
    items = [i for i in ids if i in qs]
    S = [qs[i]["search_ms"] for i in items if qs[i]["search_ms"] is not None]
    T = [qs[i]["total_ms"] for i in items]
    g = os.path.join(d, "e1par-thermal.json")
    return {"dir": d, "tree": (bench.get("engine") or {}).get("treeHash", "")[:12], "requestId": bench.get("requestId"),
            "n_items": len(items), "missing": [i for i in ids if i not in qs], "n_search": len(S),
            "search_p50_s": r3(pct(S, .5)), "search_p90_s": r3(pct(S, .9)), "answer_p50_s": r3(pct(T, .5)), "answer_p90_s": r3(pct(T, .9)),
            "blocks_rows_total": sum(qs[i]["blocks_rows"] for i in items), "telemetry": telemetry(d), "lmk_lines": lmk(d),
            "thermal_gate": json.load(open(g)) if os.path.exists(g) else None}, qs

def r3(x): return None if x is None else round(x / 1000, 3)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("results"); ap.add_argument("--arm", action="append", default=[])
    ap.add_argument("--ref"); ap.add_argument("--json"); ap.add_argument("--request", default=None)
    a = ap.parse_args()
    arms = dict(x.split("=", 1) for x in a.arm) or {k: f"e1par-{k}" for k in "abed"}
    arms = {k: v for k, v in arms.items() if os.path.exists(os.path.join(a.results, v, "rows.jsonl"))}
    req = a.request or os.path.join(os.path.dirname(os.path.abspath(a.results)), "requests", "e1par-a.request.json")
    ids = [q["id"] for q in json.load(open(req))["questions"] if q["id"] != "warmup-000"]
    out = {"ids": ids, "arms": {}, "perq": {}}
    if a.ref:
        s, _ = arm_summary(os.path.join(a.results, a.ref), ids); out["ref"] = {a.ref: {k: s[k] for k in ("n_items", "search_p50_s", "answer_p50_s", "blocks_rows_total")}}
    Q = {}
    for k, run in arms.items():
        s, qs = arm_summary(os.path.join(a.results, run), ids); out["arms"][k] = s; Q[k] = qs
    # hit identity vs A (ordered retrievedTitles)
    if "a" in Q:
        for k in Q:
            diff = [i for i in ids if i in Q[k] and i in Q["a"] and Q[k][i]["titles"] != Q["a"][i]["titles"]]
            out["arms"][k]["titles_diff_vs_a"] = diff
            out["arms"][k]["titles_identical_vs_a"] = not diff and not out["arms"][k]["missing"]
    for i in ids:
        out["perq"][i] = {k: {"search_ms": Q[k][i]["search_ms"], "total_ms": Q[k][i]["total_ms"], "ttft_ms": Q[k][i]["ttft_ms"],
                              "blocks_rows": Q[k][i]["blocks_rows"], "titles": Q[k][i]["titles"],
                              "packs": {p: [v["start_rel_ms"], v["window_ms"], v["sql_ms"], v["blocks_rows"]] for p, v in Q[k][i]["packs"].items()}}
                          for k in Q if i in Q[k]}
    # frozen clauses (E1-PAR-criterion.md)
    A = out["arms"]; v = {}
    pss = lambda k: (A[k]["telemetry"]["pss_peak_kb"] or 0) / 1024 / 1024
    def stop(k):
        return bool(A[k]["lmk_lines"]) or ("a" in A and pss(k) > pss("a") + 0.3)
    if "a" in A and "b" in A:
        dS = A["a"]["search_p50_s"] - A["b"]["search_p50_s"]; dT = A["a"]["answer_p50_s"] - A["b"]["answer_p50_s"]
        v["B"] = {"identity": A["b"]["titles_identical_vs_a"], "search_drop_s": round(dS, 3), "answer_drop_s": round(dT, 3),
                  "stop_rule": stop("b"), "pss_delta_vs_a_gb": round(pss("b") - pss("a"), 3),
                  "verdict": "VOID" if not A["b"]["titles_identical_vs_a"] else "STOP" if stop("b") else
                             "PAYS" if dS >= 0.8 and dT >= 0.8 else "DOES-NOT-PAY"}
    for k, lab in (("e", "E"), ("d", "D")):
        if k in A and "b" in A and "a" in A:
            ratio = A[k]["search_p50_s"] / A["b"]["search_p50_s"]; dB = A["b"]["search_p50_s"] - A[k]["search_p50_s"]
            dpss = pss(k) - pss("b"); ident = A[k]["titles_identical_vs_a"] and A["b"]["titles_identical_vs_a"]
            r = {"identity_vs_a_and_b": ident, "ratio_search_vs_b": round(ratio, 3), "search_drop_vs_b_s": round(dB, 3),
                 "pss_delta_vs_b_gb": round(dpss, 3), "stop_rule": stop(k), "cache_lever_closed_lt_0p4": dB < 0.4}
            if k == "e":
                r["clause1_ratio_le_0p6"] = ratio <= 0.6; r["clause2_identity"] = ident; r["clause3_pss_le_0p032"] = dpss <= 0.032
                r["verdict"] = "STOP" if stop(k) else "ADOPT" if (ratio <= 0.6 and ident and dpss <= 0.032) else "KILL"
            else:
                r["verdict"] = "VOID" if not ident else "STOP" if stop(k) else "PAYS-OVER-B" if dB >= 0.8 else "MEASURED"
            v[lab] = r
    out["verdicts"] = v
    if a.json: json.dump(out, open(a.json, "w"), indent=1)
    # human table
    print(f"{'arm':4}{'tree':14}{'n':>3}{'srch p50':>9}{'p90':>7}{'ans p50':>8}{'p90':>7}{'blkrows':>8}{'PSSpk GB':>9}{'T0-T1 C':>12}{'LMK':>4}  ident")
    for k, s in out["arms"].items():
        t = s["telemetry"]; g = s["thermal_gate"] or {}
        tb = g.get("before", {}).get("batteryDc", t["temp_first_dC"]); ta = g.get("after", {}).get("batteryDc", t["temp_last_dC"])
        print(f"{k:4}{s['tree']:14}{s['n_items']:>3}{s['search_p50_s']:>9}{s['search_p90_s']:>7}{s['answer_p50_s']:>8}{s['answer_p90_s']:>7}"
              f"{s['blocks_rows_total']:>8}{pss(k):>9.3f}{(f'{tb/10:.1f}-{ta/10:.1f}' if tb and ta else '?'):>12}{s['lmk_lines']!s:>4}  {s.get('titles_identical_vs_a')}")
    if "ref" in out: print("ref", json.dumps(out["ref"]))
    print(json.dumps(v, indent=1))

if __name__ == "__main__":
    main()
