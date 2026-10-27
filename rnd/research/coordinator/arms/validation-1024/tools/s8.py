#!/usr/bin/env python3
"""S8 cost (0 LLM): bytes/q (W78 accounting: stage-1 denselog scanBytes + F1 f1log scanBytes over retrieving items), retrieval ms p50/p95 (wallMs, retrieving items,
quiet runs QSEFIX/QSEFIX2 vs QRC/QRC2 at load < 5), context tokens p50 (retbench rule), pack sizes. python3 -I s8.py -> aggregates/S8.json"""
import json, os, math, statistics as st
VD = "<workspace>/rnd/research/coordinator/arms/validation-1024"; R = VD + "/replays/"
jl = lambda p: [json.loads(l) for l in open(p) if l.strip()]
kid = lambda r: [c["chunkId"] for c in r.get("keptFull") or []]
def pct(v, q): v = sorted(v); return v[min(len(v) - 1, max(0, math.ceil(q * len(v)) - 1))]
def run(n):
    rows = jl(R + n + "/main.jsonl"); nret = json.loads(open(R + n + "/main.err").read().strip().splitlines()[-1])["retrieved"]
    dl = jl(R + n + "/main.denselog"); f1 = jl(R + n + "/main.f1log")
    w = [r["wallMs"] for r in rows if r.get("raw")]
    tok = [sum(math.ceil(len(c.get("title", "") + c.get("body", "")) / 4) for c in r["keptFull"]) for r in rows if r.get("keptFull")]
    load = [l for l in open(R + n + "/runs.log")][-1].split("load0=")[1].split()[0]
    return dict(retrieving=nret, dense_bytes_q=round(sum(x["scanBytes"] for x in dl) / nret), f1_bytes_q=round(sum(x["scanBytes"] for x in f1) / nret),
                kit_bytes_q=round((sum(x["scanBytes"] for x in dl) + sum(x["scanBytes"] for x in f1)) / nret), stage1_scan_ms_q=round(sum(x["scanMs"] for x in dl) / nret, 1),
                wall_ms_p50=round(st.median(w), 1), wall_ms_p95=round(pct(w, 0.95), 1), ctx_tok_p50=st.median(tok), load_at_start=load, kept={r["id"]: kid(r) for r in rows})
o = {n: run(n) for n in ("A0off", "RC", "QSEFIX", "QSEFIX2", "QRC", "QRC2")}
o["identity_QRC_vs_RC"] = sum(o["QRC"]["kept"][i] == o["RC"]["kept"][i] for i in o["RC"]["kept"]); o["identity_QSEFIX_vs_A0off"] = sum(o["QSEFIX"]["kept"][i] == o["A0off"]["kept"][i] for i in o["A0off"]["kept"])
for n in ("A0off", "RC", "QSEFIX", "QSEFIX2", "QRC", "QRC2"): o[n].pop("kept")
sz = [l.split() for l in open(VD + "/build/packs.sha256")]; rc = sum(int(x[1]) for x in sz[:13])
v1 = {x[2]: int(x[1]) for x in sz}; sef = rc - v1["kiln-local/w78pf-packs/boar-simplewiki-en.sqlite"] - v1["kiln-local/w78pf-packs/qa-travel-se.sqlite"] - v1["kiln-local/shape-packs/shaped/boar-factbook.sqlite"] \
    + v1["shared-data/packs/v3proto/boar-simplewiki-en.sqlite"] + v1["shared-data/packs/v3proto/qa-travel-se.sqlite"] + v1["shared-data/packs/v3proto/boar-factbook.sqlite"]
o["kit_disk_bytes"] = dict(RC=rc, SEFIX124=sef, x=round(rc / sef, 4), per_pack={x[2]: int(x[1]) for x in sz[:13]})
o["ctx_p50_x"] = round(o["RC"]["ctx_tok_p50"] / o["A0off"]["ctx_tok_p50"], 3)
o["ms_quiet"] = dict(SEFIX124=[o["QSEFIX"]["wall_ms_p50"], o["QSEFIX"]["wall_ms_p95"], o["QSEFIX2"]["wall_ms_p50"], o["QSEFIX2"]["wall_ms_p95"]],
                     RC=[o["QRC"]["wall_ms_p50"], o["QRC"]["wall_ms_p95"], o["QRC2"]["wall_ms_p50"], o["QRC2"]["wall_ms_p95"]], note="p50, p95 per run; two runs each, alternated, load at start < 5")
o["pass"] = o["RC"]["kit_bytes_q"] <= 25_000_000 and o["ctx_p50_x"] <= 1.15
json.dump(o, open(VD + "/aggregates/S8.json", "w"), indent=1); print(json.dumps(o, indent=1))
