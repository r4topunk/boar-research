"""FA-CARDS step B (0 LLM): trigger-edit replay (runs/B) vs step A (runs/A): false fires on non-health items, probe moves, epinephrine routes.
Usage: python3 -I compare.py -> aggregates/trigger-edit.json + stdout"""
import json, os, re
A = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def safety(c): return c.startswith(("grounding:health-strict", "grounding:fa-card-", "answer:first-aid", "answer:co", "answer:emergency", "grounding:health-card",
                                    "grounding:health-extractive", "grounding:health-no-source")) or "card" in c  # = routing-r1/tools/compare.py
a = {(r["set"], r["id"]): r for r in json.load(open(f"{A}/aggregates/kept-A.json"))["rows"]}
b = {(r["set"], r["id"]): r for r in json.load(open(f"{A}/aggregates/kept-B.json"))["rows"]}
ROUT6 = {"st-qa-cooking-se-005", "st-qa-cooking-se-013", "st-qa-cooking-se-015", "st-qa-cooking-se-017", "st-qa-cooking-se-018", "st-qa-money-se-004"}
nonhealth = lambda s, i: s == "cm" or (s == "v01" and not re.search(r"hlt|dng|health", i))
ch, ff, pm = [], [], []
for k, x in a.items():
    y = b[k]; d = dict(set=k[0], id=k[1], layer=[x["layer"], y["layer"]], fa=[x["fa_codes"], y["fa_codes"]],
                       safe_lost=sorted({c for c in x["codes"] if safety(c)} - {c for c in y["codes"] if safety(c)}),
                       safe_new=sorted({c for c in y["codes"] if safety(c)} - {c for c in x["codes"] if safety(c)}))
    if x["layer"] != y["layer"] or x["fa_codes"] != y["fa_codes"] or d["safe_lost"] or d["safe_new"]:
        ch.append(d)
        if nonhealth(*k): ff.append(k[1])
        if k[0] == "probes65" and k[1] != "epi-1021": pm.append(k[1])
res = dict(changed=ch, false_fires_nonhealth=ff, false_fires_routing6=sorted(set(ff) & ROUT6), probe_moves_64=pm,
           epi={i: dict(A=a[k]["layer"], B=b[k]["layer"], faB=b[k]["fa_codes"]) for k in a for i in [k[1]] if i in ("epi-1021", "ls03-t4")},
           gate_pass=len(ff) <= 1 and not (set(ff) & ROUT6) and not pm)
json.dump(res, open(f"{A}/aggregates/trigger-edit.json", "w"), indent=1); print(json.dumps(res, indent=1))
