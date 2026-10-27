#!/usr/bin/env python3
"""FOTAPOL extra metrics (0 LLM). Usage: python3 -I extra_metrics.py <ids file> <candidate traces.jsonl> <control traces.jsonl> [<control traces.jsonl> ...]
Per arm on the ids: live = outputTokens > 0; decline / warned via null-cal/tools/labels.py rules (text only, plus trace answer.declined);
citation compliance = share of live, non-decline, non-warned answers with an engine-format [n] marker; [Source n] marker count;
output tokens mean (live); wall = timing.totalMs sum and p50 (all ids); prefill p50; decode tok/s p50 (live)."""
import json, re, sys, os, statistics as st
sys.path.insert(0, "<workspace>/rnd/research/coordinator/arms/null-cal/tools"); from labels import is_decline, W
ids = [x for x in open(sys.argv[1]).read().split() if x]
def load(paths):
    d = {}
    for p in paths:
        for l in open(p):
            r = json.loads(l); d[r["itemId"]] = r
    return d
C = load([sys.argv[2]]); K = load(sys.argv[3:])
miss = [i for i in ids if i not in C or i not in K]
if miss: sys.exit(f"missing ids: {miss[:5]} ({len(miss)})")
CIT = re.compile(r"\[\d+(?:\s*[,-]\s*\d+)*\]"); SRC = re.compile(r"\[Source\s*\d+", re.I)
def m(D):
    rows = [D[i] for i in ids]; t = lambda r: (r.get("timing") or {})
    live = [r for r in rows if (t(r).get("outputTokens") or 0) > 0]
    txt = lambda r: (r.get("answer") or {}).get("text") or ""
    shown = [r for r in live if not is_decline(txt(r), (r.get("answer") or {}).get("declined")) and not txt(r).startswith(W)]
    dec = sum(is_decline(txt(r), (r.get("answer") or {}).get("declined")) for r in rows); warn = sum(txt(r).startswith(W) for r in rows)
    tot = [t(r).get("totalMs") or 0 for r in rows]; pre = [t(r).get("prefillMs") for r in live if t(r).get("prefillMs") is not None]
    dtps = [t(r).get("decodeTokPerSec") for r in live if t(r).get("decodeTokPerSec")]
    return dict(n=len(rows), live=len(live), declines=dec, warned=warn, shown_live=len(shown),
                cited=sum(bool(CIT.search(txt(r))) for r in shown), cite_rate=round(sum(bool(CIT.search(txt(r))) for r in shown) / max(1, len(shown)), 3),
                source_tag=sum(bool(SRC.search(txt(r))) for r in rows), out_tok_mean=round(st.mean([t(r)["outputTokens"] for r in live]), 1) if live else 0,
                wall_sum_s=round(sum(tot) / 1000, 1), wall_p50_s=round(st.median(tot) / 1000, 2), prefill_p50_ms=round(st.median(pre)) if pre else None,
                decode_tps_p50=round(st.median(dtps), 1) if dtps else None, errors=sum(1 for r in rows if r.get("error")))
mc, mk = m(C), m(K)
print(json.dumps({"candidate": mc, "control": mk}, indent=1))
