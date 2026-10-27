#!/usr/bin/env python3
"""QREWRITE stage 0 oracle maps (criterion 60fdc688). -> ../items/oracle.json {id: text} (ST180 + MAIN97) + oracle.meta.json"""
import json, importlib.util
A = "<workspace>/rnd/research/coordinator/arms"; Q = A + "/qrewrite"; ST = "<workspace>/rnd/research/packs/selftest/"
BE = "<workspace>/boar-eval/bench/"
spec = importlib.util.spec_from_file_location("pc", BE.replace("bench/", "") + "scorers/vendor/lantern/precheck.py"); pc = importlib.util.module_from_spec(spec); spec.loader.exec_module(pc)
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
QF = rd(A + "/qform/items/qform.jsonl")
f5 = {q["fact_id"]: q["question"] for q in QF if q["form"] == 5}
st2f5 = {q["selftest"]["id"]: f5[q["fact_id"]] for q in QF if q["form"] == 0 and q.get("selftest")}
pp = [json.loads(l)["item"]["id"] for g in ("on-k13", "on-k13+qa-bitcoin-se", "on-k13+qa-ethereum-se") for l in open(f"{A}/packproof/in/{g}.requests.jsonl")]
main = [json.loads(l)["item"] for l in open(A + "/decode-ground/runs/req/dg-S-K1-main-s42.requests.jsonl")]
stx = {}
for p in ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se", "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en", "qa-cooking-se", "qa-money-se"]:
    for x in rd(ST + p + ".jsonl"): stx[x["id"]] = x
v01 = {q["id"]: q for q in rd(BE + "v0.1/questions.public.jsonl")}
out, meta = {}, {}
for i in pp + [m["id"] for m in main]:
    if i in st2f5: out[i] = st2f5[i]; meta[i] = "qform-F5"
    elif i in stx: out[i] = ". ".join(f["fact"].rstrip(". ") for f in stx[i]["in_pack_facts"]) + "."; meta[i] = "selftest-facts"
    elif i in v01:
        q = v01[i]; g = q.get("grading", {}); qq = pc.norm(q["question"]); terms = []
        for grp in g.get("must_any", []):
            live = [t for t in grp if not t.startswith("re:") and not pc.is_echo(t, qq)]
            if live: terms.append(live[0])
        mk = g.get("must_k")
        if mk: terms += [t for t in mk["terms"] if not t.startswith("re:") and not pc.is_echo(t, qq)]
        if terms: out[i] = q["question"] + " " + " ".join(dict.fromkeys(terms)); meta[i] = "v01-question+terms"
        else: meta[i] = "none"
    else: meta[i] = "none"
json.dump(out, open(Q + "/items/oracle.json", "w"), indent=0, ensure_ascii=False); json.dump(meta, open(Q + "/items/oracle.meta.json", "w"), indent=0)
import collections; print(len(pp), len(main), len(out), collections.Counter(meta.values()))
