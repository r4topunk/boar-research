"""SEARCHPAR R1 MAIN-97 scoring (0 LLM). python3 -I score_main.py <label>... -> r1.main.json (+ table). Control = F1b (sefix/replays/main.v3-extra.jsonl).
Same stage rule/junk reads as sefix/tools/score_sefix.py (lexical FACTPRESENT best-of the cm oracle); rule per SEARCHPAR-criterion.md."""
import json, os, re, subprocess, sys, statistics, math, glob, importlib.util, unicodedata
H = os.path.dirname(os.path.abspath(__file__))
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
for l in sys.argv[1:]:
    f = H + f"/replays/main.{l}.jsonl"
    if os.path.exists(f) and sum(1 for _ in open(f)) >= 97: files[l] = f
args = [f"{l}={f}={KIT}" for l, f in files.items()]
kf, cs = H + "/r1.kfull.json", H + "/r1.cmstage.json"
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
ctl_k = {i: stage(CTL, i) == "K" for i in ids}; junk_ids = [i for i in ids if not ctl_k[i]]
res = {"n_ids": len(ids), "labels": {}}
for lab in files:
    st = {i: stage(lab, i) for i in ids}; kv = {i: st[i] == "K" for i in ids}; rr = rows[lab]
    walls = [rr[i]["wallMs"] for i in ids if rr[i].get("wallMs") is not None]
    own = [i for i in ids if not kv[i]]; both = [i for i in ids if not kv[i] and not ctl_k[i]]
    e = dict(kept92=sum(kv.values()), kept_v01=sum(kv[i] for i in v01), kept_cm=sum(kv[i] for i in cmi),
             stages={s: sum(st[i] == s for i in ids) for s in ("S1", "S2", "S3", "K")},
             gained=[i for i in ids if kv[i] and not ctl_k[i]], lost=[i for i in ids if ctl_k[i] and not kv[i]],
             junk_ctlset=statistics.mean(len(rr[i]["keptFull"]) for i in junk_ids), junk_ownset=statistics.mean(len(rr[i]["keptFull"]) for i in own), junk_ownset_n=len(own),
             junk_bothset=statistics.mean(len(rr[i]["keptFull"]) for i in both), junk_bothset_ctl=statistics.mean(len(rows[CTL][i]["keptFull"]) for i in both), junk_bothset_n=len(both),
             mean_kept=statistics.mean(len(rr[i]["keptFull"]) for i in ids), kept_tokens=statistics.mean(sum(tok(c) for c in rr[i]["keptFull"]) for i in ids),
             wall_ms_mean=statistics.mean(walls), wall_ms_p50=statistics.median(walls),
             kept_changed_vs_ctl=sum([c["chunkId"] for c in rr[i]["keptFull"]] != [c["chunkId"] for c in rows[CTL][i]["keptFull"]] for i in ids),
             raw_changed_vs_ctl=sum([c["chunkId"] for c in rr[i]["rawFull"]] != [c["chunkId"] for c in rows[CTL][i]["rawFull"]] for i in ids),
             raw_set_changed_vs_ctl=sum(sorted(c["chunkId"] for c in rr[i]["rawFull"]) != sorted(c["chunkId"] for c in rows[CTL][i]["rawFull"]) for i in ids),
             kept_list=[i for i in ids if kv[i]])
    res["labels"][lab] = e
c = res["labels"][CTL]
for lab, e in res["labels"].items():
    e["junk_ratio_ownset"] = e["junk_ownset"] / c["junk_ownset"]; e["junk_ratio_ctlset"] = e["junk_ctlset"] / c["junk_ctlset"]; e["junk_ratio_bothset"] = e["junk_bothset"] / e["junk_bothset_ctl"]
    e["kept_tokens_ratio"] = e["kept_tokens"] / c["kept_tokens"]
    e["main_clause"] = e["kept92"] >= c["kept92"] + 4 and len(e["lost"]) <= 2 and e["junk_ratio_ownset"] <= 1.15  # QFORM clause added by score_qform.py
    e["junk_all_reads_ok"] = max(e["junk_ratio_ownset"], e["junk_ratio_ctlset"], e["junk_ratio_bothset"]) <= 1.15
json.dump(res, open(H + "/r1.main.json", "w"), indent=1)
print("label kept92 v01 cm gained lost junk(own)x junk(ctl)x junk(both)x ktok_x wall mean_kept kept_changed raw_changed raw_set_changed main_clause")
for lab, e in res["labels"].items():
    print(lab, e["kept92"], e["kept_v01"], e["kept_cm"], len(e["gained"]), len(e["lost"]), round(e["junk_ratio_ownset"], 3), round(e["junk_ratio_ctlset"], 3), round(e["junk_ratio_bothset"], 3),
          round(e["kept_tokens_ratio"], 3), round(e["wall_ms_mean"]), round(e["mean_kept"], 2), e["kept_changed_vs_ctl"], e["raw_changed_vs_ctl"], e["raw_set_changed_vs_ctl"], e["main_clause"])
