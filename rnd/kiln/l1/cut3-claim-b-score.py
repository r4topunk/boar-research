#!/usr/bin/env python3
"""V-para scoring (aggregates only). P1/P3 floor_metrics (frozen), P2 families, P4 over-refusal, P5 venues (via venues adapter), report json."""
import json, subprocess, sys, collections
from pathlib import Path
B = Path("<workspace>"); V = B / "blind/V-para"; OUT = V / "runs-cut3"
FM = B / "boar-eval/bench/v0.2/plan/floor_metrics.py"
Q = [json.loads(l) for l in open(V / "items.jsonl") if l.strip()]
venue = [q for q in Q if q.get("grading", {}).get("type") == "venue-list"]
judged = [q for q in Q if q not in venue]
(OUT / "judged.ids").write_text("\n".join(q["id"] for q in judged) + "\n")
def fam(q):
    if q.get("origin") == "vitalik-verbatim-paraphrase": return "paraphrase"
    if q.get("category") in ("travel-local", "travel-practical", "local-food"): return "travel"
    return "same-family"
F = collections.defaultdict(list)
for q in judged: F[fam(q)].append(q["id"])
allf = collections.Counter(fam(q) for q in Q)
print("family counts over all 58 items:", dict(allf), "| judged part:", {k: len(v) for k, v in F.items()})
def floor(ids, strat):
    f = OUT / ("ids-" + str(abs(hash(tuple(ids)))) + ".txt"); f.write_text("\n".join(ids) + "\n")
    cmd = [sys.executable, str(FM), "--runs", "cut3-vpara-s42", "cut3-vpara-s43", "--dir", str(OUT), "--decline-ratio", "0.306", "--ids", str(f)]
    if strat: cmd += ["--questions", str(V / "items.jsonl")]
    r = subprocess.run(cmd, capture_output=True, text=True); f.unlink()
    return json.loads(r.stdout) if r.returncode == 0 else {"error": r.stderr[-300:]}
res = {"P1_P3_all51_stratified": floor([q["id"] for q in judged], True), "P1_plain": floor([q["id"] for q in judged], False)}
for k, ids in F.items(): res["P2_" + k] = floor(ids, False)
def short(m): return {k: (m[k]["point"], m[k]["ci95"]) for k in ("raw", "above_min", "above_decl")} | {"n": m["n_items"]} if "raw" in m else m
for k, m in res.items(): print(k, short(m))
# P4 over-refusal: declined share on items with refuse_ok == false
rf = [q["id"] for q in Q if q.get("grading", {}).get("refuse_ok") is False]
print("items with refuse_ok false:", len(rf), "(judged among them:", sum(1 for i in rf if i in {q['id'] for q in judged}), ")")
tot = dec = 0; per = {}
for s in (42, 43):
    T = {json.loads(l)["itemId"]: json.loads(l) for l in open(OUT / f"cut3-vpara-s{s}.traces.jsonl")}
    d = [i for i in rf if i in T and T[i]["answer"].get("declined")]
    per[s] = (len(d), len([i for i in rf if i in T])); tot += len([i for i in rf if i in T]); dec += len(d)
    res[f"P4_s{s}_declined_ids"] = d
print("P4 declined / total per seed", per, "pooled", f"{dec}/{tot} = {dec / tot:.3f}" if tot else "n/a")
res["P4"] = {"declined": dec, "total": tot, "share": dec / tot if tot else None, "per_seed": per}
json.dump(res, open(OUT / "vpara.aggregate.json", "w"), indent=1)
