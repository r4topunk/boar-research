#!/usr/bin/env python3
"""GATELAT analysis (0 LLM). Usage: python3 -I analyze.py <arm dir> -> <arm dir>/analysis.json + printed table. Rule: GATELAT-criterion.md."""
import json, sys, random, statistics, collections
D = sys.argv[1]
RU = "<workspace>/rnd/research/coordinator/arms/refuse-unsupported"
RATE, T = 85.0, 0.919
rd = lambda p: [json.loads(l) for l in open(p)]
inp = {r["key"]: r for r in rd(f"{D}/gate/inputs.jsonl")}
tok = {r["key"]: r for r in rd(f"{D}/gate/tok.jsonl") if r["key"] != "_meta"}
plain = {r["key"]: r for r in rd(f"{D}/gate/plain.jsonl")}
hyb = {r["key"]: r for r in rd(f"{D}/gate/hyb.jsonl")}
v0 = {r["key"]: r for r in rd(f"{RU}/gate/boar.outputs.jsonl")}
lab = collections.defaultdict(dict)
for r in rd(f"{RU}/labels/labels.jsonl"): lab[r["key"]][r["call"]] = r["label"]


def sup(k):
    L = lab[k]
    f = L["A"] if L["A"] == L["B"] else collections.Counter([L["A"], L["B"], L["C"]]).most_common(1)[0][0]
    return f == "SUPPORTED"


keys = list(inp)
S = {k: sup(k) for k in keys}
W = {k: inp[k]["warned"] for k in keys}


def auc(P, N):
    return sum(1 if p > q else .5 if p == q else 0 for p in P for q in N) / (len(P) * len(N)) if P and N else None


def auc_rows(ks, P):
    return auc([P[k] for k in ks if not S[k]], [P[k] for k in ks if S[k]])


def boot_auc(ks, P, B=2000, seed=11):
    rng = random.Random(seed); v = []
    for _ in range(B):
        s = [rng.choice(ks) for _ in ks]; a = auc_rows(s, P)
        if a is not None: v.append(a)
    v.sort(); return [round(v[int(.025 * len(v))], 3), round(v[int(.975 * len(v)) - 1], 3)]


def pct(x, q):
    x = sorted(x); return x[min(len(x) - 1, int(round(q * (len(x) - 1))))]


V = {}  # variant -> {P, total, noncached, wall, server_prompt_n}
V["V0"] = {k: dict(P=v0[k]["P_FAIL"], total=v0[k]["prompt_n"], nc=v0[k]["prompt_n"], wall=v0[k]["wall_ms"], spn=v0[k]["prompt_n"]) for k in keys}
V["V1f"] = {k: dict(P=plain[k]["V1f"]["P_FAIL"], total=tok[k]["n_V1"], nc=tok[k]["n_V1"], wall=plain[k]["V1f"]["wall_ms"], spn=plain[k]["V1f"]["prompt_n"]) for k in keys}
V["V2"] = {k: dict(P=plain[k]["V2"]["P_FAIL"], total=tok[k]["n_V2"], nc=tok[k]["n_V2"], wall=plain[k]["V2"]["wall_ms"], spn=plain[k]["V2"]["prompt_n"]) for k in keys}
V["V1h"] = {k: dict(P=hyb[k]["V1h"]["P_FAIL"], total=tok[k]["n_V1"], nc=tok[k]["n_V1"] - tok[k]["cp_V1_A"], wall=hyb[k]["V1h"]["wall_ms"], spn=hyb[k]["V1h"]["prompt_n"]) for k in keys}
V["V3h"] = {k: dict(P=hyb[k]["V3h"]["P_FAIL"], total=tok[k]["n_V3"], nc=tok[k]["n_V3"] - tok[k]["cp_V3_A"], wall=hyb[k]["V3h"]["wall_ms"], spn=hyb[k]["V3h"]["prompt_n"]) for k in keys}
unw = [k for k in keys if not W[k]]
res = {"rate_tok_s": RATE, "t": T, "n": len(keys), "n_unwarned": len(unw), "n_supported": sum(S.values()),
       "checks": {"answer_prompt_tokens_match_trace": sum(tok[k]["n_A_prompt"] == inp[k]["answer_prompt_tokens_trace"] for k in keys),
                  "A_prefix_of_V1": sum(tok[k]["A_is_prefix_V1"] for k in keys),
                  "invocation_found_V1": sum(tok[k]["inv_V1"] for k in keys), "invocation_found_V3": sum(tok[k]["inv_V3"] for k in keys),
                  "V0_tokens_equal_RU": sum(v0[k]["prompt_n"] == v0[k]["prompt_n"] for k in keys),
                  "missing_token_rows": {n: sum(1 for k in keys for src in ([plain[k][n]] if n in plain[k] else [hyb[k][n]] if n in hyb[k] else []) if src["missing"]) for n in ("V1f", "V2", "V1h", "V3h")},
                  "answer_prompt_token_mismatch_ids": [k for k in keys if tok[k]["n_A_prompt"] != inp[k]["answer_prompt_tokens_trace"]]},
       "variants": {}}
for name, d in V.items():
    P = {k: d[k]["P"] for k in keys}
    agree = sum((P[k] >= T) == (V["V0"][k]["P"] >= T) for k in keys) / len(keys)
    agree5 = sum((P[k] >= .5) == (V["V0"][k]["P"] >= .5) for k in keys) / len(keys)
    flips = [k for k in keys if (P[k] >= T) != (V["V0"][k]["P"] >= T)]
    nc_u = [d[k]["nc"] for k in unw]; nc_a = [d[k]["nc"] for k in keys]
    proj_u = [x / RATE for x in nc_u]
    m = {"auc": round(auc_rows(keys, P), 3), "auc_ci": boot_auc(keys, P), "auc_unwarned": round(auc_rows(unw, P), 3),
         "agree_t0919": round(agree, 3), "agree_t05": round(agree5, 3), "flips_t0919": flips,
         "flagged_t0919": sum(P[k] >= T for k in keys), "flagged_t0919_unwarned": sum(P[k] >= T for k in unw),
         "total_tokens_p50_unw": pct([d[k]["total"] for k in unw], .5), "total_tokens_p50_all": pct([d[k]["total"] for k in keys], .5),
         "noncached_p50_unw": pct(nc_u, .5), "noncached_p90_unw": pct(nc_u, .9), "noncached_p50_all": pct(nc_a, .5),
         "server_prompt_n_p50_unw": pct([d[k]["spn"] for k in unw], .5),
         "mini_wall_s_p50_unw": round(pct([d[k]["wall"] for k in unw], .5) / 1000, 2), "mini_wall_s_p90_unw": round(pct([d[k]["wall"] for k in unw], .9) / 1000, 2),
         "pixel_s_p50_unw": round(pct(proj_u, .5), 2), "pixel_s_p90_unw": round(pct(proj_u, .9), 2),
         "pixel_s_p50_all": round(pct([x / RATE for x in nc_a], .5), 2)}
    m["eligible"] = name not in ("V1f",) and name != "V0"
    m["qualifies"] = bool(m["eligible"] and m["auc"] >= .90 and agree >= .95 and m["pixel_s_p50_unw"] <= 4.0)
    res["variants"][name] = m
q = [n for n, m in res["variants"].items() if m["qualifies"]]
q.sort(key=lambda n: (res["variants"][n]["pixel_s_p50_unw"], -res["variants"][n]["auc"]))
res["qualifying"] = q; res["best"] = q[0] if q else None
# server-measured vs token-computed non-cached on the hybrid variants
for n in ("V1h", "V3h"):
    diffs = [V[n][k]["spn"] - V[n][k]["nc"] for k in keys]
    res["checks"][f"{n}_server_minus_computed_noncached"] = {"min": min(diffs), "p50": pct(diffs, .5), "max": max(diffs)}
json.dump(res, open(f"{D}/analysis.json", "w"), indent=1)
print(json.dumps(res["checks"]))
for n, m in res["variants"].items():
    print(f"{n:4} AUC {m['auc']} {m['auc_ci']} unw {m['auc_unwarned']} | agree {m['agree_t0919']} (t.5 {m['agree_t05']}) flips {len(m['flips_t0919'])} | "
          f"tok p50 {m['total_tokens_p50_unw']} nc p50/p90 {m['noncached_p50_unw']}/{m['noncached_p90_unw']} srv {m['server_prompt_n_p50_unw']} | "
          f"mini {m['mini_wall_s_p50_unw']}/{m['mini_wall_s_p90_unw']} s | pixel {m['pixel_s_p50_unw']}/{m['pixel_s_p90_unw']} s | Q {m['qualifies']}")
print("best", res["best"])
