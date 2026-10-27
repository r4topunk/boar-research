"""DENSECHUNK-ST2 step 0 gates G1-G3 (criterion DENSECHUNK-ST2-criterion.md, sha in its .sha256). Run: python3 -I gate_st2.py
(after d0_st2.py). G1: 180 items, fact chunk in raw[:8] (extra) >= 84 AND fact chunk in kept >= 51 AND fact article in
kept >= 68. G2 (kit, sidecars on crypto + wikivoyage): v0.1 gold-in-kept >= 12; v0.2 resolvable gold (the 9 p4b-diag ids)
raw >= 6 (raw = the appended list) and kept >= 4; empty kept (retrieving items) <= 11 (v0.1), <= 28 (v0.2); the kit kept-slot
share of appended dense chunks reported, <= 0.40. G3: retrieval p50 extra <= 2 x off2 (warm) on the 180; simplewiki
two-stage scan max <= 300 ms. Differentials: kit off vs DENSECHUNK-ST off, kit on (fusion) vs DENSECHUNK-ST on.
v0.2 lines are read script-only (booleans and counts; nothing printed but counts). Writes aggregates/gate-st2.json."""
import json, re, os, statistics as st
ROOT = "<workspace>"; ARM = f"{ROOT}/rnd/research/coordinator/arms/densechunk-st"
load = lambda f: [json.loads(l) for l in open(f) if l.strip()]
_LIB = re.compile(r"^[^:]{2,40}:\s+")
norm = lambda s: " ".join(str(s or "").split()).lower()
bare = lambda t: _LIB.sub("", str(t or ""))
def gmatch(gold, ref):
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
    return json.dumps([[x.get(k) for k in ("chunkId", "title", "section", "source", "similarity", "via")] for x in l["raw"]]
                      + [[x.get(k) for k in ("chunkId", "title", "section", "source")] for x in l["kept"]] + [l.get("task"), l.get("query"), l.get("k"), l.get("codes")])
ids = lambda xs: [x.get("chunkId") for x in xs]
def kitset(f, stf, gold, sel=None):
    P = passes(load(f)); S = passes(load(stf))
    G = {k: v for k, v in gold.items() if isinstance(v, list) and v}
    sel = sel if sel is not None else sorted(G)
    r = {"n_items": len(P["off"]), "gold_items": len(sel)}
    for m in ("off", "on", "extra"):
        L = P[m]
        r[m] = {"gold_raw6": sum(any(gmatch(g, x) for g in G.get(i, []) for x in L[i]["raw"][:6]) for i in sel if i in L),
                "gold_raw": sum(any(gmatch(g, x) for g in G.get(i, []) for x in L[i]["raw"]) for i in sel if i in L),
                "gold_kept": sum(any(gmatch(g, x) for g in G.get(i, []) for x in L[i]["kept"]) for i in sel if i in L),
                "empty_kept_retrieving": sum(1 for l in L.values() if l["raw"] and not l["kept"]),
                "kept_slots": sum(len(l["kept"]) for l in L.values()),
                "ms_p50": round(st.median([l["ms"] for l in L.values() if l["ms"] is not None]), 1)}
    r["ms_p50_off2"] = round(st.median([l["ms"] for l in P["off2"].values() if l["ms"] is not None]), 1)
    app_kept = app_raw = app_items = pre = 0
    for i, o in P["off"].items():
        e = P["extra"][i]; oi, ei = ids(o["raw"]), ids(e["raw"])
        pre += ei[:len(oi)] == oi; app = ei[len(oi):]; app_raw += len(app); app_items += bool(app)
        kk = set(ids(e["kept"])); app_kept += sum(c in kk for c in app)
    r["appended"] = {"items": app_items, "raw_slots": app_raw, "kept_slots": app_kept, "prefix_ok": f"{pre}/{len(P['off'])}",
                     "kept_share": round(app_kept / r["extra"]["kept_slots"], 3) if r["extra"]["kept_slots"] else None}
    # descriptive split of the extra empty-kept count: items OFF already retrieved for vs items OFF retrieved nothing for
    # (raw empty in OFF, so not in OFF's count) that now retrieve only appended dense chunks, all dropped by grounding
    r["empty_kept_split"] = {"off_retrieving_items_empty_extra": sum(1 for i, o in P["off"].items() if o["raw"] and not P["extra"][i]["kept"]),
                             "new_retrieving_items_empty": sum(1 for i, o in P["off"].items() if not o["raw"] and P["extra"][i]["raw"] and not P["extra"][i]["kept"]),
                             "new_retrieving_items_kept": sum(1 for i, o in P["off"].items() if not o["raw"] and P["extra"][i]["kept"]),
                             "off_empty_now_kept": sum(1 for i, o in P["off"].items() if o["raw"] and not o["kept"] and P["extra"][i]["kept"]),
                             "off_kept_now_empty": sum(1 for i, o in P["off"].items() if o["kept"] and not P["extra"][i]["kept"])}
    r["churn_kept_extra"] = sum(ids(P["off"][i]["kept"]) != ids(P["extra"][i]["kept"]) for i in P["off"])
    r["off_kept_lost_items"] = sum(any(c not in set(ids(P["extra"][i]["kept"])) for c in ids(P["off"][i]["kept"])) for i in P["off"])
    r["off_vs_st_off_identical"] = f"{sum(key(P['off'][i]) == key(S['off'][i]) for i in P['off'] if i in S['off'])}/{sum(i in S['off'] for i in P['off'])}"
    r["on_vs_st_on_identical"] = f"{sum(key(P['on'][i]) == key(S['on'][i]) for i in P['on'] if i in S['on'])}/{sum(i in S['on'] for i in P['on'])}"
    r["off_vs_off2_identical"] = f"{sum(key(P['off'][i]) == key(P['off2'][i]) for i in P['off'])}/{len(P['off'])}"
    return r

def main():
    sha = open(f"{ARM}/DENSECHUNK-ST2-criterion.sha256").read().split()[0]
    d0 = json.load(open(f"{ARM}/aggregates/d0-st2.json")); a = d0["all"]; off, ex = a["off"], a["extra"]
    g1 = {"n": a["n"], "chunk_raw6_off": off["chunk_raw6"], "chunk_raw8_extra": ex["chunk_raw8"], "need_raw8": 84,
          "chunk_kept_off": off["chunk_kept"], "chunk_kept_extra": ex["chunk_kept"], "need_kept": 51,
          "art_kept_off": off["art_kept"], "art_kept_extra": ex["art_kept"], "need_art_kept": 68,
          "empty_kept_off": off["empty_kept"], "empty_kept_extra": ex["empty_kept"], "appended_kept_share_180": a["appended_kept_share"],
          "prefix_ok": a["prefix_ok"], "off_same_as_st": a["off_same_as_st"]}
    g1["pass"] = a["n"] == 180 and ex["chunk_raw8"] >= 84 and ex["chunk_kept"] >= 51 and ex["art_kept"] >= 68
    v01 = kitset(f"{ARM}/runs/v01-kit.st2.jsonl", f"{ARM}/runs/v01-kit.jsonl", json.load(open(f"{ROOT}/boar-eval/bench/v0.1/gold/sources.json")))
    p4b = json.load(open(f"{ROOT}/rnd/research/coordinator/arms/packcond/aggregates/p4b-diag.json"))["items"]
    res = sorted(x["id"] for x in p4b if x["set"] == "v02" and any(t["kind"] == "gold" and t["resolved"] for t in x["targets"]))
    B = f"{ROOT}/blind/bench-v02/runs-packs"; gv = json.load(open(f"{ROOT}/boar-eval/bench/v0.2/gold/sources.json"))
    v02 = kitset(f"{B}/densechunk-st2-v02-kit.jsonl", f"{B}/densechunk-st-v02-kit.jsonl", gv, res)
    v02all = kitset(f"{B}/densechunk-st2-v02-kit.jsonl", f"{B}/densechunk-st-v02-kit.jsonl", gv)
    kit_kept = v01["extra"]["kept_slots"] + v02["extra"]["kept_slots"]
    share = round((v01["appended"]["kept_slots"] + v02["appended"]["kept_slots"]) / kit_kept, 3) if kit_kept else 0.0
    g2 = {"v01": v01, "v02_resolvable": v02 | {"ids": res}, "v02_all_gold_descriptive": {k: v02all[k] for k in ("gold_items", "off", "extra")},
          "kit_appended_kept_share": share}
    g2["pass"] = (v01["extra"]["gold_kept"] >= 12 and v02["extra"]["gold_raw"] >= 6 and v02["extra"]["gold_kept"] >= 4
                  and v01["extra"]["empty_kept_retrieving"] <= 11 and v02["extra"]["empty_kept_retrieving"] <= 28 and share <= 0.40)
    sw = d0["per_pack"].get("boar-simplewiki-en", {}).get("scan_ms", {})
    g3 = {"ms_p50_off1": a["ms_p50_off"], "ms_p50_off2": a["ms_p50_off2"], "ms_p50_extra": a["ms_p50_extra"],
          "ratio_extra_off2": round(a["ms_p50_extra"] / a["ms_p50_off2"], 2) if a["ms_p50_off2"] else None, "simplewiki_scan_ms": sw,
          "per_pack_scan_ms": {p: v["scan_ms"] for p, v in d0["per_pack"].items()},
          "kit_ms_p50": {"v01": {m: v01[m]["ms_p50"] for m in ("off", "extra")} | {"off2": v01["ms_p50_off2"]}, "v02": {m: v02[m]["ms_p50"] for m in ("off", "extra")} | {"off2": v02["ms_p50_off2"]}}}
    g3["pass"] = bool(g3["ratio_extra_off2"] is not None and g3["ratio_extra_off2"] <= 2 and sw.get("max") is not None and sw["max"] <= 300)
    out = {"criterion_sha256": sha, "G1": g1, "G2": g2, "G3": g3,
           "verdict_step0": "PASS -> stage 1" if g1["pass"] and g2["pass"] and g3["pass"] else "FAIL at step 0"}
    json.dump(out, open(f"{ARM}/aggregates/gate-st2.json", "w"), indent=1)
    print(json.dumps({"G1": g1, "G2": {"pass": g2["pass"], "share": share, "v01": {k: v01[k] for k in ("off", "extra", "appended", "empty_kept_split", "off_kept_lost_items", "off_vs_st_off_identical", "on_vs_st_on_identical")},
                      "v02res": {k: v02[k] for k in ("off", "extra", "appended", "empty_kept_split", "off_kept_lost_items", "off_vs_st_off_identical", "on_vs_st_on_identical")}},
                      "G3": {k: g3[k] for k in ("ms_p50_off2", "ms_p50_extra", "ratio_extra_off2", "simplewiki_scan_ms", "pass")}, "verdict": out["verdict_step0"]}))
main()
