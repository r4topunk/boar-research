#!/usr/bin/env python3
"""DEFAULT-SET (H-A1) analysis, 0 LLM. usage: default_set.py <replay dir with O1..O5.jsonl + sets.json> <out json>
Path P = phone engine replay (bench-app/engine 0ca54d87); path D = PK4-PACK-PRUNE desktop KA items (reused)."""
import json, os, sys, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import packmap
C = "<workspace>/rnd/research/coordinator"
RD, OUT = sys.argv[1], sys.argv[2]
sys.path.insert(0, C + "/arms/e1-partime"); from partime_analyze import pct
PK = ["boar-crypto", "boar-wikivoyage-en", "boar-visa-en", "boar-medlineplus-en", "boar-firstaid-en", "boar-factbook"]
OPTS = {"O1": [], "O2": ["boar-visa-en"], "O3": ["boar-medlineplus-en"], "O4": ["boar-visa-en", "boar-medlineplus-en"],
        "O5": ["boar-visa-en", "boar-medlineplus-en", "boar-firstaid-en", "boar-factbook"]}
def pack_of(title, source):
    s = source or ""
    if title.startswith("Wikivoyage: ") or "wikivoyage.org" in s: return "boar-wikivoyage-en"
    if "medlineplus.gov" in s: return "boar-medlineplus-en"
    if "factbook" in s: return "boar-factbook"
    ps = [p for p in packmap.packs_of(title) if p not in ("boar-wikivoyage-en", "boar-medlineplus-en", "boar-factbook")]
    if len(ps) == 1: return ps[0]
    if "boar-firstaid-en" in ps: return "boar-firstaid-en"
    return ps[0] if ps else "other"
def load(o):
    r = {}
    for l in open(os.path.join(RD, o + ".jsonl")):
        d = json.loads(l); src = {x["title"]: x.get("source") for x in d["raw"]}
        r[d["id"]] = {"kept": d["sources"], "kept_packs": [pack_of(t, src.get(t)) for t in d["sources"]],
                      "raw_packs": [pack_of(x["title"], x.get("source")) for x in d["raw"]]}
    return r
sets = json.load(open(os.path.join(RD, "sets.json")))
main = sets["main"]; v01 = [i for i in main if not i.startswith("st-")]; cm = [i for i in main if i.startswith("st-")]
p73 = [i for i in sets["p73"] if i != "warmup-000"]; extra73 = [i for i in p73 if i not in main]
saf = [i for i in p73 if i.startswith("saf-")]
R = {o: load(o) for o in OPTS}
probes = [i for i in R["O1"] if i.startswith("probe:")]
scope = sorted(set(main) | set(p73))
SETS = {"MAIN97": main, "v01_57": v01, "cm40": cm, "p73_extra": extra73, "saf12": saf, "probes64": probes}
res = {"n": {k: len(v) for k, v in SETS.items()}, "scope_n": len(scope)}
# per-pack kept items on path P (O1)
pp = {}
for p in PK:
    pp[p] = {k: sum(1 for i in v if p in R["O1"][i]["kept_packs"]) for k, v in SETS.items()}
    pp[p]["scope"] = sum(1 for i in scope if p in R["O1"][i]["kept_packs"])
    pp[p]["raw_scope"] = sum(1 for i in scope if p in R["O1"][i]["raw_packs"])
    pp[p]["kept_ids"] = [i for i in scope if p in R["O1"][i]["kept_packs"]]
res["P_per_pack"] = pp
# option deltas on path P
gl = {}
for l in open(C + "/arms/oracle-real/gold-labels.tsv"):
    if l.startswith(("#", "item")): continue
    f = l.rstrip("\n").split("\t")
    if len(f) >= 3 and f[2] in ("Y", "P"): gl[f[0]] = f[1]
rf = json.load(open(C + "/ruler/RAG-FUNNEL-2026-10-21.json"))["items"]
gold_title = {i: (rf.get(i, {}).get("gold") or {}).get("title") for i in gl}
# manual golds (no RAG-FUNNEL title): titles from the ORACLE-REAL table text
res["gold_items"] = {i: [gl[i], gold_title[i]] for i in gl}
def gold_hit(o, i):
    t = gold_title.get(i)
    return bool(t) and any(t.lower() == k.lower() or k.lower().endswith(": " + t.lower()) for k in R[o].get(i, {"kept": []})["kept"])
opt = {}
for o, gone in OPTS.items():
    ch = {k: [i for i in v if R[o][i]["kept"] != R["O1"][i]["kept"]] for k, v in SETS.items()}
    lost_gold_P = [i for i in gl if gold_hit("O1", i) and not gold_hit(o, i)]
    opt[o] = {"dropped": gone, "P_changed": {k: len(v) for k, v in ch.items()}, "P_changed_ids_safety": ch["saf12"] + ch["probes64"],
              "P_changed_scope": len([i for i in scope if R[o][i]["kept"] != R["O1"][i]["kept"]]),
              "P_gold_kept_O1_lost": lost_gold_P,
              "P_items_retrieving": sum(1 for i in scope if R[o][i]["kept"])}
res["P_gold_kept_O1"] = [i for i in gl if gold_hit("O1", i)]
# path D (PK4 desktop KA)
pk4 = json.load(open(C + "/ruler/PK4-PACK-PRUNE-2026-10-21.json"))
it = pk4["items"]
dsets = {"v01_57": [i for i, v in it.items() if v["set"] == "v0.1"], "cm40": [i for i, v in it.items() if v["set"] == "MAIN-cm"],
         "PM180": [i for i, v in it.items() if v["set"] == "selftest"]}
dp = {}
for p in PK:
    dp[p] = {k: sum(1 for i in v if it[i]["kept"].get(p)) for k, v in dsets.items()}
    dp[p]["fact_real"] = [i for i in dsets["v01_57"] + dsets["cm40"] if p in it[i]["fact_kept"]]
    dp[p]["fact_PM180"] = sum(1 for i in dsets["PM180"] if p in it[i]["fact_kept"])
    dp[p]["kept_ids_main"] = [i for i in dsets["v01_57"] + dsets["cm40"] if it[i]["kept"].get(p)]
res["D_per_pack"] = dp
for o, gone in OPTS.items():
    opt[o]["D_items_with_dropped_kept"] = {k: sum(1 for i in v if any(it[i]["kept"].get(p) for p in gone)) for k, v in dsets.items()}
    opt[o]["D_fact_real_lost"] = sorted({i for p in gone for i in dp[p]["fact_real"]})
    opt[o]["D_fact_PM180_lost"] = sum(dp[p]["fact_PM180"] for p in gone)
res["D_measured_context_change_pk4"] = pk4["variants"]
# time (PARTIME drop logic on the Pixel aunion73-a per-pack windows)
qs = json.load(open(C + "/arms/e1-partime/aggregates/perq-aunion73-a.json"))
def nt(q, gone, mode):
    if not q.get("packs"): return q["total_ms"]
    ps = {k: v for k, v in q["packs"].items() if k not in gone}
    ws = [p["window_ms"] for p in ps.values()]; js = sum(p["js_ms"] for p in ps.values())
    new = sum(ws) if mode == "serial" else max(js, max(ws)) if mode == "par_js_lb" else max(ws)
    return q["total_ms"] - (q["search_ms"] - new)
for o, gone in OPTS.items():
    for m in ["serial", "par_js_lb", "par_ideal"]:
        opt[o]["T_p50_" + m] = round(pct([nt(q, gone, m) for q in qs], .5) / 1000, 2)
        opt[o]["T_p90_" + m] = round(pct([nt(q, gone, m) for q in qs], .9) / 1000, 2)
opt["O5"]["T_p50_measured_q17b73a"] = 4.16
res["options"] = opt
# phone traces: pack hits on aunion73-a (AUNION-PIXEL), quoted
res["phone_hits_aunion73a"] = pk4["phone_pack_hits_questions_aunion73"]
PERS = {"boar-visa-en": "travel (logistics subject: its only pack)", "boar-medlineplus-en": "science (everyday-health subject: its primary pack; firstaid stays)",
        "boar-firstaid-en": "science (first aid)", "boar-factbook": "place (its only pack)"}
for o, gone in OPTS.items(): opt[o]["persona_lost"] = [PERS[p] for p in gone]
# kill clause per pack (criterion): (a) kept >= 4 items, (b) fact >= 2, (c) safety change on path P
kill = {}
for p, o in [("boar-visa-en", "O2"), ("boar-medlineplus-en", "O3")]:
    a_P = pp[p]["scope"]; a_D = len(dp[p]["kept_ids_main"])
    b_P = sum(1 for i in res["P_gold_kept_O1"] if i in opt[o]["P_gold_kept_O1_lost"]); b_D = len(dp[p]["fact_real"])
    c = len(opt[o]["P_changed_ids_safety"])
    kill[p] = {"a_kept_P": a_P, "a_kept_D": a_D, "b_fact_P": b_P, "b_fact_D": b_D, "c_safety_changed_P": c,
               "keep": a_P >= 4 or a_D >= 4 or b_P >= 2 or b_D >= 2 or c >= 1}
res["kill"] = kill
json.dump(res, open(OUT, "w"), indent=1)
for o in OPTS: print(o, {k: v for k, v in opt[o].items() if k not in ("P_changed_ids_safety",)})
print(json.dumps(kill)); print({p: {k: v for k, v in pp[p].items() if k != "kept_ids"} for p in PK})
print({p: {k: v for k, v in dp[p].items() if k not in ("kept_ids_main",)} for p in PK})
