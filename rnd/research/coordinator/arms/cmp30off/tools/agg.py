#!/usr/bin/env python3
"""CMP30OFF aggregation (0 LLM). Usage: python3 -I agg.py -> aggregates/cmp30off.json + stdout.
Runs: product rules (cmp30-q15 / cmp30-q17, judged in CMP30) vs override compactDeclinesOff (cmp30off-q15 / -q17), Pixel 8a.
Items: the 26 judged ids of boar-eval/runs/device-pixel8a/cmp30.jids (4 saf-* first-aid cards have no public reference).
Per item s = mean of the 3 judge dims averaged over both orders; sref likewise. Q = sum s / sum sref; U0 = Q with s := 0
for declined answers (trace answer.declined). CE = answered (non-declined) items with judge correctness (mean of orders) <= 1.5.
Warning = answer text starts with the fixed CMP30OFF line. Speed: rows with tokensGenerated > 0 among the 30 ids (no warm-up):
TTFT p50 (ttftMs), decode tok/s p50 (tokPerSec). Paired deltas: item bootstrap B 2000 seed 11, 2.5/97.5 percentiles."""
import json, os, random, statistics as st
B = "<workspace>"
RUNS = f"{B}/boar-eval/runs/device-pixel8a"
RES = f"{B}/handoff/pixel8-2026-10-20/bench/results"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "aggregates", "cmp30off.json")
W = "Not found in this phone's offline library. From the model's memory, may be wrong:"
ALL = [l.strip() for l in open(f"{RUNS}/cmp30.jids") if l.strip()]
IDS = [i for i in ALL if not i.startswith("saf-")]
ARMS = {"1.5B product": "cmp30-q15", "1.7B product": "cmp30-q17", "1.5B override": "cmp30off-q15", "1.7B override": "cmp30off-q17"}

def load(rid):
    tr = {}
    for l in open(f"{RUNS}/{rid}/traces.jsonl"):
        t = json.loads(l); tr[t["itemId"]] = t
    by = {}
    for l in open(f"{RUNS}/{rid}/judgments.haiku.jsonl"):
        r = json.loads(l)
        if r.get("ok") is True: by.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
    j = {}
    for q, v in by.items():
        if len(v) != 2: continue
        ms = list(v.values()); mean = lambda d: sum(d.values()) / 3
        j[q] = dict(s=sum(mean(m["boar"]) for m in ms) / 2, sref=sum(mean(m["ref"]) for m in ms) / 2, corr=sum(m["boar"]["correctness"] for m in ms) / 2)
    rows = {}
    for l in open(f"{RES}/{rid}/rows.jsonl"):
        r = json.loads(l); rows.setdefault(r["queryId"], r)  # first try
    items = {}
    for i in IDS:
        t = tr[i]; a = t["answer"]
        items[i] = dict(j[i], dec=bool(a.get("declined")), warn=(a.get("text") or "").startswith(W), text=a.get("text") or "",
                        codes=[c for c in t["route"]["reasonCodes"] if c.startswith("grounding:")])
    return items, rows

def metrics(items, ids):
    it = [items[i] for i in ids]; sr = sum(x["sref"] for x in it); nd = [x for x in it if not x["dec"]]; wa = [x for x in it if x["warn"]]
    return dict(n=len(it), Q=sum(x["s"] for x in it) / sr, U0=sum(0.0 if x["dec"] else x["s"] for x in it) / sr,
                declines=sum(x["dec"] for x in it), decline=sum(x["dec"] for x in it) / len(it),
                answered=len(nd), CE=sum(x["corr"] <= 1.5 for x in nd), CE_rate=(sum(x["corr"] <= 1.5 for x in nd) / len(nd)) if nd else 0.0,
                corr_answered=(sum(x["corr"] for x in nd) / len(nd)) if nd else None,
                warned=len(wa), corr_warned=(sum(x["corr"] for x in wa) / len(wa)) if wa else None, CE_warned=sum(x["corr"] <= 1.5 for x in wa))

def speed(rows):
    g = [rows[i] for i in ALL if i in rows and (rows[i].get("tokensGenerated") or 0) > 0]
    return dict(gen_rows=len(g), ttft_p50_s=st.median(r["ttftMs"] for r in g) / 1000, tok_s_p50=st.median(r["tokPerSec"] for r in g),
                total_p50_s=st.median(r["totalLatencyMs"] for r in g) / 1000)

def boot(A, Bi, key, B_=2000, seed=11):
    rnd = random.Random(seed); xs = []
    for _ in range(B_):
        s = [rnd.choice(IDS) for _ in IDS]
        a, b = metrics(A, s), metrics(Bi, s)
        if a[key] is None or b[key] is None: continue
        xs.append(a[key] - b[key])
    xs.sort(); n = len(xs); return [round(xs[int(0.025 * n)], 4), round(xs[int(0.975 * n) - 1], 4)]

def delta(A, Bi):
    ma, mb = metrics(A, IDS), metrics(Bi, IDS)
    return {k: dict(d=round(ma[k] - mb[k], 4), ci=boot(A, Bi, k)) for k in ("Q", "U0", "decline", "CE_rate")}

D, S = {}, {}
for name, rid in ARMS.items():
    D[name], rows = load(rid); S[name] = speed(rows)
res = {"n_items": len(IDS), "ids_excluded": [i for i in ALL if i not in IDS], "arms": {}, "deltas": {}}
for name in ARMS:
    m = metrics(D[name], IDS); m.update(S[name])
    m["released_codes"] = {}
    for i in IDS:
        for c in D[name][i]["codes"]:
            if "released" in c: m["released_codes"][c] = m["released_codes"].get(c, 0) + 1
    res["arms"][name] = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in m.items()}
res["deltas"]["1.7B - 1.5B (override)"] = delta(D["1.7B override"], D["1.5B override"])
res["deltas"]["1.7B - 1.5B (product)"] = delta(D["1.7B product"], D["1.5B product"])
res["deltas"]["override - product (1.5B)"] = delta(D["1.5B override"], D["1.5B product"])
res["deltas"]["override - product (1.7B)"] = delta(D["1.7B override"], D["1.7B product"])
# both answer under the override: reading quality where both models answered
both = [i for i in IDS if not D["1.7B override"][i]["dec"] and not D["1.5B override"][i]["dec"]]
dc = [D["1.7B override"][i]["corr"] - D["1.5B override"][i]["corr"] for i in both]
rb = __import__("random").Random(11); xs = []
for _ in range(2000):
    smp = [rb.choice(both) for _ in both]; xs.append(st.mean(D["1.7B override"][i]["corr"] - D["1.5B override"][i]["corr"] for i in smp))
xs.sort()
res["both_answered_override"] = dict(d_corr_ci=[round(xs[50], 3), round(xs[1949], 3)], n=len(both), corr_17=round(st.mean(D["1.7B override"][i]["corr"] for i in both), 3) if both else None,
                                     corr_15=round(st.mean(D["1.5B override"][i]["corr"] for i in both), 3) if both else None,
                                     d_corr=round(st.mean(dc), 3) if dc else None)
# warned items: per model, per item
res["warned_items"] = {name: [dict(id=i, corr=D[name][i]["corr"], codes=[c for c in D[name][i]["codes"] if "released" in c]) for i in IDS if D[name][i]["warn"]]
                       for name in ("1.5B override", "1.7B override")}
res["still_declined_override"] = {name: [dict(id=i, codes=[c for c in D[name][i]["codes"] if "declin" in c]) for i in IDS if D[name][i]["dec"]]
                                  for name in ("1.5B override", "1.7B override")}
os.makedirs(os.path.dirname(OUT), exist_ok=True); json.dump(res, open(OUT, "w"), indent=1)
for name, m in res["arms"].items():
    print(f"{name:14} Q={m['Q']:.3f} U0={m['U0']:.3f} decl={m['declines']:2d}/{m['n']} CE={m['CE']} corrAns={m['corr_answered'] if m['corr_answered'] is None else round(m['corr_answered'],2)} "
          f"warn={m['warned']} corrWarn={m['corr_warned'] if m['corr_warned'] is None else round(m['corr_warned'],2)} ttft={m['ttft_p50_s']:.1f}s tok/s={m['tok_s_p50']:.1f} gen={m['gen_rows']}")
for k, v in res["deltas"].items(): print(k, json.dumps(v))
print("both answered (override)", res["both_answered_override"])
