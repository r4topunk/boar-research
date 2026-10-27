"""LITEPROFILE identity (0 LLM): every lite flag off, liteprofile tree vs pristine wt/pr1, per set (probes 64, v01 60, st 180) and
HEALTHGAP on/off: whole trace identical after dropping run/time fields (warnspec/tools/compare_warn.py norm()). Also vs the
warnspec pr1 traces of 10-16 02:38 (HG=1) as a drift check. Usage: python3 -I compare_lp.py <out.json>"""
import json, sys, copy
L = "<workspace>/rnd/research/coordinator/arms/liteprofile/runs"; W = "<workspace>/rnd/research/coordinator/arms/warnspec/runs"
def jl(p): return {t["itemId"]: t for t in (json.loads(l) for l in open(p) if l.strip())}
def norm(t):
    t = copy.deepcopy(t)
    for k in ("runId", "createdAt", "timing", "resources", "config", "engine", "runtime"): t.pop(k, None)
    t["events"] = [{k: v for k, v in e.items() if k not in ("tMs", "at", "ms")} for e in t["events"]]
    for e in t["events"]:
        if e.get("type") == "done" and isinstance(e.get("receipt"), dict):
            for k in ("ttftMs", "totalMs", "retrievalMs", "loadMs", "prefillMs", "tokPerSec"): e["receipt"].pop(k, None)
    return t
def cmp(a, b):
    A, B = jl(a), jl(b); assert A.keys() == B.keys(), (a, b)
    bad = [i for i in A if json.dumps(norm(A[i]), sort_keys=True) != json.dumps(norm(B[i]), sort_keys=True)]
    return {"n": len(A), "identical": len(A) - len(bad), "diff": bad}
out = {}
for s in ("probes", "v01", "st"):
    for hg in ("1", "0"):
        out[f"{s}-hg{hg}-lp-vs-pr1"] = cmp(f"{L}/lp-{s}-hg{hg}-lp.traces.jsonl", f"{L}/lp-{s}-hg{hg}-pr1.traces.jsonl")
    out[f"{s}-hg1-pr1-vs-warnspec-pr1"] = cmp(f"{L}/lp-{s}-hg1-pr1.traces.jsonl", f"{W}/warn-{s}-pr1.traces.jsonl")
    lp = jl(f"{L}/lp-{s}-hg1-lp.traces.jsonl").values()
    codes = [c for t in lp for c in t["route"]["reasonCodes"]]
    out[f"{s}-lite-codes-off"] = sorted({c for c in codes if c.startswith(("warn:", "sources:grouped", "headpass:"))})
json.dump(out, open(sys.argv[1], "w"), indent=1)
for k, v in out.items(): print(k, v if isinstance(v, list) else f"{v['identical']}/{v['n']} diff={v['diff'][:8]}")
