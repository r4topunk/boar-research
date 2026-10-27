#!/usr/bin/env python3
"""PIN2-SCREEN aggregate (0 LLM; criterion 175076c0). python3 -I tools/screen_agg.py -> screen.json"""
import json, random, re, glob
D = "<workspace>/rnd/research/coordinator/arms/coverage-map/pin2"; J = D + "/judge"
W = "Not found in this phone's offline library. From the model's memory, may be wrong:"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
ld = lambda p: {t["itemId"]: t for t in rd(p)}
T = {(a, s): ld(f"{D}/traces/pin2screen-{a}-{s}-s42.traces.jsonl") for a in ("base", "pin2") for s in ("main", "t27")}
MAIN = ["vit-hum-002", "vit-cry-008", "lan-exp-005", "trv-004", "st-qa-cooking-se-004"]; T27 = ["b15", "b18"]
def by(files):
    o = {}
    for f in files:
        for r in rd(f):
            if r.get("ok") is True: o.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
    return o
dim = lambda m, k: sum(m[k].values()) / 3
JB = {a: by(glob.glob(f"{J}/{a}-*.judgments.jsonl")) for a in ("base", "pin2")}; JH = by([f"{J}/h2h.judgments.jsonl"]) if glob.glob(f"{J}/h2h.judgments.jsonl") else {}
CTX = json.load(open(D + "/screen_ctx.json"))
base_rep = {r["id"]: r for r in rd(D + "/replays/main.off.jsonl")}; arm_rep = {r["id"]: r for r in rd(D + "/replays/main.PIN2.jsonl")}
t27b = {r["id"]: r for r in rd(D + "/replays/t27.off.jsonl")}; t27x = {r["id"]: r for r in rd(D + "/replays/t27.PIN2.jsonl")}
HEALTH27 = {"q2", "q4", "b2", "b8", "b13", "b14", "b21"}
health = lambda i: (i in HEALTH27) if i in T27 else any(c.startswith("grounding:health-strict") for c in base_rep[i]["reasonCodes"])
titles = lambda t: [c["title"] for c in t["retrieval"]["kept"]]
items = {}
for s, ids in (("main", MAIN), ("t27", T27)):
    for i in ids:
        tb, tx = T[("base", s)][i], T[("pin2", s)][i]; xb, xx = tb["answer"]["text"], tx["answer"]["text"]
        rb, rx = (base_rep, arm_rep) if s == "main" else (t27b, t27x)
        it = dict(set=s, health=health(i), identical=xb == xx, base_text=xb, pin2_text=xx, warned=dict(base=xb.startswith(W), pin2=xx.startswith(W)),
                  declined=dict(base=bool(tb["answer"].get("declined")), pin2=bool(tx["answer"].get("declined"))),
                  live_eq_replay=dict(base=titles(tb) == [c["title"] for c in rb[i]["keptFull"]], pin2=titles(tx) == [c["title"] for c in rx[i]["keptFull"]]),
                  kept=dict(base=titles(tb), pin2=titles(tx)))
        if it["identical"]:
            it.update(verdict="tie", judgment="identical-text", d=0.0)
        elif s == "main":
            mb, mx = list(JB["base"][i].values()), list(JB["pin2"][i].values()); assert len(mb) == len(mx) == 2, i
            sc = lambda ms, dec: 0.0 if dec else sum(dim(m, "boar") for m in ms) / 2
            it.update(s=dict(base=sc(mb, it["declined"]["base"]), pin2=sc(mx, it["declined"]["pin2"])), sref=dict(base=sum(dim(m, "ref") for m in mb) / 2, pin2=sum(dim(m, "ref") for m in mx) / 2),
                      corr=dict(base=sum(m["boar"]["correctness"] for m in mb) / 2, pin2=sum(m["boar"]["correctness"] for m in mx) / 2), judgment="vs-reference",
                      raw=dict(base=mb, pin2=mx))
            it["d"] = it["s"]["pin2"] - it["s"]["base"]
        else:
            mh = list(JH[i].values()); assert len(mh) == 2, i
            it.update(s=dict(base=sum(dim(m, "ref") for m in mh) / 2, pin2=sum(dim(m, "boar") for m in mh) / 2), corr=dict(base=sum(m["ref"]["correctness"] for m in mh) / 2, pin2=sum(m["boar"]["correctness"] for m in mh) / 2),
                      winners=[m["winner"] for m in mh], judgment="head-to-head", raw=dict(h2h=mh))
            it["d"] = it["s"]["pin2"] - it["s"]["base"]
        if "verdict" not in it: it["verdict"] = "better" if it["d"] >= 1 / 3 - 1e-9 else ("worse" if it["d"] <= -1 / 3 + 1e-9 else "tie")
        ce = lambda a: (not it["declined"][a]) and it["corr"][a] <= 1.5 if "corr" in it else False
        it["new_CE"] = bool("corr" in it and ce("pin2") and not ce("base")); it["CE"] = dict(base=ce("base"), pin2=ce("pin2")) if "corr" in it else None
        items[i] = it
jm = [i for i in MAIN if not items[i]["identical"]]
U = lambda a, xs: sum(items[i]["s"][a] for i in xs) / sum(items[i]["sref"][a] for i in xs) if xs else None
def boot(xs, B=2000):
    r = random.Random(11); v = []
    for _ in range(B):
        s = [r.choice(xs) for _ in xs]; v.append(U("pin2", s) - U("base", s))
    v.sort(); return [round(v[int(0.025 * B)], 4), round(v[int(0.975 * B) - 1], 4)]
# identical MAIN items enter U with the same row on both sides only if judged; they have no row, so U is over the divergent MAIN items (stated in the report)
paired = dict(n=len(jm), U_base=round(U("base", jm), 4) if jm else None, U_pin2=round(U("pin2", jm), 4) if jm else None)
if jm: paired.update(dU=round(U("pin2", jm) - U("base", jm), 4), ci=boot(jm))
cnt = {k: sum(items[i]["verdict"] == k for i in items) for k in ("better", "worse", "tie")}
hl = [i for i in items if items[i]["health"] and items[i]["verdict"] == "worse"]; nce = [i for i in items if items[i]["new_CE"]]
calls = sum(int(re.search(r"calls=(\d+)", l).group(1)) for l in open(J + "/calls.log")) if glob.glob(J + "/calls.log") else 0
rule = dict(context_PASS=CTX["PASS"], better_ge_worse_plus_2=cnt["better"] >= cnt["worse"] + 2, health_losses_0=not hl, new_CE_0=not nce)
res = dict(criterion_sha256="175076c03903517a46524f96cebbbcca4e07350f11b70ae67c150234e29b98dc", context=CTX, counts=cnt, paired_U_main_divergent=paired, health_items=[i for i in items if items[i]["health"]], health_losses=hl, new_CE=nce,
           haiku_calls=calls, rule=rule, verdict="LEVER-CANDIDATE" if all(rule.values()) else "NO", items=items)
json.dump(res, open(D + "/screen.json", "w"), indent=1, ensure_ascii=False)
for i, it in items.items(): print(i, it["verdict"], it.get("judgment"), it.get("s"), it.get("corr"), it.get("winners", ""), "newCE" if it["new_CE"] else "", "live=replay", it["live_eq_replay"])
print(json.dumps({k: v for k, v in res.items() if k not in ("items", "context")}, indent=1))
