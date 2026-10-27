"""H4b scoring (derived from score_h4.py: variants off / gidf (H4 replays) / gidf2 (rs-H4b) + identity reruns). Original docstring: H4-MERGE scoring (0 LLM). python3 -I tools/score_h4.py -> h4.json (+ prints tables).
QFORM: sweep.py's loader/bootstrap (exec of its helper block, as score_g2.py). MAIN: score_kfull.py (coverage-map) for the stage of every
keyed item, then kept counts / gained-lost / 25-22 funnel ids / kept-slot share per pack."""
import json, os, statistics, subprocess, sys, collections
R = "<workspace>/rnd/research/coordinator/arms/retrieve-sweep"; H = R + "/h4-merge"; CM = "<workspace>/rnd/research/coordinator/arms/coverage-map"
src = open(R + "/tools/sweep.py").read().split("\n")
i0 = next(i for i, l in enumerate(src) if l.startswith("import glob")); i1 = next(i for i, l in enumerate(src) if l.startswith("# ----") and "arm files" in l)
j0 = next(i for i, l in enumerate(src) if l.startswith("# ----") and "QFORM" in l); j1 = next(i for i, l in enumerate(src) if l.startswith("Q = {a: load_q"))
__file__ = R + "/tools/sweep.py"
exec("\n".join(src[i0:i1]) + "\n" + "\n".join(src[j0:j1]))
QF = os.path.join(ARMS_DIR, "qform"); H = R + "/h4-merge"
PK = ["boar-factbook", "boar-firstaid-en", "boar-medlineplus-en", "boar-crypto", "boar-wikivoyage-en", "boar-visa-en"]
pack_of = {i: items[i]["pack"] for i in IDS}
res = {"qform": {}, "main": {}}
# ------------------------------------------------------------ QFORM
runs = {  # block: (control file used for the paired test, {variant: file}, own rerun of the control = identity / wall)
    "merged": (QF + "/replay/qform.replay.jsonl", {"off": H + "/replays/qm.off.jsonl", "gidf": H + "/replays/qm.gidf.jsonl", "gidf2": H + "/replays/qm.h4b-g2.jsonl"}),
    "six": (R + "/g2-fullkit/runs/qform.v2-off.jsonl", {"off": H + "/replays/q6.off.jsonl", "gidf": H + "/replays/q6.gidf.jsonl", "gidf2": H + "/replays/q6.h4b-g2.jsonl"}),
}
def dci(a, b, ids):
    va = {i: int(a[i]["kept"]) for i in ids}; vb = {i: int(b[i]["kept"]) for i in ids}
    d, lo, hi = boot(va, vb, [[i] for i in ids]); fu = {}
    for i in ids: fu.setdefault(items[i]["fact_id"], []).append(i)
    dc, loc, hic = boot(va, vb, list(fu.values()))
    return dict(d=100 * d, ci=[100 * lo, 100 * hi], ci_fact=[100 * loc, 100 * hic], gained=sum(va[i] > vb[i] for i in ids), lost=sum(va[i] < vb[i] for i in ids))
for blk, (ctlf, vf) in runs.items():
    if not all(os.path.exists(f) and os.path.getsize(f) > 0 for f in vf.values()): continue
    ctl = load_q(ctlf); V = {v: load_q(f) for v, f in vf.items()}
    junk = [i for i in IDS if not ctl[i]["wide"]]
    out = {"n": len(IDS), "junk_set_n": len(junk), "control_file": os.path.relpath(ctlf, R), "variants": {}}
    out["control_identity_rerun"] = {k: sum(V["off"][i][k] == ctl[i][k] for i in IDS) for k in ("ids", "codes")}
    for v, q in list(V.items()):
        e = dict(hit_kept_n=sum(q[i]["kept"] for i in IDS), hit_raw_n=sum(q[i]["raw"] for i in IDS), hit_wide_n=sum(q[i]["wide"] for i in IDS),
                 junk_kept=statistics.mean(q[i]["nk"] for i in junk), mean_kept=statistics.mean(q[i]["nk"] for i in IDS),
                 ctx_tokens=statistics.mean([q[i]["ctx"] for i in IDS if q[i]["ctx"] is not None]), kept_tokens=statistics.mean(q[i]["ktok"] for i in IDS),
                 wall_ms_mean=statistics.mean(q[i]["wall"] for i in IDS if q[i]["wall"] is not None), wall_ms_p50=statistics.median(q[i]["wall"] for i in IDS if q[i]["wall"] is not None),
                 kept_lists_changed=sum(q[i]["ids"] != ctl[i]["ids"] for i in IDS),
                 by_form={f: sum(q[i]["kept"] for i in IDS if items[i]["form"] == f) for f in FORMS},
                 by_pack={p: sum(q[i]["kept"] for i in IDS if pack_of[i] == p) for p in PK})
        if v != "off":
            e["pooled"] = dci(q, ctl, IDS)
            if v == "gidf2":
                e["vs_gidf"] = dci(q, V["gidf"], IDS); e["vs_gidf_by_form"] = {f: dci(q, V["gidf"], [i for i in IDS if items[i]["form"] == f]) for f in FORMS}
                e["vs_gidf_by_pack"] = {p: dci(q, V["gidf"], [i for i in IDS if pack_of[i] == p]) for p in PK}
                e["kept_lists_changed_vs_gidf"] = sum(q[i]["ids"] != V["gidf"][i]["ids"] for i in IDS)
            e["by_form_delta"] = {f: dci(q, ctl, [i for i in IDS if items[i]["form"] == f]) for f in FORMS}
            e["by_pack_delta"] = {p: dci(q, ctl, [i for i in IDS if pack_of[i] == p]) for p in PK}
            e["junk_ratio"] = e["junk_kept"] / statistics.mean(ctl[i]["nk"] for i in junk)
            # crowding: share of kept slots by pack of the chunk (six files: pack = chunkId prefix)
        out["variants"][v] = e
    out["control_junk_kept"] = statistics.mean(ctl[i]["nk"] for i in junk)
    # share of kept slots whose chunk is from the item's own pack (six files only; merged = one pack)
    if blk == "six":
        pk_of = lambda cid: cid.split(":")[1].replace("local-", "") if cid.startswith("pack:") else "other"
        for v, f in vf.items():
            rows = {r["id"]: r for r in rd(f)}
            own = tot = 0; by = collections.Counter()
            for i in IDS:
                for c in rows[i]["keptFull"]:
                    tot += 1; by[pk_of(c["chunkId"])] += 1
                    own += pk_of(c["chunkId"]) == pack_of[i]
            out["variants"][v]["kept_slots_own_pack"] = own / tot; out["variants"][v]["kept_slots_by_pack"] = dict(by.most_common())
    res["qform"][blk] = out
# ------------------------------------------------------------ MAIN
KITS = ["K3", "K3CM", "K3W"]; VARS = ["off", "gidf", "gidf2"]
FN = lambda k, v: H + f"/replays/main.{k}.{'h4b-g2' if v == 'gidf2' else v}.jsonl"
args = []
for k in KITS:
    ids = ",".join(os.path.basename(p)[:-7] for p in open(CM + f"/replay/kit.{k}.txt").read().strip().split(","))
    for v in VARS:
        f = FN(k, v)
        if os.path.exists(f) and sum(1 for _ in open(f)) >= 97: args.append(f"{k}.{v}={f}={ids}")
if args:
    kf = H + "/kfull-h4b.json"
    subprocess.run(["python3", "-I", CM + "/tools/score_kfull.py", CM + "/aggregates/coverage-pool.json", kf] + args, capture_output=True, check=True)
    K = json.load(open(kf)); items_m = K["items"]
    S23 = [l.strip() for l in open(QF + "/funnel-S2S3.ids") if l.strip()]
    FUN = json.load(open(CO + "/ruler/RAG-FUNNEL-2026-10-21.json"))["items"]
    S45 = sorted(i for i, v in FUN.items() if v["K1"]["vstage"] in ("S4", "S5"))
    # cm items (cooking/money self-tests): fact home = the item's own source article (cm_stage.py oracle); stage = best of oracle and lexical,
    # as in kfull-funnel.md (K3CM kept 29). v0.1 items: lexical rule only.
    subprocess.run(["python3", "-I", CM + "/tools/cm_stage.py", H + "/cmstage-h4b.json"] + args, capture_output=True, check=True)
    CMS = json.load(open(H + "/cmstage-h4b.json"))
    kept = lambda lab, i: items_m[i][lab]["stage"] == "K" or CMS[lab]["items"].get(i) == "K"
    base = "K3.off"
    for lab in K["arms"]:
        a = K["arms"][lab]; kit, var = lab.split(".")
        ctl = f"{kit}.off"
        v01 = [i for i in items_m if items_m[i]["set"] == "v0.1"]
        kv = [i for i in items_m if items_m[i]["set"] == "v0.1"]
        e = dict(lexical_stage_MAIN92=a["MAIN92"], kept_main=sum(kept(lab, i) for i in items_m), kept_v01=sum(kept(lab, i) for i in kv), kept_cm40=sum(kept(lab, i) for i in items_m if items_m[i]["set"] == "cm"),
                 cm_oracle_counts=CMS[lab]["counts"],
                 mean_kept=a["mean_kept"], wall_ms_mean=a["wall_ms_mean"], slots=a["kept_slots_by_pack"])
        tot = sum(a["kept_slots_by_pack"].values()); e["slot_share"] = {p: n / tot for p, n in a["kept_slots_by_pack"].items()}
        e["ids25_kept"] = sum(kept(lab, i) for i in S23); e["ids22_kept"] = sum(kept(lab, i) for i in S45)
        if lab != ctl and ctl in K["arms"]:
            e["gained_vs_ctl"] = sorted(i for i in items_m if kept(lab, i) and not kept(ctl, i)); e["lost_vs_ctl"] = sorted(i for i in items_m if kept(ctl, i) and not kept(lab, i))
            e["gained_v01_vs_ctl"] = [i for i in e["gained_vs_ctl"] if items_m[i]["set"] == "v0.1"]; e["lost_v01_vs_ctl"] = [i for i in e["lost_vs_ctl"] if items_m[i]["set"] == "v0.1"]
            e["rec25_vs_ctl"] = [i for i in S23 if kept(lab, i) and not kept(ctl, i)]; e["loss22_vs_ctl"] = [i for i in S45 if kept(ctl, i) and not kept(lab, i)]
        if lab != base and base in K["arms"]:
            e["gained_vs_K3"] = sorted(i for i in items_m if kept(lab, i) and not kept(base, i)); e["lost_vs_K3"] = sorted(i for i in items_m if kept(base, i) and not kept(lab, i))
            e["gained_v01_vs_K3"] = [i for i in e["gained_vs_K3"] if items_m[i]["set"] == "v0.1"]; e["lost_v01_vs_K3"] = [i for i in e["lost_vs_K3"] if items_m[i]["set"] == "v0.1"]
        res["main"][lab] = e
    # identity of the control reruns against the coverage-map replays
    ident = {}
    for k in KITS:
        old = CM + f"/replay/main.{k}.jsonl"; new = H + f"/replays/main.{k}.h4b-off.jsonl"
        if os.path.exists(new) and os.path.getsize(new):
            o = {r["id"]: [c["chunkId"] for c in r["keptFull"]] for r in rd(old)}; n = {r["id"]: [c["chunkId"] for c in r["keptFull"]] for r in rd(new)}
            ident[k] = f"{sum(o[i] == n[i] for i in o)}/{len(o)}"
    res["main_control_identity_vs_coveragemap"] = ident
json.dump(res, open(H + "/h4b.json", "w"), indent=1)
print(json.dumps({"qform": {b: {v: {k: e[k] for k in ("hit_kept_n", "junk_kept", "mean_kept", "ctx_tokens", "wall_ms_mean")} | ({"d": round(e["pooled"]["d"], 1), "ci": [round(x, 1) for x in e["pooled"]["ci"]]} if "pooled" in e else {}) for v, e in o["variants"].items()} for b, o in res["qform"].items()},
                  "main": {l: {k: e[k] for k in ("kept_main", "kept_v01", "ids25_kept", "ids22_kept")} for l, e in res["main"].items()}, "ident": res.get("main_control_identity_vs_coveragemap")}, indent=1))
