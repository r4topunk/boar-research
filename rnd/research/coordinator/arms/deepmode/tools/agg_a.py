# DEEPMODE set A aggregation (0 LLM). python3 -I tools/agg_a.py. Estimates weight sampled strata by their sizes (criterion).
import json, sys, math, collections, hashlib, numpy as np
D = "<workspace>/rnd/research/coordinator/arms/deepmode/"; T27 = D + "../topics27/"; P135 = D + "../para135/"
assert hashlib.sha256(open(D + "DEEPMODE-criterion.md", "rb").read()).hexdigest() == open(D + "DEEPMODE-criterion.sha256").read().split()[0]
P = json.load(open(D + "judge/prep.json")); AU = {}
for l in open(D + "judge/audit.jsonl"):
    r = json.loads(l)
    if r["ok"]: AU[r["key"]] = r
POS = ["1", "2", "3", "4", "5", "6+"]
def wilson(k, n):
    if n == 0: return None
    z = 1.96; p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 3), round(c + h, 3)]
bad = lambda a: a["label"] in ("UNSUPPORTED", "PARTIAL") and a["invented_specific"]
def table(units, lab):
    st = collections.defaultdict(list); [st[u["pos"]].append(u) for u in units]; res = {}; inv_t = 0; uns_t = 0; par_t = 0; N = len(units)
    for p in POS:
        us = st.get(p, []); au = [lab[u["key"]] for u in us if u["key"] in lab]; m = len(au)
        uns = sum(a["label"] == "UNSUPPORTED" for a in au); par = sum(a["label"] == "PARTIAL" for a in au); inv = sum(map(bad, au))
        ie = inv * len(us) / m if m else 0; inv_t += ie; uns_t += uns / m * len(us) if m else 0; par_t += par / m * len(us) if m else 0
        res[p] = dict(sentences=len(us), audited=m, unsupported=uns, partial=par, invented=inv, unsup_share=round(uns / m, 3) if m else None, unsup_ci=wilson(uns, m),
                      inv_per_audited=round(inv / m, 3) if m else None, inv_est=round(ie, 1))
    for p in POS: res[p]["share_of_invented"] = round(res[p]["inv_est"] / inv_t, 3) if inv_t else None
    au = [lab[u["key"]] for u in units if u["key"] in lab]
    tot = dict(sentences=N, audited=len(au), unsupported_sample=sum(a["label"] == "UNSUPPORTED" for a in au), partial_sample=sum(a["label"] == "PARTIAL" for a in au),
               invented_sample=sum(map(bad, au)), unsup_share_est=round(uns_t / N, 3) if N else None, partial_share_est=round(par_t / N, 3) if N else None,
               invented_est=round(inv_t, 1), num_absent=sum(u.get("num_absent", 0) for u in units), missing=len([u for u in units if u["key"] in set(P["sample"]) and u["key"] not in lab]))
    tot["unsup_share_sample"] = round(tot["unsupported_sample"] / len(au), 3) if au else None
    return res, tot
it = P["items"]; res, tot = table(P["units"], AU)
# multipass sets no timing.retrievalMs: sum of the trace's retrieve events (ms) instead
RMS = {(j := json.loads(l))["itemId"]: sum(e.get("ms") or 0 for e in j["events"] if e.get("type") == "retrieve") for l in open(D + "gen/dm-a-deep-s42/traces.jsonl")}
med = lambda xs: float(np.median([x for x in xs if x is not None])) if xs else None
ot = [i["out_tokens"] or 0 for i in it]
tot.update(banner=sum(bool(i["banner"]) for i in it), out_tokens_p50=med(ot), out_tokens_mean=round(float(np.mean(ot)), 1), at_cap=sum(o >= 2047 for o in ot),
           words_p50=med([i["words"] for i in it]), words_mean=round(float(np.mean([i["words"] for i in it])), 1), ms_p50=round(med([i["total_ms"] for i in it])),
           retrieval_ms_p50=med([i["retrieval_ms"] if i["retrieval_ms"] is not None else RMS[i["key"]] for i in it]), retrieval_ms_events_p50=med(list(RMS.values())), hit=sum(i["hit"] for i in it), in_raw=sum(i["in_raw"] for i in it),
           chunks_read_p50=med([i["n_read"] for i in it]), chunks_read_mean=round(float(np.mean([i["n_read"] for i in it])), 2), read_none=sum(i["n_read"] == 0 for i in it),
           modes=dict(collections.Counter(f'{i["tier"]}/{i["mode"]}/{i["ctx_src"]}' for i in it)), declined=sum(bool(i["declined"]) for i in it),
           errors=sum(bool(i["error"]) for i in it), persona_sha=(it[0]["persona_sha"] or "")[:8],
           stages_mean={k: round(np.mean([i["stages"].get(k, 0) for i in it]), 2) for k in ("decompose", "research", "synthesize", "single", "other")})
# references (0 calls)
TI = {o["key"]: o for o in json.load(open(T27 + "aggregates/titles.json"))}
def ref(path):
    tr = {json.loads(l)["itemId"]: json.loads(l) for l in open(path)}; out = {}
    for k, t in tr.items():
        an = {x.lower() for g in TI[k]["groups"] for x in g}; kept = [s["title"] for s in t["retrieval"]["kept"]]; tm = t["timing"]
        out[k] = dict(hit=any(x.lower() in an for x in kept), n_kept=len(kept), kept=kept, ms=tm.get("totalMs"), rms=tm.get("retrievalMs"), ot=tm.get("outputTokens"),
                      words=len((t["answer"]["text"] or "").split()))
    return out
RD, RS = ref(T27 + "gen/traces.jsonl"), ref(T27 + "gen-succinct/traces.jsonl")
summ = lambda R: dict(hit=sum(v["hit"] for v in R.values()), kept_p50=med([v["n_kept"] for v in R.values()]), kept_mean=round(float(np.mean([v["n_kept"] for v in R.values()])), 2),
                      kept_none=sum(v["n_kept"] == 0 for v in R.values()), ms_p50=round(med([v["ms"] for v in R.values()])), retrieval_ms_p50=med([v["rms"] for v in R.values()]),
                      out_tokens_p50=med([v["ot"] for v in R.values()]), words_p50=med([v["words"] for v in R.values()]))
S27 = json.load(open(T27 + "aggregates/summary.json")); SS = json.load(open(T27 + "aggregates/succinct-summary.json"))
refs = {"detailed": {**summ(RD), "unsup_share": S27["unsup_share"], "unsup_share_all_per_sentence": SS["sensitivity_all_per_sentence"]["detailed"]["unsup_share"],
                     "sentences": S27["sentences"], "invented": S27["invented"], "banner": S27["banner"]},
        "succinct": {**summ(RS), "unsup_share": SS["unsup_share"], "sentences": SS["sentences"], "invented": SS["invented"], "banner": SS["banner"]}}
DP = json.load(open(P135 + "aggregates/setA.json"))["detailed_topics27"]
per = {i["key"]: dict(deep_hit=i["hit"], fast_hit=RD[i["key"]]["hit"], deep_read=i["n_read"], fast_kept=RD[i["key"]]["n_kept"], deep_titles=sorted(set(i["read_titles"])),
                      fast_titles=RD[i["key"]]["kept"], mode=f'{i["tier"]}/{i["mode"]}', banner=bool(i["banner"]), n_sent=i["n_sent"], out_tokens=i["out_tokens"],
                      ms=i["total_ms"], fast_ms=RD[i["key"]]["ms"]) for i in it}
gained = [k for k, v in per.items() if v["deep_hit"] and not v["fast_hit"]]; lost = [k for k, v in per.items() if v["fast_hit"] and not v["deep_hit"]]
pred = {"P1_hit_plus2": dict(hit=tot["hit"] >= refs["detailed"]["hit"] + 2, deep=tot["hit"], fast=refs["detailed"]["hit"], gained=gained, lost=lost),
        "P2_unsup_between": dict(hit=SS["unsup_share"] < tot["unsup_share_est"] < S27["unsup_share"], deep=tot["unsup_share_est"], succinct=SS["unsup_share"], detailed=S27["unsup_share"]),
        "P4a_time_2x": dict(hit=tot["ms_p50"] >= 2 * refs["detailed"]["ms_p50"], ratio=round(tot["ms_p50"] / refs["detailed"]["ms_p50"], 2))}
out = dict(deep=dict(total=tot, by_pos=res), refs=refs, detailed_by_pos=DP, per_topic=per, predictions=pred)
json.dump(out, open(D + "aggregates/setA.json", "w"), indent=1)
print(json.dumps(tot, indent=0)); [print(p, res[p]) for p in POS]; print(json.dumps(refs)); print(json.dumps(pred))
