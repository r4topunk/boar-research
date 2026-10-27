#!/usr/bin/env python3
"""Keep/kill read-out for the stacked arm (B6 + replylang) vs B6 alone, pooled chat-slice v0+v1+v2 (CRITERIA.md).
Criteria 1-3 from score_l0's lang_of / searched_from_trace, 4 = safety v0.8.5 (pre-registered) and v0.8.6 (current),
5 = outofkit identity, 6 = every changed answer printed for the hand read (changed_answers.txt)."""
import importlib.util, json, sys
from pathlib import Path
CS = Path(__file__).resolve().parents[2]; RUNS = CS.parents[3] / "boar-eval/runs"; EXP = CS.parent / "exp"
sys.path.insert(0, str(CS))
from score_l0 import lang_of, searched_from_trace, REPLY_LANG
def mod(p, n):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
SAF = {v: (mod(EXP / f"safety-v{v.replace('.', '')}/safety_check.v{v}.py", v), ) for v in ("0.8.5", "0.8.6")}
SAF = {v: (m, m.load(rules_path=EXP / f"safety-v{v.replace('.', '')}/rules.v{v}.json", overlay_path=EXP / f"safety-v{v.replace('.', '')}/overlay.v0.4.json")) for v, (m,) in SAF.items()}
SL = {"v0": CS / "slice.v0.jsonl", "v1": CS / "v1-fresh/slice.v1.jsonl", "v2": CS / "v2-fresh/slice.v2.jsonl"}
PAIRS = {("v0", "4b"): (RUNS / "kiln/b6replylang/v0-4b-b6gate", RUNS / "kiln/b6replylang/v0-4b-b6replylang"),
         ("v0", "15b"): (RUNS / "kiln/b6replylang/v0-15b-b6gate", RUNS / "kiln/b6replylang/v0-15b-b6replylang"),
         ("v1", "4b"): (CS / "v1-fresh/runs/stack-4b-b6gate", CS / "v1-fresh/runs/stack-4b-b6replylang"),
         ("v1", "15b"): (CS / "v1-fresh/runs/stack-15b-b6gate", CS / "v1-fresh/runs/stack-15b-b6replylang"),
         ("v2", "4b"): (CS / "v2-fresh/runs/b6gate", CS / "v2-fresh/runs/stack-4b-b6replylang"),
         ("v2", "15b"): (CS / "v2-fresh/runs/stack-15b-b6gate", CS / "v2-fresh/runs/stack-15b-b6replylang")}
tr = lambda d: {t["itemId"]: t for t in map(json.loads, open(Path(d) / "traces.jsonl"))}
def unsafe(v, it, t):
    m, S = SAF[v]; r = m.rules_for_v085(it, S)
    return sorted(h["rule"] for h in m.check(t["answer"]["text"], r, S) if h.get("status", "unsafe") == "unsafe") if r else []
out = open(Path(__file__).with_name("changed_answers.txt"), "w")
tot = {}
for (sl, mdl), (pa, pb) in PAIRS.items():
    items = {json.loads(l)["id"]: json.loads(l) for l in open(SL[sl])}
    A, Bt = tr(pa), tr(pb); want = {i: it.get("reply_lang") or REPLY_LANG.get(i) or it["lang"] for i, it in items.items()}
    T = tot.setdefault(mdl, {"n": 0, "lmA": 0, "lmB": 0, "broke": [], "fixed": 0, "route": 0, "newmiss": [], "unsafe85": [], "unsafe86": [], "changed": 0})
    for i, it in items.items():
        a, b = A[i], Bt[i]; la, lb = lang_of(a["answer"]["text"]), lang_of(b["answer"]["text"])
        T["n"] += 1; T["lmA"] += la == want[i]; T["lmB"] += lb == want[i]
        if la == want[i] and lb != want[i]: T["broke"].append(f"{i}({want[i]}:{la}→{lb})")
        T["fixed"] += la != want[i] and lb == want[i]
        sa, sb = searched_from_trace(a), searched_from_trace(b); T["route"] += sa == sb
        if it["expected_search"] == "yes" and sa and not sb: T["newmiss"].append(i)
        for v, key in (("0.8.5", "unsafe85"), ("0.8.6", "unsafe86")):
            ua, ub = unsafe(v, it, a), unsafe(v, it, b)
            if set(ub) - set(ua): T[key].append(f"{i}:{sorted(set(ub) - set(ua))}")
        if a["answer"]["text"] != b["answer"]["text"]:
            T["changed"] += 1
            out.write(f"--- [{sl} {mdl}] {i} ({it['lang']},{it['kind']}) want {want[i]}: {la}→{lb} | expected: {it['expected']}\n  B6 : {a['answer']['text'][:420]!r}\n  ARM: {b['answer']['text'][:420]!r}\n")
for mdl, T in tot.items():
    print(f"== {mdl}: lang_match B6 {T['lmA']}/{T['n']} → arm {T['lmB']}/{T['n']} ({100*T['lmB']/T['n']:.1f}%), +{T['lmB']-T['lmA']}; fixed {T['fixed']}; broke {len(T['broke'])} {T['broke']}")
    print(f"   route identical {T['route']}/{T['n']}; new missed-search {T['newmiss']}; new unsafe v0.8.5 {T['unsafe85']} | v0.8.6 {T['unsafe86']}; changed answers {T['changed']}")
oa, ob = tr(RUNS / "kiln/l1/b6gate-outofkit-quality-s42"), tr(RUNS / "kiln/l1/b6replylang-outofkit-quality-s42")
print(f"== outofkit 4B: identical {sum(oa[i]['answer']['text'] == ob[i]['answer']['text'] for i in oa if i in ob)}/{len(oa)}")
