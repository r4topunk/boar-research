#!/usr/bin/env python3
"""BATCHRET-PHONE A/B comparison on litelat-9 (runs batchret-1a/3a = A, batchret-2b/4b = B).

Uses LITELAT's analyze.py for per-question spans (retrieve wall, pack SQL calls/ms, prefill, TTFT, total).
Identity per question: retrievedTitles (row), retrieve event n/k, reason codes context:X->Y, prompt tokens (promptN).
usage: compare_ab.py [--json out.json]
"""
import json, statistics as st, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "litelat"))
import analyze  # noqa: E402

RES = Path("<workspace>/handoff/pixel8-2026-10-20/bench/results")
RUNS = {"A": ["batchret-1a", "batchret-3a"], "B": ["batchret-2b", "batchret-4b"]}
KEYS = ["retrieve", "wikipacks", "packSqlN", "packSqlMs", "pre", "post", "prefill", "promptN", "ttft", "total", "decode", "tokS"]


def load_run(rid):
    rows, bench, tl = analyze.load(RES / rid)
    out = {}
    for i, r in enumerate(rows):
        q = tl[i] if i < len(tl) else None
        p = analyze.per_question(r, q)
        ret = [x for x in (q["items"] if q else []) if x.get("kind") == "retrieve"]
        p["ident"] = {
            "titles": r.get("retrievedTitles"),
            "retrieveNK": [(x.get("n"), x.get("k")) for x in ret],
            "context": [c for c in (r.get("reasonCodes") or []) if c.startswith("context:")],
            "promptN": p["promptN"],
            "declined": r.get("declined"),
        }
        p["group"] = "model" if (p["model"] or "").startswith("qwen") else ("card" if p["nRetrieve"] else "other")
        out[r["queryId"]] = p
    return out, bench.get("engine") or bench.get("engineTree") or None


def med(v):
    return round(st.median(v), 1) if v else None


def main():
    runs = {rid: load_run(rid)[0] for arm in RUNS.values() for rid in arm}
    ids = list(runs[RUNS["A"][0]].keys())
    report = {"perRun": {}, "pooled": {}, "paired": {}, "identity": {}}
    for rid, per in runs.items():
        report["perRun"][rid] = {g: {k: med([p[k] for p in per.values() if p["group"] == g and p.get(k) is not None]) for k in KEYS}
                                 for g in ("model", "card")}
    for arm, rids in RUNS.items():
        report["pooled"][arm] = {g: {k: med([runs[r][i][k] for r in rids for i in ids if runs[r][i]["group"] == g and runs[r][i].get(k) is not None])
                                     for k in KEYS} for g in ("model", "card")}
    # paired: per question, mean(B runs) - mean(A runs); median over questions of the group
    for g in ("model", "card"):
        gi = [i for i in ids if all(runs[r][i]["group"] == g for r in runs)]
        report["paired"][g] = {"n": len(gi)}
        for k in KEYS:
            d = []
            for i in gi:
                a = [runs[r][i][k] for r in RUNS["A"] if runs[r][i].get(k) is not None]
                b = [runs[r][i][k] for r in RUNS["B"] if runs[r][i].get(k) is not None]
                if a and b:
                    d.append(st.mean(b) - st.mean(a))
            report["paired"][g][k] = {"medianDelta": med(d), "min": round(min(d), 1) if d else None, "max": round(max(d), 1) if d else None}
    # identity
    for i in ids:
        ident = {r: runs[r][i]["ident"] for r in runs}
        same = {f: len({json.dumps(v[f]) for v in ident.values()}) == 1 for f in ("titles", "retrieveNK", "context", "promptN", "declined")}
        report["identity"][i] = {"group": runs[RUNS["A"][0]][i]["group"], "same": same, "values": ident}
    report["perQuestion"] = {i: {r: {k: runs[r][i].get(k) for k in KEYS} for r in runs} for i in ids}
    print(json.dumps({k: report[k] for k in ("perRun", "pooled", "paired")}, indent=1))
    for i, v in report["identity"].items():
        print(i, v["group"], v["same"], v["values"][RUNS["A"][0]]["titles"])
    if "--json" in sys.argv:
        Path(sys.argv[sys.argv.index("--json") + 1]).write_text(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
