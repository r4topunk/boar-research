#!/usr/bin/env python3
"""Mini control vs MacBook LITEPACKS parity (0 LLM). Usage: python3 -I parity.py <K0|K1> <screen|main> [--json out]
Identical answer text count; identical retrieval.kept (source+title) count; per-item CE agreement (mini control judgments vs the MacBook LITEPACKS
judgments, agg.py rules: K1 reuses K0 rows for byte-identical answers); lists the items whose CE status flips."""
import json, sys, glob
K, ST = sys.argv[1], sys.argv[2]; H = "<workspace>/rnd/research/coordinator/arms"; LP = H + "/litepacks"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
ctl = json.load(open(f"{H}/lp-screens/control/aggregates/lpctl-{K}-{ST}-s42.json"))
mt = {t["itemId"]: t for t in rd(f"{H}/lp-screens/control/traces/lpctl-{K}-{ST}-s42.traces.jsonl")}
def tr(a):
    o = {}
    for f in glob.glob(f"{LP}/traces/lp-{a}-*-s42.traces.jsonl"):
        if "smoke" not in f: o.update({t["itemId"]: t for t in rd(f)})
    return o
def jd(a):
    by = {}
    for f in glob.glob(f"{LP}/judgments/lp-{a}-*.judgments.jsonl"):
        for r in rd(f):
            if r.get("ok") is True: by.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]["boar"]["correctness"]
    return {q: sum(v.values()) / 2 for q, v in by.items() if len(v) == 2}
T0, TK = tr("K0"), tr(K); J0, JK = jd("K0"), jd(K)
ids = list(ctl["items"]); same = [i for i in ids if TK[i]["answer"]["text"] == mt[i]["answer"]["text"]]
kk = lambda t: [(k.get("source"), k.get("title")) for k in t["retrieval"]["kept"]]
same_kept = [i for i in ids if kk(TK[i]) == kk(mt[i])]
def mb_ce(i):
    c = J0[i] if (K == "K0" or TK[i]["answer"]["text"] == T0[i]["answer"]["text"]) else JK[i]
    return (not TK[i]["answer"].get("declined")) and c <= 1.5, c
flips = [(i, mb_ce(i)[1], ctl["items"][i]["corr"]) for i in ids if mb_ce(i)[0] != ctl["items"][i]["CE"]]
out = dict(pack_set=K, stage=ST, n=len(ids), identical_text=len(same), identical_kept=len(same_kept), ce_agree=len(ids) - len(flips),
           ce_mini=sum(ctl["items"][i]["CE"] for i in ids), ce_macbook=sum(mb_ce(i)[0] for i in ids), ce_flips=flips,
           ce_agree_on_identical_text=sum(1 for i in same if mb_ce(i)[0] == ctl["items"][i]["CE"]))
print(f"{K} {ST}: identical text {len(same)}/{len(ids)} | identical kept {len(same_kept)}/{len(ids)} | CE agree {out['ce_agree']}/{len(ids)} "
      f"(on identical text {out['ce_agree_on_identical_text']}/{len(same)}) | CE mini {out['ce_mini']} vs MacBook {out['ce_macbook']}")
for f in flips: print("  CE flip", f[0], "macbook corr", f[1], "mini corr", f[2])
if "--json" in sys.argv: json.dump(out, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
