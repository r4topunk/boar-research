"""SEFIX QFORM 432 six-file read (0 LLM): hit@kept pooled, paired vs qform.v2-off (g2-fullkit/runs), junk-kept, ctx tokens, wall.
python3 -I tools/score_qform.py -> qform.json. Preamble = g2-fullkit/score_g2.py (sweep.py's QFORM loader)."""
import json, os, statistics, sys, glob
R = "<workspace>/rnd/research/coordinator/arms/retrieve-sweep"; H = R + "/g2-fullkit"; D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(R + "/tools/sweep.py").read().split("\n")
i0 = next(i for i, l in enumerate(src) if l.startswith("import glob")); i1 = next(i for i, l in enumerate(src) if l.startswith("# ----") and "arm files" in l)
j0 = next(i for i, l in enumerate(src) if l.startswith("# ----") and "QFORM" in l); j1 = next(i for i, l in enumerate(src) if l.startswith("Q = {a: load_q"))
__file__ = H + "/score_g2.py"
exec("\n".join(src[i0:i1]) + "\n" + "\n".join(src[j0:j1]))
files = {"v2off": H + "/runs/qform.v2-off.jsonl", "q6gidf": R + "/h4-merge/replays/q6.gidf.jsonl"}
for f in sorted(glob.glob(D + "/replays/qform.*.jsonl")): files[os.path.basename(f)[6:-6]] = f
Qs = {a: load_q(f) for a, f in files.items() if sum(1 for _ in open(f)) >= 432}
ctl = Qs["v2off"]; junk = [i for i in IDS if not ctl[i]["wide"]]
def d_ci(a, b, ids):
    va = {i: int(Qs[a][i]["kept"]) for i in ids}; vb = {i: int(Qs[b][i]["kept"]) for i in ids}
    d, lo, hi = boot(va, vb, [[i] for i in ids])
    fu = {}
    for i in ids: fu.setdefault(items[i]["fact_id"], []).append(i)
    dc, loc, hic = boot(va, vb, list(fu.values()))
    return dict(d=d * 100, ci=[lo * 100, hi * 100], ci_fact=[loc * 100, hic * 100], gained=sum(va[i] > vb[i] for i in ids), lost=sum(va[i] < vb[i] for i in ids))
res = {"n": len(IDS), "junk_set_n": len(junk), "arms": {}, "vs_v2off": {}, "vs_q6gidf": {}}
for a, q in Qs.items():
    walls = [q[i]["wall"] for i in IDS if q[i]["wall"] is not None]
    res["arms"][a] = dict(hit_kept_n=sum(q[i]["kept"] for i in IDS), hit_raw_n=sum(q[i]["raw"] for i in IDS), junk_kept=statistics.mean(q[i]["nk"] for i in junk), mean_kept=statistics.mean(q[i]["nk"] for i in IDS),
        kept_tokens=statistics.mean(q[i]["ktok"] for i in IDS), wall_ms_mean=statistics.mean(walls), kept_ids_changed_vs_v2off=sum(q[i]["ids"] != ctl[i]["ids"] for i in IDS),
        kept_ids_changed_vs_q6gidf=sum(q[i]["ids"] != Qs["q6gidf"][i]["ids"] for i in IDS) if "q6gidf" in Qs else None)
    if a not in ("v2off", "q6gidf"):
        res["vs_v2off"][a] = d_ci(a, "v2off", IDS)
        if "q6gidf" in Qs: res["vs_q6gidf"][a] = d_ci(a, "q6gidf", IDS)
json.dump(res, open(D + "/r34.qform.json", "w"), indent=1)
for a, e in res["arms"].items():
    v = res["vs_v2off"].get(a); g = res["vs_q6gidf"].get(a)
    print(a, e["hit_kept_n"], "junk", round(e["junk_kept"], 3), "wall", round(e["wall_ms_mean"]), "changed_v2off", e["kept_ids_changed_vs_v2off"],
          "vs v2off", None if not v else (round(v["d"], 2), [round(x, 1) for x in v["ci"]], v["gained"], v["lost"]),
          "vs q6gidf", None if not g else (round(g["d"], 2), [round(x, 1) for x in g["ci"]], g["gained"], g["lost"]))
