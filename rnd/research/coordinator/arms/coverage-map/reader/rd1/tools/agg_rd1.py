#!/usr/bin/env python3
"""RD1 (READ-SEQ) aggregate, 0 LLM. python3 -I agg_rd1.py -> ../../RD1.json, ../../RD1.md
Rows: F1b rows from sefix/answers-f1b.json (control, ARM-G, F1b). RD1 row = F1b row if the RD1 answer text equals the F1b text; else the Haiku judgment of this run (reader/rd1/judge, judge.v1, both orders);
else (changed but not judged because of the cap) the F1b row, reported as left. Definitions as sefix/ans-tools/agg_f1b.py (ratio-of-sums U, CE = not declined and corr <= 1.5, warned = engine warning line first). Bootstrap: items, B 2000, seed 11."""
import json, glob, random, re, collections
A = "<workspace>/rnd/research/coordinator/arms"; CM = A + "/coverage-map"; SF = CM + "/sefix"; RD = CM + "/reader/rd1"; OUT = CM + "/reader"
W = "Not found in this phone's offline library. From the model's memory, may be wrong:"
TARGETS = "st-qa-money-se-010 lan-hlt-003 lan-rsn-001 vit-hlt-003 st-qa-cooking-se-008 st-qa-cooking-se-001 st-qa-money-se-018 st-qa-cooking-se-012".split()
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
ld = lambda p: {json.loads(l)["itemId"]: json.loads(l) for l in open(p) if l.strip()}
ids = open(A + "/lp-screens/main-97.ids").read().split()
F = json.load(open(SF + "/answers-f1b.json")); ROWS = F["rows"]
TF = ld(SF + "/ans-traces/f1b-main-s42.traces.jsonl"); TR = ld(RD + "/traces/rd1-main-s42.traces.jsonl")
ctl = json.load(open(A + "/null-cal/control/pool-K1.json"))["items"]
def jby(JD):
    by = {}
    for f in sorted(glob.glob(JD + "/*.judgments.jsonl")):
        for r in rd(f):
            if r.get("ok") is True: by.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
    return by
BY = jby(RD + "/judge"); dim = lambda m, k: sum(m[k].values()) / 3
def jrow(i):
    ms = list(BY[i].values())
    return dict(s=sum(dim(m, "boar") for m in ms) / 2, sref=sum(dim(m, "ref") for m in ms) / 2, corr=sum(m["boar"]["correctness"] for m in ms) / 2, use=sum(m["boar"]["usefulness"] for m in ms) / 2)
chg_all = sorted(i for i in ids if TR[i]["answer"]["text"] != TF[i]["answer"]["text"])
RR, src = {}, {}
for i in ids:
    t = TR[i]; txt = t["answer"]["text"]; d = bool(t["answer"].get("declined")); fr = ROWS["F1b"][i]
    if txt == TF[i]["answer"]["text"]: j = {k: fr[k] for k in ("s", "sref", "corr", "use")}; src[i] = "reused-F1b"
    elif i in BY and len(BY[i]) == 2: j = jrow(i); src[i] = "judged"
    else: j = {k: fr[k] for k in ("s", "sref", "corr", "use")}; src[i] = "LEFT-unjudged(F1b row)"
    RR[i] = dict(j, declined=(d if src[i] == "judged" or txt == TF[i]["answer"]["text"] else fr["declined"]), warned=txt.startswith(W), CE=None, outTok=t["timing"].get("outputTokens") or 0, totalMs=t["timing"].get("totalMs") or 0)
    RR[i]["CE"] = (not RR[i]["declined"] and RR[i]["corr"] <= 1.5)
    if src[i].startswith("LEFT"): RR[i]["warned"] = fr["warned"]
judged = [i for i in ids if src[i] == "judged"]; left = [i for i in ids if src[i].startswith("LEFT")]
FR, CR = ROWS["F1b"], ROWS["control"]
U = lambda S, xs: sum(0 if S[i]["declined"] else S[i]["s"] for i in xs) / sum(S[i]["sref"] for i in xs)
mean = lambda S, xs, k: round(sum(S[i][k] for i in xs) / len(xs), 3) if xs else None
def summ(S, xs):
    nd = [i for i in xs if not S[i]["declined"]]; ce = [i for i in nd if S[i]["corr"] <= 1.5]
    return dict(n=len(xs), U=round(U(S, xs), 4), corr=mean(S, xs, "corr"), CE=len(ce), CE_unwarned=sum(1 for i in ce if not S[i]["warned"]), warned=sum(1 for i in xs if S[i]["warned"]), declined=sum(1 for i in xs if S[i]["declined"]))
def boot(xs, f, B=2000):
    r = random.Random(11); v = sorted(f([r.choice(xs) for _ in xs]) for _ in range(B)); return [round(v[int(0.025 * B)], 4), round(v[int(0.975 * B) - 1], 4)]
def pair(Sa, Sb, xs):
    if not xs: return dict(n=0)
    f = lambda s: U(Sa, s) - U(Sb, s); g = lambda s: sum(Sa[i]["corr"] - Sb[i]["corr"] for i in s) / len(s)
    return dict(n=len(xs), d=round(f(xs), 4), ci=boot(xs, f), dcorr=round(g(xs), 4), dcorr_ci=boot(xs, g))
chg = [i for i in judged]  # changed and judged (text differs from F1b)
res = dict(n=len(ids), changed_text_vs_F1b=len(chg_all), judged=len(judged), left=left, haiku_calls=2 * len(judged), changed_ids=chg_all)
res["all97"] = dict(control=summ(CR, ids), F1b=summ(FR, ids), RD1=summ(RR, ids))
res["changed"] = dict(F1b=summ(FR, chg), RD1=summ(RR, chg), control=summ(CR, chg))
res["vs_F1b_changed"] = pair(RR, FR, chg); res["vs_F1b_all97"] = pair(RR, FR, ids); res["vs_control_all97"] = pair(RR, CR, ids); res["F1b_vs_control_all97"] = pair(FR, CR, ids)
tg = [i for i in TARGETS if i in ids]
res["targets"] = dict(ids=tg, changed=[i for i in tg if i in chg_all], corr_before=mean(FR, tg, "corr"), corr_after=mean(RR, tg, "corr"), d=round(mean(RR, tg, "corr") - mean(FR, tg, "corr"), 3),
                      per_item={i: dict(F1b=FR[i]["corr"], RD1=RR[i]["corr"], F1b_warned=FR[i]["warned"], RD1_warned=RR[i]["warned"], F1b_CE=FR[i]["CE"], RD1_CE=RR[i]["CE"], text_changed=i in chg_all, judgment=src[i]) for i in tg},
                      CE_unwarned_before=sum(1 for i in tg if FR[i]["CE"] and not FR[i]["warned"]), CE_unwarned_after=sum(1 for i in tg if RR[i]["CE"] and not RR[i]["warned"]))
res["by_source_changed"] = {}
sof = lambda i: "v0.1" if not i.startswith("st-") else ("cooking" if "cooking" in i else "money")
for s in ("v0.1", "cooking", "money"):
    xs = [i for i in chg if sof(i) == s]
    if xs: res["by_source_changed"][s] = dict(F1b=summ(FR, xs), RD1=summ(RR, xs), **{k: v for k, v in pair(RR, FR, xs).items()})
res["corr_up_ge1"] = [i for i in chg if RR[i]["corr"] - FR[i]["corr"] >= 1]; res["corr_down_ge1"] = [i for i in chg if FR[i]["corr"] - RR[i]["corr"] >= 1]
res["CE_new"] = [i for i in chg if RR[i]["CE"] and not FR[i]["CE"]]; res["CE_fixed"] = [i for i in chg if FR[i]["CE"] and not RR[i]["CE"]]
res["CE_new_unwarned"] = [i for i in res["CE_new"] if not RR[i]["warned"]]; res["CE_fixed_unwarned"] = [i for i in res["CE_fixed"] if not FR[i]["warned"]]
# sanity
def loop(txt):
    w = txt.split(); c = collections.Counter(tuple(w[k:k + 6]) for k in range(len(w) - 5)); return any(v >= 3 for v in c.values())
det = lambda t: (t["timing"].get("outputTokens") or 0) == 0 or not any(r.startswith("generate:user-model") for r in t["route"]["reasonCodes"])
dets = [i for i in ids if det(TF[i])]
res["sanity"] = dict(rows=len(TR), missing=[i for i in ids if i not in TR], empty=[i for i in ids if not (TR[i]["answer"]["text"] or "").strip()], loops=[i for i in ids if loop(TR[i]["answer"]["text"] or "")], errors=[i for i in ids if TR[i].get("error")],
                     det_items=len(dets), det_text_identical_to_F1b=sum(TR[i]["answer"]["text"] == TF[i]["answer"]["text"] for i in dets), det_text_diff=[i for i in dets if TR[i]["answer"]["text"] != TF[i]["answer"]["text"]],
                     mean_out_tok=round(sum(TR[i]["timing"].get("outputTokens") or 0 for i in ids) / len(ids), 2), F1b_mean_out_tok=round(sum(TF[i]["timing"].get("outputTokens") or 0 for i in ids) / len(ids), 2),
                     mean_total_ms=round(sum(TR[i]["timing"].get("totalMs") or 0 for i in ids) / len(ids)), F1b_mean_total_ms=round(sum(TF[i]["timing"].get("totalMs") or 0 for i in ids) / len(ids)))
res["readseq_codes"] = {i: [c for c in TR[i]["route"]["reasonCodes"] if c.startswith("readseq:")] for i in ids if any(c.startswith("readseq:") for c in TR[i]["route"]["reasonCodes"])}
# frozen rule
a = res["vs_F1b_changed"]; b = res["vs_control_all97"]; ceu_b = res["all97"]["F1b"]["CE_unwarned"]; ceu_a = res["all97"]["RD1"]["CE_unwarned"]
rule = dict(dU_vs_F1b_changed_ge_0_02_ci_low_gt_minus_0_01=bool(a.get("n") and a["d"] >= 0.02 and a["ci"][0] > -0.01), CE_unwarned_not_up=ceu_a <= ceu_b, targets_corr_ge_plus_0_5=res["targets"]["d"] >= 0.5,
            dU_vs_K3_all97_ge_0_02_ci_low_gt_minus_0_01=bool(b["d"] >= 0.02 and b["ci"][0] > -0.01))
rule["READS"] = rule["dU_vs_F1b_changed_ge_0_02_ci_low_gt_minus_0_01"] and rule["CE_unwarned_not_up"] and rule["targets_corr_ge_plus_0_5"]
rule["LEVER_CANDIDATE"] = rule["READS"] and rule["dU_vs_K3_all97_ge_0_02_ci_low_gt_minus_0_01"]
rule["verdict"] = "LEVER-CANDIDATE" if rule["LEVER_CANDIDATE"] else ("READS" if rule["READS"] else "no")
res["rule"] = rule
res["rows"] = {n: {i: {k: v for k, v in r.items()} for i, r in S.items()} for n, S in (("F1b", FR), ("RD1", RR))}; res["judgment_source"] = src
res["texts"] = {i: dict(F1b=TF[i]["answer"]["text"], RD1=TR[i]["answer"]["text"]) for i in chg_all}
json.dump(res, open(OUT + "/RD1.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps({k: v for k, v in res.items() if k not in ("rows", "texts", "judgment_source")}, indent=0, ensure_ascii=False)[:9000])
