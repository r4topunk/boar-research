#!/usr/bin/env python3
"""DILUTION-K aggregate (0 LLM). Readings per DILUTION-criterion.md. Usage: dk_agg.py <out json> | dk_agg.py --need <k1|k2|k3> <jids out>
Judged-text pool (item, exact answer text) -> both-order rows: LITEPACKS K0/K3 v0.1, ORACLE-REAL ctl-mini + oracle, CHUNKCLEAN C + P (read only), DILUTION k1-k3."""
import json, sys, glob, random, re, hashlib, os
DK = "<workspace>/rnd/research/coordinator/arms/dilution-k/"; CC = DK + "../chunkclean/"; OR = DK + "../oracle-real/"; A = DK + "../"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
IDS = [l.strip() for l in open(DK + "items.ids") if l.strip()]
WARN = "Not found in this phone's offline library"
def trmap(f): return {t["itemId"]: t for t in rd(f)}
SYSTR = {"R": OR + "traces/oracle-K3-v01gold-s42.traces.jsonl", "ctl_mini": A + "refuse-unsupported/traces/ru-K3-dump-s42.traces.jsonl",
         **{k: DK + f"traces/dilution-{k}-K3-v01gold-s42.traces.jsonl" for k in ("k1", "k2", "k3")}}
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
add(CC + "traces/chunkclean-C-K3-v01gold-s42.traces.jsonl", CC + "judgments/cc-C.judgments.jsonl")
add(CC + "traces/chunkclean-P-K3-v01gold-s42.traces.jsonl", CC + "judgments/cc-P.judgments.jsonl")
for k in ("k1", "k2", "k3"): add(SYSTR[k], DK + f"judgments/dk-{k}.judgments.jsonl")
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
                    codes=[c for c in t["route"]["reasonCodes"] if c.startswith("oracle:")], nkept=len(t["retrieval"]["kept"]))
    return o
ARMS = [k for k in ("k1", "k2", "k3") if os.path.exists(SYSTR[k])]
S = {k: items(k) for k in ["R", "ctl_mini"] + ARMS}
U = lambda d, ids: sum(d[i]["s"] for i in ids) / sum(d[i]["sref"] for i in ids)
B = 2000
def pct(xs): xs = sorted(xs); return [round(xs[int(0.025 * B)], 3), round(xs[int(0.975 * B) - 1], 3)]
def dci(d1, d0, ids):
    r = random.Random(11); return pct([U(d1, s) - U(d0, s) for s in ([r.choice(ids) for _ in ids] for _ in range(B))])
def ce(d, ids):
    nd = [i for i in ids if not d[i]["declined"]]; c = [i for i in nd if d[i]["corr"] <= 1.5 and not d[i]["warned"]]
    return dict(n=len(c), rate=round(len(c) / len(nd), 3) if nd else None)
# validity gate: oracle:first must come with oracle:k:<k>
gate = {a: dict(first=sum(any(c.startswith("oracle:first") for c in S[a][i]["codes"]) for i in IDS),
                k_code=sum(any(c.startswith(f"oracle:k:{a[1]}:") for c in S[a][i]["codes"]) for i in IDS),
                void=[i for i in IDS if any(c.startswith("oracle:first") for c in S[a][i]["codes"]) and not any(c.startswith(f"oracle:k:{a[1]}:") for c in S[a][i]["codes"])],
                cut_items=sum(any(c.startswith(f"oracle:k:{a[1]}:") and not c.endswith("cut-0") for c in S[a][i]["codes"]) for i in IDS)) for a in ARMS}
lab = {l.split("\t")[0]: l.split("\t") for l in open(OR + "gold-labels.tsv") if not l.startswith("#") and "\t" in l}
of = json.load(open(OR + "tools/oracle-file.json"))
src = {i: next((v[3] for l in open(OR + "gold-labels.tsv") if "\t" in l and not l.startswith("#") for v in [l.split("\t")] if v[0] == i and v[1] == f"pack:{of[i]['pack']}:{of[i]['chunk_id']}"), "?") for i in IDS}
SUB = {"R kept >= 4 passages (cut bites)": [i for i in IDS if S["R"][i]["nkept"] >= 4], "R kept <= 3": [i for i in IDS if S["R"][i]["nkept"] <= 3],
       "gold lexical": [i for i in IDS if src[i] == "lexical"], "gold manual": [i for i in IDS if src[i] == "manual"]}
res = dict(criterion_sha256=open(DK + "DILUTION-criterion.sha256").read().split()[0], n=len(IDS), arms=ARMS, gate=gate,
           U={k: round(U(v, IDS), 3) for k, v in S.items()})
for a in ARMS + ["ctl_mini"]:
    res[f"dU_{a}_minus_R"] = dict(d=round(U(S[a], IDS) - U(S["R"], IDS), 3), ci=dci(S[a], S["R"], IDS))
res["CE_unwarned"] = {k: ce(v, IDS) for k, v in S.items()}
res["warned"] = {k: sum(v[i]["warned"] for i in IDS) for k, v in S.items()}
res["declined"] = {k: sum(v[i]["declined"] for i in IDS) for k, v in S.items()}
res["support"] = {k: dict(cite1=sum(v[i]["cite1"] for i in IDS), cite_any=sum(v[i]["cite_any"] for i in IDS)) for k, v in S.items()}
res["prompt_tokens_mean"] = {k: round(sum(v[i]["ptok"] or 0 for i in IDS) / sum(1 for i in IDS if v[i]["ptok"]), 1) if any(v[i]["ptok"] for i in IDS) else None for k, v in S.items()}
res["changed_vs_R"] = {a: sum(trmap(SYSTR[a])[i]["answer"]["text"] != trmap(SYSTR["R"])[i]["answer"]["text"] for i in IDS) for a in ARMS}
res["subgroups"] = {k: dict(n=len(v), **{f"d_{a}_R": round(U(S[a], v) - U(S["R"], v), 3) for a in ARMS},
                            **{f"ci_{a}_R": dci(S[a], S["R"], v) for a in ARMS if len(v) > 1}) for k, v in SUB.items()}
res["context_oracle_st_4B_only_minus_add"] = dict(opus=0.020, haiku=0.006, note="ORACLE-ST 180 self-tests, 4B cut 7, existing (ONLY +0.115 vs ADD +0.095 Opus; Haiku +0.096 vs +0.090)")
if "k1" in ARMS:
    d = res["dU_k1_minus_R"]; v = []
    v.append("PASS: other passages suppress fact use (dU k1-R >= +0.05, CI low > 0)" if d["d"] >= 0.05 and d["ci"][0] > 0 else
             "KILL: dU k1-R < +0.03 or CI low <= 0 (distractor count is not the 1.7B lever)" if d["d"] < 0.03 or d["ci"][0] <= 0 else "INCONCLUSIVE at n 30 (indicative)")
    if "k2" in ARMS:
        v.append("no maintainer item (dU k2-R < +0.02)" if res["dU_k2_minus_R"]["d"] < 0.02 else "k2 clause met (dU k2-R >= +0.02)")
    for a in ("k1", "k2"):
        if a in ARMS and res["CE_unwarned"][a]["n"] - res["CE_unwarned"]["R"]["n"] >= 3: v.append(f"STOP for cap recommendation: CE-unwarned +{res['CE_unwarned'][a]['n'] - res['CE_unwarned']['R']['n']} at {a}")
    res["verdict"] = v
res["items"] = {i: {k: S[k][i] for k in S} | {"gold_source": src[i]} for i in IDS}
res["script_sha256"] = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
open(sys.argv[1], "w").write(json.dumps(res, indent=1) + "\n")
print(json.dumps({k: v for k, v in res.items() if k != "items"}, indent=1))
