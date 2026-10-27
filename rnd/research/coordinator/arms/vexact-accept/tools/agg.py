#!/usr/bin/env python3
"""VEXACT-ACCEPT aggregate + verdict. Usage: agg.py --label L --seeds "42 43" [--prompt D4] [--baseline B] [--own-gate PASS|FAIL|NA]
Judged ratio = sum of the judge's three scores for BOAR / the same sum for the web+frontier reference, over both orders (judge.v1 rows, mapped),
pooled over the 5 judged items and the seeds (= claim_report.py's raw ratio; reproduces cut 2's 0.510 on its Opus judgments).
Venues = rnd/kiln/l1/vexact-venues.mjs output (scoreFoodAnswer pass = >= 3 real OSM vegan venues). Verdict rules: VEXACT-ACCEPT-criterion.md."""
import argparse, json, os, random, re
A = "<workspace>/rnd/research/coordinator/arms/vexact-accept"
ap = argparse.ArgumentParser(); ap.add_argument("--label", required=True); ap.add_argument("--seeds", default="42 43")
ap.add_argument("--prompt", default="D4"); ap.add_argument("--baseline"); ap.add_argument("--own-gate", default="NA")
a = ap.parse_args(); seeds = a.seeds.split()

def load(label, seed):
    base = f"{A}/runs/{label}/vxa-{label}-s{seed}"
    T = {json.loads(l)["itemId"]: json.loads(l) for l in open(base + ".traces.jsonl") if l.strip()}
    J = [json.loads(l) for l in open(base + ".judgments.jsonl") if l.strip()] if os.path.exists(base + ".judgments.jsonl") else []
    return base, T, J

def sums(J):
    b, r = {}, {}
    for x in J:
        if not x.get("ok"): continue
        q = x["queryId"]; b[q] = b.get(q, 0) + sum(x["mapped"]["boar"].values()); r[q] = r.get(q, 0) + sum(x["mapped"]["ref"].values())
    return b, r

def runset(label):
    out = {"seeds": {}, "items": {}}
    B, R = {}, {}
    ids = [x for x in open(f"{A}/runs/{label}/judged.ids").read().split() if x]
    V = json.load(open(f"{A}/runs/{label}/venues.json"))
    for s in seeds:
        base, T, J = load(label, s); b, r = sums(J)
        for q in ids: B.setdefault(q, []).append(b.get(q, 0)); R.setdefault(q, []).append(r.get(q, 0))
        rw = [json.loads(l) for l in open(base + ".traces.rewrites.jsonl")] if os.path.exists(base + ".traces.rewrites.jsonl") else []
        gen = [i for i, t in T.items() if any(c.startswith("generate:") for c in (t.get("route") or {}).get("reasonCodes", []))]
        v = V[os.path.basename(base)]
        out["seeds"][s] = {
            "ratio": round(sum(b.get(q, 0) for q in ids) / sum(r.get(q, 0) for q in ids), 4) if J else None,
            "per_item": {q: round(b[q] / r[q], 3) for q in ids if q in b and r[q]},
            "reused": sorted({x["queryId"] for x in J if x.get("reusedFrom")}),
            "traces": len(T), "errored": sum(bool(t.get("error")) for t in T.values()),
            "model_answered": gen, "rewritten": sum(1 for x in rw if x.get("rewritten")), "facts_override_hits": sum(1 for x in rw if x.get("factsOverride")),
            "tiers": {i: (t.get("route") or {}).get("tier") for i, t in T.items()},
            "venues_pass": v["pass"], "venues_n": v["n"], "gps_names_city": f'{v["gpsCity"]}/{v["gpsN"]}',
            "venue_rows": {x["id"]: x["verifiedDietVenues"] for x in v["rows"]},
        }
    out["ids"] = ids
    out["items"] = {q: round(sum(B[q]) / sum(R[q]), 3) for q in ids}
    out["ratio"] = round(sum(map(sum, B.values())) / sum(map(sum, R.values())), 4)
    out["_B"], out["_R"] = B, R
    return out

def boot_delta(c, b, n=2000, seed=11):
    ids = c["ids"]; rng = random.Random(seed); ds = []
    for _ in range(n):
        s = [rng.choice(ids) for _ in ids]
        rc = sum(sum(c["_B"][q]) for q in s) / sum(sum(c["_R"][q]) for q in s)
        rb = sum(sum(b["_B"][q]) for q in s) / sum(sum(b["_R"][q]) for q in s)
        ds.append(rc - rb)
    ds.sort(); return round(ds[int(0.025 * n)], 4), round(ds[int(0.975 * n) - 1], 4)

def boot_ratio(c, n=2000, seed=11):
    ids = c["ids"]; rng = random.Random(seed); xs = []
    for _ in range(n):
        s = [rng.choice(ids) for _ in ids]; xs.append(sum(sum(c["_B"][q]) for q in s) / sum(sum(c["_R"][q]) for q in s))
    xs.sort(); return round(xs[int(0.025 * n)], 4), round(xs[int(0.975 * n) - 1], 4)

C = runset(a.label); C["ratio_ci"] = boot_ratio(C)
res = {"label": a.label, "prompt": a.prompt, "seeds": seeds, "ratio": C["ratio"], "ratio_ci_items": C["ratio_ci"], "per_item": C["items"], "per_seed": C["seeds"]}
valid = all(x["errored"] == 0 and x["traces"] == 11 for x in C["seeds"].values())
if a.prompt == "D4": valid = valid and all(x["rewritten"] == len(x["model_answered"]) for x in C["seeds"].values())
res["valid"] = valid
venues_ok = all(x["venues_pass"] == 6 and x["venues_n"] == 6 for x in C["seeds"].values())
res["venues_6of6_every_seed"] = venues_ok
if a.baseline:
    Bs = runset(a.baseline); d = round(C["ratio"] - Bs["ratio"], 4); ci = boot_delta(C, Bs)
    a1 = d >= -0.03; own = a.own_gate.upper()
    res["baseline"] = {"label": a.baseline, "ratio": Bs["ratio"], "delta": d, "delta_ci_items": ci,
                       "per_item_delta": {q: round(C["items"][q] - Bs["items"][q], 3) for q in C["ids"]}}
    res["verdict"] = {"A1_ratio_not_below_baseline_minus_0.03": a1, "A2_venues_6of6": venues_ok, "A3_own_gate": own, "valid_run": valid,
                      "ACCEPT": bool(valid and a1 and venues_ok and own == "PASS"),
                      "note": "ACCEPT needs A1 and A2 and A3 = PASS on a valid run; A3 NA -> not accepted (the asset's own gate must be run and frozen separately)."}
json.dump(res, open(f"{A}/runs/{a.label}/result.json", "w"), indent=1)
L = [f"# V-exact acceptance run: {a.label}", "", f"prompt {a.prompt}, seeds {', '.join(seeds)}, judge Haiku 5.5-low (judge.v1, N = 4, both orders) on the 5 judged items; venues by OSM gold on the 6 venue items.", "",
     f"**Judged ratio (pooled, {len(seeds)} seeds): {C['ratio']:.3f}** (item-bootstrap 95% CI {C['ratio_ci'][0]:.3f}-{C['ratio_ci'][1]:.3f}, n = 5 items: wide)", "",
     "| item | " + " | ".join(f"s{s}" for s in seeds) + " | pooled |", "|---|" + "---|" * (len(seeds) + 1)]
for q in C["ids"]: L.append(f"| {q} | " + " | ".join(f"{C['seeds'][s]['per_item'].get(q, float('nan')):.3f}" for s in seeds) + f" | {C['items'][q]:.3f} |")
L += ["", "| seed | ratio | venues pass | GPS answers name the city | model-answered (D4-rewritten) | errored | judged rows reused |", "|---|---|---|---|---|---|---|"]
for s in seeds:
    x = C["seeds"][s]; L.append(f"| {s} | {x['ratio']:.3f} | {x['venues_pass']}/{x['venues_n']} | {x['gps_names_city']} | {len(x['model_answered'])} ({x['rewritten']}) | {x['errored']} | {len(x['reused'])} |")
if a.baseline:
    b = res["baseline"]; v = res["verdict"]
    L += ["", f"Baseline `{a.baseline}` {b['ratio']:.3f}; delta **{b['delta']:+.3f}** (paired item-bootstrap {b['delta_ci_items'][0]:+.3f}..{b['delta_ci_items'][1]:+.3f}).",
          f"A1 (delta >= -0.03): {'PASS' if v['A1_ratio_not_below_baseline_minus_0.03'] else 'FAIL'}; A2 (venues 6/6 each seed): {'PASS' if v['A2_venues_6of6'] else 'FAIL'}; A3 own gate: {v['A3_own_gate']}; valid run: {v['valid_run']}.",
          f"**{'ACCEPT' if v['ACCEPT'] else 'NOT ACCEPTED'}**"]
open(f"{A}/runs/{a.label}/RESULT.md", "w").write("\n".join(L) + "\n")
print("\n".join(L))
