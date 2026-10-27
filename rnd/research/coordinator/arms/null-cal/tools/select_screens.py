#!/usr/bin/env python3
"""NULLCAL / GATE v2 screen selection (0 LLM; uses only the MINI control). Usage: python3 -I select_screens.py <K0|K1> <pool-K.json> <out dir>
Pool = MAIN 97 (v01 57 + qa-cooking-se 20 + qa-money-se 20) + the 180 pack self-tests (dev only), generated once on the mini for pack set K.
Corrected labels from labels.py. Rule (frozen in NULLCAL2-criterion.md before any null/arm generation on the new screens):
  PROBLEMS  = every LIVE item (control trace generated tokens > 0) that is CE-unwarned in the control (CE and not warned, not a decline), ids ascending.
  SENTINELS = 20 LIVE items that the default product SHOWS (not warned, not a decline), not CE, ranked by (-corr, sha256(id)), at most 3 per unit
              (unit = v01, or the self-test pack / SE community), so no source dominates.
Writes <out>/screen2-<K>.ids (problems then sentinels), screen2-<K>.json, screen2-<K>.ids.sha256."""
import json, sys, os, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from labels import label
K, pj, od = sys.argv[1:4]; os.makedirs(od, exist_ok=True)
items = json.load(open(pj))["items"]; L = {i: label(x) for i, x in items.items()}
unit = lambda i: "v01" if not i.startswith("st-") else i.rsplit("-", 1)[0]
sha = lambda i: hashlib.sha256(i.encode()).hexdigest()
P = sorted(i for i in items if items[i]["live"] and L[i]["CEu"])
cand = sorted((i for i in items if items[i]["live"] and L[i]["shown"] and not L[i]["CE"]), key=lambda i: (-L[i]["corr"], sha(i)))
S, cnt = [], {}
for i in cand:
    if len(S) == 20: break
    if cnt.get(unit(i), 0) >= 3: continue
    S.append(i); cnt[unit(i)] = cnt.get(unit(i), 0) + 1
ids = P + S; f = f"{od}/screen2-{K}.ids"; open(f, "w").write("\n".join(ids) + "\n"); h = hashlib.sha256(open(f, "rb").read()).hexdigest()
open(f + ".sha256", "w").write(f"{h}  screen2-{K}.ids\n")
pool = dict(n=len(items), live=sum(x["live"] for x in items.values()), CE=sum(L[i]["CE"] for i in items), CEu=sum(L[i]["CEu"] for i in items),
            CEu_live=len(P), CEw=sum(L[i]["CE"] and L[i]["warned"] for i in items), decline=sum(L[i]["decline"] for i in items), warned=sum(L[i]["warned"] for i in items))
by = {}
for i in P: by[unit(i)] = by.get(unit(i), 0) + 1
json.dump(dict(pack_set=K, rule="see select_screens.py docstring", pool=pool, problems=P, sentinels=S, sentinel_corr={i: L[i]["corr"] for i in S},
               problems_by_unit=by, ids_sha256=h), open(f"{od}/screen2-{K}.json", "w"), indent=1)
print(K, pool, "| problems", len(P), by, "| sentinels", len(S), "| ids sha256", h)
