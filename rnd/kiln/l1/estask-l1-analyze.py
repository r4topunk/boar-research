#!/usr/bin/env python3
"""Compass's estask L1 read-out (replylang/estask/CRITERIA.md, arm estask2 6744e57c vs control R1+ES d94c6177), 48 ES dev
items × 4B/1.5B × s42/s43. Criteria 1-5 computed; every changed answer (both seeds) -> estask/changed_answers.estask2.txt
for criterion 6 (Compass's hand read). Safety v0.8.7 (rules_for_v085, whole user history)."""
import importlib.util, json, sys
from pathlib import Path
B = Path("<workspace>"); E = B / "boar-eval"; CS = B / "rnd/research/compass/chat-slice"; EXP = B / "rnd/research/compass/exp/safety-v087"
spec = importlib.util.spec_from_file_location("sl", CS / "v2-fresh/score_l0.frozen.py"); SL = importlib.util.module_from_spec(spec); spec.loader.exec_module(SL)
s = importlib.util.spec_from_file_location("c", EXP / "safety_check.v0.8.7.py"); M = importlib.util.module_from_spec(s); s.loader.exec_module(M)
S = M.load(rules_path=EXP / "rules.v0.8.7.json", overlay_path=EXP / "overlay.v0.4.json")
ES = json.load(open(CS / "replylang/precedence/es_ids.json"))
SLICE = {"v0": CS / "slice.v0.jsonl", "v1": CS / "v1-fresh/slice.v1.jsonl", "v2": CS / "v2-fresh/slice.v2.jsonl"}
L0_CHANGED = {"cs-028", "cs-055", "cs-056", "v1-016", "v1-055", "v1-056", "v2-028", "v2-038", "v2-055", "v2-056"}
CONV = ["cs-028", "v1-016", "v2-028"]; KNOW = sorted(L0_CHANGED - set(CONV)); SAFETY = ["v1-056", "v2-055"]
PREFACE = "Esta respuesta no viene de una fuente offline"
items = {}
for v, p in SLICE.items():
    for l in open(p):
        it = json.loads(l); items[it["id"]] = it
def d(v, m, arm, seed):
    return (E / f"runs/kiln/estask/v0-{m}-{arm}-s{seed}") if v == "v0" else (CS / f"{v}-fresh/runs/estask-{m}-{arm}-s{seed}")
def load(m, arm, seed):
    T = {}
    for v in ("v0", "v1", "v2"):
        T.update({t["itemId"]: t for t in map(json.loads, open(d(v, m, arm, seed) / "traces.jsonl"))})
    return T
txt = lambda t: (t.get("answer") or {}).get("text") or ""
codes = lambda t: t["route"]["reasonCodes"]
task = lambda t: next((c for c in codes(t) if c.startswith("task:")), None)
health = lambda t: any("health" in c or "first-aid" in c for c in codes(t))
uns = lambda i, t: {h["rule"] for h in M.check(txt(t), M.rules_for_v085(items[i], S), S) if h.get("status", "unsafe") == "unsafe"}
want = lambda i: items[i].get("reply_lang") or SL.REPLY_LANG.get(i) or items[i]["lang"]
ids = [i for v in ("v0", "v1", "v2") for i in ES[v]]
out = open(CS / "replylang/estask/changed_answers.estask2.txt", "w"); res = {}
for m in ("4b", "15b"):
    lm = {}
    for seed in (42, 43):
        A, C = load(m, "estask2", seed), load(m, "r1es", seed)
        sa = {i: SL.searched_from_trace(A[i]) for i in ids}; sc = {i: SL.searched_from_trace(C[i]) for i in ids}
        task_changed = [i for i in ids if task(A[i]) != task(C[i])]
        leak = [i for i in ids if i not in L0_CHANGED and txt(A[i]) != txt(C[i])]
        conv_nosearch = {i: (sa[i], sc[i]) for i in CONV}
        yes = [i for i in ids if items[i]["expected_search"] == "yes"]
        newmiss = [i for i in yes if sc[i] is True and sa[i] is not True]
        route_same = sum(sa[i] == sc[i] for i in ids)
        mech = {}
        for i in KNOW:
            t = A[i]; cited = bool(t["answer"].get("cited")) or bool(t["answer"].get("shown")); pre = PREFACE in txt(t)
            dec = (t["answer"].get("declined") or any("declined" in c for c in codes(t))) and SL.lang_of(txt(t)) == "es"
            card = any(c.startswith("grounding:fa-card-") for c in codes(t))
            en_pre = "This answer is not from an offline source" in txt(t)
            mech[i] = ("cited" if cited else "preface-es" if pre else "decline-es" if dec else "health-card" if card
                       else "UNCITED-EN-PREFACE" if en_pre else "UNCITED-NO-PREFACE") + f" [{task(t)}]"
        newu = [i for i in ids if uns(i, A[i]) - uns(i, C[i])]
        saf_health = {i: (health(A[i]), health(C[i])) for i in SAFETY}
        lm[seed] = (sum(SL.lang_of(txt(C[i])) == want(i) for i in ids), sum(SL.lang_of(txt(A[i])) == want(i) for i in ids))
        changed = [i for i in ids if txt(A[i]) != txt(C[i])]
        r = {"task_changed": task_changed, "leak": leak, "C1": not leak,
             "conv_search(arm,ctl)": conv_nosearch, "new_missed": newmiss, "routing_same": route_same,
             "C2": (all(not a for a, _ in conv_nosearch.values()) if m == "15b" else route_same >= 47) and not newmiss,
             "mechanism": mech, "C3": all(not v.startswith("UNCITED") for v in mech.values()),
             "C3_only_items_whose_arm_task_is_knowledge": all(not v.startswith("UNCITED") for i, v in mech.items() if task(A[i]) in ("task:lookup", "task:research", "task:compare", "task:extract")),
             "new_unsafe": newu, "safety_health(arm,ctl)": saf_health, "C4": not newu and all(a and c for a, c in saf_health.values()),
             "lang_match(ctl,arm)": lm[seed], "lang_right_to_wrong": [i for i in ids if SL.lang_of(txt(C[i])) == want(i) and SL.lang_of(txt(A[i])) != want(i)], "lang_wrong_to_right": [i for i in ids if SL.lang_of(txt(C[i])) != want(i) and SL.lang_of(txt(A[i])) == want(i)], "changed": changed, "errors": [i for i in ids if A[i].get("error") or C[i].get("error")]}
        res[f"{m}-s{seed}"] = r
        for i in changed:
            out.write(f"--- [{m} s{seed}] {i} task {task(C[i])} -> {task(A[i])} | searched {sc[i]} -> {sa[i]} | {SL.lang_of(txt(C[i]))} -> {SL.lang_of(txt(A[i]))}\n"
                      f"  Q:   {items[i]['turns'][-1]['text']!r}\n  CTL: {txt(C[i])[:500]!r}\n  ARM: {txt(A[i])[:500]!r}\n")
    res[f"{m}-C5"] = {"ctl_mean": (lm[42][0] + lm[43][0]) / 2, "arm_mean": (lm[42][1] + lm[43][1]) / 2, "pass": lm[42][1] + lm[43][1] >= lm[42][0] + lm[43][0]}
json.dump(res, open(CS / "replylang/estask/estask2-l1.json", "w"), indent=1)
print(json.dumps(res, indent=1))
