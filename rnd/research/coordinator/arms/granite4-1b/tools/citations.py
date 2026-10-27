#!/usr/bin/env python3
"""GRANITE4-1B citation compliance + sanity + length/wall vs control traces on the same items (0 LLM).
Usage: python3 -I citations.py <cand traces.jsonl> <control traces.jsonl>[,<more>] [--json out]
Per run (live items = control generated tokens > 0):
  with_sources  = items whose answer had shown sources (answer.shown non-empty) in the candidate run
  cited         = answers with answer.cited non-empty;  marker = answers whose text contains an [n] marker
  cite_drop     = route reasonCodes grounding:compact-decline-released-uncited-with-sources / -all-citations-removed (engine warns: refused in default mode)
  warned        = answer text starts with the memory-warning line; ctl_cited_lost = control cited, candidate not cited
Sanity: errors, generation_failed, model.sha256 (expected granite 22ec0f9c...), reasoning tokens > 0, role/think token leaks."""
import json, re, sys, statistics as st
SHA = "22ec0f9cc99a90185312de3c882c84e7bd6789bdd050389844380a01a831d7f1"
LEAKS = ("<think>", "</think>", "<|start_of_role|>", "<|end_of_role|>", "<|end_of_text|>", "<tool_call>")
WARN = "Not found in this phone's offline library"
rd = lambda f: {json.loads(l)["itemId"]: json.loads(l) for l in open(f) if l.strip()}
C = rd(sys.argv[1]); K = {}
for f in sys.argv[2].split(","): K.update(rd(f))
ids = sorted(i for i in C if i in K)
def feats(r):
    a = r["answer"]; t = a.get("text") or ""; rc = " ".join((r.get("route") or {}).get("reasonCodes") or [])
    return dict(src=bool(a.get("shown")), cited=bool(a.get("cited")), marker=bool(re.search(r"\[\d+\]", t)),
                drop=("uncited-with-sources" in rc or "all-citations-removed" in rc), warned=t.startswith(WARN), declined=bool(a.get("declined")))
FC = {i: feats(C[i]) for i in ids}; FK = {i: feats(K[i]) for i in ids}
cnt = lambda F, k, xs: sum(F[i][k] for i in xs)
live = [i for i in ids if (K[i]["timing"].get("outputTokens") or 0) > 0]
out = dict(n=len(C), matched=len(ids), live=len(live),
    errors=sum(bool(C[i].get("error")) for i in C), genfail=sum("generation_failed" in json.dumps(C[i]) for i in C),
    sha_bad=sum(C[i]["runtime"]["versions"].get("model.sha256") != SHA for i in C),
    reasoning=sum((C[i]["timing"].get("reasoningTokens") or 0) > 0 for i in C),
    leaks=sum(any(t in (C[i]["answer"].get("text") or "") for t in LEAKS) for i in C),
    temps=sorted({str(C[i]["runtime"]["sampler"].get("temperature")) for i in C}))
for tag, F in (("ctl", FK), ("cand", FC)):
    for k in ("src", "cited", "marker", "drop", "warned", "declined"): out[f"{k}_{tag}"] = cnt(F, k, live)
out["ctl_cited_lost"] = sum(FK[i]["cited"] and not FC[i]["cited"] for i in live)
out["cite_rate_ctl"] = round(out["cited_ctl"] / max(1, out["src_ctl"]), 3); out["cite_rate_cand"] = round(out["cited_cand"] / max(1, out["src_cand"]), 3)
tc = [C[i]["timing"].get("outputTokens") or 0 for i in live]; tk = [K[i]["timing"].get("outputTokens") or 0 for i in live]
wc = [C[i]["timing"].get("totalMs") or 0 for i in ids]; wk = [K[i]["timing"].get("totalMs") or 0 for i in ids]
dc = [C[i]["timing"]["decodeTokPerSec"] for i in live if C[i]["timing"].get("decodeTokPerSec")]
dk = [K[i]["timing"]["decodeTokPerSec"] for i in live if K[i]["timing"].get("decodeTokPerSec")]
if live:
    out.update(tok_med_cand=st.median(tc), tok_med_ctl=st.median(tk), tok_mean_cand=round(st.mean(tc), 1), tok_mean_ctl=round(st.mean(tk), 1), tok_max_cand=max(tc),
               decode_med_cand=round(st.median(dc), 1) if dc else None, decode_med_ctl=round(st.median(dk), 1) if dk else None)
out.update(wall_mean_cand_s=round(st.mean(wc) / 1000, 2), wall_mean_ctl_s=round(st.mean(wk) / 1000, 2), wall_ratio=round(sum(wc) / max(1, sum(wk)), 3))
print(json.dumps(out))
if "--json" in sys.argv: json.dump(out, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
