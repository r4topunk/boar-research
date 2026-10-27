#!/usr/bin/env python3
"""analyze.py <traces.jsonl> <variants.json>: FOLLOWQ decision numbers + per-item table (markdown on stdout)."""
import json, sys
ts = {}
for l in open(sys.argv[1]):
    t = json.loads(l); ts[t["itemId"]] = t
V = json.load(open(sys.argv[2]))
def srcs(t):  # passages after the engine's grounding (last sources event = what reaches the prompt); [] when none
    ev = [e for e in t["events"] if e["type"] == "sources"]
    return [(s["title"], s.get("section")) for s in (ev[-1]["sources"] if ev else [])]
def raw(t): return [(s["title"], s.get("section")) for s in t["retrieval"]["raw"]]
R = {}
for v in V:
    for q in ("Q0", "Q1", "Q2"):
        t = ts[f"{v['id']}@{q}"]; R[(v["id"], q)] = (srcs(t), raw(t), any(e["type"] == "retrieve" for e in t["events"]))
fol = [v for v in V if v["follow"]]
hist = [v for v in V if v["hist"]]
yes = [v for v in V if v["exp"] == "yes"]
def has(i, q): return len(R[(i, q)][0]) > 0
def gain(vs, q): return [v["id"] for v in vs if not has(v["id"], "Q0") and has(v["id"], q)]
def lose(vs, q): return [v["id"] for v in vs if has(v["id"], "Q0") and not has(v["id"], q)]
def chg(vs, q, k=0): return [v["id"] for v in vs if R[(v["id"], "Q0")][k] != R[(v["id"], q)][k]]
non = [v for v in V if not v["follow"]]
print(f"messages {len(V)}; with history {len(hist)}; follow-ups (rule) {len(fol)} (expected-search yes: {sum(v['exp']=='yes' for v in fol)}); expected-yes {len(yes)}; non-follow-ups {len(non)}")
print(f"Q0 with >=1 passage: all {sum(has(v['id'],'Q0') for v in V)}/192, expected-yes {sum(has(v['id'],'Q0') for v in yes)}/69, follow-ups {sum(has(v['id'],'Q0') for v in fol)}/{len(fol)}")
for q in ("Q1", "Q2"):
    print(f"\n== {q} ==")
    print(f"with >=1 passage: all {sum(has(v['id'],q) for v in V)}/192, expected-yes {sum(has(v['id'],q) for v in yes)}/69, follow-ups {sum(has(v['id'],q) for v in fol)}/{len(fol)}")
    g = gain(fol, q); print(f"DECISION-A follow-ups gaining sources (Q0 none -> {q} >=1): {len(g)}  {g}")
    print(f"  follow-ups expected-yes only gaining: {len([i for i in g if next(v for v in V if v['id']==i)['exp']=='yes'])}; history items (any flag) gaining: {len(gain(hist,q))} {gain(hist,q)}; follow-ups losing sources: {lose(fol,q)}")
    c = chg(non, q); print(f"DECISION-B non-follow-ups whose kept passages change: {len(c)}  {c}   (raw top-k change: {len(chg(non,q,1))} {chg(non,q,1)})")
    print(f"  of which history items: {[i for i in c if next(v for v in V if v['id']==i)['hist']]}; follow-ups whose kept change at all: {len(chg(fol,q))}; follow-ups with raw change: {len(chg(fol,q,1))}")
    print(f"  retrieval ran Q0->{q} (follow-ups): {sum(R[(v['id'],'Q0')][2] for v in fol)} -> {sum(R[(v['id'],q)][2] for v in fol)}")
print("\n## per-item (69 expected-search)")
print("| id | follow-up | n Q0/Q1/Q2 | Q0 top-2 | Q1 top-2 | Q2 top-2 |\n|---|---|---|---|---|---|")
def top(i, q):
    ts_ = []
    for t, s in R[(i, q)][0]:
        if t not in ts_: ts_.append(t)
    return "; ".join(ts_[:2]) or "-"
for v in yes:
    i = v["id"]
    print(f"| {i} | {'y' if v['follow'] else 'n'}{' (hist)' if v['hist'] and not v['follow'] else ''} | {len(R[(i,'Q0')][0])}/{len(R[(i,'Q1')][0])}/{len(R[(i,'Q2')][0])} | {top(i,'Q0')} | {top(i,'Q1')} | {top(i,'Q2')} |")
print("\n## history items (39): variants")
for v in hist: print(f"{v['id']} exp={v['exp']} F={'y' if v['follow'] else 'n'} Q1={v['q']['Q1']!r} Q2={v['q']['Q2']!r}")
