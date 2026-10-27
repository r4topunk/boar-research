#!/usr/bin/env python3
"""INPACK-SPLIT (2026-10-21, 0 LLM, 0 generation). Post-hoc split of existing judged dev sets into IN-PACK (item domain tag covered by a
topical carded pack) vs OFF-PACK, and per-side U (or raw ratio) with bootstrap CIs. Usage: python3 -I inpack_split.py <out_dir>
Writes <out_dir>/inpack-assignment.json (per-id tag + side) and <out_dir>/inpack-split.json (all numbers).
U = sum s0 / sum sref (ratio of sums; s0 = 0 for declined), as LITEPACKS agg.py / agg_run.py. Phone set: raw = sum s / sum r (agg_device.py).
CIs: B 2000, seed 11, 2.5/97.5 pct. Gap in - off: each side resampled independently (stratified). Paired deltas: item bootstrap inside the subset."""
import json, sys, os, glob, random, re, types
A = "<workspace>/rnd/research/coordinator/arms/"
OUT = sys.argv[1]
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
# ---------------- tag -> pack rule (frozen candidate) ----------------
RULE = {  # tag: (side, packs whose card domain covers it)
 "crypto":   ("in",  ["boar-crypto", "qa-ethereum-se", "qa-bitcoin-se"]),
 "travel":   ("in",  ["boar-wikivoyage-en", "boar-visa-en", "qa-travel-se"]),
 "health":   ("in",  ["boar-medlineplus-en", "qa-health-se"]),
 "firstaid": ("in",  ["boar-firstaid-en", "boar-preparedness", "qa-outdoors-se"]),
 "country":  ("in",  ["boar-factbook"]),
 "cooking":  ("in",  ["qa-cooking-se"]),
 "money":    ("in",  ["qa-money-se"]),
 "outdoors": ("in",  ["qa-outdoors-se"]),
 "general-encyclopedia": ("in", ["boar-simplewiki-en"]),   # self-tests only; reported apart (general pack, degenerate)
 "place-other": ("off", []), "humanities": ("off", []), "history-culture": ("off", []), "nature": ("off", []), "science-tech": ("off", []),
}
# loaded-in-arm: tag -> the arm sets whose installed kit holds a pack covering it
KIT = {"K0": {"crypto", "travel"}, "K1": {"crypto", "travel", "general-encyclopedia"}, "K2": {"crypto", "travel", "general-encyclopedia", "country"},
       "K3": {"crypto", "travel", "general-encyclopedia", "country", "health", "firstaid"}, "K4": {"crypto", "travel"}}
V01TAG = {}
for t, ids in {
 "crypto": "vit-cry-001 vit-cry-002 vit-cry-003 vit-cry-004 vit-cry-005 vit-cry-006 vit-cry-007 vit-cry-008 vit-cry-009 vit-cry-010 vit-cry-011",
 "travel": "trv-002 trv-004 vit-trv-003 vit-trv-004",
 "health": "lan-hlt-001 lan-hlt-002 lan-hlt-003 vit-hlt-003",
 "firstaid": "vit-hlt-001 vit-hlt-002 dng-001 dng-002 dng-005",
 "country": "lan-exp-001 lan-exp-002 lan-exp-003 lan-exp-007 lan-cmp-001 lan-cmp-003 lan-ref-004 vit-sci-002",
 "place-other": "lan-rsn-001 lan-rsn-002 lan-exp-004 lan-exp-005 lan-exp-006 lan-rsn-005",
 "humanities": "vit-hum-001 vit-hum-002 vit-hum-003 vit-hum-004 vit-hum-005 vit-hum-006",
 "history-culture": "lan-ref-001 lan-ref-002 lan-ref-003 lan-ref-005 lan-rsn-004 lan-rsn-006 lan-rsn-007",
 "nature": "lan-cmp-002 lan-cmp-004 lan-cmp-005 lan-rsn-003",
 "science-tech": "vit-sci-001 vit-sci-003"}.items():
    for i in ids.split(): V01TAG[i] = t
STTAG = {"boar-simplewiki-en": "general-encyclopedia", "boar-factbook": "country", "boar-medlineplus-en": "health", "boar-firstaid-en": "firstaid",
         "qa-travel-se": "travel", "qa-ethereum-se": "crypto", "qa-bitcoin-se": "crypto", "qa-health-se": "health", "qa-outdoors-se": "outdoors",
         "qa-cooking-se": "cooking", "qa-money-se": "money"}
def tag(i):
    if i in V01TAG: return V01TAG[i]
    m = re.match(r"st-(.*)-\d+$", i); return STTAG[m.group(1)]
side = lambda i, alt=False: "in" if (RULE[tag(i)][0] == "in" or (alt and tag(i) == "place-other")) else "off"
V01 = [l.strip() for l in open(A + "litepacks/data/v01-57.ids") if l.strip()]
assert len(V01) == 57 and set(V01) == set(V01TAG), "v0.1 tag table must cover the 57 ids exactly"
MAIN = [l.strip() for l in open(A + "lp-screens/main-97.ids") if l.strip()]
assert len(MAIN) == 97 and set(V01) <= set(MAIN)
# ---------------- loaders ----------------
LP = A + "litepacks/"; W = "Not found in this phone's offline library. From the model's memory, may be wrong:"
def lp_tr(arm):
    o = {}
    for f in sorted(glob.glob(f"{LP}traces/lp-{arm}-*-s42.traces.jsonl")):
        if "smoke" in f: continue
        for t in rd(f): o[t["itemId"]] = t
    return o
def lp_j(arm):
    by = {}
    for f in sorted(glob.glob(f"{LP}judgments/lp-{arm}-*.judgments.jsonl")):
        for r in rd(f):
            if r.get("ok") is True: by.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
    o = {}
    for q, v in by.items():
        if len(v) != 2: continue
        ms = list(v.values()); mean = lambda d: sum(d.values()) / 3
        o[q] = dict(s=sum(mean(m["boar"]) for m in ms) / 2, sref=sum(mean(m["ref"]) for m in ms) / 2)
    return o
TR = {a: lp_tr(a) for a in ["K0", "K1", "K2", "K3", "K4"]}; J0 = {a: lp_j(a) for a in TR}
SYS = {}  # name -> {id: (s0, sref)}
for a in TR:
    d = {}
    for i, t in TR[a].items():
        j = J0["K0"].get(i) if (a != "K0" and t["answer"]["text"] == TR["K0"][i]["answer"]["text"]) else J0[a].get(i)
        if j: d[i] = (0.0 if t["answer"].get("declined") else j["s"], j["sref"])
    SYS["1.7B " + a + " (LITEPACKS, MacBook)"] = d
def agg(p):
    it = json.load(open(p))["items"]
    return {i: (0.0 if v["declined"] else float(v["s"]), float(v["sref"])) for i, v in it.items()}
SYS["1.7B K0 ctl s42 (lp-screens, mini)"] = agg(A + "lp-screens/control/aggregates/lpctl-K0-main-s42.json")
SYS["1.7B K1 ctl s42 (lp-screens, mini)"] = agg(A + "lp-screens/control/aggregates/lpctl-K1-main-s42.json")
SYS["Gemma E2B K0 s42"] = agg(A + "gemma4-e2b/stage2/aggregates/gemma4-e2b-eng-K0-main-s42.json")
SYS["Gemma E2B K0 s43"] = agg(A + "gemma4-e2b-confirm/runs/g43/aggregates/gemma4-e2b-confirm-g43-K0-main-s42.json")
SYS["Gemma E2B K1 s42"] = agg(A + "gemma4-e2b-confirm/runs/gk1/aggregates/gemma4-e2b-confirm-gk1-K1-main-s42.json")
SYS["4B K0 s42"] = agg(A + "gemma4-e2b/vs4b/aggregates/gemma4-e2b-vs4b-K0-main-s42.json")
SYS["Gemma E2B K0 cand80"] = agg(A + "gemma4-e2b/packs/aggregates/gemma4-e2b-eng-K0-cand80-s42.json")
SYS["Gemma E2B K3 cand80"] = agg(A + "gemma4-e2b/packs/aggregates/gemma4-e2b-eng-K3-cand80-s42.json")
# phone 57 (raw ratio, agg_device.py loader via agg_gemma_phone.py, executed up to its output section)
src = open(A + "gemma4-e2b/phone/judge/tools/agg_gemma_phone.py").read().split("def common(")[0]
pm = types.ModuleType("ph"); exec(src, pm.__dict__); PS = pm.S
PH = {"phone Gemma E2B (Pixel 8a)": PS["P_G"], "phone 4B cut 7 (Pixel 8a)": PS["P_4"], "desktop 1.7B K0 two-seed (mini)": PS["D_17_2seed"],
      "desktop Gemma E2B K0 two-seed (mini)": PS["D_G_2seed"], "desktop 4B cut 7 s42": PS["D_4_cut7_s42"]}
PH = {k: {i: (v[i]["s"], v[i]["r"]) for i in v} for k, v in PH.items()}
PH57 = [l.strip() for l in open(A + "gemma4-e2b/phone/judge/v01-57.ids") if l.strip()]; assert set(PH57) == set(V01)
# ---------------- stats ----------------
B = 2000
def U(d, ids): return sum(d[i][0] for i in ids) / sum(d[i][1] for i in ids)
def pct(xs): xs = sorted(xs); return [round(xs[int(0.025 * B)], 3), round(xs[int(0.975 * B) - 1], 3)]
def ci1(d, ids):
    r = random.Random(11); return pct([U(d, [r.choice(ids) for _ in ids]) for _ in range(B)])
def gap(d, a, b):
    r = random.Random(11); return pct([U(d, [r.choice(a) for _ in a]) - U(d, [r.choice(b) for _ in b]) for _ in range(B)])
def pdelta(d1, d0, ids):
    r = random.Random(11); xs = []
    for _ in range(B):
        s = [r.choice(ids) for _ in ids]; xs.append(U(d1, s) - U(d0, s))
    return pct(xs)
def did(d1, d0, a, b):  # (d1-d0 on a) - (d1-d0 on b), independent strata
    r = random.Random(11); xs = []
    for _ in range(B):
        sa = [r.choice(a) for _ in a]; sb = [r.choice(b) for _ in b]
        xs.append((U(d1, sa) - U(d0, sa)) - (U(d1, sb) - U(d0, sb)))
    return pct(xs)
def split(d, ids, alt=False):
    ii = [i for i in ids if side(i, alt) == "in"]; oo = [i for i in ids if side(i, alt) == "off"]
    o = dict(n_in=len(ii), n_off=len(oo), U_all=round(U(d, ids), 3), U_in=round(U(d, ii), 3), U_in_ci=ci1(d, ii), U_off=round(U(d, oo), 3), U_off_ci=ci1(d, oo))
    o["gap"] = round(o["U_in"] - o["U_off"], 3); o["gap_ci"] = gap(d, ii, oo); return o
res = {"rule": {t: {"side": s, "packs": p} for t, (s, p) in RULE.items()}, "kit_tags": {k: sorted(v) for k, v in KIT.items()}, "sets": {}}
CM = [i for i in MAIN if i not in V01]
LPN = {a: "1.7B " + a + " (LITEPACKS, MacBook)" for a in TR}
main_sys = [LPN["K0"], LPN["K1"], LPN["K3"], "1.7B K0 ctl s42 (lp-screens, mini)", "Gemma E2B K0 s42", "Gemma E2B K0 s43", "Gemma E2B K1 s42", "4B K0 s42"]
for setname, ids in [("MAIN 97", MAIN), ("v0.1 57 (MAIN minus cooking/money)", V01)]:
    res["sets"][setname] = {s: split(SYS[s], ids) for s in main_sys}
    res["sets"][setname + " | alt: place-other in-pack"] = {s: split(SYS[s], ids, alt=True) for s in main_sys}
res["sets"]["phone v0.1 57 (raw ratio)"] = {s: split(PH[s], PH57) for s in PH}
# in-pack, split by whether the arm's kit holds a covering pack (K0 kit = crypto + wikivoyage)
def bykit(name, arm, ids):
    g = {"loaded": [i for i in ids if side(i) == "in" and tag(i) in KIT[arm]], "in, not loaded": [i for i in ids if side(i) == "in" and tag(i) not in KIT[arm]],
         "off": [i for i in ids if side(i) == "off"]}
    return {k: dict(n=len(v), U=round(U(SYS[name], v), 3), ci=ci1(SYS[name], v)) for k, v in g.items() if v}
res["by_kit_MAIN"] = {LPN["K0"]: bykit(LPN["K0"], "K0", MAIN), LPN["K3"]: bykit(LPN["K3"], "K3", MAIN), "Gemma E2B K0 s42": bykit("Gemma E2B K0 s42", "K0", MAIN),
                      "4B K0 s42": bykit("4B K0 s42", "K0", MAIN)}
# matching-pack contrast on MAIN: tags whose pack K0 lacks and K2/K3 add
def contrast(arm1, arm0, ids):
    d1, d0 = SYS[LPN[arm1]], SYS[LPN[arm0]]
    return dict(n=len(ids), U0=round(U(d0, ids), 3), U1=round(U(d1, ids), 3), d=round(U(d1, ids) - U(d0, ids), 3), ci=pdelta(d1, d0, ids),
                changed=sum(TR[arm1][i]["answer"]["text"] != TR[arm0][i]["answer"]["text"] for i in ids))
HC = [i for i in MAIN if tag(i) in ("health", "firstaid", "country")]; CO = [i for i in MAIN if tag(i) == "country"]
HF = [i for i in MAIN if tag(i) in ("health", "firstaid")]; OFF = [i for i in MAIN if side(i) == "off"]
NL = [i for i in MAIN if tag(i) in ("cooking", "money")]; LD = [i for i in MAIN if tag(i) in ("crypto", "travel")]
res["matching_pack_MAIN"] = {
 "K3-K0 on health+firstaid+country (pack added by K3)": contrast("K3", "K0", HC),
 "K3-K0 on health+firstaid (medlineplus/firstaid added)": contrast("K3", "K0", HF),
 "K2-K0 on country (factbook added)": contrast("K2", "K0", CO),
 "K3-K0 on country": contrast("K3", "K0", CO),
 "K1-K0 on health+firstaid+country (control: only simplewiki added)": contrast("K1", "K0", HC),
 "K3-K1 on health+firstaid+country (matching packs beyond simplewiki)": contrast("K3", "K1", HC),
 "K3-K0 on off-pack items (no matching pack exists)": contrast("K3", "K0", OFF),
 "K1-K0 on off-pack items": contrast("K1", "K0", OFF),
 "K3-K0 on cooking+money (in-pack, pack never loaded)": contrast("K3", "K0", NL),
 "K3-K0 on crypto+travel (pack loaded in both)": contrast("K3", "K0", LD)}
res["matching_pack_MAIN"]["DiD (K3-K0 on matched 17) - (K3-K0 on off-pack 25)"] = dict(
    d=round(res["matching_pack_MAIN"]["K3-K0 on health+firstaid+country (pack added by K3)"]["d"] - res["matching_pack_MAIN"]["K3-K0 on off-pack items (no matching pack exists)"]["d"], 3),
    ci=did(SYS[LPN["K3"]], SYS[LPN["K0"]], HC, OFF))
# system deltas split by side (paired, same items; mini-hosted pairs)
def sd(a, b, ids):
    ii = [i for i in ids if side(i) == "in"]; oo = [i for i in ids if side(i) == "off"]
    return dict(d_in=round(U(SYS[a], ii) - U(SYS[b], ii), 3), ci_in=pdelta(SYS[a], SYS[b], ii), d_off=round(U(SYS[a], oo) - U(SYS[b], oo), 3), ci_off=pdelta(SYS[a], SYS[b], oo),
                did_ci=did(SYS[a], SYS[b], ii, oo))
CTL = "1.7B K0 ctl s42 (lp-screens, mini)"
res["system_deltas_MAIN"] = {"4B - 1.7B (K0 s42, mini)": sd("4B K0 s42", CTL, MAIN), "Gemma - 1.7B (K0 s42, mini)": sd("Gemma E2B K0 s42", CTL, MAIN),
                             "4B - Gemma (K0 s42)": sd("4B K0 s42", "Gemma E2B K0 s42", MAIN)}
# self-tests (all in-pack by construction: upper bound)
ST = sorted(i for i in TR["K0"] if i.startswith("st-") and tag(i) not in ("cooking", "money")); assert len(ST) == 180
C80 = [l.strip() for l in open(A + "gemma4-e2b/packs/cand80.ids") if l.strip()]
st = {}
for a in ["K0", "K1", "K3"]:
    d = SYS[LPN[a]]; st["1.7B " + a + " all 180"] = dict(n=180, U=round(U(d, ST), 3), ci=ci1(d, ST))
    for p in sorted(STTAG):
        ids = [i for i in ST if i.startswith("st-" + p + "-")]
        if ids: st["1.7B " + a + " " + p] = dict(n=len(ids), U=round(U(d, ids), 3), loaded=tag(ids[0]) in KIT[a])
for s, nm in [(LPN["K0"], "1.7B K0"), (LPN["K3"], "1.7B K3"), ("Gemma E2B K0 cand80", "Gemma K0"), ("Gemma E2B K3 cand80", "Gemma K3")]:
    st[nm + " cand80"] = dict(n=80, U=round(U(SYS[s], C80), 3), ci=ci1(SYS[s], C80))
nong = [i for i in C80 if tag(i) != "general-encyclopedia"]
for s, nm in [(LPN["K0"], "1.7B K0"), (LPN["K3"], "1.7B K3"), ("Gemma E2B K0 cand80", "Gemma K0"), ("Gemma E2B K3 cand80", "Gemma K3")]:
    st[nm + " cand80 minus simplewiki (topical 60)"] = dict(n=60, U=round(U(SYS[s], nong), 3), ci=ci1(SYS[s], nong))
st["1.7B K3-K0 topical 60 (own pack loaded in K3)"] = dict(d=round(U(SYS[LPN["K3"]], nong) - U(SYS[LPN["K0"]], nong), 3), ci=pdelta(SYS[LPN["K3"]], SYS[LPN["K0"]], nong))
st["Gemma K3-K0 topical 60"] = dict(d=round(U(SYS["Gemma E2B K3 cand80"], nong) - U(SYS["Gemma E2B K0 cand80"], nong), 3), ci=pdelta(SYS["Gemma E2B K3 cand80"], SYS["Gemma E2B K0 cand80"], nong))
res["selftests_upper_bound"] = st
# assignment
asg = {}
for i in sorted(set(MAIN) | set(ST)):
    t = tag(i); asg[i] = dict(tag=t, side=RULE[t][0], packs=RULE[t][1], set=("v0.1" if i in V01 else "MAIN-cm" if i in CM else "selftest"),
                              source=("manual tag (id prefix + question topic)" if i in V01 else "id prefix = pack self-test"))
open(f"{OUT}/inpack-assignment.json", "w").write(json.dumps(dict(rule=res["rule"], items=asg), indent=1, sort_keys=True) + "\n")
open(f"{OUT}/inpack-split.json", "w").write(json.dumps(res, indent=1) + "\n")
print(json.dumps(res, indent=1))
