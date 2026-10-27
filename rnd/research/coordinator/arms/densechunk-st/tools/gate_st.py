"""DENSECHUNK-ST step 0 gates G1-G3 (criterion sha 24793013…). Run: python3 -I gate_st.py  (after d0_st.py).
G1 reach: 180 items, fact chunk in raw[:6] ON >= ceil(1.25 x OFF) AND fact article in kept ON >= OFF.
G2 no-harm (kit only, sidecars on crypto + wikivoyage): v0.1 public gold-in-kept ON >= OFF; v0.2 resolvable gold (the 9
   p4b-diag ids) in raw6 and in kept ON >= OFF; empty kept not up (v0.1, v0.2, 180); churn reported. v0.2 lines are read
   script-only (gold match booleans and counts; nothing printed but counts).
G3 cost: retrieval p50 ON <= 2 x OFF (warm second off pass; first off pass reported) on the 180; the item pack's two-stage
   scan (lead + chunk ms, first-load excluded and reported) <= 300 ms per query on boar-simplewiki-en (max over its 20 items).
Writes aggregates/gate-st.json (counts/ids only)."""
import json, math, re, os, statistics as st
ROOT = "<workspace>"; ARM = f"{ROOT}/rnd/research/coordinator/arms/densechunk-st"
load = lambda f: [json.loads(l) for l in open(f) if l.strip()]
_LIB = re.compile(r"^[^:]{2,40}:\s+")
norm = lambda s: " ".join(str(s or "").split()).lower()
bare = lambda t: _LIB.sub("", str(t or ""))
def gmatch(gold, ref):  # p4b_diag / scorers/retrieval.py rule
    title, _, section = gold.partition("#")
    if norm(title) != norm(ref.get("title")) and (_LIB.match(title) or norm(title) != norm(bare(ref.get("title")))): return False
    return not section or norm(section) == norm(ref.get("section"))
def passes(lines):
    out, seen = {}, {}
    for l in lines:
        n = seen.get((l["mode"], l["id"]), 0); seen[(l["mode"], l["id"])] = n + 1
        out.setdefault(l["mode"] + ("2" if n else ""), {})[l["id"]] = l
    return out
def key(l):
    return json.dumps([[x.get(k) for k in ("chunkId", "title", "section", "source", "similarity", "via")] for x in l["raw"]] + [[x.get("chunkId"), x.get("title")] for x in l["kept"]])
def kitset(f, tk2f, gold, ids=None):
    P = passes(load(f)); T = {l["id"]: l for l in load(tk2f)} if os.path.exists(tk2f) else {}
    G = {k: v for k, v in gold.items() if isinstance(v, list) and v}
    sel = ids if ids is not None else sorted(G)
    r = {"n_items": len(P.get("off", {})), "gold_items": len(sel)}
    for m in ("off", "on"):
        L = P[m]
        r[m] = {"gold_raw6": sum(any(gmatch(g, x) for g in G.get(i, []) for x in L[i]["raw"][:6]) for i in sel if i in L),
                "gold_kept": sum(any(gmatch(g, x) for g in G.get(i, []) for x in L[i]["kept"]) for i in sel if i in L),
                "empty_kept_retrieving": sum(1 for l in L.values() if l["raw"] and not l["kept"]),
                "ms_p50": round(st.median([l["ms"] for l in L.values() if l["ms"] is not None]), 1)}
    r["ms_p50_off2"] = round(st.median([l["ms"] for l in P["off2"].values() if l["ms"] is not None]), 1) if "off2" in P else None
    r["churn_raw"] = sum(P["off"][i]["raw"] != P["on"][i]["raw"] and [x["chunkId"] for x in P["off"][i]["raw"]] != [x["chunkId"] for x in P["on"][i]["raw"]] for i in P["off"])
    r["churn_kept"] = sum([x["chunkId"] for x in P["off"][i]["kept"]] != [x["chunkId"] for x in P["on"][i]["kept"]] for i in P["off"])
    r["off_vs_tk2_identical"] = f"{sum(key(P['off'][i]) == key(T[i]) for i in P['off'] if i in T)}/{sum(i in T for i in P['off'])}"
    r["off_vs_off2_identical"] = f"{sum(key(P['off'][i]) == key(P['off2'][i]) for i in P['off'] if i in P.get('off2', {}))}/{len(P.get('off2', {}))}"
    return r

def main():
    d0 = json.load(open(f"{ARM}/aggregates/d0-st.json")); a = d0["all"]
    off, on = a["off"], a["on"]
    need = math.ceil(1.25 * off["chunk_raw6"] - 1e-9)
    g1 = {"chunk_raw6_off": off["chunk_raw6"], "chunk_raw6_on": on["chunk_raw6"], "need_on": need,
          "art_kept_off": off["art_kept"], "art_kept_on": on["art_kept"], "n": a["n"], "packs_done": d0["packs_done"]}
    g1["pass"] = a["n"] == 180 and on["chunk_raw6"] >= need and on["art_kept"] >= off["art_kept"]
    v01 = kitset(f"{ARM}/runs/v01-kit.jsonl", f"{ARM}/runs/v01-kit.tk2.jsonl", json.load(open(f"{ROOT}/boar-eval/bench/v0.1/gold/sources.json")))
    p4b = json.load(open(f"{ROOT}/rnd/research/coordinator/arms/packcond/aggregates/p4b-diag.json"))["items"]
    res = sorted(x["id"] for x in p4b if x["set"] == "v02" and any(t["kind"] == "gold" and t["resolved"] for t in x["targets"]))
    B = f"{ROOT}/blind/bench-v02/runs-packs"
    g2v02 = json.load(open(f"{ROOT}/boar-eval/bench/v0.2/gold/sources.json"))
    v02 = kitset(f"{B}/densechunk-st-v02-kit.jsonl", f"{B}/densechunk-st-v02-kit.tk2.jsonl", g2v02, res)
    v02all = kitset(f"{B}/densechunk-st-v02-kit.jsonl", f"{B}/densechunk-st-v02-kit.tk2.jsonl", g2v02)
    st180 = {"empty_kept_off": off["empty_kept"], "empty_kept_on": on["empty_kept"], "churn_raw": a["churn_raw"], "churn_kept": a["churn_kept"]}
    g2 = {"v01": v01, "v02_resolvable": v02 | {"ids": res}, "v02_all_gold_descriptive": {k: v02all[k] for k in ("gold_items", "off", "on")}, "selftest180": st180}
    g2["pass"] = (v01["on"]["gold_kept"] >= v01["off"]["gold_kept"] and v02["on"]["gold_raw6"] >= v02["off"]["gold_raw6"]
                  and v02["on"]["gold_kept"] >= v02["off"]["gold_kept"]
                  and v01["on"]["empty_kept_retrieving"] <= v01["off"]["empty_kept_retrieving"]
                  and v02["on"]["empty_kept_retrieving"] <= v02["off"]["empty_kept_retrieving"])
    # the 180 self-test items' empty-kept is reported (selftest180), not gated: G2 is the kit no-harm check
    sw = d0["per_pack"].get("boar-simplewiki-en", {}).get("scan_ms", {})
    g3 = {"ms_p50_off1": a["ms_p50_off"], "ms_p50_off2": a["ms_p50_off2"], "ms_p50_on": a["ms_p50_on"],
          "ratio_on_off2": round(a["ms_p50_on"] / a["ms_p50_off2"], 2) if a["ms_p50_off2"] else None, "simplewiki_scan_ms": sw,
          "per_pack_scan_ms": {p: v["scan_ms"] for p, v in d0["per_pack"].items()}}
    g3["pass"] = bool(g3["ratio_on_off2"] is not None and g3["ratio_on_off2"] <= 2 and sw.get("max") is not None and sw["max"] <= 300)
    out = {"criterion_sha256": d0["criterion_sha256"], "G1": g1, "G2": g2, "G3": g3,
           "verdict_step0": "PASS -> stage 1" if g1["pass"] and g2["pass"] and g3["pass"] else "FAIL at step 0"}
    json.dump(out, open(f"{ARM}/aggregates/gate-st.json", "w"), indent=1)
    print(json.dumps({"G1": g1, "G2pass": g2["pass"], "G3": {k: g3[k] for k in ("ms_p50_off2", "ms_p50_on", "ratio_on_off2", "simplewiki_scan_ms", "pass")}, "verdict": out["verdict_step0"]}))
main()
