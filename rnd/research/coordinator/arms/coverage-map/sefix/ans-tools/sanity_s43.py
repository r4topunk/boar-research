#!/usr/bin/env python3
"""SEFIX-ALL seed-43 sanity + judge plan (0 LLM). python3 -I sanity_s43.py -> ans-judge/sanity_s43.json, ans-judge/plan.s43.json
Arms: ans-traces/sefixall-main-s43 (ALL) vs ans-traces/ctlk1-main-s43 (K1 control, stock). Judge plan (cap Haiku 200 = 50 ids x 2 arms x 2 orders): ids whose answer text differs between the arms,
ordered by priority: (1) kept differs, cooking/money; (2) kept differs, v0.1; (3) text-only differs, cooking/money; (4) text-only, v0.1; ties by id order in main-97.ids; first 50."""
import json, collections
A = "<workspace>/rnd/research/coordinator/arms"; SF = A + "/coverage-map/sefix"
ld = lambda p: {json.loads(l)["itemId"]: json.loads(l) for l in open(p)}
ids = open(A + "/lp-screens/main-97.ids").read().split()
T = ld(SF + "/ans-traces/sefixall-main-s43.traces.jsonl"); C = ld(SF + "/ans-traces/ctlk1-main-s43.traces.jsonl")
def loop(txt):
    w = txt.split(); c = collections.Counter(tuple(w[i:i+6]) for i in range(len(w) - 5)); return any(v >= 3 for v in c.values())
seq = lambda t: [(c["title"], c.get("section"), c.get("source")) for c in t["retrieval"]["kept"]]
r = {}
for nm, D in (("ALL", T), ("CTL", C)):
    r[nm] = dict(rows=len(D), missing=[i for i in ids if i not in D], errors=[i for i in ids if i in D and D[i].get("error")],
                 empty=[i for i in ids if i in D and not (D[i]["answer"]["text"] or "").strip()], loops=[i for i in ids if i in D and loop(D[i]["answer"]["text"] or "")])
r["kill"] = any(r[n][k] for n in ("ALL", "CTL") for k in ("missing", "errors", "empty", "loops"))
td = [i for i in ids if T[i]["answer"]["text"] != C[i]["answer"]["text"]]; kd = [i for i in ids if seq(T[i]) != seq(C[i])]
src = lambda i: "v0.1" if not i.startswith("st-") else "se"
# cache: judged rows of the same (id, answer text) from the seed-42 screens (control pool-K1, ARM-G, SEFIX-ALL); a hit costs 0 calls
r42 = json.load(open(SF + "/answers-sefixall.json")); pool = json.load(open(A + "/null-cal/control/pool-K1.json"))["items"]
TG = ld(A + "/coverage-map/compose/screen/traces/cmp-G-K10-main-s42.traces.jsonl"); TF = ld(SF + "/ans-traces/sefixall-main-s42.traces.jsonl")
cache = {}
for i in ids:
    cache[(i, pool[i]["text"])] = "ctl42"; cache[(i, TG[i]["answer"]["text"])] = "G42"; cache[(i, TF[i]["answer"]["text"])] = "ALL42"
new23 = set(r42["newly_delivered_cm"]["items"])
need = {i: [n for n, D in (("ALL", T), ("CTL", C)) if (i, D[i]["answer"]["text"]) not in cache] for i in td}
pri = lambda i: (0 if i in new23 else 1, 0 if i in kd else 1, 0 if src(i) == "se" else 1)
plan, calls = [], 0
for i in sorted(td, key=lambda i: (pri(i), ids.index(i))):
    c = 2 * len(need[i])
    if calls + c <= 200: plan.append(i); calls += c
r.update(text_differs=len(td), kept_differs=len(kd), text_differs_kept_differs=sum(i in kd for i in td), text_only=sum(i not in kd for i in td), cache_hits_among_differing_units=sum(2 - len(need[i]) for i in td),
         plan_ids=len(plan), plan_calls=calls, unjudged=[i for i in td if i not in plan], new23_text_differs=sum(i in new23 for i in td), new23_in_plan=sum(i in new23 for i in plan))
json.dump(r, open(SF + "/ans-judge/sanity_s43.json", "w"), indent=1)
D = SF + "/ans-judge"
open(D + "/plan.s43.ALL.ids", "w").write("\n".join(i for i in plan if "ALL" in need[i]) + "\n"); open(D + "/plan.s43.CTL.ids", "w").write("\n".join(i for i in plan if "CTL" in need[i]) + "\n")
json.dump(dict(plan=plan, need=need), open(D + "/plan.s43.json", "w"), indent=1)
print(json.dumps({k: (v if not isinstance(v, (list, dict)) or len(v) < 8 else f"[{len(v)}]") for k, v in r.items()}))
