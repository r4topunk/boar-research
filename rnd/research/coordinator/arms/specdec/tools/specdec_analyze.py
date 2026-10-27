#!/usr/bin/env python3
"""SPECDEC analysis: acceptance, accepted/pass, identity vs non-spec, tok/s, RSS, A15 projection (criterion formula) and gates.
usage: specdec_analyze.py RESDIR   (RESDIR = fetched <runner>/kiln/specdec/res; reads summary.jsonl + <name>.jsonl)"""
import json, sys, os, statistics as st, collections
sys.path.insert(0, "<workspace>/rnd/research/coordinator/device/tools")
R = sys.argv[1]
summ = {}
for l in open(f"{R}/summary.jsonl"):
    x = json.loads(l); summ[x["name"]] = x
def load(n): return {r["itemId"]: r for r in map(json.loads, open(f"{R}/{n}.jsonl"))}
runs = {n: load(n) for n in summ if summ[n].get("ok")}
GiB = 1024 ** 3
# ---- c: draft/target per-token cost ratio = weight bytes read per token (A15 decode is memory-bandwidth bound) ----
TGT_B = 2497281120
DRAFT_B = {"q06": 639446688, "q15": 986048768}
C = {k: v / TGT_B for k, v in DRAFT_B.items()}
# ---- draft KV (llama.cpp: draft ctx n_ctx = target n_ctx; engine n_ctx 4096 on >6.5 GB phones, 3072 on <=6.5, 2048 on <=4.5) ----
KV_PER_TOK = {"q06": 28 * 2 * 8 * 128 * 2, "q15": 28 * 2 * 2 * 128 * 2}  # layers * K,V * kv_heads * head_dim * 2 B (f16)
def added_gib(d, nctx=4096, kvq=1.0): return (DRAFT_B[d] + KV_PER_TOK[d] * nctx * kvq) / GiB

def stats(name, base_name, ident_base_name=None):
    r = runs[name]; b = runs[base_name]
    items = sorted(r)
    ident = sum(r[i]["text"] == b[i]["text"] for i in items)
    n = sum(r[i]["predicted_n"] or 0 for i in items)
    dn = sum(r[i]["draft_n"] or 0 for i in items); da = sum(r[i]["draft_n_accepted"] or 0 for i in items)
    passes = n - da  # each target pass yields accepted+1 tokens
    tok_s = sum(r[i]["predicted_n"] for i in items) / (sum(r[i]["predicted_ms"] for i in items) / 1000)
    return dict(ident=ident, n=len(items), tokens=n, drafted=dn, accepted=da, passes=passes,
                acc_rate=da / dn if dn else None, acc_per_pass=da / passes if passes else None, drafted_per_pass=dn / passes if passes else None,
                tok_s=tok_s, per_item_acc=[(r[i]["draft_n_accepted"] or 0) / max(1, (r[i]["predicted_n"] or 0) - (r[i]["draft_n_accepted"] or 0)) for i in items], items=items)

def speedup(acc, nmax, c): return (acc + 1) / (1 + nmax * c)

if __name__ == "__main__":
    out = {"c": C, "added_gib_4096_f16": {d: added_gib(d) for d in C}, "added_gib_3072_f16": {d: added_gib(d, 3072) for d in C},
           "added_gib_4096_q8kv": {d: added_gib(d, 4096, 17 / 32) for d in C}, "runs": {}}
    for n, s in summ.items():
        if not s.get("ok"): out["runs"][n] = s; continue
        if s["draft"] == "none":
            tot = sum(r["predicted_n"] for r in runs[n].values()); ms = sum(r["predicted_ms"] for r in runs[n].values())
            out["runs"][n] = dict(cfg=s, tok_s=tot / (ms / 1000), tokens=tot, idle_rss=s["idle_rss_mb"], peak_rss=s["peak_rss_mb"]); continue
        base = "baseg" if s["mode"] == "greedy" else "base1"
        if base not in runs: continue
        if not any(r["draft_n"] for r in runs[n].values()):  # server started but refused speculation (vocab check): run == non-speculative
            out["runs"][n] = dict(cfg=s, refused=True, note="llama-server logged 'draft vocabs not compatible', ran WITHOUT speculation"); continue
        d = stats(n, base); d["cfg"] = s; d.pop("items")
        d["rss_added_idle_mb"] = s["idle_rss_mb"] - summ[base]["idle_rss_mb"]; d["rss_added_peak_mb"] = s["peak_rss_mb"] - summ[base]["peak_rss_mb"]
        c0 = C[s["draft"]]
        d["speedup"] = {lab: speedup(d["acc_per_pass"], s["nmax"], c0 * f) for lab, f in (("c-50%", .5), ("c", 1.0), ("c+50%", 1.5))}
        d["speedup_pass_pooled_drafted"] = {lab: speedup(d["acc_per_pass"], d["drafted_per_pass"], c0 * f) for lab, f in (("c-50%", .5), ("c", 1.0), ("c+50%", 1.5))}
        out["runs"][n] = d
    # control-vs-control identity
    if "base2" in runs and "base1" in runs:
        out["control_vs_control"] = sum(runs["base1"][i]["text"] == runs["base2"][i]["text"] for i in runs["base1"])
    json.dump(out, open(f"{R}/analysis.json", "w"), indent=1, default=lambda x: round(x, 4))
    print(json.dumps(out, indent=1, default=lambda x: round(x, 4))[:6000])
