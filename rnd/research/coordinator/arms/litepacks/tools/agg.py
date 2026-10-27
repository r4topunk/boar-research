#!/usr/bin/env python3
"""LITEPACKS aggregation (0 LLM). Usage: python3 -I agg.py -> aggregates/litepacks.json, aggregates/examples.jsonl, stdout tables.
Per item s = mean of the 3 judge dims averaged over both orders; s_ref likewise. Q = sum s / sum s_ref; U = Q with s := 0 for declined answers.
CE = share of non-declined answers with correctness (mean of the two orders) <= 1.5. Warned = answer text starts with the CMP30OFF warning line.
Kept-slot share per pack: retrieval.kept entries attributed by source domain (en.wikipedia.org titles: crypto pack if the title is in its articles
table, else the top100k pack on K4). Paired deltas K - K0: item bootstrap B 2000, seed 11. K1-K4 rows reuse K0 judgments for byte-identical answers."""
import json, random, glob, os, re, sqlite3, statistics
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BE = "<workspace>/boar-eval/bench"
W = "Not found in this phone's offline library. From the model's memory, may be wrong:"
ARMS = ["K0", "K1", "K2", "K3", "K4"]
SIZE = {"K0": 387186688, "K1": 1122697216, "K2": 1134526464, "K3": 1165385728, "K4": 2929401856}
PACKS = {"K0": ["crypto", "wikivoyage"], "K1": ["crypto", "wikivoyage", "simplewiki"], "K2": ["crypto", "wikivoyage", "simplewiki", "factbook"],
         "K3": ["crypto", "wikivoyage", "simplewiki", "factbook", "medlineplus", "firstaid"], "K4": ["crypto", "wikivoyage", "top100k"]}
CRYPTO_TITLES = {r[0].lower() for r in sqlite3.connect("file:<workspace>/shared-data/crypto/boar-crypto.sqlite?mode=ro", uri=True).execute("select title from articles")}
DOM = {"en.wikivoyage.org": "wikivoyage", "simple.wikipedia.org": "simplewiki", "medlineplus.gov": "medlineplus", "github.com": "factbook",
       "www.cia.gov": "factbook", "archive.org": "firstaid", "www.ready.gov": "firstaid", "www.appropedia.org": "firstaid", "en.wikibooks.org": "firstaid",
       "ethereum.org": "crypto", "eips.ethereum.org": "crypto", "ercs.ethereum.org": "crypto"}
def pack_of(k, arm):
    s = k.get("source") or ""; m = re.match(r"^.*? — https?://([^/]+)", s)
    if not m: return "other"
    d = m.group(1)
    if d in DOM: return DOM[d]
    if d == "en.wikipedia.org":
        t = (k.get("title") or "").lower()
        return "crypto" if (arm != "K4" or t in CRYPTO_TITLES) else "top100k"
    return "other:" + d
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
def traces(arm):
    out = {}
    for f in sorted(glob.glob(f"{H}/traces/lp-{arm}-*-s42.traces.jsonl")):
        if "smoke" in f: continue
        for t in rd(f): out[t["itemId"]] = t
    return out
def judg(arm):
    by = {}
    for f in sorted(glob.glob(f"{H}/judgments/lp-{arm}-*.judgments.jsonl")):
        for r in rd(f):
            if r.get("ok") is not True: continue
            by.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
    out = {}
    for q, v in by.items():
        if len(v) != 2: continue
        ms = list(v.values()); mean = lambda d: sum(d.values()) / 3
        out[q] = dict(s=sum(mean(m["boar"]) for m in ms) / 2, sref=sum(mean(m["ref"]) for m in ms) / 2, corr=sum(m["boar"]["correctness"] for m in ms) / 2)
    return out
TR = {a: traces(a) for a in ARMS}
J0 = {a: judg(a) for a in ARMS}
V01 = [l.strip() for l in open(f"{H}/data/v01-57.ids") if l.strip()]
CM = sorted(i for i in TR["K0"] if i.startswith("st-qa-cooking-se") or i.startswith("st-qa-money-se"))
ST = sorted(i for i in TR["K0"] if i.startswith("st-") and i not in CM)
STC = [i for i in ST if i.startswith("st-boar-")]; STS = [i for i in ST if i.startswith("st-qa-")]
SETS = {"MAIN": V01 + CM, "v01": V01, "cm": CM, "st_cand": STC, "st_se": STS}
for p in ["boar-simplewiki-en", "boar-factbook", "boar-medlineplus-en", "boar-firstaid-en"]: SETS["st:" + p] = [i for i in STC if i.startswith("st-" + p + "-")]
CAT = {}
for q in rd(f"{BE}/v0.1/questions.public.jsonl"): CAT[q["id"]] = "v01:" + q["category"]
for i in CM: CAT[i] = "cm:" + ("cooking" if "cooking" in i else "money")
for i in ST: CAT[i] = "st:" + re.match(r"st-(.*)-\d+$", i).group(1)
ans = lambda a, i: TR[a][i]["answer"]["text"]
dec = lambda a, i: bool(TR[a][i]["answer"].get("declined"))
warned = lambda a, i: ans(a, i).startswith(W)
J = {"K0": J0["K0"]}
for a in ARMS[1:]:
    J[a] = {}
    for i in TR[a]:
        J[a][i] = J0["K0"].get(i) if ans(a, i) == ans("K0", i) else J0[a].get(i)
def avail(a): return [i for i in SETS["MAIN"] + ST if i in TR.get(a, {}) and J.get(a, {}).get(i)]
def item(a, i):
    j = J[a][i]; d = dec(a, i)
    return dict(s=j["s"], s0=0.0 if d else j["s"], sref=j["sref"], dec=d, corr=j["corr"], w=warned(a, i))
def metrics(a, ids):
    it = [item(a, i) for i in ids]; sr = sum(x["sref"] for x in it); nd = [x for x in it if not x["dec"]]
    return dict(Q=sum(x["s"] for x in it) / sr, U=sum(x["s0"] for x in it) / sr, decline=sum(x["dec"] for x in it) / len(it),
                CE=(sum(x["corr"] <= 1.5 for x in nd) / len(nd)) if nd else 0.0, warned=sum(x["w"] for x in it) / len(it),
                n=len(it), ce_count=sum(x["corr"] <= 1.5 for x in nd), warned_count=sum(x["w"] for x in it),
                ce_warned=sum(x["corr"] <= 1.5 and x["w"] for x in nd), ce_unwarned=sum(x["corr"] <= 1.5 and not x["w"] for x in nd), corr_mean=sum(x["corr"] for x in it) / len(it))
def boot(a, b, ids, key, B=2000, seed=11):
    rnd = random.Random(seed); xs = []
    for _ in range(B):
        s = [rnd.choice(ids) for _ in ids]; xs.append(metrics(a, s)[key] - metrics(b, s)[key])
    xs.sort(); return [round(xs[int(0.025 * B)], 4), round(xs[int(0.975 * B) - 1], 4)]
def retr(a, ids):
    cnt, tot, pt, rms = {}, 0, [], []
    for i in ids:
        t = TR[a][i]
        for k in t["retrieval"]["kept"]:
            p = pack_of(k, a); cnt[p] = cnt.get(p, 0) + 1; tot += 1
        if t["timing"].get("promptTokens"): pt.append(t["timing"]["promptTokens"])
        if t["timing"].get("retrievalMs") is not None: rms.append(t["timing"]["retrievalMs"])
    return dict(kept_total=tot, kept_per_item=round(tot / max(1, len(ids)), 2), share={p: round(c / tot, 3) for p, c in sorted(cnt.items(), key=lambda x: -x[1])} if tot else {},
                prompt_tokens_mean=round(statistics.mean(pt), 1) if pt else None, prompt_tokens_p50=statistics.median(pt) if pt else None,
                retrieval_ms_p50=round(statistics.median(rms), 1) if rms else None, ttft_ms_p50=round(statistics.median([TR[a][i]["timing"]["ttftMs"] for i in ids if TR[a][i]["timing"].get("ttftMs")]), 1))
r4 = lambda v: round(v, 4) if isinstance(v, float) else v
res = {"criterion_sha256": open(f"{H}/LITEPACKS-criterion.sha256").read().split()[0], "sizes_bytes": SIZE, "packs": PACKS,
       "sets": {k: len(v) for k, v in SETS.items()}, "arms": {}, "retrieval": {}, "deltas": {}, "per_category": {}}
done = [a for a in ARMS if all(i in TR[a] and J[a].get(i) for i in SETS["MAIN"])]
done_st = [a for a in ARMS if len(ST) == 180 and all(i in TR[a] and J[a].get(i) for i in ST)]
for a in done:
    res["arms"][a] = {k: {m: r4(v) for m, v in metrics(a, ids).items()} for k, ids in SETS.items() if (k in ("MAIN", "v01", "cm") or a in done_st)}
    res["retrieval"][a] = {k: retr(a, ids) for k, ids in SETS.items() if (k in ("MAIN", "v01", "cm") or a in done_st)}
    if a != "K0" and "K0" in done:
        res["deltas"][a] = {}
        for k, ids in SETS.items():
            if k not in ("MAIN", "v01", "cm") and not (a in done_st and "K0" in done_st): continue
            mo, mn = metrics(a, ids), metrics("K0", ids)
            res["deltas"][a][k] = {m: dict(d=r4(mo[m] - mn[m]), ci=boot(a, "K0", ids, m)) for m in ("U", "Q", "CE", "warned")}
            res["deltas"][a][k]["changed_answers"] = sum(ans(a, i) != ans("K0", i) for i in ids)
    cats = {}
    for i in SETS["MAIN"] + (ST if a in done_st else []): cats.setdefault(CAT[i], []).append(i)
    res["per_category"][a] = {c: {m: r4(v) for m, v in metrics(a, ids).items() if m in ("n", "U", "CE", "warned", "corr_mean")} for c, ids in sorted(cats.items())}
# verdict (frozen rule)
cand = []
for a in ["K1", "K2", "K3", "K4"]:
    d = res["deltas"].get(a, {}).get("MAIN")
    if not d: continue
    ok = d["U"]["d"] >= 0.03 and d["U"]["ci"][0] > 0 and d["CE"]["d"] <= 0.02
    cand.append(dict(arm=a, size=SIZE[a], dU=d["U"]["d"], ci=d["U"]["ci"], dCE=d["CE"]["d"], qualifies=ok))
q = sorted([c for c in cand if c["qualifies"]], key=lambda c: c["size"])
res["candidates"] = cand
res["verdict"] = (f"ADOPT {q[0]['arm']}" if q else "NO CHANGE (K0)") if len(cand) == 4 else "INCOMPLETE"
res["crowding_flags"] = {a: d["st_se"]["U"] for a, d in res["deltas"].items() if "st_se" in d and d["st_se"]["U"]["ci"][1] < 0}
# examples: warned confident error on K0 -> grounded (unwarned) correctness >= 4 on K; crowding: K0 unwarned corr >= 4 -> K corr drops >= 1.5
ex = []
for a in done:
    if a == "K0": continue
    for i in SETS["MAIN"] + (ST if a in done_st and "K0" in done_st else []):
        if i not in J["K0"] or i not in J[a] or not J[a][i] or not J["K0"].get(i): continue
        j0, j1 = J["K0"][i], J[a][i]
        kept_new = [pack_of(k, a) for k in TR[a][i]["retrieval"]["kept"]]
        row = dict(arm=a, id=i, cat=CAT[i], q=TR[a][i]["question"], corr_k0=j0["corr"], corr_k=j1["corr"], warned_k0=warned("K0", i), warned_k=warned(a, i),
                   ans_k0=ans("K0", i)[:400], ans_k=ans(a, i)[:400], kept_k=kept_new, kept_k0=[pack_of(k, "K0") for k in TR["K0"][i]["retrieval"]["kept"]])
        if warned("K0", i) and j0["corr"] <= 1.5 and not warned(a, i) and j1["corr"] >= 4: ex.append(dict(kind="fixed", **row))
        elif warned("K0", i) and j0["corr"] <= 1.5 and not warned(a, i) and j1["corr"] <= 1.5: ex.append(dict(kind="unwarned_error", **row))
        elif j0["corr"] >= 4 and j1["corr"] <= j0["corr"] - 1.5: ex.append(dict(kind="crowding" if not warned("K0", i) else "regressed", **row))
open(f"{H}/aggregates/examples.jsonl", "w").write("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in ex))
res["example_counts"] = {a: {k: sum(1 for e in ex if e["arm"] == a and e["kind"] == k) for k in ("fixed", "unwarned_error", "crowding", "regressed")} for a in done if a != "K0"}
json.dump(res, open(f"{H}/aggregates/litepacks.json", "w"), indent=1)
for a, d in res["arms"].items():
    for k, m in d.items():
        rr = res["retrieval"][a][k]
        print(f"{a} {k:22} n={m['n']:3} U={m['U']:.3f} Q={m['Q']:.3f} CE={m['CE']:.3f} ({m['ce_count']}, warned {m['ce_warned']}, unwarned {m['ce_unwarned']}) warned={m['warned']:.3f} decl={m['decline']:.3f} ptok={rr['prompt_tokens_mean']} rms50={rr['retrieval_ms_p50']} share={rr['share']}")
for a, d in res["deltas"].items():
    for k, m in d.items(): print("delta", a, k, {x: m[x] for x in ("U", "CE", "warned")}, "changed", m["changed_answers"])
print("candidates", json.dumps(cand)); print("VERDICT", res["verdict"], "crowding", res["crowding_flags"], "examples", res["example_counts"])

# ---- POST-HOC (not frozen; 2026-10-20 evening product decision): CE-unwarned = assertive answers without the warning line.
# Engine refusal/notice strings and short model abstentions are declines (definition from arms/reread-2026-10-20/reread.py), never CE.
# Reported as count and per-item rate (count / n); in default mode warned answers are refused, so this is the default-mode confident-error load.
ENGINE_DECLINE = re.compile(
    r"I don't have a reliable offline source on this, so I won't give health advice from memory|offline places pack is not installed"
    r"|I didn't find (this in this phone's library|safe first-aid instructions)"
    r"|^The offline source doesn't give first-aid steps for this\. In an emergency, call your local emergency number \(911 in the US, 112 in Europe\)\.$", re.I)
MODEL_DECLINE = re.compile(r"\b(i (do not|don't) know|i'?m not sure|i cannot answer|i can'?t answer|i don'?t have (enough |reliable )?information|not able to answer"
    r"|not enough information|(sources?|context|passages?) (do|does) not (contain|provide|mention)|unanswerable)\b", re.I)
def is_decl2(a, i):
    t = ans(a, i); body = t[len(W):].strip() if t.startswith(W) else t
    return dec(a, i) or bool(ENGINE_DECLINE.search(t)) or (len(body) < 300 and bool(MODEL_DECLINE.search(body))) or body == ""
def ceu(a, i): return (not is_decl2(a, i)) and (not warned(a, i)) and J[a][i]["corr"] <= 1.5
def ceu_rate(a, ids): return sum(ceu(a, i) for i in ids) / len(ids)
def ceu_boot(a, ids, B=2000, seed=11):
    rnd = random.Random(seed); xs = []
    for _ in range(B):
        s = [rnd.choice(ids) for _ in ids]; xs.append(ceu_rate(a, s) - ceu_rate("K0", s))
    xs.sort(); return [round(xs[int(0.025 * B)], 4), round(xs[int(0.975 * B) - 1], 4)]
ph = {}
for a in done:
    ph[a] = {}
    for k, ids in SETS.items():
        if not (k in ("MAIN", "v01", "cm") or a in done_st): continue
        row = dict(n=len(ids), ce_unwarned=sum(ceu(a, i) for i in ids), rate=r4(ceu_rate(a, ids)), engine_or_model_declines=sum(is_decl2(a, i) for i in ids))
        if a != "K0": row["delta_vs_K0"] = dict(d=r4(ceu_rate(a, ids) - ceu_rate("K0", ids)), ci=ceu_boot(a, ids))
        ph[a][k] = row
res["posthoc_ce_unwarned"] = ph
json.dump(res, open(f"{H}/aggregates/litepacks.json", "w"), indent=1)
for a in ph:
    for k in ("MAIN", "st_cand", "st_se"):
        print("POSTHOC", a, k, ph[a][k])
