#!/usr/bin/env python3
"""DECLINE2STAGE input builder (0 calls). python3 -I decline2stage_prep.py -> ../decline2stage/in/{units.jsonl,retest.keys,opus_main.json}
Units (question + answer text only, no references):
  FLOOR-a/b/c  30 ids x 3 frozen decline variants (arms/floor-anchors/traces/fa-decline-{a,b,c}.traces.jsonl)
  MAIN         97 K0 1.7B control answers (arms/lp-screens/control/traces/lpctl-K0-main-s42.traces.jsonl; the MAIN 97 control of RV1/CV5)
  WARN         51 warned units of WARN-OPUS (strata W-nh 20 + W-h 31; text = representative arm, Opus corr = WARN-OPUS unit corr)
ref_corr = Opus judge.v1 correctness (mean of both orders; MAIN: mean over every available Opus judge.v1 pair on the identical (id, text),
found by tracesSha256 over arms/, ruler/, boar-eval/runs/); Haiku v1 corr kept beside it. Retest 20 = Random('2110-retest'): 2 per FLOOR variant, 7 MAIN, 7 WARN."""
import json, glob, hashlib, collections, os, random
R0 = "<workspace>"; C = R0 + "/rnd/research/coordinator"; A = C + "/arms"; OUT = C + "/ruler/decline2stage/in"
sha = lambda t: hashlib.sha256(t.encode()).hexdigest()
units = []
def add(set_, i, q, t, **kw): units.append(dict(key=f"{set_}|{i}|{sha(t)[:16]}", set=set_, id=i, question=q, text=t, text_sha256=sha(t), **kw))
ids30 = open(A + "/floor-anchors/decline-30.ids").read().split()
for v in "abc":
    T = {(t := json.loads(l))["itemId"]: t for l in open(f"{A}/floor-anchors/traces/fa-decline-{v}.traces.jsonl")}
    for i in ids30: add(f"FLOOR-{v}", i, T[i]["question"], T[i]["answer"]["text"])
# ---- Opus index over all judge.v1 Opus rows (by tracesSha256 -> traces file -> (id, text))
roots = [A, C + "/ruler", R0 + "/boar-eval/runs"]; rows = collections.defaultdict(lambda: collections.defaultdict(dict)); shas = set()
for r in roots:
    for f in glob.glob(r + "/**/*.jsonl", recursive=True):
        if "judg" not in os.path.basename(f): continue
        for l in open(f):
            if "opus" not in l: continue
            try: x = json.loads(l)
            except Exception: continue
            if not x.get("ok") or x.get("judgeVersion") != "judge.v1" or x.get("floorScored"): continue
            if "opus" not in str(x.get("requestedModel") or x.get("judgeModel")) or not x.get("tracesSha256"): continue
            shas.add(x["tracesSha256"]); rows[x["tracesSha256"]][x["queryId"]].setdefault(x["order"], x["mapped"]["boar"]["correctness"])
tf = {}
for r in roots:
    for f in glob.glob(r + "/**/*traces*.jsonl", recursive=True):
        h = hashlib.sha256(open(f, "rb").read()).hexdigest()
        if h in shas: tf[h] = f
idx = collections.defaultdict(list)
for h, f in sorted(tf.items()):
    T = {}
    for l in open(f):
        if l.strip(): t = json.loads(l); T[t["itemId"]] = t["answer"]["text"]
    for q, v in rows[h].items():
        if q in T and set(v) == {"boarA", "boarB"}: idx[(q, sha(T[q]))].append(dict(corr=(v["boarA"] + v["boarB"]) / 2, traces=os.path.relpath(f, R0)))
def hk(files):  # Haiku v1 corr, first ok row per (item, order)
    J = collections.defaultdict(dict)
    for p in files:
        for l in open(p):
            x = json.loads(l)
            if x.get("ok") and x["order"] not in J[x["queryId"]]: J[x["queryId"]][x["order"]] = x["mapped"]["boar"]["correctness"]
    return {q: (v["boarA"] + v["boarB"]) / 2 for q, v in J.items() if set(v) == {"boarA", "boarB"}}
MH = hk(sorted(glob.glob(f"{A}/lp-screens/control/judgments/lpctl-K0-main-s42-*.judgments.jsonl")))
opus_main = {}
for l in open(f"{A}/lp-screens/control/traces/lpctl-K0-main-s42.traces.jsonl"):
    t = json.loads(l); i, tx = t["itemId"], t["answer"]["text"]; o = idx.get((i, sha(tx)), [])
    oc = sum(x["corr"] for x in o) / len(o) if o else None
    opus_main[i] = dict(n_opus_pairs=len(o), sources=sorted({x["traces"] for x in o}))
    add("MAIN", i, t["question"], tx, opus_corr=oc, haiku_corr=MH.get(i), ref_corr=oc if oc is not None else MH.get(i),
        ref_src="opus" if oc is not None else "haiku", declined_flag=bool(t["answer"].get("declined")))
# ---- WARN-OPUS warned units
W = C + "/ruler/warn-opus"; D = json.load(open(W + "/in/set.json")); LPD = A + "/litepacks/traces"
def jload(files):
    by = collections.defaultdict(dict)
    for f in files:
        for l in open(f):
            x = json.loads(l)
            if x.get("ok") is True: by[x["queryId"]][x["order"]] = x["mapped"]
    return by
TX = {}
def trace(arm, i):
    if arm not in TX:
        TX[arm] = {}
        for f in sorted(glob.glob(f"{LPD}/lp-{arm}-*-s42.traces.jsonl")):
            for l in open(f):
                if l.strip(): t = json.loads(l); TX[arm][t["itemId"]] = t
    return TX[arm][i]
ru = jload(glob.glob(f"{A}/refuse-unsupported/ce-opus-ru/out/*.judgments.jsonl"))
for s in ("W-nh", "W-h"):
    for u in D["sample"][s]:
        j = D["judge"][u["key"]]; t = trace(j["arm"], j["id"]); tx = t["answer"]["text"]
        assert u["key"].split("|")[1] == sha(tx)[:16], u["key"]
        if j["reuse_ceopusru"]: v = ru[j["id"]]
        else:
            un = "v01" if not j["id"].startswith("st-") else j["id"][3:].rsplit("-", 1)[0]
            v = jload([f"{W}/out/{j['arm']}-{un}.judgments.jsonl"])[j["id"]]
        assert set(v) == {"boarA", "boarB"}
        oc = (v["boarA"]["boar"]["correctness"] + v["boarB"]["boar"]["correctness"]) / 2
        add("WARN", j["id"], t["question"], tx, stratum=s, opus_corr=oc, haiku_corr=u["rows"][0]["haiku_corr"], ref_corr=oc, ref_src="opus", warn_key=u["key"])
cnt = collections.Counter(u["set"] for u in units)
assert cnt == {"FLOOR-a": 30, "FLOOR-b": 30, "FLOOR-c": 30, "MAIN": 97, "WARN": 51}, cnt
assert len({u["key"] for u in units}) == len(units)
rng = random.Random("2110-retest"); ret = []
for s, k in (("FLOOR-a", 2), ("FLOOR-b", 2), ("FLOOR-c", 2), ("MAIN", 7), ("WARN", 7)):
    ret += rng.sample(sorted(u["key"] for u in units if u["set"] == s), k)
with open(OUT + "/units.jsonl", "w") as f:
    for u in units: f.write(json.dumps(u, ensure_ascii=False) + "\n")
open(OUT + "/retest.keys", "w").write("\n".join(ret) + "\n")
json.dump(opus_main, open(OUT + "/opus_main.json", "w"), indent=0)
print(dict(cnt), "retest", len(ret), "MAIN ref_src", collections.Counter(u.get("ref_src") for u in units if u["set"] == "MAIN"),
      "MAIN ref>=3", sum(u["ref_corr"] >= 3 for u in units if u["set"] == "MAIN"), "WARN opus>=3", sum(u["ref_corr"] >= 3 for u in units if u["set"] == "WARN"))
