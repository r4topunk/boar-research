#!/usr/bin/env python3
"""GEMMA-VS-4B report (0 LLM). Usage: python3 -I vs4b_report.py <out.json>   (paths fixed below; frozen with VS4B-criterion.md)
Definitions as gemma4-e2b-confirm/tools/confirm_report.py: labels = null-cal/tools/labels.py; U = agg_run U (s := 0 for declined); default-mode U (R := 0);
bootstrap over the 97 items with replacement, B 2000, seed 11, CI = sorted[50], sorted[1949]. Pairs are on item ids (paired within the MAIN 97).
U_both = U over items that NEITHER side refuses in default mode (R = decline or warned), ratio of sums on that subset (subset fixed, items resampled).
F = fraction of the 4B gain Gemma captures = dU(Gemma - 1.7B) / dU(4B - 1.7B), seed 42 pairs (F42) and with Gemma and the 1.7B pooled over seeds 42 + 43
against the 4B seed 42 (Fpool: numerator = pooled two-seed dU, denominator = seed-42 4B - 1.7B); percentile CI of the ratio over the same item resamples
(resamples whose denominator <= 0 are counted and reported as share_den_le0). Tokens / wall from traces: outputTokens and promptTokens mean over items with
outputTokens > 0 (live LLM answers), totalMs mean and p50 over all items (mini wall, includes slot contention)."""
import json, sys, random, statistics as st
A = "<workspace>/rnd/research/coordinator/arms"
sys.path.insert(0, A + "/null-cal/tools"); from labels import label
P = dict(q42=(A + "/lp-screens/control/aggregates/lpctl-K0-main-s42.json", A + "/lp-screens/control/traces/lpctl-K0-main-s42.traces.jsonl"),
         q43=(A + "/gemma4-e2b-confirm/runs/c43/aggregates/gemma4-e2b-confirm-c43-K0-main-s42.json", A + "/gemma4-e2b-confirm/runs/c43/traces/gemma4-e2b-confirm-c43-K0-main-s42.traces.jsonl"),
         g42=(A + "/gemma4-e2b/stage2/aggregates/gemma4-e2b-eng-K0-main-s42.json", A + "/gemma4-e2b/stage2/traces/gemma4-e2b-eng-K0-main-s42.traces.jsonl"),
         g43=(A + "/gemma4-e2b-confirm/runs/g43/aggregates/gemma4-e2b-confirm-g43-K0-main-s42.json", A + "/gemma4-e2b-confirm/runs/g43/traces/gemma4-e2b-confirm-g43-K0-main-s42.traces.jsonl"),
         b42=(A + "/gemma4-e2b/vs4b/aggregates/gemma4-e2b-vs4b-K0-main-s42.json", A + "/gemma4-e2b/vs4b/traces/gemma4-e2b-vs4b-K0-main-s42.traces.jsonl"))
D = {k: json.load(open(v[0]))["items"] for k, v in P.items()}
T = {k: {json.loads(l)["itemId"]: json.loads(l) for l in open(v[1]) if l.strip()} for k, v in P.items()}
ids = sorted(D["q42"])
for k in D: assert set(D[k]) == set(ids), k
L = {k: {i: label(D[k][i]) for i in ids} for k in D}
B = 2000
U = lambda k, xs: sum(0 if D[k][i]["declined"] else D[k][i]["s"] for i in xs) / sum(D[k][i]["sref"] for i in xs)
UD = lambda k, xs: sum(0 if L[k][i]["R"] else L[k][i]["s"] for i in xs) / sum(L[k][i]["sref"] for i in xs)
ceu = lambda k, xs: sum(L[k][i]["CEu"] for i in xs) / len(xs)
def boot(f, pool):
    rnd = random.Random(11); return [f([rnd.choice(pool) for _ in pool]) for _ in range(B)]
def ci(f, pool):
    b = sorted(boot(f, pool)); return [round(b[50], 4), round(b[1949], 4)]
def cost(k):
    t = T[k]; live = [t[i] for i in ids if (t[i]["timing"].get("outputTokens") or 0) > 0]; tot = [t[i]["timing"]["totalMs"] for i in ids]
    return dict(live=len(live), out_tok_mean=round(st.mean(x["timing"]["outputTokens"] for x in live), 1), prompt_tok_mean=round(st.mean(x["timing"]["promptTokens"] for x in live), 1),
                totalMs_mean=round(st.mean(tot)), totalMs_p50=round(st.median(tot)), model_sha=sorted({t[i]["runtime"]["versions"].get("model.sha256", "?")[:8] for i in ids}), host=sorted({t[i]["runtime"]["host"][:12] for i in ids}))
def pair(c, g, name):
    both = [i for i in ids if L[c][i]["shown"] and L[g][i]["shown"]]
    f = lambda xs: U(g, xs) - U(c, xs)
    return dict(name=name, ctl=c, cand=g, n=len(ids), U_ctl=round(U(c, ids), 4), U_cand=round(U(g, ids), 4), dU=round(f(ids), 4), dU_ci=ci(f, ids),
                CEu_count=[sum(L[c][i]["CEu"] for i in ids), sum(L[g][i]["CEu"] for i in ids)], dCEu=round(ceu(g, ids) - ceu(c, ids), 4), dCEu_ci=ci(lambda xs: ceu(g, xs) - ceu(c, xs), ids),
                CE_count=[sum(L[c][i]["CE"] for i in ids), sum(L[g][i]["CE"] for i in ids)],
                decline_count=[sum(L[c][i]["decline"] for i in ids), sum(L[g][i]["decline"] for i in ids)],
                warned_count=[sum(L[c][i]["warned"] for i in ids), sum(L[g][i]["warned"] for i in ids)],
                refused_R_count=[sum(L[c][i]["R"] for i in ids), sum(L[g][i]["R"] for i in ids)],
                Udefault=[round(UD(c, ids), 4), round(UD(g, ids), 4)], Udefault_d=round(UD(g, ids) - UD(c, ids), 4), Udefault_d_ci=ci(lambda xs: UD(g, xs) - UD(c, xs), ids),
                both_shown=len(both), Uboth=[round(U(c, both), 4), round(U(g, both), 4)] if both else None,
                Uboth_d=round(U(g, both) - U(c, both), 4) if both else None, Uboth_d_ci=ci(f, both) if both else None,
                changed_text=sum(D[g][i]["text"] != D[c][i]["text"] for i in ids))
def ratio(num, den):
    rnd = random.Random(11); r = []; le0 = 0
    for _ in range(B):
        xs = [rnd.choice(ids) for _ in ids]; d = den(xs)
        if d <= 0: le0 += 1; continue
        r.append(num(xs) / d)
    r.sort(); n = len(r)
    return dict(F=round(num(ids) / den(ids), 3) if den(ids) > 0 else None, ci=[round(r[int(0.025 * n)], 3), round(r[int(0.975 * n) - 1], 3)] if n > 40 else None, share_den_le0=round(le0 / B, 4))
Up = lambda ks, xs: sum((0 if D[k][i]["declined"] else D[k][i]["s"]) for k in ks for i in xs) / sum(D[k][i]["sref"] for k in ks for i in xs)
out = dict(
    b4_vs_q17_s42=pair("q42", "b42", "4B - 1.7B (seed 42)"),
    b4_vs_gemma_s42=pair("g42", "b42", "4B - Gemma (seed 42 stage 2)"),
    b4_vs_gemma_s43=pair("g43", "b42", "4B seed 42 - Gemma seed 43 (g43; cross seed, item-paired)"),
    gemma_vs_q17_s42_ref=pair("q42", "g42", "Gemma - 1.7B seed 42 (reference = stage2 verdict)"),
    F42=ratio(lambda xs: U("g42", xs) - U("q42", xs), lambda xs: U("b42", xs) - U("q42", xs)),
    Fpool=ratio(lambda xs: Up(["g42", "g43"], xs) - Up(["q42", "q43"], xs), lambda xs: U("b42", xs) - U("q42", xs)),
    cost={k: cost(k) for k in P})
json.dump(out, open(sys.argv[1], "w"), indent=1)
for k, v in out.items(): print(k, json.dumps(v))
