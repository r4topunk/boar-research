#!/usr/bin/env python3
"""COVERAGE-MATRIX report (0 LLM). Usage: python3 -I matrix_report.py <out.json>   (paths fixed below; frozen with MATRIX-criterion.md)
Cells = tier x pack set on the 80 candidate-pack self-tests (cand80.ids) + the 1.7B KA vs K0 no-harm pair on MAIN 97 (main-97.ids). Labels: null-cal/tools/labels.py.
U = sum(s, declined -> 0) / sum(sref) (agg_run U). Deltas: paired item bootstrap (all rows of a resampled item move together), B 2000, seed 11,
CI = sorted[50], sorted[1949]. Cost per cell: prompt / answer tokens mean and p50 over live items (outputTokens > 0), wall totalMs mean and p50 over all items, host.
A missing cell (not generated or not judged) is reported as pending and every quantity that needs it is omitted."""
import json, sys, os, random, statistics as st
A = "<workspace>/rnd/research/coordinator/arms"; CM = A + "/coverage-matrix"; GP = A + "/gemma4-e2b/packs"
sys.path.insert(0, A + "/null-cal/tools"); from labels import label
C = {  # cell: (aggregate, traces, host note)
 "q17-K0": (A + "/null-cal/control/aggregates/poolctl-K0-st180-s42.json", A + "/null-cal/control/traces/poolctl-K0-st180-s42.traces.jsonl"),
 "q17-K0mb": (GP + "/aggregates/q17-lp-K0-cand80.json", A + "/litepacks/traces/lp-K0-st-s42.traces.jsonl"),
 "q17-K3mb": (GP + "/aggregates/q17-lp-K3-cand80.json", A + "/litepacks/traces/lp-K3-st-s42.traces.jsonl"),
 "q17-KA": (CM + "/q17/aggregates/q17-KA-cand80-s42.json", CM + "/q17/traces/q17-KA-cand80-s42.traces.jsonl"),
 "gem-K0": (GP + "/aggregates/gemma4-e2b-eng-K0-cand80-s42.json", GP + "/traces/gemma4-e2b-eng-K0-cand80-s42.traces.jsonl"),
 "gem-K3": (GP + "/aggregates/gemma4-e2b-eng-K3-cand80-s42.json", GP + "/traces/gemma4-e2b-eng-K3-cand80-s42.traces.jsonl"),
 "gem-KA": (CM + "/gemma/aggregates/gemma-KA-cand80-s42.json", CM + "/gemma/traces/gemma-KA-cand80-s42.traces.jsonl"),
 "q4b-K0": (CM + "/q4b/aggregates/q4b-K0-cand80-s42.json", CM + "/q4b/traces/q4b-K0-cand80-s42.traces.jsonl"),
 "q4b-K3": (CM + "/q4b/aggregates/q4b-K3-cand80-s42.json", CM + "/q4b/traces/q4b-K3-cand80-s42.traces.jsonl"),
 "q4b-KA": (CM + "/q4b/aggregates/q4b-KA-cand80-s42.json", CM + "/q4b/traces/q4b-KA-cand80-s42.traces.jsonl"),
 "main-q17-K0": (A + "/lp-screens/control/aggregates/lpctl-K0-main-s42.json", A + "/lp-screens/control/traces/lpctl-K0-main-s42.traces.jsonl"),
 "main-q17-KA": (CM + "/q17/aggregates/q17-KA-main-97-s42.json", CM + "/q17/traces/q17-KA-main-97-s42.traces.jsonl")}
ids80 = open(CM + "/cand80.ids").read().split(); ids97 = open(CM + "/main-97.ids").read().split()
SL = {"all80": ids80, "simplewiki20": [i for i in ids80 if "simplewiki" in i], "on60": [i for i in ids80 if "simplewiki" not in i]}
for p in ("factbook", "medlineplus", "firstaid"): SL[p + "20"] = [i for i in ids80 if p in i]
D, T, pending = {}, {}, []
for k, (ag, tr) in C.items():
    xs = ids97 if k.startswith("main") else ids80
    if not (os.path.isfile(ag) and os.path.isfile(tr)): pending.append(k); continue
    it = json.load(open(ag))["items"]
    if not set(xs) <= set(it): pending.append(k); continue
    D[k] = {i: label(it[i]) for i in xs}; D[k]["_raw"] = it
    T[k] = {json.loads(l)["itemId"]: json.loads(l) for l in open(tr) if l.strip()}
B = 2000
U = lambda k, xs: sum(0 if D[k]["_raw"][i]["declined"] else D[k][i]["s"] for i in xs) / sum(D[k][i]["sref"] for i in xs)
def ci(f, pool):
    rnd = random.Random(11); b = sorted(f([rnd.choice(pool) for _ in pool]) for _ in range(B)); return [round(b[50], 4), round(b[1949], 4)]
def delta(a, b, xs):  # U(a) - U(b) with CI; None if a cell is pending
    if a not in D or b not in D: return None
    f = lambda s: U(a, s) - U(b, s); return dict(d=round(f(xs), 4), ci=ci(f, xs))
def did(a1, a0, b1, b0, xs):
    if any(k not in D for k in (a1, a0, b1, b0)): return None
    f = lambda s: (U(a1, s) - U(a0, s)) - (U(b1, s) - U(b0, s)); return dict(d=round(f(xs), 4), ci=ci(f, xs))
def cell(k, xs):
    if k not in D: return "pending"
    t = T[k]; live = [t[i] for i in xs if (t[i]["timing"].get("outputTokens") or 0) > 0]; tot = [t[i]["timing"]["totalMs"] for i in xs]
    L = D[k]; n = len(xs); ceu = sum(L[i]["CEu"] for i in xs)
    return dict(n=n, U=round(U(k, xs), 4), U_ci=ci(lambda s: U(k, s), xs), CEu=ceu, CEu_rate=round(ceu / n, 4), CE=sum(L[i]["CE"] for i in xs),
                declines=sum(L[i]["decline"] for i in xs), warned=sum(L[i]["warned"] for i in xs), refused_R=sum(L[i]["R"] for i in xs),
                live=len(live), prompt_tok_mean=round(st.mean(x["timing"]["promptTokens"] for x in live), 1) if live else None,
                prompt_tok_p50=st.median(x["timing"]["promptTokens"] for x in live) if live else None,
                out_tok_mean=round(st.mean(x["timing"]["outputTokens"] for x in live), 1) if live else None,
                wall_ms_mean=round(st.mean(tot)), wall_ms_p50=round(st.median(tot)), host=sorted({(t[i].get("runtime") or {}).get("host", "?")[:12] for i in xs}))
def ceu_d(a, b, xs):
    if a not in D or b not in D: return None
    f = lambda s: (sum(D[a][i]["CEu"] for i in s) - sum(D[b][i]["CEu"] for i in s)) / len(s); return dict(d=round(f(xs), 4), ci=ci(f, xs))
out = dict(pending=pending, slices={})
for sn, xs in SL.items():
    r = dict(cells={k: cell(k, xs) for k in C if not k.startswith("main")})
    r["dU_vs_K0"] = {"q17-K3mb (MacBook pair)": delta("q17-K3mb", "q17-K0mb", xs), "q17-KA (mini pair)": delta("q17-KA", "q17-K0", xs),
                     "gem-K3": delta("gem-K3", "gem-K0", xs), "gem-KA": delta("gem-KA", "gem-K0", xs),
                     "q4b-K3": delta("q4b-K3", "q4b-K0", xs), "q4b-KA": delta("q4b-KA", "q4b-K0", xs)}
    r["KA_minus_K3"] = {"q17 (cross-host: KA mini, K3 MacBook)": delta("q17-KA", "q17-K3mb", xs), "gem": delta("gem-KA", "gem-K3", xs), "q4b": delta("q4b-KA", "q4b-K3", xs)}
    r["dCEu_rate_vs_K0"] = {"q17-K3mb": ceu_d("q17-K3mb", "q17-K0mb", xs), "q17-KA": ceu_d("q17-KA", "q17-K0", xs), "gem-K3": ceu_d("gem-K3", "gem-K0", xs),
                            "gem-KA": ceu_d("gem-KA", "gem-K0", xs), "q4b-K3": ceu_d("q4b-K3", "q4b-K0", xs), "q4b-KA": ceu_d("q4b-KA", "q4b-K0", xs)}
    r["tier_gaps"] = {"K0": {"q4b-q17": delta("q4b-K0", "q17-K0", xs), "gem-q17": delta("gem-K0", "q17-K0", xs), "q4b-gem": delta("q4b-K0", "gem-K0", xs)},
                      "K3 (q17 MacBook)": {"q4b-q17": delta("q4b-K3", "q17-K3mb", xs), "gem-q17": delta("gem-K3", "q17-K3mb", xs), "q4b-gem": delta("q4b-K3", "gem-K3", xs)},
                      "KA": {"q4b-q17": delta("q4b-KA", "q17-KA", xs), "gem-q17": delta("gem-KA", "q17-KA", xs), "q4b-gem": delta("q4b-KA", "gem-KA", xs)}}
    r["pack_gain_DiD_vs_q17"] = {"K3 q4b": did("q4b-K3", "q4b-K0", "q17-K3mb", "q17-K0mb", xs), "K3 gem": did("gem-K3", "gem-K0", "q17-K3mb", "q17-K0mb", xs),
                                 "KA q4b": did("q4b-KA", "q4b-K0", "q17-KA", "q17-K0", xs), "KA gem": did("gem-KA", "gem-K0", "q17-KA", "q17-K0", xs)}
    out["slices"][sn] = r
out["MAIN97_noharm"] = dict(cells={k: cell(k, ids97) for k in ("main-q17-K0", "main-q17-KA")}, dU=delta("main-q17-KA", "main-q17-K0", ids97),
                            dCEu_rate=ceu_d("main-q17-KA", "main-q17-K0", ids97))
nh = out["MAIN97_noharm"]["dU"]
out["MAIN97_noharm"]["reading"] = "pending" if nh is None else ("harm" if nh["ci"][1] < 0 else "no harm shown" if nh["ci"][0] >= -0.03 else "inconclusive")
json.dump(out, open(sys.argv[1], "w"), indent=1)
a = out["slices"]["all80"]
for k, v in a["cells"].items(): print(k, v if v == "pending" else (v["U"], v["CEu"], v["refused_R"], v["prompt_tok_mean"], v["wall_ms_p50"]))
print("dU", json.dumps(a["dU_vs_K0"])); print("KA-K3", json.dumps(a["KA_minus_K3"])); print("MAIN", json.dumps(out["MAIN97_noharm"]["dU"]), out["MAIN97_noharm"]["reading"]); print("pending", pending)
