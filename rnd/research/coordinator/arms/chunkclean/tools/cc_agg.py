#!/usr/bin/env python3
"""CHUNKCLEAN aggregate (0 LLM). Readings per CHUNKCLEAN-criterion.md. Usage: cc_agg.py <out json> | cc_agg.py --need <C|P> <jids out>
Judged-text pool (item, exact answer text) -> both-order rows: LITEPACKS K0/K3 v0.1, ORACLE-REAL ctl-mini + oracle, CHUNKCLEAN C + P."""
import json, sys, glob, random, re, hashlib, os
CC = "<workspace>/rnd/research/coordinator/arms/chunkclean/"; OR = CC + "../oracle-real/"; A = CC + "../"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
IDS = [l.strip() for l in open(CC + "items.ids") if l.strip()]
WARN = "Not found in this phone's offline library"
def trmap(f): return {t["itemId"]: t for t in rd(f)}
SYSTR = {"R": OR + "traces/oracle-K3-v01gold-s42.traces.jsonl", "C": CC + "traces/chunkclean-C-K3-v01gold-s42.traces.jsonl",
         "P": CC + "traces/chunkclean-P-K3-v01gold-s42.traces.jsonl", "ctl_mini": A + "refuse-unsupported/traces/ru-K3-dump-s42.traces.jsonl"}
POOL = {}
def add(trf, jglob):
    if not os.path.exists(trf): return
    tr = trmap(trf); by = {}
    for f in glob.glob(jglob):
        for r in rd(f):
            if r.get("ok") is True: by.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
    for i, v in by.items():
        if len(v) == 2 and i in tr: POOL.setdefault((i, tr[i]["answer"]["text"]), list(v.values()))
add(A + "litepacks/traces/lp-K3-v01-s42.traces.jsonl", A + "litepacks/judgments/lp-K3-v01*.judgments.jsonl")
add(A + "litepacks/traces/lp-K0-v01-s42.traces.jsonl", A + "litepacks/judgments/lp-K0-v01*.judgments.jsonl")
add(SYSTR["ctl_mini"], OR + "judgments/ctlmini-K3-v01.judgments.jsonl")
add(SYSTR["R"], OR + "judgments/oracle-K3-v01.judgments.jsonl")
add(SYSTR["C"], CC + "judgments/cc-C.judgments.jsonl")
add(SYSTR["P"], CC + "judgments/cc-P.judgments.jsonl")
if sys.argv[1] == "--need":
    arm = sys.argv[2]; tr = trmap(SYSTR[arm]); need = [i for i in IDS if (i, tr[i]["answer"]["text"]) not in POOL]
    open(sys.argv[3], "w").write("".join(i + "\n" for i in need)); print("need", arm, len(need), "of", len(IDS)); sys.exit()
mean3 = lambda d: sum(d.values()) / 3
def items(sysname):
    tr = trmap(SYSTR[sysname]); o = {}
    for i in IDS:
        t = tr[i]; rows = POOL[(i, t["answer"]["text"])]; dec = bool(t["answer"].get("declined")); txt = t["answer"]["text"]
        o[i] = dict(s=0.0 if dec else sum(mean3(m["boar"]) for m in rows) / 2, sref=sum(mean3(m["ref"]) for m in rows) / 2,
                    corr=sum(m["boar"]["correctness"] for m in rows) / 2, declined=dec, warned=txt.lstrip().startswith(WARN),
                    cite1="[1]" in txt, cite_any=bool(re.search(r"\[\d+\]", txt)), ptok=t["timing"].get("promptTokens"),
                    codes=[c for c in t["route"]["reasonCodes"] if c.startswith("oracle:")])
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
# validity gate: oracle:first must come with oracle:text-replaced (C, P)
gate = {a: dict(first=sum(any(c.startswith("oracle:first") for c in S[a][i]["codes"]) for i in IDS),
                replaced=sum("oracle:text-replaced" in S[a][i]["codes"] for i in IDS),
                mismatch=[i for i in IDS if "oracle:text-mismatch" in S[a][i]["codes"]]) for a in ("C", "P")}
fun = json.load(open("<workspace>/rnd/research/coordinator/ruler/RAG-FUNNEL-2026-10-21.json"))["items"]
lab = {l.split("\t")[0]: l.split("\t") for l in open(OR + "gold-labels.tsv") if not l.startswith("#") and "\t" in l and l.split("\t")[2] in ("Y", "P")}
of = json.load(open(OR + "tools/oracle-file.json"))
gold = {i: f"pack:{of[i]['pack']}:{of[i]['chunk_id']}" for i in IDS}
src = {i: next((v[3] for k, v in [(l.split("\t")[0], l.split("\t")) for l in open(OR + "gold-labels.tsv") if "\t" in l and not l.startswith("#")] if k == i and v[1] == gold[i]), "?") for i in IDS}
labl = {i: next((v[2] for k, v in [(l.split("\t")[0], l.split("\t")) for l in open(OR + "gold-labels.tsv") if "\t" in l and not l.startswith("#")] if k == i and v[1] == gold[i]), "?") for i in IDS}
SUB = {"gold lexical": [i for i in IDS if src[i] == "lexical"], "gold manual": [i for i in IDS if src[i] == "manual"],
       "gold Y": [i for i in IDS if labl[i] == "Y"], "gold P": [i for i in IDS if labl[i] == "P"],
       "fact kept in K3 (S4/S5)": [i for i in IDS if fun[i]["K3"]["stage"] in ("S4", "S5")],
       "fact not kept in K3 (S1-S3)": [i for i in IDS if fun[i]["K3"]["stage"] not in ("S4", "S5")]}
res = dict(criterion_sha256=open(CC + "CHUNKCLEAN-criterion.sha256").read().split()[0], n=len(IDS), gate=gate, U={k: round(U(v, IDS), 3) for k, v in S.items()})
for a, b in (("C", "R"), ("P", "R"), ("C", "ctl_mini"), ("P", "ctl_mini"), ("R", "ctl_mini"), ("P", "C")):
    res[f"dU_{a}_minus_{b}"] = dict(d=round(U(S[a], IDS) - U(S[b], IDS), 3), ci=dci(S[a], S[b], IDS))
res["CE_unwarned"] = {k: ce(v, IDS) for k, v in S.items()}
res["warned"] = {k: sum(v[i]["warned"] for i in IDS) for k, v in S.items()}
res["declined"] = {k: sum(v[i]["declined"] for i in IDS) for k, v in S.items()}
res["support"] = {k: dict(cite1=sum(v[i]["cite1"] for i in IDS), cite_any=sum(v[i]["cite_any"] for i in IDS)) for k, v in S.items()}
res["prompt_tokens_mean"] = {k: round(sum(v[i]["ptok"] or 0 for i in IDS) / sum(1 for i in IDS if v[i]["ptok"]), 1) if any(v[i]["ptok"] for i in IDS) else None for k, v in S.items()}
res["changed_vs_R"] = {a: sum(trmap(SYSTR[a])[i]["answer"]["text"] != trmap(SYSTR["R"])[i]["answer"]["text"] for i in IDS) for a in ("C", "P")}
res["subgroups"] = {k: dict(n=len(v), **{f"d_{a}_R": round(U(S[a], v) - U(S["R"], v), 3) for a in ("C", "P")},
                            ci_C_R=dci(S["C"], S["R"], v) if len(v) > 1 else None) for k, v in SUB.items()}
d = res["dU_C_minus_R"]
res["verdict"] = ("PASS: chunk construction is a lever (dU C-R >= +0.05, CI low > 0)" if d["d"] >= 0.05 and d["ci"][0] > 0 else
                  "KILL: dU C-R < +0.02" if d["d"] < 0.02 else "INCONCLUSIVE at n 30 (indicative)")
res["items"] = {i: {k: S[k][i] for k in S} | {"stage_K3": fun[i]["K3"]["stage"], "gold": gold[i], "label": labl[i], "source": src[i]} for i in IDS}
res["script_sha256"] = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
open(sys.argv[1], "w").write(json.dumps(res, indent=1) + "\n")
print(json.dumps({k: v for k, v in res.items() if k != "items"}, indent=1))
