#!/usr/bin/env python3
"""WEB-ACTIONS-B item 2 (T3.3 / W10): per-item CE-label retest flip rate of judge.v1-low (Haiku 5.5-low, N 4, both orders) on 3 existing repeats of the
same 97 MAIN answers (mini K0 control; repeats = lp-screens control + judge-v2 rep2/rep3), and what it implies for CE counts of 12-14 per 100.
0 LLM, 0 judge. Usage: python3 -I b2_ce_flip.py -> ../aggregates/b2-ce-flip.json"""
import json, os, itertools, random, hashlib, math, sys
A = "<workspace>/rnd/research/coordinator/arms"; OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(f"{A}/judge-v2/tools/analyze.py").read(); G = {"__name__": "x", "__file__": f"{A}/judge-v2/tools/analyze.py"}
sys.argv = ["x"]; exec(src[:src.index("def v2_rep")], G)   # ids, T, v1_rep, V1 (3 repeats)
sys.path.insert(0, f"{A}/null-cal/tools"); from labels import W  # noqa
ids, V1, T = G["ids"], G["V1"], G["T"]
warned = {i: T[i]["answer"]["text"].startswith(W) for i in ids}
def labels(key):
    if key == "CE": return {i: [V1[r][i]["ce"] for r in range(3)] for i in ids}
    return {i: [V1[r][i]["ce"] and not warned[i] for r in range(3)] for i in ids}   # CEu = CE on an unwarned shown answer
res = {"n_items": len(ids), "repeats": 3, "judge": "judge.v1-low Haiku 5.5-low, N 4, both orders (same instrument as X2B-OFF-MAIN Haiku rows)",
       "answers": "lp-screens/control lpctl-K0-main-s42 (1.7B mini K0, 97 MAIN dev ids)"}
for key in ("CE", "CEu"):
    L = labels(key); pairs = list(itertools.combinations(range(3), 2))
    counts = [sum(L[i][r] for i in ids) for r in range(3)]
    flip_all = sum(L[i][a] != L[i][b] for i in ids for a, b in pairs) / (len(ids) * len(pairs))
    ever = [i for i in ids if any(L[i])]; unanim = [i for i in ever if all(L[i])]
    flip_dec = sum(L[i][a] != L[i][b] for i in ever for a, b in pairs) / (len(ever) * len(pairs)) if ever else None
    # P(CE in repeat b | CE in repeat a), averaged over ordered pairs
    num = sum(L[i][a] and L[i][b] for i in ids for a in range(3) for b in range(3) if a != b); den = sum(L[i][a] for i in ids for a in range(3) for b in range(3) if a != b)
    p = {i: sum(L[i]) / 3 for i in ids}; var = sum(p[i] * (1 - p[i]) * 3 / 2 for i in ids)  # unbiased per-item Bernoulli variance
    sd_count = math.sqrt(var); mean_c = sum(counts) / 3
    # simulation: two arms with IDENTICAL answers, each judged once; distribution of count difference (judge noise only)
    rnd = random.Random(11); diffs = []
    for _ in range(20000):
        diffs.append(sum(L[i][rnd.randrange(3)] for i in ids) - sum(L[i][rnd.randrange(3)] for i in ids))
    diffs.sort(); ge2 = sum(abs(d) >= 2 for d in diffs) / len(diffs); ge3 = sum(abs(d) >= 3 for d in diffs) / len(diffs)
    per100 = 100 / len(ids)
    res[key] = dict(counts_per_repeat=counts, mean_count=round(mean_c, 2), per100=round(mean_c * per100, 1),
                    pairwise_label_flip_rate_all_items=round(flip_all, 4), items_ever=len(ever), items_unanimous=len(unanim), items_flipping=len(ever) - len(unanim),
                    flip_ids=sorted(set(ever) - set(unanim)), pairwise_flip_rate_on_deciding_items=round(flip_dec, 3) if flip_dec is not None else None,
                    p_retest_ce_given_ce=round(num / den, 3) if den else None, judge_sd_count=round(sd_count, 2), judge_sd_per100=round(sd_count * per100, 2),
                    identical_answers_two_arms_count_diff_p95=[diffs[int(0.025 * len(diffs))], diffs[int(0.975 * len(diffs)) - 1]],
                    P_absdiff_ge2=round(ge2, 3), P_absdiff_ge3=round(ge3, 3))
s = json.dumps(res, indent=1); open(f"{OUT}/aggregates/b2-ce-flip.json", "w").write(s); print(s); print("sha256", hashlib.sha256(s.encode()).hexdigest())
