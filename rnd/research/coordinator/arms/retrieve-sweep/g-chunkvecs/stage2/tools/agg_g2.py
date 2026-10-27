"""Arm G stage 2 aggregate (0 LLM). python3 -I stage2/tools/agg_g2.py  -> g-chunkvecs/answers.{json,md}
Definitions as arms/qform/judge/agg_answers.py: s = mean of the 3 judge.v1 dims averaged over both orders; sref likewise for the reference answer; U = sum(s-1)/sum(sref-1) with
declined answers at the floor (s := 1); corr/use = correctness/usefulness averaged over orders; CE (confident error) = not declined and corr <= 1.5; warned = answer starts with the
weak-sources line. Population = the changed-context items that were judged (stage2/changed.ids, minus any named in 'left'); unchanged items reuse CTL by construction (same context,
same seed) and are only counted. Paired dU = U_arm - U_ctl with item bootstrap B 2000 seed 11 (percentile 2.5/97.5). Gold-kept = quote match (normalised) of the item's fact
gold in the replay's keptFull when the run's kept titles equal the replay's; False when the run's kept list is empty; None (excluded from the 2x2) otherwise."""
import json, os, random, re, sys, collections
S2 = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); G = os.path.dirname(S2)
A = "<workspace>/rnd/research/coordinator/arms"
W = "Not found in this phone's offline library. From the model's memory, may be wrong:"
facts = {f["fact_id"]: f for f in json.load(open(f"{A}/qform/items/facts.json"))}
IT = {}
for l in open(f"{A}/qform/items/qform.jsonl"):
    d = json.loads(l); IT[d["id"]] = d
ids = [json.loads(l)["id"] for l in open(f"{G}/q3.jsonl") if l.strip()]
norm = lambda s: re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", s.lower())).strip()
SAN = json.load(open(f"{S2}/sanity.json"))
chg = [x for x in open(f"{S2}/changed.ids").read().split() if x]
T, REP, J = {}, {}, {}
for w, rf in (("ctl", "ctl3"), ("arm", "dense2-true")):
    T[w] = {}
    for l in open(f"{S2}/traces/g2-{w}.traces.jsonl"):
        t = json.loads(l); T[w][t["itemId"]] = t
    REP[w] = {json.loads(l)["id"]: json.loads(l) for l in open(f"{G}/{rf}.jsonl")}
    J[w] = {}
    for suf in ("", "-F4"):
        jf = f"{S2}/judge/g2-{w}{suf}.judgments.jsonl"
        if os.path.exists(jf):
            for l in open(jf):
                r = json.loads(l)
                if r.get("ok") is True: J[w].setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
def gold_in(lst, i):
    q = norm(facts[IT[i]["fact_id"]]["gold"]["quote"]); return any(q in norm(c["title"] + " " + c["body"]) for c in lst)
def gk(w, i):
    t = T[w][i]; run = [c["title"] for c in t["retrieval"]["kept"]]; rp = REP[w][i]["keptFull"]
    if run == [c["title"] for c in rp]: return gold_in(rp, i)
    return False if not run else None
def row(w, i):
    t = T[w][i]; ms = list(J[w][i].values()); txt = t["answer"]["text"]; d = bool(t["answer"].get("declined"))
    m3 = lambda m: sum(m.values()) / 3
    s = sum(m3(m["boar"]) for m in ms) / 2; sr = sum(m3(m["ref"]) for m in ms) / 2
    corr = sum(m["boar"]["correctness"] for m in ms) / 2; use = sum(m["boar"]["usefulness"] for m in ms) / 2
    return dict(id=i, form=IT[i]["form"], pack=IT[i]["pack"], fact=IT[i]["fact_id"], s=s, sr=sr, corr=corr, use=use, declined=d, warned=txt.startswith(W), CE=(not d and corr <= 1.5),
                out_tok=t["timing"].get("outputTokens") or 0, total_ms=t["timing"].get("totalMs") or 0, gk=gk(w, i), instant=(t["timing"].get("outputTokens") or 0) == 0)
same_txt = [i for i in chg if T["ctl"][i]["answer"]["text"] == T["arm"][i]["answer"]["text"]]   # kept list differs, answer text identical: dU = 0 by construction
judged = [i for i in chg if i in J["ctl"] and i in J["arm"] and len(J["ctl"][i]) == 2 and len(J["arm"][i]) == 2]
left = [i for i in chg if i not in judged and i not in same_txt]
R = {w: {i: row(w, i) for i in judged} for w in ("ctl", "arm")}
def stats(rs):
    n = len(rs)
    if not n: return None
    den = sum(r["sr"] - 1 for r in rs)
    return dict(n=n, corr=sum(r["corr"] for r in rs) / n, use=sum(r["use"] for r in rs) / n, U=sum((1 if r["declined"] else r["s"]) - 1 for r in rs) / den,
                CE=sum(r["CE"] for r in rs), declined=sum(r["declined"] for r in rs), warned=sum(r["warned"] for r in rs), instant=sum(r["instant"] for r in rs),
                out_tok=sum(r["out_tok"] for r in rs) / n, total_ms=sum(r["total_ms"] for r in rs) / n)
def dU(pairs):
    return stats([b for a, b in pairs])["U"] - stats([a for a, b in pairs])["U"]
def boot(pairs, fn, B=2000, seed=11):
    rng = random.Random(seed); n = len(pairs); bs = sorted(fn([pairs[rng.randrange(n)] for _ in range(n)]) for _ in range(B)); return [bs[int(0.025 * B)], bs[int(0.975 * B) - 1]]
P = [(R["ctl"][i], R["arm"][i]) for i in judged]
res = dict(n_items=len(ids), changed=len(chg), judged=len(judged), same_text=len(same_txt), left=left, unchanged=len(ids) - len(chg))
res["ctl"] = stats([a for a, b in P]); res["arm"] = stats([b for a, b in P])
for w in ("ctl", "arm"):
    for k in ("U", "corr", "use"): res[w][k + "_ci"] = boot([(r, r) for r in R[w].values()], lambda p, k=k: stats([a for a, b in p])[k])
res["dU"] = dU(P); res["dU_ci"] = boot(P, dU)
def boot_fact(B=2000, seed=11):
    by = collections.defaultdict(list)
    for a, b in P: by[a["fact"]].append((a, b))
    fs = sorted(by); rng = random.Random(seed); bs = []
    for _ in range(B):
        pr = [x for f in (fs[rng.randrange(len(fs))] for _ in fs) for x in by[f]]; bs.append(dU(pr))
    bs.sort(); return [bs[int(0.025 * B)], bs[int(0.975 * B) - 1]]
res["dU_ci_fact"] = boot_fact()
res["dcorr"] = stats([b for a, b in P])["corr"] - stats([a for a, b in P])["corr"]
res["dcorr_ci"] = boot(P, lambda p: stats([b for a, b in p])["corr"] - stats([a for a, b in p])["corr"])
res["duse"] = stats([b for a, b in P])["use"] - stats([a for a, b in P])["use"]
res["wins"] = dict(arm_better=sum(b["s"] > a["s"] + 1e-9 for a, b in P), ctl_better=sum(a["s"] > b["s"] + 1e-9 for a, b in P), tie=sum(abs(a["s"] - b["s"]) <= 1e-9 for a, b in P))
# dilution: identical-text changed-context items and all unchanged items contribute 0 to the numerator; their reference denominators are imputed at the judged mean sref - 1
msr = sum(a["sr"] - 1 for a, b in P) / len(P); num = sum((1 if b["declined"] else b["s"]) - (1 if a["declined"] else a["s"]) for a, b in P)
res["dU_diluted"] = {k: num / (sum(a["sr"] - 1 for a, b in P) + msr * extra) for k, extra in (("changed_context_incl_same_text", len(same_txt) + len(left)), ("all216_nonF8_imputed", len(ids) - len(P)))}
res["dU_diluted"]["note"] = "indicative: numerator = judged items only (the unjudged F8 items assumed 0), denominator = sum(sref-1) of judged + imputed mean sref-1 for the rest"
# 2x2 gold kept (ctl/arm)
res["gk22"] = {}
for gc in (True, False):
    for ga in (True, False):
        sub = [(a, b) for a, b in P if a["gk"] is gc and b["gk"] is ga]
        res["gk22"][f"ctl={int(gc)},arm={int(ga)}"] = dict(n=len(sub), U_ctl=stats([a for a, b in sub])["U"] if sub else None, U_arm=stats([b for a, b in sub])["U"] if sub else None,
                                                          CE_ctl=sum(a["CE"] for a, b in sub), CE_arm=sum(b["CE"] for a, b in sub), dU=dU(sub) if sub else None)
res["gk_unknown"] = [a["id"] for a, b in P if a["gk"] is None or b["gk"] is None]
# gold-kept over all 216 (replay flags + run flags) for context
res["gold_kept_all216"] = {w: dict(replay=sum(gold_in(REP[w][i]["keptFull"], i) for i in ids), run_known=sum(gk(w, i) is True for i in ids), run_unknown=sum(gk(w, i) is None for i in ids)) for w in ("ctl", "arm")}
res["all216"] = {w: dict(out_tok=sum(T[w][i]["timing"].get("outputTokens") or 0 for i in ids) / len(ids), total_ms=sum(T[w][i]["timing"].get("totalMs") or 0 for i in ids) / len(ids),
                         prompt_tok=sum(T[w][i]["timing"].get("promptTokens") or 0 for i in ids) / len(ids), warned=sum(T[w][i]["answer"]["text"].startswith(W) for i in ids),
                         declined=sum(bool(T[w][i]["answer"].get("declined")) for i in ids)) for w in ("ctl", "arm")}
res["by_form"] = {}; res["by_pack"] = {}
for f in sorted({IT[i]["form"] for i in ids}):
    sub = [(a, b) for a, b in P if a["form"] == f]
    if sub: res["by_form"][f] = dict(n=len(sub), U_ctl=stats([a for a, b in sub])["U"], U_arm=stats([b for a, b in sub])["U"], dU=dU(sub))
for p in sorted({IT[i]["pack"] for i in ids}):
    sub = [(a, b) for a, b in P if a["pack"] == p]
    if sub: res["by_pack"][p] = dict(n=len(sub), U_ctl=stats([a for a, b in sub])["U"], U_arm=stats([b for a, b in sub])["U"], dU=dU(sub), CE_ctl=sum(a["CE"] for a, b in sub), CE_arm=sum(b["CE"] for a, b in sub))
res["items"] = {i: dict(ctl=R["ctl"][i], arm=R["arm"][i]) for i in judged}
json.dump(res, open(f"{G}/answers.json", "w"), indent=1, ensure_ascii=False)
f3 = lambda x: "-" if x is None else f"{x:.3f}"; f2 = lambda x: "-" if x is None else f"{x:.2f}"
ci = lambda c, d=3: f" [{c[0]:+.{d}f}, {c[1]:+.{d}f}]"
L = ["# Arm G stage 2: Qwen3-1.7B answers, CTL (v2 packs) vs ARM (v3proto, packDense2 true) on the changed-context items (exploratory)", "",
     f"216 items; changed-context {res['changed']} = judged {res['judged']} (answers differ) + {res['same_text']} with identical answer text (dU 0 by construction) + {len(left)} not judged (cap); unchanged-context {res['unchanged']} (identical answers, reuse CTL). judge.v1 Haiku 5.5-low N 4 both orders. CIs item bootstrap B 2000 seed 11.", "",
     "| arm | n | U [CI] | corr | use | CE (corr<=1.5) | warned | declined | instant | out tok | total ms |", "|---|---|---|---|---|---|---|---|---|---|---|"]
for w in ("ctl", "arm"):
    s = res[w]; L.append(f"| {w.upper()} | {s['n']} | {f3(s['U'])}{ci(s['U_ci'], 3).replace('+', '')} | {f2(s['corr'])} | {f2(s['use'])} | {s['CE']} | {s['warned']} | {s['declined']} | {s['instant']} | {s['out_tok']:.0f} | {s['total_ms']:.0f} |")
L += ["", f"Diluted (indicative): dU over all changed-context items {res['dU_diluted']['changed_context_incl_same_text']:+.3f}; over all 216 {res['dU_diluted']['all216_nonF8_imputed']:+.3f}.", f"Paired ARM - CTL on the judged changed items: dU {res['dU']:+.3f}{ci(res['dU_ci'])}; fact-cluster CI {ci(res['dU_ci_fact']).strip()}; d corr {res['dcorr']:+.2f}{ci(res['dcorr_ci'], 2)}; d use {res['duse']:+.2f}; item score better ARM/CTL/tie = {res['wins']['arm_better']}/{res['wins']['ctl_better']}/{res['wins']['tie']}.", "",
      "## Gold kept (CTL/ARM) x U on the changed items", "| gold kept ctl/arm | n | U ctl | U arm | dU | CE ctl | CE arm |", "|---|---|---|---|---|---|---|"]
for k, v in res["gk22"].items(): L.append(f"| {k} | {v['n']} | {f3(v['U_ctl'])} | {f3(v['U_arm'])} | {'-' if v['dU'] is None else f'{v['dU']:+.3f}'} | {v['CE_ctl']} | {v['CE_arm']} |")
L.append(f"gold-kept unknown (kept list differs from the replay, non-empty): {len(res['gk_unknown'])} items")
L += ["", "## Per form (changed items; indicative)", "| form | n | U ctl | U arm | dU |", "|---|---|---|---|---|"]
for k, v in res["by_form"].items(): L.append(f"| F{k} | {v['n']} | {f3(v['U_ctl'])} | {f3(v['U_arm'])} | {v['dU']:+.3f} |")
L += ["", "## Per pack (changed items; indicative)", "| pack | n | U ctl | U arm | dU | CE ctl | CE arm |", "|---|---|---|---|---|---|---|"]
for k, v in res["by_pack"].items(): L.append(f"| {k} | {v['n']} | {f3(v['U_ctl'])} | {f3(v['U_arm'])} | {v['dU']:+.3f} | {v['CE_ctl']} | {v['CE_arm']} |")
a = res["all216"]
L += ["", f"All 216 (from the traces): prompt tokens ctl {a['ctl']['prompt_tok']:.0f} / arm {a['arm']['prompt_tok']:.0f}; out tokens {a['ctl']['out_tok']:.1f} / {a['arm']['out_tok']:.1f}; total ms {a['ctl']['total_ms']:.0f} / {a['arm']['total_ms']:.0f}; warned {a['ctl']['warned']} / {a['arm']['warned']}; declined {a['ctl']['declined']} / {a['arm']['declined']}.",
      f"Gold kept in the run (all 216; replay flag where kept titles match, unknown otherwise): ctl {res['gold_kept_all216']['ctl']}, arm {res['gold_kept_all216']['arm']}.", f"Not judged: {left}"]
open(f"{G}/answers.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
