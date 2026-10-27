"""COMPOSE scoring (0 LLM). python3 -I tools/score_compose.py -> compose.json (+ prints the curves).
Stage per MAIN-92 keyed item = coverage-map's: lexical FACTPRESENT stage (score_kfull.py) best-of the cm oracle (cm_stage.py) for the 40 cooking/money self-tests
(as h4-merge/kfull-funnel: K = kept). Crowding, kept tokens, wall, funnel ids, rule verdicts computed here."""
import json, os, re, subprocess, sys, statistics, math, importlib.util, unicodedata, glob
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
NS = [0, 2, 4, 6, 8, 10]; VS = ["stock", "gidf"]
args = []; labs = []
for n in NS:
    ids = ",".join(os.path.basename(p)[:-7] for p in kits.kit(n))
    for v in VS:
        f = D + f"/replays/main.N{n}.{v}.jsonl"
        if os.path.exists(f) and sum(1 for _ in open(f)) >= 97: args.append(f"N{n}.{v}={f}={ids}"); labs.append((n, v))
kf = D + "/kfull.json"; cs = D + "/cmstage.json"
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
    lab = f"N{n}.{v}"; rows = {r["id"]: r for r in rd(D + f"/replays/main.N{n}.{v}.jsonl")}
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
# deltas
base = "N0.stock"
for lab, e in res["labels"].items():
    n, v = e["N"], e["merge"]; kv = e.pop("_kv")
    e["_kvh"] = kv
for lab, e in res["labels"].items():
    kv = e["_kvh"]; n, v = e["N"], e["merge"]
    if base in res["labels"]:
        b = res["labels"][base]["_kvh"]
        e["rec25_vs_N0stock"] = [i for i in S23 if kv[i] and not b[i]]; e["loss22_vs_N0stock"] = [i for i in S45 if b[i] and not kv[i]]
        e["gained_vs_N0stock"] = [i for i in kv if kv[i] and not b[i]]; e["lost_vs_N0stock"] = [i for i in kv if b[i] and not kv[i]]
    prev = max([m for m in NS if m < n and f"N{m}.{v}" in res["labels"]], default=None)
    if prev is not None:
        p = res["labels"][f"N{prev}.{v}"]["_kvh"]
        e["step_from"] = prev; e["step_net"] = e["kept_main92"] - res["labels"][f"N{prev}.{v}"]["kept_main92"]
        e["step_gained"] = [i for i in kv if kv[i] and not p[i]]; e["step_lost"] = [i for i in kv if p[i] and not kv[i]]
    sm = f"N{n}.stock"
    if v == "gidf" and sm in res["labels"]:
        s = res["labels"][sm]["_kvh"]; e["gidf_vs_stock_gained"] = [i for i in kv if kv[i] and not s[i]]; e["gidf_vs_stock_lost"] = [i for i in kv if s[i] and not kv[i]]
for e in res["labels"].values(): e.pop("_kvh", None)
# ---- frozen rule (COMPOSE-criterion.md, sha 2d071770)
def curve(v): return [(n, res["labels"][f"N{n}.{v}"]) for n in NS if f"N{n}.{v}" in res["labels"]]
rule = {}
for v in VS:
    c = curve(v)
    if len(c) < len(NS): rule[v] = "incomplete"; continue
    kept = [e["kept_main92"] for n, e in c]; v01 = [e["kept_v01"] for n, e in c]
    steps = [kept[j] - kept[j - 1] for j in range(1, len(kept))]
    out = dict(kept=kept, v01=v01, steps=steps,
               nondecreasing=all(s >= -1 for s in steps), n10_ge_base6_same_merge=kept[-1] >= kept[0] + 6, n10_ge_base6_stock_n0=kept[-1] >= res["labels"]["N0.stock"]["kept_main92"] + 6,
               v01_ge_base_same_merge=all(x >= v01[0] for x in v01), v01_ge_base_stock_n0=all(x >= res["labels"]["N0.stock"]["kept_v01"] for x in v01),
               crowds=any(s <= -3 for s in steps))
    out["composes_same_merge_base"] = out["nondecreasing"] and out["n10_ge_base6_same_merge"] and out["v01_ge_base_same_merge"]
    out["composes_stock_n0_base"] = out["nondecreasing"] and out["n10_ge_base6_stock_n0"] and out["v01_ge_base_stock_n0"]
    out["verdict"] = "CROWDS" if out["crowds"] else "COMPOSES" if out["composes_same_merge_base"] else "NEITHER (no COMPOSES, no CROWDS)"
    rule[v] = out
res["rule"] = rule
if all(isinstance(r, dict) for r in rule.values()):
    cand = [(e["kept_main92"], -n, 1 if v == "gidf" else 0, f"N{n}.{v}") for (n, v) in labs for e in [res["labels"][f"N{n}.{v}"]]]
    res["best_by_kept"] = sorted(cand, reverse=True)[:4]
json.dump(res, open(D + "/compose.json", "w"), indent=1)
hdr = "label kept92 v01 cm S1/S2/S3/K mean_kept crowd% ktok wall25 ids25 ids22 rec25 loss22 step"
print(hdr)
for lab, e in res["labels"].items():
    s = e["stages_main92"]
    print(lab, e["kept_main92"], e["kept_v01"], e["kept_cm40"], f'{s["S1"]}/{s["S2"]}/{s["S3"]}/{s["K"]}', round(e["mean_kept"], 2), round(100 * (e["crowding_other_pack_share"] or 0), 1),
          round(e["kept_tokens"]), round(e["wall_ms_mean"]), e["ids25_kept"], e["ids22_kept"], len(e.get("rec25_vs_N0stock", [])), len(e.get("loss22_vs_N0stock", [])), e.get("step_net"))
print(json.dumps(rule, indent=1)); print(res.get("best_by_kept"))
