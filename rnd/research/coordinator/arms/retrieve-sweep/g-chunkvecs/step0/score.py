"""Step 0 scoring (0 LLM): python3 -I step0/score.py <arm main.jsonl> [<label>]. Same FACTPRESENT rule and ids as tools/sweep.py (the PRESENT/QS/present code is exec'd from it).
Recovery = of the funnel's 25 S2/S3 ids, fact PRESENT in the arm's kept list and not in the K1 baseline replay (replay/B0.main.jsonl); losses = of the 22 S4/S5 ids, PRESENT in baseline and not in arm."""
import json, os, sys, re, unicodedata, importlib.util, glob
R = "<workspace>/rnd/research/coordinator/arms/retrieve-sweep"; CO = "<workspace>/rnd/research/coordinator"; QF = CO + "/arms/qform"
BE = "<workspace>/boar-eval/bench/"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
src = open(R + "/tools/sweep.py").read().split("\n")
a = next(i for i, l in enumerate(src) if l.startswith("spec = importlib.util.spec_from_file_location")); b = next(i for i, l in enumerate(src) if l.startswith("FUN = json.load"))
exec("\n".join(src[a:b]))
FUN = json.load(open(CO + "/ruler/RAG-FUNNEL-2026-10-21.json"))["items"]
S23 = [l.strip() for l in open(QF + "/funnel-S2S3.ids") if l.strip()]
S45 = sorted(i for i, v in FUN.items() if v["K1"]["vstage"] in ("S4", "S5"))
def load(fn): return {r["id"]: r for r in rd(fn)}
base = load(R + "/replay/B0.main.jsonl"); arm = load(sys.argv[1])
pb = {i: bool(present(i, base[i]["keptFull"])) for i in base}; pa = {i: bool(present(i, arm[i]["keptFull"])) for i in arm}
rec = [i for i in S23 if pa[i] and not pb[i]]; los = [i for i in S45 if pb[i] and not pa[i]]
chg = [i for i in base if [c["chunkId"] for c in base[i]["keptFull"]] != [c["chunkId"] for c in arm[i]["keptFull"]]]
src_of = lambda i, k: sorted({c["chunkId"].split(":")[1] for c in arm[i]["keptFull"]})
out = dict(label=sys.argv[2] if len(sys.argv) > 2 else sys.argv[1], n=len(arm), S2S3_present_baseline=sum(pb[i] for i in S23), S2S3_present_arm=sum(pa[i] for i in S23),
           S4S5_present_baseline=sum(pb[i] for i in S45), S4S5_present_arm=sum(pa[i] for i in S45), recovery=len(rec), recovery_ids=rec, losses=len(los), loss_ids=los,
           kept_changed=len(chg), mean_kept_base=sum(len(base[i]["keptFull"]) for i in base) / len(base), mean_kept_arm=sum(len(arm[i]["keptFull"]) for i in arm) / len(arm),
           simplewiki_kept_ids_arm=sum(any("simplewiki" in c["chunkId"] for c in arm[i]["keptFull"]) for i in arm), simplewiki_kept_ids_base=sum(any("simplewiki" in c["chunkId"] for c in base[i]["keptFull"]) for i in base))
print(json.dumps(out, indent=1))
