#!/usr/bin/env python3
"""WARN-TUNE (0 LLM, 0 judge). Criterion: ../WARN-TUNE-criterion.md (sha in ../WARN-TUNE-criterion.sha256).
Reuses tools/warncal_showanyway.py UNCHANGED (sha 8e162cea...): its definition block (before "R = []") and wilson/cboot are exec'd verbatim.
Usage: python3 -I warn_tune.py -> ../WARN-TUNE-2026-10-21.json (+ stdout)."""
import json, glob, hashlib, os, random, re, collections, itertools
HERE = os.path.dirname(os.path.abspath(__file__)); RUL = os.path.dirname(HERE)
WC = f"{HERE}/warncal_showanyway.py"; WSHA = "8e162ceae8fd71919a8f9573ac3813636ca1beca44df51b9632e8ef4ca50cdc7"
src = open(WC).read(); assert hashlib.sha256(src.encode()).hexdigest() == WSHA, "warncal_showanyway.py changed"
CRIT = open(f"{RUL}/WARN-TUNE-criterion.sha256").read().split()[0]
assert hashlib.sha256(open(f"{RUL}/WARN-TUNE-criterion.md", "rb").read()).hexdigest() == CRIT
G = {"__file__": WC, "__name__": "warncal_defs"}
exec(src[:src.index("R = []")], G)
exec(src[src.index("def wilson"):src.index("LPR = [r for r")], G)
row, wilson, cboot, rd, r3, sd = (G[k] for k in ("row", "wilson", "cboot", "rd", "r3", "sd"))
A = G["A"]; LP = G["LP"]; Wl = G["W"]
# ---------------- rows + features ----------------
J0 = G["judg_lp"]("K0"); TR0 = G["traces"](sorted(glob.glob(f"{LP}/traces/lp-K0-*-s42.traces.jsonl")))
R = []; dropped = collections.Counter()
def feats(t, w):
    rc = t["route"]["reasonCodes"]; kept = t["retrieval"]["kept"]; nk = len(kept)
    off = sum(int(c.rsplit("-", 1)[1]) for c in rc if re.match(r"grounding:(health-)?off-topic-dropped-\d+$", c))
    sims = [k["similarity"] for k in kept if k.get("similarity") is not None]
    d = G["done_ev"](t); rem = sum(int(n) for c in rc if c.startswith("citations:removed-") for n in c.split("-", 1)[1].split("-") if n.isdigit())
    tx = t["answer"]["text"]; body = tx[len(Wl):].strip() if w else tx.strip()
    return dict(nkept=nk, onsub=max(0, nk - off), maxcos=max(sims) if sims else 0.0, ncit=len(d.get("cited") or []) + rem, alen=len(body))
for arm in ("K0", "K1", "K3"):
    TR = G["traces"](sorted(glob.glob(f"{LP}/traces/lp-{arm}-*-s42.traces.jsonl"))); Ja = G["judg_lp"](arm)
    for i, t in TR.items():
        if G["setof"](i) is None: continue
        j = J0.get(i) if t["answer"]["text"] == TR0[i]["answer"]["text"] else Ja.get(i)
        if not j: dropped[arm] += 1; continue
        r = row("LP", arm, i, t, j); r.update(feats(t, r["w"])); r["text"] = t["answer"]["text"]; r["corrH"] = r["corr"]; R.append(r)
# ---------------- Opus labels (existing judgments only) ----------------
CO = f"{RUL}/../arms"; OP = {}; ocnt = collections.Counter(); TRC = {}
def trace_text(run, qid):
    if run not in TRC:
        f = f"{LP}/traces/{run}.traces.jsonl" if run.startswith("lp-") else f"{A}/lp-screens/control/traces/{run}.traces.jsonl" if run.startswith("lpctl-") else None
        TRC[run] = {t["itemId"]: t["answer"]["text"] for t in rd(f)} if f and os.path.exists(f) else None
    return (TRC[run] or {}).get(qid)
ofiles = sorted(glob.glob(f"{RUL}/warn-opus/out/*.judgments.jsonl") + glob.glob(f"{RUL}/cv5-per100/out/*.judgments.jsonl") + glob.glob(f"{RUL}/cv5-ladder/out/*.judgments.jsonl")
                + glob.glob(f"{RUL}/gemma-opus-main/out/*.judgments.jsonl") + glob.glob(f"{A}/ce-opus-check/out/*.judgments.jsonl") + glob.glob(f"{A}/refuse-unsupported/ce-opus-ru/out/*.judgments.jsonl"))
by = collections.defaultdict(dict)
for f in ofiles:
    for x in rd(f):
        if not x.get("ok") or "opus" not in (x.get("judgeModel") or ""): continue
        by[(f, x["runId"], x["queryId"])][x["order"]] = x["mapped"]["boar"]["correctness"]
for (f, run, q), v in by.items():
    if len(v) != 2: ocnt["one-order"] += 1; continue
    tx = trace_text(run, q)
    if tx is None: ocnt[f"no-trace:{run.split('-')[0]}"] += 1; continue
    k = (q, tx); c = sum(v.values()) / 2
    if k in OP and OP[k] != c: ocnt["conflict(first kept)"] += 1; continue
    OP.setdefault(k, c); ocnt["units"] += 1
for r in R:
    o = OP.get((r["id"], r["text"])); r["corrO"] = o if o is not None else r["corrH"]; r["hasO"] = o is not None
def relabel(rows, fam):
    out = []
    for r in rows:
        c = r["corrH"] if fam == "H" else r["corrO"]; x = dict(r); x["corr"] = c; x["CE"] = (not r["dec"]) and c <= 1.5; x["correct"] = (not r["dec"]) and c >= 4; out.append(x)
    return out
# ---------------- rule family ----------------
WB = ("W:no-source", "W:all-citations-removed", "W:uncited-with-sources"); UB = ("U:kept-weak", "U:no-kept(banner)", "U:grounded")
GRID = dict(nkept=range(0, 7), onsub=range(0, 5), maxcos=(0.55, 0.60, 0.65, 0.70, 0.75, 0.80), ncit=range(0, 4), alen=(150, 250, 400, 600, 900))
PREDS = [(f, op, t) for f, ts in GRID.items() for t in ts for op in ("<=", ">=")]
def ptest(p, r): f, op, t = p; return r[f] <= t if op == "<=" else r[f] >= t
def subsets(xs): return [s for k in range(1, len(xs) + 1) for s in itertools.combinations(xs, k)]
EOPTS = [None] + [(sw, ps) for sw in subsets(WB) for ps in [()] + [(p,) for p in PREDS] + [(p, q) for p, q in itertools.combinations(PREDS, 2) if p[0] != q[0]]]
AOPTS = [None] + [(su, ps) for su in subsets(UB) for ps in [()] + [(p,) for p in PREDS]]
def npred(e, a): return (len(e[1]) if e else 0) + (len(a[1]) if a else 0)
def e_hit(e, r): return e is not None and r["w"] and r["bucket"] in e[0] and all(ptest(p, r) for p in e[1])
def a_hit(a, r): return a is not None and (not r["w"]) and r["ot"] > 0 and r["bucket"] in a[0] and all(ptest(p, r) for p in a[1])
def flag(rule, r): e, a = rule; return (r["w"] and not e_hit(e, r)) or a_hit(a, r)
def masks(rows):
    m = lambda fn: sum(1 << k for k, r in enumerate(rows) if fn(r))
    pm = {p: m(lambda r, p=p: ptest(p, r)) for p in PREDS}; bm = {b: m(lambda r, b=b: r["bucket"] == b) for b in WB + UB}
    return pm, bm, m(lambda r: r["w"]), m(lambda r: (not r["w"]) and r["ot"] > 0), (1 << len(rows)) - 1
def search(rows_by_fam, keep):
    """rows_by_fam: {fam: non-decline rows (same order)}; keep(stats) -> rank key or None. Returns best list."""
    fams = list(rows_by_fam); base = rows_by_fam[fams[0]]; pm, bm, Wm, Um, ALL = masks(base)
    CE = {f: sum(1 << k for k, r in enumerate(rows_by_fam[f]) if r["CE"]) for f in fams}; tot = {f: bin(CE[f]).count("1") for f in fams}
    emask = {}
    for e in EOPTS:
        if e is None: emask[e] = 0; continue
        x = Wm & sum(bm[b] for b in e[0])
        for p in e[1]: x &= pm[p]
        emask[e] = x
    amask = {}
    for a in AOPTS:
        if a is None: amask[a] = 0; continue
        x = Um & sum(bm[b] for b in a[0])
        for p in a[1]: x &= pm[p]
        amask[a] = x
    best = []
    for e, em in emask.items():
        ne = len(e[1]) if e else 0; fw = Wm & ~em
        for a, am in amask.items():
            na = len(a[1]) if a else 0
            if ne + na > 3: continue
            fl = fw | am; n = bin(fl).count("1")
            st = {f: (bin(fl & CE[f]).count("1"), n, tot[f]) for f in fams}
            key = keep(st, ne + na)
            if key is not None: best.append((key, (e, a), st))
    best.sort(key=lambda x: x[0]); return best
def stats(rows, fl):
    a = [r for r in rows if not r["dec"]]; f = [r for r in a if fl(r)]; u = [r for r in a if not fl(r)]
    ce = sum(r["CE"] for r in a); cf = sum(r["CE"] for r in f); kf = sum(r["correct"] for r in f); ku = sum(r["correct"] for r in u)
    return dict(n=len(a), flagged=len(f), ce=ce, ce_f=cf, precision=sd(cf, len(f)), recall=sd(cf, ce), p_corr_f=sd(kf, len(f)), p_corr_u=sd(ku, len(u)),
                p_ce_u=sd(ce - cf, len(u)), correct_f=kf, correct_u=ku)
def full(rows, fl, boot=False):
    s = stats(rows, fl); o = {k: r3(v) for k, v in s.items()}
    o["wilson"] = dict(precision=wilson(s["ce_f"], s["flagged"]), recall=wilson(s["ce_f"], s["ce"]), p_corr_f=wilson(s["correct_f"], s["flagged"]))
    if boot: o["cluster_ci"] = {k: cboot(rows, lambda x, k=k: stats(x, fl)[k]) for k in ("precision", "recall", "p_corr_f", "p_corr_u")}
    return o
def pdelta(rows, fa, fb, B=2000, seed=11):
    byi = collections.defaultdict(list)
    for r in rows: byi[r["id"]].append(r)
    ids = sorted(byi); rnd = random.Random(seed); xs = collections.defaultdict(list)
    for _ in range(B):
        s = [x for _ in ids for x in byi[ids[rnd.randrange(len(ids))]]]; a = stats(s, fa); b = stats(s, fb)
        for k in ("precision", "recall", "p_corr_f"):
            if a[k] is not None and b[k] is not None: xs[k].append(b[k] - a[k])
    return {k: [round(sorted(v)[int(0.025 * len(v))], 3), round(sorted(v)[int(0.975 * len(v)) - 1], 3)] for k, v in xs.items()}
def desc(rule):
    e, a = rule; P = lambda ps: " AND ".join(f"{f} {op} {t}" for f, op, t in ps)
    s = []
    s.append("keep the line, except " + ("nothing" if e is None else f"{'/'.join(e[0])}" + (f" with {P(e[1])}" if e[1] else " (whole bucket)")) + " -> unwarned")
    s.append("add the line to " + ("nothing" if a is None else f"{'/'.join(a[0])}" + (f" with {P(a[1])}" if a[1] else " (whole bucket)")))
    return "; ".join(s)
# ---------------- per-100 (hon67.py per100 formula, copied unchanged) ----------------
def per100(rows, mode, hid):
    n = len(rows); sh = [r for r in rows if not r["dec"]] if mode == "show" else [r for r in rows if not hid(r)]
    k = sum(r["correct"] for r in sh); ce = sum(r["CE"] for r in sh); sref = sum(r["sref"] for r in rows) or 1; fref = sum(r["sref"] - 1 for r in rows) or 1
    return dict(n=n, correct=100 * k / n, ce=100 * ce / n, partial=100 * (len(sh) - k - ce) / n, hidden=100 * (n - len(sh)) / n,
                U=sum(r["s"] for r in sh) / sref, U_fa=sum(r["s"] - 1 for r in sh) / fref)
def p100(rows, fl):
    hid = lambda r: r["dec"] or fl(r) or (r["ot"] > 0 and r["kept"] == 0); return per100(rows, "refuse", hid)
def p100d(rows, fa, fb, B=2000, seed=11):
    byi = collections.defaultdict(list)
    for r in rows: byi[r["id"]].append(r)
    ids = sorted(byi); rnd = random.Random(seed); xs = collections.defaultdict(list)
    for _ in range(B):
        s = [x for _ in ids for x in byi[ids[rnd.randrange(len(ids))]]]; a = p100(s, fa); b = p100(s, fb)
        for k in ("correct", "ce", "partial", "hidden", "U_fa"): xs[k].append(b[k] - a[k])
    return {k: [round(sorted(v)[int(0.025 * B)], 3), round(sorted(v)[int(0.975 * B) - 1], 3)] for k, v in xs.items()}
# ---------------- run ----------------
out = {"criterion_sha256": CRIT, "rows": len(R), "dropped": dict(dropped), "opus_label_build": dict(ocnt), "opus_files": len(ofiles)}
FIT = [r for r in R if r["set"] != "MAIN"]; EV = [r for r in R if r["set"] == "MAIN"]
fitN = [r for r in FIT if not r["dec"]]
def fitkey(st, np):
    tp, n, tot = st["H"]
    if n < 30 or tp / tot < 0.60: return None
    return (-tp / n, np, -tp / tot)
fit = search({"H": fitN}, fitkey)
SEL = fit[0][1]; base = lambda r: r["w"]; sel = lambda r: flag(SEL, r)
out["n_rules"] = dict(E=len(EOPTS), A=len(AOPTS))
out["SEL"] = dict(rule=desc(SEL), raw=repr(SEL), fit_precision=r3(fit[0][2]["H"][0] / fit[0][2]["H"][1]), fit_recall=r3(fit[0][2]["H"][0] / fit[0][2]["H"][2]), fit_flagged=fit[0][2]["H"][1])
EVH = relabel(EV, "H"); EVO = relabel(EV, "O"); FITH = relabel(FIT, "H")
ev = {}
for nm, rows in (("H", EVH), ("O", EVO)):
    ev[nm] = dict(before=full(rows, base, boot=True), after=full(rows, sel, boot=True), paired_delta=pdelta(rows, base, sel),
                  per100_refuse=dict(before={k: r3(v) for k, v in p100(rows, base).items()}, after={k: r3(v) for k, v in p100(rows, sel).items()}, delta_ci=p100d(rows, base, sel)),
                  by_arm={a: dict(before=full([r for r in rows if r["arm"] == a], base), after=full([r for r in rows if r["arm"] == a], sel)) for a in ("K0", "K1", "K3")})
oo = [r for r in EV if r["hasO"]]
ev["O_only"] = dict(n_rows=len(oo), n_nondecline=sum(not r["dec"] for r in oo), before=full(relabel(oo, "O"), base), after=full(relabel(oo, "O"), sel),
                    haiku_same_rows_before=full(relabel(oo, "H"), base), haiku_same_rows_after=full(relabel(oo, "H"), sel))
evn = [r for r in EV if not r["dec"]]
ev["opus_coverage"] = dict(eval_nondecline=f"{sum(r['hasO'] for r in evn)}/{len(evn)}", warned=f"{sum(r['hasO'] for r in evn if r['w'])}/{sum(r['w'] for r in evn)}",
                           flagged_after=f"{sum(r['hasO'] for r in evn if sel(r))}/{sum(sel(r) for r in evn)}",
                           changed=f"{sum(r['hasO'] for r in evn if sel(r) != r['w'])}/{sum(sel(r) != r['w'] for r in evn)}")
out["EVAL_MAIN"] = ev
out["FIT_180"] = dict(before=full(FITH, base, boot=True), after=full(FITH, sel, boot=True),
                      by_set={s: dict(before=full([r for r in FITH if r["set"] == s], base), after=full([r for r in FITH if r["set"] == s], sel)) for s in ("ST-cand", "ST-SE")})
# changed rows on MAIN
ch = [r for r in EV if not r["dec"] and sel(r) != r["w"]]
out["changed_MAIN"] = dict(unwarned_now=sum(r["w"] for r in ch), warned_now=sum(not r["w"] for r in ch),
                           rows=[dict(arm=r["arm"], id=r["id"], bucket=r["bucket"], to="warned" if sel(r) else "unwarned", corrH=r["corrH"], corrO=r["corrO"] if r["hasO"] else None,
                                      **{k: (r3(r[k]) if k == "maxcos" else r[k]) for k in GRID}) for r in ch])
# top-10 FIT rules on EVAL (sensitivity)
out["fit_top10_on_MAIN"] = []
for key, rule, st in fit[:10]:
    fl = lambda r, rule=rule: flag(rule, r); h = stats(EVH, fl); o = stats(EVO, fl)
    out["fit_top10_on_MAIN"].append(dict(rule=desc(rule), fit_p=r3(st["H"][0] / st["H"][1]), fit_r=r3(st["H"][0] / st["H"][2]), H_p=r3(h["precision"]), H_r=r3(h["recall"]), O_p=r3(o["precision"]), O_r=r3(o["recall"])))
# oracle on MAIN (both families, same rule)
EVHn = [r for r in EVH if not r["dec"]]; EVOn = [r for r in EVO if not r["dec"]]
def orkey(st, np):
    (th, n, toth), (to, _, toto) = st["H"], st["O"]
    if n == 0: return None
    ok = th / n >= 0.55 and th / toth >= 0.60 and to / n >= 0.55 and to / toto >= 0.60
    return (0 if ok else 1, -min(th / n, to / n) if min(th / toth, to / toto) >= 0.60 else 9, np)
orc = search({"H": EVHn, "O": EVOn}, orkey)
def ostat(x):
    (th, n, toth), (to, _, toto) = x[2]["H"], x[2]["O"]; return dict(rule=desc(x[1]), flagged=n, H_p=r3(th / n), H_r=r3(th / toth), O_p=r3(to / n), O_r=r3(to / toto))
out["oracle_MAIN"] = dict(any_reaches=orc[0][0][0] == 0, n_reaching=sum(1 for x in orc if x[0][0] == 0), best=ostat(orc[0]), top5=[ostat(x) for x in orc[:5]])
# Haiku-only oracle (info)
hk = search({"H": EVHn}, lambda st, np: None if st["H"][1] == 0 or st["H"][0] / st["H"][2] < 0.60 else (-st["H"][0] / st["H"][1], np))
out["oracle_MAIN_haiku_only_best"] = dict(rule=desc(hk[0][1]), precision=r3(hk[0][2]["H"][0] / hk[0][2]["H"][1]), recall=r3(hk[0][2]["H"][0] / hk[0][2]["H"][2]), flagged=hk[0][2]["H"][1])
# feature table by bucket on MAIN (CE rates by feature bins) for the report
fb = {}
for b in WB + UB:
    rs = [r for r in EVH if not r["dec"] and r["bucket"] == b]
    for f, cuts in (("onsub", (0, 1, 2)), ("ncit", (0, 1)), ("maxcos", (0.0, 0.70))):
        for c in cuts:
            sub = [r for r in rs if r[f] <= c]; sub2 = [r for r in rs if r[f] > c]
            fb[f"{b}|{f}<={c}"] = dict(n=len(sub), ce=sum(r["CE"] for r in sub), p_ce=r3(sd(sum(r["CE"] for r in sub), len(sub))))
            fb[f"{b}|{f}>{c}"] = dict(n=len(sub2), ce=sum(r["CE"] for r in sub2), p_ce=r3(sd(sum(r["CE"] for r in sub2), len(sub2))))
out["MAIN_bucket_feature_ce"] = fb
pH, pO = ev["H"]["after"], ev["O"]["after"]
passed = all(x["precision"] >= 0.55 and x["recall"] >= 0.60 for x in (pH, pO))
out["verdict"] = "PASS" if passed else ("KILL" if not out["oracle_MAIN"]["any_reaches"] else "INDETERMINATE")
out["script"] = "ruler/tools/warn_tune.py"; out["script_sha256"] = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
s = json.dumps(out, indent=1, ensure_ascii=False, default=str); open(f"{RUL}/WARN-TUNE-2026-10-21.json", "w").write(s)
print("json sha256", hashlib.sha256(s.encode()).hexdigest())
print(json.dumps({k: out[k] for k in ("rows", "dropped", "opus_label_build", "SEL", "verdict", "oracle_MAIN", "oracle_MAIN_haiku_only_best")}, indent=0, default=str))
for nm in ("H", "O"): print(nm, {k: ev[nm][k] for k in ("before", "after")}, ev[nm]["per100_refuse"])
print(ev["opus_coverage"])
