# PARA135 set A aggregation (0 LLM). python3 -I tools/agg_a.py (run from arms/para135). Estimates weight sampled strata by their sizes (criterion).
import json, sys, math, collections, hashlib, numpy as np
D = "<workspace>/rnd/research/coordinator/arms/para135/"; T27 = D + "../topics27/"
sys.path.insert(0, D + "tools"); from para import paragraphs
assert hashlib.sha256(open(D + "PARA135-criterion.md", "rb").read()).hexdigest() == open(D + "PARA135-criterion.sha256").read().split()[0]
P = json.load(open(D + "judge/prep.json")); AU = {}
for l in open(D + "judge/audit.jsonl"):
    r = json.loads(l)
    if r["ok"]: AU[r["key"]] = r
POS = ["1", "2", "3", "4", "5", "6+"]
def wilson(k, n):
    if n == 0: return None
    z = 1.96; p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 3), round(c + h, 3)]
def table(units, lab):
    st = collections.defaultdict(list); [st[u["pos"]].append(u) for u in units]
    res = {}; inv_est_tot = 0; uns_est_tot = 0; N = len(units)
    for p in POS:
        us = st.get(p, []); au = [lab[u["key"]] for u in us if u["key"] in lab]; m = len(au)
        uns = sum(a["label"] == "UNSUPPORTED" for a in au); par = sum(a["label"] == "PARTIAL" for a in au)
        inv = sum(1 for a in au if a["label"] in ("UNSUPPORTED", "PARTIAL") and a["invented_specific"])
        inv_est = inv * len(us) / m if m else 0; inv_est_tot += inv_est; uns_est_tot += (uns / m * len(us) if m else 0)
        res[p] = dict(sentences=len(us), audited=m, unsupported=uns, partial=par, invented=inv, unsup_share=round(uns / m, 3) if m else None, unsup_ci=wilson(uns, m),
                      inv_per_audited=round(inv / m, 3) if m else None, inv_est=round(inv_est, 1), num_absent=sum(u.get("num_absent", 0) for u in us))
    for p in POS: res[p]["share_of_invented"] = round(res[p]["inv_est"] / inv_est_tot, 3) if inv_est_tot else None
    au = [lab[u["key"]] for u in units if u["key"] in lab]
    tot = dict(sentences=N, audited=len(au), unsupported_sample=sum(a["label"] == "UNSUPPORTED" for a in au), partial_sample=sum(a["label"] == "PARTIAL" for a in au),
               invented_sample=sum(1 for a in au if a["label"] in ("UNSUPPORTED", "PARTIAL") and a["invented_specific"]),
               unsup_share_est=round(uns_est_tot / N, 3) if N else None, invented_est=round(inv_est_tot, 1), num_absent=sum(u.get("num_absent", 0) for u in units))
    tot["unsup_share_sample"] = round(tot["unsupported_sample"] / len(au), 3) if au else None
    early = [lab[u["key"]] for u in units if u["key"] in lab and u["pos"] in ("1", "2")]; late = [lab[u["key"]] for u in units if u["key"] in lab and u["pos"] in ("3", "4", "5")]
    ir = lambda xs: round(sum(1 for a in xs if a["label"] in ("UNSUPPORTED", "PARTIAL") and a["invented_specific"]) / len(xs), 3) if xs else None
    us_ = lambda xs: round(sum(a["label"] == "UNSUPPORTED" for a in xs) / len(xs), 3) if xs else None
    tot.update(inv_rate_pos12=ir(early), inv_rate_pos345=ir(late), unsup_pos12=us_(early), unsup_pos345=us_(late),
               share_invented_pos345=round(sum(res[p]["inv_est"] for p in ("3", "4", "5")) / inv_est_tot, 3) if inv_est_tot else None)
    return res, tot
out = {"arms": {}}
for a, N in (("p1", 1), ("p3", 3), ("p5", 5)):
    X = P["arms"][a]; it = X["items"]; ot = np.array([i["out_tokens"] or 0 for i in it]); ms = np.array([i["total_ms"] or 0 for i in it])
    res, tot = table(X["units"], AU)
    tot.update(compliance=sum(i["n_para"] == N for i in it), compliance_pm1=sum(abs(i["n_para"] - N) <= 1 for i in it), paras_hist=dict(sorted(collections.Counter(i["n_para"] for i in it).items())),
               banner=sum(bool(i["banner"]) for i in it), out_tokens_p50=float(np.median(ot)), out_tokens_mean=round(float(ot.mean()), 1), at_cap=int((ot >= 1023).sum()),
               ms_p50=round(float(np.median(ms))), words_p50=float(np.median([i["words"] for i in it])), declined=sum(bool(i["declined"]) for i in it),
               persona_sha=it[0]["persona_sha"][:8], ctx_src=dict(collections.Counter(i["ctx_src"] for i in it)), budget=P["budget"][a])
    out["arms"][a] = dict(total=tot, by_pos=res, per_topic={i["key"]: dict(n_para=i["n_para"], n_sent=i["n_sent"], banner=bool(i["banner"]), out_tokens=i["out_tokens"]) for i in it})
# secondary: TOPICS27 Detailed by position (0 calls): per-sentence labels + sensitivity re-audit of its batched units
tr = {json.loads(l)["itemId"]: json.loads(l) for l in open(T27 + "gen/traces.jsonl")}
lab = {}
for l in open(T27 + "judge/audit.jsonl"):
    r = json.loads(l)
    if r["ok"]: lab[r["key"]] = r
for l in open(T27 + "judge-succinct/sens-detailed.jsonl"):
    r = json.loads(l)
    if r["ok"]: lab[r["key"]] = r
pp = json.load(open(T27 + "judge/prep.json")); su = {u["key"]: u for u in pp["units"]}
units = []; dpar = []
for k, t in tr.items():
    b, ps = paragraphs(t["answer"]["text"] or ""); dpar.append(len(ps)); idx = 0
    for pi, s_ in enumerate(ps, 1):
        for s in s_:
            key = f"{k}#{idx}"; assert su[key]["sentence"] == s, key
            units.append(dict(key=key, pos=str(pi) if pi <= 5 else "6+")); idx += 1
res, tot = table(units, lab); tot["paras_hist"] = dict(sorted(collections.Counter(dpar).items()))
out["detailed_topics27"] = dict(total=tot, by_pos=res, note="TOPICS27 Detailed, maxTokens 512, 3-5 paragraphs; labels = per-sentence audit + sens-detailed re-audit of batched units")
pred = {}
s = {a: out["arms"][a]["total"]["unsup_share_est"] for a in ("p1", "p3", "p5")}
pred["P1_monotone"] = dict(hit=s["p1"] < s["p3"] < s["p5"], values=s)
t5 = out["arms"]["p5"]["total"]
pred["P2_late_invented"] = dict(hit=bool(t5["share_invented_pos345"] is not None and t5["share_invented_pos345"] > 0.5 and (t5["inv_rate_pos345"] or 0) > (t5["inv_rate_pos12"] or 0)),
    share_pos345=t5["share_invented_pos345"], rate12=t5["inv_rate_pos12"], rate345=t5["inv_rate_pos345"])
out["predictions_setA"] = pred
json.dump(out, open(D + "aggregates/setA.json", "w"), indent=1)
for a in ("p1", "p3", "p5"):
    t = out["arms"][a]["total"]; print(a, {k: t[k] for k in ("sentences", "audited", "unsup_share_est", "unsup_share_sample", "invented_sample", "invented_est", "compliance", "banner", "out_tokens_p50", "at_cap", "ms_p50", "words_p50")})
    for p in POS: print("   ", p, out["arms"][a]["by_pos"][p])
print("D27", {k: tot[k] for k in ("sentences", "audited", "unsup_share_est", "invented_est")}); [print("   ", p, res[p]) for p in POS]
print(json.dumps(pred, indent=1))
