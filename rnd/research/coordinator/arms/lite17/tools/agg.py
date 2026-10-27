#!/usr/bin/env python3
"""LITE17 aggregation (0 LLM; criterion 453826c0). Score = PACKREAD agg: per-item s = mean of the 3 dims averaged over both judge orders,
Q = sum s / sum s_ref, item bootstrap B 2000 (single-run CI seed 11, paired CI seed 1, percentiles 2.5/97.5 as PACKREAD agg.py).
Decision per arm vs B, paired over the items where the arm differs from B (T, Q: all 150; S: items with >= 1 dropped chunk):
  CANDIDATE iff delta >= +0.03 and paired CI low > 0 and no pack family with delta <= -0.05 (families fixed before any judgment, see FAM).
S on unchanged items = B (same answer and judgment). Comparator (report only): CHAINWHEN OFF = 4B + D4 (../chainwhen/judgments), if present.
Writes ../aggregates/lite17.json. Usage: python3 -I agg.py"""
import json, os, random, collections, statistics
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAM = {"boar-firstaid-en": "health", "boar-medlineplus-en": "health", "qa-health-se": "health",
       "qa-bitcoin-se": "crypto-se", "qa-ethereum-se": "crypto-se", "qa-outdoors-se": "outdoors-travel-se", "qa-travel-se": "outdoors-travel-se",
       "boar-factbook": "reference", "boar-simplewiki-en": "reference"}
def load(p):
    by = {}
    if not os.path.exists(p): return None
    for l in open(p):
        r = json.loads(l)
        if str(r.get("ok")) != "True": continue
        m = r["mapped"] if isinstance(r["mapped"], dict) else json.loads(r["mapped"].replace("'", '"'))
        mr = lambda d: sum(d.values()) / len(d)
        by.setdefault(r["queryId"], []).append((mr(m["boar"]), mr(m["ref"]), m["boar"]["correctness"], m["winner"]))
    return {q: dict(s=sum(x[0] for x in v) / 2, r=sum(x[1] for x in v) / 2, corr=sum(x[2] for x in v) / 2, win=sum(x[3] == "boar" for x in v) / 2)
            for q, v in by.items() if len(v) == 2}
def ratio(d, ids): return sum(d[i]["s"] for i in ids) / sum(d[i]["r"] for i in ids)
def boot(fn, ids, seed, B=2000):
    if not ids: return None
    rnd = random.Random(seed); xs = sorted(fn([rnd.choice(ids) for _ in ids]) for _ in range(B)); return [round(xs[50], 3), round(xs[1949], 3)]
def contrast(A, Bd, ids):
    ids = sorted(i for i in ids if i in A and i in Bd)
    if not ids: return dict(n=0)
    return dict(n=len(ids), Q_base=round(ratio(Bd, ids), 3), Q_arm=round(ratio(A, ids), 3), delta=round(ratio(A, ids) - ratio(Bd, ids), 3),
                ci=boot(lambda s: ratio(A, s) - ratio(Bd, s), ids, 1), corr_base=round(sum(Bd[i]["corr"] for i in ids) / len(ids), 3),
                corr_arm=round(sum(A[i]["corr"] for i in ids) / len(ids), 3))
def pq(xs):
    xs = sorted(xs); return dict(p50=statistics.median(xs), p90=xs[min(len(xs) - 1, int(0.9 * len(xs)))], mean=round(sum(xs) / len(xs), 1)) if xs else None
ids = [l.strip() for l in open(f"{H}/data/ids-150.ids") if l.strip()]
s_ids = [l.strip() for l in open(f"{H}/data/ids-S.ids") if l.strip()]
pack = {}; ans = {}
for l in open(f"{H}/answers/answers-Q17.jsonl"):
    r = json.loads(l); pack[r["id"]] = r["pack"]; ans[(r["arm"], r["id"])] = r
J = {a: load(f"{H}/judgments/lite17-{a}.judgments.jsonl") for a in "BTQS"}
B = J["B"]; S = {i: (J["S"][i] if i in s_ids else B[i]) for i in B if i not in s_ids or i in (J["S"] or {})} if J["S"] is not None else None
ARMS = {"T": J["T"], "Q": J["Q"], "S": S}
M4 = load(f"{H}/../chainwhen/judgments/chainwhen-OFF.judgments.jsonl")
M4_ok = M4 is not None and all(i in M4 for i in ids)
out = dict(criterion="453826c0", n_judged={a: (len(v) if v else 0) for a, v in J.items()},
           B=dict(Q=round(ratio(B, ids), 3), ci=boot(lambda s: ratio(B, s), ids, 11), corr=round(sum(B[i]["corr"] for i in ids) / len(ids), 3),
                  win=round(sum(B[i]["win"] for i in ids) / len(ids), 3)),
           comparator_4B=(dict(Q=round(ratio(M4, ids), 3), ci=boot(lambda s: ratio(M4, s), ids, 11), corr=round(sum(M4[i]["corr"] for i in ids) / len(ids), 3),
                               gap_4B_minus_B=round(ratio(M4, ids) - ratio(B, ids), 3), gap_ci=boot(lambda s: ratio(M4, s) - ratio(B, s), ids, 1),
                               by_family={f: contrast(M4, B, [i for i in ids if FAM[pack[i]] == f]) for f in sorted(set(FAM.values()))},
                               by_pack={p: contrast(M4, B, [i for i in ids if pack[i] == p]) for p in sorted(set(pack.values()))})
                          if M4_ok else ("missing" if M4 is None else f"partial {len(M4)}/150")),
           families=FAM, arms={})
tok = lambda arm: [ans[(arm, i)]["tokens"] for i in ids if (arm, i) in ans]
out["tokens"] = dict(B=pq(tok("B")), T=pq(tok("T")), Q1=pq(tok("Q1")), Q2=pq(tok("Q2")),
                     Q_total=pq([ans[("Q1", i)]["tokens"] + ans[("Q2", i)]["tokens"] for i in ids if ("Q1", i) in ans and ("Q2", i) in ans]),
                     S=pq(tok("S")), T_reasoning_chars=pq([ans[("T", i)]["reasoning_chars"] for i in ids if ("T", i) in ans]),
                     T_finish=dict(collections.Counter(ans[("T", i)]["finish"] for i in ids if ("T", i) in ans)),
                     T_empty_answer=sum(1 for i in ids if ("T", i) in ans and not ans[("T", i)]["text"]),
                     Q1_none=sum(1 for i in ids if ("Q1", i) in ans and ans[("Q1", i)]["text"].strip().upper().startswith("NONE")),
                     prompt_tokens=dict(B=pq([ans[("B", i)]["n_prompt_tokens"] for i in ids if ("B", i) in ans]),
                                        Q1=pq([ans[("Q1", i)]["n_prompt_tokens"] for i in ids if ("Q1", i) in ans])))
for a, A in ARMS.items():
    if not A: out["arms"][a] = "not judged"; continue
    diff = s_ids if a == "S" else ids
    main = contrast(A, B, diff)
    fam = {f: contrast(A, B, [i for i in diff if FAM[pack[i]] == f]) for f in sorted(set(FAM.values()))}
    bypack = {p: contrast(A, B, [i for i in diff if pack[i] == p]) for p in sorted(set(pack.values()))}
    rule = {"delta>=+0.03": main.get("delta", -9) >= 0.03, "ci_low>0": bool(main.get("ci")) and main["ci"][0] > 0,
            "no_family<=-0.05": all(v.get("n", 0) == 0 or v["delta"] > -0.05 for v in fam.values())}
    allc = contrast(A, B, ids)
    gap = None
    if M4_ok:
        g = ratio(M4, ids) - ratio(B, ids)
        gap = dict(all150=round((ratio(A, ids) - ratio(B, ids)) / g, 3) if g else None,
                   by_family={f: (round((ratio(A, fi) - ratio(B, fi)) / (ratio(M4, fi) - ratio(B, fi)), 2) if abs(ratio(M4, fi) - ratio(B, fi)) > 0.02 else "gap<0.02")
                              for f in sorted(set(FAM.values())) for fi in [[i for i in ids if FAM[pack[i]] == f and i in A]]})
    out["arms"][a] = dict(decision_set=main, all150=allc, by_family=fam, by_pack=bypack, rule=rule, verdict="CANDIDATE" if all(rule.values()) else "NO",
                          gap_closed_vs_4B=gap)
json.dump(out, open(f"{H}/aggregates/lite17.json", "w"), indent=1)
print("B", out["B"]); print("4B", out["comparator_4B"] if isinstance(out["comparator_4B"], str) else {k: out["comparator_4B"][k] for k in ("Q", "ci", "gap_4B_minus_B", "gap_ci")})
for a, v in out["arms"].items():
    if isinstance(v, str): print(a, v); continue
    print(a, v["verdict"], v["decision_set"], "gap", v["gap_closed_vs_4B"])
    for f, c in v["by_family"].items(): print("   ", f, c)
print("tokens", json.dumps(out["tokens"]))
