"""GROUND-ST step 0 gates G1-G3 (criterion GROUND-ST-criterion.md, sha in its .sha256), for both variants (ground = packGround
true, top1 = packGround "top1"). Run: python3 -I gate_gs.py (after d0_gs.py).
G1 (180): fact chunk kept >= 55 AND fact article kept >= 85 AND fact chunk in raw6 unchanged (= OFF, 67).
G2 (RULE 26, kit v0.1 public 60 + v0.2 110): lost-context 0 (OFF kept non-empty -> variant kept empty); empty kept over
OFF-retrieving items <= 11 (v0.1) / <= 28 (v0.2); v0.1 gold kept >= 12; v0.2 resolvable gold (the 9 p4b-diag ids) kept >= 4;
kept lists change on <= 15 % of the 170 kit items, a change that only ADDS pack passages (OFF kept is an ordered subsequence and
every added chunk is a pack chunk) counts as harmless and is reported; context tokens per item never above the cap
(kept tokens <= max(budget, OFF kept tokens)) on kit and 180.
G3: retrieval p50 variant <= 1.2 x OFF (warm OFF2 = the repeated OFF pass; first-pass OFF ratio reported).
Identity: OFF raw+kept (and task/query/k/codes) == ST2's OFF replays 180/180, 60/60, 110/110 (+ DENSECHUNK-ST OFF), OFF == OFF2.
v0.2 lines are read script-only (booleans and counts; ids only for the 9 resolvable). Writes aggregates/gate-gs.json.
Addendum 1: `python3 -I gate_gs.py perpack` gates X3 from runs/*.perpack.jsonl -> aggregates/gate-gs.perpack.json; G3 then
uses retrieval + keep-step (keepMs) p50 vs warm OFF2 (keep-step ratio reported); lost-context ids (v0.1 only; v0.2 counted)
and OFF-kept chunks cut on the kit are added; OFF identity also vs the step-0 OFF."""
import json, re, statistics as st, sys
X = sys.argv[1] if len(sys.argv) > 1 else None
SFX = f".{X}" if X else ""
ROOT = "<workspace>"; ARM = f"{ROOT}/rnd/research/coordinator/arms/groundst"
DC = f"{ROOT}/rnd/research/coordinator/arms/densechunk-st/runs"; B = f"{ROOT}/blind/bench-v02/runs-packs"
VAR = (X,) if X else ("ground", "top1")
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
def add_only(o, v):
    it = iter(v); sub = all(c in it for c in o)
    return sub and all(str(c).startswith("pack:") for c in v if c not in set(o))
def ident(P, refs):
    return {name: f"{sum(key(P['off'][i]) == key(R['off'][i]) for i in P['off'] if i in R['off'])}/{sum(i in R['off'] for i in P['off'])}" for name, R in refs.items()}
def p50(L): return round(st.median([l["ms"] for l in L.values() if l["ms"] is not None]), 1)
def kp50(L):
    v = [l["keepMs"] for l in L.values() if l.get("keepMs") is not None]; return round(st.median(v), 3) if v else None
def tp50(L):
    v = [l["ms"] + l["keepMs"] for l in L.values() if l["ms"] is not None and l.get("keepMs") is not None]; return round(st.median(v), 1) if v else None

def kitset(P, gold, sel):
    G = {k: v for k, v in gold.items() if isinstance(v, list) and v}
    r = {"n_items": len(P["off"]), "gold_items": len(sel), "ms_p50_off2": p50(P["off2"]), "keep_ms_p50_off2": kp50(P["off2"]), "total_ms_p50_off2": tp50(P["off2"])}
    for m in ("off",) + VAR:
        L = P[m]
        r[m] = {"gold_raw": sum(any(gmatch(g, x) for g in G.get(i, []) for x in L[i]["raw"]) for i in sel if i in L),
                "gold_kept": sum(any(gmatch(g, x) for g in G.get(i, []) for x in L[i]["kept"]) for i in sel if i in L),
                "empty_kept_off_retrieving": sum(1 for i, o in P["off"].items() if o["raw"] and not L[i]["kept"]),
                "kept_slots": sum(len(l["kept"]) for l in L.values()), "ms_p50": p50(L), "keep_ms_p50": kp50(L), "total_ms_p50": tp50(L)}
        if m == "off": continue
        O = P["off"]
        ch = [i for i in O if ids(O[i]["kept"]) != ids(L[i]["kept"])]
        add = [i for i in ch if add_only(ids(O[i]["kept"]), ids(L[i]["kept"]))]
        r[m] |= {"lost_context": sum(1 for i in O if O[i]["kept"] and not L[i]["kept"]),
                 "lost_context_ids": [i for i in O if O[i]["kept"] and not L[i]["kept"]],
                 "off_kept_chunks_cut": sum(1 for i in O for c in ids(O[i]["kept"]) if c not in set(ids(L[i]["kept"]))),
                 "cut_code_sum": sum(int(c.split("-")[-1]) for i in O for c in L[i].get("keepCodes", []) if c.startswith("packground:cut-")),
                 "kept_changed": len(ch), "kept_changed_add_only": len(add), "kept_changed_other": len(ch) - len(add),
                 "off_kept_chunk_dropped_items": sum(1 for i in ch if any(c not in set(ids(L[i]["kept"])) for c in ids(O[i]["kept"]))),
                 "empty_filled": sum(1 for i in O if O[i]["raw"] and not O[i]["kept"] and L[i]["kept"]),
                 "raw_identical": sum(ids(O[i]["raw"]) == ids(L[i]["raw"]) for i in O),
                 "tokens_over_cap": sum(1 for i in O if L[i].get("budget") is not None and L[i]["keptTokens"] > max(L[i]["budget"], O[i]["keptTokens"])),
                 "max_tokens_over_budget": max([L[i]["keptTokens"] - L[i]["budget"] for i in O if L[i].get("budget") is not None] or [0]),
                 "keep_codes": {c: sum(c in L[i].get("keepCodes", []) for i in O) for c in sorted({c for i in O for c in L[i].get("keepCodes", [])})}}
    r["off_vs_off2_identical"] = f"{sum(key(P['off'][i]) == key(P['off2'][i]) for i in P['off'])}/{len(P['off'])}"
    return r

def main():
    sha = open(f"{ARM}/GROUND-ST-criterion.sha256").read().split()[0]
    d0 = json.load(open(f"{ARM}/aggregates/d0-gs{SFX}.json")); a = d0["all"]
    P1 = passes(load(f"{ARM}/runs/v01-kit.gs{SFX}.jsonl"))
    v01 = kitset(P1, json.load(open(f"{ROOT}/boar-eval/bench/v0.1/gold/sources.json")), sorted(k for k, v in json.load(open(f"{ROOT}/boar-eval/bench/v0.1/gold/sources.json")).items() if isinstance(v, list) and v))
    v01["identity"] = ident(P1, {"st2_off": passes(load(f"{DC}/v01-kit.st2.jsonl")), "st_off": passes(load(f"{DC}/v01-kit.jsonl")),
                                 **({"step0_off": passes(load(f"{ARM}/runs/v01-kit.gs.jsonl"))} if X else {})})
    p4b = json.load(open(f"{ROOT}/rnd/research/coordinator/arms/packcond/aggregates/p4b-diag.json"))["items"]
    res = sorted(x["id"] for x in p4b if x["set"] == "v02" and any(t["kind"] == "gold" and t["resolved"] for t in x["targets"]))
    P2 = passes(load(f"{B}/groundst-v02-kit{SFX}.jsonl")); gv = json.load(open(f"{ROOT}/boar-eval/bench/v0.2/gold/sources.json"))
    v02 = kitset(P2, gv, res)
    v02["identity"] = ident(P2, {"st2_off": passes(load(f"{B}/densechunk-st2-v02-kit.jsonl")), "st_off": passes(load(f"{B}/densechunk-st-v02-kit.jsonl")),
                                 **({"step0_off": passes(load(f"{B}/groundst-v02-kit.jsonl"))} if X else {})})
    for m in VAR: v02[m]["lost_context_ids"] = f"{len(v02[m]['lost_context_ids'])} (blind: ids not printed)"
    v02all = {m: kitset(P2, gv, sorted(k for k, v in gv.items() if isinstance(v, list) and v))[m]["gold_kept"] for m in ("off",) + VAR}
    nkit = v01["n_items"] + v02["n_items"]
    out = {"criterion_sha256": sha, "identity_180": {"off_vs_st2ref": a["off_same_as_st2ref"], "off_vs_off2": a["off_repeat_same"],
           "diag_agree_nonspecial": a["diag_agree_nonspecial"], **({"off_vs_step0_off": a["off_same_as_step0"]} if X else {})}, "D0": {"chunk_loss": a["chunk_loss"], "art_loss": a["art_loss"]},
           "kit": {"v01": v01, "v02_resolvable": v02 | {"ids": res}, "v02_all_gold_kept_descriptive": v02all}, "variants": {}}
    for m in VAR:
        g1 = {"chunk_raw6_off": a["off"]["chunk_raw6"], "chunk_raw6": a[m]["chunk_raw6"], "raw_same_180": a[f"{m}_raw_same"],
              "chunk_kept_off": a["off"]["chunk_kept"], "chunk_kept": a[m]["chunk_kept"], "need_chunk_kept": 55,
              "art_kept_off": a["off"]["art_kept"], "art_kept": a[m]["art_kept"], "need_art_kept": 85,
              "empty_kept_off": a["off"]["empty_kept"], "empty_kept": a[m]["empty_kept"], "enter_leave": a[f"{m}_enter_leave"]}
        g1["pass"] = a["n"] == 180 and a[m]["chunk_kept"] >= 55 and a[m]["art_kept"] >= 85 and a[m]["chunk_raw6"] == a["off"]["chunk_raw6"]
        changed_other = v01[m]["kept_changed_other"] + v02[m]["kept_changed_other"]
        changed_all = v01[m]["kept_changed"] + v02[m]["kept_changed"]
        g2 = {"lost_context": v01[m]["lost_context"] + v02[m]["lost_context"],
              "empty_kept_v01": v01[m]["empty_kept_off_retrieving"], "empty_kept_v01_off": v01["off"]["empty_kept_off_retrieving"], "need_v01": 11,
              "empty_kept_v02": v02[m]["empty_kept_off_retrieving"], "empty_kept_v02_off": v02["off"]["empty_kept_off_retrieving"], "need_v02": 28,
              "v01_gold_kept": v01[m]["gold_kept"], "v01_gold_kept_off": v01["off"]["gold_kept"], "v02_res_gold_kept": v02[m]["gold_kept"], "v02_res_gold_kept_off": v02["off"]["gold_kept"],
              "kit_changed_all": changed_all, "kit_changed_add_only": changed_all - changed_other, "kit_changed_other": changed_other, "kit_n": nkit,
              "kit_change_share_counted": round(changed_other / nkit, 3), "kit_change_share_all": round(changed_all / nkit, 3),
              "tokens_over_cap": v01[m]["tokens_over_cap"] + v02[m]["tokens_over_cap"] + a[f"{m}_tokens_over_budget"],
              "lost_context_ids_v01": v01[m]["lost_context_ids"], "off_kept_chunks_cut_kit": v01[m]["off_kept_chunks_cut"] + v02[m]["off_kept_chunks_cut"],
              "off_kept_chunks_cut_180": a[f"{m}_off_kept_cut_chunks"], "cut_code_sum_kit": v01[m]["cut_code_sum"] + v02[m]["cut_code_sum"]}
        g2["pass"] = (g2["lost_context"] == 0 and g2["empty_kept_v01"] <= 11 and g2["empty_kept_v02"] <= 28 and g2["v01_gold_kept"] >= 12
                      and g2["v02_res_gold_kept"] >= 4 and g2["kit_change_share_counted"] <= 0.15 and g2["tokens_over_cap"] == 0)
        g3 = {"ms_p50_off": a["off"]["ms_p50"], "ms_p50_off2": a["off2"]["ms_p50"], "ms_p50": a[m]["ms_p50"],
              "ratio_vs_off2": round(a[m]["ms_p50"] / a["off2"]["ms_p50"], 2), "ratio_vs_off": round(a[m]["ms_p50"] / a["off"]["ms_p50"], 2),
              "kit_ratio_vs_off2": {"v01": round(v01[m]["ms_p50"] / v01["ms_p50_off2"], 2), "v02": round(v02[m]["ms_p50"] / v02["ms_p50_off2"], 2)}}
        if X:
            g3 |= {"keep_ms_p50_off": a["off"]["keep_ms_p50"], "keep_ms_p50_off2": a["off2"]["keep_ms_p50"], "keep_ms_p50": a[m]["keep_ms_p50"],
                   "keep_ratio_vs_off2": round(a[m]["keep_ms_p50"] / a["off2"]["keep_ms_p50"], 2),
                   "total_ms_p50_off2": a["off2"]["total_ms_p50"], "total_ms_p50": a[m]["total_ms_p50"],
                   "total_ratio_vs_off2": round(a[m]["total_ms_p50"] / a["off2"]["total_ms_p50"], 2),
                   "kit_total_ratio_vs_off2": {"v01": round(v01[m]["total_ms_p50"] / v01["total_ms_p50_off2"], 2), "v02": round(v02[m]["total_ms_p50"] / v02["total_ms_p50_off2"], 2)},
                   "kit_keep_ms_p50": {"v01": [v01["keep_ms_p50_off2"], v01[m]["keep_ms_p50"]], "v02": [v02["keep_ms_p50_off2"], v02[m]["keep_ms_p50"]]}}
            g3["pass"] = g3["total_ratio_vs_off2"] <= 1.2
        else:
            g3["pass"] = g3["ratio_vs_off2"] <= 1.2
        out["variants"][m] = {"G1": g1, "G2": g2, "G3": g3, "pass": g1["pass"] and g2["pass"] and g3["pass"]}
    ok = [m for m in VAR if out["variants"][m]["pass"]]
    best = max(ok, key=lambda m: (out["variants"][m]["G1"]["chunk_kept"], m == "ground")) if ok else None  # tie -> ground (fewer rules)
    out["verdict_step0"] = f"PASS -> stage 1 with {best}" if best else "FAIL at step 0"
    if X: out["addendum"] = {"sha256": open(f"{ARM}/GROUND-ST-criterion-addendum-1.sha256").read().split()[0], "variant": X}
    json.dump(out, open(f"{ARM}/aggregates/gate-gs{SFX}.json", "w"), indent=1)
    print(json.dumps({"identity_180": out["identity_180"], "v01_identity": v01["identity"], "v02_identity": v02["identity"],
                      "off2": [v01["off_vs_off2_identical"], v02["off_vs_off2_identical"]],
                      **{m: {g: {k: v for k, v in out["variants"][m][g].items() if k != "enter_leave"} for g in ("G1", "G2", "G3")} for m in VAR},
                      "verdict": out["verdict_step0"]}, indent=None))
main()
