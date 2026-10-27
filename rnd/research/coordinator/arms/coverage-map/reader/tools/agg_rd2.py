#!/usr/bin/env python3
"""RD2 (READ-GROUND) aggregate, 0 LLM. usage: python3 -I agg_rd2.py RUN TAG   -> reader/RD2[.TAG].json (TAG empty for the headline run)
Arm = reader/traces/RUN.traces.jsonl; base = F1b (sefix/ans-traces + sefix/answers-f1b.json rows); control = K3 pool-K1 (rows in answers-f1b.json 'control').
RD2 row = F1b row if text equals F1b's, else control row if equal to control's, else ARM-G row if equal, else the arm's own Haiku judgment (reader/judge/RUN).
Definitions as sefix/ans-tools/agg_f1b.py: ratio-of-sums U, corr = mean over both orders, CE = not declined and corr <= 1.5, warned = engine warning line first. Bootstrap: items, B 2000, seed 11.
Frozen rule (READER-criterion.md, sha f361f738): READS iff dU vs F1b on changed >= +0.02 with CI low > -0.01 AND CE-unwarned (all 97) not up AND target items' mean correctness +0.5 or better;
LEVER-CANDIDATE iff additionally dU vs the K3 control over all 97 >= +0.02 with CI low > -0.01."""
import json, glob, random, sys
A = "<workspace>/rnd/research/coordinator/arms"; CM = A + "/coverage-map"; RD = CM + "/reader"; SF = CM + "/sefix"
RUN = sys.argv[1]; TAG = sys.argv[2] if len(sys.argv) > 2 else ""
W = "Not found in this phone's offline library. From the model's memory, may be wrong:"
TARGETS = ["st-qa-money-se-003", "vit-cry-001", "lan-cmp-004", "lan-exp-002", "st-qa-cooking-se-012"]
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
ids = open(A + "/lp-screens/main-97.ids").read().split()
FA = json.load(open(SF + "/answers-f1b.json")); RC, RG, RF = FA["rows"]["control"], FA["rows"]["G"], FA["rows"]["F1b"]
TF = {t["itemId"]: t for t in rd(SF + "/ans-traces/f1b-main-s42.traces.jsonl")}; TG = {t["itemId"]: t for t in rd(CM + "/compose/screen/traces/cmp-G-K10-main-s42.traces.jsonl")}
ctl = json.load(open(A + "/null-cal/control/pool-K1.json"))["items"]
TR = {t["itemId"]: t for t in rd(f"{RD}/traces/{RUN}.traces.jsonl")}
by = {}
for f in sorted(glob.glob(f"{RD}/judge/{RUN}/*.judgments.jsonl")):
    for r in rd(f):
        if r.get("ok") is True: by.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
dim = lambda m, k: sum(m[k].values()) / 3
def jrow(i):
    ms = list(by[i].values()); return dict(s=sum(dim(m, "boar") for m in ms) / 2, sref=sum(dim(m, "ref") for m in ms) / 2, corr=sum(m["boar"]["correctness"] for m in ms) / 2, use=sum(m["boar"]["usefulness"] for m in ms) / 2)
chg = [i for i in ids if TR[i]["answer"]["text"] != TF[i]["answer"]["text"]]
R = {}; unjudged = []
for i in ids:
    t = TR[i]; txt = t["answer"]["text"] or ""; d = bool(t["answer"].get("declined"))
    if txt == TF[i]["answer"]["text"]: j = {k: RF[i][k] for k in ("s", "sref", "corr", "use")}; src = "reused-F1b"
    elif txt == ctl[i]["text"]: j = {k: RC[i][k] for k in ("s", "sref", "corr", "use")}; src = "control-row"
    elif txt == TG[i]["answer"]["text"]: j = {k: RG[i][k] for k in ("s", "sref", "corr", "use")}; src = "ARM-G-row"
    elif i in by and len(by[i]) == 2: j = jrow(i); src = "judged"
    else: unjudged.append(i); continue
    R[i] = dict(j, text=txt, declined=d, warned=txt.startswith(W), CE=(not d and j["corr"] <= 1.5), judgment=src, reasonCodes=t["route"]["reasonCodes"], cited=t["answer"]["cited"])
if unjudged: print("UNJUDGED", unjudged); json.dump(unjudged, open(f"{RD}/RD2{'.'+TAG if TAG else ''}.unjudged.json", "w")); sys.exit(2)
def U(src, xs): return sum(0 if src[i]["declined"] else src[i]["s"] for i in xs) / sum(src[i]["sref"] for i in xs)
def mean(src, xs, k, nn=3): v = [src[i][k] for i in xs if src[i].get(k) is not None]; return round(sum(v) / len(v), nn) if v else None
def summ(src, xs):
    nd = [i for i in xs if not src[i]["declined"]]; ce = [i for i in nd if src[i]["corr"] <= 1.5]
    return dict(n=len(xs), U=round(U(src, xs), 4), corr=mean(src, xs, "corr"), use=mean(src, xs, "use"), CE=len(ce), CE_unwarned=sum(1 for i in ce if not src[i]["warned"]), warned=sum(1 for i in xs if src[i]["warned"]), declined=sum(1 for i in xs if src[i]["declined"]))
def boot(xs, f, B=2000):
    r = random.Random(11); v = sorted(f([r.choice(xs) for _ in xs]) for _ in range(B)); return [round(v[int(0.025 * B)], 4), round(v[int(0.975 * B) - 1], 4)]
def pair(sa, sb, xs):
    if not xs: return dict(n=0, d=0.0, ci=[0.0, 0.0], dcorr=0.0)
    f = lambda s: U(sa, s) - U(sb, s); g = lambda s: sum(sa[i]["corr"] - sb[i]["corr"] for i in s) / len(s)
    return dict(n=len(xs), d=round(f(xs), 4), ci=boot(xs, f), dcorr=round(g(xs), 4), dcorr_ci=boot(xs, g))
res = dict(run=RUN, bar=TR[ids[0]]["config"].get("arm"), n=len(ids), changed_n=len(chg), changed_ids=chg, judged_rows=sum(1 for i in ids if R[i]["judgment"] == "judged"))
res["all97"] = dict(control=summ(RC, ids), F1b=summ(RF, ids), RD2=summ(R, ids))
res["changed"] = dict(F1b=summ(RF, chg), RD2=summ(R, chg), control=summ(RC, chg))
res["vs_F1b_changed"] = pair(R, RF, chg); res["vs_F1b_all97"] = pair(R, RF, ids); res["vs_control_all97"] = pair(R, RC, ids); res["F1b_vs_control_all97"] = pair(RF, RC, ids)
res["targets"] = {i: dict(F1b_corr=RF[i]["corr"], RD2_corr=R[i]["corr"], F1b_warned=RF[i]["warned"], RD2_warned=R[i]["warned"], changed=i in chg, reason=[x for x in R[i]["reasonCodes"] if "ground" in x and "citations" in x or x.startswith("citations:")]) for i in TARGETS}
tb = sum(RF[i]["corr"] for i in TARGETS) / len(TARGETS); ta = sum(R[i]["corr"] for i in TARGETS) / len(TARGETS); res["targets_mean_corr"] = dict(F1b=round(tb, 3), RD2=round(ta, 3), delta=round(ta - tb, 3))
nh = FA["factpresent_2x2_all97"]["G_P__F_P"]["ids"]; res["no_harm_set_G_P_F_P"] = dict(n=len(nh), changed=[i for i in nh if i in chg], F1b=summ(RF, nh), RD2=summ(R, nh), **{k: v for k, v in pair(R, RF, nh).items() if k in ("d", "ci")})
res["per_item"] = {i: dict(F1b=dict(corr=RF[i]["corr"], s=round(RF[i]["s"], 3), warned=RF[i]["warned"], CE=RF[i]["CE"]), RD2=dict(corr=R[i]["corr"], s=round(R[i]["s"], 3), warned=R[i]["warned"], CE=R[i]["CE"], judgment=R[i]["judgment"]), grounded=[x for x in R[i]["reasonCodes"] if x.startswith("citations:grounded")], F1b_text=TF[i]["answer"]["text"], RD2_text=R[i]["text"]) for i in chg}
res["grounded_items_all"] = [i for i in ids if any(x.startswith("citations:grounded") for x in R[i]["reasonCodes"])]
res["CE_new_unwarned"] = [i for i in ids if R[i]["CE"] and not R[i]["warned"] and not (RF[i]["CE"] and not RF[i]["warned"])]
res["CE_removed_unwarned"] = [i for i in ids if RF[i]["CE"] and not RF[i]["warned"] and not (R[i]["CE"] and not R[i]["warned"])]
res["warned_to_cited"] = [i for i in chg if RF[i]["warned"] and not R[i]["warned"]]
a = res["vs_F1b_changed"]; b = res["vs_control_all97"]
ce_up = res["all97"]["RD2"]["CE_unwarned"] > res["all97"]["F1b"]["CE_unwarned"]
c1 = len(chg) > 0 and a["d"] >= 0.02 and a["ci"][0] > -0.01; c2 = not ce_up; c3 = res["targets_mean_corr"]["delta"] >= 0.5; c4 = b["d"] >= 0.02 and b["ci"][0] > -0.01
res["rule"] = dict(dU_changed_ge_0_02_cilow_gt_minus_0_01=c1, CE_unwarned_not_up=c2, targets_corr_plus_0_5=c3, vs_control_all97_dU_ge_0_02_cilow_gt_minus_0_01=c4)
res["verdict"] = "LEVER-CANDIDATE" if (c1 and c2 and c3 and c4) else ("READS" if (c1 and c2 and c3) else "no")
out = f"{RD}/RD2{'.' + TAG if TAG else ''}.json"; json.dump(res, open(out, "w"), indent=1, ensure_ascii=False)
print(json.dumps({k: v for k, v in res.items() if k not in ("per_item",)}, indent=0, ensure_ascii=False)[:7000])
