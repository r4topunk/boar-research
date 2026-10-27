#!/usr/bin/env python3
# LITE4 0-call gate (frozen in LITE4-criterion.md). Usage: gate0.py <off_kit> <off_st20> <on_kit> <on_st20> <gate-ids.json> <out.json>
# Prints and writes counts / ids / numbers only (never answer text). rc 0 = PASS, 1 = FAIL.
import json, re, sys, statistics as st
ok_, ok_s, on_k, on_s, idsf, out = sys.argv[1:7]
tr = lambda p: {(t := json.loads(l))["itemId"]: t for l in open(p) if l.strip()}
OFF = tr(ok_) | tr(ok_s); ON = tr(on_k) | tr(on_s); G = json.load(open(idsf))
NOTICE = "This answer is not from an offline source on this phone; check it before relying on it."   # the app's fixed no-source line (same in ON and OFF), removed before the hedge regex
HEDGE = re.compile(r"\b(not sure|unsure|uncertain|unclear|i don'?t know|i do not know|(cannot|can'?t|could not|couldn'?t) (confirm|verify|determine|find|tell)|"
                   r"no (offline )?source|(sources?|passages?|context) (do(es)?n'?t|do(es)? not) (say|answer|mention|cover|provide|state|specify)|"
                   r"not (mentioned|stated|covered|specified|provided|supported)|(isn'?t|is not|aren'?t|are not) (supported|true|accurate|correct)|premise|"
                   r"may not be (accurate|correct)|didn'?t find|did not find)\b", re.I)
norm = lambda s: " ".join((s or "").split())
ans = lambda t: (t.get("answer") or {}).get("text") or ""
hedged = lambda t: bool(HEDGE.search(ans(t).replace(NOTICE, " ")))
words = lambda t: len(ans(t).split())
ptok = lambda t: (t.get("timing") or {}).get("promptTokens")
reas = lambda t: max(sum(e.get("reasoningTokens") or 0 for e in t.get("events", []) if e.get("kind") == "generation"), (t.get("timing") or {}).get("reasoningTokens") or 0)
miss = [i for i in G["core32"] + G["health_safety8"] if i not in ON or i not in OFF]
assert not miss, f"missing ids {miss}"
inv, oth, core = G["invented10"], G["core22"], G["core32"]
changed = [i for i in inv if norm(ans(ON[i])) != norm(ans(OFF[i]))]
h_on = [i for i in oth if hedged(ON[i])]; h_off = [i for i in oth if hedged(OFF[i])]
w_on = st.median(words(ON[i]) for i in core); w_off = st.median(words(OFF[i]) for i in core)
pp = [(ptok(ON[i]), ptok(OFF[i])) for i in core if ptok(ON[i]) is not None and ptok(OFF[i]) is not None]
p_on = st.median(a for a, _ in pp); p_off = st.median(b for _, b in pp); dp = st.median(a - b for a, b in pp)
det = [i for i in G["health_safety8"] if ptok(OFF[i]) is None]
det_same = [i for i in det if norm(ans(ON[i])) == norm(ans(OFF[i])) and ptok(ON[i]) is None]
allon = list(ON.values())
infra = {"n_on": len(allon), "errors": sum(bool(t.get("error")) for t in allon), "empty": sum(words(t) == 0 for t in allon),
         "reasoning_pos": sum(reas(t) > 0 for t in allon), "think_tag": sum("<think>" in ans(t) for t in allon)}
g = {"G1_changed_invented": [len(changed), 10, len(changed) >= 8],
     "G2_hedged_core22": [len(h_off), len(h_on), len(h_on) <= len(h_off) + 2],
     "G3_words_p50_core32": [w_off, w_on, w_on >= 0.9 * w_off],
     "G4_prompt_tokens_p50_core32": [p_off, p_on, dp, (p_on - p_off) <= 60 and dp <= 60],
     "G5_deterministic_identical": [len(det_same), len(det), len(det_same) == len(det)],
     "G0_infra": [infra, all(v == 0 for k, v in infra.items() if k != "n_on")]}
verdict = all(v[-1] for v in g.values())
res = {"gate": g, "verdict": "PASS" if verdict else "FAIL", "changed_invented_ids": changed, "unchanged_invented_ids": [i for i in inv if i not in changed],
       "hedged_core22_on": h_on, "hedged_core22_off": h_off, "deterministic_ids": det,
       "hedged_invented": [sum(hedged(OFF[i]) for i in inv), sum(hedged(ON[i]) for i in inv)],
       "words_p50_invented": [st.median(words(OFF[i]) for i in inv), st.median(words(ON[i]) for i in inv)],
       "lite_codes": {c: sum(c in (ON[i].get("route") or {}).get("reasonCodes", []) for i in ON) for c in ["lite:source-bound-sourced", "lite:source-bound-memory", "lite:source-bound-nosource"]}}
json.dump(res, open(out, "w"), indent=1)
for k, v in g.items(): print(k, v)
print("GATE0", res["verdict"]); sys.exit(0 if verdict else 1)
