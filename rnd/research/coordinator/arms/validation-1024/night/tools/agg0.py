#!/usr/bin/env python3
"""VALIDATION 2026-10-24 night: 0-LLM metrics per mini job (ADDENDUM-1 section 2). usage: python3 -I agg0.py [job ...]   (after sync_mini.sh fetch)
Reads night/fetched/<job>/out/<NN-group>/traces.jsonl, job.json reference. Writes night/aggregates/<job>.json and night/aggregates/NIGHT0.md.
Per job (and per group): n, errors, output tokens p50/p90, outputs at the 512 cap, time p50 (timing.totalMs), prompt tokens p50, Not-found banner rate,
'passages found' banner rate (bannerkept), health decline line rate, declined rate, warnings rate, funnel means raw / kept / shown / cited and share with >= 1 cited;
divergence vs the reference traces: items present in both, answer text differs, kept list (title + source, in order) differs."""
import json, os, re, sys, glob
N = "<workspace>/rnd/research/coordinator/arms/validation-1024/night"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
q = lambda v, p: sorted(v)[min(len(v) - 1, int(p * len(v)))] if v else None
W1 = "Not found in this phone's offline library."; W2 = "The passages found don't support this answer."; H = "I don't have a reliable offline source"
def ref_traces(ref, g):
    """reference = a traces file (by item id) or a dir of group dirs (<g>, NN-<g>, or out/NN-<g>)."""
    if not ref: return {}
    if os.path.isfile(ref): return {t["itemId"]: t for t in rd(ref)}
    gg = re.sub(r"^\d\d-", "", g)
    for c in (f"{ref}/{gg}/traces.jsonl", f"{ref}/{g}/traces.jsonl", f"{ref}/out/{g}/traces.jsonl", f"{ref}/traces.jsonl"):
        if os.path.exists(c): return {t["itemId"]: t for t in rd(c)}
    return {}
kl = lambda t: [(c["title"], c["source"]) for c in (t.get("retrieval") or {}).get("kept") or []]
def stats(T, R):
    n = len(T); A = [t.get("answer") or {} for t in T]; tm = [t.get("timing") or {} for t in T]
    tok = [x.get("outputTokens") or 0 for x in tm]; sh = lambda k: round(k / n, 3) if n else None
    both = [t for t in T if t["itemId"] in R]
    return dict(n=n, errors=sum(bool(t.get("error")) for t in T), out_tokens_p50=q(tok, .5), out_tokens_p90=q(tok, .9), at_cap_512=sum(x >= 512 for x in tok),
                time_ms_p50=q([x["totalMs"] for x in tm if x.get("totalMs")], .5), prompt_tokens_p50=q([x["promptTokens"] for x in tm if x.get("promptTokens")], .5),
                banner_notfound=sh(sum((a.get("text") or "").startswith(W1) for a in A)), banner_passages_found=sh(sum((a.get("text") or "").startswith(W2) for a in A)),
                health_decline_line=sh(sum((a.get("text") or "").startswith(H) for a in A)), declined=sh(sum(bool(a.get("declined")) for a in A)),
                warnings=sh(sum(bool(a.get("warnings")) for a in A)),
                raw_mean=round(sum(len((t.get("retrieval") or {}).get("raw") or []) for t in T) / n, 2) if n else None,
                kept_mean=round(sum(len(kl(t)) for t in T) / n, 2) if n else None, shown_mean=round(sum(len(a.get("shown") or []) for a in A) / n, 2) if n else None,
                cited_mean=round(sum(len(a.get("cited") or []) for a in A) / n, 2) if n else None, cited_any=sh(sum(bool(a.get("cited")) for a in A)),
                ref_n=len(both), text_differs=sum((t.get("answer") or {}).get("text") != (R[t["itemId"]].get("answer") or {}).get("text") for t in both),
                kept_differs=sum(kl(t) != kl(R[t["itemId"]]) for t in both),
                text_differs_ids=sorted(t["itemId"] for t in both if (t.get("answer") or {}).get("text") != (R[t["itemId"]].get("answer") or {}).get("text")))
jobs = sys.argv[1:] or (json.load(open(N + "/jobs.json"))["order"] + (json.load(open(N + "/jobs-ext.json"))["order"] if os.path.exists(N + "/jobs-ext.json") else []))
os.makedirs(N + "/aggregates", exist_ok=True); md = ["| job | group | n | err | tok p50/p90 | at cap | ms p50 | prompt tok p50 | Not-found | passages-found | health decline | declined | kept | shown | cited>=1 | vs ref: n / text differs / kept differs |", "|---|" * 1 + "---|" * 15]
for j in jobs:
    d = f"{os.environ.get('FETCHED', N + '/fetched')}/{j}"; M = json.load(open(f"{N}/jobs/{j}/job.json"))
    if not os.path.isdir(d + "/out"): md.append(f"| {j} | (not fetched) |" + " |" * 14); continue
    per, allT, allR = {}, [], {}
    for gd in sorted(glob.glob(d + "/out/*/")):
        g = os.path.basename(gd.rstrip("/"))
        if not os.path.exists(gd + "traces.jsonl"): continue
        T = rd(gd + "traces.jsonl"); R = ref_traces(M.get("reference"), g)
        per[g] = stats(T, R); allT += T; allR.update({f"{g}|{k}": v for k, v in R.items()})
        md.append(f"| {j} | {g} | {per[g]['n']} | {per[g]['errors']} | {per[g]['out_tokens_p50']}/{per[g]['out_tokens_p90']} | {per[g]['at_cap_512']} | {per[g]['time_ms_p50']:.0f} | {per[g]['prompt_tokens_p50']} | {per[g]['banner_notfound']} | {per[g]['banner_passages_found']} | {per[g]['health_decline_line']} | {per[g]['declined']} | {per[g]['kept_mean']} | {per[g]['shown_mean']} | {per[g]['cited_any']} | {per[g]['ref_n']} / {per[g]['text_differs']} / {per[g]['kept_differs']} |")
    tot = stats(allT, {})  # pooled (divergence summed from groups)
    tot.update(ref_n=sum(v["ref_n"] for v in per.values()), text_differs=sum(v["text_differs"] for v in per.values()), kept_differs=sum(v["kept_differs"] for v in per.values()),
               text_differs_ids=sorted({i for v in per.values() for i in v["text_differs_ids"]}))
    st = open(d + "/STATUS").read().strip().splitlines()[-1] if os.path.exists(d + "/STATUS") else "?"
    json.dump(dict(job=j, suite=M["suite"], status=st, reference=M.get("reference"), pooled=tot, groups=per), open(f"{N}/aggregates/{j}.json", "w"), indent=1)
    md.append(f"| **{j}** | pooled ({st}) | {tot['n']} | {tot['errors']} | {tot['out_tokens_p50']}/{tot['out_tokens_p90']} | {tot['at_cap_512']} | {tot['time_ms_p50']:.0f} | {tot['prompt_tokens_p50']} | {tot['banner_notfound']} | {tot['banner_passages_found']} | {tot['health_decline_line']} | {tot['declined']} | {tot['kept_mean']} | {tot['shown_mean']} | {tot['cited_any']} | {tot['ref_n']} / {tot['text_differs']} / {tot['kept_differs']} |")
open(N + "/aggregates/NIGHT0.md", "w").write("\n".join(md) + "\n"); print("\n".join(md))
