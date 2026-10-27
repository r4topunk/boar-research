"""SEARCHPAR R1 QFORM 432 six-file read (0 LLM): hit@kept pooled, paired vs the R1-off run on the same tree (and vs g2-fullkit v3-extra, v2-off). python3 -I score_qform.py <label>... -> r1.qform.json"""
import json, os, statistics, sys
H = os.path.dirname(os.path.abspath(__file__)); R = "<workspace>/rnd/research/coordinator/arms/retrieve-sweep"; G = R + "/g2-fullkit"
src = open(R + "/tools/sweep.py").read().split("\n")
i0 = next(i for i, l in enumerate(src) if l.startswith("import glob")); i1 = next(i for i, l in enumerate(src) if l.startswith("# ----") and "arm files" in l)
j0 = next(i for i, l in enumerate(src) if l.startswith("# ----") and "QFORM" in l); j1 = next(i for i, l in enumerate(src) if l.startswith("Q = {a: load_q"))
__file__ = G + "/score_g2.py"
exec("\n".join(src[i0:i1]) + "\n" + "\n".join(src[j0:j1]))
files = {"v2off": G + "/runs/qform.v2-off.jsonl", "v3extra": G + "/runs/qform.v3-extra.jsonl"}
for l in sys.argv[1:]: files[l] = H + f"/replays/qform.{l}.jsonl"
Qs = {a: load_q(f) for a, f in files.items() if os.path.exists(f) and sum(1 for _ in open(f)) >= 432}
ctl = Qs["v2off"]; junk = [i for i in IDS if not ctl[i]["wide"]]
def d_ci(a, b, ids):
    va = {i: int(Qs[a][i]["kept"]) for i in ids}; vb = {i: int(Qs[b][i]["kept"]) for i in ids}
    d, lo, hi = boot(va, vb, [[i] for i in ids])
    fu = {}
    for i in ids: fu.setdefault(items[i]["fact_id"], []).append(i)
    dc, loc, hic = boot(va, vb, list(fu.values()))
    return dict(d=d * 100, ci=[lo * 100, hi * 100], ci_fact=[loc * 100, hic * 100], gained=sum(va[i] > vb[i] for i in ids), lost=sum(va[i] < vb[i] for i in ids))
FORMS_ = sorted(set(items[i]["form"] for i in IDS)); PKS = sorted(set(items[i]["pack"] for i in IDS))
res = {"n": len(IDS), "junk_set_n": len(junk), "arms": {}, "vs": {}}
for a, q in Qs.items():
    walls = [q[i]["wall"] for i in IDS if q[i]["wall"] is not None]
    res["arms"][a] = dict(hit_kept_n=sum(q[i]["kept"] for i in IDS), hit_raw_n=sum(q[i]["raw"] for i in IDS), hit_wide_n=sum(q[i]["wide"] for i in IDS), junk_kept=statistics.mean(q[i]["nk"] for i in junk), mean_kept=statistics.mean(q[i]["nk"] for i in IDS),
        kept_tokens=statistics.mean(q[i]["ktok"] for i in IDS), wall_ms_mean=statistics.mean(walls), kept_changed_vs_v3extra=sum(q[i]["ids"] != Qs["v3extra"][i]["ids"] for i in IDS),
        by_form={f: sum(q[i]["kept"] for i in IDS if items[i]["form"] == f) for f in FORMS_}, by_pack={p: sum(q[i]["kept"] for i in IDS if items[i]["pack"] == p) for p in PKS})
for a in Qs:
    if a in ("v2off", "v3extra"): continue
    for b in ("off", "v3extra", "v2off"):
        if b in Qs and b != a:
            res["vs"][f"{a}-{b}"] = dict(pooled=d_ci(a, b, IDS), by_form={f: d_ci(a, b, [i for i in IDS if items[i]["form"] == f]) for f in FORMS_}, by_pack={p: d_ci(a, b, [i for i in IDS if items[i]["pack"] == p]) for p in PKS})
json.dump(res, open(H + "/r1.qform.json", "w"), indent=1)
for a, e in res["arms"].items():
    print(a, "kept", e["hit_kept_n"], "raw", e["hit_raw_n"], "wide", e["hit_wide_n"], "junk", round(e["junk_kept"], 3), "ktok", round(e["kept_tokens"]), "wall", round(e["wall_ms_mean"]), "changed_vs_v3extra", e["kept_changed_vs_v3extra"])
for k, v in res["vs"].items():
    p = v["pooled"]; print(k, round(p["d"], 2), [round(x, 1) for x in p["ci"]], "gained/lost", p["gained"], p["lost"])
