#!/usr/bin/env python3
"""COVERAGE-MAP funnel read of a replay (0 LLM). Per MAIN keyed item (92): stage under the kit of that replay.
  S1 no kit pack holds the fact (coverage-pool.json, RAG-FUNNEL pack rule) and it is not retrieved/kept
  S2 a kit pack holds it, not among the retrieved candidates (rawFull U wideFull-12)
  S3 retrieved (FACTPRESENT rule over the union of candidate chunks), not kept
  K  kept (FACTPRESENT PRESENT on keptFull) = S4+S5 (no generation, so no S4/S5 split)
present() / share rules exec'd verbatim from retrieve-sweep/tools/sweep.py.
Usage: python3 -I score_kfull.py <pool json> <out json> <label>=<replay jsonl>=<kit csv of pack ids> ..."""
import json, sys, re, os, glob, unicodedata, importlib.util
CO = "<workspace>/rnd/research/coordinator/"; R = CO + "arms/retrieve-sweep"; BE = "<workspace>/boar-eval/bench/"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
src = open(R + "/tools/sweep.py").read().split("\n")
a = next(i for i, l in enumerate(src) if l.startswith("spec = importlib.util.spec_from_file_location"))
b = next(i for i, l in enumerate(src) if l.startswith("FUN = json.load"))
exec("\n".join(src[a:b]))
POOL = json.load(open(sys.argv[1]))["items"]; OUT = sys.argv[2]
FUN = json.load(open(CO + "ruler/RAG-FUNNEL-2026-10-21.json"))["items"]
pk_of = lambda c: re.match(r"^pack:(?:local-)?([^:]+):", c["chunkId"]).group(1) if c["chunkId"].startswith("pack:") else c["chunkId"].split(":")[0]
res = {"arms": {}, "items": {}}
for arg in sys.argv[3:]:
    lab, fn, kit = arg.split("="); kit = kit.split(","); rows = {r["id"]: r for r in rd(fn)}
    cnt = {"v0.1": {}, "cm": {}}
    for i, p in POOL.items():
        r = rows[i]; cands = {c["chunkId"]: c for c in r["rawFull"] + r.get("wideFull", [])}.values()
        kept = present(i, r["keptFull"]); retr = present(i, list(cands)) if cands else False
        inpk = sorted(k for k in p["packs"] if k in kit)
        st = "K" if kept else "S3" if retr else "S2" if inpk else "S1"
        kp = sorted({pk_of(c) for c in r["keptFull"]})
        res["items"].setdefault(i, {"set": p["set"], "tag": p["tag"], "funnel_K1": FUN[i]["K1"]["vstage"], "funnel_K3": FUN[i]["K3"]["vstage"]})[lab] = dict(stage=st, inpack=inpk, kept_packs=kp, n_kept=len(r["keptFull"]))
        cnt[p["set"]][st] = cnt[p["set"]].get(st, 0) + 1
    tot = {s: cnt["v0.1"].get(s, 0) + cnt["cm"].get(s, 0) for s in ("S1", "S2", "S3", "K")}
    share_kept = {}
    for i in POOL:
        for k in {pk_of(c) for c in rows[i]["keptFull"]}: share_kept[k] = share_kept.get(k, 0) + 1
    slots = {}
    for i in POOL:
        for c in rows[i]["keptFull"]: slots[pk_of(c)] = slots.get(pk_of(c), 0) + 1
    res["arms"][lab] = dict(kit=kit, MAIN92=tot, v01_52={s: cnt["v0.1"].get(s, 0) for s in ("S1", "S2", "S3", "K")}, cm40={s: cnt["cm"].get(s, 0) for s in ("S1", "S2", "S3", "K")},
                            kept_slots_by_pack=dict(sorted(slots.items(), key=lambda x: -x[1])), mean_kept=sum(len(rows[i]["keptFull"]) for i in POOL) / len(POOL),
                            wall_ms_mean=sum(rows[i].get("wallMs") or 0 for i in POOL) / len(POOL))
    print(lab, json.dumps(res["arms"][lab]))
json.dump(res, open(OUT, "w"), indent=1)
