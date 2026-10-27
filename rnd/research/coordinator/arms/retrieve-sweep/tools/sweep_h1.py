"""RETRIEVE-SWEEP stage-1b arm H1 scoring (copy of sweep.py restricted to B0/B1/H1) (0 LLM). python3 -I tools/sweep.py
QFORM 432: gold hit = matrix.py rule (normalised quote in title+body of a kept chunk, or the gold merged chunk id).
MAIN 97 (K1 kit, K1 settings): FACTPRESENT lexical rule (ruler/tools/factpresent.py share_v01 / share_st, PRESENT = share >= 0.5) on the
kept chunks ("title\\nbody" blocks); recovery set = the funnel's 25 K1 S2/S3 ids, must-not-lose set = its 22 K1 S4/S5 ids.
Writes aggregates/sweep.json and aggregates/sweep.md."""
import glob, importlib.util, json, math, os, random, re, statistics, sys, unicodedata
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARMS_DIR = os.path.dirname(R); QF = os.path.join(ARMS_DIR, "qform"); CO = os.path.dirname(ARMS_DIR)
BE = "<workspace>/boar-eval/bench/"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
P = lambda *a: os.path.join(R, *a)
# ------------------------------------------------------------------ arm files
ARMS = [  # name, qform file, main file, label  (H1 sweep: B0, B1 and H1 only; same scoring as sweep.py)
    ("B0", os.path.join(QF, "replay/qform.replay.jsonl"), P("replay/B0.main.jsonl"), "stock (QFORM replay)"),
    ("B1", os.path.join(QF, "replay/qform.replay.k1settings.jsonl"), P("replay/B0.main.jsonl"), "K1 settings (head pass a2 + dense append-budget)"),
    ("H1", P("replay/H1.qform.jsonl"), P("replay/H1.main.jsonl"), "HP-SLATE (RS_HP_SLATE=1 on K1 settings)"),
]
WALL = {"B0": P("replay/B0w.qform.jsonl"), "B1": P("replay/B1w.qform.jsonl")}  # same trees, re-run with the wall-time tool
ARMS = [a for a in ARMS if os.path.exists(a[1])]
# ------------------------------------------------------------------ QFORM
items = {d["id"]: d for d in rd(os.path.join(QF, "items/qform.jsonl"))}
facts = {f["fact_id"]: f for f in json.load(open(os.path.join(QF, "items/facts.json")))}
norm = lambda s: re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", s.lower())).strip()
def cid(c):
    m = re.search(r":(\d+)$", c["chunkId"]); return int(m.group(1)) if m else None
def ghit(lst, f):
    q = norm(f["gold"]["quote"]); g = f["gold"]["merged_chunk_id"]
    return any(q in norm(c["title"] + " " + c["body"]) or cid(c) == g for c in lst)
tok = lambda c: math.ceil(len(f"{c['title']}\n{c['body']}") / 4)
def ctx_after(codes):
    for c in codes:
        m = re.match(r"context:(\d+)->(\d+)$", c)
        if m: return int(m.group(2))
    return None
def load_q(fn):
    out = {}
    for r in rd(fn):
        f = facts[items[r["id"]]["fact_id"]]
        out[r["id"]] = {"kept": ghit(r["keptFull"], f), "raw": ghit(r["rawFull"], f), "wide": ghit(r["wideFull"], f), "nk": len(r["keptFull"]),
                        "ktok": sum(tok(c) for c in r["keptFull"]), "ctx": ctx_after(r["reasonCodes"]), "wall": r.get("wallMs"), "ms": r.get("ms"),
                        "ids": [c["chunkId"] for c in r["keptFull"]], "codes": r["reasonCodes"]}
    return out
IDS = sorted(items)
FORMS = sorted({items[i]["form"] for i in IDS})
def boot(a, b, units, B=2000, seed=11):
    """mean(a - b) over items; percentile CI resampling `units` (list of lists of item ids)."""
    rng = random.Random(seed); n = len(units)
    d = {i: a[i] - b[i] for u in units for i in u}
    tot = sum(d.values()) / len(d); bs = []
    for _ in range(B):
        s = c = 0
        for _ in range(n):
            u = units[rng.randrange(n)]; s += sum(d[i] for i in u); c += len(u)
        bs.append(s / c)
    bs.sort(); return tot, bs[int(0.025 * B)], bs[int(0.975 * B) - 1]
Q = {a: load_q(fq) for a, fq, fm, lab in ARMS}
WQ = {a: load_q(f) for a, f in WALL.items() if os.path.exists(f)}
b0 = Q["B0"]
junk_ids = [i for i in IDS if not b0[i]["wide"]]  # gold not in B0's wide-12
dropped25 = [i for i in IDS if b0[i]["raw"] and not b0[i]["kept"]]  # QFORM: gold retrieved (raw) then dropped by the keep step
res = {"n_qform": len(IDS), "junk_set_n": len(junk_ids), "qform_dropped_n": len(dropped25), "arms": {}}
item_units = [[i] for i in IDS]
fact_units = {}
for i in IDS: fact_units.setdefault(items[i]["fact_id"], []).append(i)
fact_units = list(fact_units.values())
for a, fq, fm, lab in ARMS:
    q = Q[a]; v = {i: int(q[i]["kept"]) for i in IDS}; v0 = {i: int(b0[i]["kept"]) for i in IDS}
    d, lo, hi = boot(v, v0, item_units); dc, loc, hic = boot(v, v0, fact_units)
    wq = WQ.get(a, q)
    walls = [wq[i]["wall"] for i in IDS if wq[i]["wall"] is not None]
    ctxs = [q[i]["ctx"] for i in IDS if q[i]["ctx"] is not None]
    e = {"label": lab, "hit_kept": sum(v.values()) / len(IDS), "hit_kept_n": sum(v.values()),
         "delta_vs_B0": d, "ci_item": [lo, hi], "ci_fact_cluster": [loc, hic],
         "gained": sum(v[i] > v0[i] for i in IDS), "lost": sum(v[i] < v0[i] for i in IDS),
         "by_form": {str(f): sum(v[i] for i in IDS if items[i]["form"] == f) / sum(1 for i in IDS if items[i]["form"] == f) for f in FORMS},
         "junk_kept": statistics.mean(q[i]["nk"] for i in junk_ids), "mean_kept": statistics.mean(q[i]["nk"] for i in IDS),
         "ctx_tokens_after_compression": statistics.mean(ctxs) if ctxs else None,
         "kept_tokens": statistics.mean(q[i]["ktok"] for i in IDS),
         "wall_ms_mean": statistics.mean(walls) if walls else None, "wall_ms_p50": statistics.median(walls) if walls else None,
         "retrieve_ms_mean": statistics.mean(q[i]["ms"] for i in IDS if q[i]["ms"] is not None),
         "dropped_recovered": sum(q[i]["kept"] for i in dropped25),
         "kept_ids_changed": sum(q[i]["ids"] != b0[i]["ids"] for i in IDS)}
    res["arms"][a] = e
# ------------------------------------------------------------------ MAIN 97 (FACTPRESENT rule)
spec = importlib.util.spec_from_file_location("pc", "<workspace>/boar-eval/scorers/vendor/lantern/precheck.py")
pc = importlib.util.module_from_spec(spec); spec.loader.exec_module(pc)
QS = {q["id"]: q for q in rd(BE + "v0.1/questions.public.jsonl")}
for f in glob.glob(BE + "selftest/*/questions.jsonl"):
    for q in rd(f): QS[q["id"]] = q
STOP = set("the a an and or of to in on for with is are was were be been it its this that as at by from not no but if then than so do does did can could "
           "will would should may might has have had you your they their there which what when where who how why also more most very just only into "
           "out up about over after before such these those other some any all each".split())
def fnrm(s):
    s = unicodedata.normalize("NFKC", s or "").lower().replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"[‐-―−]", "-", s); return re.sub(r"\s+", " ", s).strip()
toks = lambda s: [w for w in re.findall(r"[a-z0-9][a-z0-9'.%-]*[a-z0-9%]|[a-z0-9]", fnrm(s)) if len(w) >= 3 and w not in STOP] or []
def tok_in_block(phrase, blocks, need):
    t = set(toks(phrase))
    if len(t) < need: return False
    return any(len(t & set(toks(b))) / len(t) >= 0.8 for b in blocks)
def share_v01(q, blocks):
    g = q.get("grading", {}); text = pc.norm("\n\n".join(blocks)); question = pc.norm(q["question"]); groups = []
    for grp in g.get("must_any", []):
        live = [t for t in grp if not pc.is_echo(t, question)]
        if live: groups.append(any(pc.hits(t, text) for t in live))
    mk = g.get("must_k")
    if mk:
        live = [t for t in mk["terms"] if not pc.is_echo(t, question)]
        groups.append(sum(pc.hits(t, text) for t in live) >= mk["k"])
    return (sum(groups) / len(groups)) if groups else None
def share_st(q, blocks):
    facts_ = q["selftest"]["in_pack_facts"]; whole = fnrm("\n\n".join(blocks)); hit = 0
    for f in facts_:
        quote = fnrm(f.get("quote", ""))
        hit += bool((len(quote) >= 12 and quote in whole) or tok_in_block(quote, blocks, 4) or tok_in_block(f.get("fact", ""), blocks, 3))
    return hit / len(facts_) if facts_ else None
def present(i, kept):
    q = QS[i]; blocks = [f"{c['title']}\n{c['body']}" for c in kept]
    s = share_st(q, blocks) if "selftest" in q else share_v01(q, blocks)
    return None if s is None else s >= 0.5
FUN = json.load(open(os.path.join(CO, "ruler/RAG-FUNNEL-2026-10-21.json")))["items"]
S23 = [l.strip() for l in open(os.path.join(QF, "funnel-S2S3.ids")) if l.strip()]
S45 = sorted(i for i, v in FUN.items() if v["K1"]["vstage"] in ("S4", "S5"))
def load_m(fn):
    return {r["id"]: {"present": present(r["id"], r["keptFull"]), "nk": len(r["keptFull"]), "wall": r.get("wallMs"),
                      "ids": [c["chunkId"] for c in r["keptFull"]], "retrieved": bool(r["rawFull"])} for r in rd(fn)}
M = {a: load_m(fm) for a, fq, fm, lab in ARMS if os.path.exists(fm)}
if "B0" in M:
    m0 = M["B0"]
    res["main_baseline"] = {"n": len(m0), "S2S3_present_in_baseline_replay": sum(bool(m0[i]["present"]) for i in S23),
                            "S4S5_present_in_baseline_replay": sum(bool(m0[i]["present"]) for i in S45),
                            "S2S3_ids_absent_in_baseline": [i for i in S23 if not m0[i]["present"]],
                            "S4S5_ids_absent_in_baseline": [i for i in S45 if not m0[i]["present"]]}
    for a, m in M.items():
        if a == "B1": continue
        rec = [i for i in S23 if m[i]["present"] and not m0[i]["present"]]
        los = [i for i in S45 if m0[i]["present"] and not m[i]["present"]]
        res["arms"][a].update({"main_recovery": len(rec), "main_recovery_ids": rec, "main_losses": len(los), "main_loss_ids": los,
                               "main_S2S3_present": sum(bool(m[i]["present"]) for i in S23), "main_S4S5_present": sum(bool(m[i]["present"]) for i in S45),
                               "main_kept_changed": sum(m[i]["ids"] != m0[i]["ids"] for i in m), "main_mean_kept": statistics.mean(m[i]["nk"] for i in m),
                               "main_wall_ms_mean": statistics.mean([m[i]["wall"] for i in m if m[i]["wall"] is not None] or [float("nan")])})
# ------------------------------------------------------------------ rule (RETRIEVE-SWEEP-criterion.md)
j0 = res["arms"]["B0"]["junk_kept"]
for a, e in res["arms"].items():
    if a in ("B0", "B1"): continue
    c = {"hit_ge_8pt_ci_gt_0": e["delta_vs_B0"] >= 0.08 and e["ci_item"][0] > 0,
         "recovery_ge_5": e.get("main_recovery", -1) >= 5, "losses_le_2": e.get("main_losses", 99) <= 2,
         "junk_le_1.25xB0": e["junk_kept"] <= 1.25 * j0}
    e["rule"] = c; e["verdict"] = "CANDIDATE" if all(c.values()) else "no"
json.dump(res, open(P("aggregates/sweep-H1.json"), "w"), indent=1)
# ------------------------------------------------------------------ md
pp = lambda x: f"{100 * x:+.1f}"
L = ["# RETRIEVE-SWEEP stage 1 (0 LLM): arms x metrics", "",
     f"QFORM n {len(IDS)} (hit@kept, paired vs B0; CI = item bootstrap B 2000 seed 11; fact-cluster CI beside it). Junk set = {len(junk_ids)} items whose gold is not in B0's wide-12. "
     f"MAIN 97 = K1 kit + K1 settings; recovery = of the funnel's 25 S2/S3 ids, fact PRESENT in the arm's kept list and not in the switch-off replay; losses = of the 22 S4/S5 ids, PRESENT in the switch-off replay and not in the arm.", "",
     "| arm | hit@kept | Δ vs B0 pts [CI item] | [CI fact] | gained/lost | QFORM dropped-25 kept | recovery /25 | losses /22 | junk-kept (B0 ×) | mean kept | ctx tok after compr. | kept tok | wall ms/q (mean) | verdict |",
     "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for a, e in res["arms"].items():
    L.append(f"| {a} {e['label']} | {100 * e['hit_kept']:.1f} ({e['hit_kept_n']}) | {pp(e['delta_vs_B0'])} [{pp(e['ci_item'][0])}, {pp(e['ci_item'][1])}] | [{pp(e['ci_fact_cluster'][0])}, {pp(e['ci_fact_cluster'][1])}] | "
             f"{e['gained']}/{e['lost']} | {e['dropped_recovered']}/{len(dropped25)} | {e.get('main_recovery', '-')} | {e.get('main_losses', '-')} | {e['junk_kept']:.2f} ({e['junk_kept'] / j0:.2f}) | {e['mean_kept']:.2f} | "
             f"{e['ctx_tokens_after_compression']:.0f} | {e['kept_tokens']:.0f} | {e['wall_ms_mean']:.0f} | {e.get('verdict', '-')} |")
L += ["", "## hit@kept % per form", "", "| arm | " + " | ".join(f"F{f}" for f in FORMS) + " |", "|---" * (len(FORMS) + 1) + "|"]
for a, e in res["arms"].items():
    L.append(f"| {a} | " + " | ".join(f"{100 * e['by_form'][str(f)]:.0f}" for f in FORMS) + " |")
if "main_baseline" in res:
    mb = res["main_baseline"]
    L += ["", f"MAIN switch-off replay vs the funnel labels: S2/S3 fact present {mb['S2S3_present_in_baseline_replay']}/25 (funnel: 0), S4/S5 present {mb['S4S5_present_in_baseline_replay']}/22 (funnel: 22)."]
open(P("aggregates/sweep-H1.md"), "w").write("\n".join(L) + "\n")
print("\n".join(L))
