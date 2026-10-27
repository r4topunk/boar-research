#!/usr/bin/env python3
"""REREAD 2026-10-20: 0-call re-analysis of today's 7 LP-SCREENS stage-1 verdicts under the corrected measurement
(model-usage audit M1, M2, M4, N1; refute-1, refute-2). Never replaces a frozen verdict; post-hoc, not a decision.
Inputs (read only): arms/lp-screens/{screen-K*.json, control/aggregates, control/traces}, arms/<arm>/aggregates/<run>.json,
arms/occrag/sidecar/*.occ.jsonl. No judge calls, no generation; judgments are the frozen per-item corr values in the aggregates.
Usage: python3 -I reread.py [--json out.json]   (paths are absolute; run from anywhere)

Corrected labels per item (answer text t, frozen Haiku corr c):
  warned        = t starts with the CMP30OFF warning line (memory answer released behind it; the new default would refuse it)
  decline       = trace answer.declined, or t is an engine refusal / notice (ENGINE_DECLINE), or a model-written abstention (MODEL_DECLINE,
                  short answers only), or a warning line with no answer body. Never CE.
  CE            = not decline and c <= 1.5   (frozen threshold)
  CE-unwarned   = CE and not warned  (what the user sees in the new default mode)
  CE-warned     = CE and warned      (show-anyway mode only)
  reachable     = the item reached the answer LLM in the mini control trace (runtime.sampler.temperature present and outputTokens > 0)
Gates:
  frozen        = copied from arms/<arm>/aggregates/<run>.gate.json
  v1-corrected  = frozen rule (fixed >= ceil(0.22 * 27) = 6, sentinels worse <= 1) with the corrected CE / decline labels
  v1-reachable  = post-hoc: need = ceil(0.22 * reachable corrected control CE on problems); sentinels = live (reachable) ones only, max 1 worse
  Sentinel worse (all gates) = frozen definition: corr drop >= 1.0, or newly decline, or newly CE.
OCCRAG-decline variant: OCC abstentions are kept as declines instead of falling back to Qwen: sidecar route occ-abstain-*, and
occ-malformed-* whose OCC answer text says it lacks the information ('Not enough information', 'do not contain', status 'unanswerable').
Malformed / looped traces with a real OCC answer keep the Qwen fallback text (the only judged text). False-refusal proxy: the judge never
saw the sources, so 'source supports the answer' is read from the same-context Qwen answer (the fallback request is byte-identical to the
control): tag = unwarned|warned (did the control engine keep an on-topic source) : supported (Qwen corr >= 3.0) | ambiguous (2.0-2.5) |
not-supported (<= 1.5). False refusal = unwarned:supported. A warned item is already refused in the new default mode, so declining it costs
only the show-anyway answer.
"""
import json, math, re, sys

A = "<workspace>/rnd/research/coordinator/arms"
W = "Not found in this phone's offline library. From the model's memory, may be wrong:"
# Engine refusal and notice strings (grep of be-0cfd4a77-cut7-litepacks src/: context.ts:1385/1417/1284, geo.ts:452, answer.ts:1310ff).
ENGINE_DECLINE = re.compile(
    r"I don't have a reliable offline source on this, so I won't give health advice from memory"
    r"|offline places pack is not installed"
    r"|I didn't find (this in this phone's library|safe first-aid instructions)"
    r"|^The offline source doesn't give first-aid steps for this\. In an emergency, call your local emergency number \(911 in the US, 112 in Europe\)\.$"
    r"|N(ã|a)o encontrei isso no acervo deste celular", re.I)
# Model-written abstentions (frozen agg_run RX extended with the OCC / reader phrasings); only on short answers.
MODEL_DECLINE = re.compile(
    r"\b(i (do not|don't) know|i'?m not sure|i cannot answer|i can'?t answer|i don'?t have (enough |reliable )?information|not able to answer"
    r"|not enough information|(sources?|context|passages?) (do|does) not (contain|provide|mention)|unanswerable)\b", re.I)

RUNS = [  # arm, pack set, run id
    ("b-honest", "K0", "b-honest-K0-screen-s42"), ("greedy", "K0", "greedy-K0-screen-s42"),
    ("vendorsamp", "K0", "vendorsamp-K0-screen-s42"), ("occrag", "K0", "occrag-K0-screen-s42"),
    ("shortctx", "K1", "shortctx-K1-screen-s42"), ("quotefirst", "K1", "quotefirst-K1-screen-s42"),
    ("occrag", "K1", "occrag-K1-screen-s42")]

def is_decline(t, declined):
    body = t[len(W):].strip() if t.startswith(W) else t
    return bool(declined) or bool(ENGINE_DECLINE.search(t)) or (len(body) < 300 and bool(MODEL_DECLINE.search(body))) or body == ""

def relabel(items):
    out = {}
    for i, x in items.items():
        d = is_decline(x["text"], x["declined"]); ce = (not d) and x["corr"] <= 1.5; w = x["text"].startswith(W)
        out[i] = dict(corr=x["corr"], text=x["text"], warned=w, decline=d, CE=ce, CEu=ce and not w, CEw=ce and w)
    return out

def reachable(K):
    r = {}
    for l in open(f"{A}/lp-screens/control/traces/lpctl-{K}-screen-s42.traces.jsonl"):
        t = json.loads(l)
        r[t["itemId"]] = t["runtime"].get("sampler", {}).get("temperature") is not None and (t["timing"].get("outputTokens") or 0) > 0
    return r

def gate(C, K, P, S, need):
    ctlce = [i for i in P if K[i]["CE"]]; fixed = [i for i in ctlce if not C[i]["CE"]]
    worse = []
    for i in S:
        why = []
        if C[i]["corr"] <= K[i]["corr"] - 1.0 and not C[i]["decline"]: why.append(f"corr {K[i]['corr']}->{C[i]['corr']}")
        if C[i]["decline"] and not K[i]["decline"]: why.append("newly decline")
        if C[i]["CE"] and not K[i]["CE"]: why.append("newly CE")
        if why: worse.append((i, why))
    return dict(ctl_ce=len(ctlce), fixed=fixed, fixed_by_decline=[i for i in fixed if C[i]["decline"]], need=need, worse=worse,
                verdict="GO" if len(fixed) >= need and len(worse) <= 1 else "NO-GO")

def occ_variant(cand, K):
    """Arm items with OCC abstentions turned into declines (no Qwen fallback)."""
    v = {i: dict(x) for i, x in cand.items()}; info = {}
    for l in open(f"{A}/occrag/sidecar/occrag-{K}-screen-s42.occ.jsonl"):
        r = json.loads(l); route = r["route"]; occ = (r.get("occText") or "").strip(); st = (r.get("status") or "")
        abst = route.startswith("occ-abstain") or (route.startswith("occ-malformed") and (st.strip().lower() == "unanswerable" or bool(MODEL_DECLINE.search(occ))))
        if abst:
            v[r["itemId"]].update(decline=True, CE=False, CEu=False, CEw=False, text="[OCC abstain -> decline]")
            info[r["itemId"]] = route
    return v, info

def main():
    rows, detail = [], {}
    for arm, K, run in RUNS:
        sc = json.load(open(f"{A}/lp-screens/screen-{K}.json")); P, S = sc["problems"], sc["sentinels"]
        ctl = relabel(json.load(open(f"{A}/lp-screens/control/aggregates/lpctl-{K}-screen-s42.json"))["items"])
        cand = relabel(json.load(open(f"{A}/{arm}/aggregates/{run}.json"))["items"])
        frozen = json.load(open(f"{A}/{arm}/aggregates/{run}.gate.json"))
        R = reachable(K)
        variants = [(arm, cand, None)]
        if arm == "occrag": v, info = occ_variant(cand, K); variants.append(("occrag-decline", v, info))
        for name, C, info in variants:
            g1 = gate(C, ctl, P, S, math.ceil(0.22 * len(P)))
            Pr = [i for i in P if R[i]]; Sl = [i for i in S if R[i]]
            nreach = sum(ctl[i]["CE"] for i in Pr)
            g2 = gate(C, ctl, Pr, Sl, math.ceil(0.22 * nreach))
            cnt = lambda X, key, ids: sum(X[i][key] for i in ids)
            row = dict(arm=name, K=K, frozen=frozen["verdict"], frozen_fixed=len(frozen["fixed"]), v1c=g1["verdict"], v1c_fixed=len(g1["fixed"]),
                       v1c_fixed_by_decline=len(g1["fixed_by_decline"]), v1c_worse=[w[0] for w in g1["worse"]],
                       ceu_prob=(cnt(ctl, "CEu", P), cnt(C, "CEu", P)), ceu_all=(cnt(ctl, "CEu", P + S), cnt(C, "CEu", P + S)),
                       cew_prob=(cnt(ctl, "CEw", P), cnt(C, "CEw", P)), dec_all=(cnt(ctl, "decline", P + S), cnt(C, "decline", P + S)),
                       ceu_new=[i for i in P + S if C[i]["CEu"] and not ctl[i]["CEu"]], ceu_gone=[i for i in P + S if ctl[i]["CEu"] and not C[i]["CEu"]],
                       reach_ctl_ce=nreach, reach_live_sent=len(Sl), v1r=g2["verdict"], v1r_fixed=len(g2["fixed"]), v1r_need=g2["need"],
                       v1r_worse=[w[0] for w in g2["worse"]], fixed_ids=g2["fixed"],
                       ctl_ceu_ids=[i for i in P if ctl[i]["CEu"]], arm_ceu_ids=[i for i in P if C[i]["CEu"]],
                       default_declines=(sum(ctl[i]["decline"] or ctl[i]["warned"] for i in P + S), sum(C[i]["decline"] or C[i]["warned"] for i in P + S)))
            if info is not None:
                fr = []
                for i, route in sorted(info.items()):
                    k = ctl[i]; tag = ("unwarned:" if not k["warned"] else "warned:") + (
                        "supported" if k["corr"] >= 3.0 else "not-supported" if k["corr"] <= 1.5 else "ambiguous")
                    fr.append(dict(id=i, role="problem" if i in P else "sentinel", route=route, ctl_corr=k["corr"], ctl_warned=k["warned"], tag=tag))
                row["occ_declines"] = fr
            rows.append(row)
    print("| arm | K | frozen (fixed) | v1-corrected (fixed; by decline) | CE-unwarned ctl->arm, problems (all 37) | CE-warned ctl->arm, problems | declines ctl->arm (37) | v1-reachable post-hoc (fixed/need; live sentinels worse) |")
    print("|---|---|---|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['arm']} | {r['K']} | {r['frozen']} ({r['frozen_fixed']}) | {r['v1c']} ({r['v1c_fixed']}; {r['v1c_fixed_by_decline']}) | "
              f"{r['ceu_prob'][0]} -> {r['ceu_prob'][1]} ({r['ceu_all'][0]} -> {r['ceu_all'][1]}) | {r['cew_prob'][0]} -> {r['cew_prob'][1]} | "
              f"{r['dec_all'][0]} -> {r['dec_all'][1]} | {r['v1r']} ({r['v1r_fixed']}/{r['v1r_need']}; {len(r['v1r_worse'])}/{r['reach_live_sent']}) |")
    for r in rows:
        print(f"\n{r['arm']} {r['K']}: v1-reachable fixed {r['fixed_ids']}; v1c sentinels worse {r['v1c_worse']}; live worse {r['v1r_worse']}; "
              f"CE-unwarned new {r['ceu_new']} gone {r['ceu_gone']}; ctl CEu problems {r['ctl_ceu_ids']}; arm CEu problems {r['arm_ceu_ids']}; "
              f"default-mode declines (explicit + warned, 37) {r['default_declines']}")
        for d in r.get("occ_declines", []): print("  occ decline", d)
    if "--json" in sys.argv: json.dump(rows, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1, ensure_ascii=False)

main()
