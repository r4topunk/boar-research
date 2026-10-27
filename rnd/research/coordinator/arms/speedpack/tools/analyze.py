#!/usr/bin/env python3
"""analyze.py <dir> [ctl_prefix arm_prefix]: paired delta (two-level bootstrap, CI90), cw/unsafe/empty/truncated, tokens.
Judgments: <dir>/<prefix>-v01-sNN.judgments.v1-med.jsonl (merged). Safety rules v0.9.1 (as in the KVQ8 report)."""
import json, sys, math, statistics as st
sys.path.insert(0, "<workspace>/boar-eval")
from scorers import score, stats
from scorers.bench import Bench
D = sys.argv[1]; CP, AP = (sys.argv[2], sys.argv[3]) if len(sys.argv) > 3 else ("spctl", "spsp")
SEEDS = ["44", "45"]
bench = Bench("<workspace>/boar-eval/bench/v0.1")
import importlib.util
H = "<workspace>/rnd/research/compass/exp/safety-v091"
_sp = importlib.util.spec_from_file_location("sc091", H + "/safety_check.v0.9.1.py"); _m = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(_m)
S091 = _m.load(rules_path=H + "/rules.v0.9.1.json", overlay_path=H + "/overlay.v0.4.json")
S091["check"] = lambda answer, rule_ids, S_, _c=_m.check: [h for h in _c(answer, rule_ids, S_) if h.get("status") != "review"]
S091["check_all"], S091["rules_for"], S091["dir"] = _m.check, _m.rules_for, H
def ld(p): return {t["itemId"]: t for t in map(json.loads, open(p))}
def run(pref, s):
    tr = f"{D}/{pref}-v01-s{s}.traces.jsonl"; js = f"{D}/{pref}-v01-s{s}.judgments.v1-med.jsonl"
    rep = score.score(tr, bench, js, system=f"{pref}-s{s}", safety=False)
    traces = ld(tr)
    rep["items"] = score.apply_safety(rep["items"], bench, score.answers_from_traces(traces), S091)
    rep["safety"] = score.safety_summary(rep["items"], S091)
    return rep, traces
def trunc(t):
    a = t["answer"]["text"].rstrip()
    if not a: return False
    if a[-1] in '.!?)"': return False
    last = a.split("\n")[-1].strip()
    return not (last[:1] in "-*•" or (last[:1].isdigit() and last[1:3] in (". ", ") ")))
res = {}
for pref in (CP, AP):
    for s in SEEDS:
        rep, traces = run(pref, s)
        items = rep["items"]
        pairs = rep["pairs"]
        cw = sorted(i for i, p in pairs.items() if p["correctness"] <= 1.0)
        gen = [t for t in traces.values() if (t["timing"].get("promptTokens") or 0) > 0]
        res[(pref, s)] = dict(
            rep=rep, traces=traces, cw=cw, unsafe=rep["safety"]["n_unsafe"], unsafe_ids=[x["id"] for x in rep["safety"]["unsafe"]],
            empty=[i for i, t in traces.items() if not t["answer"]["text"].strip()],
            truncated=[i for i, t in traces.items() if t["route"]["tier"] != "instant" and (t["timing"].get("outputTokens") or 0) > 0 and trunc(t)],
            outtok=[(t["timing"].get("outputTokens") or 0) for t in gen], prompt=[t["timing"]["promptTokens"] for t in gen],
            errors=rep["n_errors"], n_pairs=len(pairs), pmap={i: (p["boarMean"], p["refMean"]) for i, p in pairs.items()})
# paired bootstrap with CI90 (same procedure as stats.two_level_diff, percentiles 5/95)
oa, ob = stats._obs([res[(CP, s)]["pmap"] for s in SEEDS]), stats._obs([res[(AP, s)]["pmap"] for s in SEEDS])
items = [i for i in oa if i in ob]
def diff(sub, seed=11, n=2000):
    pa = stats.ratio([stats._item_mean(oa[i]) for i in sub]); pb = stats.ratio([stats._item_mean(ob[i]) for i in sub])
    r = stats.rng(seed); k = len(sub); xs = []
    for _ in range(n):
        na = da = nb = db = 0
        for _ in range(k):
            i = sub[math.floor(r() * k)]
            b1, r1 = stats._draw_runs(r, oa[i]); b2, r2 = stats._draw_runs(r, ob[i])
            na += b1; da += r1; nb += b2; db += r2
        xs.append(nb / db - na / da)
    xs.sort()
    return pa, pb, pb - pa, stats.percentile(xs, 0.05), stats.percentile(xs, 0.95)
print("POOLED (n items %d x 2 seeds): ctl %.4f arm %.4f delta %+.4f CI90 [%+.4f, %+.4f]" % ((len(items),) + diff(items)))
for s in SEEDS:
    a, b = res[(CP, s)]["pmap"], res[(AP, s)]["pmap"]
    oa_, ob_ = oa, ob
    it = [i for i in a if i in b]
    pa = stats.ratio([a[i] for i in it]); pb = stats.ratio([b[i] for i in it])
    print(f"s{s}: ctl {pa:.4f} arm {pb:.4f} delta {pb-pa:+.4f} (n={len(it)})")
for s in SEEDS:
    for pref in (CP, AP):
        r = res[(pref, s)]
        print(f"{pref} s{s}: unsafe {r['unsafe']} {r['unsafe_ids']} | cw {len(r['cw'])} {r['cw']} | empty {len(r['empty'])} | truncated {len(r['truncated'])} {r['truncated']} | errors {r['errors']} | "
              f"gen items {len(r['outtok'])} meanOutTok {st.mean(r['outtok']):.1f} p50 {st.median(r['outtok'])} max {max(r['outtok'])} meanPromptTok {st.mean(r['prompt']):.1f}")
for pref in (CP, AP):
    o = sum((res[(pref, s)]["outtok"] for s in SEEDS), []); p = sum((res[(pref, s)]["prompt"] for s in SEEDS), [])
    print(f"{pref} pooled: n {len(o)} meanOutTok {st.mean(o):.2f} meanPromptTok {st.mean(p):.2f}")
json.dump({f"{k[0]}-s{k[1]}": {kk: v[kk] for kk in ("cw", "unsafe", "empty", "truncated", "outtok", "prompt")} for k, v in res.items()}, open(f"{D}/analysis.json", "w"))
