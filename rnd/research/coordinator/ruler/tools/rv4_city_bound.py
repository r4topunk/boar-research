#!/usr/bin/env python3
"""RV4-CITY-BOUND (criterion ruler/RV24-criterion.md). 0 LLM. Usage: python3 -I rv4_city_bound.py <out.json>
Reads only INPACK-STRATUM-2026-10-21.json tags (ids, health_safety, has_location, anchor_vexact) and dev v0.1 judge.v1 rows."""
import json, sys, collections, numpy as np
C = "<workspace>/rnd/research/coordinator/"; A = C + "arms/"; R = "<workspace>/boar-eval/runs/"
it = json.load(open(C + "ruler/INPACK-STRATUM-2026-10-21.json"))["items"]
H = [r for r in it if not r["tags"]["anchor_vexact"]]; w = {r["id"]: 0.5 if r["tags"]["health_safety"] else 1.0 for r in H}
loc = [r["id"] for r in H if r["tags"]["has_location"]]; W = sum(w.values()); Wl = sum(w[q] for q in loc); Wn = W - Wl
K = ("correctness", "completeness", "usefulness"); mr = lambda s: sum(s[k] for k in K) / 3
def load(p):
    J = collections.defaultdict(dict); cat = {}
    for l in open(p):
        r = json.loads(l); cat[r["queryId"]] = r.get("category")
        if r.get("ok") and r["order"] not in J[r["queryId"]]: J[r["queryId"]][r["order"]] = r["mapped"]
    return {q: {"s": (mr(v["boarA"]["boar"]) + mr(v["boarB"]["boar"])) / 2, "r": (mr(v["boarA"]["ref"]) + mr(v["boarB"]["ref"])) / 2, "cat": cat[q]}
            for q, v in J.items() if set(v) == {"boarA", "boarB"}}
ids57 = open(A + "gemma4-e2b/phone/judge/v01-57.ids").read().split()
P4 = load(R + "device-pixel8a/final-cut7-v01/judgments.haiku.jsonl"); L17 = load(A + "lp-screens/control/judgments/lpctl-K0-main-s42-v01.judgments.jsonl")
ids = [q for q in ids57 if q in P4 and q in L17]
trav = [q for q in ids if P4[q]["cat"] == "travel" or q.startswith(("trv-", "vit-trv-"))]
ci = lambda x: [round(float(v), 4) for v in np.percentile(x, [2.5, 97.5])]
def rho(ii_all, ii_t): return np.mean([P4[q]["r"] - 1 for q in ii_t]) / np.mean([P4[q]["r"] - 1 for q in ii_all])
def Ut(D, ii): return sum(D[q]["s"] - 1 for q in ii) / sum(D[q]["r"] - 1 for q in ii)
phi = lambda rh: Wl * rh / (Wl * rh + Wn)
rng = np.random.default_rng(11); B = []
for _ in range(2000):
    a = [ids[i] for i in rng.integers(0, len(ids), len(ids))]; t = [trav[i] for i in rng.integers(0, len(trav), len(trav))]
    rh = rho(a, t); B.append((rh, phi(rh), Ut(P4, t), Ut(L17, t)))
B = np.array(B); rh0 = rho(ids, trav); ph0 = phi(rh0); phinom = Wl / W
out = {"criterion_sha256": open(C + "ruler/RV24-criterion.sha256").read().split()[0],
       "H_n": len(H), "sum_w_H": W, "loc_ids": loc, "loc_weights": [w[q] for q in loc], "phi_nominal": round(phinom, 4),
       "max_swing_all0_vs_all1_lower_bound": round(Wl / W, 4), "note_max": "7/D with D = sum_H w s_ref <= 65.5, so >= 0.1069 whatever the reference scores; larger if the reference scores < 1",
       "proxy": {"travel_ids": trav, "rho_refmass_travel_vs_all": round(rh0, 4), "rho_ci": ci(B[:, 0]), "phi_proxy": round(ph0, 4), "phi_ci": ci(B[:, 1]),
                 "app_level_4B_phone_travel_U": round(Ut(P4, trav), 4), "app_level_4B_ci": ci(B[:, 2]), "app_level_17B_travel_U": round(Ut(L17, trav), 4), "app_level_17B_ci": ci(B[:, 3]),
                 "app_level_4B_all57_U": round(Ut(P4, ids), 4)}}
sw = {}
for nm, ph, phc in (("nominal", phinom, None), ("proxy", ph0, B[:, 1])):
    sw[nm] = {"refusal_to_tile_ceiling (app = ref)": round(ph, 4), "refusal_to_memory_4B_level": round(ph * Ut(P4, trav), 4),
              "refusal_to_memory_17B_level": round(ph * Ut(L17, trav), 4)}
    if phc is not None:
        sw[nm]["refusal_to_tile_ceiling_ci"] = ci(phc); sw[nm]["refusal_to_memory_4B_ci"] = ci(phc * B[:, 2])
out["swing"] = sw
# band windows (U_excl = U on H minus loc; U_with = U_excl (1-phi) + phi * a, a = app level on loc relative to ref)
win = {}
for nm, ph in (("nominal", phinom), ("proxy", ph0)):
    win[nm] = {"scored0_vs_excluded: band flips iff U_excl in": [0.5, round(0.5 / (1 - ph), 4)],
               "scored0_vs_tile_ceiling: band flips iff U_excl in": [round((0.5 - ph) / (1 - ph), 4), round(0.5 / (1 - ph), 4)]}
out["band_windows"] = win
hi = max(sw["proxy"]["refusal_to_tile_ceiling_ci"][1], sw["nominal"]["refusal_to_tile_ceiling (app = ref)"])
out["rule"] = {"projected swing CI high": round(hi, 4), "> 0.03": bool(hi > 0.03),
               "decision": "KILL branch: separate pre-registered stratum; U-total printed with and without; verdict on 'with' (scored as given); headline row states the APK cannot answer current-city questions" if hi > 0.03 else "headline as given + one sensitivity row"}
js = json.dumps(out, indent=1); open(sys.argv[1], "w").write(js + "\n"); print(js)
