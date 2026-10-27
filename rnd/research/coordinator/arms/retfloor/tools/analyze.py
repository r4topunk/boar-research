#!/usr/bin/env python3
"""RETFLOOR analysis (0 LLM). Usage: python3 -I analyze.py <out dir> [variants...] -> prints tables, writes <out dir>/../aggregates/retfloor.json
Per trace: retfloor:cand:<x1|dense>:<chunkId>:<cos|na>:<onSubject 0/1> (pending appends, before the variant gate),
retfloor:kept:<grounded count>:<final chunk ids> (sources the answer step receives), headpass:add / headpass:dense:add (appended).
off-topic append = onSubject 0 AND cosine < 0.70 (both checks fail). Coverage = >= 1 final kept source (RULER-SPEC-v1 §3.3)."""
import json, sys, os, collections
OUT = sys.argv[1]; VARS = sys.argv[2:] or ["base", "V1", "V2", "V2b", "V3", "V4", "V1orC", "V1V4"]
A = "<workspace>/rnd/research/coordinator/arms"
MAIN97 = [l.strip() for l in open(f"{A}/lp-screens/main-97.ids") if l.strip()]
FACTS = json.load(open(f"{A}/oracle-st/tools/oracle-facts.json"))
PM = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se", "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
norm = lambda x: x.replace("pack:local-", "pack:")
def load(v, s):
    f = f"{OUT}/{v}-{s}.traces.jsonl"
    return {r["itemId"]: r for r in map(json.loads, open(f))} if os.path.exists(f) else None
def parse(r):
    rc = r["route"]["reasonCodes"]; cands = {}; kept = []; pre = 0; app = []
    for c in rc:
        if c.startswith("retfloor:cand:"):
            _, _, kind, rest = c.split(":", 3); cid, cos, sj = rest.rsplit(":", 2)
            cands[norm(cid)] = (kind, None if cos == "na" else float(cos), sj == "1")
        elif c.startswith("retfloor:kept:"):
            _, _, n, ids = c.split(":", 3); pre = int(n); kept = [norm(x) for x in ids.split(",") if x]
        elif c.startswith("headpass:add:") or c.startswith("headpass:dense:add:"):
            app.append(norm(c.split(":add:", 1)[1]))
    return dict(cands=cands, kept=kept, pre=pre, app=app, task=next((c for c in rc if c.startswith("task:")), ""))
off = lambda t: (not t[2]) and (t[1] is None or t[1] < 0.70)
def stats(v, ids, setnames, base=None):
    rows = {}
    for s in setnames:
        d = load(v, s)
        if d is None: return None
        rows.update({i: parse(r) for i, r in d.items()})
    rows = {i: rows[i] for i in ids}
    n = len(ids); S = collections.Counter()
    for i, p in rows.items():
        S["kept_chunks"] += len(p["kept"]); S["appended"] += len(p["app"]); S["covered"] += bool(p["kept"]); S["grounded"] += p["pre"] > 0
        S["app_x1"] += sum(p["cands"].get(c, ("?",))[0] == "x1" for c in p["app"]); S["app_dense"] += sum(p["cands"].get(c, ("?",))[0] == "dense" for c in p["app"])
        offs = [c for c in p["app"] if c in p["cands"] and off(p["cands"][c])]
        S["app_offtopic"] += len(offs); S["app_ontopic"] += len(p["app"]) - len(offs)
        S["app_cos_ge70"] += sum((p["cands"][c][1] or 0) >= 0.70 for c in p["app"] if c in p["cands"])
        if p["pre"] == 0 and p["app"]:
            S["cov_by_append_only"] += 1
            S["cov_by_offtopic_only"] += len(offs) == len(p["app"])
        if i in FACTS:
            fc = {norm(x) for x in FACTS[i]["fact_chunks"]}
            S["fact_reach"] += bool(fc & set(p["kept"])); S["fact_in_cands"] += bool(fc & (set(p["cands"]) | set(p["kept"])))
        if base is not None:
            b = base[i]
            S["emptied_vs_base"] += bool(b["kept"]) and not p["kept"]
            S["app_removed_vs_base"] += len(set(b["app"]) - set(p["app"])); S["app_added_vs_base"] += len(set(p["app"]) - set(b["app"]))
            S["offtopic_removed_vs_base"] += sum(1 for c in set(b["app"]) - set(p["app"]) if c in b["cands"] and off(b["cands"][c]))
            S["ontopic_removed_vs_base"] += sum(1 for c in set(b["app"]) - set(p["app"]) if c in b["cands"] and not off(b["cands"][c]))
            if i in FACTS:
                fc = {norm(x) for x in FACTS[i]["fact_chunks"]}; fb, fv = bool(fc & set(b["kept"])), bool(fc & set(p["kept"]))
                S["fact_lost_vs_base"] += fb and not fv; S["fact_gained_vs_base"] += fv and not fb
    S["n"] = n; S["covered_wo_offtopic_padding"] = S["covered"] - S["cov_by_offtopic_only"]
    return dict(S), rows
res = {}
for setname, ids, sets in (("MAIN97", MAIN97, ["MAIN"]), ("PM180", [i for i in FACTS], [f"PM-{p}" for p in PM])):
    base = stats("base", ids, sets)
    if base is None: print("missing base", setname); continue
    res[setname] = {"base": base[0]}
    for v in VARS[1:] if VARS[0] == "base" else VARS:
        st = stats(v, ids, sets, base[1])
        if st: res[setname][v] = st[0]
os.makedirs(f"{OUT}/../aggregates", exist_ok=True)
json.dump(res, open(f"{OUT}/../aggregates/retfloor.json", "w"), indent=1)
cols = ["n", "kept_chunks", "appended", "app_x1", "app_dense", "app_offtopic", "app_ontopic", "app_removed_vs_base", "offtopic_removed_vs_base", "ontopic_removed_vs_base",
        "covered", "grounded", "cov_by_append_only", "cov_by_offtopic_only", "covered_wo_offtopic_padding", "emptied_vs_base", "fact_reach", "fact_lost_vs_base", "fact_gained_vs_base", "fact_in_cands"]
for s, d in res.items():
    print(f"\n## {s}\n| variant | " + " | ".join(cols) + " |\n|" + "---|" * (len(cols) + 1))
    for v, st in d.items(): print(f"| {v} | " + " | ".join(str(st.get(c, "")) for c in cols) + " |")
