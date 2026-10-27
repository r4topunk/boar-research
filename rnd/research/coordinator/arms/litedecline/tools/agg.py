#!/usr/bin/env python3
"""LITEDECLINE aggregation (0 LLM). Usage: python3 -I agg.py   -> aggregates/litedecline.json + stdout tables.
Per item s = mean of the 3 judge dims averaged over both orders (PACKREAD agg); s_ref likewise for the reference.
Q = sum s / sum s_ref. U0 = Q with s := 0 for every declined answer (trace answer.declined == true). decline rate = share declined.
confident-error rate (CE) = share of non-declined answers with judge correctness (mean over the two orders) <= 1.5.
Paired deltas OFF - ON: item bootstrap B 2000 seed 11, 2.5/97.5 percentiles. Sets: v01 (57 judged public v0.1 ids), st (180 self-tests), pooled (237).
Judgments: ON judged in full; OFF/OFF5 judged on the items whose answer text differs from ON; identical answers reuse ON's rows (Deviations)."""
import json, random, glob, os
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES = ["grounding:declined-compact", "grounding:false-claim-declined-compact", "grounding:all-citations-removed-declined-compact"]
OTHER = ["grounding:uncited-with-sources-declined-compact", "grounding:uncited-declined-compact"]
def traces(arm):
    out = {}
    for f in sorted(glob.glob(f"{H}/traces/ld-{arm}-*-s42.traces.jsonl")):
        if "smoke" in f: continue
        for l in open(f):
            t = json.loads(l); out[t["itemId"]] = t
    return out
def judg(arm):
    by = {}
    for f in sorted(glob.glob(f"{H}/judgments/ld-{arm}-*.judgments.jsonl")):
        for l in open(f):
            r = json.loads(l)
            if r.get("ok") is not True: continue
            m = r["mapped"]; by.setdefault(r["queryId"], {})[r["order"]] = m
    out = {}
    for q, v in by.items():
        if len(v) != 2: continue
        ms = list(v.values()); mean = lambda d: sum(d.values()) / 3
        out[q] = dict(s=sum(mean(m["boar"]) for m in ms) / 2, sref=sum(mean(m["ref"]) for m in ms) / 2,
                      corr=sum(m["boar"]["correctness"] for m in ms) / 2)
    return out
TR = {a: traces(a) for a in ("on", "off", "off5")}
J0 = {a: judg(a) for a in ("on", "off", "off5")}
V01 = [l.strip() for l in open(f"{H}/data/v01-57.ids") if l.strip()]
ST = sorted(i for i in TR["on"] if i.startswith("st-"))
SETS = {"v01": V01, "st": ST, "pooled": V01 + ST}
ans = lambda a, i: TR[a][i]["answer"]["text"]
dec = lambda a, i: bool(TR[a][i]["answer"].get("declined"))
codes = lambda a, i: TR[a][i]["route"]["reasonCodes"]
J = {"on": J0["on"]}
for a in ("off", "off5"):
    J[a] = {}
    for i in SETS["pooled"]:
        if a in TR and i in TR[a] and ans(a, i) == ans("on", i): J[a][i] = J0["on"].get(i)
        else: J[a][i] = J0[a].get(i)
def item(a, i):
    j = J[a][i]; d = dec(a, i)
    return dict(s=j["s"], s0=0.0 if d else j["s"], sref=j["sref"], dec=d, corr=j["corr"])
def metrics(a, ids):
    it = [item(a, i) for i in ids]; sr = sum(x["sref"] for x in it); nd = [x for x in it if not x["dec"]]
    return dict(Q=sum(x["s"] for x in it) / sr, U0=sum(x["s0"] for x in it) / sr, decline=sum(x["dec"] for x in it) / len(it),
                CE=(sum(x["corr"] <= 1.5 for x in nd) / len(nd)) if nd else 0.0, n=len(it), n_nondeclined=len(nd), ce_count=sum(x["corr"] <= 1.5 for x in nd),
                corr_mean_all=sum(x["corr"] for x in it) / len(it))
def boot(a, b, ids, key, B=2000, seed=11):
    rnd = random.Random(seed); xs = []
    for _ in range(B):
        s = [rnd.choice(ids) for _ in ids]; xs.append(metrics(a, s)[key] - metrics(b, s)[key])
    xs.sort(); return [round(xs[int(0.025 * B)], 4), round(xs[int(0.975 * B) - 1], 4)]
def complete(a): return all(J[a].get(i) for i in SETS["pooled"]) and all(i in TR[a] for i in SETS["pooled"])
res = {"criterion_sha256": open(f"{H}/LITEDECLINE-criterion.sha256").read().split()[0], "sets": {k: len(v) for k, v in SETS.items()}, "arms": {}, "deltas": {}}
for a in ("on", "off", "off5"):
    if not complete(a): print("incomplete", a); continue
    res["arms"][a] = {k: {m: round(v, 4) if isinstance(v, float) else v for m, v in metrics(a, ids).items()} for k, ids in SETS.items()}
    if a != "on":
        res["deltas"][f"{a}-on"] = {}
        for k, ids in SETS.items():
            mo, mn = metrics(a, ids), metrics("on", ids)
            res["deltas"][f"{a}-on"][k] = {m: dict(d=round(mo[m] - mn[m], 4), ci=boot(a, "on", ids, m)) for m in ("Q", "U0", "decline", "CE")}
            res["deltas"][f"{a}-on"][k]["changed_answers"] = sum(ans(a, i) != ans("on", i) for i in ids)
# per-rule fire counts (ON) and what OFF / OFF5 did there
pr = {}
for r in RULES + OTHER:
    ids = [i for i in SETS["pooled"] if r in codes("on", i)]
    row = {"fires_on": len(ids), "by_set": {"v01": sum(i in V01 for i in ids), "st": sum(i.startswith("st-") for i in ids)}, "ids": ids}
    for a in ("off", "off5"):
        if a not in res["arms"]: continue
        ch = [i for i in ids if ans(a, i) != ans("on", i)]
        row[a] = {"changed": len(ch), "still_declined": sum(dec(a, i) for i in ids),
                  "codes_after": sorted({c for i in ids for c in codes(a, i) if c.startswith("grounding:") and ("declin" in c or "uncited" in c or "memory" in c or "false-claim" in c)}),
                  "corr_mean_nondeclined": round(sum(J[a][i]["corr"] for i in ids if not dec(a, i)) / max(1, sum(not dec(a, i) for i in ids)), 3),
                  "ce_nondeclined": sum(J[a][i]["corr"] <= 1.5 for i in ids if not dec(a, i)),
                  "s_on": round(sum(J["on"][i]["s"] for i in ids) / max(1, len(ids)), 3), "s_arm": round(sum(J[a][i]["s"] for i in ids) / max(1, len(ids)), 3),
                  "corr_hist": {str(k): sum(1 for i in ids if not dec(a, i) and round(J[a][i]["corr"]) == k) for k in range(1, 6)}}
    pr[r] = row
res["per_rule"] = pr
# identity: items with none of the five compact codes in ON must be byte-identical in OFF (answer + reason codes)
idn = {}
for a in ("off", "off5"):
    if a not in TR or not TR[a]: continue
    base = [i for i in SETS["pooled"] if i in TR[a] and not any(r in codes("on", i) for r in (RULES if a == "off" else RULES + OTHER))]
    same = [i for i in base if ans(a, i) == ans("on", i) and codes(a, i) == codes("on", i)]
    idn[a] = {"items_rule_not_fired": len(base), "byte_identical_answer_and_codes": len(same), "diff_ids": [i for i in base if i not in same]}
res["identity"] = idn
# verdict (frozen rule) on OFF pooled
def rule(p):
    du, lo, dce = p["U0"]["d"], p["U0"]["ci"][0], p["CE"]["d"]
    if du >= 0.03 and lo > 0 and dce <= 0.05: return "ADOPT OFF"
    if du <= 0 or dce > 0.10: return "KEEP ON"
    return "PARTIAL"
if "off-on" in res["deltas"]: res["verdict"] = rule(res["deltas"]["off-on"]["pooled"])  # the frozen rule, on the criterion's OFF arm
if "off5-on" in res["deltas"]: res["off5_same_rule_report_only"] = rule(res["deltas"]["off5-on"]["pooled"])
json.dump(res, open(f"{H}/aggregates/litedecline.json", "w"), indent=1)
for a, d in res["arms"].items():
    for k, m in d.items(): print(f"{a:5} {k:7} n={m['n']:3} Q={m['Q']:.3f} U0={m['U0']:.3f} decl={m['decline']:.3f} CE={m['CE']:.3f} (nd {m['n_nondeclined']}, ce {m['ce_count']})")
for c, d in res["deltas"].items():
    for k, m in d.items(): print(c, k, {x: m[x] for x in ("Q", "U0", "decline", "CE")}, "changed", m["changed_answers"])
for r, row in pr.items(): print(r, {k: v for k, v in row.items() if k != "ids"})
print("identity", json.dumps(idn)); print("VERDICT", res.get("verdict"), "| OFF5 (report only, same rule):", res.get("off5_same_rule_report_only"))
