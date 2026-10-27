#!/usr/bin/env python3
"""X2B-OFF-MAIN report (0 LLM): OFF vs the ON K1 mini control on the 77 live MAIN ids, per X2B-OFF-MAIN-criterion.md. Writes main/aggregates/x2b-off-main.json."""
import json, random, statistics as st, sys
A = "<workspace>/rnd/research/coordinator/arms"; X = A + "/x2b-retest"; R = "x2boffmain-K1-main-live77-s42"
sys.path.insert(0, A + "/null-cal/tools"); from labels import label
ids = open(X + "/main-live77.ids").read().split()
rd = lambda f: {json.loads(l)["itemId"]: json.loads(l) for l in open(f) if l.strip()}
CT = rd(A + "/lp-screens/control/traces/lpctl-K1-main-s42.traces.jsonl")
CA = json.load(open(A + "/null-cal/control/pool-K1.json"))["items"]
T = rd(f"{X}/main/x2boffmain/traces/{R}.traces.jsonl"); AG = json.load(open(f"{X}/main/x2boffmain/aggregates/{R}.json"))["items"]
kept = lambda t: [(c.get("title"), c.get("section")) for c in (t.get("retrieval") or {}).get("kept", [])]
ctx = lambda t: (kept(t), t["timing"].get("promptTokens"))
LC = {i: label(CA[i]) for i in ids}; LA = {i: label(AG[i]) for i in ids}
def U(xs, L): return sum(0 if L[i]["R"] else L[i]["s"] for i in xs) / sum(L[i]["sref"] for i in xs)
def boot(xs):
    r = random.Random(11); d = []
    for _ in range(2000):
        s = [r.choice(xs) for _ in xs]; d.append(U(s, LA) - U(s, LC))
    d.sort(); return [round(d[49], 4), round(d[1949], 4)]
def side(L, xs, TT):
    rw = [TT[i]["timing"].get("retrievalMs") or 0 for i in xs]
    return dict(U_d=round(U(xs, L), 4), CEu=sum(L[i]["CEu"] for i in xs), R=sum(L[i]["R"] for i in xs), ret_ms_mean=round(st.mean(rw), 1), ret_ms_p50=round(st.median(rw), 1))
sets = {"MAIN77": ids, "v01": [i for i in ids if not i.startswith("st-")], "cm": [i for i in ids if i.startswith("st-")]}
out = {"criterion_sha": open(X + "/X2B-OFF-MAIN-criterion.sha256").read().split()[0], "n_rows": len(T),
       "errors": sum(bool(T[i].get("error")) for i in ids),
       "headpass_add_items": sum(any(c.startswith("headpass:add") for c in T[i]["route"].get("reasonCodes", [])) for i in ids),
       "zero_tok_on_nonzero_off": [i for i in ids if not (CT[i]["timing"].get("promptTokens") or 0) and (T[i]["timing"].get("promptTokens") or 0)],
       "changed_answers": sum(T[i]["answer"]["text"] != CA[i]["text"] for i in ids),
       "changed_contexts": sum(ctx(T[i]) != ctx(CT[i]) for i in ids), "sets": {}}
for k, xs in sets.items():
    both = [i for i in xs if (T[i]["timing"].get("promptTokens") or 0) > 0 and (CT[i]["timing"].get("promptTokens") or 0) > 0]
    pc = st.mean([CT[i]["timing"]["promptTokens"] for i in both]); pa = st.mean([T[i]["timing"]["promptTokens"] for i in both])
    on, off = side(LC, xs, CT), side(LA, xs, T)
    out["sets"][k] = dict(n=len(xs), on=on, off=off, dU=round(off["U_d"] - on["U_d"], 4), ci=boot(xs), dCEu=off["CEu"] - on["CEu"], dR=off["R"] - on["R"],
                          pt_live=[round(pc, 1), round(pa, 1), round((pa - pc) / pc * 100, 1)], n_live=len(both))
m = out["sets"]["MAIN77"]; safe = m["dU"] >= -0.02 and m["ci"][0] >= -0.05 and m["dCEu"] <= 2
out["verdict"] = "OFF is better" if (safe and m["dU"] > 0 and m["ci"][0] > 0) else ("OFF is safe for kit-only installs" if safe else "X2b stays on")
# nondeterminism check vs the X2B-RETEST OFF traces (same patch, overlapping ids)
try:
    P = rd(f"{X}/x2boff/traces/x2boff-K1-stage1-pool-s42.traces.jsonl"); ov = [i for i in ids if i in P]
    out["retest_overlap"] = dict(n=len(ov), same_text=sum(P[i]["answer"]["text"] == T[i]["answer"]["text"] for i in ov), same_ctx=sum(ctx(P[i]) == ctx(T[i]) for i in ov))
except FileNotFoundError: pass
json.dump(out, open(X + "/main/aggregates/x2b-off-main.json", "w"), indent=1)
print({k: out[k] for k in ("n_rows", "errors", "headpass_add_items", "zero_tok_on_nonzero_off", "changed_answers", "changed_contexts", "retest_overlap") if k in out})
for k, x in out["sets"].items():
    print(f"{k:6s} n {x['n']:2d} U_d ON {x['on']['U_d']:.4f} OFF {x['off']['U_d']:.4f} d {x['dU']:+.4f} {x['ci']} | CEu {x['on']['CEu']}->{x['off']['CEu']} R {x['on']['R']}->{x['off']['R']} | ptok {x['pt_live']} (n {x['n_live']}) | ret ms mean {x['on']['ret_ms_mean']}->{x['off']['ret_ms_mean']} p50 {x['on']['ret_ms_p50']}->{x['off']['ret_ms_p50']}")
print("VERDICT:", out["verdict"])
