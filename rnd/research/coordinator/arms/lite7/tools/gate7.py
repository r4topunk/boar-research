#!/usr/bin/env python3
"""LITE7 0-call gates (LITE7-criterion.md). 0 LLM. Prints counts/numbers only (never answer text).
  gate7.py run <pack>     per-run gate: 20 rows, 0 errors/empty/reasoning/<think>
  gate7.py checkpoint     after pack 1 (qa-travel-se): KILL if lite:style missing on an LLM item or words p50 ON <= OFF
  gate7.py all            G0..G7 on the 180 -> aggregates/gate7.json
rc 0 PASS, 8 FAIL/KILL."""
import json, re, sys, statistics as st, importlib.util
A = "<workspace>/rnd/research/coordinator/arms"; H = f"{A}/lite7"; R = f"{H}/runs/180"
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se", "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
SENT = re.compile(r"(?<=[.!?])\s+"); nsent = lambda s: len([x for x in SENT.split((s or "").strip()) if len(x.strip()) > 1])   # = lite3.nsent
NOTICE = "This answer is not from an offline source on this phone; check it before relying on it."   # = lite4 gate0.py
HEDGE = re.compile(r"\b(not sure|unsure|uncertain|unclear|i don'?t know|i do not know|(cannot|can'?t|could not|couldn'?t) (confirm|verify|determine|find|tell)|"
                   r"no (offline )?source|(sources?|passages?|context) (do(es)?n'?t|do(es)? not) (say|answer|mention|cover|provide|state|specify)|"
                   r"not (mentioned|stated|covered|specified|provided|supported)|(isn'?t|is not|aren'?t|are not) (supported|true|accurate|correct)|premise|"
                   r"may not be (accurate|correct)|didn'?t find|did not find)\b", re.I)
ld = lambda f: {(t := json.loads(l))["itemId"]: t for l in open(f) if l.strip()}
txt = lambda t: (t.get("answer") or {}).get("text") or ""; tm = lambda t: t.get("timing") or {}
kept = lambda t: [(s.get("title"), s.get("section")) for s in (t.get("retrieval") or {}).get("kept") or []]
codes = lambda t: (t.get("route") or {}).get("reasonCodes") or []
hp = lambda t: [c for c in codes(t) if c.startswith("headpass")]
words = lambda t: len(txt(t).split()); gen = lambda t: (tm(t).get("outputTokens") or 0) > 0
import os; V2 = os.environ.get("CRIT") == "v2"   # v2 (LITE7-criterion-v2.md): G3 ignores one trailing [n] citation after sentence punctuation
CRITF = f"{H}/LITE7-criterion-v2.sha256" if V2 else f"{H}/LITE7-criterion.sha256"; GOUT = f"{H}/aggregates/gate7-v2.json" if V2 else f"{H}/aggregates/gate7.json"
_eo = lambda s: bool(s) and s[-1] not in '.!?)"\'*'
ends_open = lambda t: _eo(re.sub(r'(?<=[.!?])\s*\[\d+\]$', "", txt(t).strip()) if V2 else txt(t).strip())
hedged = lambda t: bool(HEDGE.search(txt(t).replace(NOTICE, " ")))
def g0(T): return {"errors": sum(bool(t.get("error")) for t in T.values()), "empty": sum(not txt(t).strip() for t in T.values()),
                   "reasoning_tokens": sum(tm(t).get("reasoningTokens") or 0 for t in T.values()), "think_tag": sum("<think>" in txt(t) for t in T.values())}
def pair(packs):
    ON, OFF = {}, {}
    for p in packs: ON.update(ld(f"{R}/lite7-180-on-{p}-s42.traces.jsonl")); OFF.update(ld(f"{A}/lite5/runs/180/lite5-180-on-{p}-s42.traces.jsonl"))
    assert set(ON) == set(OFF), "id sets differ"; return ON, OFF
def profile(T, ids):
    return {"n": len(ids), "gt2_share": round(sum(nsent(txt(T[i])) > 2 for i in ids) / len(ids), 3), "words_p50": st.median(words(T[i]) for i in ids),
            "sent_p50": st.median(nsent(txt(T[i])) for i in ids), "ends_open": sum(ends_open(T[i]) for i in ids),
            "out_tokens_p50": st.median(tm(T[i]).get("outputTokens") or 0 for i in ids), "out_tokens_max": max(tm(T[i]).get("outputTokens") or 0 for i in ids)}
mode = sys.argv[1]
if mode == "run":
    p = sys.argv[2]; T = ld(f"{R}/lite7-180-on-{p}-s42.traces.jsonl"); r = {"rows": len(T), **g0(T)}
    ok = r["rows"] == 20 and all(r[k] == 0 for k in ("errors", "empty", "reasoning_tokens", "think_tag"))
    r["verdict"] = "PASS" if ok else "FAIL"; print(f"gate run {p}", json.dumps(r)); sys.exit(0 if ok else 8)
if mode == "checkpoint":
    ON, OFF = pair(PACKS[:1]); llm = [i for i in OFF if gen(OFF[i])]
    miss = sum("lite:style" not in codes(ON[i]) for i in llm); w_on, w_off = st.median(words(ON[i]) for i in llm), st.median(words(OFF[i]) for i in llm)
    r = {"pack": PACKS[0], "llm": len(llm), "lite_style_missing": miss, "words_p50_on": w_on, "words_p50_off": w_off}
    r["verdict"] = "CONTINUE" if miss == 0 and w_on > w_off else "KILL"
    json.dump(r, open(f"{H}/aggregates/checkpoint7.json", "w"), indent=1); print(json.dumps(r)); sys.exit(0 if r["verdict"] == "CONTINUE" else 8)
if mode == "all":
    ON, OFF = pair(PACKS); ids = sorted(ON); llm = [i for i in ids if gen(OFF[i])]; det = [i for i in ids if not gen(OFF[i])]
    assert not any(c.startswith("grounding:health") for i in llm for c in codes(OFF[i])), "a health route generates"
    PON, POFF = profile(ON, ids), profile(OFF, ids)
    ptd = [tm(ON[i])["promptTokens"] - tm(OFF[i])["promptTokens"] for i in llm]
    pt_on, pt_off = st.median(tm(ON[i])["promptTokens"] for i in llm), st.median(tm(OFF[i])["promptTokens"] for i in llm)
    G = {"G0": {"on": g0(ON)}, "G1": {"gt2_on": PON["gt2_share"], "gt2_off": POFF["gt2_share"]}, "G2": {"words_p50_on": PON["words_p50"], "words_p50_off": POFF["words_p50"]},
         "G3": {"ends_open_on": PON["ends_open"], "ends_open_off": POFF["ends_open"], "cap_hits_on": sum((tm(ON[i]).get("outputTokens") or 0) >= 200 for i in ids)},
         "G4": {"hedged_on": sum(hedged(ON[i]) for i in llm), "hedged_off": sum(hedged(OFF[i]) for i in llm), "n": len(llm)},
         "G5": {"det_n": len(det), "det_identical": sum(txt(ON[i]) == txt(OFF[i]) for i in det), "lite_style_llm": sum("lite:style" in codes(ON[i]) for i in llm),
                "lite_style_det": sum("lite:style" in codes(ON[i]) for i in det)},
         "G6": {"pt_p50_on": pt_on, "pt_p50_off": pt_off, "growth_max": max(ptd), "growth_min": min(ptd), "growth_p50": st.median(ptd)},
         "G7": {"kept_and_hp_same": sum(kept(ON[i]) == kept(OFF[i]) and hp(ON[i]) == hp(OFF[i]) for i in ids)}}
    ok = {"G0": all(v == 0 for v in G["G0"]["on"].values()), "G1": PON["gt2_share"] >= 0.45, "G2": 42 <= PON["words_p50"] <= 60,
          "G3": PON["ends_open"] <= POFF["ends_open"] + 2 and G["G3"]["cap_hits_on"] == 0, "G4": G["G4"]["hedged_on"] <= G["G4"]["hedged_off"] + 2,
          "G5": G["G5"]["det_identical"] == len(det) == 28 and G["G5"]["lite_style_llm"] == len(llm) == 152 and G["G5"]["lite_style_det"] == 0,
          "G6": pt_on <= pt_off + 15 and max(ptd) <= 15, "G7": G["G7"]["kept_and_hp_same"] >= 178}
    tot = lambda T, k: st.median(tm(T[i])[k] / 1000 for i in llm if tm(T[i]).get(k) is not None)
    out = {"criterion_version": "v2" if V2 else "v1", "criterion_sha256": open(CRITF).read().split()[0], "gates": G, "pass": ok, "profile_180": {"on": PON, "off": POFF},
           "profile_llm152": {"on": profile(ON, llm), "off": profile(OFF, llm)}, "answer_changed_llm": sum(txt(ON[i]) != txt(OFF[i]) for i in llm),
           "latency_llm_p50_s": {"total": [tot(ON, "totalMs"), tot(OFF, "totalMs")], "ttft": [tot(ON, "ttftMs"), tot(OFF, "ttftMs")]}, "det_ids": det}
    out["verdict"] = "PASS" if all(ok.values()) else "FAIL"
    json.dump(out, open(GOUT, "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "det_ids"}, indent=1)); sys.exit(0 if out["verdict"] == "PASS" else 8)
