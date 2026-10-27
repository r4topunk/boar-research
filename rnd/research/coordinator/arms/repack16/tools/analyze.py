#!/usr/bin/env python3
"""REPACK16 analysis (0 LLM). usage: analyze.py <replay out dir> <arm dir>
Reads <kit>-<order>-<kb>-<cache>.{blocklog,replay}.jsonl from tools/run_replay.sh; writes aggregates/repack16-summary.json."""
import json, os, sys, glob
OUT, ARM = sys.argv[1], sys.argv[2]
def load(n):
    L = [json.loads(l) for l in open(f"{OUT}/{n}.blocklog.jsonl")]; R = [json.loads(l) for l in open(f"{OUT}/{n}.replay.jsonl")]
    miss = [x for x in L if x["e"] == "miss"]; srch = sum(1 for x in L if x["e"] == "search")
    bp = {}
    for x in miss:
        p = (x["pack"] or "?").replace("local-", ""); d = bp.setdefault(p, [0, 0]); d[0] += 1; d[1] += x["bytes"]
    raw = {r["id"]: [(h["title"], h.get("section"), h.get("source")) for h in (r.get("raw") or [])] for r in R}
    src = {r["id"]: r.get("sources") for r in R}
    dec = sum(x["bytes"] for x in miss)
    return {"searches": srch, "misses": len(miss), "decoded_MB": round(dec / 1e6, 2), "decoded_KB_per_search": round(dec / 1e3 / max(1, srch), 1),
            "misses_per_search": round(len(miss) / max(1, srch), 1), "peak_held_MB": round(max([x["held"] for x in miss] or [0]) / 2**20, 2),
            "by_pack": {p: {"misses": v[0], "decoded_MB": round(v[1] / 1e6, 2)} for p, v in sorted(bp.items())}, "_raw": raw, "_src": src}
runs = {n: None for n in (os.path.basename(f)[:-len(".blocklog.jsonl")] for f in glob.glob(f"{OUT}/*.blocklog.jsonl")) if len(n.split("-")) == 4 and n.split("-")[0] in ("A", "ASW", "A6") and n.split("-")[1] in ("S", "M")}
for n in runs: runs[n] = load(n)
out = {"runs": {}, "parity": {}, "vs64": {}}
for n, r in sorted(runs.items()):
    kit, o, kb, c = n.split("-")
    out["runs"][n] = {k: v for k, v in r.items() if not k.startswith("_")}
    if kb == "64": continue
    for base in [f"{kit}-{o}-64-{c}", f"{kit}-{o}-64-16" if c in ("128", "256") else None]:
        if not base or base not in runs: continue
        b = runs[base]
        rawd = sum(1 for i in b["_raw"] if r["_raw"].get(i) != b["_raw"][i]); srcd = sum(1 for i in b["_src"] if r["_src"].get(i) != b["_src"][i])
        out["parity"][f"{n} vs {base}"] = {"items": len(b["_raw"]), "raw_diffs": rawd, "sources_diffs": srcd,
                                          "sources_nonempty": sum(1 for i in b["_src"] if b["_src"][i])}
        out["vs64"][f"{n} vs {base}"] = {"decoded_bytes_ratio": round(r["decoded_KB_per_search"] / b["decoded_KB_per_search"], 4),
                                        "misses_ratio": round(r["misses"] / b["misses"], 4), "peak_held_MB": [b["peak_held_MB"], r["peak_held_MB"]]}
cl1 = {o: out["vs64"].get(f"A-{o}-16-64 vs A-{o}-64-64", {}).get("decoded_bytes_ratio") for o in ("S", "M")}
par = all(v["raw_diffs"] == 0 and v["sources_diffs"] == 0 for v in out["parity"].values())
out["clauses"] = {"c1_ratio_cache64_16KB": cl1, "c1_pass": all(v is not None and v <= 0.50 for v in cl1.values()), "c2_parity_pass": par,
                  "c2_runs_compared": len(out["parity"])}
os.makedirs(f"{ARM}/aggregates", exist_ok=True)
json.dump(out, open(f"{ARM}/aggregates/repack16-summary.json", "w"), indent=1)
for n, r in sorted(out["runs"].items()): print(n, r["searches"], r["misses"], r["decoded_MB"], r["decoded_KB_per_search"], r["peak_held_MB"])
print(json.dumps({"vs64": out["vs64"], "clauses": out["clauses"]}, indent=1))
print("parity:", {k: (v["raw_diffs"], v["sources_diffs"]) for k, v in out["parity"].items()})
