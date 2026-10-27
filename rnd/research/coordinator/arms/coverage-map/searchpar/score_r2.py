"""COMPOSE scoring (0 LLM). python3 -I tools/score_compose.py -> compose.json (+ prints the curves).
Stage per MAIN-92 keyed item = coverage-map's: lexical FACTPRESENT stage (score_kfull.py) best-of the cm oracle (cm_stage.py) for the 40 cooking/money self-tests
(as h4-merge/kfull-funnel: K = kept). Crowding, kept tokens, wall, funnel ids, rule verdicts computed here."""
import json, os, re, subprocess, sys, statistics, math, importlib.util, unicodedata, glob
D = "<workspace>/rnd/research/coordinator/arms/coverage-map/compose"
SF = "<workspace>/rnd/research/coordinator/arms/coverage-map/sefix"
CM = "<workspace>/rnd/research/coordinator/arms/coverage-map"; CO = "<workspace>/rnd/research/coordinator/"
R = CO + "arms/retrieve-sweep"; BE = "<workspace>/boar-eval/bench/"
sys.path.insert(0, D + "/tools"); import kits
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
# present(), QS, facts rule: exec'd verbatim from sweep.py exactly as score_kfull.py does
src = open(R + "/tools/sweep.py").read().split("\n")
a = next(i for i, l in enumerate(src) if l.startswith("spec = importlib.util.spec_from_file_location"))
b = next(i for i, l in enumerate(src) if l.startswith("FUN = json.load"))
__file__ = R + "/tools/sweep.py"
exec("\n".join(src[a:b]))
NS = [10]
LABS = {"N10.gidf": D + "/replays/main.N10.gidf.jsonl", "v2-extra": SF + "/replays/main.v2-extra.jsonl", "v3-extra": SF + "/replays/main.v3-extra.jsonl"}
LABS.update({k: CM + f"/searchpar/r2/replays/main.{k}.jsonl" for k in sys.argv[1:]})
args = []; labs = []
for lab, f in LABS.items():
    if os.path.exists(f) and sum(1 for _ in open(f)) >= 97:
        args.append(f"{lab}={f}=" + ",".join(os.path.basename(p)[:-7] for p in kits.kit(10))); labs.append((10, lab))
kf = CM + "/searchpar/r2/r2.kfull.json"; cs = CM + "/searchpar/r2/r2.cmstage.json"
subprocess.run(["python3", "-I", CM + "/tools/score_kfull.py", CM + "/aggregates/coverage-pool.json", kf] + args, capture_output=True, check=True)
subprocess.run(["python3", "-I", CM + "/tools/cm_stage.py", cs] + args, capture_output=True, check=True)
K = json.load(open(kf)); CMS = json.load(open(cs)); POOLJ = json.load(open(CM + "/aggregates/coverage-pool.json"))["items"]
O = json.load(open(CM + "/aggregates/cm-oracle.json"))
items = K["items"]; ORDER = {"S1": 0, "S2": 1, "S3": 2, "K": 3}
S23 = [l.strip() for l in open(CO + "arms/qform/funnel-S2S3.ids") if l.strip()]
FUNJ = json.load(open(CO + "ruler/RAG-FUNNEL-2026-10-21.json"))["items"]
S45 = sorted(i for i, v in FUNJ.items() if v["K1"]["vstage"] in ("S4", "S5"))
pk_of = lambda c: re.match(r"^pack:(?:local-)?([^:]+):", c["chunkId"]).group(1) if c["chunkId"].startswith("pack:") else c["chunkId"].split(":")[0]
tok = lambda c: math.ceil(len(f"{c['title']}\n{c['body']}") / 4)
def stage(lab, i):
    s = items[i][lab]["stage"]
    if i in O:
        o = CMS[lab]["items"].get(i)
        if o and ORDER[o] > ORDER[s]: s = o
    return s
res = {"labels": {}, "kits": {n: [os.path.basename(p)[:-7] for p in kits.kit(n)] for n in NS}}
for (n, v) in labs:
    lab = v; rows = {r["id"]: r for r in rd(LABS[lab])}
    kit = [os.path.basename(p)[:-7] for p in kits.kit(n)]
    ids = list(items)
    st = {i: stage(lab, i) for i in ids}
    cnt = lambda sub: {s: sum(st[i] == s for i in sub) for s in ("S1", "S2", "S3", "K")}
    v01 = [i for i in ids if items[i]["set"] == "v0.1"]; cmi = [i for i in ids if items[i]["set"] == "cm"]
    kept_ids = [i for i in ids if st[i] == "K"]
    # crowding: on items whose fact is kept, share of kept slots in packs other than the fact's pack(s)
    tot = oth = joint = 0; own_cnt = {}
    for i in kept_ids:
        ks = rows[i]["keptFull"]
        carriers = [c for c in ks if present(i, [c])]
        if i in O:
            doc = f"pack:local-{O[i]['pack']}:a{O[i]['article_id']}"
            carriers += [c for c in ks if c.get("docId") == doc and c not in carriers]
        own = {pk_of(c) for c in carriers}
        if not own:
            joint += 1; own = {p for p in POOLJ[i]["packs"] if p in kit} if i in POOLJ else set()
        for c in ks:
            tot += 1; oth += pk_of(c) not in own
    kv = {i: st[i] == "K" for i in ids}
    walls = [rows[i].get("wallMs") for i in ids if rows[i].get("wallMs") is not None]
    slots = {}
    for i in ids:
        for c in rows[i]["keptFull"]: slots[pk_of(c)] = slots.get(pk_of(c), 0) + 1
    gt = sum(slots.values())
    res["labels"][lab] = dict(N=n, merge=v, n_packs=len(kit), kept_main92=len(kept_ids), kept_v01=sum(kv[i] for i in v01), kept_cm40=sum(kv[i] for i in cmi),
        stages_main92=cnt(ids), stages_v01=cnt(v01), stages_cm=cnt(cmi),
        mean_kept=statistics.mean(len(rows[i]["keptFull"]) for i in ids), kept_tokens=statistics.mean(sum(tok(c) for c in rows[i]["keptFull"]) for i in ids),
        crowding_other_pack_share=(oth / tot if tot else None), crowd_items=len(kept_ids), crowd_slots=tot, crowd_joint_items=joint,
        wall_ms_mean=statistics.mean(walls), wall_ms_p50=statistics.median(walls),
        ids25_kept=sum(kv[i] for i in S23), ids22_kept=sum(kv[i] for i in S45),
        slot_share_top={p: round(c / gt, 3) for p, c in sorted(slots.items(), key=lambda x: -x[1])[:5]}, slot_share_all={p: c / gt for p, c in slots.items()},
        kept_list=kept_ids)
    res["labels"][lab]["_kv"] = kv

for lab, e in res["labels"].items():
    e.pop("_kv", None)
json.dump(res, open(CM + "/searchpar/r2/r2.scored.json", "w"), indent=1)
for lab, e in res["labels"].items():
    print(lab, {k: e[k] for k in ("kept_main92","kept_v01","kept_cm40","stages_main92","mean_kept","kept_tokens","wall_ms_mean","wall_ms_p50","ids25_kept","ids22_kept","crowding_other_pack_share")})
