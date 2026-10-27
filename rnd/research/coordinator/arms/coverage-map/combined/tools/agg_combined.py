#!/usr/bin/env python3
"""COMBINED aggregate (0 LLM). python3 -I agg_combined.py -> ../answers-combined.json, ../answers-combined.md
Arms per seed s in (42, 43): K = K3 control (s42: null-cal/control/pool-K1 rows via sefix/answers-sefixall.json rows.control; s43: ctlk1-main-s43 rows of sefix/answers-sefixall-s43.json items[*].ctl),
F = SEFIX-ALL (s42: answers-sefixall.json rows.ALL; s43: answers-sefixall-s43.json items[*].ALL), C = COMBINED = SEFIX-ALL + RD1 (traces/combined-main-s<seed>).
Row of C for an item: text equal to F's -> F's row (reused); else text equal to K's -> K's row; else Haiku judge.v1 N4 both orders rows of this arm (judge/S<seed>/C); else UNJUDGED -> F's row imputed (delta 0, flagged, counted).
Rows of F/K that are proxies in the s43 replicate (judgment == 'proxy') and have no row of mine (judge/S43/{F,K} fill judgments) stay proxies, flagged.
Definitions as sefix/ans-tools/agg_all.py: ratio-of-sums U (declined = 0), CE = not declined and corr <= 1.5, warned = engine warning line first, bootstrap over items B 2000 random.Random(11), paired on the same draws.
Pooled two seeds: per item mean over the seeds of (0 if declined else s), mean sref, mean corr."""
import json, glob, random, collections, os
A = "<workspace>/rnd/research/coordinator/arms"; CM = A + "/coverage-map"; SF = CM + "/sefix"; CB = CM + "/combined"
W = "Not found in this phone's offline library. From the model's memory, may be wrong:"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
ld = lambda p: {t["itemId"]: t for t in rd(p)}
ids = open(A + "/lp-screens/main-97.ids").read().split()
src_of = lambda i: "v0.1" if not i.startswith("st-") else ("cooking" if "cooking" in i else "money")
r42 = json.load(open(SF + "/answers-sefixall.json")); pool = json.load(open(A + "/null-cal/control/pool-K1.json"))["items"]
r43 = json.load(open(SF + "/answers-sefixall-s43.json"))
def jby(JD):
    by = {}
    for f in sorted(glob.glob(JD + "/*.judgments.jsonl")):
        for r in rd(f):
            if r.get("ok") is True: by.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
    return by
dim = lambda m, k: sum(m[k].values()) / 3
def jrow(by, i):
    ms = list(by[i].values())
    return dict(s=sum(dim(m, "boar") for m in ms) / 2, sref=sum(dim(m, "ref") for m in ms) / 2, corr=sum(m["boar"]["correctness"] for m in ms) / 2, use=sum(m["boar"]["usefulness"] for m in ms) / 2)
TC = {s: ld(f"{CB}/traces/combined-main-s{s}.traces.jsonl") for s in (42, 43)}
TF = {42: ld(SF + "/ans-traces/sefixall-main-s42.traces.jsonl"), 43: ld(SF + "/ans-traces/sefixall-main-s43.traces.jsonl")}
TK = {42: None, 43: ld(SF + "/ans-traces/ctlk1-main-s43.traces.jsonl")}
def rowof(t, j, judgment):
    txt = t["answer"]["text"]; d = bool(t["answer"].get("declined"))
    r = dict(s=j["s"], sref=j["sref"], corr=j["corr"], use=j.get("use"), text=txt, declined=d, warned=txt.startswith(W), judgment=judgment, outTok=t["timing"].get("outputTokens") or 0)
    r["CE"] = (not d) and r["corr"] <= 1.5; return r
ROWS = {}   # (seed, arm) -> {id: row}
for s in (42, 43):
    F, K = {}, {}
    fill = {"F": jby(f"{CB}/judge/S{s}/F"), "K": jby(f"{CB}/judge/S{s}/K")}
    for i in ids:
        if s == 42:
            a = r42["rows"]["ALL"][i]; k = r42["rows"]["control"][i]
            F[i] = rowof(TF[42][i], a, "s42-" + a["judgment"]); K[i] = dict(rowof(dict(answer=dict(text=pool[i]["text"], declined=pool[i].get("declined")), timing=dict(outputTokens=k.get("outTok"))), k, "control"))
        else:
            a = r43["items"][i]["ALL"]; k = r43["items"][i]["ctl"]
            for arm, D, T, x in (("F", F, TF[43], a), ("K", K, TK[43], k)):
                if x["judgment"] == "proxy" and i in fill[arm] and len(fill[arm][i]) == 2: D[i] = rowof(T[i], jrow(fill[arm], i), "judged-mine")
                else:
                    D[i] = rowof(T[i], x, x["judgment"])
                    if x["judgment"] == "proxy": D[i]["declined"] = bool(x.get("declined")); D[i]["warned"] = bool(x.get("warned")); D[i]["CE"] = (not D[i]["declined"]) and D[i]["corr"] <= 1.5
    ROWS[(s, "F")] = F; ROWS[(s, "K")] = K
# cache of every known judged (id, text) -> row source, to reuse for C
cache = {}
TG = ld(CM + "/compose/screen/traces/cmp-G-K10-main-s42.traces.jsonl")
for i in ids: cache[(i, TG[i]["answer"]["text"])] = r42["rows"]["G"][i]
for s in (42, 43):
    for arm in ("F", "K"):
        for i in ids:
            r = ROWS[(s, arm)][i]
            if r["judgment"] != "proxy": cache.setdefault((i, r["text"]), r)
byC = {s: jby(f"{CB}/judge/S{s}/C") for s in (42, 43)}
for s in (42, 43):
    C = {}; F = ROWS[(s, "F")]; K = ROWS[(s, "K")]
    for i in ids:
        t = TC[s][i]; txt = t["answer"]["text"]
        if txt == F[i]["text"]: C[i] = dict(F[i], judgment="reused-F", outTok=t["timing"].get("outputTokens") or 0)
        elif i in byC[s] and len(byC[s][i]) == 2: C[i] = rowof(t, jrow(byC[s], i), "judged")
        elif txt == K[i]["text"] and K[i]["judgment"] != "proxy": C[i] = dict(K[i], judgment="reused-K")
        elif (i, txt) in cache:
            c = cache[(i, txt)]; C[i] = rowof(t, c, "cache")
        else: C[i] = dict(F[i], judgment="UNJUDGED-imputed-F", text=txt)
    ROWS[(s, "C")] = C
def U(R, xs): return sum(0 if R[i]["declined"] else R[i]["s"] for i in xs) / sum(R[i]["sref"] for i in xs)
def mean(R, xs, k, nn=3):
    v = [R[i][k] for i in xs if R[i].get(k) is not None]; return round(sum(v) / len(v), nn) if v else None
def summ(R, xs):
    nd = [i for i in xs if not R[i]["declined"]]; ce = [i for i in nd if R[i]["corr"] <= 1.5]
    return dict(n=len(xs), U=round(U(R, xs), 4), corr=mean(R, xs, "corr"), CE=len(ce), CE_unwarned=sum(1 for i in ce if not R[i]["warned"]), warned=sum(1 for i in xs if R[i]["warned"]), declined=sum(1 for i in xs if R[i]["declined"]), outTok=mean(R, xs, "outTok", 2))
def boot(xs, f, B=2000):
    r = random.Random(11); v = []
    for _ in range(B): v.append(f([r.choice(xs) for _ in xs]))
    v.sort(); return [round(v[int(0.025 * B)], 4), round(v[int(0.975 * B) - 1], 4)]
def pair(a, b, xs):
    if not xs: return dict(n=0)
    f = lambda s: U(a, s) - U(b, s); g = lambda s: sum(a[i]["corr"] - b[i]["corr"] for i in s) / len(s)
    return dict(n=len(xs), d=round(f(xs), 4), ci=boot(xs, f), dcorr=round(g(xs), 4), dcorr_ci=boot(xs, g))
res = dict(per_seed={})
CHG = {}
for s in (42, 43):
    F, K, C = ROWS[(s, "F")], ROWS[(s, "K")], ROWS[(s, "C")]
    chg = [i for i in ids if TC[s][i]["answer"]["text"] != TF[s][i]["answer"]["text"]]; CHG[s] = chg
    unj = [i for i in chg if C[i]["judgment"].startswith("UNJUDGED")]
    fproxy = [i for i in chg if F[i]["judgment"] == "proxy"]; kproxy = [i for i in ids if K[i]["judgment"] == "proxy"]
    p = dict(text_differs_vs_SEFIXALL=len(chg), unjudged_changed=unj, F_proxy_among_changed=fproxy, K_proxy_rows=len(kproxy), C_judgment=dict(collections.Counter(C[i]["judgment"] for i in ids)),
             all97=dict(K=summ(K, ids), F=summ(F, ids), C=summ(C, ids)), changed=dict(F=summ(F, chg), C=summ(C, chg)),
             vs_F_changed=pair(C, F, chg), vs_F_all97=pair(C, F, ids), vs_K_all97=pair(C, K, ids), F_vs_K_all97=pair(F, K, ids))
    p["by_source"] = {}
    for sc in ("v0.1", "cooking", "money"):
        al = [i for i in ids if src_of(i) == sc]; xs = [i for i in chg if src_of(i) == sc]
        p["by_source"][sc] = dict(n=len(al), changed=len(xs), K=summ(K, al), F=summ(F, al), C=summ(C, al), vs_K=pair(C, K, al), vs_F_changed=pair(C, F, xs) if xs else None)
    p["CE_new_vs_F"] = [i for i in chg if C[i]["CE"] and not F[i]["CE"]]; p["CE_fixed_vs_F"] = [i for i in chg if F[i]["CE"] and not C[i]["CE"]]
    p["corr_up_ge1"] = [i for i in chg if C[i]["corr"] - F[i]["corr"] >= 1]; p["corr_down_ge1"] = [i for i in chg if F[i]["corr"] - C[i]["corr"] >= 1]
    p["warned_F_to_C"] = dict(newly_warned=[i for i in chg if C[i]["warned"] and not F[i]["warned"]], newly_unwarned=[i for i in chg if F[i]["warned"] and not C[i]["warned"]])
    res["per_seed"][s] = p
def prow(a, b):
    ea = 0 if a["declined"] else a["s"]; eb = 0 if b["declined"] else b["s"]
    return dict(s=(ea + eb) / 2, sref=(a["sref"] + b["sref"]) / 2, corr=(a["corr"] + b["corr"]) / 2, declined=False)
P = {arm: {i: prow(ROWS[(42, arm)][i], ROWS[(43, arm)][i]) for i in ids} for arm in ("K", "F", "C")}
union = [i for i in ids if i in set(CHG[42]) or i in set(CHG[43])]
pooled = dict(vs_K_all97=pair(P["C"], P["K"], ids), vs_F_all97=pair(P["C"], P["F"], ids), vs_F_changed_union=dict(n_union=len(union), **pair(P["C"], P["F"], union)), F_vs_K_all97=pair(P["F"], P["K"], ids),
              U=dict(K=round(U(P["K"], ids), 4), F=round(U(P["F"], ids), 4), C=round(U(P["C"], ids), 4)))
pooled["by_source"] = {sc: dict(n=sum(1 for i in ids if src_of(i) == sc), vs_K=pair(P["C"], P["K"], [i for i in ids if src_of(i) == sc]), F_vs_K=pair(P["F"], P["K"], [i for i in ids if src_of(i) == sc])) for sc in ("v0.1", "cooking", "money")}
ceu = lambda arm: {s: res["per_seed"][s]["all97"][{"K": "K", "F": "F", "C": "C"}[arm]]["CE_unwarned"] for s in (42, 43)}
pooled["CE_unwarned"] = {arm: dict(per_seed=ceu(arm), sum=sum(ceu(arm).values())) for arm in ("K", "F", "C")}
pooled["CE"] = {arm: {s: res["per_seed"][s]["all97"][arm]["CE"] for s in (42, 43)} for arm in ("K", "F", "C")}
# chunk-level 2x2 from the replay read (flags: K3 control replay B0, SEFIX-ALL replay, COMBINED replay)
rr = json.load(open(CB + "/replays-read.json")); fk, ff, fc = rr["flags_k3"], rr["flags_sefixall"], rr["flags_combined"]
keyed = [i for i in ids if i in fk and i in fc]
rsf = set(rr.get("readseq_codes_fired", []))
cells = collections.defaultdict(list)
for i in keyed: cells[("K3:" + ("P" if fk[i]["chunk"] else "A")) + " | COMBINED:" + ("P" if fc[i]["chunk"] else "A")].append(i)
def cellrow(xs):
    d = dict(n=len(xs), ids=xs, U_K=round(U(P["K"], xs), 4), U_F=round(U(P["F"], xs), 4), U_C=round(U(P["C"], xs), 4), corr_K=mean(P["K"], xs, "corr"), corr_F=mean(P["F"], xs, "corr"), corr_C=mean(P["C"], xs, "corr"))
    d["C_vs_K"] = {k: v for k, v in pair(P["C"], P["K"], xs).items() if k in ("d", "ci")}; d["C_vs_F"] = {k: v for k, v in pair(P["C"], P["F"], xs).items() if k in ("d", "ci")}; return d
pooled["chunk_2x2"] = {k: cellrow(v) for k, v in sorted(cells.items())}
rd1_items = [i for i in ids if i in rsf]
pooled["chunk_2x2_split_RD1_fired"] = {}
for k, v in sorted(cells.items()):
    for lab, sel in (("RD1 fired", [i for i in v if i in rsf]), ("RD1 silent", [i for i in v if i not in rsf])):
        if sel: pooled["chunk_2x2_split_RD1_fired"][k + " | " + lab] = cellrow(sel)
pooled["delivery"] = dict(summary=rr["summary"], flips_vs_SEFIXALL=rr.get("delivery_flips_vs_SEFIXALL"), contexts_changed_by_RD1=rr.get("contexts_changed_by_RD1", {}).get("n"), identity_off=(rr.get("identity_off_vs_SEFIXALL") or {}).get("all_four_identical"))
newly = sorted(i for i in keyed if fc[i]["chunk"] and not fk[i]["chunk"])
pooled["newly_delivered_chunk_vs_K3"] = dict(n=len(newly), vs_K=pair(P["C"], P["K"], newly) if newly else None, vs_F=pair(P["C"], P["F"], newly) if newly else None, corr=dict(K=mean(P["K"], newly, "corr"), F=mean(P["F"], newly, "corr"), C=mean(P["C"], newly, "corr")))
# frozen rule
a, b = pooled["vs_K_all97"], pooled["vs_F_changed_union"]
cu = pooled["CE_unwarned"]
rule = dict(pooled_dU_vs_K3_all97_ge_0_03=a["d"] >= 0.03, pooled_dU_vs_K3_ci_low_gt_0=a["ci"][0] > 0, dU_vs_SEFIXALL_changed_ge_0=b["d"] >= 0, CE_unwarned_not_above_SEFIXALL=cu["C"]["sum"] <= cu["F"]["sum"],
            CE_unwarned_not_above_SEFIXALL_each_seed=all(cu["C"]["per_seed"][s] <= cu["F"]["per_seed"][s] for s in (42, 43)))
rule["PASS"] = rule["pooled_dU_vs_K3_all97_ge_0_03"] and rule["pooled_dU_vs_K3_ci_low_gt_0"] and rule["dU_vs_SEFIXALL_changed_ge_0"] and rule["CE_unwarned_not_above_SEFIXALL"]
res["pooled"] = pooled; res["rule"] = rule
res["rows"] = {f"s{s}_{arm}": {i: {k: v for k, v in r.items() if k != "text"} for i, r in ROWS[(s, arm)].items()} for s in (42, 43) for arm in ("K", "F", "C")}
res["texts_changed"] = {f"s{s}": {i: dict(F=ROWS[(s, "F")][i]["text"], C=ROWS[(s, "C")][i]["text"]) for i in CHG[s]} for s in (42, 43)}
json.dump(res, open(CM + "/combined/answers-combined.json", "w"), indent=1, ensure_ascii=False)
# markdown table
L = ["| seed | set | arm | U | corr | CE | CE unwarned | warned | declined |", "|---|---|---|---|---|---|---|---|---|"]
for s in (42, 43):
    p = res["per_seed"][s]
    for lab, blk, arms in (("all 97", p["all97"], ("K", "F", "C")), (f"changed vs SEFIX-ALL ({p['text_differs_vs_SEFIXALL']})", p["changed"], ("F", "C"))):
        for arm in arms:
            x = blk[arm]; L.append(f"| {s} | {lab} | {'K3 control' if arm == 'K' else 'SEFIX-ALL' if arm == 'F' else 'COMBINED'} | {x['U']} | {x['corr']} | {x['CE']} | {x['CE_unwarned']} | {x['warned']} | {x['declined']} |")
open(CM + "/combined/answers-combined.md", "w").write("\n".join(L) + "\n\n```json\n" + json.dumps(dict(rule=rule, pooled={k: v for k, v in pooled.items() if k in ("U", "vs_K_all97", "vs_F_all97", "vs_F_changed_union", "F_vs_K_all97", "CE_unwarned", "CE")}), indent=1) + "\n```\n")
print("\n".join(L)); print(json.dumps(dict(rule=rule, pooled={k: v for k, v in pooled.items() if k not in ("chunk_2x2", "chunk_2x2_split_RD1_fired", "delivery", "by_source")}), indent=0)[:5000])
