#!/usr/bin/env python3
"""COMBINED stage-0 sanity per seed (0 LLM). python3 -I sanity.py 42|43 -> judge/sanity_s<seed>.json
Arm = traces/combined-main-s<seed>; reference = SEFIX-ALL of the same seed (sefix/ans-traces/sefixall-main-s<seed>). Checks: 97/97 rows, 0 errors/empty/loops; deterministic items (no generate:user-model code or 0 output tokens in the SEFIX-ALL trace)
byte-identical to SEFIX-ALL; items with readseq reason codes; answers that differ from SEFIX-ALL (the judge set); kept multiset identical to SEFIX-ALL (RD1 reorders/drops question chunks, it must not retrieve)."""
import json, sys, collections
A = "<workspace>/rnd/research/coordinator/arms"; CM = A + "/coverage-map"; SF = CM + "/sefix"; CB = CM + "/combined"
s = sys.argv[1]
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
ld = lambda p: {t["itemId"]: t for t in rd(p)}
ids = open(A + "/lp-screens/main-97.ids").read().split()
T = ld(f"{CB}/traces/combined-main-s{s}.traces.jsonl"); F = ld(f"{SF}/ans-traces/sefixall-main-s{s}.traces.jsonl")
def loop(txt):
    w = txt.split(); c = collections.Counter(tuple(w[i:i+6]) for i in range(len(w) - 5)); return any(v >= 3 for v in c.values())
det = lambda t: (t["timing"].get("outputTokens") or 0) == 0 or not any(r.startswith("generate:user-model") for r in t["route"]["reasonCodes"])
ttl = lambda t: [c["title"] for c in t["retrieval"]["kept"]]
seq = lambda t: [(c["title"], c.get("section"), c.get("source")) for c in t["retrieval"]["kept"]]
rs = lambda t: [r for r in t["route"]["reasonCodes"] if r.startswith("readseq")]
r = dict(seed=int(s), rows=len(T), missing=[i for i in ids if i not in T], errors=[i for i in ids if i in T and T[i].get("error")],
         empty=[i for i in ids if i in T and not (T[i]["answer"]["text"] or "").strip()], loops=[i for i in ids if i in T and loop(T[i]["answer"]["text"] or "")])
dets = [i for i in ids if det(F[i])]; r["det_items_in_SEFIXALL"] = len(dets)
r["det_text_diff"] = [i for i in dets if T[i]["answer"]["text"] != F[i]["answer"]["text"]]; r["det_not_det_in_arm"] = [i for i in dets if not det(T[i])]
r["det_identical"] = sum(T[i]["answer"]["text"] == F[i]["answer"]["text"] for i in dets)
r["readseq_fired"] = [i for i in ids if rs(T[i])]; r["readseq_fired_n"] = len(r["readseq_fired"])
r["readseq_codes_in_SEFIXALL"] = sum(1 for i in ids if rs(F[i]))
td = [i for i in ids if T[i]["answer"]["text"] != F[i]["answer"]["text"]]; r["text_differs_vs_SEFIXALL"] = len(td); r["text_differs_ids"] = td
r["text_differs_without_readseq_code"] = [i for i in td if not rs(T[i])]; r["readseq_but_text_same"] = [i for i in r["readseq_fired"] if i not in td]
r["kept_multiset_differs"] = [i for i in ids if collections.Counter(seq(T[i])) != collections.Counter(seq(F[i]))]
r["kept_order_differs"] = [i for i in ids if seq(T[i]) != seq(F[i])]
r["kept_count_differs"] = [i for i in ids if len(seq(T[i])) != len(seq(F[i]))]
m = lambda D, f: round(sum(f(D[i]) for i in ids) / len(ids), 2)
r["mean_out_tok"] = m(T, lambda t: t["timing"].get("outputTokens") or 0); r["SEFIXALL_mean_out_tok"] = m(F, lambda t: t["timing"].get("outputTokens") or 0)
r["mean_kept"] = m(T, lambda t: len(t["retrieval"]["kept"])); r["SEFIXALL_mean_kept"] = m(F, lambda t: len(t["retrieval"]["kept"]))
r["kill"] = bool(r["missing"] or r["errors"] or r["empty"] or r["loops"] or r["det_text_diff"])
json.dump(r, open(f"{CB}/judge/sanity_s{s}.json", "w"), indent=1)
print(json.dumps({k: (v if not isinstance(v, (list, dict)) or len(v) < 10 else f"[{len(v)}]") for k, v in r.items()}))
