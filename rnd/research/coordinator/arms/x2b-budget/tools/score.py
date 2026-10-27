#!/usr/bin/env python3
"""X2B-BUDGET scorer (0 LLM). Reuses retbench/tools/score.py (score, compare) with replays read from x2b-budget/replays; adds context max,
the 40 firstaid+medlineplus self-tests, the class-E items, probe kept-set changes and the gate. python3 -I score.py -> x2b-budget.json + table."""
import json, os, math, re
A = "<workspace>/rnd/research/coordinator/arms"; X = A + "/x2b-budget"; RBS = A + "/retbench/tools/score.py"
G = {"__name__": "rb"}; src = open(RBS).read(); src = src[:src.index('if __name__ == "__main__":')]
exec(compile(src, "retbench_score.py", "exec"), G); G["RB"] = X   # rows()/bytes_q() read RB/replays/<name>/
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
tok = G["tok"]; ST = G["ST"]
H40 = sorted(i for i, x in ST.items() if x["pack"] in ("boar-firstaid-en", "boar-medlineplus-en"))
E5 = ["st-boar-firstaid-en-015", "st-boar-medlineplus-en-003", "st-boar-medlineplus-en-007", "st-boar-medlineplus-en-009", "st-boar-medlineplus-en-014"]
F3 = A + "/coverage-map/sefix/f3-safety"
def plist(r): return [(c.get("title"), c.get("source")) for c in (r.get("keptFull") or [])]
def probes(name):
    f = f"{X}/replays/{name}/probes.jsonl"
    return {r["id"]: r for r in rd(f)} if os.path.exists(f) else None
def kmax(name, L):
    out = []
    for l in (["main"] if L == "main" else ["st.on-k13", "st.on-k13+qa-bitcoin-se", "st.on-k13+qa-ethereum-se"]):
        out += [tok(r.get("keptFull") or []) for r in rd(f"{X}/replays/{name}/{l}.jsonl")]
    return max(out)
ARMS = ["B600", "B900", "B1200", "BINF"]
S = {a: G["score"](a) for a in ARMS if os.path.exists(f"{X}/replays/{a}/probes.jsonl")}
base = S["B600"]; P0 = probes("B600")
# identity vs retbench base
rbb = json.load(open(A + "/retbench/aggregates/base.json"))
ident = dict(main=sum(base["main"]["kept_ids"][i] == rbb["main"]["kept_ids"][i] for i in rbb["main"]["kept_ids"]),
             st=sum(base["st"]["kept_ids"][i] == rbb["st"]["kept_ids"][i] for i in rbb["st"]["kept_ids"]),
             main_facts=base["main"]["facts"], st_fact=base["st"]["fact"], topics=base["topics"]["expected_in_kept"])
off = {t["itemId"]: [(k.get("title"), k.get("source")) for k in t["retrieval"]["kept"]] for t in rd(F3 + "/runs/f3safety-off-s42.traces.jsonl")}
ident["probes_vs_off_traces_title_source"] = sum(plist(P0[i]) == off.get(i) for i in P0); ident["probes_n"] = len(P0)
ident["probes_vs_off_traces_title"] = sum([t for t, _ in plist(P0[i])] == [t for t, _ in off.get(i, [])] for i in P0)
RES = {"criterion_sha": open(X + "/X2B-BUDGET-criterion.sha256").read().split()[0], "identity": ident, "arms": {}}
for a, o in S.items():
    d = G["compare"](o, base) if a != "B600" else {}
    P = probes(a); ch = sorted(i for i in P0 if plist(P[i]) != plist(P0[i])); dn = [i for i in ch if re.match(r"^(h|n)\d", i)]
    stf = set(o["st"]["fact_ids"])
    e = dict(main_facts=o["main"]["facts"], main_cm=o["main"]["cm"], main_v01=o["main"]["v01"], main_ctx_p50=o["main"]["ctx"]["p50"], main_ctx_max=kmax(a, "main"),
             main_mean_kept=o["main"]["mean_kept"], st_fact=o["st"]["fact"], st_own_kept=o["st"]["own_kept"], st_ctx_p50=o["st"]["ctx"]["p50"], st_ctx_max=kmax(a, "st"),
             st_crowd_all=o["st"]["crowd_all"], st_mean_kept=o["st"]["mean_kept"], h40_fact=sum(i in stf for i in H40), e5_fact=[i for i in E5 if i in stf],
             topics=o["topics"]["expected_in_kept"], probes_changed=ch, probes_changed_dosenum=dn, vs_base=d)
    if a != "B600":
        g1 = e["main_facts"] >= base["main"]["facts"] + 3 or e["st_fact"] >= base["st"]["fact"] + 8
        g2 = d["health_losses"] == 0
        g3 = e["main_ctx_p50"] <= 1.15 * base["main"]["ctx"]["p50"] and max(e["main_ctx_max"], e["st_ctx_max"]) + 1024 <= 4096
        g4 = len(ch) <= 5 and not dn
        e["gate"] = dict(g1_gain=g1, g2_health=g2, g3_context=g3, g4_probes=g4, PASS=(g1 and g2 and g3 and g4) and a != "BINF")
    RES["arms"][a] = e
json.dump(RES, open(X + "/x2b-budget.json", "w"), indent=1)
print("identity", ident)
for a, e in RES["arms"].items():
    v = e["vs_base"]
    print(a, "MAIN", e["main_facts"], f"(cm {e['main_cm']} v01 {e['main_v01']})", "ctx p50/max", e["main_ctx_p50"], e["main_ctx_max"], "| ST fact", e["st_fact"], "own", e["st_own_kept"], "H40", e["h40_fact"], "E5", len(e["e5_fact"]),
          "ctx", e["st_ctx_p50"], e["st_ctx_max"], "| TOP", e["topics"], "| probes chg", len(e["probes_changed"]), "dn", len(e["probes_changed_dosenum"]),
          "|", {k: (vv if not isinstance(vv, dict) else {kk: (len(x) if isinstance(x, list) else x) for kk, x in vv.items()}) for k, vv in v.items()}, e.get("gate"))
