# DEEPMODE set B aggregation (0 LLM; PARA135 agg_b.py / ship15b_analyze.py definitions). python3 -I tools/agg_b.py
import json, sys, os, re, glob, collections, hashlib, importlib.util, unicodedata, numpy as np
A = "<workspace>/rnd/research/coordinator/arms/"; D = A + "deepmode/"; BE = "<workspace>/boar-eval/bench/"
sys.path.insert(0, D + "tools"); from prep_a import context_of, blocks, load as loadgen
assert hashlib.sha256(open(D + "DEEPMODE-criterion.md", "rb").read()).hexdigest() == open(D + "DEEPMODE-criterion.sha256").read().split()[0]
ids = open(A + "native-parity/cv5-51.ids").read().split(); assert len(ids) == 51
TRF = {"DEEP": D + "gen/dm-b-deep-s42/traces.jsonl", "D17": A + "style17-detailed/traces/style17-detailed-K1-main-sub3e6183-s42.traces.jsonl",
       "S17": A + "lp-screens/control/traces/lpctl-K1-main-s42.traces.jsonl"}
TR = {k: {(j := json.loads(l)).get("itemId"): j for l in open(f)} for k, f in TRF.items()}
TX = {k: {q: TR[k][q]["answer"]["text"] or "" for q in ids} for k in TR}
K = ("correctness", "completeness", "usefulness"); mr = lambda d: sum(d[k] for k in K) / 3
def sr(a, b): return {"s": (mr(a["boar"]) + mr(b["boar"])) / 2, "r": (mr(a["ref"]) + mr(b["ref"])) / 2, "corr": (a["boar"]["correctness"] + b["boar"]["correctness"]) / 2}
def load(*paths):
    J = collections.defaultdict(dict)
    for p in paths:
        if not os.path.exists(p): continue
        for l in open(p):
            r = json.loads(l)
            if r.get("ok") and not r.get("floorScored") and r["order"] not in J[r["queryId"]]: J[r["queryId"]][r["order"]] = r["mapped"]
    return {q: sr(v["boarA"], v["boarB"]) for q, v in J.items() if set(v) == {"boarA", "boarB"}}
K1C = load(A + "lp-screens/control/judgments/lpctl-K1-main-s42-v01.judgments.jsonl")
def hk(files, k):
    own = load(*files); out = {}
    for q in ids:
        if q in own: out[q] = own[q]
        else: assert TX[k][q] == TX["S17"][q], (k, q); out[q] = K1C[q]
    return out
H = {"DEEP": hk([D + "judge/b/dm-b-deep-s42-v01.judgments.jsonl"], "DEEP"),
     "D17": hk([A + "style17-detailed/judgments/style17-detailed-K1-main-sub3e6183-s42-v01.judgments.jsonl"], "D17"), "S17": hk([], "S17")}
U = lambda s, r: (s - 1).sum() / (r - 1).sum(); RAW = lambda s, r: s.sum() / r.sum()
ci = lambda x: [round(float(v), 4) for v in np.percentile(x, [2.5, 97.5])]
rng = np.random.default_rng(11); n = len(ids); draws = [rng.integers(0, n, n) for _ in range(2000)]
dec = lambda k, q: bool(TR[k][q]["answer"].get("declined"))
def lv(k, sub=ids):
    J = H[k]; s = np.array([J[q]["s"] for q in sub]); r = np.array([J[q]["r"] for q in sub]); sh = [q for q in sub if not dec(k, q)]
    return {"U": round(U(s, r), 4), "U_ci": ci([U(s[ii], r[ii]) for ii in draws]) if sub is ids else None, "U_raw": round(RAW(s, r), 4), "win_rate": round(float((s > r).mean()), 4),
            "correct_shown_per100": round(100 * sum(J[q]["corr"] >= 4 for q in sh) / len(sub), 2), "ce_per100": round(100 * sum(J[q]["corr"] <= 1.5 for q in sh) / len(sub), 2),
            "declined": len(sub) - len(sh)}
def pair(a, b, sub=None):
    sub = sub or ids; full = sub is ids or len(sub) == n
    sa, ra = np.array([H[a][q]["s"] for q in sub]), np.array([H[a][q]["r"] for q in sub]); sb, rb = np.array([H[b][q]["s"] for q in sub]), np.array([H[b][q]["r"] for q in sub])
    o = {"n": len(sub), "dU": round(U(sa, ra) - U(sb, rb), 4), "better_tie_worse": [int((sa > sb).sum()), int((sa == sb).sum()), int((sa < sb).sum())]}
    if full: o["dU_ci"] = ci([U(sa[ii], ra[ii]) - U(sb[ii], rb[ii]) for ii in draws])
    return o
def cost(k, cap):
    t = [TR[k][q]["timing"] for q in ids]; ot = np.array([x.get("outputTokens") or 0 for x in t]); w = np.array([x.get("totalMs") or 0 for x in t])
    return {"out_tokens_p50": float(np.median(ot)), "out_tokens_mean": round(float(ot.mean()), 1), "at_cap": int((ot >= cap - 1).sum()), "ms_p50": round(float(np.median(w))),
            "retrieval_ms_p50": round(float(np.median([TR[k][q]["timing"].get("retrievalMs") if TR[k][q]["timing"].get("retrievalMs") is not None else sum(e.get("ms") or 0 for e in TR[k][q]["events"] if e.get("type") == "retrieve") for q in ids])), 1), "words_p50": float(np.median([len(TX[k][q].split()) for q in ids])),
            "kept_items": sum(bool(TR[k][q]["retrieval"]["kept"]) for q in ids), "kept_mean": round(float(np.mean([len(TR[k][q]["retrieval"]["kept"]) for q in ids])), 2),
            "banner": sum(bool(re.match(r"^(Not found in this phone's offline library\.|From the model's memory)", TX[k][q].strip(), re.I)) for q in ids),
            "modes": dict(collections.Counter(f'{TR[k][q]["route"].get("tier")}/{TR[k][q]["route"].get("mode", "-")}' for q in ids)),
            "errors": sum(bool(TR[k][q].get("error")) for q in ids), "persona_sha": TR[k][ids[0]]["runtime"]["versions"].get("persona.sha256", "")[:8]}
caps = {"DEEP": 2048, "D17": 1024, "S17": 512}
arms = {k: {**lv(k), **cost(k, caps[k])} for k in ("DEEP", "D17", "S17")}
deepen = [TR["D17"][q]["timing"]["totalMs"] + TR["DEEP"][q]["timing"]["totalMs"] for q in ids]; arms["DEEP"]["deepen_ms_p50"] = round(float(np.median(deepen)))
# chunk-level delivered facts (v0.1 keyed)
R = A + "retrieve-sweep"; rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
src = open(R + "/tools/sweep.py").read().split("\n")
a_ = next(i for i, l in enumerate(src) if l.startswith("spec = importlib.util.spec_from_file_location")); b_ = next(i for i, l in enumerate(src) if l.startswith("FUN = json.load"))
exec("\n".join(src[a_:b_]))
keyed = [q for q in ids if q in QS and QS[q].get("grading", {}).get("must_any")]
_, PD = loadgen("b", "dm-b-deep-s42")
PF = collections.defaultdict(list)
for l in open(A + "para135/gen/p135-b-p1-s42/prompts.jsonl"):
    d = json.loads(l); PF[d["itemId"]].append(d)
def fast_ctx(q):
    for d in reversed(PF[q]):
        s = next((m["content"] for m in d.get("messages", []) if m["role"] == "system"), d.get("prompt", "") or "")
        if "\nContext:\n" in s: return blocks(s.split("\nContext:\n", 1)[1])
    return []
cl = {}; mism = []
for q in ids:
    fb = fast_ctx(q); dctx, dsrc, dtitles, kinds = context_of(PD.get(q, [])); db = blocks(dctx) if dctx else []
    ft = [t for _, t, _ in fb]; d17 = [s["title"] for s in TR["D17"][q]["retrieval"]["kept"]]
    if [t.lower() for t in ft] != [t.lower() for t in d17]: mism.append(q)
    row = dict(fast_n=len(fb), deep_n=len(db), deep_src=dsrc, fast_titles=ft, deep_titles=sorted(set(t for _, t, _ in db)), stages=dict(kinds))
    if q in keyed:
        f = max([share_v01(QS[q], [b]) or 0.0 for _, _, b in fb], default=0.0); g = max([share_v01(QS[q], [b]) or 0.0 for _, _, b in db], default=0.0)
        row.update(fast_best=round(f, 3), deep_best=round(g, 3), fast_fact=bool(f >= 0.5), deep_fact=bool(g >= 0.5))
    cl[q] = row
chunk = dict(keyed=len(keyed), fast_delivered=sum(cl[q]["fast_fact"] for q in keyed), deep_delivered=sum(cl[q]["deep_fact"] for q in keyed),
             gained=[q for q in keyed if cl[q]["deep_fact"] and not cl[q]["fast_fact"]], lost=[q for q in keyed if cl[q]["fast_fact"] and not cl[q]["deep_fact"]],
             fast_ctx_vs_D17_kept_title_mismatch=mism, deep_read_none=[q for q in ids if cl[q]["deep_n"] == 0], fast_read_none=[q for q in ids if cl[q]["fast_n"] == 0],
             deep_chunks_mean=round(float(np.mean([cl[q]["deep_n"] for q in ids])), 2), fast_chunks_mean=round(float(np.mean([cl[q]["fast_n"] for q in ids])), 2))
empty = [q for q in ids if not TR["D17"][q]["retrieval"]["kept"]]; rest = [q for q in ids if q not in empty]
sub = {"fast_kept_empty": dict(ids=empty, DEEP_vs_D17=pair("DEEP", "D17", empty) if empty else None, DEEP_vs_S17=pair("DEEP", "S17", empty) if empty else None),
       "rest": dict(n=len(rest), DEEP_vs_D17=pair("DEEP", "D17", rest), DEEP_vs_S17=pair("DEEP", "S17", rest))}
per = {q: dict(deep=round(H["DEEP"][q]["s"], 3), d17=round(H["D17"][q]["s"], 3), s17=round(H["S17"][q]["s"], 3), ref=round(H["DEEP"][q]["r"], 3),
               deep_corr=H["DEEP"][q]["corr"], mode=f'{TR["DEEP"][q]["route"].get("tier")}/{TR["DEEP"][q]["route"].get("mode", "-")}', deep_ms=TR["DEEP"][q]["timing"]["totalMs"],
               d17_ms=TR["D17"][q]["timing"]["totalMs"], deep_out=TR["DEEP"][q]["timing"].get("outputTokens"), **{k: cl[q].get(k) for k in ("fast_n", "deep_n", "fast_fact", "deep_fact")}) for q in ids}
pr = {"P3_dU_vs_D17_ge_0.02": dict(hit=bool(arms["DEEP"]["U"] - arms["D17"]["U"] >= 0.02), dU=round(arms["DEEP"]["U"] - arms["D17"]["U"], 4)),
      "P4b_time_2x_vs_D17": dict(hit=bool(arms["DEEP"]["ms_p50"] >= 2 * arms["D17"]["ms_p50"]), ratio=round(arms["DEEP"]["ms_p50"] / arms["D17"]["ms_p50"], 2))}
out = {"n": n, "arms": arms, "DEEP_vs_D17": pair("DEEP", "D17"), "DEEP_vs_S17": pair("DEEP", "S17"), "D17_vs_S17": pair("D17", "S17"), "chunk_level": chunk, "subgroups": sub,
       "predictions": pr, "reused_rows_DEEP": sum(1 for q in ids if q not in load(D + "judge/b/dm-b-deep-s42-v01.judgments.jsonl")), "per_item": per}
json.dump(out, open(D + "aggregates/setB.json", "w"), indent=1); print(json.dumps({k: v for k, v in out.items() if k != "per_item"}, indent=1))
