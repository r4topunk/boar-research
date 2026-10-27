"""QFORM secondary aggregate (0 LLM). python3 -I judge/agg_answers.py <traces.jsonl> <judgments.jsonl...>   -> aggregates/answers.{json,md}
s = mean of the 3 judge.v1 dims averaged over both orders (agg_run.py definition); sref likewise; corr/use = correctness / usefulness averaged over orders.
U = sum(s-1)/sum(sref-1) with declined answers at the floor (s := 1); Q = same without the decline floor. Gold-kept = hit_kept of the PRIMARY replay (aggregates/matrix.json).
CIs: item (or, for paired reads, fact) bootstrap, B 2000, seed 11, percentile 2.5/97.5."""
import json, sys, random, os, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = "Not found in this phone's offline library. From the model's memory, may be wrong:"
trf, *jfs = sys.argv[1:]
T = {}
for l in open(trf):
    t = json.loads(l); T[t["itemId"]] = t
J = {}
for f in jfs:
    for l in open(f):
        r = json.loads(l)
        if r.get("ok") is True: J.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
M = {x["id"]: x for x in json.load(open(f"{ROOT}/aggregates/matrix.json"))["items"]}
SAN = json.load(open(f"{ROOT}/gen/sanity.json")); DIFF = set(SAN["diffs"])
def gk_run(i, t):
    """gold-kept in THIS generation run: the primary replay's flag where the kept title list is identical; False where the run's kept list is empty (nothing
    to hold the gold); None (unknown, excluded from the gold-kept splits) where the run's kept list differs from the replay's but is not empty."""
    if i not in DIFF: return bool(M[i]["hit_kept"])
    return False if not t["retrieval"]["kept"] else None
IT = {}
for l in open(f"{ROOT}/items/qform.jsonl"):
    d = json.loads(l); IT[d["id"]] = d
FORMS = [0, 1, 3, 8]; FN = {0: "F0 base", 1: "F1 entity-free", 3: "F3 situational", 8: "F8 follow-up"}
PACKS = ["boar-factbook", "boar-firstaid-en", "boar-medlineplus-en", "boar-crypto", "boar-wikivoyage-en", "boar-visa-en"]
rows = {}; missing = []
for i, t in T.items():
    if i not in J or len(J[i]) < 2: missing.append(i); continue
    ms = list(J[i].values()); d = bool(t["answer"].get("declined")); txt = t["answer"]["text"]
    mean3 = lambda m: sum(m.values()) / 3
    s = sum(mean3(m["boar"]) for m in ms) / 2; sr = sum(mean3(m["ref"]) for m in ms) / 2
    corr = sum(m["boar"]["correctness"] for m in ms) / 2; use = sum(m["boar"]["usefulness"] for m in ms) / 2; comp = sum(m["boar"]["completeness"] for m in ms) / 2
    wins = sum(m["winner"] == "boar" for m in ms)
    rows[i] = dict(id=i, pack=IT[i]["pack"], fact=IT[i]["fact_id"], form=IT[i]["form"], gk=gk_run(i, t), gk_replay=bool(M[i]["hit_kept"]), kept_changed=(i in DIFF), s=s, sr=sr, corr=corr, use=use, comp=comp,
                   declined=d, warned=txt.startswith(W), CE=(not d and corr <= 1.5), out_tok=t["timing"].get("outputTokens"), total_ms=t["timing"].get("totalMs"),
                   instant=(t["timing"].get("outputTokens") or 0) == 0, boar_win_orders=wins, empty=not txt.strip())
if missing: print("WARNING: no judgments for", len(missing), "items:", ",".join(missing[:10]), "...")
def stats(rs):
    n = len(rs)
    if n == 0: return None
    sref1 = sum(r["sr"] - 1 for r in rs)
    return dict(n=n, corr=sum(r["corr"] for r in rs) / n, use=sum(r["use"] for r in rs) / n, comp=sum(r["comp"] for r in rs) / n,
                U=sum((1 if r["declined"] else r["s"]) - 1 for r in rs) / sref1, Q=sum(r["s"] - 1 for r in rs) / sref1,
                CE=sum(r["CE"] for r in rs), declined=sum(r["declined"] for r in rs), warned=sum(r["warned"] for r in rs), instant=sum(r["instant"] for r in rs),
                out_tok=sum(r["out_tok"] or 0 for r in rs) / n, total_ms=sum(r["total_ms"] or 0 for r in rs) / n, empty=sum(r["empty"] for r in rs))
def boot(rs, fn, B=2000, seed=11):
    rng = random.Random(seed); n = len(rs); bs = []
    for _ in range(B):
        x = fn([rs[rng.randrange(n)] for _ in range(n)])
        bs.append(x)
    bs.sort(); return [bs[int(0.025 * B)], bs[int(0.975 * B) - 1]]
def withci(rs):
    s = stats(rs)
    if s is None: return None
    if len(rs) >= 2:
        for k in ("corr", "use", "U"): s[k + "_ci"] = boot(rs, lambda x, k=k: stats(x)[k])
    return s
def paired(rs0, rsi):
    """rs0, rsi dicts fact->row; deltas F0 - Fi on common facts."""
    fs = sorted(set(rs0) & set(rsi))
    if not fs: return None
    pr = [(rs0[f], rsi[f]) for f in fs]
    def d(p, k):
        a = [x[0] for x in p]; b = [x[1] for x in p]
        return (stats(a)[k] - stats(b)[k])
    out = dict(n=len(fs))
    for k in ("corr", "use", "U"):
        out[k] = d(pr, k)
        out[k + "_ci"] = boot(pr, lambda p, k=k: d(p, k)) if len(fs) >= 3 else None
    return out
R = list(rows.values())
res = dict(n=len(R), missing=missing)
res["by_form"] = {f: withci([r for r in R if r["form"] == f]) for f in FORMS}
res["by_form_gk"] = {f"{f}|gold_kept={int(g)}": withci([r for r in R if r["form"] == f and r["gk"] is g]) for f in FORMS for g in (True, False)}
res["by_gk"] = {f"gold_kept={int(g)}": withci([r for r in R if r["gk"] is g]) for g in (True, False)}
res["gk_unknown"] = [r["id"] for r in R if r["gk"] is None]
res["gk_replay_flags"] = {f: [sum(r["gk_replay"] for r in R if r["form"] == f), sum(r["gk"] is True for r in R if r["form"] == f)] for f in FORMS}
byf = {f: {r["fact"]: r for r in R if r["form"] == f} for f in FORMS}
res["paired"] = {}
for fi in (1, 3, 8):
    for tag, cond in (("both_kept", lambda a, b: a["gk"] is True and b["gk"] is True), ("neither_kept", lambda a, b: a["gk"] is False and b["gk"] is False),
                      ("f0_kept_fi_not", lambda a, b: a["gk"] is True and b["gk"] is False), ("f0_not_fi_kept", lambda a, b: a["gk"] is False and b["gk"] is True), ("all", lambda a, b: True)):
        common = [f for f in byf[0] if f in byf[fi] and cond(byf[0][f], byf[fi][f])]
        res["paired"][f"F0-F{fi}|{tag}"] = paired({f: byf[0][f] for f in common}, {f: byf[fi][f] for f in common}) if common else dict(n=0)
# unpaired gold-kept F0 vs F1 (prediction read): all items with gold kept in each form
res["pack_form"] = {p: {f: stats([r for r in R if r["pack"] == p and r["form"] == f]) for f in FORMS} for p in PACKS}
res["pack"] = {p: stats([r for r in R if r["pack"] == p]) for p in PACKS}
res["items"] = rows
json.dump(res, open(f"{ROOT}/aggregates/answers.json", "w"), indent=1, ensure_ascii=False)
# ---- markdown
def f2(x): return "-" if x is None else f"{x:.2f}"
def f3(x): return "-" if x is None else f"{x:.3f}"
def ci(s, k): return "" if s is None or (k + "_ci") not in s else f" [{s[k+'_ci'][0]:.2f},{s[k+'_ci'][1]:.2f}]"
L = ["# QFORM secondary: Qwen3-1.7B answers with the reference (A-union, stock retrieval = primary replay)", "",
     f"192 items (F0/F1/F3/F8 x 48), judge.v1 Haiku 5.5-low N 4 both orders; judged {len(R)} items. corr/use on the 1-5 scale; U = sum(s-1)/sum(ref-1), declined at floor. Bootstrap CIs over items (B 2000, seed 11).", "",
     "## Per form", "| form | n | corr [CI] | use [CI] | U [CI] | gold kept | CE (corr<=1.5) | declined | warned | instant (0 tok) | out tok | total ms |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
for f in FORMS:
    s = res["by_form"][f]; gk = sum(r["gk"] is True for r in R if r["form"] == f)
    L.append(f"| {FN[f]} | {s['n']} | {f2(s['corr'])}{ci(s,'corr')} | {f2(s['use'])}{ci(s,'use')} | {f3(s['U'])}{ci(s,'U')} | {gk} | {s['CE']} | {s['declined']} | {s['warned']} | {s['instant']} | {s['out_tok']:.0f} | {s['total_ms']:.0f} |")
L += ["", "## Gold kept (primary replay) x form", "| form | gold kept | n | corr | use | U [CI] | CE | warned | declined |", "|---|---|---|---|---|---|---|---|---|"]
for f in FORMS:
    for g in (1, 0):
        s = res["by_form_gk"][f"{f}|gold_kept={g}"]
        if s is None: L.append(f"| {FN[f]} | {'yes' if g else 'no'} | 0 | | | | | | |"); continue
        L.append(f"| {FN[f]} | {'yes' if g else 'no'} | {s['n']} | {f2(s['corr'])} | {f2(s['use'])} | {f3(s['U'])}{ci(s,'U')} | {s['CE']} | {s['warned']} | {s['declined']} |")
for g in (1, 0):
    s = res["by_gk"][f"gold_kept={g}"]
    L.append(f"| all forms | {'yes' if g else 'no'} | {s['n']} | {f2(s['corr'])} | {f2(s['use'])} | {f3(s['U'])}{ci(s,'U')} | {s['CE']} | {s['warned']} | {s['declined']} |")
L.append(f"gold-kept unknown (kept list changed vs replay, non-empty; excluded from the splits): {len(res['gk_unknown'])} items {res['gk_unknown']}")
L += ["", "## Paired F0 - Fi on the same fact (positive = F0 better); bootstrap over facts", "| pair | subset | n facts | d corr [CI] | d use [CI] | d U [CI] |", "|---|---|---|---|---|---|"]
for k, p in res["paired"].items():
    pr, sub = k.split("|")
    if not p or p.get("n", 0) == 0: L.append(f"| {pr} | {sub} | 0 | | | |"); continue
    c = lambda key: "" if p.get(key + "_ci") is None else f" [{p[key+'_ci'][0]:+.2f},{p[key+'_ci'][1]:+.2f}]"
    L.append(f"| {pr} | {sub} | {p['n']} | {p['corr']:+.2f}{c('corr')} | {p['use']:+.2f}{c('use')} | {p['U']:+.3f}{c('U')} |")
L += ["", "## Per pack (n 8 per form; indicative): U / corr", "| pack | F0 | F1 | F3 | F8 | all |", "|---|---|---|---|---|---|"]
for p in PACKS:
    cells = [f"{f3(res['pack_form'][p][f]['U'])} / {f2(res['pack_form'][p][f]['corr'])}" if res['pack_form'][p][f] else "-" for f in FORMS]
    s = res["pack"][p]; L.append(f"| {p} | " + " | ".join(cells) + f" | {f3(s['U'])} / {f2(s['corr'])} |" if s else f"| {p} | - |")
open(f"{ROOT}/aggregates/answers.md", "w").write("\n".join(L) + "\n")
print("\n".join(L))
