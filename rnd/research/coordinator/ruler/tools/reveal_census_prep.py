#!/usr/bin/env python3
"""REVEAL-CENSUS prep (0 calls). python3 -I reveal_census_prep.py -> ../reveal-census/in/{set.json,<pop>-<unit>.ids}
Rows = tools/warncal_showanyway.py data section exec'd UNCHANGED (sha 8e162cea...), source MINI, arm K0 (1.7B lp-screens/null-cal control, mini frame, s42).
Population MAIN = MAIN 97 rows hidden (declined / warned / no kept source) and not a decline (text exists): the CV5-PER100 1.7B hidden-with-text population.
Population ST = the 180 self-tests (ST-SE 100 + ST-cand 80), same definition; stratified sample of 38 (strata = set x health; proportional, largest remainder,
>= 4 per non-empty stratum; random.Random(f"reveal-census-{stratum}")).
Unit = (item, sha16(text), refs sha of the frame). Existing Opus judge.v1 both-order pairs on the identical unit are reused (any file under boar-eval/ or rnd/,
never blind/ or veil/). New units are listed in ids files ordered divergent-main / divergent-st180 ids first."""
import json, os, sys, glob, hashlib, random, collections
HERE = os.path.dirname(os.path.abspath(__file__)); RUL = os.path.dirname(HERE); OUT = f"{RUL}/reveal-census/in/"; ROOT = "<workspace>"
WC = f"{HERE}/warncal_showanyway.py"; src = open(WC).read(); assert hashlib.sha256(src.encode()).hexdigest().startswith("8e162cea"), "warncal changed"
G = {"__file__": WC, "__name__": "warncal_defs"}; exec(src[:src.index("def wilson")], G)
A = G["A"]; R = [r for r in G["R"] if r["src"] == "MINI" and r["arm"] == "K0"]
TRF = {"MAIN": f"{A}/lp-screens/control/traces/lpctl-K0-main-s42.traces.jsonl", "ST": f"{A}/null-cal/control/traces/poolctl-K0-st180-s42.traces.jsonl"}
TX = {}
for p, f in TRF.items():
    for l in open(f):
        if l.strip(): t = json.loads(l); TX[t["itemId"]] = t["answer"]["text"]
unit_of = lambda i: "v01" if not i.startswith("st-") else i[3:].rsplit("-", 1)[0]
JD = {"MAIN": f"{A}/lp-screens/control/judgments/lpctl-K0-main-s42-", "ST": f"{A}/null-cal/control/judgments/poolctl-K0-st180-s42-"}
def frame(pop, u):
    f = f"{JD[pop]}{u}.judgments.jsonl"; r = json.loads(open(f).readline()); return r["refsSha256"]
pop = {"MAIN": [r for r in R if r["set"] == "MAIN" and r["hidden"] and not r["dec"]],
       "ST": [r for r in R if r["set"] in ("ST-SE", "ST-cand") and r["hidden"] and not r["dec"]]}
for r in pop["MAIN"] + pop["ST"]: assert TX[r["id"]].startswith(r["text200"]), r["id"]
# ST stratified sample
NS = 38; by = collections.defaultdict(list)
for r in pop["ST"]: by[f'{r["set"]}|{"h" if r["health"] else "nh"}'].append(r["id"])
N = len(pop["ST"]); ks = sorted(by); quota = {k: NS * len(by[k]) / N for k in ks}; alloc = {k: min(len(by[k]), max(4, int(quota[k]))) for k in ks}
for k in sorted(ks, key=lambda k: -(quota[k] - int(quota[k]))):
    if sum(alloc.values()) >= NS: break
    if alloc[k] < len(by[k]): alloc[k] += 1
while sum(alloc.values()) > NS: k = max(ks, key=lambda k: alloc[k] - quota[k]); alloc[k] -= 1
sample = {}
for k in ks:
    ids = sorted(by[k]); random.Random(f"reveal-census-{k}").shuffle(ids); sample[k] = sorted(ids[:alloc[k]])
# Opus reuse index
need = {}
for p, rows in (("MAIN", pop["MAIN"]), ("ST", [r for r in pop["ST"] if any(r["id"] in v for v in sample.values())])):
    for r in rows:
        k = f'{r["id"]}|{hashlib.sha256(TX[r["id"]].encode()).hexdigest()[:16]}|{frame(p, unit_of(r["id"]))[:16]}'; need[k] = (p, r["id"])
sha2tr = {}
for base in (f"{ROOT}/boar-eval", f"{ROOT}/rnd"):
    for dp, dn, fn in os.walk(base):
        dn[:] = [d for d in dn if d not in ("blind", "veil", "node_modules", ".git") and not d.endswith(".shards")]
        for f in fn:
            if f.endswith(".traces.jsonl") or f == "traces.jsonl": pth = f"{dp}/{f}"; sha2tr.setdefault(hashlib.sha256(open(pth, "rb").read()).hexdigest(), pth)
want_ids = {v[1] for v in need.values()}; grp = collections.defaultdict(dict); TC = {}
for base in (f"{ROOT}/boar-eval", f"{ROOT}/rnd"):
    for dp, dn, fn in os.walk(base):
        dn[:] = [d for d in dn if d not in ("blind", "veil", "node_modules", ".git") and not d.endswith(".shards") and not d.endswith(".preflight")]
        for f in fn:
            if "judgments" not in f or not f.endswith(".jsonl") or "/reveal-census/" in dp: continue
            for l in open(f"{dp}/{f}"):
                if '"claude-opus-5-5"' not in l: continue
                x = json.loads(l)
                if x.get("ok") is not True or x.get("floorScored") or x.get("judgeVersion") != "judge.v1" or x["queryId"] not in want_ids: continue
                ts = x.get("tracesSha256")
                if ts not in sha2tr: continue
                if ts not in TC: TC[ts] = {(t := json.loads(l2)).get("itemId"): t["answer"]["text"] for l2 in open(sha2tr[ts]) if l2.strip()}
                tx = TC[ts].get(x["queryId"])
                if tx is None: continue
                k = f'{x["queryId"]}|{hashlib.sha256(tx.encode()).hexdigest()[:16]}|{(x.get("refsSha256") or "")[:16]}'
                if k in need: grp[(k, f"{dp}/{f}")][x["order"]] = x["mapped"]
reuse = {}
for (k, f), v in sorted(grp.items()):
    if set(v) == {"boarA", "boarB"}: reuse.setdefault(k, dict(file=os.path.relpath(f, ROOT), files=[], mapped=[]));  reuse[k]["files"].append(os.path.relpath(f, ROOT)) if set(v) == {"boarA", "boarB"} else None; reuse[k]["mapped"].append(v) if set(v) == {"boarA", "boarB"} else None
div = [l.strip() for f in ("divergent-main.ids", "divergent-st180.ids") for l in open(f"{RUL}/ids/{f}") if l.strip()]
files = collections.defaultdict(list)
for k, (p, i) in need.items():
    if k not in reuse: files[f"{p}-{unit_of(i)}"].append(i)
for f in glob.glob(OUT + "*.ids"): os.remove(f)
for f, ids in files.items():
    ids = sorted(ids, key=lambda i: (i not in div, i)); open(OUT + f"{f}.ids", "w").write("".join(i + "\n" for i in ids))
slim = lambda r: {k: r[k] for k in ("id", "set", "w", "kept", "ot", "corr", "s", "sref", "CE", "correct", "bucket", "health", "tier", "text200")}
new = sum(len(v) for v in files.values())
doc = dict(warncal_sha256=hashlib.sha256(src.encode()).hexdigest(), traces=TRF, pop={p: [slim(r) for r in v] for p, v in pop.items()},
           pop_n={p: len(v) for p, v in pop.items()}, st_strata={k: len(v) for k, v in by.items()}, st_alloc=alloc, st_sample=sample,
           units={k: dict(pop=p, id=i, reuse=reuse[k]["files"] if k in reuse else None) for k, (p, i) in need.items()}, reuse_mapped={k: v["mapped"] for k, v in reuse.items()},
           n_units=len(need), reused=len(reuse), new_units=new, planned_calls=2 * new, files={k: len(v) for k, v in files.items()})
json.dump(doc, open(OUT + "set.json", "w"), indent=1)
print(json.dumps({k: doc[k] for k in ("pop_n", "st_strata", "st_alloc", "n_units", "reused", "new_units", "planned_calls", "files")}))
