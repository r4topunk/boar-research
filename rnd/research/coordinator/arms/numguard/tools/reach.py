"""NUMGUARD step 1 reach read (0 LLM calls). Usage: python3 -I reach.py <traces.jsonl>...
Per trace file: items where the learned detector fired (reason code detector:fire) and whether the answer is the health refusal."""
import json, re, sys
REF = re.compile(r"won't give health advice|grounding:health-no-source")
for p in sys.argv[1:]:
    rows = [json.loads(l) for l in open(p) if l.strip()]
    fired = []
    for t in rows:
        rc = (t.get("route") or {}).get("reasonCodes") or []
        pm = next((c for c in rc if c.startswith("detector:p=")), "")
        txt = (t.get("answer") or {}).get("text") or ""
        refusal = bool(REF.search(txt) or REF.search(" ".join(rc)))
        if "detector:fire" in rc: fired.append((t["itemId"], pm[11:], refusal, "numeric-guard" if "detector:numeric-guard" in rc else "", txt[:70].replace("\n", " ")))
    print(f"== {p.split('/arms/')[-1]}: n={len(rows)} detector:fire={len(fired)} refusals_among_fired={sum(f[2] for f in fired)}")
    for f in fired: print("  ", f[0], "p=" + f[1], "REFUSAL" if f[2] else "answered", f[3], "|", f[4])
