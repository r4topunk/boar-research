#!/usr/bin/env python3
"""TK2FIX-L1 0-call gates (TK2FIX-L1-criterion.md 49beb0c5…). 0 LLM.
  gate.py run <pack>     per-run gate: 20 rows, ids = OFF ids, 0 errors / empty answers / reasoning tokens
  gate.py checkpoint     first 3 packs (medlineplus, factbook, simplewiki): KILL if kept-diff share vs OFF traces < 0.15 -> l1/checkpoint.json
  gate.py all            G0 on 180, G1 precheck kept-diff >= 25 and >= 90 % in the 3 changed packs, G2 kept-same on >= 140 of the 146 step-0 kept-same ids -> l1/gate.json
rc 0 PASS/CONTINUE, 8 FAIL/KILL."""
import json, sys, statistics as st
A = "<workspace>/rnd/research/coordinator/arms"; H = f"{A}/tk2fix"; R = f"{H}/l1/runs"
PACKS = ["boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en", "qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se", "boar-firstaid-en"]
CHANGED = PACKS[:3]; SP = json.load(open(f"{H}/l1/splits.json")); SHA = open(f"{H}/TK2FIX-L1-criterion.md.sha256").read().split()[0]
ld = lambda f: {(t := json.loads(l))["itemId"]: t for l in open(f) if l.strip()}
txt = lambda t: (t.get("answer") or {}).get("text") or ""; tm = lambda t: t.get("timing") or {}
kept = lambda t: [(s.get("title"), s.get("section")) for s in (t.get("retrieval") or {}).get("kept") or []]
on = lambda p: ld(f"{R}/tk2fix-l1-{p}-s42.traces.jsonl"); off = lambda p: ld(f"{A}/packs/selftest-runs/st-{p}-cut7-s42.traces.jsonl")
def g0(T): return {"rows": len(T), "errors": sum(bool(t.get("error")) for t in T.values()), "empty": sum(not txt(t).strip() for t in T.values()),
                   "reasoning_tokens": sum(tm(t).get("reasoningTokens") or 0 for t in T.values())}
def pair(packs):
    N, F = {}, {}
    for p in packs: N.update(on(p)); F.update(off(p))
    assert set(N) == set(F); return N, F
m = sys.argv[1]
if m == "run":
    p = sys.argv[2]; T, F = on(p), off(p); r = g0(T); ok = r["rows"] == 20 and set(T) == set(F) and r["errors"] == r["empty"] == r["reasoning_tokens"] == 0
    r["kept_diff"] = sum(kept(T[i]) != kept(F[i]) for i in T); r["verdict"] = "PASS" if ok else "FAIL"; print("gate run", p, json.dumps(r)); sys.exit(0 if ok else 8)
if m == "checkpoint":
    N, F = pair(CHANGED); kd = sum(kept(N[i]) != kept(F[i]) for i in N)
    r = {"criterion_sha256": SHA, "packs": CHANGED, "n": len(N), "kept_diff": kd, "kept_diff_share": round(kd / len(N), 3), "verdict": "CONTINUE" if kd / len(N) >= 0.15 else "KILL"}
    json.dump(r, open(f"{H}/l1/checkpoint.json", "w"), indent=1); print(json.dumps(r)); sys.exit(0 if r["verdict"] == "CONTINUE" else 8)
if m == "all":
    N, F = pair(PACKS); ids = sorted(N); kd = [i for i in ids if kept(N[i]) != kept(F[i])]
    same_ids = [i for i in ids if i not in set(SP["kept_diff"])]
    kd_in = sum(any(c in i for c in CHANGED) for i in kd); unexpected = [i for i in kd if i not in set(SP["kept_diff"])]
    G0 = g0(N); G1 = {"kept_diff": len(kd), "in_changed_packs": kd_in, "share_in_changed": round(kd_in / max(1, len(kd)), 3), "expected_step0": SP["n_kept_diff"],
                     "step0_kept_diff_reproduced": sum(i in set(kd) for i in SP["kept_diff"])}
    G2 = {"n": len(same_ids), "kept_identical": sum(kept(N[i]) == kept(F[i]) for i in same_ids), "unexpected_kept_diff": unexpected,
          "route_tier_diff": [i for i in ids if (N[i]["route"].get("task"), N[i]["route"].get("tier"), N[i]["route"].get("outcome")) != (F[i]["route"].get("task"), F[i]["route"].get("tier"), F[i]["route"].get("outcome"))]}
    ok = {"G0": G0["rows"] == 180 and G0["errors"] == G0["empty"] == G0["reasoning_tokens"] == 0, "G1": len(kd) >= 25 and kd_in / max(1, len(kd)) >= 0.9, "G2": G2["kept_identical"] >= 140}
    p50 = lambda T, k, I: st.median([tm(T[i])[k] for i in I if tm(T[i]).get(k) is not None])
    both = [i for i in ids if tm(N[i]).get("promptTokens") is not None and tm(F[i]).get("promptTokens") is not None]
    lat = {f"{k}_{a}": p50(T, k, ids) for k in ("promptTokens", "totalMs", "ttftMs") for a, T in (("on", N), ("off", F))}
    lat |= {"answerWords_on": st.median(len(txt(N[i]).split()) for i in ids), "answerWords_off": st.median(len(txt(F[i]).split()) for i in ids),
            "promptTokens_paired_p50_kept_diff": st.median([tm(N[i])["promptTokens"] - tm(F[i])["promptTokens"] for i in kd if i in both]) if kd else None,
            "totalMs_on_kept_diff": p50(N, "totalMs", kd), "totalMs_off_kept_diff": p50(F, "totalMs", kd)}
    r = {"criterion_sha256": SHA, "G0": G0, "G1": G1, "G2": G2, "latency_p50": lat, "answers_identical_on_off": sum(txt(N[i]) == txt(F[i]) for i in ids),
         "kept_diff_ids": kd, "pass": ok, "verdict": "PASS" if all(ok.values()) else "FAIL"}
    json.dump(r, open(f"{H}/l1/gate.json", "w"), indent=1); print(json.dumps({k: v for k, v in r.items() if k != "kept_diff_ids"})); sys.exit(0 if all(ok.values()) else 8)
