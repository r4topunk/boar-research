#!/usr/bin/env python3
"""QUANTLITE 0-call gate + speed: Q8 + X2b traces vs LITE5's Q4 + X2b traces (lite5/runs/lite5-on-st20-s42, MacBook) on the same ids.
G0 0 errors / 0 empty / 0 reasoning tokens / no <think>; G1 headpass:* codes + kept (title, section) == Q4 traces on every item;
G2 promptTokens == Q4 traces on every LLM item (same tokenizer, same context); answers identical (descriptive); speed: decodeTokPerSec p50,
prefill tok/s p50, totalMs p50, RSS from the runner status files. Usage: gate_q.py <q8 traces> <ids file|-> <out.json> [status files...]; rc 0 PASS, 8 FAIL."""
import json, re, statistics as st, sys
A = "<workspace>/rnd/research/coordinator/arms"
ld = lambda f: {(t := json.loads(l))["itemId"]: t for l in open(f) if l.strip()}
Q8 = ld(sys.argv[1]); ids = sorted(Q8) if sys.argv[2] == "-" else [l.strip() for l in open(sys.argv[2]) if l.strip()]
Q4 = ld(f"{A}/lite5/runs/lite5-on-st20-s42.traces.jsonl")
txt = lambda t: (t.get("answer") or {}).get("text") or ""; tm = lambda t: t.get("timing") or {}
kept = lambda t: [(s.get("title"), s.get("section")) for s in (t.get("retrieval") or {}).get("kept") or []]
hp = lambda t: [c for c in t["route"]["reasonCodes"] if c.startswith("headpass")]
norm = lambda s: re.sub(r"\s+", " ", s).strip()
llm = [i for i in ids if tm(Q8[i]).get("outputTokens")]
g0 = {"errors": sum(bool(Q8[i].get("error")) for i in ids), "empty": sum(not txt(Q8[i]).strip() for i in ids),
      "reasoning_tokens": sum(tm(Q8[i]).get("reasoningTokens") or 0 for i in ids), "think_tag": sum("<think>" in txt(Q8[i]) for i in ids)}
g1 = {"codes_same_as_q4": sum(hp(Q8[i]) == hp(Q4[i]) for i in ids), "kept_same_as_q4": sum(kept(Q8[i]) == kept(Q4[i]) for i in ids)}
g2 = {"n_llm": len(llm), "promptTokens_same_as_q4": sum(tm(Q8[i]).get("promptTokens") == tm(Q4[i]).get("promptTokens") for i in llm)}
p50 = lambda T, k, I: st.median([tm(T[i])[k] for i in I if tm(T[i]).get(k) is not None]) if I else None
pf = lambda T, I: st.median([tm(T[i])["promptTokens"] / (tm(T[i])["prefillMs"] / 1000) for i in I if tm(T[i]).get("prefillMs")]) if I else None
rss = []
for f in sys.argv[4:]:
    for l in open(f):
        if l.startswith("rss_kib"): p = l.split(); rss.append({"max_kib": int(p[2]), "median_kib": int(p[4])})
res = {"n": len(ids), "G0": g0, "G1": g1, "G2": g2,
       "answers_identical_q8_q4": sum(norm(txt(Q8[i])) == norm(txt(Q4[i])) for i in ids),
       "speed_q8_mini": {"decodeTokPerSec_p50": p50(Q8, "decodeTokPerSec", llm), "prefillTokPerSec_p50": pf(Q8, llm), "totalMs_p50": p50(Q8, "totalMs", ids), "ttftMs_p50": p50(Q8, "ttftMs", llm),
                         "promptTokens_p50": p50(Q8, "promptTokens", llm), "outputTokens_p50": p50(Q8, "outputTokens", llm)},
       "speed_q4_macbook": {"decodeTokPerSec_p50": p50(Q4, "decodeTokPerSec", llm), "prefillTokPerSec_p50": pf(Q4, llm), "totalMs_p50": p50(Q4, "totalMs", ids), "outputTokens_p50": p50(Q4, "outputTokens", llm)},
       "answerWords_p50": {"q8": st.median(len(txt(Q8[i]).split()) for i in ids), "q4": st.median(len(txt(Q4[i]).split()) for i in ids)},
       "rss_runs": rss, "rss_max_gib": round(max(r["max_kib"] for r in rss) / 1048576, 3) if rss else None, "rss_median_of_medians_gib": round(st.median(r["median_kib"] for r in rss) / 1048576, 3) if rss else None}
ok = {"G0": all(v == 0 for v in g0.values()), "G1": g1["codes_same_as_q4"] == len(ids) and g1["kept_same_as_q4"] == len(ids), "G2": g2["promptTokens_same_as_q4"] == len(llm)}
res["pass"] = ok; res["verdict"] = "PASS" if all(ok.values()) else "FAIL"
json.dump(res, open(sys.argv[3], "w"), indent=1); print(json.dumps(res)); sys.exit(0 if all(ok.values()) else 8)
