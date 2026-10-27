#!/usr/bin/env python3
"""HON-10 WARN-OPUS sample builder (0 calls). python3 -I warn_opus_prep.py -> ../warn-opus/in/{set.json,<arm>-<unit>.ids}
Rows = the frozen WARNCAL/SHOWANYWAY LP rows (warncal_showanyway.py row-building section, exec'd unchanged; no output files written).
Unit = unique answer (item id, answer text) within a stratum; weight = number of LP rows (K0/K1/K3) carrying that answer in the stratum.
Strata (MS = MAIN 97 + ST-SE 100; non-decline LP rows):
  W-nh  warned, not health-tagged ............ SRS n_W_NH
  W-h   warned, health-tagged ................ census
  H-nh  unwarned hidden (ot>0, no kept), not health  SRS n_H_NH
  H-h   unwarned hidden, health-tagged ....... census
  S     unwarned shown (not hidden) .......... SRS n_S
  CAND-h  ST-cand revealable hidden (warned or no-kept), health-tagged ... census (health / safety only, not in MS estimates)
Representative row for judging = first of K0, K1, K3 carrying the answer. Existing Opus judge.v1 judgments of the same (item, text)
from CE-OPUS-RU (LP K3 traces) are reused (0 calls)."""
import json, glob, random, hashlib, collections, sys
SEED = 2110; N_W_NH, N_H_NH, N_S = 20, 11, 16
T = "<workspace>/rnd/research/coordinator/ruler/tools/warncal_showanyway.py"; S = open(T).read()
G = {"__file__": T, "__name__": "warnopus"}; exec(S[:S.index("# ---------------- HON-1")], G)
A = G["A"]; LPD = G["LP"]; OUT = "<workspace>/rnd/research/coordinator/ruler/warn-opus"
TX = {a: G["traces"](sorted(glob.glob(f"{LPD}/traces/lp-{a}-*-s42.traces.jsonl"))) for a in ("K0", "K1", "K3")}
def stratum(r):
    if r["dec"]: return None
    if r["set"] == "ST-cand": return "CAND-h" if (r["revealable"] and r["health"]) else None
    if r["w"]: return "W-h" if r["health"] else "W-nh"
    if r["hidden"]: return "H-h" if r["health"] else "H-nh"
    return "S"
units = collections.defaultdict(dict)  # stratum -> key -> unit
for r in G["R"]:
    if r["src"] != "LP": continue
    s = stratum(r)
    if s is None: continue
    txt = TX[r["arm"]][r["id"]]["answer"]["text"]; key = r["id"] + "|" + hashlib.sha256(txt.encode()).hexdigest()[:16]
    u = units[s].setdefault(key, dict(key=key, id=r["id"], set=r["set"], rows=[]))
    u["rows"].append(dict(arm=r["arm"], haiku_corr=r["corr"], haiku_s=r["s"], haiku_sref=r["sref"], w=r["w"], hidden=r["hidden"], health=r["health"], bucket=r["bucket"], tier=r["tier"]))
pop = {s: dict(units=len(u), rows=sum(len(x["rows"]) for x in u.values()), haiku_ce_rows=sum(r["haiku_corr"] <= 1.5 for x in u.values() for r in x["rows"]),
              haiku_correct_rows=sum(r["haiku_corr"] >= 4 for x in u.values() for r in x["rows"])) for s, u in units.items()}  # census Haiku totals (auxiliary for the difference estimator)
take = {"W-nh": N_W_NH, "H-nh": N_H_NH, "S": N_S}
sample = {}
for s, u in sorted(units.items()):
    keys = sorted(u)
    if s in take: random.Random(f"{SEED}-{s}").shuffle(keys); keys = keys[:take[s]]
    sample[s] = [u[k] for k in keys]
# judging units (dedup across strata), representative arm, reuse of CE-OPUS-RU Opus judgments
reuse = {}
RU = f"{A}/refuse-unsupported/ce-opus-ru/out"; tk3 = TX["K3"]
for f in glob.glob(f"{RU}/*.judgments.jsonl"):
    for l in open(f):
        x = json.loads(l)
        if x.get("ok") and x["queryId"] in tk3:
            k = x["queryId"] + "|" + hashlib.sha256(tk3[x["queryId"]]["answer"]["text"].encode()).hexdigest()[:16]; reuse.setdefault(k, set()).add(x["order"])
judge = {}
for s, us in sample.items():
    for u in us:
        if u["key"] in judge: continue
        arm = next(a for a in ("K0", "K1", "K3") if any(r["arm"] == a for r in u["rows"]))
        ru = reuse.get(u["key"]) == {"boarA", "boarB"}
        judge[u["key"]] = dict(id=u["id"], arm="K3" if ru else arm, reuse_ceopusru=ru)
def bunit(i):
    if not i.startswith("st-"): return "v01"
    return i[3:].rsplit("-", 1)[0]
files = collections.defaultdict(list)
for k, j in sorted(judge.items()):
    if not j["reuse_ceopusru"]: files[f'{j["arm"]}-{bunit(j["id"])}'].append(j["id"])
for f in glob.glob(f"{OUT}/in/*.ids"): __import__("os").remove(f)
for fu, ids in files.items():
    assert len(ids) == len(set(ids)), fu
    open(f"{OUT}/in/{fu}.ids", "w").write("".join(i + "\n" for i in ids))
new = sum(len(v) for v in files.values())
doc = dict(seed=SEED, n=dict(W_nh=N_W_NH, H_nh=N_H_NH, S=N_S), population=pop, sample={s: [dict(key=u["key"], id=u["id"], set=u["set"], rows=u["rows"]) for u in us] for s, us in sample.items()},
           judge=judge, files={k: len(v) for k, v in files.items()}, unique_answers=len(judge), reused=sum(j["reuse_ceopusru"] for j in judge.values()), new_answers=new, planned_calls=2 * new)
json.dump(doc, open(f"{OUT}/in/set.json", "w"), indent=1)
print(json.dumps(dict(population=pop, sample={s: len(v) for s, v in sample.items()}, unique=len(judge), reused=doc["reused"], new=new, calls=2 * new, files=doc["files"])))
