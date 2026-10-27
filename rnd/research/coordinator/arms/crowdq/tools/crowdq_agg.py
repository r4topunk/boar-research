#!/usr/bin/env python3
"""CROWDQ step 4 (0 LLM): paired Δ P − S (P = all 9 packs installed, runs/st-<pack>-cut7-all9-s42; S = one pack, arms/packs/selftest-runs/st-<pack>-cut7-s42),
Haiku 5.5-low rows both orders. Estimator = arms/packs/tools/localjudge_agg.py (ratio of sums; per-item bootstrap B 2000 seed 11 of the difference).
Over the 180, by family (SE qa-*, topic boar-*), per pack. + RULE 27 same_answer.py per pack and pooled, + reach.json. Writes aggregates/crowdq.json."""
import json, os, subprocess, collections, numpy as np
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); AR = os.path.dirname(H); SD = f"{AR}/packs/selftest-runs"; R = f"{H}/runs"
K = ("correctness", "completeness", "usefulness"); mr = lambda s: sum(s[k] for k in K) / 3
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se", "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
def load(p):
    J = collections.defaultdict(dict)
    for l in open(p):
        r = json.loads(l)
        if r.get("ok"): J[r["queryId"]][r["order"]] = r["mapped"]
    out = {}
    for q, v in J.items():
        assert len(v) == 2, q
        a, b = v["boarA"], v["boarB"]
        out[q] = {"s": (mr(a["boar"]) + mr(b["boar"])) / 2, "r": (mr(a["ref"]) + mr(b["ref"])) / 2, "winner": a["winner"] if a["winner"] == b["winner"] else "tie"}
    return out
def ratios(S, R): return S.sum() / R.sum(), (S - 1).sum() / (R - 1).sum()
def boot(fn, n, B=2000, seed=11):
    rng = np.random.default_rng(seed); return np.array([fn(rng.integers(0, n, n)) for _ in range(B)])
ci = lambda x: [round(float(v), 3) for v in np.percentile(x, [2.5, 97.5])]
def setstats(d, ids):
    S = np.array([d[q]["s"] for q in ids]); Rr = np.array([d[q]["r"] for q in ids]); pt = ratios(S, Rr); b = boot(lambda ii: ratios(S[ii], Rr[ii]), len(ids))
    w = collections.Counter(d[q]["winner"] for q in ids)
    return {"n": len(ids), "raw": round(pt[0], 3), "raw_ci": ci(b[:, 0]), "above_min": round(pt[1], 3), "above_min_ci": ci(b[:, 1]), "win_tie_loss": [w["boar"], w["tie"], w["ref"]]}
def paired(P, S, ids):
    SP = np.array([P[q]["s"] for q in ids]); RP = np.array([P[q]["r"] for q in ids]); SS = np.array([S[q]["s"] for q in ids]); RS = np.array([S[q]["r"] for q in ids])
    f = lambda ii: [ratios(SP[ii], RP[ii])[j] - ratios(SS[ii], RS[ii])[j] for j in (0, 1)]
    pt = f(np.arange(len(ids))); b = boot(f, len(ids))
    return {"n": len(ids), "d_raw": round(pt[0], 3), "d_raw_ci": ci(b[:, 0]), "d_above_min": round(pt[1], 3), "d_above_min_ci": ci(b[:, 1]),
            "items_better_worse_same": [int(sum(P[q]["s"] > S[q]["s"] for q in ids)), int(sum(P[q]["s"] < S[q]["s"] for q in ids)), int(sum(P[q]["s"] == S[q]["s"] for q in ids))]}
def same(a, b, label):
    o = subprocess.run(["python3", "-I", f"{AR}/seedgen/tools/same_answer.py", a, b, "--label", label], capture_output=True, text=True, check=True).stdout
    d = json.loads(o.splitlines()[0]); return {k: d[k] for k in ("n_paired", "all", "kept_unchanged", "kept_unchanged_prompt_same", "kept_unchanged_no_llm", "kept_unchanged_prompt_diff_n", "diff_ids_kept_unchanged_prompt_same")}
reach = json.load(open(f"{H}/aggregates/reach.json"))
out = {"criterion_sha256": open(f"{H}/CROWDQ-criterion.sha256").read().split()[0], "packs": []}; aP, aS = {}, {}
cat = lambda pat: "".join(open(pat.format(p)).read() for p in PACKS)
for p in PACKS:
    P = load(f"{R}/st-{p}-cut7-all9-s42.judgments.jsonl"); S = load(f"{SD}/st-{p}-cut7-s42.judgments.jsonl"); ids = sorted(set(P) & set(S)); assert len(ids) == 20, p
    rp = reach["per_pack"][p]
    out["packs"].append({"pack": p, "S": setstats(S, ids), "P": setstats(P, ids), "paired": paired(P, S, ids),
                         "reach": {k: rp[k] for k in ("fact_S", "fact_P", "own_kept_S", "own_kept_P", "kept_S", "kept_P", "changed")}, "kept_P_by_owner": rp["kept_from_P_by_owner"],
                         "same_answer": same(f"{SD}/st-{p}-cut7-s42.traces.jsonl", f"{R}/st-{p}-cut7-all9-s42.traces.jsonl", p)})
    aP.update({f"{p}|{q}": P[q] for q in ids}); aS.update({f"{p}|{q}": S[q] for q in ids})
for name, sel in (("pooled", lambda k: True), ("SE", lambda k: k.startswith("qa-")), ("topic", lambda k: k.startswith("boar-"))):
    ids = sorted(k for k in aP if sel(k)); out[name] = {"S": setstats(aS, ids), "P": setstats(aP, ids), "paired": paired(aP, aS, ids)}
# pooled same_answer over concatenated traces
sc = f"{H}/aggregates/_S180.traces.jsonl"; pc = f"{H}/aggregates/_P180.traces.jsonl"
open(sc, "w").write(cat(SD + "/st-{}-cut7-s42.traces.jsonl")); open(pc, "w").write(cat(R + "/st-{}-cut7-all9-s42.traces.jsonl"))
out["same_answer_pooled"] = same(sc, pc, "pooled"); os.remove(sc); os.remove(pc)
out["reach_total"] = reach["total"]; out["reach_family"] = {"SE": reach["SE"], "topic": reach["topic"]}
d = out["pooled"]["paired"]; cl, ch = d["d_raw_ci"]
out["reading"] = ("crowding cost confirmed" if ch < 0 and d["d_raw"] <= -0.03 else
                  "near-miss -> Opus 360 recommended" if d["d_raw"] <= -0.02 and cl <= 0 <= ch else
                  "cost small" if (cl <= 0 <= ch) or abs(d["d_raw"]) < 0.03 else "other (see numbers)")
json.dump(out, open(f"{H}/aggregates/crowdq.json", "w"), indent=1)
print(json.dumps({k: out[k] for k in ("pooled", "SE", "topic", "reading")}, indent=1))
for r in out["packs"]: print(r["pack"], r["S"]["raw"], r["P"]["raw"], r["paired"]["d_raw"], r["paired"]["d_raw_ci"], r["paired"]["items_better_worse_same"], r["same_answer"]["kept_unchanged_prompt_same"]["same_answer"], "/", r["same_answer"]["kept_unchanged_prompt_same"]["n"])
print("same_answer pooled", json.dumps({k: out["same_answer_pooled"][k] for k in ("all", "kept_unchanged", "kept_unchanged_prompt_same")}))
