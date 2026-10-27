#!/usr/bin/env python3
"""DIVERGENCE-MAP (2026-10-21; 0 LLM, 0 generation, 0 paid). Usage, from ruler/: python3 -I tools/divergence_map.py .
Reads existing traces/aggregates/judgments only (dev ids: MAIN 97, the 180 self-tests, the v0.1 73 phone set; never blind/, rnd/veil, bench/v0.4).
Writes divergence-map.json, ids/*.ids (+ .sha256), savings in the json; prints a summary.

Per item and condition (one judged answer): u = s0 / sref, s = mean of the 3 judge dims over both orders, s0 = 0 if declined (engine flag),
sref = same for the reference. Labels from null-cal/tools/labels.py: decline never CE; CE = not decline and corr <= 1.5; warned = warning line;
R = decline or warned (refused in the default product).
DIVERGENCE SCORE  D = u_range + 0.25*[CE flips] + 0.25*[R flips] + 0.25*[judge flip]
  u_range = max u - min u over every judged condition of the item (pack sets, models, seeds, hosts, phone);
  CE / R flips = the label is not the same in every condition; judge flip = Haiku vs Opus CE label differs, or |corr_H - corr_O| >= 1.5,
  on any answer where both exist. D is NaN with < 2 judged conditions.
deterministic = the answer never reaches a model: phone (v0.1 73) = identical text and 0 generated tokens on the 1.7B, Gemma and 4B phone runs;
  desktop (MAIN/st180) = control trace generated 0 tokens on the K0 and K1 mini controls (pool 'live' False) and identical text across
  every desktop condition. reaches_model = not deterministic.
"""
import json, glob, os, sys, re, math, hashlib, collections, statistics
R0 = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
A = "<workspace>/rnd/research/coordinator/arms"; BOAR = "<workspace>"
sys.path.insert(0, f"{A}/null-cal/tools"); from labels import is_decline, W  # noqa: E402
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]

# ---------------- sets ----------------
V57 = open(f"{A}/litepacks/data/v01-57.ids").read().split()
MAIN = open(f"{A}/lp-screens/main-97.ids").read().split()
ST = open(f"{A}/null-cal/pool/st180.ids").read().split()
PH = {"q17b73": f"{A}/gemma4-e2b/phone/q17b73-a/rows.jsonl", "gemma73": f"{A}/gemma4-e2b/phone/gemma73-a/rows.jsonl",
      "4b-pixel": f"{BOAR}/handoff/pixel8-2026-10-20/bench/results/final-cut7-v01/rows.jsonl",
      "4b-poco": f"{BOAR}/boar-eval/runs/device-poco-x6pro/final-cut7-v01/rows.jsonl",
      "gemma10": f"{A}/gemma4-e2b/phone/gemma10-b/rows.jsonl", "q17b10": f"{A}/gemma4-e2b/phone/q17b10-a/rows.jsonl"}
PROWS = {k: {r["queryId"]: r for r in rd(f)} for k, f in PH.items()}
V73 = [i for i in PROWS["q17b73"]]  # warmup-000 + 72 v0.1 ids, request order
V72 = [i for i in V73 if i != "warmup-000"]
assert len(MAIN) == 97 and len(ST) == 180 and len(V73) == 73 and set(V57) <= set(MAIN) and set(V57) <= set(V72)
SETS = {"main": MAIN, "st180": ST, "v01": V72}

# ---------------- conditions: cond -> {id: rec} ----------------
C = {}
def lab(text, declined, corr, s, sref):
    d = is_decline(text, declined); w = text.startswith(W); ce = (not d) and corr <= 1.5
    return dict(u=(0.0 if declined else s) / sref if sref else None, corr=corr, CE=ce, R=d or w, warned=w, text=text)
def from_agg(name, f):
    it = json.load(open(f))["items"]; C[name] = {}
    for i, x in it.items():
        if x.get("errored") or x.get("s") is None or x.get("sref") is None: continue
        C[name][i] = lab(x["text"], x["declined"], x["corr"], x["s"], x["sref"])
def judg_pairs(files):
    by = {}
    for f in files:
        for r in rd(f):
            if r.get("ok") is True: by.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
    out = {}
    for q, v in by.items():
        if len(v) != 2: continue
        ms = list(v.values()); mean = lambda d: sum(d.values()) / 3
        out[q] = dict(s=sum(mean(m["boar"]) for m in ms) / 2, sref=sum(mean(m["ref"]) for m in ms) / 2, corr=sum(m["boar"]["correctness"] for m in ms) / 2)
    return out
# (a) LITEPACKS K0..K4 (MacBook, 1.7B, s42; K1-K4 reuse K0 judgments for byte-identical answers, as agg.py does)
LP = f"{A}/litepacks"; LTR, LJ = {}, {}
for k in ["K0", "K1", "K2", "K3", "K4"]:
    LTR[k] = {}
    for f in sorted(glob.glob(f"{LP}/traces/lp-{k}-*-s42.traces.jsonl")):
        if "smoke" in f: continue
        for t in rd(f): LTR[k][t["itemId"]] = t
    LJ[k] = judg_pairs(sorted(glob.glob(f"{LP}/judgments/lp-{k}-*.judgments.jsonl")))
for k in LTR:
    C[f"lp-{k}"] = {}
    for i, t in LTR[k].items():
        txt = t["answer"]["text"]; j = LJ["K0"].get(i) if (k != "K0" and txt == LTR["K0"].get(i, {}).get("answer", {}).get("text")) else LJ[k].get(i)
        if j: C[f"lp-{k}"][i] = lab(txt, bool(t["answer"].get("declined")), j["corr"], j["s"], j["sref"])
# (b) mini agg_run aggregates (controls, seeds, models, nulls)
AGG = {"ctl17-K0-s42": "lp-screens/control/aggregates/lpctl-K0-main-s42.json", "ctl17-K1-s42": "lp-screens/control/aggregates/lpctl-K1-main-s42.json",
       "ctl17-K0-st-s42": "null-cal/control/aggregates/poolctl-K0-st180-s42.json", "ctl17-K1-st-s42": "null-cal/control/aggregates/poolctl-K1-st180-s42.json",
       "q17-K0-s43": "gemma4-e2b-confirm/runs/c43/aggregates/gemma4-e2b-confirm-c43-K0-main-s42.json",
       "gemma-K0-s42": "gemma4-e2b/stage2/aggregates/gemma4-e2b-eng-K0-main-s42.json",
       "gemma-K0-s43": "gemma4-e2b-confirm/runs/g43/aggregates/gemma4-e2b-confirm-g43-K0-main-s42.json",
       "gemma-K1-s42": "gemma4-e2b-confirm/runs/gk1/aggregates/gemma4-e2b-confirm-gk1-K1-main-s42.json",
       "q4b-K0-s42": "gemma4-e2b/vs4b/aggregates/gemma4-e2b-vs4b-K0-main-s42.json",
       "gemma-K0-cand80": "gemma4-e2b/packs/aggregates/gemma4-e2b-eng-K0-cand80-s42.json",
       "gemma-K3-cand80": "gemma4-e2b/packs/aggregates/gemma4-e2b-eng-K3-cand80-s42.json",
       "nullws-K0": "null-cal/arms/null-ws/aggregates/null-ws-K0-screen2-K0-s42.json", "nulls43-K0": "null-cal/arms/null-s43/aggregates/null-s43-K0-screen2-K0-s42.json",
       "nullws-K1": "null-cal/arms/null-ws/aggregates/null-ws-K1-screen2-K1-s42.json", "nulls43-K1": "null-cal/arms/null-s43/aggregates/null-s43-K1-screen2-K1-s42.json"}
for n, f in AGG.items(): from_agg(n, f"{A}/{f}")
# (c) phone, judged (57 device-parity v0.1 ids)
PJ = {"ph-gemma": f"{BOAR}/boar-eval/runs/device-pixel8a/gemma73-a", "ph-4b-pixel": f"{BOAR}/boar-eval/runs/device-pixel8a/final-cut7-v01",
      "ph-4b-poco": f"{BOAR}/boar-eval/runs/device-poco-x6pro/final-cut7-v01"}
PRK = {"ph-gemma": "gemma73", "ph-4b-pixel": "4b-pixel", "ph-4b-poco": "4b-poco"}
for n, d in PJ.items():
    j = judg_pairs([f"{d}/judgments.haiku.jsonl"]); C[n] = {}
    for i, x in j.items():
        r = PROWS[PRK[n]][i]; C[n][i] = lab(r["answer"], bool(r.get("declined")), x["corr"], x["s"], x["sref"])
GROUP = {n: ("pack" if n.startswith("lp-") else "phone" if n.startswith("ph-") else "null" if n.startswith("null") else "model/seed") for n in C}

# ---------------- judges: Haiku vs Opus on the same answer text ----------------
JD = collections.defaultdict(list)  # id -> [(haiku_corr, opus_corr, haiku_CE, opus_CE, src)]
CO = f"{A}/ce-opus-check"
ctl = json.load(open(f"{A}/lp-screens/control/aggregates/lpctl-K0-screen-s42.json"))["items"]
gr = json.load(open(f"{A}/greedy/aggregates/greedy-K0-screen-s42.json"))["items"]
for tag, src in (("ctl", ctl), ("greedy", gr)):
    op = judg_pairs(glob.glob(f"{CO}/out/{tag}-*.judgments.jsonl"))
    for i, o in op.items():
        x = src[i]; d = is_decline(x["text"], x["declined"])
        JD[i].append((x["corr"], o["corr"], (not d) and x["corr"] <= 1.5, (not d) and o["corr"] <= 1.5, "ceopus-" + tag))
ru = json.load(open(f"{A}/refuse-unsupported/ce-opus-ru/ceopusru-opus.json"))["per_item"]
for i, v in ru.items():
    t = LTR["K3"][i]["answer"]; d = is_decline(t["text"], t.get("declined"))
    JD[i].append((v["haiku"], v["opus"], (not d) and v["haiku"] <= 1.5, (not d) and v["opus"] <= 1.5, "ceopus-ru-K3"))

# ---------------- in-pack ----------------
IP = json.load(open(f"{R0}/inpack-assignment.json"))["items"]

# ---------------- deterministic / reaches_model ----------------
P0 = json.load(open(f"{A}/null-cal/control/pool-K0.json"))["items"]; P1 = json.load(open(f"{A}/null-cal/control/pool-K1.json"))["items"]
def phone_det(i):
    rs = [PROWS[k][i] for k in ("q17b73", "gemma73", "4b-pixel") if i in PROWS[k]]
    return len(rs) == 3 and len({r["answer"] for r in rs}) == 1 and all((r.get("tokensGenerated") or 0) == 0 for r in rs)
def phone_gen(i): return {k: (PROWS[k][i].get("tokensGenerated") or 0) > 0 for k in ("q17b73", "gemma73", "4b-pixel", "4b-poco") if i in PROWS[k]}
def desk_texts(i): return {C[n][i]["text"] for n in C if not n.startswith("ph-") and i in C[n]}
def desk_det(i):
    if i not in P0: return None
    return (not P0[i]["live"]) and (not P1[i]["live"]) and len(desk_texts(i)) <= 1

# ---------------- per item ----------------
def pair(a, b, i):
    if i in C[a] and i in C[b]:
        x, y = C[a][i], C[b][i]
        return dict(du=round(y["u"] - x["u"], 4), ce_flip=x["CE"] != y["CE"], r_flip=x["R"] != y["R"], same_text=x["text"] == y["text"])
    return None
ITEMS = {}
for i in sorted(set(MAIN) | set(ST) | set(V72)):
    recs = {n: C[n][i] for n in C if i in C[n] and C[n][i]["u"] is not None}
    us = [r["u"] for r in recs.values()]
    jd = JD.get(i, [])
    judge_flip = any(h_ce != o_ce or abs(hc - oc) >= 1.5 for hc, oc, h_ce, o_ce, _ in jd) if jd else None
    ce_flip = len({r["CE"] for r in recs.values()}) > 1; r_flip = len({r["R"] for r in recs.values()}) > 1
    w_flip = len({r["warned"] for r in recs.values()}) > 1
    urange = (max(us) - min(us)) if len(us) >= 2 else None
    D = None if urange is None else round(urange + 0.25 * ce_flip + 0.25 * r_flip + 0.25 * bool(judge_flip), 4)
    inv72 = i in V72; det_p = phone_det(i) if inv72 else None; det_d = desk_det(i)
    dets = [x for x in (det_p, det_d) if x is not None]
    det = all(dets) if dets else False
    ip = IP.get(i)
    texts = desk_texts(i) | ({PROWS[k][i]["answer"] for k in ("q17b73", "gemma73", "4b-pixel") if i in PROWS[k]} if inv72 else set())
    seeds = dict(gemma_s42_s43=pair("gemma-K0-s42", "gemma-K0-s43", i), q17_s42_s43=pair("ctl17-K0-s42", "q17-K0-s43", i),
                 nullcal_K0_s43=pair("ctl17-K0-s42" if i in MAIN else "ctl17-K0-st-s42", "nulls43-K0", i),
                 nullcal_K1_s43=pair("ctl17-K1-s42" if i in MAIN else "ctl17-K1-st-s42", "nulls43-K1", i),
                 nullcal_K0_ws=pair("ctl17-K0-s42" if i in MAIN else "ctl17-K0-st-s42", "nullws-K0", i),
                 host_K0_macbook_mini=pair("lp-K0", "ctl17-K0-s42" if i in MAIN else "ctl17-K0-st-s42", i))
    seeds = {k: v for k, v in seeds.items() if v}
    ITEMS[i] = dict(sets=[s for s, ids in SETS.items() if i in ids], deterministic=det, reaches_model=not det,
                    deterministic_phone=det_p, deterministic_desktop=det_d,
                    live_K0=P0[i]["live"] if i in P0 else None, live_K1=P1[i]["live"] if i in P1 else None,
                    phone_generates=phone_gen(i) if inv72 else None,
                    phone_reason=[c for c in PROWS["q17b73"][i]["reasonCodes"] if c.startswith(("answer:", "grounding:", "detector:fire"))] if inv72 else None,
                    phone_wall_ms_q17=round(PROWS["q17b73"][i]["totalLatencyMs"]) if inv72 else None,
                    in_pack=(ip["side"] == "in") if ip else None, pack_tag=ip["tag"] if ip else None,
                    n_cond=len(recs), u_min=round(min(us), 4) if us else None, u_max=round(max(us), 4) if us else None,
                    u_mean=round(statistics.mean(us), 4) if us else None, u_range=round(urange, 4) if urange is not None else None,
                    corr_min=min((r["corr"] for r in recs.values()), default=None), corr_mean=round(statistics.mean([r["corr"] for r in recs.values()]), 3) if recs else None,
                    ce_flip=ce_flip, r_flip=r_flip, warned_flip=w_flip, ce_any=any(r["CE"] for r in recs.values()), r_all=all(r["R"] for r in recs.values()) if recs else None,
                    shown_all=(not any(r["R"] for r in recs.values())) if recs else None, distinct_texts=len(texts),
                    judge=[dict(haiku=h, opus=o, haiku_CE=a, opus_CE=b, src=s) for h, o, a, b, s in jd] or None, judge_flip=judge_flip,
                    seeds=seeds, D=D, conds=sorted(recs))
# ---------------- subsets ----------------
TOPN = {"main": 30, "st180": 40, "v01": 20}
# K0 family = every condition a K0 runner is compared with (any model, seed, host, null perturbation, phone); pack sets K1-K4 excluded
FK0 = [n for n in C if n == "lp-K0" or n.startswith("ph-") or ("K0" in n and not n.startswith("lp-"))]
def live(s, i): return (not ITEMS[i]["deterministic_phone"]) if s == "v01" else (ITEMS[i]["deterministic_desktop"] is not True)
SUB, SENT = {}, {}
for s, ids in SETS.items():
    lv = [i for i in ids if live(s, i) and ITEMS[i]["D"] is not None]
    SUB[s] = sorted(lv, key=lambda i: (-ITEMS[i]["D"], i))[:TOPN[s]]
    # sentinels (K0 family): tier 1 = 0 CE, 0 refused (R), min corr >= 3.0 in every K0-family condition (>= 3 conditions);
    # tier 2 fill = 0 CE and min corr >= 3.0, ranked by refused share; both ranked by u_range asc, then u_mean desc
    st = []
    for i in lv:
        r = [C[n][i] for n in FK0 if i in C[n]]
        if len(r) < 3 or i in SUB[s]: continue
        nce = sum(x["CE"] for x in r); us = [x["u"] for x in r]; rs = sum(x["R"] for x in r) / len(r)
        cmin = min(x["corr"] for x in r); cmed = statistics.median([x["corr"] for x in r])
        if nce == 0 and cmin >= 3.0: tier = 1 if rs == 0 else 2
        elif nce <= 1 and cmed >= 3.5: tier = 3  # fill only: one CE draw allowed
        else: continue
        st.append((tier, nce, round(rs, 3), round(max(us) - min(us), 4), -round(sum(us) / len(us), 4), i, len(r)))
    st.sort(); SENT[s] = [x[5] for x in st[:10]]
    for t, nce, rs, ur, um, i, n in st[:10]: ITEMS[i]["sentinel_" + s] = dict(tier=t, ce_draws_K0fam=nce, refused_share_K0fam=rs, u_range_K0fam=ur, u_mean_K0fam=-um, n_K0fam=n)
DET_V01 = [i for i in V73 if i == "warmup-000" or ITEMS[i]["deterministic_phone"]]
for s in SETS:
    for i in SUB[s]: ITEMS[i].setdefault("flags", []).append(f"divergent-{s}")
    for i in SENT[s]: ITEMS[i].setdefault("flags", []).append(f"sentinel-{s}")

# ---------------- savings on this week's arms (traces / judgment rows since 2026-10-19 00:00 local) ----------------
import time
T0 = time.mktime(time.strptime("2026-10-19 00:00", "%Y-%m-%d %H:%M"))
ALLIDS = set(MAIN) | set(ST) | set(V72)
DIV = {s: set(SUB[s]) for s in SETS}; DS = {s: set(SUB[s]) | set(SENT[s]) for s in SETS}
DIVU = set().union(*DIV.values()); DSU = set().union(*DS.values()); DETU = {i for i in ALLIDS if ITEMS[i]["deterministic"]}
def arm_of(p): return os.path.relpath(p, A).split("/")[0]
gen = collections.defaultdict(lambda: collections.Counter()); cal = collections.defaultdict(lambda: collections.Counter())
for f in glob.glob(f"{A}/**/*.traces.jsonl", recursive=True):
    if os.path.islink(f) or os.path.getmtime(f) < T0 or "smoke" in f: continue
    a = arm_of(os.path.realpath(f))
    for l in open(f):
        try: i = json.loads(l).get("itemId")
        except Exception: continue
        if i not in ALLIDS: gen[a]["other"] += 1; continue
        gen[a]["all"] += 1; gen[a]["div"] += i in DIVU; gen[a]["div+sent"] += i in DSU; gen[a]["live"] += i not in DETU
for f in glob.glob(f"{A}/**/*.judgments.jsonl", recursive=True) + glob.glob(f"{A}/**/*.judgments.shards/*.jsonl", recursive=True):
    if os.path.islink(f) or os.path.getmtime(f) < T0 or ".shards/" in f: continue  # merged files only (shards duplicate them)
    a = arm_of(os.path.realpath(f))
    for l in open(f):
        try: i = json.loads(l).get("queryId")
        except Exception: continue
        if i not in ALLIDS: cal[a]["other"] += 1; continue
        cal[a]["all"] += 1; cal[a]["div"] += i in DIVU; cal[a]["div+sent"] += i in DSU; cal[a]["live"] += i not in DETU
SAV = {a: dict(gen=dict(gen[a]), calls=dict(cal[a])) for a in sorted(set(gen) | set(cal)) if gen[a]["all"] or cal[a]["all"]}
tot = lambda k, c: sum(SAV[a][k].get(c, 0) for a in SAV)
SAVT = {k: {c: tot(k, c) for c in ("all", "live", "div+sent", "div", "other")} for k in ("gen", "calls")}


# ---------------- summary stats (pairs, judge, deterministic test-retest) ----------------
def pearson(x, y):
    mx, my = statistics.mean(x), statistics.mean(y); sx = math.sqrt(sum((a - mx) ** 2 for a in x)); sy = math.sqrt(sum((b - my) ** 2 for b in y))
    return round(sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy), 3) if sx and sy else None
PAIRS = {"1.7B K0 seed 42 vs 43 (mini, MAIN)": ("ctl17-K0-s42", "q17-K0-s43"), "Gemma K0 seed 42 vs 43 (mini, MAIN)": ("gemma-K0-s42", "gemma-K0-s43"),
         "1.7B K0 MacBook vs mini (s42, MAIN)": ("lp-K0", "ctl17-K0-s42"), "1.7B K0 MacBook vs mini (s42, st180)": ("lp-K0", "ctl17-K0-st-s42"),
         "null-cal K0 seed 43 vs control (screen2)": ("ctl17-K0-s42+st", "nulls43-K0"), "null-cal K0 whitespace vs control (screen2)": ("ctl17-K0-s42+st", "nullws-K0"),
         "null-cal K1 seed 43 vs control (screen2)": ("ctl17-K1-s42+st", "nulls43-K1"), "1.7B K0 vs K1 pack set (MacBook)": ("lp-K0", "lp-K1"),
         "1.7B K0 vs K3 pack set (MacBook)": ("lp-K0", "lp-K3"), "1.7B vs Gemma (K0 s42 mini, MAIN)": ("ctl17-K0-s42", "gemma-K0-s42"),
         "1.7B vs 4B (K0 s42 mini, MAIN)": ("ctl17-K0-s42", "q4b-K0-s42"), "phone Gemma vs desktop Gemma s42 (v0.1 57)": ("gemma-K0-s42", "ph-gemma"),
         "phone 4B Pixel vs POCO (v0.1 57)": ("ph-4b-pixel", "ph-4b-poco")}
C["ctl17-K0-s42+st"] = {**C["ctl17-K0-s42"], **C["ctl17-K0-st-s42"]}; C["ctl17-K1-s42+st"] = {**C["ctl17-K1-s42"], **C["ctl17-K1-st-s42"]}
PS = {}
for nm, (a, b) in PAIRS.items():
    ids = [i for i in C[b] if i in C[a] and C[a][i]["u"] is not None and C[b][i]["u"] is not None]
    lvi = [i for i in ids if not ITEMS.get(i, {}).get("deterministic")]
    x = [C[a][i]["u"] for i in lvi]; y = [C[b][i]["u"] for i in lvi]
    PS[nm] = dict(n=len(ids), n_live=len(lvi), same_text_live=sum(C[a][i]["text"] == C[b][i]["text"] for i in lvi), r_live=pearson(x, y) if len(lvi) > 2 else None,
                  mean_abs_du_live=round(statistics.mean(abs(p - q) for p, q in zip(x, y)), 3) if lvi else None,
                  ce_flips_live=sum(C[a][i]["CE"] != C[b][i]["CE"] for i in lvi), r_flips_live=sum(C[a][i]["R"] != C[b][i]["R"] for i in lvi),
                  big_moves_live=sum(abs(C[a][i]["u"] - C[b][i]["u"]) >= 0.3 for i in lvi))
del C["ctl17-K0-s42+st"], C["ctl17-K1-s42+st"]
jr = [(h, o, a, b) for i in JD for h, o, a, b, _ in JD[i]]
JS = dict(answers=len(jr), items=len(JD), ce_label_flips=sum(a != b for _, _, a, b in jr), corr_gap_ge_1_5=sum(abs(h - o) >= 1.5 for h, o, _, _ in jr),
          mean_abs_corr_gap=round(statistics.mean(abs(h - o) for h, o, _, _ in jr), 3), items_flagged=sum(1 for i in ITEMS if ITEMS[i]["judge_flip"]))
DT = [ITEMS[i] for i in ITEMS if ITEMS[i]["deterministic"] and ITEMS[i]["u_range"] is not None]
DS_ = dict(n=len(DT), u_range_median=round(statistics.median([x["u_range"] for x in DT]), 3) if DT else None,
           u_range_p90=round(sorted(x["u_range"] for x in DT)[int(0.9 * len(DT))], 3) if DT else None, ce_flip=sum(x["ce_flip"] for x in DT),
           note="deterministic items: one answer text in every condition, so u_range here is pure judge test-retest noise (Haiku re-judging identical text across runs)")

# ---------------- write ----------------
os.makedirs(f"{R0}/ids", exist_ok=True)
def wids(name, ids, note):
    p = f"{R0}/ids/{name}.ids"; open(p, "w").write("".join(x + "\n" for x in ids))
    h = hashlib.sha256(open(p, "rb").read()).hexdigest(); open(p + ".sha256", "w").write(f"{h}  {name}.ids\n"); return dict(file=f"ids/{name}.ids", n=len(ids), sha256=h, note=note)
IDF = {}
IDF["divergent-main"] = wids("divergent-main", SUB["main"], "top 30 of MAIN 97 by D, live items only")
IDF["divergent-st180"] = wids("divergent-st180", SUB["st180"], "top 40 of the 180 self-tests by D, live items only")
IDF["divergent-v01"] = wids("divergent-v01", SUB["v01"], "top 20 of the 72 v0.1 phone ids by D, phone-live items only")
IDF["divergent-pool"] = wids("divergent-pool", sorted(set(SUB["main"]) | set(SUB["st180"])), "union main + st180 (for run_pool.sh, any order)")
for s in SETS: IDF[f"sentinels-{s}"] = wids(f"sentinels-{s}", SENT[s], "10 stable, shown, judge-correct live items")
IDF["sentinels-pool"] = wids("sentinels-pool", sorted(set(SENT["main"]) | set(SENT["st180"])), "union main + st180 sentinels")
IDF["stage1-pool"] = wids("stage1-pool", sorted(set(SUB["main"]) | set(SUB["st180"]) | set(SENT["main"]) | set(SENT["st180"])), "divergent + sentinels, main + st180")
IDF["stage1-v01-phone"] = wids("stage1-v01-phone", ["warmup-000"] + [i for i in V73 if i in set(SUB["v01"]) | set(SENT["v01"])], "warm-up + divergent + sentinels, phone order")
IDF["deterministic-v01"] = wids("deterministic-v01", DET_V01, "phone: identical text and 0 generated tokens on 1.7B, Gemma and 4B (warm-up included); skip on phone runs")
IDF["deterministic-pool"] = wids("deterministic-pool", sorted(i for i in set(MAIN) | set(ST) if ITEMS[i]["deterministic"]), "desktop: 0 tokens on K0+K1 controls and one text across all desktop conditions")
out = dict(generated="2026-10-21", script="ruler/tools/divergence_map.py", definition=__doc__.split("DIVERGENCE SCORE")[1].split("deterministic =")[0].strip(),
           conditions={n: dict(n=len(C[n]), group=GROUP[n]) for n in C}, sets={s: len(v) for s, v in SETS.items()}, ids_files=IDF,
           pair_stats=PS, judge_stats=JS, deterministic_judge_noise=DS_, subsets=dict(divergent=SUB, sentinels=SENT, deterministic_v01=DET_V01), savings_since_2026_10_19=dict(per_arm=SAV, total=SAVT), items=ITEMS)
json.dump(out, open(f"{R0}/divergence-map.json", "w"), indent=1, sort_keys=False)
h = hashlib.sha256(open(f"{R0}/divergence-map.json", "rb").read()).hexdigest(); open(f"{R0}/divergence-map.json.sha256", "w").write(f"{h}  divergence-map.json\n")
# ---------------- summary ----------------
print("conditions", {n: len(C[n]) for n in C})
for s, ids in SETS.items():
    it = [ITEMS[i] for i in ids]; live = [x for x in it if x["reaches_model"]]; Ds = sorted(x["D"] for x in live if x["D"] is not None)
    q = lambda p: Ds[min(len(Ds) - 1, int(p * len(Ds)))] if Ds else None
    print(f"[{s}] n {len(ids)} det {sum(x['deterministic'] for x in it)} live {len(live)} in_pack {sum(bool(x['in_pack']) for x in it)} "
          f"D p25/50/75/90 {q(.25)}/{q(.5)}/{q(.75)}/{q(.9)} ce_flip {sum(x['ce_flip'] for x in live)} r_flip {sum(x['r_flip'] for x in live)} "
          f"judge_flip {sum(bool(x['judge_flip']) for x in it)}/{sum(x['judge'] is not None for x in it)} ncond med {statistics.median([x['n_cond'] for x in it])}")
    print("  divergent", [(i, ITEMS[i]["D"]) for i in SUB[s][:8]], "... cut D", ITEMS[SUB[s][-1]]["D"] if SUB[s] else None)
    print("  sentinels", [(i, ITEMS[i]["u_range"], ITEMS[i]["corr_min"]) for i in SENT[s]])
print(json.dumps(PS, indent=0)); print(JS); print(DS_); print("deterministic-v01", len(DET_V01)); print("savings total", SAVT); print("sha", h)
