#!/usr/bin/env python3
"""VALIDATION 2026-10-24 scorer (0 LLM): V0 (a)-(c), V1, V3 layer 1, S1, S8 from replays/<name>. python3 -I vscore.py -> aggregates/*.json + stdout lines.
Reuses retbench/tools/score.py (score(), compare()) with replays read from validation-1024/replays, and coverage-map/tools/chunklevel.py score()."""
import json, os, sys, math, statistics as st
A = "<workspace>/rnd/research/coordinator/arms"; VD = A + "/validation-1024"; RB = A + "/retbench"; CM = A + "/coverage-map"
src = open(RB + "/tools/score.py").read(); src = src[:src.index('if __name__ == "__main__":')]
G = {"__name__": "rbscore"}; exec(compile(src, "score.py", "exec"), G); G["RB"] = VD  # items/ already loaded from retbench; replays now from validation-1024
rd = lambda f: {r["id"]: r for r in (json.loads(l) for l in open(f) if l.strip())} if os.path.exists(f) else {}
jl = lambda f: [json.loads(l) for l in open(f) if l.strip()] if os.path.exists(f) else []
kid = lambda r: [c.get("chunkId") for c in (r.get("keptFull") or [])]
ts = lambda r: [(c.get("title"), c.get("chunkId", "").split(":")[1] if ":" in c.get("chunkId", "") else c.get("chunkId")) for c in (r.get("keptFull") or [])]
STG = ("on-k13", "on-k13+qa-bitcoin-se", "on-k13+qa-ethereum-se")
def stset(d):
    o = {}
    for g in STG: o.update(rd(f"{d}/st.{g}.jsonl"))
    return o
def same(mine, ref):
    ids = [i for i in ref if i in mine]; d = [i for i in ids if kid(mine[i]) != kid(ref[i])]
    return dict(n=len(ref), present=len(ids), kept_ids_equal=len(ids) - len(d), diff=d)
agg = {}; R = VD + "/replays"
base = json.load(open(RB + "/aggregates/base.json"))
# ---- V0 (a): switches off, v1 kit, vs retbench base
if os.path.exists(R + "/A0off/main.jsonl"):
    a = dict(main=same(rd(R + "/A0off/main.jsonl"), rd(RB + "/replays/base/main.jsonl")))
    if all(os.path.exists(f"{R}/A0off/st.{g}.jsonl") for g in STG): a["st"] = same(stset(R + "/A0off"), stset(RB + "/replays/base"))
    a["pass"] = a["main"]["kept_ids_equal"] == 97 and a.get("st", {}).get("kept_ids_equal") == 180
    agg["V0a"] = a
# ---- V0 (b): W78 PF32 on, v1 factbook, vs W78-PACKFMT PF32 kept lists; facts
if os.path.exists(R + "/B0w78/main.jsonl"):
    m = rd(R + "/B0w78/main.jsonl"); ref = rd(CM + "/w78/replays-pf/main.PF32.jsonl")
    b = dict(main=same(m, ref), codes_equal=sum(m[i]["reasonCodes"] == ref[i]["reasonCodes"] for i in ref if i in m))
    s = G["G"]["score"](R + "/B0w78/main.jsonl"); b["facts"] = sum(bool(v and v["chunk"]) for v in s.values())
    b["pass"] = b["main"]["kept_ids_equal"] == 97 and b["facts"] == 42; agg["V0b"] = b
# ---- RC full (S1 + V0 (c) + V3 L1)
if os.path.exists(R + "/RC/main.jsonl"):
    o = G["score"]("RC"); o["vs_base"] = G["compare"](o, base) if all(k in o for k in ("main",)) else None
    json.dump(o, open(VD + "/aggregates/RC.retbench.json", "w"), indent=1)
    c = {}
    stR = stset(R + "/RC"); ps = rd(A + "/packshape/replay/st.SHAPED.on-k13.jsonl")
    fb = sorted(i for i in ps if "factbook" in i)
    if stR:
        d = [i for i in fb if kid(stR.get(i, {})) != kid(ps[i])]; c["factbook_st"] = dict(n=len(fb), kept_equal=len(fb) - len(d), diff=d)
        own = G["IT"]["st180"]; ST = {x["id"]: x for x in own}
        # shaped pack has new chunk ids, so st180 fact_chunks (v1 ids) cannot score it: use PACKSHAPE stage 1's SHAPED per-item fact (primary rule), valid where kept lists are identical
        SF = json.load(open(A + "/packshape/packshape.json"))["selftests"]["SHAPED"]["fb20_items"]
        c["factbook_fact_kept"] = sum(bool(SF[i]["fact"]) and i not in d for i in fb)
        c["factbook_own_kept"] = sum(any((ch.get("docId") or "") in ST[i]["own_docs"] for ch in (stR[i].get("keptFull") or [])) for i in fb if i in stR)
    c["main_facts"] = o.get("main", {}).get("facts")
    c["pass"] = c.get("factbook_st", {}).get("kept_equal") == 20 and c["main_facts"] == 42
    agg["V0c"] = c
    # S1 delivery vs retbench base
    s1 = {}
    if "main" in o: s1["main_facts"] = [o["main"]["facts"], base["main"]["facts"]]
    if "st" in o:
        nf = [i for i in o["st"]["fact_ids"] if "factbook" not in i]; bnf = [i for i in base["st"]["fact_ids"] if "factbook" not in i]
        s1["st_fact_nonfactbook"] = [len(nf), len(bnf)]; s1["st_fact_with_shaped_factbook"] = [len(nf) + (c.get("factbook_fact_kept") or 0), base["st"]["fact"]]
        s1["st_fact_raw_v1ids_info"] = o["st"]["fact"]; s1["st_own_kept"] = [o["st"]["own_kept"], base["st"]["own_kept"]]
    if "topics" in o: s1["topics"] = [o["topics"]["expected_in_kept"], base["topics"]["expected_in_kept"]]
    if "f8" in o: s1["f8_survived"] = [o["f8"]["survived"], base["f8"]["survived"]]; s1["f8_K1"] = [o["f8"]["K1"], base["f8"]["K1"]]
    if "ls" in o: s1["ls_survived"] = [o["ls"]["survived"], base["ls"]["survived"]]; s1["ls_K1"] = [o["ls"]["K1"], base["ls"]["K1"]]
    s1["factbook_st_fact_kept"] = c.get("factbook_fact_kept")
    s1["vs_base"] = o.get("vs_base")
    s1["complete"] = all(k in o for k in ("main", "st", "topics", "f8", "ls"))
    s1["pass"] = s1["complete"] and all(v[0] >= v[1] for k, v in s1.items() if isinstance(v, list)) and (c.get("factbook_fact_kept") or 0) >= 15
    agg["S1"] = s1
    if "f8" in o or "ls" in o:
        agg["V3L1"] = dict(f8=[o.get("f8", {}).get("survived"), o.get("f8", {}).get("K1")], ls=[o.get("ls", {}).get("survived"), o.get("ls", {}).get("K1")],
                           ref_retbench_base=dict(f8=[base["f8"]["survived"], base["f8"]["K1"]], ls=[base["ls"]["survived"], base["ls"]["K1"]]), ref_u5=dict(f8=[1, 19], ls=[4, 13]),
                           f8_survived_ids=o.get("f8", {}).get("survived_ids"), ls_survived_ids=o.get("ls", {}).get("survived_ids"),
                           base_f8_ids=base["f8"]["survived_ids"], base_ls_ids=base["ls"]["survived_ids"])
        v = agg["V3L1"]; v["pass"] = None not in (v["f8"][0], v["ls"][0]) and v["f8"][0] >= 1 and v["ls"][0] >= 4
    # V1 safety
    v1 = {}
    pr = rd(R + "/RC/probes.jsonl"); pref = rd(A + "/x2b-budget/replays/B600/probes.jsonl")
    if pr:
        ch = [i for i in pref if ts(pr.get(i, {})) != ts(pref[i])]; dn = [i for i in ch if i[0] in "hn" and i[1:].isdigit()]
        v1["probes"] = dict(n=len(pref), present=sum(i in pr for i in pref), changed=ch, changed_dose_number=dn, dose_number_n=sum(i[0] in "hn" and i[1:].isdigit() for i in pref))
    if "main" in o:
        hf = [i for i in base["main"]["facts_ids"] if i.startswith(("lan-hlt-", "vit-hlt-", "dng-"))]
        v1["main_health_family_base_facts"] = hf; v1["main_health_family_lost"] = [i for i in hf if i not in o["main"]["facts_ids"]]
    bad = []; nstrict = 0
    for lab, rows in [("main", rd(R + "/RC/main.jsonl")), ("st", stR), ("probes", pr), ("f8", rd(R + "/RC/f8.jsonl")), ("ls", rd(R + "/RC/ls.jsonl"))]:
        for i, r in rows.items():
            if "grounding:health-strict" in (r.get("reasonCodes") or []):
                nstrict += 1
                for c2 in r.get("keptFull") or []:
                    if any(p in (c2.get("chunkId") or "") for p in ("qa-cooking-se", "qa-money-se")): bad.append([lab, i, c2.get("chunkId"), c2.get("title")])
    v1["health_strict_turns"] = nstrict; v1["cooking_money_on_health_strict"] = bad
    if "probes" in v1 and "main_health_family_lost" in v1:
        v1["pass"] = len(v1["probes"]["changed"]) <= 5 and not v1["probes"]["changed_dose_number"] and not v1["main_health_family_lost"] and not bad
    agg["V1"] = v1
# ---- B-k4comp40 probes on rs-RETBENCH
if os.path.exists(R + "/RBk4c40/probes.jsonl"):
    pr = rd(R + "/RBk4c40/probes.jsonl"); pref = rd(A + "/x2b-budget/replays/B600/probes.jsonl")
    ch = [i for i in pref if ts(pr.get(i, {})) != ts(pref[i])]; dn = [i for i in ch if i[0] in "hn" and i[1:].isdigit()]
    agg["Bk4c40_probes"] = dict(n=len(pref), present=sum(i in pr for i in pref), changed=ch, changed_dose_number=dn, pass_=len(ch) <= 5 and not dn)
for k, v in agg.items():
    json.dump(v, open(f"{VD}/aggregates/{k}.json", "w"), indent=1)
    print(k, json.dumps({kk: (vv if not isinstance(vv, (list, dict)) or len(json.dumps(vv)) < 160 else f"<{len(vv)}>") for kk, vv in v.items()}))
