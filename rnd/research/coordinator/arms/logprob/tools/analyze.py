#!/usr/bin/env python3
"""LOGPROB analysis (0 LLM). Usage:
  python3 -I analyze.py <cand traces.jsonl> <cand logprobs.jsonl> <control aggregate.json> <control traces.jsonl> <out.json>
Labels come from the EXISTING Haiku judgments of the mini K0 MAIN control (aggregate items: CE, corr, warned); 0 judge calls.
Steps: (1) byte-identity of answer.text vs the control on all items (labels are only valid on identical text; non-identical items are
reported and excluded from the analysis); (2) per item, the generate row whose content is the answer body (last generate of the item;
the body must be a substring of answer.text, checked); items with no generate (deterministic layers) get no features and are treated as
never flagged (most-confident score) in the all-97 analysis; (3) features on the body tokens (all visible generated tokens, i.e. after the
engine-prepended warning line):
  mean_lp  = mean sampled-token logprob            (flag score = -mean_lp)
  min_lp   = min sampled-token logprob             (flag score = -min_lp)
  ent20    = mean entropy over the first 20 tokens, top-20 probabilities + one residual bucket (1 - sum), nats  (flag score = +ent20)
  low_p    = share of tokens with p < 0.5          (flag score = +low_p)
  Direction is pre-declared (low confidence = flag); AUC is not flipped.
(4) AUC (CE = positive; ties 0.5) with item bootstrap B 2000 seed 11 (2.5 / 97.5 pct); flag-rate table at 10 / 20 / 30 %:
  k = floor(rate x n) answers flagged, highest score first; a tie group at the boundary is included only if the total stays <= k;
  no-LLM items are never flagged. Precision = CE flagged / flagged, recall = CE flagged / CE total, also correctness of flagged/unflagged.
(5) the same on warned-only answers (control 'warned'). Verdict per LOGPROB-criterion.md."""
import json, math, random, sys

FEATS = ["mean_lp", "min_lp", "ent20", "low_p"]
SIGN = {"mean_lp": -1, "min_lp": -1, "ent20": 1, "low_p": 1}


def feats(lps):
    lp = [t["logprob"] for t in lps]
    if not lp:
        return None
    ents = []
    for t in lps[:20]:
        ps = [math.exp(x) for _, x in t["top"]]
        r = max(0.0, 1.0 - sum(ps))
        ents.append(-sum(p * math.log(p) for p in ps if p > 0) - (r * math.log(r) if r > 0 else 0.0))
    return {"mean_lp": sum(lp) / len(lp), "min_lp": min(lp), "ent20": sum(ents) / len(ents) if ents else 0.0,
            "low_p": sum(1 for x in lp if math.exp(x) < 0.5) / len(lp), "n_tokens": len(lp)}


def auc(pos, neg):
    if not pos or not neg:
        return None
    s = 0.0
    for p in pos:
        for q in neg:
            s += 1.0 if p > q else 0.5 if p == q else 0.0
    return s / (len(pos) * len(neg))


def flag_table(rows, f, rate):
    n = len(rows); k = math.floor(rate * n)
    cand = sorted([r for r in rows if r["score"][f] is not None], key=lambda r: -r["score"][f])
    flagged = []
    i = 0
    while i < len(cand):
        j = i
        while j < len(cand) and cand[j]["score"][f] == cand[i]["score"][f]:
            j += 1
        if len(flagged) + (j - i) > k:
            break
        flagged += cand[i:j]; i = j
    ids = {r["id"] for r in flagged}
    ce_tot = sum(r["CE"] for r in rows); ce_f = sum(r["CE"] for r in flagged)
    unfl = [r for r in rows if r["id"] not in ids]
    return {"rate": rate, "k": k, "flagged": len(flagged), "ce_flagged": ce_f, "ce_total": ce_tot,
            "precision": ce_f / len(flagged) if flagged else None, "recall": ce_f / ce_tot if ce_tot else None,
            "corr_flagged": sum(r["corr"] for r in flagged) / len(flagged) if flagged else None,
            "corr_unflagged": sum(r["corr"] for r in unfl) / len(unfl) if unfl else None,
            "flagged_ids": sorted(ids)}


def analyse(rows):
    out = {"n": len(rows), "ce": sum(r["CE"] for r in rows), "with_features": sum(1 for r in rows if r["f"]), "features": {}}
    for f in FEATS:
        # no-LLM items: most-confident score (never flagged) -> -inf for the AUC
        sc = lambda r: r["score"][f] if r["score"][f] is not None else -math.inf
        a = auc([sc(r) for r in rows if r["CE"]], [sc(r) for r in rows if not r["CE"]])
        rnd = random.Random(11); bs = []
        for _ in range(2000):
            smp = [rows[rnd.randrange(len(rows))] for _ in rows]
            b = auc([sc(r) for r in smp if r["CE"]], [sc(r) for r in smp if not r["CE"]])
            if b is not None:
                bs.append(b)
        bs.sort()
        llm = [r for r in rows if r["f"]]
        a_llm = auc([r["score"][f] for r in llm if r["CE"]], [r["score"][f] for r in llm if not r["CE"]])
        out["features"][f] = {"auc": a, "ci": [bs[int(0.025 * len(bs))], bs[int(0.975 * len(bs)) - 1]] if bs else None,
                              "auc_llm_only": a_llm, "flags": [flag_table(rows, f, x) for x in (0.10, 0.20, 0.30)]}
    return out


def main():
    ctr, clp, cagg, ctl_tr, outp = sys.argv[1:6]
    ctl = json.load(open(cagg))["items"]
    cand = {}
    for l in open(ctr):
        t = json.loads(l); cand[t["itemId"]] = t
    ctl_ids = [json.loads(l)["itemId"] for l in open(ctl_tr)]
    gens = {}
    for l in open(clp):
        g = json.loads(l); gens.setdefault(g["itemId"], []).append(g)
    ident = [i for i in ctl_ids if i in cand and cand[i]["answer"]["text"] == ctl[i]["text"]]
    nonid = [i for i in ctl_ids if i not in ident]
    rows, body_miss = [], []
    for i in ident:
        g = gens.get(i, [])
        body = g[-1] if g else None
        if body is not None and body["content"].strip() and body["content"].strip() not in ctl[i]["text"]:
            body_miss.append(i)
        f = feats(body["logprobs"]) if body else None
        rows.append({"id": i, "CE": bool(ctl[i]["CE"]), "corr": ctl[i]["corr"], "warned": bool(ctl[i]["warned"]),
                     "declined": bool(ctl[i]["declined"]), "n_gens": len(g), "f": f,
                     "score": {k: (SIGN[k] * f[k] if f else None) for k in FEATS}})
    allr = analyse(rows)
    warned = analyse([r for r in rows if r["warned"]])
    best = max(FEATS, key=lambda k: allr["features"][k]["auc"])
    bf = allr["features"][best]; f30 = bf["flags"][2]
    go = bf["auc"] >= 0.75 and bf["ci"][0] >= 0.65 and f30["recall"] is not None and f30["recall"] >= 0.50
    res = {"identical": len(ident), "n_control": len(ctl_ids), "non_identical": nonid, "body_not_substring": body_miss,
           "items_without_generate": [r["id"] for r in rows if not r["f"]], "best_feature": best,
           "verdict": "VOID" if len(ident) < 90 else "GO" if go else "NO", "all": allr, "warned_only": warned, "rows": rows}
    json.dump(res, open(outp, "w"), indent=1)
    print(f"identical text {len(ident)}/{len(ctl_ids)}; non-identical {nonid}; body-not-substring {body_miss}; no-generate {len(res['items_without_generate'])}")
    for name, a in (("ALL", allr), ("WARNED", warned)):
        print(f"== {name}: n {a['n']} CE {a['ce']} with features {a['with_features']}")
        for f in FEATS:
            x = a["features"][f]
            print(f"  {f:8s} AUC {x['auc']:.3f} CI {x['ci'][0]:.3f}-{x['ci'][1]:.3f} llm-only {x['auc_llm_only'] if x['auc_llm_only'] is None else round(x['auc_llm_only'], 3)}  " +
                  "  ".join(f"@{int(t['rate']*100)}%: {t['ce_flagged']}/{t['flagged']} P {t['precision'] if t['precision'] is None else round(t['precision'], 2)} R {t['recall'] if t['recall'] is None else round(t['recall'], 2)}" for t in x["flags"]))
    print(f"best {best}: AUC {bf['auc']:.3f} CI low {bf['ci'][0]:.3f}, recall@30% {f30['recall']:.3f} -> {res['verdict']}")
    if res["verdict"] == "VOID":
        print("VOID: fewer than 90/97 byte-identical answers (requesting logprobs changed decoding)")


if __name__ == "__main__":
    main()
