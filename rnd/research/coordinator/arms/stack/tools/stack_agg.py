#!/usr/bin/env python3
"""STACK-2 analysis (criterion sha e875d463…; 0 LLM). Run: python3 -I stack_agg.py  (after chain.sh + judge_stack.sh).
X = runs/st-<pack>-cut7-stack-s42 (stack tree, all 9 + kit, packGround perpack + packRoute quota); P = arms/crowdq/runs/st-<pack>-cut7-all9-s42;
S = arms/packs/selftest-runs/st-<pack>-cut7-s42. Haiku 5.5-low rows both orders. Estimator = crowdq_agg.py (ratio of sums; per-item bootstrap
B 2000 seed 11 of the paired difference). Reach / attribution = crowdq reach.py logic (exact / path-segment URL match of the item's source.url in a kept source;
owner by URL in the 9 packs' article_meta, else Wikivoyage -> kit:wikivoyage, else kit:other). Precheck: kept (title, section) list or
promptTokens differ vs P. v0.1: ON − OFF paired, OFF identity = OFF trace kept (title, section) lists vs the kit-only step-0 replay OFF.
Writes aggregates/stack.json."""
import json, os, re, sqlite3, subprocess, collections, numpy as np
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); AR = os.path.dirname(H); B = "<workspace>"
R = f"{H}/runs"; PD = f"{AR}/crowdq/runs"; SD = f"{AR}/packs/selftest-runs"
K = ("correctness", "completeness", "usefulness"); mr = lambda s: sum(s[k] for k in K) / 3
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se", "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
def load(p):
    J = collections.defaultdict(dict)
    for l in open(p):
        r = json.loads(l)
        if r.get("ok"): J[r["queryId"]][r["order"]] = r["mapped"]
    out = {}
    for q, v in J.items():
        assert len(v) == 2, q
        a, b = v["boarA"], v["boarB"]
        out[q] = {"s": (mr(a["boar"]) + mr(b["boar"])) / 2, "r": (mr(a["ref"]) + mr(b["ref"])) / 2, "winner": a["winner"] if a["winner"] == b["winner"] else "tie"}
    return out
def ratios(S, Rr): return S.sum() / Rr.sum(), (S - 1).sum() / (Rr - 1).sum()
def boot(fn, n, B=2000, seed=11):
    rng = np.random.default_rng(seed); return np.array([fn(rng.integers(0, n, n)) for _ in range(B)])
ci = lambda x: [round(float(v), 3) for v in np.percentile(x, [2.5, 97.5])]
def setstats(d, ids):
    S = np.array([d[q]["s"] for q in ids]); Rr = np.array([d[q]["r"] for q in ids]); pt = ratios(S, Rr); b = boot(lambda ii: ratios(S[ii], Rr[ii]), len(ids))
    w = collections.Counter(d[q]["winner"] for q in ids)
    return {"n": len(ids), "raw": round(pt[0], 3), "raw_ci": ci(b[:, 0]), "above_min": round(pt[1], 3), "above_min_ci": ci(b[:, 1]), "win_tie_loss": [w["boar"], w["tie"], w["ref"]]}
def paired(X, Y, ids):
    SX = np.array([X[q]["s"] for q in ids]); RX = np.array([X[q]["r"] for q in ids]); SY = np.array([Y[q]["s"] for q in ids]); RY = np.array([Y[q]["r"] for q in ids])
    f = lambda ii: [ratios(SX[ii], RX[ii])[j] - ratios(SY[ii], RY[ii])[j] for j in (0, 1)]
    pt = f(np.arange(len(ids))); b = boot(f, len(ids))
    return {"n": len(ids), "d_raw": round(pt[0], 3), "d_raw_ci": ci(b[:, 0]), "d_above_min": round(pt[1], 3), "d_above_min_ci": ci(b[:, 1]),
            "items_better_worse_same": [int(sum(X[q]["s"] > Y[q]["s"] for q in ids)), int(sum(X[q]["s"] < Y[q]["s"] for q in ids)), int(sum(X[q]["s"] == Y[q]["s"] for q in ids))]}
def same(a, b, label):
    o = subprocess.run(["python3", "-I", f"{AR}/seedgen/tools/same_answer.py", a, b, "--label", label], capture_output=True, text=True, check=True).stdout
    d = json.loads(o.splitlines()[0]); return {k: d[k] for k in ("n_paired", "errors", "all", "kept_unchanged", "kept_unchanged_prompt_same", "kept_unchanged_no_llm", "kept_unchanged_prompt_diff_n", "diff_ids_kept_unchanged_prompt_same")}
# ---------------------------------------------------------------- reach (crowdq reach.py logic)
pub = lambda p: f"{B}/shared-data/packs/{'wave2' if p in ('boar-factbook', 'boar-simplewiki-en') else 'wave1'}/{p}.sqlite"
URL = {}
for p in PACKS:
    for (u,) in sqlite3.connect(f"file:{pub(p)}?mode=ro", uri=True).execute("SELECT url FROM article_meta"):
        if u: URL.setdefault(u, p)
U = re.compile(r"https?://[^\s)]+")
def owner(s):
    for u in U.findall(s.get("source") or ""):
        if u in URL: return URL[u]
    return "kit:wikivoyage" if (s.get("source") or "").startswith("Wikivoyage") else "kit:other"
tl = lambda f: {t["itemId"]: t for t in map(json.loads, open(f))}
def url_in(u, src):  # audit F9: exact URL or path-segment prefix match (substring matched .../wiki/Google inside .../wiki/Google_AdSense)
    if not u: return False
    for v in U.findall(src or ""):
        v = v.rstrip(".,;:'\"]>")
        if v == u or (v.startswith(u) and v[len(u)] in "/#?"): return True
    return False
fact = lambda t, it: any(url_in(it["source"].get("url"), s.get("source")) for s in t["retrieval"]["kept"])
kl = lambda t: [(x["title"], x["section"]) for x in t["retrieval"]["kept"]]
reach = {"per_pack": {}}; tot = collections.Counter(); ownX = collections.Counter(); ownP = collections.Counter(); fam = {"SE": collections.Counter(), "topic": collections.Counter()}
TR = {}
for p in PACKS:
    items = {j["id"]: j for j in map(json.loads, open(f"{B}/rnd/research/packs/selftest/{p}.jsonl"))}
    X = tl(f"{R}/st-{p}-cut7-stack-s42.traces.jsonl"); P = tl(f"{PD}/st-{p}-cut7-all9-s42.traces.jsonl"); S = tl(f"{SD}/st-{p}-cut7-s42.traces.jsonl"); TR[p] = (X, P, S)
    c = collections.Counter()
    for i, it in items.items():
        x, q, s = X[i], P[i], S[i]
        ox = [owner(k) for k in x["retrieval"]["kept"]]; op = [owner(k) for k in q["retrieval"]["kept"]]
        ownX.update(o for o in ox if o != p); ownP.update(o for o in op if o != p)
        row = {"fact_S": fact(s, it), "fact_P": fact(q, it), "fact_X": fact(x, it), "own_kept_P": op.count(p), "own_kept_X": ox.count(p),
               "kept_P": len(op), "kept_X": len(ox), "empty_P": not op, "empty_X": not ox, "err_X": bool(x.get("error")), "kit11_X": len(x["config"]["kit"]) == 11,
               "changed_vs_P": kl(x) != kl(q) or x["timing"].get("promptTokens") != q["timing"].get("promptTokens"), "kept_changed_vs_P": kl(x) != kl(q),
               "pg_codes": any(cd.startswith("packground:kept") for cd in x["route"]["reasonCodes"])}
        c.update({k: int(v) for k, v in row.items()})
    reach["per_pack"][p] = dict(c); tot.update(c); fam["SE" if p.startswith("qa-") else "topic"].update(c)
reach["total"] = dict(tot); reach["family"] = {f: dict(v) for f, v in fam.items()}
reach["foreign_kept_X"] = dict(ownX.most_common()); reach["foreign_kept_P"] = dict(ownP.most_common())
allX = collections.Counter(); 
for p in PACKS:
    for t in TR[p][0].values(): allX.update(owner(k) for k in t["retrieval"]["kept"])
n = sum(allX.values()); reach["kept_share_X"] = {k: round(v / n, 3) for k, v in allX.most_common(6)}
reach["precheck"] = {"changed": tot["changed_vs_P"], "share": round(tot["changed_vs_P"] / 180, 3), "pass": tot["changed_vs_P"] / 180 >= 0.20}
# ---------------------------------------------------------------- quality 180
out = {"criterion_sha256": open(f"{H}/STACK2-criterion.sha256").read().split()[0], "reach": reach, "packs": []}
aX, aP, aS = {}, {}, {}
for p in PACKS:
    X = load(f"{R}/st-{p}-cut7-stack-s42.judgments.jsonl"); P = load(f"{PD}/st-{p}-cut7-all9-s42.judgments.jsonl"); S = load(f"{SD}/st-{p}-cut7-s42.judgments.jsonl")
    ids = sorted(set(X) & set(P) & set(S)); assert len(ids) == 20, p
    out["packs"].append({"pack": p, "S": setstats(S, ids), "P": setstats(P, ids), "X": setstats(X, ids), "X_minus_P": paired(X, P, ids), "X_minus_S": paired(X, S, ids),
                         "reach": {k: reach["per_pack"][p][k] for k in ("fact_S", "fact_P", "fact_X", "own_kept_P", "own_kept_X", "changed_vs_P")},
                         "same_answer_X_P": same(f"{PD}/st-{p}-cut7-all9-s42.traces.jsonl", f"{R}/st-{p}-cut7-stack-s42.traces.jsonl", p)})
    aX.update({f"{p}|{q}": X[q] for q in ids}); aP.update({f"{p}|{q}": P[q] for q in ids}); aS.update({f"{p}|{q}": S[q] for q in ids})
for name, sel in (("pooled", lambda k: True), ("SE", lambda k: k.startswith("qa-")), ("topic", lambda k: k.startswith("boar-"))):
    ids = sorted(k for k in aX if sel(k))
    out[name] = {"S": setstats(aS, ids), "P": setstats(aP, ids), "X": setstats(aX, ids), "X_minus_P": paired(aX, aP, ids), "X_minus_S": paired(aX, aS, ids)}
cat = lambda pat: "".join(open(pat.format(p)).read() for p in PACKS)
pc, xc = f"{H}/aggregates/_P180.traces.jsonl", f"{H}/aggregates/_X180.traces.jsonl"
open(pc, "w").write(cat(PD + "/st-{}-cut7-all9-s42.traces.jsonl")); open(xc, "w").write(cat(R + "/st-{}-cut7-stack-s42.traces.jsonl"))
out["same_answer_X_P_pooled"] = same(pc, xc, "pooled"); os.remove(pc); os.remove(xc)
# ---------------------------------------------------------------- v0.1 no-harm
OFF = load(f"{R}/v01-cut7-stack-off-s42.judgments.jsonl"); ON = load(f"{R}/v01-cut7-stack-on-s42.judgments.jsonl"); ids = sorted(set(OFF) & set(ON))
TO = tl(f"{R}/v01-cut7-stack-off-s42.traces.jsonl"); TN = tl(f"{R}/v01-cut7-stack-on-s42.traces.jsonl")
rep = {}; seen = collections.Counter()
for l in map(json.loads, open(f"{H}/runs/v01-kit.jsonl")):
    seen[(l["mode"], l["id"])] += 1
    if seen[(l["mode"], l["id"])] == 1: rep.setdefault(l["mode"], {})[l["id"]] = [(x["title"], x["section"]) for x in l["kept"]]
ident = lambda T, m: sum(kl(T[i]) == rep[m][i] for i in rep[m] if i in T)
v = {"n": len(ids), "OFF": setstats(OFF, ids), "ON": setstats(ON, ids), "ON_minus_OFF": paired(ON, OFF, ids),
     "identity_OFF_vs_kit_replay_off": f"{ident(TO, 'off')}/{len(rep['off'])}", "identity_ON_vs_kit_replay_stack": f"{ident(TN, 'stack')}/{len(rep['stack'])}",
     "kept_changed_ON_vs_OFF": sum(kl(TN[i]) != kl(TO[i]) for i in TO), "errors": [sum(bool(t.get("error")) for t in T.values()) for T in (TO, TN)],
     "same_answer": same(f"{R}/v01-cut7-stack-off-s42.traces.jsonl", f"{R}/v01-cut7-stack-on-s42.traces.jsonl", "v01")}
v["no_harm"] = v["ON_minus_OFF"]["d_raw_ci"][1] >= -0.03; out["v01"] = v
# ---------------------------------------------------------------- verdict (STACK-2 §2)
d = out["pooled"]["X_minus_P"]; lo, hi = d["d_raw_ci"]
verdict = ("LEVER" if lo > 0 and d["d_raw"] >= 0.03 else "SMALL" if lo > 0 else
           "near-miss -> Opus 720 recommended" if d["d_raw"] >= 0.015 and lo <= 0 <= hi else
           "NO" if hi < 0 else "not decided at MDE 0.03")
if v["ON_minus_OFF"]["d_raw_ci"][1] < -0.03 and verdict in ("LEVER", "SMALL"): verdict += " overridden by v0.1 harm -> not recommended"
out["verdict"] = verdict
json.dump(out, open(f"{H}/aggregates/stack.json", "w"), indent=1)
print(json.dumps({k: out[k] for k in ("pooled", "SE", "topic", "verdict")}, indent=1))
print("v01", json.dumps({k: v[k] for k in ("OFF", "ON", "ON_minus_OFF", "identity_OFF_vs_kit_replay_off", "identity_ON_vs_kit_replay_stack", "kept_changed_ON_vs_OFF", "errors", "no_harm")}))
print("v01 same", json.dumps({k: v["same_answer"][k] for k in ("all", "kept_unchanged", "kept_unchanged_prompt_same")}))
for r in out["packs"]: print(r["pack"], r["P"]["raw"], r["X"]["raw"], r["X_minus_P"]["d_raw"], r["X_minus_P"]["d_raw_ci"], r["X_minus_P"]["items_better_worse_same"], r["X_minus_S"]["d_raw"], r["reach"], r["same_answer_X_P"]["kept_unchanged_prompt_same"]["same_answer"], "/", r["same_answer_X_P"]["kept_unchanged_prompt_same"]["n"])
print("same pooled", json.dumps({k: out["same_answer_X_P_pooled"][k] for k in ("all", "kept_unchanged", "kept_unchanged_prompt_same")}))
print("reach", json.dumps({k: reach[k] for k in ("total", "family", "precheck", "kept_share_X", "foreign_kept_X", "foreign_kept_P")}))
