#!/usr/bin/env python3
"""SMALLROUTE S0 (0 calls). Criterion sha a2fa9572... Reads arms/ aggregates + public self-test judgments/traces only; v0.2: lossmap aggregates (id + numeric scores)."""
import json, collections, statistics as st, csv, os, datetime
import numpy as np
A = "<workspace>/rnd/research/coordinator/arms"; O = f"{A}/smallroute"
K3 = ("correctness", "completeness", "usefulness")
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se", "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
def jr(p):  # per-item ratio = sum(boar)/sum(ref) over 3 dims x both orders (LITE6/LITE3 estimator)
    J = collections.defaultdict(dict)
    for l in open(p):
        r = json.loads(l)
        if r.get("ok"): J[r["queryId"]][r["order"]] = r["mapped"]
    out = {}
    for q, v in J.items():
        if set(v) == {"boarA", "boarB"}:
            out[q] = sum(v[o]["boar"][k] for o in v for k in K3) / sum(v[o]["ref"][k] for o in v for k in K3)
    return out
rd = lambda f: {(t := json.loads(l))["itemId"]: t for l in open(f) if l.strip()}
def boot_ci(x, B=2000, seed=1):
    rng = np.random.default_rng(seed); x = np.asarray(x); n = len(x)
    m = np.array([x[rng.integers(0, n, n)].mean() for _ in range(B)]); return np.percentile(m, [2.5, 97.5])
# ---------- stage 1: lite ----------
arm, ctl, tr = {}, {}, {}
for p in PACKS:
    arm.update(jr(f"{A}/lite5/runs/180/lite5-180-on-{p}-s42.judgments.haiku55-low.jsonl"))
    ctl.update(jr(f"{A}/headpass-st/gen-x2b/st-{p}-cut7-headpassx2b-s42.judgments.jsonl"))
    tr.update(rd(f"{A}/headpass-st/gen-x2b/st-{p}-cut7-headpassx2b-s42.traces.jsonl"))
ids = sorted(arm); assert len(ids) == 180 and set(ids) == set(ctl) == set(tr)
FIC = json.load(open(f"{A}/lite5/aggregates/fic-180.json")); L6 = json.load(open(f"{A}/lite6/aggregates/lite6.json"))
bucket = {i: "tie" for i in ids}
for b, v in L6["below"]["table"].items():
    for i in v["ids"]: bucket[i] = "below:" + b
for b, v in L6["above"]["table"].items():
    for i in v["ids"]: bucket[i] = "above:" + b
codes = lambda t: (t.get("route") or {}).get("reasonCodes") or []
rows = []
for i in ids:
    t = tr[i]; c = codes(t)
    rows.append(dict(route="lite", item_id=i, ctl=ctl[i], arm=arm[i], delta=arm[i] - ctl[i], fic=int(FIC[i]["on"]),
        kept_n=len((t.get("retrieval") or {}).get("kept") or []), r2=int(any(x in ("grounding:no-good-source", "grounding:no-source-memory") for x in c)),
        hp=int(any(x.startswith(("headpass:add:", "headpass:dense:add:")) for x in c)), bucket=bucket[i]))
d = np.array([r["delta"] for r in rows]); C = np.array([r["ctl"] for r in rows]); Aa = np.array([r["arm"] for r in rows])
orc = np.maximum(C, Aa); for_r = lambda r: r
LITE = dict(n=180, ctl=C.mean(), arm=Aa.mean(), oracle=orc.mean(), ceiling=orc.mean() - C.mean(), n_win=int((d > 0).sum()), n_tie=int((np.abs(d) <= 0.02).sum()),
            n_lose=int((d < -0.02).sum()), n_strict_win=int((d > 0.02).sum()), target=int((d >= -0.02).sum()))
TGT = d >= -0.02
def sig_eval(mask, base=C, alt=Aa):
    mask = np.asarray(mask, bool); n = mask.sum(); tp = (mask & TGT).sum()
    prec = tp / n if n else float("nan"); rec = tp / TGT.sum()
    hyb = np.where(mask, alt, base); dd = hyb - base; lo, hi = boot_ci(dd)
    return dict(routed=int(n), share=n / len(mask), prec=prec, rec=rec, hyb=hyb.mean(), d=dd.mean(), lo=lo, hi=hi)
S = collections.OrderedDict()
col = lambda k: np.array([r[k] for r in rows])
S["fic=1"] = col("fic") == 1; S["fic=0"] = col("fic") == 0
for t in (0, 1, 2, 3, 4): S[f"kept_n<={t}"] = col("kept_n") <= t
for t in (1, 2, 3, 4): S[f"kept_n>={t}"] = col("kept_n") >= t
S["hp fired=1"] = col("hp") == 1; S["hp fired=0"] = col("hp") == 0
S["R2 code=1"] = col("r2") == 1; S["R2 code=0"] = col("r2") == 0
S["fic=1 & kept>=2"] = (col("fic") == 1) & (col("kept_n") >= 2)
S["LITE6 bucket thin (outcome-derived, leaky)"] = np.array([r["bucket"] == "below:thin" for r in rows])
S["LITE6 not below (outcome-derived, leaky)"] = np.array([not r["bucket"].startswith("below:") for r in rows])
LS = {k: sig_eval(m) for k, m in S.items()}
# ---------- stage 2: deep (v0.2, lossmap rows: K = cut6 s42 Opus, H = deep + think 512 s42 Opus) ----------
Kj = {i["id"]: i for i in json.load(open(f"{A}/lossmap/aggregates/lossmap-K-v02-s42.json"))["items"]}
Hj = {i["id"]: i for i in json.load(open(f"{A}/lossmap/aggregates/lossmap-H-v02-s42.json"))["items"]}
dids = sorted(Kj); assert len(dids) == 110 and set(dids) == set(Hj)
dc = np.array([Kj[i]["ratio"] for i in dids]); da = np.array([Hj[i]["ratio"] for i in dids]); dd = da - dc
DEEP = dict(n=110, ctl=dc.mean(), arm=da.mean(), oracle=np.maximum(dc, da).mean(), ceiling=np.maximum(dc, da).mean() - dc.mean(), gain=dd.mean(),
            n_win=int((dd > 0).sum()), n_tie=int((np.abs(dd) <= 0.02).sum()), n_lose=int((dd < -0.02).sum()))
for i in dids:
    rows.append(dict(route="deep", item_id=i, ctl=Kj[i]["ratio"], arm=Hj[i]["ratio"], delta=Hj[i]["ratio"] - Kj[i]["ratio"], fic="", kept_n=Kj[i]["n_kept"], r2="",
                     hp="", bucket=Kj[i]["path"] + "|" + ("ontopic" if Kj[i]["labels"]["source_on_topic"] else "offtopic")))
dk = np.array([Kj[i]["n_kept"] for i in dids]); dsot = np.array([Kj[i]["labels"]["source_on_topic"] for i in dids]); dpath = np.array([Kj[i]["path"] for i in dids])
def deep_eval(mask):  # route to deep; capture = hybrid gain / all-deep gain
    mask = np.asarray(mask, bool); hyb = np.where(mask, da, dc); x = hyb - dc; lo, hi = boot_ci(x)
    return dict(routed=int(mask.sum()), share=mask.mean(), hyb=hyb.mean(), d=x.mean(), lo=lo, hi=hi, cap=x.mean() / dd.mean())
DS = collections.OrderedDict()
DS["oracle (per-item best)"] = dd > 0
for t in (0, 1, 2): DS[f"kept_n<={t}"] = dk <= t
DS["source_on_topic=False (post-gen jev label; proxy for R2)"] = ~dsot
DS["kept_n==0 & off-topic"] = (dk == 0) & ~dsot
DS["path=health-strict"] = dpath == "health-strict"
rng = np.random.default_rng(1); DS["random 30% (mean of 2000)"] = None
DR = {k: deep_eval(m) for k, m in DS.items() if m is not None}
rs = [deep_eval(rng.permutation(np.arange(110) < 33))["cap"] for _ in range(300)]; DR["random 30% (300 draws)"] = dict(routed=33, share=.3, cap=float(np.mean(rs)), d=float(np.mean(rs)) * dd.mean(), hyb=float("nan"), lo=float("nan"), hi=float("nan"))
# ---------- verdict ----------
lite_ok = [(k, v) for k, v in LS.items() if "leaky" not in k and v["prec"] >= .70 and v["rec"] >= .40]
deep_ok = [(k, v) for k, v in DR.items() if "oracle" not in k and "random" not in k and v["cap"] >= .70 and v["share"] <= .40]
seen_lite = LITE["ceiling"] >= .03 and bool(lite_ok); seen_deep = DEEP["ceiling"] >= .05 and bool(deep_ok)
verdict = ("SEEN-LITE " if seen_lite else "") + ("SEEN-DEEP" if seen_deep else "")
verdict = verdict.strip() or "NOT SEEN"
# ---------- write ----------
with open(f"{O}/items.csv", "w", newline="") as f:
    w = csv.DictWriter(f, ["route", "item_id", "ctl", "arm", "delta", "oracle", "fic", "kept_n", "r2", "bucket"], extrasaction="ignore"); w.writeheader()
    for r in rows: r["oracle"] = max(r["ctl"], r["arm"]); w.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})
f3 = lambda x: f"{x:.3f}"; pc = lambda x: f"{100*x:.0f}%"
L = [f"# SMALLROUTE S0 (probe, 0 calls) — verdict: **{verdict}**",
     f"criterion sha256 a2fa9572…2158a (verified) · generated {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} · tools/s0.py · items.csv (lite 180 + deep 110 rows)",
     "Files/fields: lite = lite5/runs/180 `*-on-*.judgments.haiku55-low.jsonl` (arm 1.7B+X2b) and headpass-st/gen-x2b `*.judgments.jsonl` (ctl 4B+X2b); per-item ratio = Σboar/Σref over 3 dims × both orders (LITE6 estimator; N=4 shards pooled in the files); fic = fic-180.json `on`; kept_n/R2 code/hp = ctl traces `retrieval.kept`, `route.reasonCodes` (kept identical on ON, gate-180 G1); bucket = lite6.json ids (OUTCOME-derived: only for below/above items, so leaky, shown for completeness).",
     "Deep = lossmap/aggregates/lossmap-{K,H}-v02-s42.json items (id, Opus ratio, n_kept, path, jev label): K = cut6 4B s42, H = deep+think 512 s42. **Deviation:** per-item TV (think 1024) / seed-43 rows and the R2 reason code exist only in blind/ (not opened), so TV 2-seed is aggregate-only and R2 is replaced by n_kept / source_on_topic proxies; the R2 capture on v0.2 is quoted from DEEPROUTE-VPARA addendum (48% at 30% routed, H).",
     "", "## Stage 1: lite route (180 public self-tests; ctl 4B+X2b, arm 1.7B+X2b; target = 1.7B ≥ 4B − 0.02)",
     f"mean 4B {f3(LITE['ctl'])} · 1.7B {f3(LITE['arm'])} · oracle {f3(LITE['oracle'])} · **ceiling {f3(LITE['ceiling'])}** · 1.7B strictly better n_win={LITE['n_win']} (>0.02: {LITE['n_strict_win']}) · n_tie(|Δ|≤0.02)={LITE['n_tie']} · n_lose(<−0.02)={LITE['n_lose']} · target set {LITE['target']}/180 (base rate {pc(LITE['target']/180)})",
     "| route to 1.7B when | routed | share | precision | recall | hybrid | Δ vs 4B (95% CI) |", "|---|---|---|---|---|---|---|"]
for k, v in LS.items(): L.append(f"| {k} | {v['routed']} | {pc(v['share'])} | {f3(v['prec']) if v['routed'] else '-'} | {f3(v['rec'])} | {f3(v['hyb'])} | {v['d']:+.3f} ({v['lo']:+.3f}…{v['hi']:+.3f}) |")
L += ["", "## Stage 2: deep route (v0.2, 110 ids, dev; K = 4B cut6 s42, H = deep+think 512 s42, Opus; one seed)",
      f"mean 4B {f3(DEEP['ctl'])} · deep {f3(DEEP['arm'])} (all-deep gain {DEEP['gain']:+.3f}) · oracle {f3(DEEP['oracle'])} · **ceiling {f3(DEEP['ceiling'])}** · deep better {DEEP['n_win']}, tie(|Δ|≤0.02) {DEEP['n_tie']}, deep worse {DEEP['n_lose']}",
      "| route to deep when | routed | share | hybrid | Δ vs 4B (95% CI) | capture of all-deep gain |", "|---|---|---|---|---|---|"]
for k, v in DR.items(): L.append(f"| {k} | {v['routed']} | {pc(v['share'])} | {f3(v['hyb'])} | {v['d']:+.3f} ({v['lo']:+.3f}…{v['hi']:+.3f}) | {pc(v['cap'])} |")
L += ["", "## Verdict (criterion stage 3)",
      f"- Lite: ceiling {f3(LITE['ceiling'])} (≥0.03: {'yes' if LITE['ceiling']>=.03 else 'no'}); signals meeting precision ≥0.70 & recall ≥0.40 (non-leaky): " + (", ".join(f"{k} (P {f3(v['prec'])}, R {f3(v['rec'])})" for k, v in lite_ok) or "none") + f" → {'SEEN-LITE' if seen_lite else 'not seen'}.",
      f"- Deep: ceiling {f3(DEEP['ceiling'])} (≥0.05: {'yes' if DEEP['ceiling']>=.05 else 'no'}); signals with capture ≥70% at ≤40% routed: " + (", ".join(f"{k} ({pc(v['cap'])} at {pc(v['share'])})" for k, v in deep_ok) or "none") + f" → {'SEEN-DEEP' if seen_deep else 'not seen'}.",
      "- Caveats: oracle ceilings are in-sample upper bounds (judge noise inflates max; SEEDVAR: deep one-seed Δ<0.03 is noise); signal rows were swept over many thresholds (multiplicity); LITE6 rows are outcome-derived and excluded from the verdict; single Haiku pass lite, single Opus seed deep.",
      f"- **{verdict}**"]
open(f"{O}/S0.md", "w").write("\n".join(L) + "\n"); print("\n".join(L)); print(len(L), "lines")
