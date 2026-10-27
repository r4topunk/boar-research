#!/usr/bin/env python3
"""PACKCOND P4b step 0 (PACKDENSE D0): dense article-router headroom + rule simulation, 0 LLM, 0 judge calls.
Inputs: replay-p4b.ts outputs (blind/bench-v02/runs-packcond/p4b-v02.jsonl: 110 v0.2 items, --tasks-from H s42 traces;
arms/packcond/replay/p4b-v01.jsonl: 60 v0.1 public items), aggregates/p4-diag.json (F0 articles + classes), gold files.
Checks: OFF raw lists (full raw objects) identical to pg-off-H32 / pg-off-R20. Simulation of the dense rule on the
engine's raw list: per pack, top-M articles by lead cosine >= floor that are not engine named hits, P passages each
(articlePassages order), inserted after the named/step prefix and before the rest, dedup by chunk id, cut at 6.
Writes aggregates/p4b-diag.json (ids, titles, sections, ranks, cosines, booleans, ms; never text) and prints tables.
usage: p4b_diag.py [--v02 f] [--v01 f]"""
import sys, json, re, argparse, statistics as st
sys.path.insert(0, "<workspace>/rnd/research/coordinator/arms/packcond/tools")
import p4_diag as P
ROOT = "<workspace>"; ARM = f"{ROOT}/rnd/research/coordinator/arms/packcond"; D = f"{ROOT}/blind/bench-v02/runs-packcond"
_LIB = re.compile(r"^[^:]{2,40}:\s+"); norm = lambda s: " ".join(str(s or "").split()).casefold(); bare = lambda t: _LIB.sub("", str(t or ""), count=1)
def gmatch(gold, ref):  # p4_gate / scorers/retrieval.py rule
    title, _, section = gold.partition("#")
    if norm(title) != norm(ref.get("title")) and (_LIB.match(title) or norm(title) != norm(bare(ref.get("title")))): return False
    return not section or norm(section) == norm(ref.get("section"))
load = lambda f: [json.loads(l) for l in open(f) if l.strip()]
K = 6
MS, FLOORS, PS = (1, 2, 3, 5), (0.50, 0.55, 0.60, 0.65, 0.70, 0.75), (1, 2)

def dense(r, M, floor, Pn):
    p = r.get("p4b") or {}
    out = []
    for pk, v in (p.get("packs") or {}).items():
        ex = set(v["engine_named_ids"]); n = 0
        for a in v["top"]:
            if n >= M or a["cos"] < floor: break
            if a["id"] in ex: continue
            n += 1
            for ps in a["passages"][:Pn]: out.append((a["cos"], {"title": ps["title"], "section": ps["section"], "cid": ps["cid"]}))
    return [x for _, x in sorted(out, key=lambda t: -t[0])]

def sim(r, M, floor, Pn):
    p = r.get("p4b") or {}
    raw = [dict(x, cid=c) for x, c in zip(r["raw"], p.get("raw_ids") or [None] * len(r["raw"]))]
    if not p or p.get("no_retrieve") or p.get("error"): return raw[:K]
    pre = raw[:p["prefix_n"]]; ids = {x["cid"] for x in pre}
    add = [x for x in dense(r, M, floor, Pn) if x["cid"] not in ids and not ids.add(x["cid"])]
    rest = [x for x in raw[p["prefix_n"]:] if x["cid"] not in ids]
    return (pre + add + rest)[:K]

key6 = lambda L: [(x["title"], x.get("section")) for x in L[:K]]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--v02", default=f"{D}/p4b-v02.jsonl"); ap.add_argument("--v01", default=f"{ARM}/replay/p4b-v01.jsonl")
    a = ap.parse_args()
    v02 = {r["id"]: r for r in load(a.v02)}; v01 = {r["id"]: r for r in load(a.v01)}
    diag = {x["id"]: x for x in json.load(open(f"{ARM}/aggregates/p4-diag.json"))["H"]["items"]}
    H32 = [l.strip() for l in open(f"{ARM}/inpack-H-v02.ids") if l.strip()]; R20 = [l.strip() for l in open(f"{ROOT}/rnd/research/coordinator/arms/random20-v02.ids") if l.strip()]
    F0 = {i: {pk: set(diag[i]["f0_articles"]) for pk in diag[i]["f0_packs"]} for i in H32}
    G2 = {k: v for k, v in json.load(open(f"{ROOT}/boar-eval/bench/v0.2/gold/sources.json")).items() if isinstance(v, list) and v}
    G1 = {k: v for k, v in json.load(open(f"{ROOT}/boar-eval/bench/v0.1/gold/sources.json")).items() if isinstance(v, list) and v}
    out = {"inputs": {"v02": a.v02, "v01": a.v01}, "K": K}
    # ---- identity check vs P4 OFF runs
    chk = {}
    for n, ids in (("H32", H32), ("R20", R20)):
        ref = {r["id"]: r for r in load(f"{D}/pg-off-{n}.jsonl")}
        f = lambda r: json.dumps([r["raw"], r["kept"], r["codes"], r.get("pool"), r["k"], r["task"]], sort_keys=True)
        chk[n] = {"raw_identical": sum(v02[i]["raw"] == ref[i]["raw"] for i in ids), "all_fields_identical": sum(f(v02[i]) == f(ref[i]) for i in ids), "n": len(ids)}
    out["identity"] = chk; print("identity vs pg-off:", chk)
    # ---- per-item rows
    rows = []
    for setn, R, G in (("v02", v02, G2), ("v01", v01, G1)):
        for i, r in R.items():
            p = r.get("p4b") or {}
            row = {"id": i, "set": setn, "inpack": setn == "v02" and i in F0, "r20": setn == "v02" and i in R20, "class": diag.get(i, {}).get("class") if setn == "v02" else None,
                   "task": r["task"], "k": r["k"], "ms": r["ms"], "raw_titles": [x["title"] for x in r["raw"]], "no_retrieve": bool(p.get("no_retrieve")) or not r["k"],
                   "prefix_n": p.get("prefix_n"), "action": p.get("action"), "explain": p.get("explain"), "packs": {}, "targets": []}
            if setn == "v02" and i in F0: row["f0_in_raw6"] = any(P.is_f0(x, F0[i]) for x in r["raw"][:K]); row["f0_in_pool20"] = any(P.is_f0(x, F0[i]) for x in (r.get("pool") or []))
            if i in G: row["gold_in_raw6"] = any(gmatch(g, x) for g in G[i] for x in r["raw"][:K])
            tgt_ids = set()
            for t in p.get("targets") or []:
                tr = {k: t.get(k) for k in ("kind", "title", "pack", "id", "source", "resolved_title", "named", "share", "engine_named", "bm25_80", "bm25_400", "bm25_2000",
                                            "bm25_rank", "in_pool80", "cov_best", "lead_cos", "lead_rank", "n_chunks")}
                tr["resolved"] = t.get("id") is not None
                if t.get("id") is not None: tgt_ids.add((t["pack"], t["id"]))
                if t["kind"] == "f0":
                    one = {t["pack"]: {t["title"].lower()}}
                    tr["in_raw6"] = any(P.is_f0(x, one) for x in r["raw"][:K]); tr["in_pool20"] = any(P.is_f0(x, one) for x in (r.get("pool") or []))
                else:
                    gs = ("Wikivoyage: " if t["pack"] == "wikivoyage" else "") + t["title"]
                    tr["in_raw6"] = any(gmatch(gs, x) for x in r["raw"][:K]); tr["in_pool20"] = any(gmatch(gs, x) for x in (r.get("pool") or []))
                tr["passages"] = [{k: q[k] for k in ("title", "section", "lead", "cov")} for q in t.get("passages") or []]
                row["targets"].append(tr)
            noise = []
            for pk, v in (p.get("packs") or {}).items():
                row["packs"][pk] = {"scan_ms": v["scan_ms"], "cos_ms": v["cos_ms"], "n_articles": v["n_articles"], "named": v["named"], "engine_named_ids": v["engine_named_ids"],
                                    "top5": [{"id": x["id"], "title": x["title"], "cos": x["cos"]} for x in v["top"][:5]]}
                nt = next((x["cos"] for x in v["top"] if (pk, x["id"]) not in tgt_ids), None)
                if nt is not None: noise.append(nt)
            row["top_nontarget_cos"] = max(noise) if noise else None
            rows.append(row)
    out["items"] = rows
    byid = {(r["set"], r["id"]): r for r in rows}
    # ---- headroom
    def best(i):
        ts = [t for t in byid[("v02", i)]["targets"] if t["kind"] == "f0" and t["resolved"]]
        mn = lambda k: min([t[k] for t in ts if t[k] is not None], default=None)
        return {"n_res": len(ts), "lead_rank": mn("lead_rank"), "lead_cos": max([t["lead_cos"] for t in ts if t["lead_cos"] is not None], default=None),
                "bm25_80": mn("bm25_80"), "bm25_400": mn("bm25_400"), "bm25_2000": mn("bm25_2000"), "cov": max([t["cov_best"] or 0 for t in ts], default=None),
                "named": any(t["named"] for t in ts), "no_retrieve": byid[("v02", i)]["no_retrieve"]}
    clsA = [i for i in H32 if diag[i]["class"] == "a"]; inraw = [i for i in H32 if diag[i]["class"] != "a"]
    le = lambda x, n: x is not None and x <= n; ge = lambda x, n: x is not None and x >= n
    head = {}
    for name, ids in (("classA", clsA), ("in_raw", inraw)):
        B = [best(i) for i in ids]
        head[name] = {"n": len(ids), "no_retrieve": sum(b["no_retrieve"] for b in B), "unresolved": sum(b["n_res"] == 0 for b in B),
                      **{f"lead_rank<={n}": sum(le(b["lead_rank"], n) for b in B) for n in (1, 3, 5, 10)},
                      **{f"lead_cos>={c}": sum(ge(b["lead_cos"], c) for b in B) for c in (0.5, 0.55, 0.6, 0.65, 0.7)},
                      **{f"bm25<={n}": sum(le(b[f"bm25_{n}"], n) for b in B) for n in (80, 400, 2000)}, "bm25_absent": sum(b["bm25_2000"] is None for b in B if not b["no_retrieve"]),
                      "cov_best>=0.5": sum(ge(b["cov"], 0.5) for b in B), "named": sum(b["named"] for b in B),
                      "per_item": {i: b for i, b in zip(ids, B)}}
        print(name, {k: v for k, v in head[name].items() if k != "per_item"})
    out["headroom"] = head
    # ---- noise floor
    def pct(xs, q): xs = sorted(x for x in xs if x is not None); return round(xs[min(len(xs) - 1, int(q * len(xs)))], 4) if xs else None
    nf = {}
    for name, sel in (("inpack32", [byid[("v02", i)] for i in H32]), ("v02_all", [r for r in rows if r["set"] == "v02"]), ("v01_all", [r for r in rows if r["set"] == "v01"])):
        xs = [r["top_nontarget_cos"] for r in sel if not r["no_retrieve"]]
        nf[name] = {"n": len([x for x in xs if x is not None]), "p50": pct(xs, .5), "p90": pct(xs, .9), "min": pct(xs, 0), "max": pct(xs, 1)}
    tc = [t["lead_cos"] for i in H32 for t in byid[("v02", i)]["targets"] if t["kind"] == "f0" and t["lead_cos"] is not None]
    nf["f0_target_cos"] = {"n": len(tc), "p50": pct(tc, .5), "p90": pct(tc, .9), "min": pct(tc, 0), "max": pct(tc, 1)}
    out["noise_floor"] = nf; print("noise floor:", nf)
    sc = {pk: [r["packs"][pk]["scan_ms"] for r in rows if pk in r["packs"]] for pk in ("crypto", "wikivoyage")}
    cc = {pk: [r["packs"][pk]["cos_ms"] for r in rows if pk in r["packs"]] for pk in ("crypto", "wikivoyage")}
    out["scan_ms"] = {pk: {"n": len(v), "p50": pct(v, .5), "p90": pct(v, .9), "max": max(v), "cos_only_p50": pct(cc[pk], .5), "cos_only_max": max(cc[pk])} for pk, v in sc.items()}
    out["retrieve_ms"] = {"v02_p50": pct([r["ms"] for r in rows if r["set"] == "v02" and r["ms"]], .5)}
    print("scan_ms:", out["scan_ms"], out["retrieve_ms"])
    # ---- simulation
    base = {"f0": sum(any(P.is_f0(x, F0[i]) for x in v02[i]["raw"][:K]) for i in H32),
            "gold02": sum(any(gmatch(g, x) for g in G2[i] for x in v02[i]["raw"][:K]) for i in G2 if i in v02),
            "gold01": sum(any(gmatch(g, x) for g in G1[i] for x in v01[i]["raw"][:K]) for i in G1 if i in v01)}
    out["baseline"] = base; print("baseline raw6:", base)
    simt = []
    for Pn in PS:
        for M in MS:
            for fl in FLOORS:
                s = {i: sim(v02[i], M, fl, Pn) for i in v02}; s1 = {i: sim(v01[i], M, fl, Pn) for i in v01}
                f0 = {i for i in H32 if any(P.is_f0(x, F0[i]) for x in s[i])}
                b0 = {i for i in H32 if any(P.is_f0(x, F0[i]) for x in v02[i]["raw"][:K])}
                g2 = sum(any(gmatch(g, x) for g in G2[i] for x in s[i]) for i in G2 if i in v02)
                g1 = sum(any(gmatch(g, x) for g in G1[i] for x in s1[i]) for i in G1 if i in v01)
                row = {"P": Pn, "M": M, "floor": fl, "G1_f0_raw6": len(f0), "f0_enter": sorted(f0 - b0), "f0_leave": sorted(b0 - f0),
                       "gold02_raw6": g2, "gold01_raw6": g1, "r20_changed": sum(key6(s[i]) != key6(v02[i]["raw"]) for i in R20),
                       "v02_changed": sum(key6(s[i]) != key6(v02[i]["raw"]) for i in v02), "v01_changed": sum(key6(s1[i]) != key6(v01[i]["raw"]) for i in v01),
                       "added_slots_v02": sum(sum(1 for x in s[i] if x.get("cid") is not None and x["cid"] not in set((v02[i].get("p4b") or {}).get("raw_ids") or [])) for i in v02)}
                row["g3_ok"] = g2 >= base["gold02"] and g1 >= base["gold01"]
                simt.append(row)
    out["simulation"] = simt
    print(f"{'P':>2} {'M':>2} {'floor':>5} {'G1':>3} {'gold02':>6} {'gold01':>6} {'R20chg':>6} {'v02chg':>6} {'v01chg':>6} g3  enter/leave")
    for r in simt: print(f"{r['P']:>2} {r['M']:>2} {r['floor']:>5} {r['G1_f0_raw6']:>3} {r['gold02_raw6']:>6} {r['gold01_raw6']:>6} {r['r20_changed']:>6} {r['v02_changed']:>6} {r['v01_changed']:>6} {str(r['g3_ok'])[0]}  {len(r['f0_enter'])}/{len(r['f0_leave'])}")
    ok = [r for r in simt if r["g3_ok"]]
    dec = max(ok, key=lambda r: (r["G1_f0_raw6"], -r["r20_changed"], -r["added_slots_v02"], r["gold02_raw6"] + r["gold01_raw6"], r["floor"], -r["P"]))
    # tiebreak after G1: least control churn, fewest displaced slots, most gold, higher floor, fewer passages if ok else None
    out["declared"] = dec and {k: dec[k] for k in ("P", "M", "floor", "G1_f0_raw6", "gold02_raw6", "gold01_raw6", "r20_changed", "v02_changed", "v01_changed", "added_slots_v02", "f0_enter", "f0_leave")}
    print("declared:", out["declared"])
    json.dump(out, open(f"{ARM}/aggregates/p4b-diag.json", "w"), indent=1)
    print("wrote", f"{ARM}/aggregates/p4b-diag.json")

if __name__ == "__main__": main()
