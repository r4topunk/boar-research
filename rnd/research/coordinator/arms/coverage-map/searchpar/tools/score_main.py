"""SEARCHPAR MAIN 97 scoring (0 LLM). python3 -I tools/score_main.py -> main.json (+ table). Same stage rule as sefix/tools/score_sefix.py
(lexical FACTPRESENT best-of the cm article oracle). CTL = F1b replay (sefix/replays/main.v3-extra.jsonl); every searchpar/replays/main.*.jsonl with 97 rows is a label."""
import json, os, re, subprocess, sys, statistics, math, glob, importlib.util, unicodedata
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CM = "<workspace>/rnd/research/coordinator/arms/coverage-map"; CO = "<workspace>/rnd/research/coordinator/"
R = CO + "arms/retrieve-sweep"; BE = "<workspace>/boar-eval/bench/"
sys.path.insert(0, CM + "/compose/tools"); import kits
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
src = open(R + "/tools/sweep.py").read().split("\n")
a = next(i for i, l in enumerate(src) if l.startswith("spec = importlib.util.spec_from_file_location"))
b = next(i for i, l in enumerate(src) if l.startswith("FUN = json.load"))
__file__ = R + "/tools/sweep.py"
exec("\n".join(src[a:b]))
KIT = ",".join(os.path.basename(p)[:-7] for p in kits.kit(10))
CTL = "F1b"; files = {CTL: CM + "/sefix/replays/main.v3-extra.jsonl"}
for f in sorted(glob.glob(D + "/replays/main.*.jsonl")):
    lab = os.path.basename(f)[5:-6]
    if sum(1 for _ in open(f)) >= 97: files[lab] = f
args = [f"{l}={f}={KIT}" for l, f in files.items()]
kf, cs = D + "/r34.kfull.json", D + "/r34.cmstage.json"
subprocess.run(["python3", "-I", CM + "/tools/score_kfull.py", CM + "/aggregates/coverage-pool.json", kf] + args, capture_output=True, check=True)
subprocess.run(["python3", "-I", CM + "/tools/cm_stage.py", cs] + args, capture_output=True, check=True)
K = json.load(open(kf)); CMS = json.load(open(cs)); O = json.load(open(CM + "/aggregates/cm-oracle.json"))
items = K["items"]; ORDER = {"S1": 0, "S2": 1, "S3": 2, "K": 3}
tok = lambda c: math.ceil(len(f"{c['title']}\n{c['body']}") / 4)
def stage(lab, i):
    s = items[i][lab]["stage"]
    if i in O:
        o = CMS[lab]["items"].get(i)
        if o and ORDER[o] > ORDER[s]: s = o
    return s
rows = {l: {r["id"]: r for r in rd(f)} for l, f in files.items()}
ids = list(items); v01 = [i for i in ids if items[i]["set"] == "v0.1"]; cmi = [i for i in ids if items[i]["set"] == "cm"]
ctl_k = {i: stage(CTL, i) == "K" for i in ids}
res = {"labels": {}}
for lab in files:
    st = {i: stage(lab, i) for i in ids}; kv = {i: st[i] == "K" for i in ids}; rr = rows[lab]
    walls = [rr[i]["wallMs"] for i in ids if rr[i].get("wallMs") is not None]
    own_junk = [i for i in ids if not kv[i]]; ctl_junk = [i for i in ids if not ctl_k[i]]
    kl = lambda L, i: [c["chunkId"] for c in L[i]["keptFull"]]
    res["labels"][lab] = dict(kept92=sum(kv.values()), kept_v01=sum(kv[i] for i in v01), kept_cm=sum(kv[i] for i in cmi),
        gained=[i for i in ids if kv[i] and not ctl_k[i]], lost=[i for i in ids if ctl_k[i] and not kv[i]],
        junk_own=statistics.mean(len(rr[i]["keptFull"]) for i in own_junk), junk_ctlset=statistics.mean(len(rr[i]["keptFull"]) for i in ctl_junk),
        mean_kept=statistics.mean(len(rr[i]["keptFull"]) for i in ids), kept_tokens=statistics.mean(sum(tok(c) for c in rr[i]["keptFull"]) for i in ids),
        wall_ms_mean=statistics.mean(walls), wall_ms_p50=statistics.median(walls),
        kept_changed_vs_F1b=sum(kl(rr, i) != kl(rows[CTL], i) for i in ids),
        raw_changed_vs_F1b=sum([c["chunkId"] for c in rr[i]["rawFull"]] != [c["chunkId"] for c in rows[CTL][i]["rawFull"]] for i in ids) if "rawFull" in rr[ids[0]] else None,
        kept_list=[i for i in ids if kv[i]])
b0 = res["labels"][CTL]
for lab, e in res["labels"].items():
    e["junk_ratio_own"] = e["junk_own"] / b0["junk_own"]; e["junk_ratio_ctlset"] = e["junk_ctlset"] / b0["junk_ctlset"]; e["tok_ratio"] = e["kept_tokens"] / b0["kept_tokens"]
json.dump(res, open(D + "/r34.main.json", "w"), indent=1)
print("label kept92 v01 cm gained lost junk_own_x junk_ctlset_x tok_x wall_mean wall_p50 mean_kept kept_changed")
for lab, e in res["labels"].items():
    print(lab, e["kept92"], e["kept_v01"], e["kept_cm"], len(e["gained"]), len(e["lost"]), round(e["junk_ratio_own"], 3), round(e["junk_ratio_ctlset"], 3), round(e["tok_ratio"], 3), round(e["wall_ms_mean"]), round(e["wall_ms_p50"]), round(e["mean_kept"], 2), e["kept_changed_vs_F1b"], e["lost"])
