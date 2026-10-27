#!/usr/bin/env python3
"""LITELAT comparison under the frozen rule (LITELAT-criterion.md 22c987fc). usage: compare.py <results root> [--json out]"""
import json, statistics as st, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from analyze import load, per_question

RUNS = ["litelat-00-base", "litelat-01-fa-off", "litelat-02-kvq8", "litelat-03-t5", "litelat-04-t6", "litelat-05-mlock", "litelat-07-base-repeat"]
root = Path(sys.argv[1])
therm = {json.loads(l)["label"]: json.loads(l) for l in (Path(__file__).parent / "thermal.jsonl").read_text().splitlines()}
M = {}
for r in RUNS:
    rows, bench, tl = load(root / r)
    per = [per_question(x, tl[i]) for i, x in enumerate(rows)]
    model = [p for p in per if (p["model"] or "").startswith("qwen")]
    cards = [p for p in per if not (p["model"] or "").startswith("qwen")]
    pf = [p["promptN"] / p["prefill"] * 1000 for p in model if p["prefill"]]
    M[r] = {
        "ttft": st.median(p["ttft"] for p in model), "total": st.median(p["total"] for p in model),
        "prefillTokS": st.median(pf), "decodeTokS": st.median(p["tokS"] for p in model),
        "prefillMs": st.median(p["prefill"] for p in model), "retrieve": st.median(p["retrieve"] for p in model),
        "cardTtft": st.median(p["ttft"] for p in cards), "llmInit": per[0]["llmInit"] or next((p["llmInit"] for p in per if p["llmInit"]), 0),
        "batteryC": therm.get(r, {}).get("batteryDc", 0) / 10,
        "answers": {x["queryId"]: x["answer"] for x in rows},
        "declined": sorted(x["queryId"] for x in rows if x.get("declined")),
        "outcomes": sorted({x["outcome"] for x in rows}),
        "tokens": sum(x.get("tokensGenerated") or 0 for x in rows),
    }
b, rep = M["litelat-00-base"], M["litelat-07-base-repeat"]
rel = lambda a, k: (a[k] - b[k]) / b[k]
noise = {k: max(0.05, abs(rel(rep, k))) for k in ["ttft", "total", "prefillTokS", "decodeTokS"]}
print("noise band:", {k: f"{v:.1%}" for k, v in noise.items()})
print("| run | batt C | TTFT p50 ms | total p50 ms | prefill tok/s | decode tok/s | prefill ms | retrieve ms | card TTFT ms | llm init ms | identical answers | declined | verdict |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
out = {}
for r in RUNS:
    m = M[r]
    same = sum(m["answers"][q] == b["answers"][q] for q in b["answers"])
    newdec = sorted(set(m["declined"]) - set(b["declined"]))
    d = {k: rel(m, k) for k in noise}
    qual = not newdec and m["outcomes"] == ["success"]
    if r in ("litelat-00-base", "litelat-07-base-repeat"):
        v = "baseline" if r.endswith("base") else "noise"
    elif (d["ttft"] > noise["ttft"]) or (d["total"] > noise["total"]):
        v = "LOSS"
    elif d["ttft"] <= -0.20 and d["ttft"] < -noise["ttft"] and d["total"] <= noise["total"] and qual:
        v = "ADOPT"
    elif ((d["prefillTokS"] >= 0.15 and d["prefillTokS"] > noise["prefillTokS"]) or (d["decodeTokS"] >= 0.10 and d["decodeTokS"] > noise["decodeTokS"])) and d["total"] <= noise["total"] and qual:
        v = "LEAD"
    else:
        v = "NO"
    f = lambda k, fmt="{:.0f}": fmt.format(m[k]) + ("" if r.endswith("base") else f" ({rel(m, k):+.1%})")
    print(f"| {r.replace('litelat-', '')} | {m['batteryC']:.1f} | {f('ttft')} | {f('total')} | {f('prefillTokS', '{:.1f}')} | {f('decodeTokS', '{:.1f}')} | {m['prefillMs']:.0f} | {m['retrieve']:.0f} | {f('cardTtft')} | {m['llmInit']} | {same}/9 | {','.join(m['declined']) or '-'}{' NEW ' + ','.join(newdec) if newdec else ''} | {v} |")
    out[r] = {k: v2 for k, v2 in m.items() if k != "answers"} | {"verdict": v, "identical": same, "newDeclined": newdec}
if "--json" in sys.argv:
    Path(sys.argv[sys.argv.index("--json") + 1]).write_text(json.dumps({"noise": noise, "runs": out}, indent=1))
