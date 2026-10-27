#!/usr/bin/env python3
"""LITE5-180 0-call gates (LITE5-180-criterion.md 8fafa952…). 0 LLM.
  gate180.py run <on|off> <pack>      per-run gate (stage 1): 20 rows, 0 errors/empty/reasoning/<think>; ON: headpass:* fired on >= 1 item, no nosidecar/noopts beyond the 4B X2b trace; OFF: no headpass add codes
  gate180.py checkpoint               stage 2 on the first 3 packs: KILL if fact-in-context gain <= 0 or kept-diff share < 0.50   -> aggregates/checkpoint-180.json
  gate180.py all                      stage 3 on the 180: G0..G3                                                                     -> aggregates/gate-180.json
rc 0 PASS, 8 FAIL/KILL."""
import json, re, sys, statistics as st
A = "<workspace>/rnd/research/coordinator/arms"; H = f"{A}/lite5"; R = f"{H}/runs/180"
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se", "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
FACTS = json.load(open(f"{A}/oracle-st/tools/oracle-facts.json")); CID = re.compile(r"^pack:(?:local-)?([^:]+):(\d+)$")
SPLIT = {d["id"]: d for d in map(json.loads, open(f"{A}/headpass-st/runs-x2/split-x2b.jsonl"))}
ld = lambda f: {(t := json.loads(l))["itemId"]: t for l in open(f) if l.strip()}
txt = lambda t: (t.get("answer") or {}).get("text") or ""; tm = lambda t: t.get("timing") or {}
kept = lambda t: [(s.get("title"), s.get("section")) for s in (t.get("retrieval") or {}).get("kept") or []]
codes = lambda t: (t.get("route") or {}).get("reasonCodes") or []
hp = lambda t: [c for c in codes(t) if c.startswith("headpass")]
ADD = ("headpass:add:", "headpass:dense:add:")
def g0(T):
    return {"errors": sum(bool(t.get("error")) for t in T.values()), "empty": sum(not txt(t).strip() for t in T.values()),
            "reasoning_tokens": sum(tm(t).get("reasoningTokens") or 0 for t in T.values()), "think_tag": sum("<think>" in txt(t) for t in T.values())}
def fic(i, t):
    p = FACTS[i]["pack"]; app = [x.split(":add:")[1] for x in codes(t) if x.startswith(ADD)]
    fc = {int(x.rsplit(":", 1)[1]) for x in FACTS[i]["fact_chunks"]}
    own = {int(m.group(2)) for x in app for m in [CID.match(x)] if m and m.group(1) == p}
    return {"off": SPLIT[i]["S_present"], "appended_fact": bool(fc & own), "on": SPLIT[i]["S_present"] or bool(fc & own), "n_appended": len(app)}
def pair(packs):
    ON, OFF, X4 = {}, {}, {}
    for p in packs:
        ON.update(ld(f"{R}/lite5-180-on-{p}-s42.traces.jsonl")); OFF.update(ld(f"{R}/lite5-180-off-{p}-s42.traces.jsonl"))
        X4.update(ld(f"{A}/headpass-st/gen-x2b/st-{p}-cut7-headpassx2b-s42.traces.jsonl"))
    assert set(ON) == set(OFF) == set(X4), "id sets differ"
    return ON, OFF, X4
mode = sys.argv[1]
if mode == "run":
    m, p = sys.argv[2], sys.argv[3]; T = ld(f"{R}/lite5-180-{m}-{p}-s42.traces.jsonl"); X4 = ld(f"{A}/headpass-st/gen-x2b/st-{p}-cut7-headpassx2b-s42.traces.jsonl")
    r = {"rows": len(T), **g0(T)}; ok = r["rows"] == 20 and set(T) == set(X4) and all(r[k] == 0 for k in ("errors", "empty", "reasoning_tokens", "think_tag"))
    if m == "on":
        bad = lambda t: [c for c in codes(t) if re.search(r":(nosidecar|noopts)$", c)]
        r["fired"] = sum(any(c.startswith(ADD) for c in codes(t)) for t in T.values()); r["hp_any"] = sum(bool(hp(t)) for t in T.values())
        r["extra_nosidecar"] = sum(bool(bad(T[i])) and not bad(X4[i]) for i in T); ok = ok and r["hp_any"] >= 1 and r["extra_nosidecar"] == 0
    else:
        r["add_codes"] = sum(any(c.startswith(ADD) for c in codes(t)) for t in T.values()); ok = ok and r["add_codes"] == 0
    r["verdict"] = "PASS" if ok else "FAIL"; print(f"gate run {m} {p}", json.dumps(r)); sys.exit(0 if ok else 8)
if mode == "checkpoint":
    ON, OFF, _ = pair(PACKS[:3]); F = {i: fic(i, ON[i]) for i in ON}
    gain = sum(f["on"] for f in F.values()) - sum(f["off"] for f in F.values()); kd = sum(kept(ON[i]) != kept(OFF[i]) for i in ON)
    r = {"criterion_sha256": open(f"{H}/LITE5-180-criterion.sha256").read().split()[0], "packs": PACKS[:3], "n": len(ON), "fic_on": sum(f["on"] for f in F.values()),
         "fic_off": sum(f["off"] for f in F.values()), "fic_gain": gain, "kept_diff": kd, "kept_diff_share": round(kd / len(ON), 3)}
    r["verdict"] = "CONTINUE" if gain > 0 and kd / len(ON) >= 0.5 else "KILL"
    json.dump(r, open(f"{H}/aggregates/checkpoint-180.json", "w"), indent=1); print(json.dumps(r)); sys.exit(0 if r["verdict"] == "CONTINUE" else 8)
if mode == "all":
    ON, OFF, X4 = pair(PACKS); ids = sorted(ON); F = {i: fic(i, ON[i]) for i in ids}
    G0 = {"on": g0(ON), "off": g0(OFF)}
    G1 = {"codes_same_as_4b_x2b": sum(hp(ON[i]) == hp(X4[i]) for i in ids), "kept_same_as_4b_x2b": sum(kept(ON[i]) == kept(X4[i]) for i in ids)}
    ch = sum(kept(ON[i]) != kept(OFF[i]) or tm(ON[i]).get("promptTokens") != tm(OFF[i]).get("promptTokens") for i in ids)
    G3 = {"on_present": sum(f["on"] for f in F.values()), "off_present": sum(f["off"] for f in F.values())}
    d = [tm(ON[i])["promptTokens"] - tm(OFF[i])["promptTokens"] for i in ids if tm(ON[i]).get("promptTokens") is not None and tm(OFF[i]).get("promptTokens") is not None]
    ok = {"G0": all(v == 0 for g in G0.values() for v in g.values()), "G1": min(G1.values()) >= 170, "G2": ch / 180 >= 0.5, "G3": G3["on_present"] > G3["off_present"]}
    p50 = lambda T, k: st.median([tm(T[i])[k] for i in ids if tm(T[i]).get(k) is not None])
    # LITE5 MacBook anchor (same host, seed, tree) on the 20 shared ids
    anc = {}
    for m, T in (("on", ON), ("off", OFF)):
        L = ld(f"{H}/runs/lite5-{m}-st20-s42.traces.jsonl"); anc[m] = {"n": len(L), "answer_identical": sum(txt(L[i]) == txt(T[i]) for i in L), "kept_identical": sum(kept(L[i]) == kept(T[i]) for i in L),
            "promptTokens_identical": sum(tm(L[i]).get("promptTokens") == tm(T[i]).get("promptTokens") for i in L)}
    r = {"criterion_sha256": open(f"{H}/LITE5-180-criterion.sha256").read().split()[0], "G0": G0, "G1": G1, "G2": {"changed": ch, "share": round(ch / 180, 3)}, "G3": G3,
         "fired_on": sum(f["n_appended"] > 0 for f in F.values()), "appended_chunks": sum(f["n_appended"] for f in F.values()),
         "growth": {"n_llm_both": len(d), "p50": st.median(d), "max": max(d)},
         "p50": {k + "_" + m: p50(T, k) for k in ("promptTokens", "totalMs", "ttftMs") for m, T in (("on", ON), ("off", OFF))} | {"answerWords_on": st.median(len(txt(ON[i]).split()) for i in ids), "answerWords_off": st.median(len(txt(OFF[i]).split()) for i in ids)},
         "answers_identical_on_off": sum(txt(ON[i]) == txt(OFF[i]) for i in ids), "lite5_macbook_anchor": anc, "pass": ok, "verdict": "PASS" if all(ok.values()) else "FAIL"}
    json.dump(r, open(f"{H}/aggregates/gate-180.json", "w"), indent=1)
    json.dump({i: F[i] | {"reach": "newly_present" if F[i]["on"] and not F[i]["off"] else "present_off" if F[i]["off"] else "absent"} for i in ids}, open(f"{H}/aggregates/fic-180.json", "w"), indent=1)
    print(json.dumps(r)); sys.exit(0 if all(ok.values()) else 8)
