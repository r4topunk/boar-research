#!/usr/bin/env python3
"""GEMMA-PACKS report (0 LLM). Usage: python3 -I packs_report.py <out.json>   (paths fixed below; frozen with PACKS-criterion.md)
Set: the 80 candidate-pack self-tests (packs/cand80.ids), each arm's installed pack set (K0 = claim kit; K3 = K0 + simplewiki, factbook, medlineplus,
firstaid: pack-matched). Rows: Q0/Q3 = the 1.7B LITEPACKS K0/K3 (MacBook traces + existing Haiku judgments, aggregated by lp-screens/tools/agg_run.py
into packs/aggregates/q17-lp-K{0,3}-cand80.json), G0/G3 = Gemma 4 E2B (engine sampler) K0/K3 on the mini (this arm).
Labels null-cal/tools/labels.py; U = agg_run U; default-mode U (R := 0). dU_G = U(G3) - U(G0), dU_Q = U(Q3) - U(Q0), DiD = dU_G - dU_Q; one paired item
bootstrap (the 4 rows of a resampled item move together), B 2000, seed 11, CI = sorted[50], sorted[1949]. Per pack slice (20 items each) the same,
point + CI (indicative). Prompt / output tokens: mean and p50 over items with outputTokens > 0; totalMs mean and p50 over all items."""
import json, sys, random, statistics as st
A = "<workspace>/rnd/research/coordinator/arms"; G = A + "/gemma4-e2b/packs"; LP = A + "/litepacks/traces"
sys.path.insert(0, A + "/null-cal/tools"); from labels import label
P = dict(Q0=(G + "/aggregates/q17-lp-K0-cand80.json", LP + "/lp-K0-st-s42.traces.jsonl"),
         Q3=(G + "/aggregates/q17-lp-K3-cand80.json", LP + "/lp-K3-st-s42.traces.jsonl"),
         G0=(G + "/aggregates/gemma4-e2b-eng-K0-cand80-s42.json", G + "/traces/gemma4-e2b-eng-K0-cand80-s42.traces.jsonl"),
         G3=(G + "/aggregates/gemma4-e2b-eng-K3-cand80-s42.json", G + "/traces/gemma4-e2b-eng-K3-cand80-s42.traces.jsonl"))
ids = open(G + "/cand80.ids").read().split()
D = {k: json.load(open(v[0]))["items"] for k, v in P.items()}
T = {k: {json.loads(l)["itemId"]: json.loads(l) for l in open(v[1]) if l.strip()} for k, v in P.items()}
for k in D: assert set(ids) <= set(D[k]), k
L = {k: {i: label(D[k][i]) for i in ids} for k in D}
B = 2000
U = lambda k, xs: sum(0 if D[k][i]["declined"] else D[k][i]["s"] for i in xs) / sum(D[k][i]["sref"] for i in xs)
UD = lambda k, xs: sum(0 if L[k][i]["R"] else L[k][i]["s"] for i in xs) / sum(L[k][i]["sref"] for i in xs)
ceu = lambda k, xs: sum(L[k][i]["CEu"] for i in xs) / len(xs)
def ci(f, pool):
    rnd = random.Random(11); b = sorted(f([rnd.choice(pool) for _ in pool]) for _ in range(B)); return [round(b[50], 4), round(b[1949], 4)]
def block(xs):
    dG = lambda s: U("G3", s) - U("G0", s); dQ = lambda s: U("Q3", s) - U("Q0", s); did = lambda s: dG(s) - dQ(s)
    dGd = lambda s: UD("G3", s) - UD("G0", s); dQd = lambda s: UD("Q3", s) - UD("Q0", s)
    cG = lambda s: ceu("G3", s) - ceu("G0", s); cQ = lambda s: ceu("Q3", s) - ceu("Q0", s)
    return dict(n=len(xs), U={k: round(U(k, xs), 4) for k in P}, dU_G=round(dG(xs), 4), dU_G_ci=ci(dG, xs), dU_Q=round(dQ(xs), 4), dU_Q_ci=ci(dQ, xs),
                DiD=round(did(xs), 4), DiD_ci=ci(did, xs),
                level_K0_G_minus_Q=round(U("G0", xs) - U("Q0", xs), 4), level_K0_ci=ci(lambda s: U("G0", s) - U("Q0", s), xs),
                level_K3_G_minus_Q=round(U("G3", xs) - U("Q3", xs), 4), level_K3_ci=ci(lambda s: U("G3", s) - U("Q3", s), xs),
                Udefault={k: round(UD(k, xs), 4) for k in P}, dUdefault_G=round(dGd(xs), 4), dUdefault_Q=round(dQd(xs), 4),
                DiD_default=round(dGd(xs) - dQd(xs), 4), DiD_default_ci=ci(lambda s: dGd(s) - dQd(s), xs),
                CEu_count={k: sum(L[k][i]["CEu"] for i in xs) for k in P}, dCEu_G=round(cG(xs), 4), dCEu_Q=round(cQ(xs), 4),
                DiD_CEu=round(cG(xs) - cQ(xs), 4), DiD_CEu_ci=ci(lambda s: cG(s) - cQ(s), xs),
                CE_count={k: sum(L[k][i]["CE"] for i in xs) for k in P}, decline_count={k: sum(L[k][i]["decline"] for i in xs) for k in P},
                warned_count={k: sum(L[k][i]["warned"] for i in xs) for k in P}, refused_R_count={k: sum(L[k][i]["R"] for i in xs) for k in P})
def cost(k):
    t = T[k]; live = [t[i] for i in ids if (t[i]["timing"].get("outputTokens") or 0) > 0]; tot = [t[i]["timing"]["totalMs"] for i in ids]
    pt = [x["timing"]["promptTokens"] for x in live]
    return dict(live=len(live), prompt_tok_mean=round(st.mean(pt), 1), prompt_tok_p50=st.median(pt), out_tok_mean=round(st.mean(x["timing"]["outputTokens"] for x in live), 1),
                totalMs_mean=round(st.mean(tot)), totalMs_p50=round(st.median(tot)), host=sorted({t[i]["runtime"]["host"][:12] for i in ids}),
                model_sha=sorted({t[i]["runtime"]["versions"].get("model.sha256", "?")[:8] for i in ids}))
packs = ["simplewiki-en", "factbook", "medlineplus-en", "firstaid-en"]
out = dict(all80=block(ids), per_pack={p: block([i for i in ids if i.startswith(f"st-boar-{p}-")]) for p in packs}, cost={k: cost(k) for k in P},
           changed_text=dict(G3_vs_G0=sum(D["G3"][i]["text"] != D["G0"][i]["text"] for i in ids), Q3_vs_Q0=sum(D["Q3"][i]["text"] != D["Q0"][i]["text"] for i in ids)))
json.dump(out, open(sys.argv[1], "w"), indent=1)
for k, v in out.items(): print(k, json.dumps(v))
