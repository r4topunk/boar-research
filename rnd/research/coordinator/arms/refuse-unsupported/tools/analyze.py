#!/usr/bin/env python3
"""RU analysis (0 LLM). Usage: python3 -I analyze.py <items.json> <gate outputs.jsonl> <labels.jsonl> <out analysis.json>
Implements RU-criterion.md exactly. Answers and correctness = MacBook LITEPACKS K3 traces + Haiku 5.5-low judge.v1-low judgments
(K3 reuses the K0 judgment where the answer text is byte-identical, as litepacks/tools/agg.py). Per item: s = mean of the 3 judge dims over both
orders, s_ref likewise, corr = correctness mean over both orders.
Default mode (both arms): shown(C) = not decline AND not warned AND (deterministic layer, outputTokens == 0, OR retrieval.kept non-empty).
  i.e. warned answers (engine: not found in the library) and LLM answers with no kept source are refused; engine declines stay declines.
shown(R, t) = shown(C) AND NOT (gated AND P_FAIL >= t).
Metrics over n (pooled 177 decides; MAIN 97 and CAND 80 reported):
 (a) CE-unwarned rate = #(shown AND corr <= 1.5) / n; relative drop 1 - R/C; paired item bootstrap of R - C (B 2000, seed 11, 2.5/97.5 pct).
 (b) false refusals = #(shown(C) AND gated AND SUPPORTED AND corr >= 4 AND not shown(R)) / #(shown(C) AND gated AND SUPPORTED AND corr >= 4); Wilson 95 %.
 (c) U on answered = sum s / sum s_ref over shown items, per arm; R - C with paired bootstrap (report).
 (d) coverage = #shown / n.
PASS iff rel drop >= 0.50 AND CI high < 0 AND FR <= 0.15 (denominator >= 5, else INCONCLUSIVE) AND U_R >= U_C - 0.02. Primary t = 0.919; 0.5 secondary.
Support label = majority of Haiku calls A/B (C on disagreement), exact GATE17S procedure."""
import json, math, random, sys, glob, collections
A = "<workspace>/rnd/research/coordinator/arms"; LP = f"{A}/litepacks"
W = "Not found in this phone's offline library. From the model's memory, may be wrong:"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]


def judg(arm):
    by = {}
    for f in sorted(glob.glob(f"{LP}/judgments/lp-{arm}-*.judgments.jsonl")):
        for r in rd(f):
            if r.get("ok") is True: by.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
    out = {}
    for q, v in by.items():
        if len(v) != 2: continue
        ms = list(v.values()); mean = lambda d: sum(d.values()) / 3
        out[q] = dict(s=sum(mean(m["boar"]) for m in ms) / 2, sref=sum(mean(m["ref"]) for m in ms) / 2, corr=sum(m["boar"]["correctness"] for m in ms) / 2)
    return out


def traces(arm):
    out = {}
    for f in sorted(glob.glob(f"{LP}/traces/lp-{arm}-*-s42.traces.jsonl")):
        if "smoke" in f: continue
        for t in rd(f): out[t["itemId"]] = t
    return out


def wilson(k, n, z=1.96):
    if n == 0: return None
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 4), round(c + h, 4)]


def metrics(rows, t):
    n = len(rows); shC = [r for r in rows if r["shownC"]]; shR = [r for r in rows if r["shownC"] and not (r["gated"] and r["s_gate"] >= t)]
    ceC = sum(r["corr"] <= 1.5 for r in shC); ceR = sum(r["corr"] <= 1.5 for r in shR)
    U = lambda S: (sum(r["s"] for r in S) / sum(r["sref"] for r in S)) if S else None
    sc = [r for r in shC if r["gated"] and r["sup"] is True and r["corr"] >= 4]; fr = [r for r in sc if r["s_gate"] >= t]
    return dict(n=n, shown_C=len(shC), shown_R=len(shR), ceu_C=ceC, ceu_R=ceR, ceu_rate_C=ceC / n, ceu_rate_R=ceR / n,
                rel_drop=(1 - ceR / ceC) if ceC else None, U_C=U(shC), U_R=U(shR), cov_C=len(shC) / n, cov_R=len(shR) / n,
                fr_k=len(fr), fr_n=len(sc), fr=(len(fr) / len(sc)) if sc else None, fr_wilson=wilson(len(fr), len(sc)),
                refused_by_gate=len(shC) - len(shR), refused_by_gate_ce=ceC - ceR,
                refused_by_gate_correct=sum(r["corr"] >= 4 for r in shC if r["gated"] and r["s_gate"] >= t),
                unlabelled_gated_shown=sum(1 for r in shC if r["gated"] and r["sup"] is None))


def boot(rows, t, key, B=2000, seed=11):
    rnd = random.Random(seed); xs = []
    for _ in range(B):
        s = [rows[rnd.randrange(len(rows))] for _ in rows]; m = metrics(s, t)
        if key == "ceu": xs.append(m["ceu_rate_R"] - m["ceu_rate_C"])
        elif m["U_R"] is not None and m["U_C"] is not None: xs.append(m["U_R"] - m["U_C"])
    xs.sort(); return [round(xs[int(0.025 * len(xs))], 4), round(xs[int(0.975 * len(xs)) - 1], 4)]


def auc(P, N):
    return sum(1 if p > q else .5 if p == q else 0 for p in P for q in N) / (len(P) * len(N)) if P and N else None


def main():
    it = json.load(open(sys.argv[1]))["items"]
    g = {r["key"]: r for r in rd(sys.argv[2])}
    lab = collections.defaultdict(dict)
    for r in rd(sys.argv[3]): lab[r["key"]][r["call"]] = r["label"]
    T3, T0 = traces("K3"), traces("K0"); J0, J3 = judg("K0"), judg("K3")
    rows = []
    for x in it:
        i = x["key"]; j = J0.get(i) if T3[i]["answer"]["text"] == T0[i]["answer"]["text"] else J3.get(i)
        assert j, f"no judgment for {i}"
        L = lab.get(i, {}); sup = None
        if "A" in L and "B" in L:
            f = L["A"] if L["A"] == L["B"] else (collections.Counter([L["A"], L["B"], L["C"]]).most_common(1)[0][0] if "C" in L else None)
            sup = None if f is None else f == "SUPPORTED"
        shownC = (not x["decline"]) and (not x["warned"]) and ((not x["llm"]) or x["kept"])
        rows.append({**x, **j, "shownC": shownC, "sup": sup, "s_gate": g[i]["P_FAIL"] if x["gated"] else None,
                     "prompt_n": g[i]["prompt_n"] if x["gated"] else None, "prompt_ms": g[i]["prompt_ms"] if x["gated"] else None,
                     "wall_ms": g[i]["wall_ms"] if x["gated"] else None, "missing": g[i]["missing"] if x["gated"] else None})
    res = {"thresholds": {}, "sets": {"pooled": len(rows), "MAIN": sum(r["set"] == "MAIN" for r in rows), "CAND": sum(r["set"] == "CAND" for r in rows)}}
    for t in (0.919, 0.5):
        tr = {}
        for name, S in (("pooled", rows), ("MAIN", [r for r in rows if r["set"] == "MAIN"]), ("CAND", [r for r in rows if r["set"] == "CAND"])):
            m = metrics(S, t); m["ceu_diff_ci"] = boot(S, t, "ceu"); m["U_diff"] = (m["U_R"] - m["U_C"]) if m["U_R"] is not None else None
            m["U_diff_ci"] = boot(S, t, "U"); tr[name] = m
        p = tr["pooled"]
        if p["fr_n"] < 5: v = "INCONCLUSIVE (supported-correct denominator < 5)"
        else:
            ok = (p["rel_drop"] is not None and p["rel_drop"] >= 0.5 and p["ceu_diff_ci"][1] < 0 and p["fr"] <= 0.15 and p["U_R"] >= p["U_C"] - 0.02)
            v = "PASS" if ok else "FAIL"
        tr["verdict"] = v; res["thresholds"][str(t)] = tr
    gated = [r for r in rows if r["gated"]]; lab_g = [r for r in gated if r["sup"] is not None]
    res["support"] = {"gated": len(gated), "gated_unwarned": sum(not r["warned"] for r in gated), "gated_warned": sum(r["warned"] for r in gated),
                      "labelled": len(lab_g), "supported": sum(r["sup"] for r in lab_g), "supported_unwarned": sum(r["sup"] for r in lab_g if not r["warned"]),
                      "supported_warned": sum(r["sup"] for r in lab_g if r["warned"]),
                      "auc_unsupported_vs_supported": auc([r["s_gate"] for r in lab_g if not r["sup"]], [r["s_gate"] for r in lab_g if r["sup"]]),
                      "auc_unwarned_only": auc([r["s_gate"] for r in lab_g if not r["sup"] and not r["warned"]], [r["s_gate"] for r in lab_g if r["sup"] and not r["warned"]]),
                      "supported_correct": sum(r["sup"] and r["corr"] >= 4 for r in lab_g), "supported_wrong_ce": sum(r["sup"] and r["corr"] <= 1.5 for r in lab_g),
                      "unsupported_correct": sum((not r["sup"]) and r["corr"] >= 4 for r in lab_g),
                      "warned_supported_correct_gate_pass_0919": sum(r["sup"] and r["warned"] and r["corr"] >= 4 and r["s_gate"] < 0.919 for r in lab_g)}
    q = lambda v, f: v[min(len(v) - 1, int(f * len(v)))] if v else None
    for name, S in (("all_gated", gated), ("unwarned_gated", [r for r in gated if not r["warned"]])):
        pn = sorted(r["prompt_n"] for r in S); pm = sorted(r["prompt_ms"] for r in S); wm = sorted(r["wall_ms"] for r in S)
        ap = sorted(r["answer_prompt_tokens"] for r in S if r["answer_prompt_tokens"])
        res.setdefault("latency", {})[name] = {"n": len(S), "gate_prompt_tokens_p50": q(pn, .5), "p90": q(pn, .9), "max": pn[-1] if pn else None,
            "mean": round(sum(pn) / len(pn), 1) if pn else None, "answer_prompt_tokens_p50": q(ap, .5),
            "mini_prompt_ms_p50": q(pm, .5), "mini_prompt_ms_p90": q(pm, .9), "mini_wall_ms_p50": q(wm, .5), "mini_wall_ms_p90": q(wm, .9),
            "mini_prefill_tok_s": round(sum(pn) / (sum(pm) / 1000), 1) if pm else None,
            "pixel8a_prefill_s_p50_at_85tok_s": round(q(pn, .5) / 85, 2) if pn else None, "pixel8a_prefill_s_p90_at_85tok_s": round(q(pn, .9) / 85, 2) if pn else None}
    res["missing_token_rows"] = [r["key"] for r in gated if r["missing"]]
    res["rows"] = [{k: r[k] for k in ("key", "set", "decline", "warned", "llm", "kept", "gated", "shownC", "corr", "s", "sref", "sup", "s_gate", "mini_text_same")} for r in rows]
    json.dump(res, open(sys.argv[4], "w"), indent=1)
    f3 = lambda v: "NA" if v is None else (f"{v:.3f}" if isinstance(v, float) else str(v))
    for t, tr in res["thresholds"].items():
        for name in ("pooled", "MAIN", "CAND"):
            m = tr[name]
            print(f"t {t} {name:6s} n {m['n']} CEu C {m['ceu_C']} ({f3(m['ceu_rate_C'])}) R {m['ceu_R']} ({f3(m['ceu_rate_R'])}) rel {f3(m['rel_drop'])} diff CI {m['ceu_diff_ci']} | "
                  f"FR {m['fr_k']}/{m['fr_n']} Wilson {m['fr_wilson']} | U C {f3(m['U_C'])} R {f3(m['U_R'])} d {f3(m['U_diff'])} CI {m['U_diff_ci']} | cov C {f3(m['cov_C'])} R {f3(m['cov_R'])} | refused by gate {m['refused_by_gate']} (CE {m['refused_by_gate_ce']}, corr>=4 {m['refused_by_gate_correct']}) unlabelled {m['unlabelled_gated_shown']}")
        print("VERDICT t", t, tr["verdict"])
    print("support", res["support"]); print("latency", res["latency"]); print("missing", res["missing_token_rows"])


if __name__ == "__main__":
    main()
