#!/usr/bin/env python3
"""ORACLE-REAL aggregate (0 LLM). Readings per ORACLE-criterion.md (sha 16f32030). Usage: oracle_agg.py <out json> [--need <jids out>]
--need: write the arm ids whose answer text has no judged twin (to judge), then exit.
Judged-text pool (item, exact answer text) -> both-order rows: LITEPACKS K0/K3 v0.1 judgments, the mini-control judgments, the arm judgments."""
import json, sys, glob, random, re, hashlib
OR = "<workspace>/rnd/research/coordinator/arms/oracle-real/"; A = OR + "../"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
IDS = [l.strip() for l in open(OR + "items.ids") if l.strip()]
WARN = "Not found in this phone's offline library"
def trmap(f): return {t["itemId"]: t for t in rd(f)}
SYSTR = {"oracle": OR + "traces/oracle-K3-v01gold-s42.traces.jsonl", "ctl_mini": A + "refuse-unsupported/traces/ru-K3-dump-s42.traces.jsonl",
         "ctl_macbook": A + "litepacks/traces/lp-K3-v01-s42.traces.jsonl"}
POOL = {}
def add(trf, jglob):
    tr = trmap(trf); by = {}
    for f in glob.glob(jglob):
        for r in rd(f):
            if r.get("ok") is True: by.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
    for i, v in by.items():
        if len(v) == 2 and i in tr: POOL.setdefault((i, tr[i]["answer"]["text"]), list(v.values()))
add(A + "litepacks/traces/lp-K3-v01-s42.traces.jsonl", A + "litepacks/judgments/lp-K3-v01*.judgments.jsonl")
add(A + "litepacks/traces/lp-K0-v01-s42.traces.jsonl", A + "litepacks/judgments/lp-K0-v01*.judgments.jsonl")
add(SYSTR["ctl_mini"], OR + "judgments/ctlmini-K3-v01.judgments.jsonl")
import os
if os.path.exists(SYSTR["oracle"]): add(SYSTR["oracle"], OR + "judgments/oracle-K3-v01.judgments.jsonl")
if "--need" in sys.argv:
    tr = trmap(SYSTR["oracle"]); need = [i for i in IDS if (i, tr[i]["answer"]["text"]) not in POOL]
    open(sys.argv[sys.argv.index("--need") + 1], "w").write("".join(i + "\n" for i in need)); print("need", len(need), "of", len(IDS)); sys.exit()
mean3 = lambda d: sum(d.values()) / 3
def items(sysname):
    tr = trmap(SYSTR[sysname]); o = {}
    for i in IDS:
        t = tr[i]; rows = POOL[(i, t["answer"]["text"])]; dec = bool(t["answer"].get("declined"))
        s = sum(mean3(m["boar"]) for m in rows) / 2; sref = sum(mean3(m["ref"]) for m in rows) / 2
        corr = sum(m["boar"]["correctness"] for m in rows) / 2; txt = t["answer"]["text"]
        o[i] = dict(s=0.0 if dec else s, sref=sref, corr=corr, declined=dec, warned=txt.lstrip().startswith(WARN),
                    cite1="[1]" in txt, cite_any=bool(re.search(r"\[\d+\]", txt)), oracle_codes=[c for c in t["route"]["reasonCodes"] if c.startswith("oracle:")])
    return o
S = {k: items(k) for k in SYSTR}
U = lambda d, ids: sum(d[i]["s"] for i in ids) / sum(d[i]["sref"] for i in ids)
B = 2000
def pct(xs): xs = sorted(xs); return [round(xs[int(0.025 * B)], 3), round(xs[int(0.975 * B) - 1], 3)]
def dci(d1, d0, ids):
    r = random.Random(11); return pct([U(d1, s) - U(d0, s) for s in ([r.choice(ids) for _ in ids] for _ in range(B))])
def ce(d, ids):
    nd = [i for i in ids if not d[i]["declined"]]; c = [i for i in nd if d[i]["corr"] <= 1.5 and not d[i]["warned"]]
    return dict(n=len(c), rate=round(len(c) / len(nd), 3) if nd else None)
fun = json.load(open("<workspace>/rnd/research/coordinator/ruler/RAG-FUNNEL-2026-10-21.json"))["items"]
lab = {l.split("\t")[0]: l.split("\t") for l in open(OR + "gold-labels.tsv") if not l.startswith("#") and "\t" in l and l.split("\t")[2] in ("Y", "P")}
SUB = {"fact kept in K3 (S4/S5)": [i for i in IDS if fun[i]["K3"]["stage"] in ("S4", "S5")],
       "fact not kept in K3 (S1-S3)": [i for i in IDS if fun[i]["K3"]["stage"] not in ("S4", "S5")],
       "gold Y": [i for i in IDS if lab[i][2] == "Y"], "gold P": [i for i in IDS if lab[i][2] == "P"],
       "gold lexical": [i for i in IDS if lab[i][3] == "lexical"], "gold manual": [i for i in IDS if lab[i][3] == "manual"]}
res = dict(criterion_sha256="16f32030871d2b8f1df7630db27e5bf4f7a8fb9aee1d6f1c02a2e8d6c07b3f8e", n=len(IDS),
           U={k: round(U(v, IDS), 3) for k, v in S.items()})
for c in ("ctl_mini", "ctl_macbook"):
    d = U(S["oracle"], IDS) - U(S[c], IDS)
    res[f"dU_oracle_minus_{c}"] = dict(d=round(d, 3), ci=dci(S["oracle"], S[c], IDS), frac_selftest_gain=round(d / 0.139, 2))
res["dU_ctl_mini_minus_ctl_macbook"] = dict(d=round(U(S["ctl_mini"], IDS) - U(S["ctl_macbook"], IDS), 3), ci=dci(S["ctl_mini"], S["ctl_macbook"], IDS))
res["CE_unwarned"] = {k: ce(v, IDS) for k, v in S.items()}
res["warned"] = {k: sum(v[i]["warned"] for i in IDS) for k, v in S.items()}
res["declined"] = {k: sum(v[i]["declined"] for i in IDS) for k, v in S.items()}
res["support"] = {k: dict(cite1=sum(v[i]["cite1"] for i in IDS), cite_any=sum(v[i]["cite_any"] for i in IDS)) for k, v in S.items()}
res["changed_vs_ctl_mini"] = sum(trmap(SYSTR["oracle"])[i]["answer"]["text"] != trmap(SYSTR["ctl_mini"])[i]["answer"]["text"] for i in IDS)
res["subgroups"] = {k: dict(n=len(v), U_oracle=round(U(S["oracle"], v), 3), U_ctl_mini=round(U(S["ctl_mini"], v), 3),
                            d=round(U(S["oracle"], v) - U(S["ctl_mini"], v), 3), ci=dci(S["oracle"], S["ctl_mini"], v) if len(v) > 1 else None) for k, v in SUB.items()}
d = res["dU_oracle_minus_ctl_mini"]
res["verdict"] = ("KILL: reading, not retrieval, is the binding stage (dU < +0.03)" if d["d"] < 0.03 else
                  "RETRIEVAL-BOUND: dU >= +0.03 with CI low > 0" if d["ci"][0] > 0 else "INCONCLUSIVE at n 30 (indicative)")
res["hypothesis_kill"] = dict(ci_high_lt_0_05=d["ci"][1] < 0.05, d_lt_half_oraclest=d["d"] < 0.0475)
res["items"] = {i: {k: S[k][i] for k in S} | {"stage_K3": fun[i]["K3"]["stage"], "gold": lab[i][1], "label": lab[i][2]} for i in IDS}
res["script_sha256"] = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
open(sys.argv[1], "w").write(json.dumps(res, indent=1) + "\n")
print(json.dumps({k: v for k, v in res.items() if k != "items"}, indent=1))
