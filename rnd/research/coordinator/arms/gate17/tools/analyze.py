#!/usr/bin/env python3
"""GATE17 analysis (0 LLM). Usage: python3 -I analyze.py <items.json> <gate outputs.jsonl> <out analysis.json>
Score = P(FAIL) from the gate (higher = flag). Positives: CE (control 'CE': not declined, correctness mean <= 1.5).
- AUC (ties 0.5) CE vs non-CE, and judge-wrong (corr <= 2) vs judge-correct (corr >= 4) (others dropped for that AUC);
  item-row bootstrap B 2000 seed 11, 2.5 / 97.5 percentiles (resamples lacking a class skipped).
- FA-10 threshold: t* = the smallest observed score s such that flagging every row with score >= s gives false alarms
  (flagged among corr >= 4) <= 10 % of the corr >= 4 rows; CE recall at t*. Also the flag table at t = 0.5 (the gate's own verdict) and t*.
- Primary set = pooled (K0main + K1screen, deduplicated); also reported per set and by warned / unwarned (not part of the rule).
GO iff pooled AUC(CE) >= 0.70 AND CI low >= 0.60 AND CE recall at t* >= 1/3."""
import json, math, random, sys


def auc(pos, neg):
    if not pos or not neg:
        return None
    return sum(1.0 if p > q else 0.5 if p == q else 0.0 for p in pos for q in neg) / (len(pos) * len(neg))


def boot(rows, posf, negf):
    rnd = random.Random(11); bs = []
    for _ in range(2000):
        s = [rows[rnd.randrange(len(rows))] for _ in rows]
        b = auc([r["s"] for r in s if posf(r)], [r["s"] for r in s if negf(r)])
        if b is not None:
            bs.append(b)
    bs.sort()
    return [bs[int(0.025 * len(bs))], bs[int(0.975 * len(bs)) - 1]] if bs else None


def flags(rows, t):
    f = [r for r in rows if r["s"] >= t]
    cor = [r for r in rows if r["corr"] >= 4]; ce = [r for r in rows if r["CE"]]; wr = [r for r in rows if r["corr"] <= 2]
    return {"t": t, "flagged": len(f), "of": len(rows), "ce_caught": sum(r["CE"] for r in f), "ce_total": len(ce),
            "ce_recall": sum(r["CE"] for r in f) / len(ce) if ce else None,
            "wrong_caught": sum(r["corr"] <= 2 for r in f), "wrong_total": len(wr),
            "false_alarms": sum(r["corr"] >= 4 for r in f), "correct_total": len(cor),
            "fa_rate": sum(r["corr"] >= 4 for r in f) / len(cor) if cor else None}


def tstar(rows):
    cor = [r for r in rows if r["corr"] >= 4]
    for s in sorted({r["s"] for r in rows}):
        fa = sum(1 for r in cor if r["s"] >= s)
        if not cor or fa <= 0.10 * len(cor):
            return s
    return math.inf


def analyse(rows):
    ce = lambda r: r["CE"]; nce = lambda r: not r["CE"]; wr = lambda r: r["corr"] <= 2; co = lambda r: r["corr"] >= 4
    a_ce = auc([r["s"] for r in rows if ce(r)], [r["s"] for r in rows if nce(r)])
    a_wr = auc([r["s"] for r in rows if wr(r)], [r["s"] for r in rows if co(r)])
    t = tstar(rows)
    return {"n": len(rows), "ce": sum(map(ce, rows)), "wrong": sum(map(wr, rows)), "correct": sum(map(co, rows)),
            "auc_ce": a_ce, "ci_ce": boot(rows, ce, nce) if a_ce is not None else None,
            "auc_wrong_vs_correct": a_wr, "ci_wrong": boot(rows, wr, co) if a_wr is not None else None,
            "tstar": t, "at_tstar": flags(rows, t), "at_0.5": flags(rows, 0.5),
            "median_PFAIL": {"CE": sorted(r["s"] for r in rows if ce(r))[len([1 for r in rows if ce(r)]) // 2] if any(map(ce, rows)) else None,
                             "correct": sorted(r["s"] for r in rows if co(r))[len([1 for r in rows if co(r)]) // 2] if any(map(co, rows)) else None}}


def main():
    it = json.load(open(sys.argv[1])); out = {}
    g = {json.loads(l)["key"]: json.loads(l) for l in open(sys.argv[2])}
    rows = []
    for x in it["items"]:
        o = g[x["key"]]
        rows.append({**{k: x[k] for k in ("key", "set", "id", "CE", "corr", "warned", "ctx_chars")}, "s": o["P_FAIL"], "tok": o["tok"],
                     "missing": o["missing"], "prompt_n": o["prompt_n"], "prompt_ms": o["prompt_ms"], "wall_ms": o["wall_ms"]})
    res = {"pooled": analyse(rows)}
    for name, f in (("K0main", lambda r: r["set"] == "K0main"), ("K1screen", lambda r: r["set"] == "K1screen"),
                    ("warned", lambda r: r["warned"]), ("unwarned", lambda r: not r["warned"])):
        res[name] = analyse([r for r in rows if f(r)])
    p = res["pooled"]
    go = p["auc_ce"] >= 0.70 and p["ci_ce"][0] >= 0.60 and p["at_tstar"]["ce_recall"] >= 1 / 3
    pn = sorted(r["prompt_n"] for r in rows); pm = sorted(r["prompt_ms"] for r in rows); wm = sorted(r["wall_ms"] for r in rows)
    q = lambda v, f: v[min(len(v) - 1, int(f * len(v)))]
    res["latency"] = {"prompt_tokens_p50": q(pn, .5), "prompt_tokens_p90": q(pn, .9), "prompt_tokens_max": pn[-1],
                      "prompt_ms_p50": q(pm, .5), "prompt_ms_p90": q(pm, .9), "wall_ms_p50": q(wm, .5), "wall_ms_p90": q(wm, .9),
                      "tok_per_s_prefill": sum(pn) / (sum(pm) / 1000)}
    res["missing_token_rows"] = [r["key"] for r in rows if r["missing"]]
    res["verdict"] = "GO" if go else "NO"
    res["rows"] = rows
    json.dump(res, open(sys.argv[3], "w"), indent=1)
    for k in ("pooled", "K0main", "K1screen", "warned", "unwarned"):
        a = res[k]; ts = a["at_tstar"]; h = a["at_0.5"]
        fmt = lambda v: "NA" if v is None else f"{v:.3f}"
        print(f"{k:9s} n {a['n']} CE {a['ce']} wrong {a['wrong']} correct {a['correct']} | AUC CE {fmt(a['auc_ce'])} CI {a['ci_ce']} | "
              f"AUC wrong/corr {fmt(a['auc_wrong_vs_correct'])} CI {a['ci_wrong']} | t* {a['tstar']:.4g}: flag {ts['flagged']}/{ts['of']} CE {ts['ce_caught']}/{ts['ce_total']} "
              f"wrong {ts['wrong_caught']}/{ts['wrong_total']} FA {ts['false_alarms']}/{ts['correct_total']} | t 0.5: flag {h['flagged']} CE {h['ce_caught']} wrong {h['wrong_caught']} FA {h['false_alarms']}")
    print("latency", res["latency"], "missing", res["missing_token_rows"])
    print("VERDICT", res["verdict"])


if __name__ == "__main__":
    main()
