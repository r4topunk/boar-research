#!/usr/bin/env python3
"""SMOLLM3-3B run extras (0 LLM): sanity + citation compliance + answer tokens + wall vs the mini control traces on the same items.
Usage: python3 -I extras.py <candidate traces.jsonl> <K0|K1> <expected non-health temperature> [--json out]
Sanity (criterion §2): n rows, error rows, generation_failed, model.sha256 = 51973255..., reasoning tokens > 0, think-tag leaks (<think>, </think>) in answer text.
Citation compliance: control answers with >= 1 citation (answer.cited) -> how many the candidate answers uncited; candidate cited count; warned
(weak_sources) ctl -> cand; candidate rows with the compact uncited/citations-removed release codes (the mechanism that sank Ministral 3 / Qwen3.5-2B)."""
import json, sys, statistics as st
A = "<workspace>/rnd/research/coordinator/arms"; SHA = "519732558d5fa7420ab058e1b776dcfe73da78013c2fe59c7ca43c325ef89132"
tr, K, temp = sys.argv[1], sys.argv[2], float(sys.argv[3])
C = {r["itemId"]: r for r in map(json.loads, open(tr))}
ctl = {}
for p in [f"{A}/lp-screens/control/traces/lpctl-{K}-main-s42.traces.jsonl", f"{A}/null-cal/control/traces/poolctl-{K}-st180-s42.traces.jsonl"]:
    for r in map(json.loads, open(p)): ctl[r["itemId"]] = r
ids = sorted(C); assert all(i in ctl for i in ids), "control missing ids"
cited = lambda r: bool(r["answer"].get("cited"))
warned = lambda r: "weak_sources" in [str(w) for w in r["answer"].get("warnings") or []] or bool(r["answer"].get("weakSources"))
rel = lambda r: any(x in ("grounding:compact-decline-released-uncited-with-sources", "grounding:compact-decline-released-all-citations-removed") for x in r["route"]["reasonCodes"])
temps = {}
for i in ids: temps.setdefault(C[i]["runtime"]["sampler"].get("temperature"), []).append(i)
live = [i for i in ids if (ctl[i]["timing"].get("outputTokens") or 0) > 0]
tc = [C[i]["timing"].get("outputTokens") or 0 for i in live]; tk = [ctl[i]["timing"].get("outputTokens") or 0 for i in live]
wc = [C[i]["timing"]["totalMs"] for i in ids]; wk = [ctl[i]["timing"]["totalMs"] for i in ids]
dc = [C[i]["timing"]["decodeTokPerSec"] for i in live if C[i]["timing"].get("decodeTokPerSec")]
ctl_cited = [i for i in ids if cited(ctl[i])]
out = dict(run=tr.split("/")[-1], n=len(ids), errors=sum(bool(C[i].get("error")) for i in ids),
           generation_failed=sum("generation_failed" in json.dumps(C[i]) for i in ids),
           sha_bad=sum(C[i]["runtime"]["versions"].get("model.sha256") != SHA for i in ids),
           reasoning_rows=sum((C[i]["timing"].get("reasoningTokens") or 0) > 0 for i in ids),
           think_leak=sum(any(t in (C[i]["answer"]["text"] or "") for t in ("<think>", "</think>")) for i in ids),
           temps={str(t): len(v) for t, v in temps.items()}, expected_temp=temp,
           ctl_cited=len(ctl_cited), ctl_cited_cand_uncited=sum(not cited(C[i]) for i in ctl_cited), cand_cited=sum(cited(C[i]) for i in ids),
           warned_ctl=sum(warned(ctl[i]) for i in ids), warned_cand=sum(warned(C[i]) for i in ids),
           declined_ctl=sum(bool(ctl[i]["answer"].get("declined")) for i in ids), declined_cand=sum(bool(C[i]["answer"].get("declined")) for i in ids),
           uncited_release_codes_cand=sum(rel(C[i]) for i in ids), uncited_release_codes_ctl=sum(rel(ctl[i]) for i in ids),
           live=len(live), tok_median_cand=st.median(tc), tok_median_ctl=st.median(tk), tok_mean_cand=round(st.mean(tc), 1), tok_mean_ctl=round(st.mean(tk), 1),
           tok_max_cand=max(tc), wall_mean_cand_s=round(st.mean(wc) / 1000, 2), wall_mean_ctl_s=round(st.mean(wk) / 1000, 2),
           wall_ratio=round(st.mean(wc) / st.mean(wk), 2), decode_median_cand=round(st.median(dc), 1) if dc else None)
out["citation_compliance"] = f"{len(ctl_cited) - out['ctl_cited_cand_uncited']}/{len(ctl_cited)}"
print(json.dumps(out))
if "--json" in sys.argv: json.dump(out, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
