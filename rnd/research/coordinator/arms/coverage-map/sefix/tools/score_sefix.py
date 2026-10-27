"""SEFIX scoring (0 LLM). python3 -I tools/score_sefix.py -> sefix.json (+ prints the table). Same stage rule as compose/tools/score_compose.py
(lexical FACTPRESENT best-of the cm article oracle), plus a strict cm read (a fact chunk of the oracle article is in keptFull, gold_cm.json).
Control = compose/replays/main.N10.gidf.jsonl (identical to replays/main.off.jsonl, tools/ident.py)."""
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
CTL = "ctl"; files = {CTL: CM + "/compose/replays/main.N10.gidf.jsonl"}
ORDER_LAB = ["off", "F1", "F1N2", "F2", "F2g", "F2g25", "F3", "F3b", "F4", "F4lit", "F1F3", "F1N2F3", "F1F2F3", "F1F2F3F4", "off2",
             "F2_allSE", "F2g_allSE", "F1F2F3_allSE", "F1F2F3F4_allSE", "F1bref", "F1b0", "F1bF3", "F1bF4", "F1bF3F4"]
for l in ORDER_LAB:
    f = D + (f"/replays/main.{l}.jsonl" if l != "F1bref" else "/replays/main.v3-extra.jsonl")
    if os.path.exists(f) and sum(1 for _ in open(f)) >= 97: files[l] = f
args = [f"{l}={f}={KIT}" for l, f in files.items()]
kf, cs = D + "/kfull.json", D + "/cmstage.json"
subprocess.run(["python3", "-I", CM + "/tools/score_kfull.py", CM + "/aggregates/coverage-pool.json", kf] + args, capture_output=True, check=True)
subprocess.run(["python3", "-I", CM + "/tools/cm_stage.py", cs] + args, capture_output=True, check=True)
K = json.load(open(kf)); CMS = json.load(open(cs)); O = json.load(open(CM + "/aggregates/cm-oracle.json"))
GOLD = json.load(open(CM + "/sefix/gold_cm40.json"))
AUT = json.load(open(CM + "/autopsy52/autopsy52.json"))["items"]
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
def strict_cm(lab, i):  # a fact chunk of the item's source thread is in keptFull (gold_cm.json)
    g = GOLD.get(i)
    if not g: return False
    gch = {f"pack:local-{g['pack']}:{f['chunk_id']}" for f in g["facts"]}
    return any(c["chunkId"] in gch for c in rows[lab][i]["keptFull"])
res = {"labels": {}, "ids52": [i for i in AUT]}
ctl_k = {i: stage(CTL, i) == "K" for i in ids}
junk_ids = [i for i in ids if not ctl_k[i]]
for lab in files:
    st = {i: stage(lab, i) for i in ids}; kv = {i: st[i] == "K" for i in ids}
    rr = rows[lab]
    walls = [rr[i]["wallMs"] for i in ids if rr[i].get("wallMs") is not None]
    own_junk = [i for i in ids if not kv[i]]
    e = dict(kept92=sum(kv.values()), kept_v01=sum(kv[i] for i in v01), kept_cm=sum(kv[i] for i in cmi),
             strict_cm=sum(strict_cm(lab, i) for i in cmi),
             gained=[i for i in ids if kv[i] and not ctl_k[i]], lost=[i for i in ids if ctl_k[i] and not kv[i]],
             junk_ctlset_mean_kept=statistics.mean(len(rr[i]["keptFull"]) for i in junk_ids),
             junk_ownset_mean_kept=statistics.mean(len(rr[i]["keptFull"]) for i in own_junk), junk_ownset_n=len(own_junk),
             junk_bothset_mean_kept=statistics.mean(len(rr[i]["keptFull"]) for i in ids if not kv[i] and not ctl_k[i]),
             junk_bothset_ctl_mean_kept=statistics.mean(len(rows[CTL][i]["keptFull"]) for i in ids if not kv[i] and not ctl_k[i]), junk_bothset_n=sum(1 for i in ids if not kv[i] and not ctl_k[i]),
             mean_kept=statistics.mean(len(rr[i]["keptFull"]) for i in ids), kept_tokens=statistics.mean(sum(tok(c) for c in rr[i]["keptFull"]) for i in ids),
             wall_ms_mean=statistics.mean(walls), wall_ms_p50=statistics.median(walls),
             kept_changed_vs_ctl=sum([c["chunkId"] for c in rr[i]["keptFull"]] != [c["chunkId"] for c in rows[CTL][i]["keptFull"]] for i in ids),
             kept_list=[i for i in ids if kv[i]])
    # recovery of the AUTOPSY52 items (the 52 = fact in a pack, not kept under ctl) and of its 36 cm part
    e["rec52"] = [i for i in AUT if kv.get(i)]; e["rec36"] = [i for i in AUT if kv.get(i) and AUT[i]["set"] == "cm"]
    e["rec52_strict_cm"] = [i for i in cmi if strict_cm(lab, i) and not strict_cm(CTL, i)]
    e["added_chunks_selead"] = sum(c.startswith("headpass:selead:add:") for i in ids for c in rr[i]["reasonCodes"])
    e["reason_counts"] = {k: sum(any(c.startswith(k) for c in rr[i]["reasonCodes"]) for i in ids) for k in ("headpass:selead:add", "grounding:health-fallback-subject", "grounding:keep-noproper-restored", "headpass:budget:dropped", "grounding:health-no-source")}
    if "F1bref" in files:
        fk = {i: stage("F1bref", i) == "K" for i in ids}
        e["vs_F1b_gained"] = [i for i in ids if kv[i] and not fk[i]]; e["vs_F1b_lost"] = [i for i in ids if fk[i] and not kv[i]]
    res["labels"][lab] = e
# DELIVERS (QFORM clause filled by score_qform.py later; here with the QFORM value None)
ctl92 = res["labels"][CTL]["kept92"]
for lab, e in res["labels"].items():
    e["junk_ratio_ctlset"] = e["junk_ctlset_mean_kept"] / res["labels"][CTL]["junk_ctlset_mean_kept"]
    e["junk_ratio_ownset"] = e["junk_ownset_mean_kept"] / res["labels"][CTL]["junk_ownset_mean_kept"]
    e["junk_ratio_bothset"] = e["junk_bothset_mean_kept"] / e["junk_bothset_ctl_mean_kept"]
    # frozen rule, junk read literally = items with no fact in any kept chunk, per run (ownset); the other two reads are reported beside it
    e["delivers_main"] = e["kept92"] >= ctl92 + 8 and len(e["lost"]) <= 2 and e["junk_ratio_ownset"] <= 1.15
    e["junk_reads_all_ok"] = max(e["junk_ratio_ownset"], e["junk_ratio_ctlset"], e["junk_ratio_bothset"]) <= 1.15
    e["kept_tokens_ratio"] = e["kept_tokens"] / res["labels"][CTL]["kept_tokens"]
json.dump(res, open(D + "/sefix.json", "w"), indent=1)
print("label kept92 v01 cm strictcm gained lost junk(ctlset)x junk(own)x junk(both)x ktok x wall mean_kept rec36 changed deliversMAIN allJunkReadsOK")
for lab, e in res["labels"].items():
    print(lab, e["kept92"], e["kept_v01"], e["kept_cm"], e["strict_cm"], len(e["gained"]), len(e["lost"]), round(e["junk_ratio_ctlset"], 3), round(e["junk_ratio_ownset"], 3), round(e["junk_ratio_bothset"], 3),
          round(e["kept_tokens_ratio"], 3), round(e["wall_ms_mean"]), round(e["mean_kept"], 2), len(e["rec36"]), e["kept_changed_vs_ctl"], e["delivers_main"], e["junk_reads_all_ok"])
