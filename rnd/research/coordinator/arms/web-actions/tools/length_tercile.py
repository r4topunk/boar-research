#!/usr/bin/env python3
"""Length-tercile CE/correct rates inside 1.5B Detailed rows. 0 LLM. python3 -I length_tercile.py <out.json>
Length = whitespace words of answer.text. Labels as ship15b_analyze.py: per item mean of both orders' boar correctness;
correct-shown = corr>=4 and not declined; CE-shown = corr<=1.5 and not declined (declined = answer.declined). Terciles by rank (ties by id), n split 17/17/17."""
import json, sys, os, collections
A = "<workspace>/rnd/research/coordinator/arms/"
ids = [l.strip() for l in open(A + "rc1-pixel/a1/in/v01-51.ids") if l.strip()]
def traces(p, key="itemId"):
    return {(j := json.loads(l))[key]: j for l in open(p)}
def load(paths):
    J = collections.defaultdict(dict)
    for p in paths:
        for l in open(p):
            r = json.loads(l)
            if r.get("ok") and not r.get("floorScored") and r["order"] not in J[r["queryId"]]: J[r["queryId"]][r["order"]] = r["mapped"]
    return {q: (v["boarA"]["boar"]["correctness"] + v["boarB"]["boar"]["correctness"]) / 2 for q, v in J.items() if set(v) == {"boarA", "boarB"}}
RUN = "K1-main-sub3e6183-s42"
d15 = traces(A + f"style15b-detailed/traces/style15b-detailed-{RUN}.traces.jsonl")
s17 = traces(A + "lp-screens/control/traces/lpctl-K1-main-s42.traces.jsonl")
own = load([A + f"style15b-detailed/judgments/style15b-detailed-{RUN}-v01.judgments.jsonl"])
ctl = load([A + "lp-screens/control/judgments/lpctl-K1-main-s42-v01.judgments.jsonl"])
hk = {q: own[q] if q in own else ctl[q] for q in ids if q in own or d15[q]["answer"]["text"] == s17[q]["answer"]["text"]}
SRC = [("RC1 phone (Pixel 8a, app 2.0.0-rc1)", "Opus judge.v1", A + "rc1-pixel/a1/in/rc-cv5-51-15b.traces.jsonl", load([A + "rc1-pixel/a1/judgments/rc1-shipped.opus.judgments.jsonl"])),
       ("N-D desktop replica (native engine)", "Opus judge.v1", A + "native-parity/traces/native-N-D-v01-s42.traces.jsonl", load([A + "native-parity/judgments/native-N-D-v01-s42.opus.judgments.jsonl"])),
       ("style15b-detailed (our engine, mini)", "Haiku judge.v1", None, hk)]
out = {"length": "whitespace words of answer.text", "ids": len(ids), "sources": {}}
for name, judge, tp, corr in SRC:
    tr = d15 if tp is None else traces(tp)
    rows = [(len(tr[q]["answer"]["text"].split()), q, bool(tr[q]["answer"].get("declined")), corr[q]) for q in ids if q in tr and q in corr]
    rows.sort(); n = len(rows); cut = [0, n // 3 + (n % 3 > 0), 2 * (n // 3) + (n % 3 > 0) + (n % 3 > 1), n]
    ts = []
    for i in range(3):
        g = rows[cut[i]:cut[i + 1]]; m = len(g)
        ts.append({"n": m, "words_min": g[0][0], "words_max": g[-1][0], "words_median": g[m // 2][0],
                   "correct_per100": round(100 * sum(c >= 4 and not d for _, _, d, c in g) / m, 1),
                   "ce_per100": round(100 * sum(c <= 1.5 and not d for _, _, d, c in g) / m, 1),
                   "declined": sum(d for _, _, d, _ in g), "mean_corr": round(sum(c for *_, c in g) / m, 2)})
    allr = [r for r in rows]
    out["sources"][name] = {"judge": judge, "n": n, "terciles": ts,
        "all": {"correct_per100": round(100 * sum(c >= 4 and not d for _, _, d, c in allr) / n, 1), "ce_per100": round(100 * sum(c <= 1.5 and not d for _, _, d, c in allr) / n, 1)}}
js = json.dumps(out, indent=1); open(sys.argv[1], "w").write(js + "\n"); print(js)
