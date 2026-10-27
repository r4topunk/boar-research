#!/usr/bin/env python3
"""X2B-OFF-MAIN addendum 1 report (0 LLM): step 1 (Opus on the 9 s42 CEu flips) + step 2 (seed 43) + two-seed pooled decision.
Writes main/aggregates/x2b-off-main-addendum1.json."""
import json, glob, random, statistics as st, sys
A = "<workspace>/rnd/research/coordinator/arms"; X = A + "/x2b-retest"; M = X + "/main"
sys.path.insert(0, A + "/null-cal/tools"); from labels import label
ids = open(X + "/main-live77.ids").read().split()
rd = lambda f: {json.loads(l)["itemId"]: json.loads(l) for l in open(f) if l.strip()}
def rows(globs):
    by = {}
    for g in globs:
        for f in sorted(glob.glob(g)):
            for l in open(f):
                if not l.strip(): continue
                r = json.loads(l)
                if r.get("ok") is True: by.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
    out = {}
    for i, o in by.items():
        if len(o) != 2: continue
        ms = list(o.values()); mean = lambda x: sum(x.values()) / 3
        out[i] = dict(s=sum(mean(m["boar"]) for m in ms) / 2, sref=sum(mean(m["ref"]) for m in ms) / 2, corr=sum(m["boar"]["correctness"] for m in ms) / 2)
    return out
# traces
TR = {"ON42": rd(A + "/lp-screens/control/traces/lpctl-K1-main-s42.traces.jsonl"), "OFF42": rd(M + "/x2boffmain/traces/x2boffmain-K1-main-live77-s42.traces.jsonl"),
      "ON43": rd(M + "/x2bon43/traces/x2bon43-K1-main-live77-s42.traces.jsonl"), "OFF43": rd(M + "/x2boff43/traces/x2boff43-K1-main-live77-s42.traces.jsonl")}
# Haiku judgment pool keyed by (id, text)
pool = {}
for f in (A + "/null-cal/control/pool-K1.json", M + "/x2boffmain/aggregates/x2boffmain-K1-main-live77-s42.json", A + "/null-cal/arms/null-s43/aggregates/null-s43-K1-screen2-K1-s42.json"):
    for i, x in json.load(open(f))["items"].items(): pool.setdefault((i, x["text"]), dict(s=x["s"], sref=x["sref"], corr=x["corr"]))
for arm, run in (("ON43", "x2bon43"), ("OFF43", "x2boff43")):
    for i, j in rows([f"{M}/{run}/judgments/{run}-K1-main-live77-s42-*.judgments.jsonl"]).items(): pool.setdefault((i, TR[arm][i]["answer"]["text"]), j)
def items(arm, opus=None):
    out, miss = {}, []
    for i in ids:
        t = TR[arm][i]; txt = t["answer"]["text"]
        j = (opus or {}).get(i) or pool.get((i, txt))
        if j is None: miss.append(i); continue
        out[i] = label(dict(j, text=txt, declined=bool(t["answer"].get("declined"))))
    return out, miss
OP = {"ON42": rows([M + "/opus9/out/on-*.judgments.jsonl"]), "OFF42": rows([M + "/opus9/out/off-*.judgments.jsonl"])}
L = {}; MISS = {}
for arm in TR: L[arm], MISS[arm] = items(arm)
LO = {arm: items(arm, OP[arm])[0] for arm in ("ON42", "OFF42")}
def U(xs, Lx): return sum(0 if Lx[i]["R"] else Lx[i]["s"] for i in xs) / sum(Lx[i]["sref"] for i in xs)
def ceu(xs, Lx): return sum(Lx[i]["CEu"] for i in xs)
def pooledU(xs, pairs):  # pairs = [(L_on, L_off)] per seed; ratio of sums over item-seed rows present in both arms of that seed
    num = lambda side: sum(sum(0 if P[side][i]["R"] else P[side][i]["s"] for i in xs if i in P[0] and i in P[1]) for P in pairs)
    den = lambda side: sum(sum(P[side][i]["sref"] for i in xs if i in P[0] and i in P[1]) for P in pairs)
    return num(1) / den(1) - num(0) / den(0)
def boot(xs, f):
    r = random.Random(11); d = []
    for _ in range(2000): d.append(f([r.choice(xs) for _ in xs]))
    d.sort(); return [round(d[49], 4), round(d[1949], 4)]
def ptok(a, b, xs):
    both = [i for i in xs if (TR[a][i]["timing"].get("promptTokens") or 0) > 0 and (TR[b][i]["timing"].get("promptTokens") or 0) > 0]
    return [round(st.mean(TR[a][i]["timing"]["promptTokens"] for i in both), 1), round(st.mean(TR[b][i]["timing"]["promptTokens"] for i in both), 1), len(both)]
rw = lambda a, xs: [round(st.mean(TR[a][i]["timing"].get("retrievalMs") or 0 for i in xs), 1), round(st.median(TR[a][i]["timing"].get("retrievalMs") or 0 for i in xs), 1)]
out = {"addendum1_sha": open(X + "/X2B-OFF-MAIN-criterion-addendum1.sha256").read().split()[0], "missing": MISS}
flip9 = [i for l in open(M + "/opus9/in/v01.ids").read().split() + open(M + "/opus9/in/qa-cooking-se.ids").read().split() + open(M + "/opus9/in/qa-money-se.ids").read().split() for i in [l]]
out["step1"] = dict(items={i: dict(ON_haiku=[L["ON42"][i]["corr"], L["ON42"][i]["CEu"]], ON_opus=[LO["ON42"][i]["corr"], LO["ON42"][i]["CEu"]],
                                    OFF_haiku=[L["OFF42"][i]["corr"], L["OFF42"][i]["CEu"]], OFF_opus=[LO["OFF42"][i]["corr"], LO["OFF42"][i]["CEu"]]) for i in flip9},
                    CEu_s42_haiku=[ceu(ids, L["ON42"]), ceu(ids, L["OFF42"])], CEu_s42_opus9=[ceu(ids, LO["ON42"]), ceu(ids, LO["OFF42"])],
                    dU_s42_haiku=round(U(ids, L["OFF42"]) - U(ids, L["ON42"]), 4), dU_s42_opus9=round(U(ids, LO["OFF42"]) - U(ids, LO["ON42"]), 4))
X43 = [i for i in ids if i in L["ON43"] and i in L["OFF43"]]
out["n_s42"] = len(ids); out["n_s43"] = len(X43); out["dropped_s43"] = [i for i in ids if i not in X43]
for s in ("42", "43"):
    a, b = L["ON" + s], L["OFF" + s]; xs = ids if s == "42" else X43
    out["seed" + s] = dict(U=[round(U(xs, a), 4), round(U(xs, b), 4)], dU=round(U(xs, b) - U(xs, a), 4), ci=boot(xs, lambda q: U(q, b) - U(q, a)),
                           CEu=[ceu(xs, a), ceu(xs, b)], R=[sum(a[i]["R"] for i in xs), sum(b[i]["R"] for i in xs)],
                           ptok=ptok("ON" + s, "OFF" + s, ids), ret_ms_on=rw("ON" + s, ids), ret_ms_off=rw("OFF" + s, ids),
                           changed_vs_on=sum(TR["OFF" + s][i]["answer"]["text"] != TR["ON" + s][i]["answer"]["text"] for i in xs))
out["seed43"]["on43_vs_on42_changed"] = sum(TR["ON43"][i]["answer"]["text"] != TR["ON42"][i]["answer"]["text"] for i in ids)
out["seed43"]["headpass_add"] = {a: sum(any(c.startswith("headpass:add") for c in TR[a][i]["route"].get("reasonCodes", [])) for i in ids) for a in ("ON43", "OFF43")}
out["seed43"]["errors"] = {a: sum(bool(TR[a][i].get("error")) for i in ids) for a in ("ON43", "OFF43")}
H = [(L["ON42"], L["OFF42"]), (L["ON43"], L["OFF43"])]; O9 = [(LO["ON42"], LO["OFF42"]), (L["ON43"], L["OFF43"])]
cz = lambda P, side: sum(sum(p[side][i]["CEu"] for i in ids if i in p[0] and i in p[1]) for p in P)
for k, P in (("pooled_haiku", H), ("pooled_opus9", O9)):
    out[k] = dict(dU=round(pooledU(ids, P), 4), ci=boot(ids, lambda q, P=P: pooledU(q, P)), rows=len(ids) + len(X43),
                  CEu_on=cz(P, 0), CEu_off=cz(P, 1), dCEu=cz(P, 1) - cz(P, 0))
# same-ids sensitivity: both seeds on the X43 ids only
out["pooled_haiku_X43_only"] = dict(dU=round(pooledU(X43, H), 4), ci=boot(X43, lambda q: pooledU(q, H)))
d = out["pooled_haiku"]; c = out["pooled_opus9"]["dCEu"]  # decision: dU Haiku (base metric), CEu with Opus on the 9 at s42 (addendum 1 Pooling)
safe = d["dU"] >= -0.02 and d["ci"][0] >= -0.05 and c <= 2
out["verdict"] = "OFF is better" if (safe and d["dU"] > 0 and d["ci"][0] > 0) else ("OFF is safe for kit-only installs" if safe else "X2b stays on")
json.dump(out, open(M + "/aggregates/x2b-off-main-addendum1.json", "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "step1"}, indent=None)[:3000]); print(json.dumps(out["step1"])[:3000]); print("VERDICT:", out["verdict"])
