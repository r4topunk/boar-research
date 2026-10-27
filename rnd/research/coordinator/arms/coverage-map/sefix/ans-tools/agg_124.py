#!/usr/bin/env python3
"""SEFIX-124 (F1+F2+F4, F3 off) answer screen aggregate (0 LLM; adapted from agg_all.py / agg_s43.py). python3 -I agg_124.py -> ../answers-sefix124.json, ../answers-sefix124.md
Arms per seed: X = ans-traces/sefix124-main-s{42,43}; CTL = K3 control of the seed (s42 pool-K1 judged rows / litepacks mini K1 traces; s43 ctlk1-main-s43); ALL = SEFIX-ALL of the seed (side by side); G = ARM-G (s42 only).
Row per (id, answer text): (1) X text == control text -> control row (delta 0); (2) X text == SEFIX-ALL text of the same seed with a real ALL row -> that row; (3) cache of every judged row with the same (id, text)
(pool-K1, ARM-G, SEFIX-ALL s42 / s43 judged+cache, control s43 judged+cache); (4) the new Haiku rows (ans-judge/S124/<seed>.<arm>); (5) else unjudged -> PROXY: the s42 control row given to BOTH arms (delta 0), flagged.
U ratio-of-sums (declined -> 0), CE = not declined and corr <= 1.5, warned = engine warning line first; bootstrap over items, B 2000, random.Random(11), paired on the same draws.
Pooled two seeds: per item mean over seeds of (0 if declined else s), mean sref, mean corr (as agg_s43). Rule = SEFIX-criterion LEVER-CANDIDATE read as in answers-sefixall-s43 (changed = items whose text differs from the control with real rows in either seed)."""
import json, glob, random, collections
A = "<workspace>/rnd/research/coordinator/arms"; CM = A + "/coverage-map"; SF = CM + "/sefix"
W = "Not found in this phone's offline library. From the model's memory, may be wrong:"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
ld = lambda p: {t["itemId"]: t for t in rd(p)}
ids = open(A + "/lp-screens/main-97.ids").read().split()
src_of = lambda i: "v0.1" if not i.startswith("st-") else ("cooking" if "cooking" in i else "money")
r42 = json.load(open(SF + "/answers-sefixall.json")); r43 = json.load(open(SF + "/answers-sefixall-s43.json")); pool = json.load(open(A + "/null-cal/control/pool-K1.json"))["items"]
ctl42 = {}
for f in glob.glob(A + "/litepacks/traces/mini/lp-K1-*-s42.mini.traces.jsonl"): ctl42.update(ld(f))
for i, t in [(i, t) for i, t in ctl42.items() if i in pool]:   # s42 control = the judged pool-K1 text/row (as agg_all.py); 2 items (lan-exp-007, st-qa-money-se-005) differ between pool-K1 and the mini K1 re-run traces
    t["answer"] = dict(t["answer"], text=pool[i]["text"], declined=bool(pool[i].get("declined")))
TG = ld(CM + "/compose/screen/traces/cmp-G-K10-main-s42.traces.jsonl")
TR = {42: dict(X=ld(SF + "/ans-traces/sefix124-main-s42.traces.jsonl"), C=ctl42, F=ld(SF + "/ans-traces/sefixall-main-s42.traces.jsonl")),
      43: dict(X=ld(SF + "/ans-traces/sefix124-main-s43.traces.jsonl"), C=ld(SF + "/ans-traces/ctlk1-main-s43.traces.jsonl"), F=ld(SF + "/ans-traces/sefixall-main-s43.traces.jsonl"))}
KEYS = ("s", "sref", "corr", "declined", "warned")
def jby(JD):
    by = {}
    for f in sorted(glob.glob(JD + "/*.judgments.jsonl")):
        for r in rd(f):
            if r.get("ok") is True: by.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
    return by
dim = lambda m, k: sum(m[k].values()) / 3
def jrow(by, i):
    ms = list(by[i].values())
    return dict(s=sum(dim(m, "boar") for m in ms) / 2, sref=sum(dim(m, "ref") for m in ms) / 2, corr=sum(m["boar"]["correctness"] for m in ms) / 2)
NEWJ = {f"{s}.{a}": jby(f"{SF}/ans-judge/S124/{s}.{a}") for s in (42, 43) for a in ("X", "C")}
cache = {}
def put(i, txt, row): cache[(i, txt)] = {k: row.get(k) for k in KEYS}
for i in ids:
    put(i, pool[i]["text"], r42["rows"]["control"][i]); put(i, TG[i]["answer"]["text"], r42["rows"]["G"][i]); put(i, TR[42]["F"][i]["answer"]["text"], r42["rows"]["ALL"][i])
    for arm, nm in (("C", "ctl"), ("F", "ALL")):
        if r43["items"][i][nm]["judgment"] != "proxy": put(i, TR[43][arm][i]["answer"]["text"], r43["items"][i][nm])
for s in (42, 43):
    for arm in ("X", "C"):
        for i, by in NEWJ[f"{s}.{arm}"].items():
            if len(by) == 2:
                t = TR[s][arm][i]; row = jrow(NEWJ[f"{s}.{arm}"], i); row.update(declined=bool(t["answer"].get("declined")), warned=t["answer"]["text"].startswith(W)); put(i, t["answer"]["text"], row)
def build(s):
    X, C, F = TR[s]["X"], TR[s]["C"], TR[s]["F"]; RX, RC, RF = {}, {}, {}
    for i in ids:
        tx, tc, tf = (D[i]["answer"]["text"] for D in (X, C, F))
        def mk(D, txt, row, src):
            return dict(row, text=txt, judgment=src, declined=bool(D[i]["answer"].get("declined")), warned=txt.startswith(W))
        crow = cache.get((i, tc)); frow = cache.get((i, tf)); xrow = cache.get((i, tx))
        RC[i] = mk(C, tc, crow, "cache") if crow else None; RF[i] = mk(F, tf, frow, "cache") if frow else None
        RX[i] = mk(X, tx, xrow, "cache" if tx != tc else "control-row") if xrow else None
    return RX, RC, RF
res = dict(); S = {}
for s in (42, 43):
    RX, RC, RF = build(s)
    for i in ids:   # proxies: delta 0 for items where an arm row is missing
        if RX[i] is None or RC[i] is None:
            p = pool[i]; px = dict(s=p["s"], sref=p["sref"], corr=p["corr"], declined=False, warned=bool(p["warned"]), judgment="proxy")
            for R in (RX, RC): R[i] = dict(R[i] or {}, text=TR[s]["X" if R is RX else "C"][i]["answer"]["text"], **px)
    for R in (RX, RC, RF):
        for i in ids:
            if R[i] is None: R[i] = dict(RC[i], judgment="proxy")
            R[i]["CE"] = (not R[i]["declined"]) and R[i]["corr"] <= 1.5
    S[s] = dict(X=RX, C=RC, F=RF)
def U(src, xs): return sum(0 if src[i]["declined"] else src[i]["s"] for i in xs) / sum(src[i]["sref"] for i in xs)
def mean(src, xs, k, nn=3):
    v = [src[i][k] for i in xs if src[i].get(k) is not None]; return round(sum(v) / len(v), nn) if v else None
def summ(src, xs):
    nd = [i for i in xs if not src[i]["declined"]]; ce = [i for i in nd if src[i]["corr"] <= 1.5]
    return dict(n=len(xs), U=round(U(src, xs), 4), corr=mean(src, xs, "corr"), CE=len(ce), CE_unwarned=sum(1 for i in ce if not src[i]["warned"]), warned=sum(1 for i in xs if src[i]["warned"]), declined=sum(1 for i in xs if src[i]["declined"]))
def boot(xs, f, B=2000):
    r = random.Random(11); v = []
    for _ in range(B): v.append(f([r.choice(xs) for _ in xs]))
    v.sort(); return [round(v[int(0.025 * B)], 4), round(v[int(0.975 * B) - 1], 4)]
def pair(sa, sb, xs):
    if not xs: return dict(n=0)
    f = lambda s: U(sa, s) - U(sb, s); g = lambda s: sum(sa[i]["corr"] - sb[i]["corr"] for i in s) / len(s)
    return dict(n=len(xs), d=round(f(xs), 4), ci=boot(xs, f), dcorr=round(g(xs), 4), dcorr_ci=boot(xs, g))
real = lambda s, i: S[s]["X"][i]["judgment"] != "proxy" and S[s]["C"][i]["judgment"] != "proxy"
td = {s: [i for i in ids if TR[s]["X"][i]["answer"]["text"] != TR[s]["C"][i]["answer"]["text"]] for s in (42, 43)}
J = {s: [i for i in td[s] if real(s, i)] for s in (42, 43)}
for s in (42, 43):
    RX, RC, RF = S[s]["X"], S[s]["C"], S[s]["F"]
    r = dict(text_differs=len(td[s]), n_differing_real=len(J[s]), unjudged_differing=[i for i in td[s] if not real(s, i)], rows=dict(X=dict(collections.Counter(RX[i]["judgment"] for i in ids)), CTL=dict(collections.Counter(RC[i]["judgment"] for i in ids))),
             all97=dict(CTL=summ(RC, ids), X=summ(RX, ids), ALL=summ(RF, ids)), vs_control_all97=pair(RX, RC, ids), ALL_vs_control_all97=pair(RF, RC, ids), X_vs_ALL_all97=pair(RX, RF, ids),
             differing_real=dict(CTL=summ(RC, J[s]), X=summ(RX, J[s]), **pair(RX, RC, J[s])), changed_text_differs=pair(RX, RC, td[s]))
    r["by_source_all"] = {}
    for sc in ("v0.1", "cooking", "money"):
        al = [i for i in ids if src_of(i) == sc]; jj = [i for i in J[s] if src_of(i) == sc]
        r["by_source_all"][sc] = dict(n=len(al), differing_real=len(jj), CTL=summ(RC, al), X=summ(RX, al), vs_control=pair(RX, RC, al), ALL_vs_control=pair(RF, RC, al), differing_only=pair(RX, RC, jj))
    if s == 42:
        RG = {i: dict(r42["rows"]["G"][i], text=TG[i]["answer"]["text"]) for i in ids}
        seq = lambda t: [(c["title"], c.get("section"), c.get("source")) for c in t["retrieval"]["kept"]]
        chgG = [i for i in ids if seq(TR[42]["X"][i]) != seq(TG[i]) and TR[42]["X"][i]["answer"]["text"] != TG[i]["answer"]["text"] and RX[i]["judgment"] != "proxy"]
        r["vs_G_changed"] = dict(n_changed_incl_unjudged=len([i for i in ids if seq(TR[42]["X"][i]) != seq(TG[i]) and TR[42]["X"][i]["answer"]["text"] != TG[i]["answer"]["text"]]), **pair(RX, RG, chgG)); r["vs_G_all97"] = pair(RX, RG, ids)
    r["timing"] = dict(X_out_tok=round(sum(TR[s]["X"][i]["timing"].get("outputTokens") or 0 for i in ids) / 97, 2), CTL_out_tok=round(sum(TR[s]["C"][i]["timing"].get("outputTokens") or 0 for i in ids) / 97, 2),
                       X_totalMs=round(sum(TR[s]["X"][i]["timing"].get("totalMs") or 0 for i in ids) / 97), CTL_totalMs=round(sum(TR[s]["C"][i]["timing"].get("totalMs") or 0 for i in ids) / 97))
    res[f"s{s}"] = r
# pooled
def prow(a, b):
    ea = 0 if a["declined"] else a["s"]; eb = 0 if b["declined"] else b["s"]
    return dict(s=(ea + eb) / 2, sref=(a["sref"] + b["sref"]) / 2, corr=(a["corr"] + b["corr"]) / 2, declined=False)
P = {k: {i: prow(S[42][k][i], S[43][k][i]) for i in ids} for k in ("X", "C", "F")}
union = [i for i in ids if i in set(J[42]) | set(J[43])]; union_td = [i for i in ids if i in set(td[42]) | set(td[43])]
pl = dict(vs_control_all97=pair(P["X"], P["C"], ids), ALL_vs_control_all97=pair(P["F"], P["C"], ids), X_vs_ALL_all97=pair(P["X"], P["F"], ids),
          changed_union_real=dict(n_ids=len(union), **pair(P["X"], P["C"], union)), changed_union_ALL_real=pair(P["F"], P["C"], union), changed_union_text_differs_imputed=dict(**pair(P["X"], P["C"], union_td)))
pl["by_source_all"] = {sc: dict(X=pair(P["X"], P["C"], [i for i in ids if src_of(i) == sc]), ALL=pair(P["F"], P["C"], [i for i in ids if src_of(i) == sc])) for sc in ("v0.1", "cooking", "money")}
ceu = lambda k, s: sum(1 for i in ids if S[s][k][i]["CE"] and not S[s][k][i]["warned"])
pl["CE_unwarned"] = {k: dict(s42=ceu(k, 42), s43=ceu(k, 43)) for k in ("C", "X", "F")}
ce = lambda k, s: sum(1 for i in ids if S[s][k][i]["CE"])
pl["CE_all"] = {k: dict(s42=ce(k, 42), s43=ce(k, 43)) for k in ("C", "X", "F")}
a = pl["changed_union_real"]; b = pl["vs_control_all97"]
up = (pl["CE_unwarned"]["X"]["s42"] + pl["CE_unwarned"]["X"]["s43"]) > (pl["CE_unwarned"]["C"]["s42"] + pl["CE_unwarned"]["C"]["s43"])
rule = dict(changed_dU_ge_0_02_ci_low_gt_minus_0_01=(a["d"] >= 0.02 and a["ci"][0] > -0.01), vs_control_all97_dU_ge_0_02_ci_low_gt_minus_0_01=(b["d"] >= 0.02 and b["ci"][0] > -0.01), CE_unwarned_not_up=not up)
rule["LEVER_CANDIDATE"] = all(rule.values()); pl["rule"] = rule; res["pooled"] = pl
# chunk-level 2x2 and newly delivered (replay flags: chunklevel-124.json; live parity = kept titles of the live trace equal the replay's keptFull titles)
CL = json.load(open(SF + "/chunklevel-124.json"))["per_item"]
RPL = {"B0": A + "/retrieve-sweep/replay/B0.main.jsonl", "G": CM + "/compose/replays/main.N10.gidf.jsonl", "X": SF + "/replays/main.F1F2F4.jsonl", "F": SF + "/replays/main.F1F2F3F4.jsonl"}
LAB = {"B0": "B0 stock (retrieve-sweep)", "G": "compose N10.gidf", "X": "sefix F1F2F4", "F": "sefix F1F2F3F4"}
RP = {k: {r["id"]: r for r in rd(f)} for k, f in RPL.items()}
ttl = lambda t: [c["title"] for c in t["retrieval"]["kept"]]
def flag(k, s, i):   # chunk-level fact flag of arm k in the replay, only where the live kept titles equal the replay's
    live = {"B0": TR[s]["C"], "G": None, "X": TR[s]["X"], "F": TR[s]["F"]}[k]
    if live is None: live = TG if s == 42 else None
    if live is None or CL[LAB[k]].get(i) is None or i not in RP[k]: return None
    return CL[LAB[k]][i]["chunk"] if ttl(live[i]) == [c["title"] for c in RP[k][i]["keptFull"]] else None
cell = {}
for s in (42, 43):
    for i in ids: cell[(s, i)] = {k: flag(k, s, i) for k in ("B0", "G", "X", "F")}
def cells(xs, base, arm, rows_b, rows_a, s=None):
    c = collections.defaultdict(list)
    for i in xs:
        fb = cell[(s, i)][base] if s else (cell[(42, i)][base] if cell[(42, i)][base] == cell[(43, i)][base] else None)
        fa = cell[(s, i)][arm] if s else (cell[(42, i)][arm] if cell[(42, i)][arm] == cell[(43, i)][arm] else None)
        if fb is None or fa is None: c["no-flag"].append(i); continue
        c[f"{base}_{'P' if fb else 'A'}__{arm}_{'P' if fa else 'A'}"].append(i)
    return {k: dict(n=len(v), corr_base=mean(rows_b, v, "corr"), corr_arm=mean(rows_a, v, "corr"), **{k2: v2 for k2, v2 in pair(rows_a, rows_b, v).items() if k2 in ("d", "ci")}) for k, v in sorted(c.items())}
res["chunk2x2_vs_control_pooled"] = dict(X=cells(ids, "B0", "X", P["C"], P["X"]), ALL=cells(ids, "B0", "F", P["C"], P["F"]))
for s in (42, 43): res[f"s{s}"]["chunk2x2_vs_control"] = dict(X=cells(ids, "B0", "X", S[s]["C"], S[s]["X"], s), ALL=cells(ids, "B0", "F", S[s]["C"], S[s]["F"], s))
# delivered facts: chunk flag True in the arm's replay and False in N10 gidf (replay-level), keyed MAIN ids
def delivered(k):
    return [i for i in ids if CL[LAB[k]].get(i) and CL["compose N10.gidf"].get(i) and CL[LAB[k]][i]["chunk"] and not CL["compose N10.gidf"][i]["chunk"]]
nd = {}
for k, nm in (("X", "X"), ("F", "F")):
    xs = delivered(k); live = [i for i in xs if cell[(42, i)][k] is not None and cell[(43, i)][k] is not None]
    nd[nm] = dict(replay_n=len(xs), cm=sum(1 for i in xs if i.startswith("st-")), v01=sum(1 for i in xs if not i.startswith("st-")), live_parity_both_seeds=len(live), ids=xs,
                  pooled_corr=dict(CTL=mean(P["C"], xs, "corr"), ARM=mean(P[k], xs, "corr")), pooled_U=dict(CTL=round(U(P["C"], xs), 4), ARM=round(U(P[k], xs), 4)), pooled_vs_control=pair(P[k], P["C"], xs),
                  s42_vs_G=pair({i: dict(r42["rows"]["G"][i], text="") for i in ids} if False else S[42][k], {i: r42["rows"]["G"][i] for i in ids}, xs),
                  per_seed={f"s{s}": dict(corr_CTL=mean(S[s]["C"], xs, "corr"), corr_ARM=mean(S[s][k], xs, "corr"), warned_ARM=sum(S[s][k][i]["warned"] for i in xs), declined_ARM=sum(S[s][k][i]["declined"] for i in xs), proxy=sum(S[s][k][i]["judgment"] == "proxy" for i in xs)) for s in (42, 43)})
res["newly_delivered_chunk"] = nd
res["newly_delivered_chunk"]["X_only_not_in_ALL_replay"] = [i for i in nd["X"]["ids"] if i not in nd["F"]["ids"]]; res["newly_delivered_chunk"]["ALL_only_not_in_124_replay"] = [i for i in nd["F"]["ids"] if i not in nd["X"]["ids"]]
res["items"] = {s: {i: dict(src=src_of(i), text_differs=i in td[s], ctl={k: S[s]["C"][i].get(k) for k in KEYS + ("judgment",)}, X={k: S[s]["X"][i].get(k) for k in KEYS + ("judgment",)}) for i in ids} for s in (42, 43)}
json.dump(res, open(SF + "/answers-sefix124.json", "w"), indent=1, ensure_ascii=False)
# markdown
L = ["# SEFIX-124 (F1+F2+F4, F3 off) answer screen, MAIN 97 (Haiku 5.5-low judge.v1 N4 both orders; Opus 0, paid 0, phone 0; generated by ans-tools/run_124_gen.sh, aggregated by ans-tools/agg_124.py)", "",
     "| seed | arm | U | corr | CE | CE unwarned | warned | declined |", "|---|---|---|---|---|---|---|---|"]
for s in (42, 43):
    for nm, k in (("K3 control", "CTL"), ("SEFIX-124", "X"), ("SEFIX-ALL", "ALL")):
        x = res[f"s{s}"]["all97"][k]; L.append(f"| s{s} | {nm} | {x['U']} | {x['corr']} | {x['CE']} | {x['CE_unwarned']} | {x['warned']} | {x['declined']} |")
for s in (42, 43):
    r = res[f"s{s}"]
    L += ["", f"## seed {s}: text differs vs control {r['text_differs']}/97; differing with real rows {r['differing_real']['n']}; unjudged differing {len(r['unjudged_differing'])}; rows X {r['rows']['X']}, CTL {r['rows']['CTL']}",
          f"- dU 124 - control all 97 {r['vs_control_all97']['d']} {r['vs_control_all97']['ci']}; ALL - control {r['ALL_vs_control_all97']['d']} {r['ALL_vs_control_all97']['ci']}; 124 - ALL {r['X_vs_ALL_all97']['d']} {r['X_vs_ALL_all97']['ci']}; differing-real {r['differing_real'].get('d')} {r['differing_real'].get('ci')}",
          "- by source (all items vs control; 124 | ALL): " + "; ".join(f"{sc} n{v['n']} {v['vs_control']['d']} {v['vs_control']['ci']} | {v['ALL_vs_control']['d']}" for sc, v in r["by_source_all"].items())]
    if s == 42: L.append(f"- vs ARM-G: changed (kept differs, text differs, real row; n {r['vs_G_changed']['n']} of {r['vs_G_changed']['n_changed_incl_unjudged']}) {r['vs_G_changed'].get('d')} {r['vs_G_changed'].get('ci')}; all 97 {r['vs_G_all97']['d']} {r['vs_G_all97']['ci']}")
p = res["pooled"]
L += ["", "## pooled two seeds", f"- 124 - control all 97 {p['vs_control_all97']['d']} {p['vs_control_all97']['ci']}; ALL - control {p['ALL_vs_control_all97']['d']} {p['ALL_vs_control_all97']['ci']}; 124 - ALL {p['X_vs_ALL_all97']['d']} {p['X_vs_ALL_all97']['ci']}",
      f"- changed union (real rows, n {p['changed_union_real']['n']}): 124 {p['changed_union_real']['d']} {p['changed_union_real']['ci']}; ALL {p['changed_union_ALL_real']['d']} {p['changed_union_ALL_real']['ci']}; text-differs union incl. imputed {p['changed_union_text_differs_imputed']['d']} {p['changed_union_text_differs_imputed']['ci']}",
      "- by source (pooled, vs control; 124 | ALL): " + "; ".join(f"{sc} {v['X']['d']} {v['X']['ci']} | {v['ALL']['d']} {v['ALL']['ci']}" for sc, v in p["by_source_all"].items()),
      f"- CE-unwarned {p['CE_unwarned']}; CE {p['CE_all']}", f"- rule: {p['rule']}", "", "## chunk-level 2x2 (pooled; B0 = control kit replay, X = F1F2F4 replay; items with live-title parity)"]
for nm, blk in res["chunk2x2_vs_control_pooled"].items():
    for k, v in blk.items(): L.append(f"- {nm} {k}: n {v['n']} corr {v['corr_base']} -> {v['corr_arm']}, dU {v.get('d')} {v.get('ci')}")
L += ["", "## delivered facts (chunk-level in replay, not in N10 gidf)"]
for nm in ("X", "F"):
    v = res["newly_delivered_chunk"][nm]; L.append(f"- {nm}: n {v['replay_n']} (cm {v['cm']}, v0.1 {v['v01']}); pooled corr control {v['pooled_corr']['CTL']} -> arm {v['pooled_corr']['ARM']}; dU vs control {v['pooled_vs_control'].get('d')} {v['pooled_vs_control'].get('ci')}; per seed {v['per_seed']}")
L.append(f"- in 124 replay not ALL: {res['newly_delivered_chunk']['X_only_not_in_ALL_replay']}; in ALL not 124: {res['newly_delivered_chunk']['ALL_only_not_in_124_replay']}")
open(SF + "/answers-sefix124.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
