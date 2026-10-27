#!/usr/bin/env python3
"""LITE5 0-call gate (LITE5-criterion.md v2 9ba8bbf3…, stage 3; v1 077b1dbd… G2 was <= 600 on timing.promptTokens) on runs/lite5-on-st20-s42.traces.jsonl.
G0 0 errors / 0 empty / 0 reasoning tokens / no <think>; G1 headpass:* codes + kept (title, section) == the 4B X2b traces 20/20; G2 per item ON − OFF promptTokens == the 4B X2b − S growth
(OFF = LITE2 l-st20 traces, S = c4b-st20 traces; items with prompt tokens in both); G3 changed vs OFF (kept or promptTokens) >= 0.20; G4 fact present ON >= 10/20 (fic.py rule).
Also: answers identical ON vs OFF (whitespace-normalised), p50 prompt tokens / total ms. Writes aggregates/gate5.json; rc 0 PASS, 8 FAIL."""
import json, re, statistics as st, subprocess, sys
A = "<workspace>/rnd/research/coordinator/arms"; H = f"{A}/lite5"
ld = lambda f: {(t := json.loads(l))["itemId"]: t for l in open(f) if l.strip()}
ids = [l.strip() for l in open(f"{A}/lite2/selftest20.ids") if l.strip()]; packs = sorted({i[3:].rsplit("-", 1)[0] for i in ids})
ON = ld(f"{H}/runs/lite5-on-st20-s42.traces.jsonl"); OFF = ld(f"{A}/lite2/runs/l-st20-s42.traces.jsonl"); X4 = {}
for p in packs: X4.update(ld(f"{A}/headpass-st/gen-x2b/st-{p}-cut7-headpassx2b-s42.traces.jsonl"))
txt = lambda t: (t.get("answer") or {}).get("text") or ""; tm = lambda t: t.get("timing") or {}
kept = lambda t: [(s.get("title"), s.get("section")) for s in (t.get("retrieval") or {}).get("kept") or []]
hp = lambda t: [c for c in t["route"]["reasonCodes"] if c.startswith("headpass")]
norm = lambda s: re.sub(r"\s+", " ", s).strip()
g0 = {"errors": sum(bool(ON[i].get("error")) for i in ids), "empty": sum(not txt(ON[i]).strip() for i in ids),
      "reasoning_tokens": sum(tm(ON[i]).get("reasoningTokens") or 0 for i in ids), "think_tag": sum("<think>" in txt(ON[i]) for i in ids)}
g1 = {"codes_same_as_4b_x2b": sum(hp(ON[i]) == hp(X4[i]) for i in ids), "kept_same_as_4b_x2b": sum(kept(ON[i]) == kept(X4[i]) for i in ids)}
d = [tm(ON[i])["promptTokens"] - tm(OFF[i])["promptTokens"] for i in ids if tm(ON[i]).get("promptTokens") is not None and tm(OFF[i]).get("promptTokens") is not None]
C4 = ld(f"{A}/lite2/runs/c4b-st20-s42.traces.jsonl")
eq = [tm(ON[i])["promptTokens"] - tm(OFF[i])["promptTokens"] == tm(X4[i])["promptTokens"] - tm(C4[i])["promptTokens"] for i in ids if tm(ON[i]).get("promptTokens") is not None and tm(OFF[i]).get("promptTokens") is not None]
g2 = {"n_llm_both": len(d), "max_growth": max(d), "p50_growth": st.median(d), "over_600_server_count": sum(x > 600 for x in d), "growth_equal_4b_x2b": sum(eq)}
ch = sum(kept(ON[i]) != kept(OFF[i]) or tm(ON[i]).get("promptTokens") != tm(OFF[i]).get("promptTokens") for i in ids)
fic = json.loads(subprocess.run([sys.executable, "-I", f"{H}/tools/fic.py", f"{H}/runs/lite5-on-st20-s42.traces.jsonl", "--out", f"{H}/aggregates/fic.json"], capture_output=True, text=True, check=True).stdout)
p50 = lambda T, k: st.median([tm(T[i])[k] for i in ids if tm(T[i]).get(k) is not None])
res = {"criterion_sha256": open(f"{H}/LITE5-criterion.sha256").read().split()[0], "G0": g0, "G1": g1, "G2": g2, "G3": {"changed": ch, "share": ch / 20}, "G4": {"on_present": fic["on_present"], "off_present": fic["off_present"], "newly_present": fic["newly_present"]},
       "answers_identical_on_off": sum(norm(txt(ON[i])) == norm(txt(OFF[i])) for i in ids),
       "p50": {"promptTokens_on": p50(ON, "promptTokens"), "promptTokens_off": p50(OFF, "promptTokens"), "totalMs_on": p50(ON, "totalMs"), "totalMs_off_mini": p50(OFF, "totalMs"),
               "answerWords_on": st.median(len(txt(ON[i]).split()) for i in ids), "answerWords_off": st.median(len(txt(OFF[i]).split()) for i in ids)}}
ok = {"G0": all(v == 0 for v in g0.values()), "G1": g1["codes_same_as_4b_x2b"] == 20 and g1["kept_same_as_4b_x2b"] == 20, "G2": g2["growth_equal_4b_x2b"] == len(d), "G3": ch / 20 >= 0.2, "G4": fic["on_present"] >= 10}
res["pass"] = ok; res["verdict"] = "PASS" if all(ok.values()) else "FAIL"
json.dump(res, open(f"{H}/aggregates/gate5.json", "w"), indent=1); print(json.dumps(res)); sys.exit(0 if all(ok.values()) else 8)
