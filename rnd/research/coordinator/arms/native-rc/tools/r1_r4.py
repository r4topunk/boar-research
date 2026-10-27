#!/usr/bin/env python3
"""NATIVE-RC R1 extras + R4 (0 LLM). Final label per unit = uxmatrix agg final() (A; borderline -> B; A != B -> C majority).
R1: per class (cm 40 / gen-delivered 15 / gen-nopack 5) shares, paired correct-any vs ENGINE-RC S (validation-1024 V2 labels, seed 42) per state.
R4: among NATIVE-RC answers labelled wrong (WRONG_CONFIDENT + WRONG_WARNED), how many show 0 citations (no [n] left in the shown text = the condition
under which ENGINE-RC's warning line fires: the answer cites nothing, or every [n] was removed); split raw-no-[n] vs [n] all removed by cleanCitations;
the same condition on correct answers (false warnings a port would add). usage: python3 -I r1_r4.py -> aggregates/r1-r4.json"""
import json, collections, os, random
A = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); C = os.path.dirname(A)
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
IT = json.load(open(C + "/uxmatrix/items.json"))["items"]
def finals(lf):
    L = collections.defaultdict(dict)
    for r in rd(lf):
        if r["ok"]: L[r["key"]][r["call"]] = r
    def final(k):
        c = L.get(k)
        if not c or "A" not in c: return None
        a = c["A"]
        if a["conf"] != "borderline" or "B" not in c or c["B"]["label"] == a["label"] or "C" not in c: return a["label"]
        v = collections.Counter([a["label"], c["B"]["label"], c["C"]["label"]]).most_common(1)[0]
        return a["label"] if v[1] == 1 else v[0]
    return final
def rows(ans, final, tag):
    out = {}
    for x in IT:
        for st in ("on", "off"):
            a = ans.get(f"{tag}|{st}|{x['id']}") or (ans.get(f"{tag}|on|{x['id']}") if not x["off_minus"] and st == "off" else None)
            if a: out[(st, x["id"])] = dict(a, label=final(a["key"]), cls=x["cls"])
    return out
N = rows(json.load(open(A + "/judge/r1/answers.json")), finals(A + "/judge/r1/labels.jsonl"), "S")
E = rows(json.load(open(C + "/validation-1024/v2/judge/answers.json")), finals(C + "/validation-1024/v2/judge/labels.jsonl"), "S")
CA = ("CORRECT_WITH_SOURCE", "CORRECT_FROM_MEMORY"); WR = ("WRONG_CONFIDENT", "WRONG_WARNED")
def shares(R, st, cls=None):
    xs = [r for k, r in R.items() if k[0] == st and (cls is None or r["cls"] == cls)]; n = len(xs); c = collections.Counter(r["label"] for r in xs)
    return dict(n=n, CWS=round(c["CORRECT_WITH_SOURCE"] / n, 3), correct_any=round((c["CORRECT_WITH_SOURCE"] + c["CORRECT_FROM_MEMORY"]) / n, 3),
                WU=round(c["WRONG_CONFIDENT"] / n, 3), WW=round(c["WRONG_WARNED"] / n, 3), RW=round(c["REFUSED_WRONGLY"] / n, 3), HU=round(c["HONEST_UNKNOWN"] / n, 3), counts=dict(c))
res = dict(native={st: {cls or "all": shares(N, st, cls) for cls in (None, "cm", "gen-delivered", "gen-nopack")} for st in ("on", "off")},
           engine_rc_S={st: {cls or "all": shares(E, st, cls) for cls in (None, "cm", "gen-delivered", "gen-nopack")} for st in ("on", "off")})
def paired(st, pred):
    ids = [x["id"] for x in IT if (st, x["id"]) in N and (st, x["id"]) in E]
    d = [int(pred(N[(st, i)]["label"])) - int(pred(E[(st, i)]["label"])) for i in ids]
    rnd = random.Random(11); bs = sorted(sum(rnd.choice(d) for _ in d) / len(d) for _ in range(2000))
    return dict(n=len(ids), delta=round(sum(d) / len(d), 3), ci=[round(bs[50], 3), round(bs[1949], 3)], better=sum(x > 0 for x in d), worse=sum(x < 0 for x in d))
res["paired_native_minus_engine"] = {f"{st}|{m}": paired(st, p) for st in ("on", "off") for m, p in (("correct_any", lambda l: l in CA), ("CWS", lambda l: l == "CORRECT_WITH_SOURCE"), ("WU", lambda l: l == "WRONG_CONFIDENT"))}
# ON - OFF within NATIVE-RC (55 items with an OFF state)
ids55 = [x["id"] for x in IT if x["off_minus"]]
for m, p in (("correct_any", lambda l: l in CA), ("CWS", lambda l: l == "CORRECT_WITH_SOURCE")):
    d = [int(p(N[("on", i)]["label"])) - int(p(N[("off", i)]["label"])) for i in ids55]
    rnd = random.Random(11); bs = sorted(sum(rnd.choice(d) for _ in d) / len(d) for _ in range(2000))
    res.setdefault("native_on_minus_off", {})[m] = dict(n=55, delta=round(sum(d) / 55, 3), ci=[round(bs[50], 3), round(bs[1949], 3)])
# R4 (render rows carry citationsRaw and citedNums)
REN = {(("off" if r["arm"] == "off" else "on"), r["id"]): r for r in rd(A + "/gen/all.render.jsonl") if r["arm"] in ("on", "off")}
for x in IT:
    if not x["off_minus"]: REN[("off", x["id"])] = REN[("on", x["id"])]
def r4(sel):
    ks = [k for k, r in N.items() if sel(r["label"])]
    nocite = [k for k in ks if not REN[k]["citedNums"]]
    raw0 = [k for k in nocite if REN[k]["citationsRaw"] == 0]
    return dict(n=len(ks), warn_condition=len(nocite), share=round(len(nocite) / len(ks), 3) if ks else None, raw_no_citation=len(raw0), all_citations_removed=len(nocite) - len(raw0),
                by_state={st: dict(n=sum(k[0] == st for k in ks), warn=sum(k[0] == st for k in nocite)) for st in ("on", "off")})
res["R4"] = dict(wrong=r4(lambda l: l in WR), wrong_unwarned=r4(lambda l: l == "WRONG_CONFIDENT"), correct=r4(lambda l: l in CA),
                 note="units = 120 answer rows (60 ON + 60 OFF; gen-nopack OFF = ON row); warn condition = shown text keeps no [n] citation")
res["ux_surface"] = {st: dict(sources_shown_mean=round(sum(REN[(st, x['id'])]["sourcesShown"].__len__() for x in IT) / 60, 2),
                              zero_sources=sum(not REN[(st, x['id'])]["sourcesShown"] for x in IT), any_citation=sum(bool(REN[(st, x['id'])]["citedNums"]) for x in IT),
                              tok_p50=sorted(REN[(st, x['id'])]["tokens_predicted"] for x in IT)[30]) for st in ("on", "off")}
json.dump(res, open(A + "/aggregates/r1-r4.json", "w"), indent=1)
for st in ("on", "off"):
    for cls in ("all", "cm", "gen-delivered", "gen-nopack"):
        a, e = res["native"][st][cls], res["engine_rc_S"][st][cls]
        print(f"{st:3} {cls:13} n{a['n']:3}  NATIVE CWS {a['CWS']:.2f} any {a['correct_any']:.2f} WU {a['WU']:.2f} WW {a['WW']:.2f} HU {a['HU']:.2f} | ENGINE CWS {e['CWS']:.2f} any {e['correct_any']:.2f} WU {e['WU']:.2f} WW {e['WW']:.2f} HU {e['HU']:.2f}")
print(json.dumps(res["paired_native_minus_engine"])); print(json.dumps(res["native_on_minus_off"])); print(json.dumps(res["R4"])); print(json.dumps(res["ux_surface"]))
